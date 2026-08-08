"""
Login View - Main Login Dialog
Clean, modular login view using component dialogs.
"""

import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QApplication, QWidget
)
from PyQt6.QtGui import QPixmap

from view.components.login_styles import get_login_dialog_qss
from view.components.login_dialogs import RegisterDialog, ToastLabel
from view.styles.theme import COLORS, SPACING, RADIUS, LAYOUT


class LoginView(QDialog):
    """Main login dialog - clean and modular"""
    
    login_success = pyqtSignal(str)
    
    def __init__(self, login_service):
        super().__init__()
        
        if login_service is None:
            raise ValueError("login_service is required - View must receive Service from Controller")
        
        self.login_service = login_service
        self.settings = self.login_service.load_settings()
        
        self.setObjectName("LoginDialog")
        self.setWindowTitle("POP Assistant")
        self.setFixedSize(380, 460)
        self.setModal(True)
        self.setStyleSheet(get_login_dialog_qss())
        
        self._setup_ui()
        self._load_window_icon()
    
    def _load_window_icon(self):
        """Load POP.png as window icon"""
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "POP.png")
        icon_path = os.path.abspath(icon_path)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                self.setWindowIcon(pixmap)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(48, 48, 48, 48)
        
        # Title - centered with proper spacing
        title = QLabel("POP Assistant")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add spacer after title
        layout.addSpacing(32)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setObjectName("InputField")
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.username_input.setFocus()
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setObjectName("InputField")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mật khẩu")
        layout.addWidget(self.password_input)
        
        # Add spacer before button
        layout.addSpacing(16)
        
        # Login button
        self.login_btn = QPushButton("Đăng nhập")
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)
        
        # Add spacer before register link
        layout.addSpacing(24)
        
        # Register link
        register_layout = QHBoxLayout()
        register_layout.addStretch()
        
        register_label = QLabel("Chưa có tài khoản? Đăng ký")
        register_label.setObjectName("LinkLabel")
        register_label.setCursor(Qt.CursorShape.PointingHandCursor)
        register_label.mousePressEvent = self._show_register_dialog
        register_layout.addWidget(register_label)
        register_layout.addStretch()
        
        layout.addLayout(register_layout)
        
        # Bottom stretch to center everything vertically
        layout.addStretch()
    
    def _show_register_dialog(self, event):
        """Show registration dialog"""
        dialog = RegisterDialog(self)
        dialog.registered.connect(self._on_user_registered)
        dialog.exec()
    
    def _on_user_registered(self, username: str, password: str):
        """Handle successful registration"""
        if self.login_service.save_new_user(username, password):
            self.username_input.setText(username)
            self.password_input.clear()
            self._show_toast("Đăng ký thành công!", True)
        else:
            self._show_toast("Đăng ký thất bại!", False)
    
    def _on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self._show_toast("Vui lòng nhập đầy đủ thông tin!", False)
            return
        
        if self.login_service.authenticate_user(username, password):
            self._show_toast("Đăng nhập thành công!", True)
            self.login_success.emit(username)
        else:
            if self.login_service.user_exists(username):
                self._show_toast("Mật khẩu không đúng!", False)
            else:
                self._show_toast("Tên đăng nhập không tồn tại!", False)
    
    def _show_toast(self, message: str, is_success: bool = True):
        """Show toast notification"""
        toast = ToastLabel(message, is_success, self)
        toast.show_at_top_center(self)
    
    def save_settings(self):
        """Save settings via service"""
        self.login_service.save_settings(self.settings)


def main():
    """Test login view standalone"""
    app = QApplication(sys.argv)
    
    # Mock login service for testing
    class MockLoginService:
        def load_settings(self):
            return {
                "auto_start_assistant": True,
                "assistant_delay": 1000,
                "speech_recognition": True,
                "text_to_speech": True,
                "volume": 80,
                "speech_rate": 1.0,
            }
        
        def save_settings(self, settings):
            print("Settings saved:", settings)
        
        def authenticate_user(self, username, password):
            return username == "admin" and password == "123456"
        
        def user_exists(self, username):
            return username == "admin"
        
        def save_new_user(self, username, password):
            print(f"New user: {username}")
            return True
    
    login_view = LoginView(MockLoginService())
    login_view.login_success.connect(lambda u: print(f"Login success: {u}"))
    login_view.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()