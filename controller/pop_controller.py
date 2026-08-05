"""PopController - Facade điều phối chính với AI Agent."""
import os
import sys
import threading

from PyQt6.QtCore import QObject, pyqtSignal

from controller.action import ActionHandler
from controller.conversation_controller import ConversationController
from controller.system_controller import SystemController
from controller.user_controller import UserController
from controller.voice_controller import VoiceController
from model.Sql import SqlService
from service.alert_service import AlertManager
from service.analytics_service import get_analytics_service
from service.AudioService import AudioService
from service.interactive_alert_service import InteractiveAlertService
from service.user_service import UserService
from service.wake_word import WakeWordDetector

# === AI AGENT IMPORTS ===
from service.agent.agent_loop import AgentLoop
from service.agent.gemma_llm_service import get_gemma_service


class PopController(QObject):
    """Facade controller - chỉ điều phối, không xử lý logic chi tiết."""
    
    # Signal để wake up từ thread khác (thread-safe)
    wakeUpRequested = pyqtSignal()
    alertReceived = pyqtSignal(dict)
    
    def __init__(self, view=None, model=None, login_username=None):
        super().__init__()
        self.view = view
        self.login_username = login_username
        
        # State
        self._started = False
        self._active = False
        
        # === KHỞI TẠO SERVICES ===
        self.audio = AudioService(view)
        self.sql = SqlService()
        self.actions = ActionHandler(self.audio, view)
        
        # === AI AGENT SYSTEM ===
        # Agent Loop thay thế ConversationFlowService cũ
        # LLM service sẽ được load async SAU khi UI hiển thị
        self._llm_service = None
        self.agent_loop = AgentLoop(
            audio_service=self.audio,
            sql_service=self.sql,
            app_scanner=None,  # Sẽ set sau
            llm_service=None  # Sẽ set sau khi load async
        )
        self._use_agent_mode = True  # Toggle giữa agent mode và legacy mode
        
        # User service
        self._user_svc = UserService(self.sql)
        if login_username:
            self._user_svc.login_name = login_username
            # Only load display_name if exists, don't fallback to login_username
            # Bot will ask for name if display_name is None
            loaded_name = self._user_svc.get_display_name_by_login(login_username)
            if loaded_name and loaded_name != "bạn":
                self._user_svc.display_name = loaded_name
            # else: leave as None so bot asks for name
        
        # Alert interaction service
        self._interactive_alert_service = InteractiveAlertService(self.audio, view=view)

        # Alert & Analytics - use login username when available, fall back to display name
        analytics_user = self._user_svc.login_name if getattr(self._user_svc, 'login_name', None) and self._user_svc.login_name != "bạn" else getattr(self._user_svc, 'display_name', None) or "bạn"
        self._alert_mgr = AlertManager(
            self.audio,
            self._interactive_alert_service.on_alert,
            30,
            analytics_user,
            interactive_callback=self._interactive_alert_service.on_interactive_alert,
        )
        self._interactive_alert_service.set_alert_manager(self._alert_mgr)
        self._analytics = get_analytics_service(analytics_user or "user")
        self._analytics.start()

        # Ensure app logging uses the canonical login username whenever available
        if login_username:
            try:
                self.actions.app_handler.set_login_name(login_username)
            except Exception:
                pass
        
        # Set app scanner cho Agent Loop
        try:
            from service.app_scanner import AppScanner
            self.agent_loop.set_app_scanner(AppScanner())
        except Exception:
            pass
        
        # === KHỞI TẠO SUB-CONTROLLERS (LEGACY) ===
        self._init_sub_controllers(view)
        
        # LLM will be loaded asynchronously after UI shows
        self._llm_loaded = False
    
    def _init_llm_service(self):
        """Khởi tạo Gemma 4 E4B LLM Service"""
        try:
            print("[PopController] Initializing Gemma 4 E4B LLM Service...")
            self._llm_service = get_gemma_service()
            print("[PopController] Gemma LLM Service loaded successfully!")
            self._llm_loaded = True
            if self._llm_service:
                self.agent_loop.set_llm(self._llm_service)
        except Exception as e:
            print(f"[PopController] Warning: Failed to load Gemma LLM: {e}")
            print("[PopController] Falling back to rule-based planning")
            self._llm_service = None
            self._llm_loaded = True
    
    def load_llm_async(self):
        """Load LLM in background thread after UI is shown."""
        import threading
        thread = threading.Thread(target=self._init_llm_service, daemon=True)
        thread.start()

    def is_llm_available(self) -> bool:
        """Kiểm tra LLM có sẵn sàng không"""
        return self._llm_loaded and self._llm_service is not None and self._llm_service.is_loaded()

    def wait_for_llm(self, timeout=30):
        """Wait for LLM to finish loading."""
        import time
        start = time.time()
        while not self._llm_loaded and time.time() - start < timeout:
            time.sleep(0.1)
        return self._llm_loaded

    def reload_llm(self):
        """Reload LLM Service"""
        try:
            from service.agent.gemma_llm_service import reset_gemma_service
            reset_gemma_service()
            self._llm_loaded = False
            self._init_llm_service()
        except Exception as e:
            print(f"[PopController] Failed to reload LLM: {e}")

    def _init_sub_controllers(self, view):
        """Khởi tạo sub-controllers (legacy)."""
        self.wake_detector = WakeWordDetector(self.audio, view)
        self.voice = VoiceController(self.audio)
        self.voice.init_wake_detector(self.wake_detector)
        self.user = UserController(self._user_svc, self.sql)
        self.system = SystemController(self._alert_mgr, self._analytics)
        self.conversation = ConversationController(
            self.audio,
            self.sql,
            self.actions,
            self.user,
            self._interactive_alert_service,
        )
        
        # === SETUP CALLBACKS ===
        self.voice.on_wake_up = self._request_wake_up
        self.voice.on_go_sleep = self._on_go_sleep
        self.wakeUpRequested.connect(self._do_wake_up)
        self.alertReceived.connect(self._handle_alert_received)
        
        # Inject controller vào view (view không cần biết services)
        if view:
            view.set_controller(self)
    
    # ============================================================
    # PUBLIC API
    # ============================================================
    
    def start(self):
        """Khởi động assistant."""
        if self._started:
            self._active = True
            return
        
        self._started = True
        self._active = True
        self.conversation.set_assistant_active(True)
        
        # Init intent service early to avoid race conditions
        self.conversation.init_intent_service()
        
        self.system.start_monitoring(self.user.get_display_name())
        self._enter_active_mode()
        
        # Load LLM asynchronously after UI is fully shown (delay 1.5s)
        # Use QTimer.singleShot to ensure UI event loop is running
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, self.load_llm_async)
    
    def stop(self):
        """Dừng assistant."""
        self._active = False
        self.conversation.set_assistant_active(False)
        self.voice.stop_wake_word_detection()
        self.system.stop_monitoring()
        self.conversation.end_session()
    
    def sleep(self, manual=True):
        """Vào sleep mode."""
        self.voice.go_to_sleep(manual, self.audio.speak)
    
    def wake(self):
        """Thức dậy từ sleep."""
        self.voice.handle_wake_up()
    
    # ============================================================
    # DELEGATE METHODS 
    # ============================================================
    
    def speak(self, text):
        """Bot nói."""
        return self.voice.speak(text, update_ui=True)
    
    def listen(self):
        """Bot nghe."""
        return self.voice.get_voice_input()

    def handle_user_message(self, text: str):
        """Xử lý tin nhắn từ user."""
        # Process through conversation flow
        if self._llm_service and self._llm_loaded:
            # Use agent loop if available
            if self.agent_loop:
                response = self.agent_loop.process_request(text)
                if response:
                    return response
        else:
            # Fallback to conversation service
            from service.conversation_service import ConversationService
            conv_svc = ConversationService(self.audio, self.sql, self.actions, self.user)
            response = conv_svc.process_exchange(text)
            if response:
                # Return response so view can add it as bot message
                return response
        return None
    
    # ============================================================
    # PRIVATE 
    # ============================================================
    
    def _request_wake_up(self):
        """Callback từ VoiceController khi wake word detected."""
        self.wakeUpRequested.emit()
    
    def _activate_view(self):
        """Activate and show main window (helper to avoid duplication)."""
        if self.view:
            self.view.show()
            self.view.raise_()
            self.view.activateWindow()
    
    def _do_wake_up(self):
        """Thực hiện wake up trên main thread."""
        self.system.set_sleep_mode(False)
        self.system.reset_wellness_timers()
        
        self._activate_view()
        self._start_conversation(from_wake_up=True)
    
    def _on_go_sleep(self):
        """Callback khi vào sleep."""
        self.system.set_sleep_mode(True)
        if self.view:
            self.view.hide()
    
    def _on_idle(self):
        """Callback khi idle timeout."""
        self.sleep(manual=False)
    
    def _on_alert(self, alert_data):
        """Callback khi có alert."""
        self.alertReceived.emit(alert_data)
    
    def _handle_alert_received(self, alert_data):
        if self.view:
            self.view.show_alert_notification(alert_data)
    
    def _on_interactive_alert(self, alert, action, context=None):
        """Callback khi có interactive alert - xử lý conversation với user"""
        try:
            if action == 'ask_details':
                # Hỏi user có muốn xem chi tiết không
                message = f"{alert.message}. Bạn có muốn xem tiến trình chi tiết không?"
                self.audio.speak(message)
                
            elif action == 'remind':
                # Nhắc lại cảnh báo
                message = f"Nhắc nhở: {alert.message}. Bạn có muốn xem tiến trình chi tiết không?"
                self.audio.speak(message)
                
            elif action == 'show_details':
                # Hiển thị top processes và hỏi có muốn đóng không
                from service.system_monitoring_service import (
                    format_process_list,
                    get_top_cpu_processes,
                    get_top_ram_processes,
                )
                
                if alert.metric == 'ram':
                    processes = get_top_ram_processes(5)
                    process_list = format_process_list(processes, 'ram')
                    message = f"Top 5 ứng dụng dùng RAM nhiều nhất:\n{process_list}\n\nBạn có muốn đóng ứng dụng nào không?"
                else:  # temperature
                    processes = get_top_cpu_processes(5)
                    process_list = format_process_list(processes, 'cpu')
                    message = f"Top 5 ứng dụng dùng CPU nhiều nhất:\n{process_list}\n\nBạn có muốn đóng ứng dụng nào không?"
                
                # Lưu context để parse selection sau
                self._interactive_context = {
                    'metric': alert.metric,
                    'top_processes': processes
                }
                
                self.audio.speak(message)
                
            elif action == 'ask_close_app':
                # Hỏi user muốn đóng app nào
                message = "Bạn muốn đóng ứng dụng nào? Hãy nói tên ứng dụng hoặc số thứ tự (1, 2, 3...)"
                self.audio.speak(message)
                
            elif action == 'close_success':
                # Thông báo đóng thành công
                closed_apps = context.get('closed_apps')
                failed_apps = context.get('failed_apps')
                if closed_apps:
                    app_names = ', '.join([app.get('name', 'ứng dụng') for app in closed_apps])
                    if failed_apps:
                        failed_names = ', '.join([app.get('name', 'ứng dụng') for app in failed_apps])
                        message = f"Đã đóng {app_names} thành công. Không thể đóng {failed_names}."
                    else:
                        message = f"Đã đóng {app_names} thành công."
                else:
                    closed_app = context.get('closed_app', {})
                    app_name = closed_app.get('name', 'ứng dụng')
                    message = f"Đã đóng {app_name} thành công."
                self.audio.speak(message)
                
            elif action == 'close_failed':
                # Thông báo đóng thất bại
                failed_apps = context.get('failed_apps')
                if failed_apps:
                    failed_names = ', '.join([app.get('name', 'ứng dụng') for app in failed_apps])
                    message = f"Không thể đóng {failed_names}. Vui lòng thử lại hoặc đóng thủ công."
                else:
                    failed_app = context.get('failed_app', {})
                    app_name = failed_app.get('name', 'ứng dụng')
                    message = f"Không thể đóng {app_name}. Vui lòng thử lại hoặc đóng thủ công."
                self.audio.speak(message)
                
        except Exception as e:
            print(f"[PopController] Error in interactive alert: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_gesture(self, gesture_type):
        """Callback từ gesture service."""
        self.handle_gesture(gesture_type)
    
    # ============================================================
    # PRIVATE - Conversation management
    # ============================================================
    
    def _enter_active_mode(self):
        """Vào active mode - hiện app và bắt đầu conversation."""
        self._activate_view()
        self.system.reset_wellness_timers()
        self._start_conversation()
        self.voice.start_idle_monitor(self._on_idle)
    
    def _start_conversation(self, from_wake_up: bool = False):
        """Bắt đầu conversation thread."""
        threading.Thread(target=self._run_conversation, args=(from_wake_up,), daemon=True).start()
    
    def _run_conversation(self, from_wake_up: bool = False):
        """Conversation main loop - hỗ trợ cả Agent mode và Legacy mode."""
        try:
            if self._use_agent_mode:
                self._run_agent_conversation(from_wake_up)
            else:
                self._run_legacy_conversation(from_wake_up)
        except Exception as e:
            print(f"[PopController] Conversation error: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_agent_conversation(self, from_wake_up: bool = False):
        """Agent mode conversation loop."""
        user_name = self.user.get_display_name() or ""
        self.agent_loop.start_session(user_name)
        
        # Vòng lặp chính
        while self._active:
            try:
                # Listen
                user_text = self.voice.get_voice_input()
                if not user_text or user_text == "...":
                    continue
                
                # Process qua Agent pipeline
                response = self.agent_loop.process_request(user_text)
                
                # Nếu response rỗng (tool đã speak trực tiếp), không speak lại
                if response:
                    self.audio.speak(response)
                    
            except Exception as e:
                print(f"[AgentLoop] Error: {e}")
                import traceback
                traceback.print_exc()
    
    def _run_legacy_conversation(self, from_wake_up: bool = False):
        """Legacy conversation loop (giữ nguyên)."""
        self.conversation.start_session()
        self.conversation.run_first_interaction(
            get_input_callback=self.voice.get_voice_input,
            speak_callback=self.audio.speak,
            from_wake_up=from_wake_up
        )
        self.conversation.run_main_loop(
            get_input_callback=self.voice.get_voice_input,
            on_idle_callback=lambda: self.sleep(manual=False),
            idle_timeout=45
        )
    
    # ============================================================
    # LEGACY COMPATIBILITY
    # ============================================================
    
    @property
    def assistant_active(self):
        return self._active
    
    @property  
    def assistant_started(self):
        return self._started
    
    def set_wake_word_enabled(self, enabled):
        """Legacy."""
        self.voice.wake_word_enabled = enabled
    
    def classify_intent_simple(self, text):
        """Legacy."""
        from service.intern import IntentClassifier
        return IntentClassifier.classify(text)
    
    # ============================================================
    # AI AGENT API
    # ============================================================
    
    def enable_agent_mode(self, enabled: bool = True):
        """Bật/tắt Agent mode."""
        self._use_agent_mode = enabled
    
    def set_llm_service(self, llm_service):
        """Gắn LLM service vào Agent Loop."""
        self.agent_loop.set_llm(llm_service)
        print("[PopController] LLM service integrated")
    
    def get_agent_loop(self) -> AgentLoop:
        """Lấy Agent Loop để debug/kiểm tra."""
        return self.agent_loop
    
    def get_agent_registry(self):
        """Lấy Agent Registry."""
        return self.agent_loop.registry
    
    def list_agents(self) -> list:
        """Liệt kê tất cả agents."""
        return self.agent_loop.registry.list_agents()
    
    def list_tools(self) -> list:
        """Liệt kê tất cả tools."""
        tools = self.agent_loop.registry.get_all_tools_flat()
        return [(t.name, t.description) for t in tools]
