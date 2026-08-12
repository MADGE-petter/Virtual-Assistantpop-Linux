"""
Agent Loop - Main loop của AI Agent
Thay thế ConversationFlowService cũ bằng kiến trúc Agent

Flow:
1. User nói → STT
2. Memory Agent cung cấp context
3. Planner Agent sinh Plan (dùng LLM)
4. Workflow Engine thực thi Plan
5. Kết quả → TTS nói lại
6. Memory Agent học từ hội thoại
"""

import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)
from service.agent import AgentRegistry, Plan
from service.agent.planner import PlannerAgent
from service.agent.workflow_engine import WorkflowEngine
from service.agent.memory_agent import MemoryAgent
from service.agent.voice_agent import VoiceAgent
from service.agent.desktop_agent import DesktopAgent
from service.agent.system_agent import SystemAgent
from service.agent.file_agent import FileAgent
from service.agent.code_agent import CodeAgent
from service.agent.browser_agent import BrowserAgent
from service.agent.weather_agent import WeatherAgent


class AgentLoop:
    """
    Main Agent Loop - orchestrates the full AI Agent pipeline.
    
    Thay thế ConversationFlowService + ConversationService.
    """
    
    def __init__(self, audio_service=None, sql_service=None, app_scanner=None, llm_service=None):
        # === KHỞI TẠO TẤT CẢ AGENTS ===
        
        # Voice Agent (STT/TTS)
        self.voice = VoiceAgent(audio_service)
        
        # Tool Agents
        self.desktop = DesktopAgent(app_scanner)
        self.system = SystemAgent()
        self.file = FileAgent()
        self.code = CodeAgent()
        self.browser = BrowserAgent()
        self.weather = WeatherAgent()
        
        # Memory Agent (3 tầng)
        self.memory = MemoryAgent(sql_service)
        
        # Planner Agent (LLM → Plan)
        self.planner = PlannerAgent(llm_service)
        
        # === REGISTRY ===
        self.registry = AgentRegistry()
        self.registry.register(self.voice)
        self.registry.register(self.desktop)
        self.registry.register(self.system)
        self.registry.register(self.file)
        self.registry.register(self.code)
        self.registry.register(self.browser)
        self.registry.register(self.weather)
        
        # Cập nhật tool schemas cho Planner
        self.planner.update_tools(self.registry.get_all_tools_flat())
        
        # === WORKFLOW ENGINE ===
        self.engine = WorkflowEngine(self.registry, self.planner, audio_service)
        
        # === STATE ===
        self._active = False
        self._session_id = None
        self._view = None
        
        # Callbacks
        self.on_speak = None
        self.on_listen = None
        self.on_plan = None
        self.on_step = None
        self.on_done = None
    
    def set_view(self, view):
        self._view = view
    
    def set_llm(self, llm_service):
        self.planner.set_llm(llm_service)
    
    def set_audio(self, audio_service):
        self.voice.set_audio(audio_service)
        self.engine.audio = audio_service
    
    def set_sql(self, sql_service):
        self.memory.set_sql(sql_service)
    
    def set_app_scanner(self, scanner):
        self.desktop.set_app_scanner(scanner)
    
    def set_user_context(self, login_username: str = None, display_name: str = None):
        """Set user context cho tất cả agents (用于 logging và habit tracking)"""
        self.desktop.set_user_context(login_username, display_name)
        self.memory.set_user_context(login_username, display_name)
    
    def start_session(self, user_name: str = ""):
        """Bắt đầu phiên mới"""
        self._active = True
        self.memory.working.user_name = user_name
        self._session_id = str(int(time.time()))
        
        # Chào user
        if user_name:
            self.voice._speak(f"Chào {user_name}, tôi có thể giúp gì cho bạn?")
        else:
            self.voice._speak("Chào bạn, tôi là Pop. Tôi có thể giúp gì?")
    
    def process_request(self, user_text: str) -> str:
        """
        Xử lý 1 yêu cầu từ user qua pipeline Agent.
        
        Args:
            user_text: Câu nói của user (đã qua STT)
        
        Returns:
            Final response text
        """
        if not user_text or user_text == "...":
            return ""
        
        logger.debug(f"\n[AgentLoop] Processing: {user_text}")
        
        # === STEP 1: Kiểm tra workflow đã lưu ===
        saved_wf = self.memory.find_saved_workflow(user_text)
        if saved_wf:
            logger.debug(f"[AgentLoop] Found saved workflow: {saved_wf['name']}")
            plan = Plan(
                goal=saved_wf["plan"].get("goal", ""),
                steps=[],  # Sẽ parse từ saved plan
                final_response_template=saved_wf["plan"].get("final_response_template", "")
            )
            # Parse steps từ saved plan
            from service.agent import PlanStep
            for s in saved_wf["plan"].get("steps", []):
                plan.steps.append(PlanStep(
                    step_id=s.get("step_id", 0),
                    tool=s.get("tool", ""),
                    args=s.get("args", {}),
                    reason=s.get("reason", ""),
                    depends_on=s.get("depends_on", [])
                ))
        else:
            # === STEP 2: Planner sinh Plan ===
            context = self.memory.get_planner_context()
            plan = self.planner.plan(user_text, context)
        
        if self.on_plan:
            self.on_plan(plan)
        
        logger.debug(f"[AgentLoop] Plan: {plan.goal} ({len(plan.steps)} steps)")
        for s in plan.steps:
            logger.debug(f" Step {s.step_id}: {s.tool}({s.args})")
        
        # === STEP 3: Workflow Engine thực thi ===
        result = self.engine.execute(plan)
        
        # === STEP 4: Speak kết quả ===
        final_text = result.final_response
        if final_text:
            self.voice._speak(final_text)
        
        # === STEP 5: Memory học ===
        self.memory.learn_from_exchange(user_text, final_text, "agent_workflow")
        
        # Lưu workflow nếu thành công và có nhiều bước
        if result.success and len(plan.steps) >= 2:
            wf_name = self._generate_workflow_name(user_text, plan)
            self.memory.learn_workflow(wf_name, {
                "goal": plan.goal,
                "steps": [
                    {
                        "step_id": s.step_id,
                        "tool": s.tool,
                        "args": s.args,
                        "reason": s.reason,
                        "depends_on": s.depends_on
                    }
                    for s in plan.steps
                ],
                "final_response_template": plan.final_response_template
            })
            logger.info(f"[AgentLoop] Saved workflow: {wf_name}")
        
        if self.on_done:
            self.on_done(result)
        
        return final_text
    
    def _generate_workflow_name(self, user_text: str, plan: Plan) -> str:
        """Sinh tên workflow từ user request"""
        # Đơn giản: lấy 3-4 từ đầu tiên
        words = user_text.lower().split()[:4]
        name = "_".join(words)
        # Clean
        import re
        name = re.sub(r'[^\w_]', '', name)
        return name or plan.goal.lower().replace(" ", "_")[:30]
    
    def run_once(self, user_text: str = None):
        """Chạy 1 lượt: listen → process → speak"""
        if user_text is None:
            # Listen
            result = self.voice._listen(timeout=12)
            if not result.success:
                return
            user_text = result.data.get("user_text", "")
        
        return self.process_request(user_text)
    
    def run_loop(self):
        """Chạy vòng lặp chính (blocking, nên chạy trong thread)"""
        self._active = True
        
        while self._active:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"[AgentLoop] Error: {e}")
    
    def stop(self):
        self._active = False
    
    def update_tools(self):
        """Cập nhật tool schemas khi có agent mới"""
        self.planner.update_tools(self.registry.get_all_tools_flat())