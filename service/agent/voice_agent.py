"""
Voice Agent - STT + TTS + Wake Word
Wrap AudioService thành Agent để Planner có thể gọi speak, listen, ask_user
"""

from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceAgent(BaseAgent):
    """Agent giọng nói - STT và TTS"""
    
    agent_name = "voice"
    agent_description = "Text-to-Speech, Speech-to-Text, lắng nghe người dùng"
    
    def __init__(self, audio_service=None):
        super().__init__()
        self._audio = audio_service
        
        self.register_tool(
            ToolSchema(
                name="speak",
                description="Nói với người dùng bằng giọng nói",
                parameters={"text": {"type": "string", "description": "Nội dung cần nói"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._speak
        )
        
        self.register_tool(
            ToolSchema(
                name="listen",
                description="Lắng nghe người dùng nói",
                parameters={"timeout": {"type": "integer", "description": "Thời gian chờ (giây, mặc định 10)"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=10.0
            ),
            self._listen
        )
        
        self.register_tool(
            ToolSchema(
                name="ask_user",
                description="Hỏi người dùng 1 câu và đợi câu trả lời",
                parameters={"question": {"type": "string", "description": "Câu hỏi"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=12.0
            ),
            self._ask_user
        )
        
        self.register_tool(
            ToolSchema(
                name="confirm",
                description="Yêu cầu người dùng xác nhận (có/không)",
                parameters={"message": {"type": "string", "description": "Thông báo cần xác nhận"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=8.0
            ),
            self._confirm
        )
    
    def set_audio(self, audio_service):
        self._audio = audio_service
    
    def _speak(self, text: str) -> ToolResult:
        if self._audio:
            self._audio.speak(text)
            logger.info(f"[Voice] {text}")
            return ToolResult(success=True, data={"spoken": text})
        return ToolResult(success=False, error="Audio service not available")
    
    def _listen(self, timeout: int = 10) -> ToolResult:
        if self._audio:
            text = self._audio.listen(timeout=timeout)
            if text and text != "...":
                return ToolResult(success=True, data={"user_text": text})
            return ToolResult(success=False, error="Không nghe thấy gì")
        return ToolResult(success=False, error="Audio service not available")
    
    def _ask_user(self, question: str) -> ToolResult:
        if self._audio:
            self._audio.speak(question)
            text = self._audio.listen(timeout=10)
            if text and text != "...":
                return ToolResult(success=True, data={"user_response": text})
            return ToolResult(success=False, error="Không có câu trả lời")
        return ToolResult(success=False, error="Audio service not available")
    
    def _confirm(self, message: str) -> ToolResult:
        if self._audio:
            self._audio.speak(message + " Nói có hoặc không.")
            text = self._audio.listen(timeout=8)
            if text:
                confirmed = any(w in text.lower() for w in ["có", "ok", "đồng ý", "yes", "ừ", "chắc"])
                return ToolResult(success=True, data={"confirmed": confirmed, "user_text": text})
        return ToolResult(success=True, data={"confirmed": False})