#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class cho các Admin Tab - Giảm duplicate code"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from admin.view.styles import (
    TABLE_WIDGET,
    BUTTON_PRIMARY,
    BG_CARD,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
)


class BaseTab(QWidget):
    """Base class cho các tab trong Admin Panel"""

    DB_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '..', 'database', 'conversations.db'
    ))

    def __init__(self, parent=None, log_callback=None):
        super().__init__(parent)
        self.log_callback = log_callback or print
        self.db_path = self.DB_PATH
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Override ở subclass"""
        pass

    def load_data(self):
        """Override ở subclass"""
        pass

    def create_table(self, columns, headers, style=None):
        """Tạo table chuẩn với style mới"""
        table = QTableWidget()
        table.setColumnCount(columns)
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(style or TABLE_WIDGET)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(50)
        table.verticalHeader().setMinimumSectionSize(40)
        table.setAlternatingRowColors(False)
        table.setShowGrid(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        return table

    def create_button_frame(self, buttons):
        """Tạo button frame với list buttons [(text, style, callback)]"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 12px 16px;
            }}
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)
        for text, style, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        layout.addStretch()
        return frame

    def log(self, message):
        """Log message"""
        self.log_callback(f"[{self.__class__.__name__}] {message}")
