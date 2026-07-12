"""
Pop Assistant - Admin Panel (Modern Redesign 2026)
Sidebar navigation + Dashboard overview
"""

import os
import sys
from datetime import datetime
if __package__ is None and __name__ == "__main__":
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
    QGridLayout,
)

from admin.controller.admin_controller import AdminController
from admin.model.admin_model import AdminModel
from admin.view.styles import (
    MAIN_WINDOW,
    SIDEBAR,
    SIDEBAR_LOGO,
    SIDEBAR_SUBTITLE,
    SIDEBAR_BUTTON,
    SIDEBAR_BUTTON_DANGER,
    HEADER_FRAME,
    HEADER_TITLE,
    HEADER_BREADCRUMB,
    HEADER_TIME,
    HEADER_STATUS,
    CONTENT_AREA,
    BUTTON_LOGOUT,
    SECTION_TITLE,
    SECTION_SUBTITLE,
    SEPARATOR,
    CARD_FRAME,
    STATS_CARD_VALUE,
    STATS_CARD_LABEL,
    STATS_CARD_ICON,
    PRIMARY,
    SUCCESS,
    WARNING,
    DANGER,
    INFO,
    ACCENT,
    BG_DARK,
    BG_CARD,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER,
)
from admin.view.tabs import ConversationsTab, DatabaseTab, HealthTab, StatsTab, UsersTab


class AdminPanel(QMainWindow):
    """Admin Panel Interface - Sidebar + Content Layout"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pop Assistant - Admin Panel")
        self.setGeometry(100, 100, 1360, 880)
        self.setMinimumSize(1100, 700)

        # Initialize MVC components
        self.admin_model = AdminModel()
        self.admin_controller = AdminController()

        # Connect signals
        self.admin_controller.data_updated.connect(self.on_data_updated)
        self.admin_controller.error_occurred.connect(self.on_error_occurred)

        # Track current page
        self.current_page = "users"
        self.sidebar_buttons = {}

        # Apply styles
        self.setStyleSheet(MAIN_WINDOW)

        # Setup UI
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup main UI with sidebar + content layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        self.create_sidebar(main_layout)

        # ── Right side: Header + Content ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(24, 16, 24, 16)
        right_layout.setSpacing(0)

        # Header
        self.create_header(right_layout)

        # Separator
        sep = QFrame()
        sep.setStyleSheet(SEPARATOR)
        sep.setFixedHeight(1)
        right_layout.addWidget(sep)

        # Content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(CONTENT_AREA)

        # Create pages
        self.users_page = UsersTab(log_callback=self.log_message)
        self.health_page = HealthTab(log_callback=self.log_message)
        self.database_page = DatabaseTab(log_callback=self.log_message)
        self.stats_page = StatsTab(log_callback=self.log_message)
        self.conversations_page = ConversationsTab(log_callback=self.log_message)

        self.content_stack.addWidget(self.users_page)          # index 0
        self.content_stack.addWidget(self.health_page)         # index 1
        self.content_stack.addWidget(self.database_page)       # index 2
        self.content_stack.addWidget(self.stats_page)          # index 3
        self.content_stack.addWidget(self.conversations_page)  # index 4

        right_layout.addWidget(self.content_stack, 1)
        main_layout.addWidget(right_widget, 1)

        # Default: Users active
        self.navigate_to("users", 0)

    # ═══════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════
    def create_sidebar(self, main_layout):
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(SIDEBAR)
        sidebar.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 16)
        sidebar_layout.setSpacing(0)

        # Logo
        logo = QLabel("POP ADMIN")
        logo.setStyleSheet(SIDEBAR_LOGO)
        sidebar_layout.addWidget(logo)

        subtitle = QLabel("Management Console")
        subtitle.setStyleSheet(SIDEBAR_SUBTITLE)
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(24)

        # Navigation buttons
        nav_items = [
            ("users", "  Người dùng", 0),
            ("health", "  Giám sát hệ thống", 1),
            ("database", "  Database", 2),
            ("stats", "  Thống kê", 3),
            ("conversations", "  Trò chuyện", 4),
        ]

        for key, label, index in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(SIDEBAR_BUTTON)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key, i=index: self.navigate_to(k, i))
            sidebar_layout.addWidget(btn)
            sidebar_layout.addSpacing(2)
            self.sidebar_buttons[key] = btn

        sidebar_layout.addStretch()

        # Logout button at bottom
        logout_btn = QPushButton("Đăng xuất")
        logout_btn.setStyleSheet(SIDEBAR_BUTTON_DANGER)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.confirm_logout)
        sidebar_layout.addWidget(logout_btn)

        # Version
        version_label = QLabel("v2.0  •  Pop Assistant")
        version_label.setStyleSheet(SIDEBAR_SUBTITLE)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        # Default: Users active
        self.sidebar_buttons["users"].setChecked(True)

    def navigate_to(self, page_key, index):
        """Navigate to a page"""
        self.current_page = page_key
        self.content_stack.setCurrentIndex(index)

        # Update breadcrumb
        page_names = {
            "users": "Quản lý người dùng",
            "health": "Sức khỏe hệ thống",
            "database": "Quản lý Database",
            "stats": "Thống kê",
            "conversations": "Lịch sử trò chuyện",
        }
        self.breadcrumb_label.setText(f"Home / {page_names.get(page_key, page_key)}")

        # Update sidebar button states
        for key, btn in self.sidebar_buttons.items():
            btn.setChecked(key == page_key)

    # ═══════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════
    def create_header(self, layout):
        """Create header bar"""
        header = QFrame()
        header.setObjectName("header")
        header.setStyleSheet(HEADER_FRAME)
        header.setFixedHeight(64)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(16)

        # Left: Breadcrumb
        left_area = QVBoxLayout()
        left_area.setSpacing(0)

        self.page_title = QLabel("Quản lý người dùng")
        self.page_title.setStyleSheet(HEADER_TITLE)
        left_area.addWidget(self.page_title)

        self.breadcrumb_label = QLabel("Home / Người dùng")
        self.breadcrumb_label.setStyleSheet(HEADER_BREADCRUMB)
        left_area.addWidget(self.breadcrumb_label)

        header_layout.addLayout(left_area)
        header_layout.addStretch()

        # Right: Time + Status
        self.time_label = QLabel()
        self.time_label.setStyleSheet(HEADER_TIME)
        self.update_time()

        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

        header_layout.addWidget(self.time_label)

        self.status_label = QLabel("● Online")
        self.status_label.setStyleSheet(HEADER_STATUS)
        header_layout.addWidget(self.status_label)

        layout.addWidget(header)

    # ═══════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M  |  %d/%m/%Y")
        self.time_label.setText(current_time)

    def log_message(self, message):
        """Log message to database tab"""
        if hasattr(self, 'database_page') and self.database_page:
            self.database_page.log_message(message)
        else:
            print(f"[AdminPanel] {message}")

    def load_data(self):
        """Load initial data"""
        self.refresh_data()

    def refresh_data(self):
        """Refresh all data via controller"""
        try:
            self.admin_controller.get_user_management_data()
            self.admin_controller.get_conversation_history_data()
            self.log_message("✅ Dữ liệu đã được làm mới")
        except Exception as e:
            self.log_message(f"❌ Lỗi làm mới dữ liệu: {e}")

    def on_data_updated(self, data_type, data):
        """Handle data updated signals"""
        if data_type == 'user_management':
            self.update_user_management(data)
        elif data_type == 'conversation_history':
            self.update_conversations(data)

    def on_error_occurred(self, error_message):
        """Handle error signals"""
        QMessageBox.warning(self, "Lỗi", error_message)
        self.log_message(f"❌ Error: {error_message}")

    def update_dashboard(self, data):
        """Update dashboard stats - DEPRECATED, dashboard removed"""
        pass

    def _update_stat_value(self, label, value):
        """Update a stat card value by label - DEPRECATED"""
        pass

    def update_user_management(self, data):
        """Update user management data"""
        pass

    def update_conversations(self, data):
        """Update conversation data"""
        pass

    def confirm_logout(self):
        """Confirm and logout"""
        reply = QMessageBox.question(
            self, "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất khỏi Admin Panel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Xác nhận thoát",
            "Bạn có chắc muốn thoát Admin Panel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            app = QApplication.instance()
            if app:
                app.quit()
            event.accept()
        else:
            event.ignore()


def create_admin_panel():
    """Create admin panel window"""
    return AdminPanel()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Pop Assistant Admin Panel")
    app.setOrganizationName("Pop AI")

    admin_panel = AdminPanel()
    admin_panel.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
