"""Conversation flow service - xử lý luồng hội thoại và idle timeout."""
import time
from typing import Callable, Optional

from controller.interfaces import (
    IActionHandler,
    IAudioService,
    ISqlService,
    IUserController,
)
from service.conversation_service import ConversationService
from service.interactive_alert_service import InteractiveAlertService
from service.memory_service import MemoryService


class ConversationFlowService:
    def __init__(
        self,
        audio_service: IAudioService,
        sql_service: ISqlService,
        action_handler: IActionHandler,
        user_controller: IUserController,
        interactive_alert_service: Optional[InteractiveAlertService] = None,
    ):
        self.audio = audio_service
        self.sql = sql_service
        self.actions = action_handler
        self.user = user_controller
        self.interactive_alert_service = interactive_alert_service

        self._assistant_active = False
        self._session_id: Optional[int] = None
        self._last_input: Optional[str] = None

        self._conversation_service = None
        self._memory_service = None
        self._first_greeting_done = False
        self._pending_habit_app: Optional[str] = None  # App đang chờ user xác nhận mở

    def init_intent_service(self):
        if self._conversation_service:
            self._conversation_service.init_intent_service()

    def start_session(self) -> None:
        user_name = self.user.get_display_name() or "guest"
        self._session_id = self.sql.start_session(user_name)
        print(f"[ConversationFlowService] Session started: {self._session_id}")

    def end_session(self) -> None:
        if self._session_id:
            self.sql.end_session(self._session_id)
            print(f"[ConversationFlowService] Session ended: {self._session_id}")
            self._session_id = None

    def run_main_loop(
        self,
        get_input_callback: Callable[[], Optional[str]],
        on_idle_callback: Optional[Callable] = None,
        idle_timeout: int = 15,
    ) -> None:
        print("[ConversationFlowService] Main loop starting...")
        self._assistant_active = True
        last_interaction = time.time()

        try:
            while self._assistant_active:
                if getattr(self.audio, "is_speaking", False):
                    last_interaction = time.time()
                    time.sleep(0.1)
                    continue

                idle_time = time.time() - last_interaction
                if idle_time > idle_timeout:
                    if on_idle_callback:
                        on_idle_callback()
                    break

                user_input = get_input_callback()

                if not user_input or user_input in ["...", "", None, 0]:
                    time.sleep(1)
                    continue

                if user_input == self._last_input:
                    time.sleep(1)
                    continue

                self._last_input = user_input
                last_interaction = time.time()

                if self._should_exit(user_input):
                    self._assistant_active = False
                    break

                self._process_exchange(user_input)

        except Exception as e:
            print(f"[ConversationFlowService] Error in main loop: {e}")
            import traceback

            traceback.print_exc()

    def run_first_interaction(
        self,
        get_input_callback: Callable[[], Optional[str]],
        speak_callback: Optional[Callable] = None,
        from_wake_up: bool = False,
    ) -> None:
        user_name = self.user.get_display_name()

        if user_name == "bạn" or not user_name:
            greeting = "Chào bạn! Tôi là Pop. Bạn có thể cho tôi biết tên của bạn được không?"
            if speak_callback:
                speak_callback(greeting)
            else:
                self.audio.speak(greeting)

            user_input = get_input_callback()
            if user_input and user_input not in ["...", "", None, 0]:
                self._process_exchange(user_input, speak_callback)
        else:
            if not self._first_greeting_done or from_wake_up:
                if from_wake_up:
                    greeting = f"Pop đây! Chào {user_name}, bạn cần giúp gì?"
                else:
                    greeting = f"Chào {user_name}! Rất vui được gặp lại bạn. Bạn cần mình giúp gì?"
                
                # Nói greeting TRƯỚC, sau đó mới query habit suggestion (non-blocking)
                if speak_callback:
                    speak_callback(greeting)
                else:
                    self.audio.speak(greeting)
                    self.audio.wait_until_speaking_done()
                self._first_greeting_done = True
                
                # Query habit suggestion sau khi đã nói greeting - không block wake up
                self._speak_habit_suggestion_if_any(speak_callback)
    
    def _get_habit_suggestion(self) -> Optional[str]:
        """Lấy gợi ý thói quen - có timeout để không block quá lâu."""
        try:
            import threading
            
            result = [None]  # Dùng list để mutable trong closure
            
            def _query():
                try:
                    from controller.habit_tracker import get_habit_tracker
                    
                    user_id = 1
                    try:
                        user_name = self.user.get_display_name()
                        login_name = self.user.get_login_name() if hasattr(self.user, 'get_login_name') else None
                        lookup_name = login_name or user_name
                        if lookup_name and lookup_name not in ("bạn", "guest", None):
                            uid = self.sql.get_or_create_user(lookup_name)
                            if uid:
                                user_id = uid
                    except Exception:
                        pass
                    
                    tracker = get_habit_tracker()
                    suggestions = tracker.get_suggestions(user_id)
                    
                    if suggestions:
                        top = suggestions[0]
                        app_name = top.get('app', '')
                        confidence = top.get('confidence', 0)
                        count = top.get('count', 0)
                        
                        if confidence >= 0.6 and app_name:
                            self._pending_habit_app = app_name
                            result[0] = f"Gợi ý: Bạn thường dùng {app_name} vào giờ này ({count} lần gần đây). Có muốn mở không?"
                except Exception as e:
                    print(f"[ConversationFlowService] Error getting habit suggestion: {e}")
            
            thread = threading.Thread(target=_query, daemon=True)
            thread.start()
            thread.join(timeout=1.5)  # Timeout 1.5s - không block quá lâu
            
            return result[0]
        except Exception as e:
            print(f"[ConversationFlowService] Error in _get_habit_suggestion: {e}")
            return None
    
    def _speak_habit_suggestion_if_any(self, speak_callback):
        """Nói habit suggestion nếu có, chạy trên thread riêng để không block."""
        try:
            import threading
            
            def _query_and_speak():
                suggestion = self._get_habit_suggestion()
                if suggestion:
                    if speak_callback:
                        speak_callback(suggestion)
                    else:
                        self.audio.speak(suggestion)
            
            thread = threading.Thread(target=_query_and_speak, daemon=True)
            thread.start()
        except Exception as e:
            print(f"[ConversationFlowService] Error in _speak_habit_suggestion: {e}")

    def stop(self) -> None:
        self._assistant_active = False

    def set_assistant_active(self, active: bool) -> None:
        self._assistant_active = active

    def _get_conversation_service(self):
        if self._conversation_service is None:
            self._conversation_service = ConversationService(
                self.audio,
                self.user,
                self.actions,
            )
            if self._memory_service is None:
                self._memory_service = MemoryService(self.sql)
            self._conversation_service.init_memory_service(self._memory_service)
        return self._conversation_service

    def _process_exchange(
        self,
        user_input: str,
        speak_callback: Optional[Callable] = None,
    ) -> str:
        if self._is_interactive_response(user_input):
            return ""

        # Kiểm tra nếu có pending habit suggestion và user đồng ý mở
        if self._pending_habit_app:
            user_lower = user_input.lower().strip()
            agree_keywords = ["mở cho tôi", "mở đi", "có", "ok", "oke", "okay", 
                            "ừ", "ừm", "uh", "đồng ý", "mở", "yes", "yeah", "yep"]
            if any(kw in user_lower for kw in agree_keywords):
                app_to_open = self._pending_habit_app
                self._pending_habit_app = None  # Clear pending
                
                # Mở app qua action handler
                from service.conversation_service import ActionResult
                result = self.actions.handle("open_app", app_to_open, 
                                            self.user.get_display_name() or "guest", None)
                response = result.text if isinstance(result, ActionResult) else str(result)
                
                if speak_callback:
                    speak_callback(response)
                else:
                    self.audio.speak(response)
                return response

        service = self._get_conversation_service()
        user_name = self.user.get_display_name() or "guest"
        session_id = self._session_id if self._session_id else 1
        return service.process_exchange(user_input, speak_callback, user_name, session_id)

    def _is_interactive_response(self, user_input: str) -> bool:
        if not self.interactive_alert_service:
            return False

        return self.interactive_alert_service.try_handle_response(user_input)

    def _should_exit(self, user_input: str) -> bool:
        service = self._get_conversation_service()
        return service.should_exit(user_input)
