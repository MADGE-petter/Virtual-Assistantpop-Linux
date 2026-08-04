"""Motion System - Premium micro-interactions."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from enum import Enum


class Easing(Enum):
    """Premium easing curves - no bounce, shake, or flash."""
    OUT_CUBIC = QEasingCurve.Type.OutCubic
    OUT_QUART = QEasingCurve.Type.OutQuart
    OUT_QUINT = QEasingCurve.Type.OutQuint
    OUT_SINE = QEasingCurve.Type.OutSine
    OUT_EXPO = QEasingCurve.Type.OutExpo
    OUT_CIRC = QEasingCurve.Type.OutCirc
    IN_OUT_CUBIC = QEasingCurve.Type.InOutCubic
    IN_OUT_QUART = QEasingCurve.Type.InOutQuart
    IN_OUT_SINE = QEasingCurve.Type.InOutSine


class Duration(Enum):
    """Standard durations in milliseconds."""
    INSTANT = 0
    FAST = 100
    NORMAL = 200
    SLOW = 300
    SLOWER = 400
    SLOWEST = 500


class Motion:
    """Premium motion utilities."""
    
    @staticmethod
    def create_animation(target, property_name: str, duration: int = Duration.NORMAL.value,
                         easing: Easing = Easing.OUT_CUBIC) -> QPropertyAnimation:
        """Create a standard property animation."""
        anim = QPropertyAnimation(target, property_name.encode())
        anim.setDuration(duration)
        anim.setEasingCurve(easing.value)
        return anim
    
    @staticmethod
    def fade_in(widget, duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Fade in animation."""
        anim = Motion.create_animation(widget, b"windowOpacity", duration, Easing.OUT_CUBIC)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        return anim
    
    @staticmethod
    def fade_out(widget, duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Fade out animation."""
        anim = Motion.create_animation(widget, b"windowOpacity", duration, Easing.OUT_CUBIC)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        return anim
    
    @staticmethod
    def slide_up(widget, distance: int = 20, duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Slide up animation."""
        from PyQt6.QtCore import QPoint
        anim = Motion.create_animation(widget, b"pos", duration, Easing.OUT_CUBIC)
        start_pos = widget.pos()
        anim.setStartValue(QPoint(start_pos.x(), start_pos.y() + distance))
        anim.setEndValue(start_pos)
        return anim
    
    @staticmethod
    def slide_down(widget, distance: int = 20, duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Slide down animation."""
        from PyQt6.QtCore import QPoint
        anim = Motion.create_animation(widget, b"pos", duration, Easing.OUT_CUBIC)
        start_pos = widget.pos()
        anim.setStartValue(QPoint(start_pos.x(), start_pos.y() - distance))
        anim.setEndValue(start_pos)
        return anim
    
    @staticmethod
    def scale_in(widget, duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Scale in animation (geometry-based)."""
        anim = Motion.create_animation(widget, b"geometry", duration, Easing.OUT_CUBIC)
        return anim
    
    @staticmethod
    def expand_height(widget, start_height: int, end_height: int, 
                      duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Expand height animation."""
        anim = Motion.create_animation(widget, b"maximumHeight", duration, Easing.OUT_CUBIC)
        anim.setStartValue(start_height)
        anim.setEndValue(end_height)
        return anim
    
    @staticmethod
    def collapse_height(widget, start_height: int, end_height: int = 0,
                        duration: int = Duration.NORMAL.value) -> QPropertyAnimation:
        """Collapse height animation."""
        anim = Motion.create_animation(widget, b"maximumHeight", duration, Easing.OUT_CUBIC)
        anim.setStartValue(start_height)
        anim.setEndValue(end_height)
        return anim
    
    @staticmethod
    def soft_glow(widget, property_name: str, start_alpha: float = 0.0, 
                  end_alpha: float = 0.15, duration: int = Duration.SLOW.value) -> QPropertyAnimation:
        """Soft glow animation for focus states."""
        anim = Motion.create_animation(widget, property_name.encode(), duration, Easing.OUT_SINE)
        anim.setStartValue(start_alpha)
        anim.setEndValue(end_alpha)
        return anim
    
    @staticmethod
    def button_lift(widget, lift_px: int = 2, duration: int = Duration.FAST.value) -> QPropertyAnimation:
        """Button lift on hover."""
        from PyQt6.QtCore import QPoint
        anim = Motion.create_animation(widget, b"pos", duration, Easing.OUT_CUBIC)
        start_pos = widget.pos()
        anim.setStartValue(QPoint(start_pos.x(), start_pos.y() + lift_px))
        anim.setEndValue(start_pos)
        return anim
    
    @staticmethod
    def stagger(animations: list, delay: int = 50) -> list:
        """Apply stagger delay to a list of animations."""
        for i, anim in enumerate(animations):
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(i * delay, anim.start)
        return animations