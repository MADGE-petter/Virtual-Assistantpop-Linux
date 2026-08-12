#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - PyQt6 Interface
Trợ lý giọng nói thông minh với giao diện hiện đại
"""

import os
import sys
from utils.logger import get_logger

logger = get_logger(__name__)


def create_main_window(username):
    """Create main window with proper MVC structure."""
    try:
        logger.info(f"Creating main window for user: {username}")

        from controller.pop_controller import PopController
        from view.pop_view import PopView
        from PyQt6.QtWidgets import QApplication
        
        view = PopView()
        view.user_name = username
        controller = PopController(view, login_username=username)
        controller.start()
        
        # Connect close event to properly stop controller and quit app
        def on_close():
            logger.info("Closing application...")
            controller.stop()
            QApplication.quit()
        
        view.close_application = on_close
        
        return view
    except Exception as e:
        logger.error(f"Error creating main window: {e}")
        import traceback
        traceback.print_exc()
        return None
