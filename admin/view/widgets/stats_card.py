#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Stats Card Widget (Modern Redesign 2026)
Clean card with accent color, icon, and hover effect
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout


class StatsCard(QFrame):
    """Modern stats card widget with accent color and hover effect"""

    def __init__(self, title, color, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.icon = icon
        self._hovered = False
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setMinimumHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()

    def setup_ui(self):
        r, g, b = self._hex_to_rgb(self.color)

        self.default_style = f"""
            QFrame#statsCard {{
                background-color: #1a1d2e;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 0px;
            }}
        """
        self.hover_style = f"""
            QFrame#statsCard {{
                background-color: #1e2138;
                border: 1px solid rgba({r}, {g}, {b}, 0.4);
                border-radius: 14px;
                padding: 0px;
            }}
        """
        self.setObjectName("statsCard")
        self.setStyleSheet(self.default_style)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(18, 18, 18, 14)

        # Top accent dot + title row
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        # Accent dot
        dot = QLabel("●")
        dot.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 10px;
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        header_row.addWidget(dot)

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: #94a3b8;
                font-weight: 500;
                letter-spacing: 0.3px;
                background: transparent;
                border: none;
            }}
        """)
        header_row.addWidget(self.title_label)
        header_row.addStretch()

        layout.addLayout(header_row)

        # Value label
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 34px;
                font-weight: 700;
                color: {self.color};
                padding: 2px 0px;
                background: transparent;
                border: none;
            }}
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.value_label)

        layout.addStretch()

    def set_value(self, value):
        """Cập nhật giá trị hiển thị"""
        self.value_label.setText(str(value))

    def enterEvent(self, event):
        """Hover in"""
        self._hovered = True
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover out"""
        self._hovered = False
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)

    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (99, 102, 241)
