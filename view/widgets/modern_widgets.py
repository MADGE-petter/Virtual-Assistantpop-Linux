"""
Modern Widgets for Pop Assistant
Includes AIOrbWidget for voice visualization and ChatBubble for modern chat interface.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QPoint
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen

class AIOrbWidget(QWidget):
    """
    A visual representation of the AI's state.
    States: 'idle', 'listening', 'thinking', 'speaking'
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._state = 'idle'
        self._pulse_value = 1.0
        
        # Animation for pulsing effect
        self.animation = QPropertyAnimation(self, b"pulse_value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(1.1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)
        self.animation.start()

    @pyqtProperty(float)
    def pulse_value(self):
        return self._pulse_value

    @pulse_value.setter
    def pulse_value(self, value):
        self._pulse_value = value
        self.update()

    def set_state(self, state):
        """Update the orb state: 'idle', 'listening', 'thinking', 'speaking'"""
        if self._state != state:
            self._state = state
            # Adjust animation speed based on state
            if state == 'thinking':
                self.animation.setDuration(500)
            elif state == 'listening':
                self.animation.setDuration(700)
            else:
                self.animation.setDuration(1000)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        radius = 60 * self._pulse_value
        
        # Color based on state
        if self._state == 'idle':
            color = QColor(0, 150, 255, 150) # Blue
        elif self._state == 'listening':
            color = QColor(0, 255, 150, 180) # Greenish
        elif self._state == 'thinking':
            color = QColor(180, 0, 255, 180) # Purple
        elif self._state == 'speaking':
            color = QColor(255, 200, 0, 180) # Gold
        else:
            color = QColor(0, 150, 255, 150)

        # Create radial gradient for the "Orb" effect
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, color)
        gradient.setColorAt(0.7, color.lighter(120))
        gradient.setColorAt(1, Qt.GlobalColor.transparent)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(radius), int(radius))
        
        # Add a subtle outer ring
        pen = QPen(color.lighter(150))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, int(radius * 1.2), int(radius * 1.2))

class ChatBubble(QFrame):
    """A modern chat bubble for User and Bot messages."""
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatBubble")
        
        layout = QVBoxLayout(self)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Style based on sender
        if is_user:
            self.setProperty("sender", "user")
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.label.setStyleSheet("color: white;")
        else:
            self.setProperty("sender", "bot")
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.label.setStyleSheet("color: #E0E0E0;")
            
        layout.addWidget(self.label)
        self.setContentsMargins(10, 10, 10, 10)
        
        # Apply dynamic style via QSS (defined in main stylesheet)
        self.update_style()

    def update_style(self):
        # This will be handled by the global QSS, but we set properties here
        self.style().unpolish(self)
        self.style().polish(self)
