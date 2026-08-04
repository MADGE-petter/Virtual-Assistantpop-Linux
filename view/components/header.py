"""Header Widget - Premium glassmorphism header with logo and window controls."""

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from view.styles.colors import COLORS
from view.styles.typography import Typography


class HeaderWidget(QWidget):
    """Premium glassmorphism header with auto-hide background on scroll."""
    settings_clicked = pyqtSignal()
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self._hovered_button = None
        self._button_rects = {}
        self._bg_opacity = 0.0
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        self.setup_ui()

    def set_bg_opacity(self, opacity: float):
        """Set background opacity (0.0 = transparent, 1.0 = fully opaque dark)."""
        self._bg_opacity = max(0.0, min(1.0, opacity))
        self.update()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(0)

        # ── Left: Logo ──
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(36, 36)
        self.logo_label.setScaledContents(True)
        pixmap = QPixmap("assets/POP.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap)
        layout.addWidget(self.logo_label)
        layout.addSpacing(12)

        # ── Center: Conversation Title ──
        center_layout = QHBoxLayout()
        center_layout.setSpacing(0)

        self.conv_title = QLabel("New Conversation")
        self.conv_title.setFont(Typography.body_sm(QFont.Weight.Medium))
        self.conv_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary'].name()};
                background: transparent;
                border: none;
            }}
        """)
        center_layout.addWidget(self.conv_title)

        # Wrap center in a container
        center_container = QWidget()
        center_container.setLayout(center_layout)
        center_container.setStyleSheet("background: transparent; border: none;")

        # Add stretch on both sides of center to keep it centered
        layout.addStretch()
        layout.addWidget(center_container)
        layout.addStretch()

        # ── Right: Settings + Window Controls ──
        right_layout = QHBoxLayout()
        right_layout.setSpacing(6)

        # Settings button
        self.settings_btn = self._make_header_button("⚙", "Settings")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        right_layout.addWidget(self.settings_btn)

        # Window controls
        self.min_btn = self._make_header_button("─", "Minimize")
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        right_layout.addWidget(self.min_btn)

        self.max_btn = self._make_header_button("□", "Maximize")
        self.max_btn.clicked.connect(self.maximize_clicked.emit)
        right_layout.addWidget(self.max_btn)

        self.close_btn = self._make_header_button("✕", "Close")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary'].name()};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                padding: 6px 10px;
                font-family: "Noto Sans", "DejaVu Sans", sans-serif;
            }}
            QPushButton:hover {{
                background: {COLORS['error'].name()};
                color: {COLORS['text_inverse'].name()};
            }}
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        right_layout.addWidget(self.close_btn)

        layout.addLayout(right_layout)

    def _make_header_button(self, text: str, tooltip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary'].name()};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-family: "Noto Sans", "DejaVu Sans", sans-serif;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_hover'].name()};
                color: {COLORS['text_primary'].name()};
            }}
            QPushButton:pressed {{
                background: {COLORS['bg_active'].name()};
            }}
        """)
        return btn

    def _make_close_button(self) -> QPushButton:
        btn = QPushButton("✕")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
    QPushButton {{
        background: transparent;
        color: {COLORS['text_secondary'].name()};
        border: none;
        border-radius: 8px;
        font-size: 13px;
        padding: 6px 10px;
        font-family: "Noto Sans", "DejaVu Sans", sans-serif;
    }}
    QPushButton:hover {{
        background: {COLORS['error'].name()};
        color: {COLORS['text_inverse'].name()};
    }}
    """)
        return btn

    def set_conversation_title(self, title: str):
        self.conv_title.setText(title)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._bg_opacity > 0.01:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            # Glassmorphism background
            bg_color = QColor(COLORS['bg_deep'])
            bg_color.setAlphaF(self._bg_opacity * 0.85)
            painter.fillRect(self.rect(), bg_color)
            # Subtle bottom border
            border_color = QColor(COLORS['border'])
            border_color.setAlphaF(self._bg_opacity * 0.4)
            painter.fillRect(0, self.height() - 1, self.width(), 1, border_color)
            painter.end()