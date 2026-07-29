"""
Agent Base Class + Agent Registry
Mỗi Agent là một module độc lập với schema rõ ràng.
Planner dùng schema này để sinh kế hoạch.
"""

from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    NEEDS_INPUT = "needs_input"


class RiskLevel(Enum):
    SAFE = "safe"        # Không ảnh hưởng hệ thống
    CONFIRM = "confirm"  # Cần xác nhận từ user
    DANGEROUS = "dangerous"  # Có thể gây hại (shutdown, delete)


@dataclass
class ToolSchema:
    """Schema cho 1 tool - để LLM biết tool làm gì, cần tham số gì"""
    name: str
    description: str
    parameters: dict  # JSON Schema format
    risk_level: RiskLevel = RiskLevel.SAFE
    requires_online: bool = False
    estimated_time: float = 1.0  # Thời gian dự kiến (giây)


@dataclass
class ToolResult:
    """Kết quả trả về từ 1 tool"""
    success: bool
    data: Any = None
    error: str = ""
    needs_user_input: bool = False
    user_prompt: str = ""


@dataclass
class PlanStep:
    """1 bước trong kế hoạch"""
    step_id: int
    tool: str
    args: dict = field(default_factory=dict)
    reason: str = ""
    depends_on: list[int] = field(default_factory=list)  # step_id cần hoàn thành trước


@dataclass
class Plan:
    """Kế hoạch do Planner sinh ra"""
    goal: str
    steps: list[PlanStep]
    final_response_template: str = ""  # Template để tổng hợp kết quả


@dataclass
class WorkflowResult:
    """Kết quả chạy 1 workflow"""
    success: bool
    goal: str
    steps_completed: int
    steps_failed: int
    results: dict[int, ToolResult]  # step_id → result
    final_response: str
    error: str = ""


class BaseAgent:
    """Base class cho tất cả Agent"""
    
    agent_name: str = "base"
    agent_description: str = ""
    
    def __init__(self):
        self.status = AgentStatus.IDLE
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, ToolSchema] = {}
    
    def register_tool(self, schema: ToolSchema, handler: Callable):
        """Đăng ký 1 tool với schema + handler"""
        self._tools[schema.name] = handler
        self._schemas[schema.name] = schema
    
    def get_schemas(self) -> list[ToolSchema]:
        """Trả về tất cả schema để Planner biết"""
        return list(self._schemas.values())
    
    def get_schema(self, tool_name: str) -> Optional[ToolSchema]:
        return self._schemas.get(tool_name)
    
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        """Thực thi 1 tool"""
        handler = self._tools.get(tool_name)
        if not handler:
            return ToolResult(success=False, error=f"Tool '{tool_name}' not found")
        
        try:
            self.status = AgentStatus.RUNNING
            result = handler(**args)
            self.status = AgentStatus.DONE
            
            if isinstance(result, ToolResult):
                return result
            elif isinstance(result, dict):
                return ToolResult(success=True, data=result)
            elif isinstance(result, str):
                return ToolResult(success=True, data={"text": result})
            else:
                return ToolResult(success=True, data=result)
                
        except Exception as e:
            self.status = AgentStatus.FAILED
            return ToolResult(success=False, error=str(e))
    
    def reset(self):
        self.status = AgentStatus.IDLE


class AgentRegistry:
    """Quản lý tất cả Agent trong hệ thống"""
    
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent):
        self._agents[agent.agent_name] = agent
    
    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)
    
    def get_all_schemas(self) -> dict[str, list[ToolSchema]]:
        """Trả về schema của tất cả agent → cho Planner"""
        return {name: agent.get_schemas() for name, agent in self._agents.items()}
    
    def get_all_tools_flat(self) -> list[ToolSchema]:
        """Trả về tất cả tools dạng phẳng"""
        tools = []
        for agent in self._agents.values():
            tools.extend(agent.get_schemas())
        return tools
    
    def execute_tool(self, tool_name: str, args: dict) -> ToolResult:
        """Tìm agent chứa tool và execute"""
        for agent in self._agents.values():
            if tool_name in agent._schemas:
                return agent.execute(tool_name, args)
        return ToolResult(success=False, error=f"No agent has tool '{tool_name}'")
    
    def list_agents(self) -> list[str]:
        return list(self._agents.keys())