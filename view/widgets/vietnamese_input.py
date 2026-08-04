"""Vietnamese Input Widgets - Wrapper cho QTextEdit và QLineEdit với SmartInputManager."""

from PyQt6.QtWidgets import QTextEdit, QLineEdit, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from utils.input_manager import input_manager


class VietnameseInputTextEdit(QTextEdit):
    """QTextEdit với hỗ trợ gõ Telex và auto-correct tiếng Việt."""
    
    textChangedWithInput = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_text = ""
        self.textChanged.connect(self._on_text_changed)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Xử lý phím bấm với SmartInputManager."""
        if event.key() == Qt.Key.Key_Space:
            # Xử lý auto-correct khi bấm space
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            current_text = self.toPlainText()
            
            # Lấy từ cuối cùng trước space
            words = current_text.rsplit(' ', 1)
            if len(words) == 2:
                last_word = words[1]
                corrected = input_manager._get_best_correction(last_word)
                if corrected != last_word:
                    new_text = words[0] + ' ' + corrected
                    self.setPlainText(new_text)
                    # Di chuyển cursor về cuối
                    cursor = self.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.setTextCursor(cursor)
                    event.accept()
                    return
        
        # Gọi method gốc
        super().keyPressEvent(event)
        
        # Sau khi nhập, xử lý Telex
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        current_text = self.toPlainText()
        
        if len(current_text) > len(self._last_text):
            # Có ký tự mới được thêm
            new_char = current_text[len(self._last_text):]
            if new_char.isalpha():
                # Xử lý Telex
                processed = input_manager.process_telex(current_text)
                if processed != current_text:
                    self.setPlainText(processed)
                    cursor = self.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.setTextCursor(cursor)
        
        self._last_text = self.toPlainText()


class VietnameseInputLineEdit(QLineEdit):
    """QLineEdit với hỗ trợ gõ Telex và auto-correct tiếng Việt."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_text = ""
    
    def keyPressEvent(self, event: QKeyEvent):
        """Xử lý phím bấm với SmartInputManager."""
        if event.key() == Qt.Key.Key_Space:
            # Xử lý auto-correct khi bấm space
            current_text = self.text()
            
            # Lấy từ cuối cùng trước space
            words = current_text.rsplit(' ', 1)
            if len(words) == 2:
                last_word = words[1]
                corrected = input_manager._get_best_correction(last_word)
                if corrected != last_word:
                    new_text = words[0] + ' ' + corrected
                    self.setText(new_text)
                    # Di chuyển cursor về cuối
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
