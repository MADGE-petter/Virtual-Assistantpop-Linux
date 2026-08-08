"""
Login View - Dialog Components
Reusable dialog widgets for login, register.
"""

import random
import string
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget
)

from view.components.login_styles import get_register_dialog_qss, get_toast_qss


class RegisterDialog(QDialog):
    """User registration dialog"""
    
    registered = pyqtSignal(str, str)  # username, password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RegisterDialog")
        self.setWindowTitle("Đăng ký")
        self.setFixedSize(400, 450)
        self.setModal(True)
        self.setStyleSheet(get_register_dialog_qss())
        
        self._captcha_text = ""
        self._setup_ui()
        self._generate_captcha()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Đăng ký tài khoản")
        title.setObjectName("DialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setObjectName("InputField")
        self.username_input.setPlaceholderText("Tên đăng ký")
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setObjectName("InputField")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mật khẩu đăng ký")
        layout.addWidget(self.password_input)
        
        # Captcha
        captcha_container = QWidget()
        captcha_container.setFixedHeight(50)
        captcha_layout = QHBoxLayout(captcha_container)
        captcha_layout.setSpacing(15)
        captcha_layout.setContentsMargins(0, 0, 0, 0)
        
        self.captcha_input = QLineEdit()
        self.captcha_input.setObjectName("CaptchaInput")
        self.captcha_input.setPlaceholderText("Mã captcha")
        self.captcha_input.setMaxLength(4)
        
        self.captcha_button = QPushButton()
        self.captcha_button.setObjectName("CaptchaButton")
        self.captcha_button.setFixedSize(60, 48)
        self.captcha_button.clicked.connect(self._generate_captcha)
        
        captcha_layout.addWidget(self.captcha_input)
        captcha_layout.addWidget(self.captcha_button)
        captcha_layout.addStretch()
        
        layout.addWidget(captcha_container)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.register_btn = QPushButton("Đăng ký")
        self.register_btn.setObjectName("PrimaryButton")
        self.register_btn.clicked.connect(self._on_register)
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.setObjectName("SecondaryButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def _generate_captcha(self):
        self._captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.captcha_button.setText(self._captcha_text)
        self.captcha_input.clear()
        self.captcha_input.setFocus()
    
    def _on_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        captcha_entered = self.captcha_input.text().strip().upper()
        
        if not username or not password or not captcha_entered:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Lỗi", "Tên phải có ít nhất 3 ký tự!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return
        
        if captcha_entered != self._captcha_text:
            QMessageBox.warning(self, "Lỗi", "Mã captcha không đúng!")
            self._generate_captcha()
            return
        
        self.registered.emit(username, password)
        self.accept()


class ToastLabel(QLabel):
    """Toast notification label with auto-hide"""
    
    def __init__(self, message: str, is_success: bool = True, parent=None):
        super().__init__(message, parent)
        self.setObjectName("ToastLabel")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setStyleSheet(get_toast_qss(is_success))
        self.adjustSize()
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, self.deleteLater)
    
    def show_at_top_center(self, parent_widget: QWidget):
        """Position toast at top center of parent"""
        x = (parent_widget.width() - self.width()) // 2
        y = 20
        self.move(x, y)
        self.show()
        self.raise_()