"""
Workflow Engine - Thực thi kế hoạch đa bước
Có retry, dependency resolution, fallback, và tự sửa lỗi
"""

import time
from typing import Optional
from service.agent import (
    Plan, PlanStep, ToolResult, WorkflowResult,
    AgentRegistry, AgentStatus
)
from utils.thread_manager import get_thread_manager


from utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowEngine:
    """Engine thực thi Plan do Planner sinh ra"""
    
    def __init__(self, registry: AgentRegistry, planner=None, audio=None):
        self.registry = registry
        self.planner = planner  # Để replan_on_failure
        self.audio = audio      # Để speak/ask_user
        
        self._current_plan: Optional[Plan] = None
        self._results: dict[int, ToolResult] = {}
        self._on_step_complete = None  # Callback
        self._on_step_fail = None
        self._on_workflow_done = None
        
        # Retry config
        self.max_retries = 2
        self.retry_delay = 1.0
    
    def set_callbacks(self, on_step=None, on_fail=None, on_done=None):
        self._on_step_complete = on_step
        self._on_step_fail = on_fail
        self._on_workflow_done = on_done
    
    def execute(self, plan: Plan) -> WorkflowResult:
        """
        Thực thi toàn bộ kế hoạch.
        Xử lý dependency: bước nào depends_on chưa xong thì đợi.
        """
        self._current_plan = plan
        self._results = {}
        
        completed_steps = set()
        failed_steps = set()
        
        # Sắp xếp steps theo dependency (topological sort đơn giản)
        ready_queue = [s for s in plan.steps if not s.depends_on]
        remaining = [s for s in plan.steps if s.depends_on]
        
        while ready_queue:
            step = ready_queue.pop(0)
            
            # Kiểm tra dependency đã hoàn thành chưa
            deps_ready = all(dep in completed_steps for dep in step.depends_on)
            if not deps_ready:
                remaining.append(step)
                continue
            
            # Thực thi bước
            result = self._execute_step(step)
            self._results[step.step_id] = result
            
            if result.success:
                completed_steps.add(step.step_id)
                if self._on_step_complete:
                    self._on_step_complete(step, result)
            else:
                # Retry
                retry_result = self._retry_step(step)
                if retry_result and retry_result.success:
                    completed_steps.add(step.step_id)
                    self._results[step.step_id] = retry_result
                else:
                    # Replan
                    replan_result = self._replan_on_failure(step, result.error)
                    if replan_result:
                        completed_steps.add(step.step_id)
                        self._results[step.step_id] = replan_result
                    else:
                        failed_steps.add(step.step_id)
                        if self._on_step_fail:
                            self._on_step_fail(step, result.error)
            
            # Kiểm tra remaining steps đã sẵn sàng chưa
            newly_ready = []
            still_remaining = []
            for s in remaining:
                if all(dep in completed_steps for dep in s.depends_on):
                    newly_ready.append(s)
                else:
                    still_remaining.append(s)
            ready_queue.extend(newly_ready)
            remaining = still_remaining
        
        # Xử lý steps còn lại (dependency loop hoặc không thể chạy)
        for step in remaining:
            failed_steps.add(step.step_id)
            self._results[step.step_id] = ToolResult(
                success=False, 
                error=f"Dependency not met: {step.depends_on}"
            )
        
        # Tổng hợp kết quả
        final_response = self._build_final_response(plan)
        
        result = WorkflowResult(
            success=len(failed_steps) == 0,
            goal=plan.goal,
            steps_completed=len(completed_steps),
            steps_failed=len(failed_steps),
            results=self._results,
            final_response=final_response
        )
        
        if self._on_workflow_done:
            self._on_workflow_done(result)
        
        return result
    
    def _execute_step(self, step: PlanStep) -> ToolResult:
        """Thực thi 1 bước"""
        logger.debug(f"[Workflow] Step {step.step_id}: {step.tool}({step.args})")
        
        # Tool đặc biệt: speak, ask_user
        if step.tool == "speak":
            return self._handle_speak(step)
        elif step.tool == "ask_user":
            return self._handle_ask_user(step)
        elif step.tool == "confirm":
            return self._handle_confirm(step)
        
        # Tool từ registry
        return self.registry.execute_tool(step.tool, step.args)
    
    def _retry_step(self, step: PlanStep) -> Optional[ToolResult]:
        """Retry 1 bước với delay"""
        for attempt in range(self.max_retries):
            logger.debug(f"[Workflow] Retry {attempt + 1}/{self.max_retries} for step {step.step_id}")
            time.sleep(self.retry_delay)
            result = self._execute_step(step)
            if result.success:
                return result
        return None
    
    def _replan_on_failure(self, failed_step: PlanStep, error: str) -> Optional[ToolResult]:
        """Gọi Planner để sinh kế hoạch thay thế"""
        if not self.planner:
            return None
        
        logger.info(f"[Workflow] Replanning after step {failed_step.step_id} failed: {error}")
        
        try:
            new_plan = self.planner.replan_on_failure(
                self._current_plan, failed_step.step_id, error
            )
            
            # Tìm bước thay thế
            for step in new_plan.steps:
                result = self._execute_step(step)
                if result.success:
                    return result
            
            return None
        except Exception as e:
            logger.error(f"[Workflow] Replan failed: {e}")
            return None
    
    def _handle_speak(self, step: PlanStep) -> ToolResult:
        """Tool speak - dùng AudioService"""
        text = step.args.get("text", "")
        if self.audio:
            self.audio.speak(text)
        else:
            logger.info(f"[Speak] {text}")
        return ToolResult(success=True, data={"spoken": text})
    
    def _handle_ask_user(self, step: PlanStep) -> ToolResult:
        """Tool ask_user - hỏi và đợi câu trả lời"""
        question = step.args.get("question", "")
        if self.audio:
            self.audio.speak(question)
            response = self.audio.listen(timeout=10)
            if response and response != "...":
                return ToolResult(success=True, data={"user_response": response})
            return ToolResult(success=False, error="No response from user")
        return ToolResult(success=False, error="Audio not available")
    
    def _handle_confirm(self, step: PlanStep) -> ToolResult:
        """Tool confirm - xác nhận hành động nguy hiểm"""
        message = step.args.get("message", "Bạn có chắc không?")
        if self.audio:
            self.audio.speak(message)
            response = self.audio.listen(timeout=8)
            if response:
                confirmed = any(w in response.lower() for w in ["có", "ok", "đồng ý", "yes", "ừ"])
                return ToolResult(success=True, data={"confirmed": confirmed})
        return ToolResult(success=True, data={"confirmed": False})
    
    def _build_final_response(self, plan: Plan) -> str:
        """Tổng hợp final response từ template + kết quả"""
        template = plan.final_response_template
        
        if not template:
            # Tự tổng hợp
            parts = []
            for step in plan.steps:
                result = self._results.get(step.step_id)
                if result and result.success:
                    data = result.data
                    if isinstance(data, dict) and "text" in data:
                        parts.append(data["text"])
                    elif isinstance(data, dict) and "spoken" in data:
                        parts.append(data["spoken"])
            return " ".join(parts) if parts else f"Đã hoàn thành: {plan.goal}"
        
        # Thay thế {step_id.field} trong template
        import re
        def replace_ref(match):
            ref = match.group(1)
            parts = ref.split(".")
            step_id = int(parts[0])
            result = self._results.get(step_id)
            if result and result.success and isinstance(result.data, dict):
                if len(parts) > 1:
                    return str(result.data.get(parts[1], ""))
                return str(result.data)
            return f"[step {step_id} failed]"
        
        return re.sub(r'\{(\d+(?:\.\w+)?)\}', replace_ref, template)
    
    def execute_async(self, plan: Plan, callback=None):
        """Chạy workflow trong thread riêng"""
        def _run():
            result = self.execute(plan)
            if callback:
                callback(result)
        
        thread_mgr = get_thread_manager("WorkflowEngine")
        return thread_mgr.start_thread(
            _run,
            name="Workflow-Execute"
        )
    
    def get_step_result(self, step_id: int) -> Optional[ToolResult]:
        return self._results.get(step_id)