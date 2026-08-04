#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom LineEdit - Pop Assistant
Widget nhập liệu tùy chỉnh hỗ trợ bộ gõ nội bộ (Internal IME)
"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from utils.input_manager import input_manager


class CustomLineEdit(QLineEdit):
    """QLineEdit tùy chỉnh bắt sự kiện phím để xử lý tiếng Việt/Trung mà không phụ thuộc vào bộ gõ hệ thống."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_language = 'vi'  # Mặc định tiếng Việt
        self._last_text = ""

    def keyPressEvent(self, event: QKeyEvent):
        # Lấy ký tự vừa nhấn
        text = event.text()
        
        if event.key() == Qt.Key.Key_Space:
            # Xử lý auto-correct khi bấm space
            current_text = self.text()
            words = current_text.rsplit(' ', 1)
            if len(words) == 2:
                last_word = words[1]
                corrected = input_manager._get_best_correction(last_word)
                if corrected != last_word:
                    new_text = words[0] + ' ' + corrected
                    self.setText(new_text)
                    self.setCursorPosition(len(new_text))
                    event.accept()
                    return
        
        # Gọi method gốc
        super().keyPressEvent(event)
        
        # Sau khi nhập, xử lý Telex
        current_text = self.text()
        
        if len(current_text) > len(self._last_text):
            # Có ký tự mới được thêm
            new_char = current_text[len(self._last_text):]
            if new_char.isalpha():
                # Xử lý Telex
                processed = input_manager.process_telex(current_text)
                if processed != current_text:
                    self.setText(processed)
                    self.setCursorPosition(len(processed))
        
        self._last_text = self.text()

    def set_language(self, lang_code):
        self.current_language = lang_code
