#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Login Launcher
Chạy giao diện đăng nhập
"""

import os
import sys
os.environ['QT_IM_MODULE'] = 'fcitx'
os.environ['XMODIFIERS'] = '@im=fcitx'
os.environ['GTK_IM_MODULE'] = 'fcitx'

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main function to run login application"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Pop Assistant Login")
        app.setOrganizationName("Pop AI")
        app.setQuitOnLastWindowClosed(False)  # Don't quit when login dialog closes
        
        # Set application icon
        try:
            from PyQt6.QtGui import QIcon
            from utils.paths import resource_path
            icon_path = resource_path('assets', 'icon.png')
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
            else:
                logger.warning(f"[Login] Icon not found: {icon_path}")
        except Exception as e:
            logger.error(f"[Login] Could not set icon: {e}")

        # Import temperature_monitor để quản lý OHM lifecycle
        _monitor_ref = None
        try:
            from model.temperature_monitor import _monitor
            _monitor_ref = _monitor
        except Exception as e:
            logger.warning(f"[Login] Không import được temperature_monitor: {e}")
        
        def on_app_exit():
            try:
                if _monitor_ref:
                    _monitor_ref.stop_ohm()
            except Exception as e:
                logger.error(f"[Login] Lỗi dừng OHM: {e}")
        app.aboutToQuit.connect(on_app_exit)

        from service.login_service import LoginService
        from view.components.login_view import LoginView
        from main import create_main_window

        # Tạo Service ở Controller level (login.py đóng vai trò Controller)
        login_service = LoginService()
        login_window = None
        main_window = None
        
        def on_login_success(username):
            logger.info(f"Login successful: {username}")
            # View đã show toast "Đăng nhập thành công!" rồi, không cần show thêm
            nonlocal main_window
            main_window = create_main_window(username)
            if main_window:
                main_window.show()
                logger.info("Main window shown")
                # Close login window
                if login_window:
                    login_window.close()
        
        login_window = LoginView(login_service)
        login_window.login_success.connect(on_login_success)
        result = login_window.exec()
        
        # Start the application event loop
        sys.exit(app.exec())
            
    except ImportError as e:
        logger.error(f"Chi tiết lỗi: {e}")
        input("Nhấn Enter để thoát...")
    except Exception as e:
        logger.error(f"Lỗi khởi động ứng dụng: {e}")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
