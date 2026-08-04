"""Input Area - World-class AI prompt input with glass surface and animated border."""

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QConicalGradient, QFont, QPen, QPainterPath, QBrush
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTextEdit,
                             QPushButton, QSizePolicy)
from view.styles.colors import COLORS
from view.styles.typography import Typography


class PlusButton(QWidget):
    """Circular plus button with animated gradient border matching the input."""

    clicked = pyqtSignal()

    def __init__(self, size: int = 56, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._border_progress = 0.0

        self._anim = QPropertyAnimation(self, b"border_progress")
        self._anim.setDuration(4000)
        self._anim.setLoopCount(-1)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)
        self._anim.start()

    @pyqtProperty(float)
    def border_progress(self):
        return self._border_progress

    @border_progress.setter
    def border_progress(self, value):
        self._border_progress = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 1.5

        # Background — subtle dark glass
        painter.setBrush(QColor(23, 26, 36, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Animated gradient border — thin, elegant
        border_grad = QConicalGradient(QPointF(cx, cy), self._border_progress * 360)
        border_grad.setColorAt(0.0, QColor("#00FFAA"))
        border_grad.setColorAt(0.25, QColor("#00CCFF"))
        border_grad.setColorAt(0.5, QColor("#00FFAA"))
        border_grad.setColorAt(0.75, QColor("#00CCFF"))
        border_grad.setColorAt(1.0, QColor("#00FFAA"))

        pen = QPen(QBrush(border_grad), 1)  # Thin 1px border
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Plus sign — thin, elegant
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        plus_size = int(radius * 0.3)
        painter.drawLine(int(cx), int(cy - plus_size), int(cx), int(cy + plus_size))
        painter.drawLine(int(cx - plus_size), int(cy), int(cx + plus_size), int(cy))

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class InputArea(QWidget):
    """Premium floating input — glass surface, animated gradient border, auto-expanding."""

    send_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self._focus_progress = 0.0
        self._border_progress = 0.0
        self.setup_ui()
        self.setup_animations()

    def setup_animations(self):
        # Focus animation
        self._focus_anim = QPropertyAnimation(self, b"focus_progress")
        self._focus_anim.setDuration(400)
        self._focus_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Border rotation animation
        self._border_anim = QPropertyAnimation(self, b"border_progress")
        self._border_anim.setDuration(4000)
        self._border_anim.setLoopCount(-1)
        self._border_anim.setStartValue(0.0)
        self._border_anim.setEndValue(1.0)
        self._border_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self._border_anim.start()

    @pyqtProperty(float)
    def focus_progress(self):
        return self._focus_progress

    @focus_progress.setter
    def focus_progress(self, value):
        self._focus_progress = value
        self.update()

    @pyqtProperty(float)
    def border_progress(self):
        return self._border_progress

    @border_progress.setter
    def border_progress(self, value):
        self._border_progress = value
        self.update()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 0, 24, 24)
        main_layout.setSpacing(12)

        # ── Plus button (circular, same height as container) ──
        self.plus_btn = PlusButton(56)
        self.plus_btn.setToolTip("Add attachment")
        main_layout.addWidget(self.plus_btn)

        # ── Floating container ──
        self.container = QWidget()
        self.container.setObjectName("inputContainer")
        self.container.setMinimumHeight(56)
        self.container.setMaximumHeight(200)
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(20, 12, 12, 12)
        container_layout.setSpacing(12)

        # Text input — clean, beautiful typography
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Ask anything...")
        self.text_input.setFont(Typography.body())
        self.text_input.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary'].name()};
                font-family: "Noto Sans", "DejaVu Sans", sans-serif;
                font-size: 15px;
                line-height: 1.6;
                selection-background-color: rgba(0, 255, 170, 0.2);
            }}
            QTextEdit:focus {{
                background: transparent;
            }}
        """)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_input.setMinimumHeight(32)
        self.text_input.setMaximumHeight(150)
        self.text_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.text_input.textChanged.connect(self._on_text_changed)
        container_layout.addWidget(self.text_input, stretch=1)

        # Send button — gradient circle
        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(44, 44)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setText("↗")
        self.send_btn.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFAA, stop:1 #00CCFF);
                border: none;
                border-radius: 22px;
                color: #0F1117;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #20E3B2, stop:1 #00CCFF);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00CCFF, stop:1 #00FFAA);
            }}
            QPushButton:disabled {{
                background: {COLORS['border'].name()};
                color: {COLORS['text_muted'].name()};
            }}
        """)
        self.send_btn.clicked.connect(self._on_send)
        container_layout.addWidget(self.send_btn)

        main_layout.addWidget(self.container)

        self._on_text_changed()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Container rect — starts after the plus button
        margin_left = 24 + 56 + 12  # margin + plus_btn width + spacing
        margin_right = 24
        rect = QRectF(margin_left, 0, self.width() - margin_left - margin_right, self.height() - 24)
        radius = 20

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Glass surface background
        glass_bg = QColor(23, 26, 36, 220)  # bg_surface with alpha
        painter.fillPath(path, QBrush(glass_bg))

        # Animated gradient border — conical gradient rotating around the rect
        progress = self._border_progress
        cx, cy = rect.center().x(), rect.center().y()

        border_grad = QConicalGradient(cx, cy, progress * 360)
        border_grad.setColorAt(0.0, QColor("#00FFAA"))
        border_grad.setColorAt(0.25, QColor("#00CCFF"))
        border_grad.setColorAt(0.5, QColor("#00FFAA"))
        border_grad.setColorAt(0.75, QColor("#00CCFF"))
        border_grad.setColorAt(1.0, QColor("#00FFAA"))

        border_width = 1.5 + self._focus_progress * 1.0
        pen = QPen(QBrush(border_grad), border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

        # Focus glow
        if self._focus_progress > 0:
            glow_alpha = int(self._focus_progress * 40)
            glow_color = QColor(0, 255, 170, glow_alpha)
            glow_pen = QPen(glow_color, 4 + self._focus_progress * 4)
            painter.setPen(glow_pen)
            painter.drawRoundedRect(rect, radius, radius)

        # Soft shadow
        shadow_path = QPainterPath()
        shadow_rect = rect.translated(0, 4)
        shadow_path.addRoundedRect(shadow_rect, radius, radius)
        shadow_color = QColor(0, 0, 0, 40 + int(self._focus_progress * 20))
        painter.fillPath(shadow_path, shadow_color)

        painter.end()

    def _on_text_changed(self):
        has_text = bool(self.text_input.toPlainText().strip())
        self.send_btn.setEnabled(has_text)

    def _on_send(self):
        text = self.text_input.toPlainText().strip()
        if text:
            self.send_message.emit(text)
            self.text_input.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            event.accept()
            self._on_send()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self._focus_anim.setStartValue(self._focus_progress)
        self._focus_anim.setEndValue(1.0)
        self._focus_anim.start()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._focus_anim.setStartValue(self._focus_progress)
        self._focus_anim.setEndValue(0.0)
        self._focus_anim.start()
        super().focusOutEvent(event)