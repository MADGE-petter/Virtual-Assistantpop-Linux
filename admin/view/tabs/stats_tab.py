#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Stats Tab (Modern Redesign)
Tab thống kê với card layout
"""

import os

from database.admin_repository import AdminRepository
from utils.logger import get_logger

logger = get_logger(__name__)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, QVBoxLayout, QFrame

from admin.view.styles import (
    BUTTON_PRIMARY,
    GROUP_BOX,
    SECTION_TITLE,
    SECTION_SUBTITLE,
    BG_CARD,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    INFO,
    SUCCESS,
    WARNING,
    DANGER,
    ACCENT,
)
from admin.view.tabs.base_tab import BaseTab
from admin.view.widgets.stats_card import StatsCard


class StatsTab(BaseTab):
    """Tab thống kê"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Section title
        title = QLabel("Thống kê hệ thống")
        title.setStyleSheet(SECTION_TITLE)
        layout.addWidget(title)

        subtitle = QLabel("Tổng quan về dữ liệu và hoạt động của Pop Assistant")
        subtitle.setStyleSheet(SECTION_SUBTITLE)
        layout.addWidget(subtitle)

        # Stats cards in grid
        stats_frame = QGroupBox(" Tổng quan")
        stats_frame.setStyleSheet(GROUP_BOX)
        stats_grid = QGridLayout(stats_frame)
        stats_grid.setSpacing(16)

        self.total_users_card = StatsCard("Tổng người dùng", INFO)
        stats_grid.addWidget(self.total_users_card, 0, 0)

        self.total_conversations_card = StatsCard("Tổng hội thoại", SUCCESS)
        stats_grid.addWidget(self.total_conversations_card, 0, 1)

        self.active_sessions_card = StatsCard("Phiên hoạt động", WARNING)
        stats_grid.addWidget(self.active_sessions_card, 0, 2)

        self.db_size_card = StatsCard("Kích thước DB", DANGER)
        stats_grid.addWidget(self.db_size_card, 1, 0)

        self.total_apps_card = StatsCard("App đã mở", ACCENT)
        stats_grid.addWidget(self.total_apps_card, 1, 1)

        layout.addWidget(stats_frame)

        # Refresh button
        refresh_btn = QPushButton("  Làm mới thống kê")
        refresh_btn.setStyleSheet(BUTTON_PRIMARY)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setMaximumWidth(220)
        layout.addWidget(refresh_btn)

        layout.addStretch()

    def load_data(self):
        """Load basic statistics"""
        try:
            self._load_basic_stats()
            self.log("✅ Thống kê đã được làm mới")
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")

    def _load_basic_stats(self):
        """Load basic database statistics"""
        total_users = total_conversations = active_sessions = 0
        total_apps = 0
        db_size_mb = 0.0

        if not os.path.exists(self.db_path):
            self.log("⚠️ Database không tìm thấy")
            return

        repo = AdminRepository(self.db_path)
        stats = repo.get_user_statistics()
        total_users = stats.get('total_users', 0)
        total_conversations = stats.get('total_conversations', 0)
        active_sessions = repo.get_active_sessions_count()
        total_apps = repo.get_app_usage_logs_count()

        size = os.path.getsize(self.db_path)
        db_size_mb = size / (1024 * 1024)

        self.total_users_card.set_value(str(total_users))
        self.total_conversations_card.set_value(str(total_conversations))
        self.active_sessions_card.set_value(str(active_sessions))
        self.db_size_card.set_value(f"{db_size_mb:.1f} MB")
        self.total_apps_card.set_value(str(total_apps))
