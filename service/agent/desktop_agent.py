"""
Desktop Agent - Thao tác với desktop: mở/tắt app, điều khiển chuột/bàn phím, chụp màn hình
"""

import os
import subprocess
import sys
from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel
from service.agent.agent_logger import log_app_opened


class DesktopAgent(BaseAgent):
    """Agent điều khiển desktop"""
    
    agent_name = "desktop"
    agent_description = "Điều khiển ứng dụng, cửa sổ, chuột, bàn phím"
    
    def __init__(self, app_scanner=None):
        super().__init__()
        self._app_scanner = app_scanner
        self._login_username = None
        self._display_name = "bạn"
        
        # Đăng ký tools
        self.register_tool(
            ToolSchema(
                name="open_app",
                description="Mở ứng dụng trên máy tính",
                parameters={"app_name": {"type": "string", "description": "Tên ứng dụng cần mở"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._open_app
        )
        
        self.register_tool(
            ToolSchema(
                name="close_app",
                description="Đóng ứng dụng đang chạy",
                parameters={"app_name": {"type": "string", "description": "Tên ứng dụng cần đóng"}},
                risk_level=RiskLevel.CONFIRM,
                estimated_time=1.0
            ),
            self._close_app
        )
        
        self.register_tool(
            ToolSchema(
                name="set_volume",
                description="Điều chỉnh âm lượng hệ thống (0-100)",
                parameters={"level": {"type": "integer", "description": "Mức âm lượng 0-100"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=0.5
            ),
            self._set_volume
        )
        
        self.register_tool(
            ToolSchema(
                name="set_brightness",
                description="Điều chỉnh độ sáng màn hình (0-100)",
                parameters={"level": {"type": "integer", "description": "Mức độ sáng 0-100"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=0.5
            ),
            self._set_brightness
        )
        
        self.register_tool(
            ToolSchema(
                name="screenshot",
                description="Chụp ảnh màn hình hiện tại",
                parameters={"save_path": {"type": "string", "description": "Đường dẫn lưu ảnh (tùy chọn)"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._screenshot
        )
    
    def set_app_scanner(self, scanner):
        self._app_scanner = scanner
    
    def set_user_context(self, login_username: str = None, display_name: str = None):
        """Set user context cho logging và habit tracking"""
        self._login_username = login_username
        self._display_name = display_name or "bạn"
    
    @property
    def _user_name(self) -> str:
        """Get current user name for logging"""
        return self._login_username or self._display_name or "user"
    
    def _open_app(self, app_name: str) -> ToolResult:
        """Mở ứng dụng"""
        user_name = self._user_name  # Use internal user context
        try:
            if self._app_scanner:
                result = self._app_scanner.find_app(app_name)
                if result:
                    app_key, app_path = result
                    os.startfile(app_path)
                    # Log app opened (habit tracking + analytics)
                    log_app_opened(app_key, user_name)
                    return ToolResult(success=True, data={"text": f"Đã mở {app_key}", "app": app_key})
            
            # Fallback: thử os.startfile
            try:
                os.startfile(app_name)
                log_app_opened(app_name, user_name)
                return ToolResult(success=True, data={"text": f"Đã mở {app_name}", "app": app_name})
            except:
                pass
            
            # Thử subprocess
            try:
                subprocess.Popen(app_name, shell=True)
                log_app_opened(app_name, user_name)
                return ToolResult(success=True, data={"text": f"Đã mở {app_name}", "app": app_name})
            except:
                pass
            
            return ToolResult(success=False, error=f"Không tìm thấy ứng dụng: {app_name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _close_app(self, app_name: str) -> ToolResult:
        """Đóng ứng dụng"""
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", f"{app_name}.exe"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return ToolResult(success=True, data={"text": f"Đã đóng {app_name}"})
                return ToolResult(success=False, error=f"Không thể đóng {app_name}: {result.stderr}")
            else:
                result = subprocess.run(["pkill", "-f", app_name], capture_output=True, text=True)
                return ToolResult(success=result.returncode == 0, data={"text": f"Đã đóng {app_name}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _set_volume(self, level: int) -> ToolResult:
        """Điều chỉnh âm lượng"""
        try:
            level = max(0, min(100, level))
            if sys.platform == "win32":
                import ctypes
                # Gửi phím volume up/down
                for _ in range(50):  # Reset về 0
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # Volume down
                for _ in range(level // 2):  # Tăng lên level
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume up
                return ToolResult(success=True, data={"text": f"Âm lượng: {level}%"})
            return ToolResult(success=False, error="Chỉ hỗ trợ Windows")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _set_brightness(self, level: int) -> ToolResult:
        """Điều chỉnh độ sáng"""
        try:
            level = max(0, min(100, level))
            if sys.platform == "win32":
                import screen_brightness_control as sbc
                sbc.set_brightness(level)
                return ToolResult(success=True, data={"text": f"Độ sáng: {level}%"})
            return ToolResult(success=False, error="Chỉ hỗ trợ Windows với screen_brightness_control")
        except ImportError:
            return ToolResult(success=False, error="Cần cài screen_brightness_control")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _screenshot(self, save_path: str = None) -> ToolResult:
        """Chụp màn hình"""
        try:
            import pyautogui
            if not save_path:
                save_path = f"screenshot_{int(__import__('time').time())}.png"
            pyautogui.screenshot(save_path)
            return ToolResult(success=True, data={"text": f"Đã chụp màn hình: {save_path}", "path": save_path})
        except ImportError:
            return ToolResult(success=False, error="Cần cài pyautogui")
        except Exception as e:
            return ToolResult(success=False, error=str(e))