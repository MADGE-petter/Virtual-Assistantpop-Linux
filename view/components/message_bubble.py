"""Message Bubble - Premium document-style message cards."""

from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from view.styles.colors import COLORS
from view.styles.typography import Typography
from view.components.markdown import MarkdownRenderer


class MessageBubble(QWidget):
    """Premium message card — elegant document-editor style, not chat bubbles."""

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self._rendered_html = ""
        self._hover_opacity = 0.0
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setMouseTracking(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.content_label.setFont(Typography.body())
        self.content_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary'].name()};
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)

        self._rendered_html = MarkdownRenderer.render(self.text)
        self.content_label.setText(self._rendered_html)
        self.content_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.content_label)

        self.time_label = QLabel()
        self.time_label.setFont(Typography.caption_sm())
        self.time_label.setStyleSheet(f"color: {COLORS['text_muted'].name()}; background: transparent;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.time_label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)
        radius = 14

        if self.is_user:
            # User card — right-aligned, subtle accent surface
            card_rect = QRect(40, 0, rect.width() - 40, rect.height())
            path = QPainterPath()
            path.addRoundedRect(card_rect, radius, radius)

            # Subtle gradient surface
            grad = QLinearGradient(0, 0, rect.width(), 0)
            grad.setColorAt(0, QColor("#1B2A3A"))
            grad.setColorAt(1, QColor("#1B2230"))
            painter.fillPath(path, QBrush(grad))

            # Thin accent left border
            painter.setClipPath(path)
            painter.fillRect(QRect(40, 0, 3, rect.height()), COLORS['accent_start'])
            painter.setClippingEnabled(False)

            # Soft shadow
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(card_rect, radius, radius)
            painter.fillPath(shadow_path.translated(0, 2), QColor(0, 0, 0, 30))
            painter.fillPath(shadow_path, QBrush(grad))
        else:
            # Assistant card — elevated card surface
            card_rect = QRect(0, 0, rect.width() - 40, rect.height())
            path = QPainterPath()
            path.addRoundedRect(card_rect, radius, radius)

            # Card surface
            bg = COLORS['bg_card']
            painter.fillPath(path, bg)

            # Subtle border
            painter.setPen(COLORS['border'])
            painter.drawPath(path)

            # Soft shadow beneath
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(card_rect, radius, radius)
            painter.fillPath(shadow_path.translated(0, 2), QColor(0, 0, 0, 25))
            painter.fillPath(shadow_path, bg)

        # Hover lighting effect
        if self._hover_opacity > 0:
            hover_path = QPainterPath()
            if self.is_user:
                hover_path.addRoundedRect(QRect(40, 0, rect.width() - 40, rect.height()), radius, radius)
            else:
                hover_path.addRoundedRect(QRect(0, 0, rect.width() - 40, rect.height()), radius, radius)
            hover_color = QColor(255, 255, 255, int(self._hover_opacity * 12))
            painter.fillPath(hover_path, hover_color)

        painter.end()

    def enterEvent(self, event):
        self._hover_opacity = 1.0
        self.update()

    def leaveEvent(self, event):
        self._hover_opacity = 0.0
        self.update()

    def sizeHint(self):
        from PyQt6.QtGui import QFontMetrics
        fm = QFontMetrics(Typography.body())
        text_width = min(fm.horizontalAdvance(self.text), 500)
        lines = max(1, (text_width // 400) + 1)
        height = lines * 24 + 32
        return QSize(600, height)