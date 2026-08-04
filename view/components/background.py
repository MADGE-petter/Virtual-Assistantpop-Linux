"""Premium Background - Multi-layered dark background with radial gradients + noise."""

import random
from PyQt6.QtCore import Qt, QPointF, QRectF, QSize
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget
from view.styles.colors import COLORS


def generate_noise_texture(width: int, height: int, opacity: float = 0.02) -> QPixmap:
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    rng = random.Random(42)
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            v = rng.randint(0, 255)
            c = QColor(v, v, v, int(opacity * 255))
            painter.setPen(QPen(c, 1))
            painter.drawPoint(x, y)
    painter.end()
    return pixmap


class PremiumBackground(QWidget):
    """Multi-layered dark background with radial gradients + noise."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._noise_pixmap = None
        self._noise_size = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPaintEvent
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Base background
        painter.fillRect(0, 0, w, h, COLORS['bg_deep'])

        # Top-right ambient glow
        g1 = QRadialGradient(QPointF(w * 0.85, h * 0.1), max(w, h) * 0.6)
        g1.setColorAt(0.0, QColor(0, 255, 170, 12))
        g1.setColorAt(0.4, QColor(0, 255, 170, 4))
        g1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(QRectF(0, 0, w, h), g1)

        # Bottom-left ambient glow
        g2 = QRadialGradient(QPointF(w * 0.15, h * 0.85), max(w, h) * 0.55)
        g2.setColorAt(0.0, QColor(0, 204, 255, 10))
        g2.setColorAt(0.5, QColor(0, 204, 255, 3))
        g2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(QRectF(0, 0, w, h), g2)

        # Center subtle accent
        g3 = QRadialGradient(QPointF(w * 0.5, h * 0.5), max(w, h) * 0.4)
        g3.setColorAt(0.0, QColor(0, 229, 212, 6))
        g3.setColorAt(0.7, QColor(0, 229, 212, 1))
        g3.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(QRectF(0, 0, w, h), g3)

        # Fine noise texture
        if self._noise_pixmap is None or self._noise_size != (w, h):
            self._noise_pixmap = generate_noise_texture(w, h, opacity=0.015)
            self._noise_size = (w, h)
        painter.drawPixmap(0, 0, self._noise_pixmap)
        painter.end()