import os
import sys
import time

from PyQt6.QtCore import QPoint, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from view.widgets import (
    AudioDialog,
    HistoryUsageDialog,
    HistoryWindow,
    PersonalInfoDialog,
    SettingsDialog,
)
from view.widgets.modern_widgets import AIOrbWidget, ChatBubble

# New modular components
from view.components import (
    PremiumBackground,
    HeaderWidget,
    ConversationArea,
    InputArea,
)


class SoundWaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.animation_offset = 0
        self.setMinimumHeight(180)
        self.setMinimumWidth(300)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        for i in range(4):
            radius = 20 + (i * 20) + (self.animation_offset % 15)
            alpha = max(0.1, 0.7 - (i * 0.15))
            
            gradient = QRadialGradient(center_x, center_y, radius)
            gradient.setColorAt(0, QColor(0, 255, 136, int(alpha * 255)))
            gradient.setColorAt(0.7, QColor(0, 200, 120, int(alpha * 200)))
            gradient.setColorAt(1, QColor(0, 150, 100, int(alpha * 100)))
            
            painter.setPen(QPen(QColor(0, 255, 136, int(alpha * 255)), 2))
            painter.setBrush(QBrush(gradient))
            
            painter.drawEllipse(center_x - radius, center_y - radius, 
                              radius * 2, radius * 2)
        
        orb_gradient = QRadialGradient(center_x, center_y, 25)
        orb_gradient.setColorAt(0, QColor(150, 255, 200))
        orb_gradient.setColorAt(0.5, QColor(0, 255, 136))
        orb_gradient.setColorAt(1, QColor(0, 200, 100))
        
        painter.setPen(QPen(QColor(0, 255, 136, 150), 2))
        painter.setBrush(QBrush(orb_gradient))
        painter.drawEllipse(center_x - 25, center_y - 25, 50, 50)
        
        painter.end()
    
    def update_animation(self):
        self.animation_offset += 1
        self.update()


class PopView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_name = "User"
        self._controller = None
        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        self.setWindowTitle("POP Assistant")
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)
        screen = QApplication.primaryScreen()
        if screen:
            center = screen.availableGeometry().center()
            self.move(
                center.x() - self.width() // 2,
                center.y() - self.height() // 2
            )
        self.setStyleSheet("""
            QMainWindow { 
                background: transparent; 
                border-radius: 20px;
            }
            #centralWidget { 
                background: transparent; 
                border-radius: 20px;
            }
        """)

    def setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = HeaderWidget()
        self.header.minimize_clicked.connect(self.showMinimized)
        self.header.maximize_clicked.connect(self._toggle_maximize)
        self.header.close_clicked.connect(self.close)
        main_layout.addWidget(self.header)

        self.conversation = ConversationArea()
        main_layout.addWidget(self.conversation, stretch=1)

        self.input_area = InputArea()
        self.input_area.send_message.connect(self._handle_send)
        main_layout.addWidget(self.input_area)

        self.background = PremiumBackground(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.lower()

        self._header_bg_opacity = 0.0
        self.conversation.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self.conversation.verticalScrollBar().rangeChanged.connect(self._on_scroll)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _on_scroll(self, *args):
        sb = self.conversation.verticalScrollBar()
        scroll_y = sb.value()
        max_scroll = sb.maximum()
        if max_scroll <= 0:
            target = 0.0
        else:
            target = min(1.0, scroll_y / 30.0)
        self._header_bg_opacity = target
        self.header.set_bg_opacity(target)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())

    def _handle_send(self, text: str):
        self.conversation.add_message(text, is_user=True)
        if self._controller:
            self._controller.handle_user_message(text)
        else:
            self.conversation.add_message(
                f"Echo: {text}", is_user=False
            )

    def update_user_text(self, text: str):
        """Update user input field text (called by AudioService during listening)."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._do_update_user_text(text))

    def _do_update_user_text(self, text: str):
        if hasattr(self, 'input_area') and hasattr(self.input_area, 'text_input'):
            self.input_area.text_input.setPlainText(text)

    def update_bot_text(self, text: str):
        """Update bot message bubble (called by AudioService during speaking)."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._do_update_bot_text(text))

    def _do_update_bot_text(self, text: str):
        if hasattr(self, 'conversation'):
            self.conversation.add_message(text, is_user=False)

    def set_controller(self, controller):
        self._controller = controller

    def show_message(self, text: str, is_user: bool = False):
        self.conversation.add_message(text, is_user)

    def set_status(self, status: str):
        status_map = {
            "online": ("#00FFAA", "Online"),
            "listening": ("#00CCFF", "Listening..."),
            "thinking": ("#FFB800", "Thinking..."),
            "speaking": ("#00FFAA", "Speaking..."),
            "offline": ("#5A606E", "Offline"),
        }
        color, text = status_map.get(status, ("#5A606E", status))
        self.header.model_selector.setStyleSheet(
            self.header.model_selector.styleSheet() + f"QComboBox {{ border: 1px solid {color}; }}"
        )

    def set_conversation_title(self, title: str):
        self.header.set_conversation_title(title)

    def set_model(self, model_name: str):
        self.conversation.set_model(model_name)

    def current_model(self) -> str:
        return self.conversation.current_model()


PopView = PopView
