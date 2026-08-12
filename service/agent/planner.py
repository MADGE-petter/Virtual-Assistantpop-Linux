"""
Planner Agent - LLM sinh kế hoạch từ yêu cầu người dùng
Dùng Gemma 4 E4B GGUF qua llama-cpp-python
"""

import json
import re
from service.agent import Plan, PlanStep, AgentStatus, BaseAgent
from service.agent.gemma_llm_service import get_gemma_service
from utils.logger import get_logger

logger = get_logger(__name__)


PLANNER_SYSTEM_PROMPT = """Bạn là Planner Agent của Pop Assistant - trợ lý AI tiếng Việt.

Nhiệm vụ: Phân tích yêu cầu người dùng → sinh kế hoạch hành động dạng JSON.

Nguyên tắc:
1. Chia yêu cầu thành các bước nhỏ, tuần tự
2. Mỗi bước dùng 1 tool có sẵn
3. Nếu không chắc chắn, thêm bước ask_user để hỏi
4. Với thao tác nguy hiểm (shutdown, delete), thêm confirm
5. Ưu tiên tool đơn giản, tránh phức tạp hóa

Output PHẢI là JSON hợp lệ, không thêm text ngoài JSON:

Format: goal (string), steps (array of objects with step_id, tool, args, reason, depends_on), final_response (string).

Ví dụ: User: "Mở Chrome và vào GitHub" → goal: "Mở Chrome và truy cập GitHub", steps: [step_id: 1, tool: "open_app", args: app_name: "Chrome"], [step_id: 2, tool: "open_website", args: url: "github.com", depends_on: [1]]
User: "Kiểm tra máy có nóng không, nếu CPU > 80% thì mở Task Manager" → goal: "Kiểm tra nhiệt độ", steps: [step_id: 1, tool: "system_status"], [step_id: 2, tool: "open_app", args: app_name: "Task Manager", depends_on: [1]]

AVAILABLE TOOLS: {tools_description}
"""


class PlannerAgent(BaseAgent):
    """Agent lập kế hoạch - dùng LLM để sinh Plan từ yêu cầu"""
    
    agent_name = "planner"
    agent_description = "Lập kế hoạch đa bước từ yêu cầu người dùng"
    
    def __init__(self, llm_service=None):
        super().__init__()
        self._llm = llm_service
        self._tool_schemas: list = []
        self._gemma_service = None
    
    def set_llm(self, llm_service):
        self._llm = llm_service
    
    def _get_gemma_llm(self):
        """Lazy load Gemma LLM service"""
        if self._gemma_service is None:
            try:
                self._gemma_service = get_gemma_service()
            except Exception as e:
                logger.error(f"[Planner] Failed to load Gemma LLM: {e}")
                return None
        return self._gemma_service
    
    def update_tools(self, tool_schemas: list):
        """Cập nhật danh sách tool để Planner biết"""
        self._tool_schemas = tool_schemas
    
    def _build_tools_description(self) -> str:
        """Tạo mô tả tools cho prompt"""
        lines = []
        for schema in self._tool_schemas:
            params_str = ", ".join(
                f"{k}: {v.get('type', 'any')}" 
                for k, v in schema.parameters.items()
            )
            lines.append(f"- {schema.name}({params_str}): {schema.description}")
        return "\n".join(lines)
    
    def plan(self, user_request: str, context: dict = None) -> Plan:
        """
        Sinh kế hoạch từ yêu cầu người dùng.
        
        Args:
            user_request: Câu yêu cầu của user
            context: Context bổ sung (memory, preferences, etc.)
        
        Returns:
            Plan object với các bước thực thi
        """
        # Try Gemma LLM first, then fallback to generic llm
        llm = self._get_gemma_llm() if self._llm is None else self._llm
        
        if not llm:
            return self._fallback_plan(user_request)
        
        tools_desc = self._build_tools_description()
        prompt = PLANNER_SYSTEM_PROMPT.format(tools_description=tools_desc)
        
        full_prompt = f"{prompt}\n\nUser request: {user_request}\n\nPlan JSON:"
        
        try:
            raw_response = llm.generate(full_prompt, max_tokens=512)
            plan_data = self._parse_json(raw_response)
            return self._build_plan(plan_data)
        except Exception as e:
            logger.error(f"[Planner] LLM error: {e}, using fallback")
            return self._fallback_plan(user_request)
    
    def _parse_json(self, raw: str) -> dict:
        """Parse JSON từ LLM response (có thể lẫn text)"""
        # Tìm JSON block
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group())
            except Exception as e:
                logger.error(f"[Planner] Error parsing JSON block: {e}")
        
        # Thử parse cả response
        try:
            return json.loads(raw)
        except Exception as e:
            logger.error(f"[Planner] Error parsing raw JSON: {e}")
        
        raise ValueError(f"Cannot parse JSON from: {raw[:200]}")
    
    def _build_plan(self, data: dict) -> Plan:
        """Chuyển dict → Plan object"""
        steps = []
        for s in data.get("steps", []):
            steps.append(PlanStep(
                step_id=s.get("step_id", len(steps) + 1),
                tool=s.get("tool", "unknown"),
                args=s.get("args", {}),
                reason=s.get("reason", ""),
                depends_on=s.get("depends_on", [])
            ))
        
        return Plan(
            goal=data.get("goal", "Không xác định"),
            steps=steps,
            final_response_template=data.get("final_response", "")
        )
    
    def _fallback_plan(self, user_request: str) -> Plan:
        """Fallback khi LLM không available - phân tích đơn giản"""
        text_lower = user_request.lower()
        
        # Phân tích keyword cơ bản
        steps = []
        step_id = 1
        
        if any(w in text_lower for w in ["mở", "chạy", "khởi động", "open", "launch"]):
            # Trích xuất tên app
            import re
            app_match = re.search(r'(?:mở|chạy|khởi động|open|launch)\s+(.+?)(?:\s+vào|\s+để|\s+rồi|$)', text_lower)
            if app_match:
                steps.append(PlanStep(
                    step_id=step_id, tool="open_app",
                    args={"app_name": app_match.group(1).strip()},
                    reason="Mở ứng dụng"
                ))
                step_id += 1
        
        if any(w in text_lower for w in ["thời tiết", "weather", "nhiệt độ"]):
            steps.append(PlanStep(
                step_id=step_id, tool="get_weather",
                args={"city": "Hà Nội"},
                reason="Lấy thời tiết"
            ))
            step_id += 1
        
        if any(w in text_lower for w in ["cpu", "ram", "hệ thống", "trạng thái", "nóng"]):
            steps.append(PlanStep(
                step_id=step_id, tool="system_status",
                args={},
                reason="Kiểm tra hệ thống"
            ))
            step_id += 1
        
        if any(w in text_lower for w in ["tìm", "search", "google", "kiếm"]):
            query_match = re.search(r'(?:tìm|search|google|kiếm)\s+(.+?)(?:\s+trên|\s+và|$)', text_lower)
            query = query_match.group(1).strip() if query_match else user_request
            steps.append(PlanStep(
                step_id=step_id, tool="web_search",
                args={"query": query},
                reason="Tìm kiếm"
            ))
            step_id += 1
        
        if not steps:
            steps.append(PlanStep(
                step_id=1, tool="speak",
                args={"text": f"Tôi chưa hiểu rõ yêu cầu: {user_request}. Bạn có thể nói rõ hơn không?"},
                reason="Không hiểu yêu cầu"
            ))
        
        return Plan(
            goal=user_request,
            steps=steps,
            final_response_template="Đã thực hiện yêu cầu"
        )
    
    def replan_on_failure(self, original_plan: Plan, failed_step: int, error: str) -> Plan:
        """Sinh kế hoạch thay thế khi 1 bước thất bại"""
        if not self._llm:
            # Fallback: bỏ qua bước lỗi, tiếp tục
            new_steps = [s for s in original_plan.steps if s.step_id != failed_step]
            return Plan(
                goal=original_plan.goal,
                steps=new_steps,
                final_response_template=original_plan.final_response_template
            )
        
        tools_desc = self._build_tools_description()
        prompt = f"""Kế hoạch gốc thất bại ở bước {failed_step}: {error}

Kế hoạch gốc:
{json.dumps({'goal': original_plan.goal, 'steps': [{'step_id': s.step_id, 'tool': s.tool, 'args': s.args} for s in original_plan.steps]}, indent=2, ensure_ascii=False)}

Hãy sinh kế hoạch THAY THẾ (chỉ các bước chưa hoàn thành). Output JSON:

AVAILABLE TOOLS:
{tools_desc}

Replan JSON:"""
        
        try:
            raw = self._llm.generate(prompt, max_tokens=512)
            data = self._parse_json(raw)
            return self._build_plan(data)
        except Exception as e:
            logger.error(f"[Planner] Replan failed: {e}")
            # Fallback: tiếp tục bỏ qua bước lỗi
            new_steps = [s for s in original_plan.steps if s.step_id != failed_step]
            return Plan(
                goal=original_plan.goal,
                steps=new_steps,
                final_response_template=original_plan.final_response_template
            )