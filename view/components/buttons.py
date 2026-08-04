"""Premium Buttons - Primary, Secondary, and Thinking Animation."""

from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen, QPainterPath
from PyQt6.QtWidgets import QPushButton, QWidget, QLabel, QHBoxLayout
from view.styles.colors import COLORS
from view.styles.typography import Typography


class PremiumButton(QPushButton):
    """Premium primary button with gradient background and hover effects."""
    
    def __init__(self, text: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(Typography.button(QFont.Weight.Medium))
        self.setFixedHeight(44)
        self.setMinimumWidth(120)
        self._hover_progress = 0.0
        self._press_progress = 0.0
        
        self._hover_anim = QPropertyAnimation(self, b"hover_progress")
        self._hover_anim.setDuration(200)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._press_anim = QPropertyAnimation(self, b"press_progress")
        self._press_anim.setDuration(100)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0F1117;
                padding: 0 24px;
                border-radius: 22px;
            }
        """)
        
    @pyqtProperty(float)
    def hover_progress(self):
        return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, value):
        self._hover_progress = value
        self.update()
        
    @pyqtProperty(float)
    def press_progress(self):
        return self._press_progress
    
    @press_progress.setter
    def press_progress(self, value):
        self._press_progress = value
        self.update()
        
    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_anim.stop()
            self._press_anim.setStartValue(self._press_progress)
            self._press_anim.setEndValue(1.0)
            self._press_anim.start()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_anim.stop()
            self._press_anim.setStartValue(self._press_progress)
            self._press_anim.setEndValue(0.0)
            self._press_anim.start()
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = rect.height() / 2
        
        # Base gradient
        grad = QLinearGradient(0, 0, rect.width(), 0)
        grad.setColorAt(0, COLORS['accent_start'])
        grad.setColorAt(1, COLORS['accent_end'])
        
        # Hover glow effect
        if self._hover_progress > 0:
            glow_grad = QLinearGradient(0, 0, rect.width(), 0)
            glow_grad.setColorAt(0, QColor(0, 255, 170, int(60 * self._hover_progress)))
            glow_grad.setColorAt(1, QColor(0, 204, 255, int(60 * self._hover_progress)))
            painter.fillRect(rect.adjusted(-4, -4, 4, 4), glow_grad)
        
        # Press scale
        scale = 1.0 - 0.02 * self._press_progress
        scaled_rect = QRectF(
            rect.center().x() - rect.width() * scale / 2,
            rect.center().y() - rect.height() * scale / 2,
            rect.width() * scale,
            rect.height() * scale
        )
        
        path = QPainterPath()
        path.addRoundedRect(scaled_rect, radius * scale, radius * scale)
        painter.fillPath(path, grad)
        
        # Draw text
        painter.setPen(QColor("#0F1117"))
        painter.setFont(self.font())
        painter.drawText(scaled_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
        painter.end()


class SecondaryButton(QPushButton):
    """Secondary button with subtle styling."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(Typography.button(QFont.Weight.Medium))
        self.setFixedHeight(40)
        self.setMinimumWidth(100)
        self._hover_progress = 0.0
        
        self._hover_anim = QPropertyAnimation(self, b"hover_progress")
        self._hover_anim.setDuration(150)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card'].name()};
                border: 1px solid {COLORS['border'].name()};
                color: {COLORS['text_primary'].name()};
                padding: 0 20px;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_hover'].name()};
                border-color: {COLORS['border_light'].name()};
            }}
            QPushButton:pressed {{
                background: {COLORS['bg_active'].name()};
            }}
        """)
        
    @pyqtProperty(float)
    def hover_progress(self):
        return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, value):
        self._hover_progress = value
        self.update()
        
    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)


class ThinkingAnimation(QWidget):
    """Animated thinking indicator with rotating status text."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self._statuses = ["Thinking...", "Processing...", "Analyzing...", "Generating..."]
        self._current_index = 0
        self._opacity = 1.0
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # Spinner dots
        self.spinner_label = QLabel("●●●")
        self.spinner_label.setFont(QFont("Inter", 12))
        self.spinner_label.setStyleSheet(f"color: {COLORS['accent_start'].name()};")
        layout.addWidget(self.spinner_label)
        
        # Status text
        self.status_label = QLabel(self._statuses[0])
        self.status_label.setFont(Typography.body_sm())
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()};")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_status)
        self._timer.start(1500)
        
        # Opacity animation
        self._opacity_anim = QPropertyAnimation(self, b"opacity")
        self._opacity_anim.setDuration(800)
        self._opacity_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._opacity_anim.setStartValue(0.3)
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.setLoopCount(-1)
        self._opacity_anim.start()
        
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; opacity: {value};")
        self.spinner_label.setStyleSheet(f"color: {COLORS['accent_start'].name()}; opacity: {value};")
        
    def _next_status(self):
        self._current_index = (self._current_index + 1) % len(self._statuses)
        self.status_label.setText(self._statuses[self._current_index])
        
    def stop(self):
        self._timer.stop()
        self._opacity_anim.stop()
        self.hide()
        
    def start(self):
        self._current_index = 0
        self.status_label.setText(self._statuses[0])
        self._timer.start(1500)
        self._opacity_anim.start()
        self.show()