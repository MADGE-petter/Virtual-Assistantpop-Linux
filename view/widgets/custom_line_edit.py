#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom LineEdit - Pop Assistant
Widget nhập liệu tùy chỉnh hỗ trợ bộ gõ nội bộ (Internal IME)
"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from utils.input_manager import input_manager

class CustomLineEdit(QLineEdit):
    """
    QLineEdit tùy chỉnh bắt sự kiện phím để xử lý tiếng Việt/Trung 
    mà không phụ thuộc vào bộ gõ hệ thống.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_language = 'vi' # Mặc định tiếng Việt

    def keyPressEvent(self, event):
        # Lấy ký tự vừa nhấn
        text = event.text()
        
        if text and text.islower() or text.isalpha():
            # Lấy toàn bộ nội dung hiện tại
            current_content = self.text()
            
            # Sử dụng InputManager để xử lý chuyển đổi (ví dụ: aa -> â)
            processed_text = input_manager.handle_input(
                current_content, 
                text, 
                language=self.current_language
            )
            
            # Cập nhật lại nội dung ô nhập liệu
            self.setText(processed_text)
            
            # Đưa con trỏ về cuối văn bản
            cursor_pos = len(processed_text)
            self.setCursorPosition(cursor_pos)
            
            # Chặn sự kiện mặc định để không bị nhập ký tự gốc (ví dụ: không bị nhập 'a' rồi mới thành 'â')
            event.accept()
            return
        
        # Các phím khác (Enter, Backspace, v.v.) xử lý bình thường
        super().keyPressEvent(event)

    def set_language(self, lang_code):
        """Thay đổi ngôn ngữ nhập liệu (vi, cn, en...)"""
        self.current_language = lang_code
