#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sidebar Component - POP Assistant
Left vertical navigation panel with collapse/expand functionality.
Implements: Structure → Color → Motion → States
"""

from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, 
    QTimer, pyqtSignal, QSize, QEvent
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QSizePolicy, QSpacerItem, QFrame, QToolTip
)
from PyQt6.QtGui import QPixmap, QIcon, QCursor, QFont, QPainter, QColor, QBrush, QPen

from view.styles.theme import COLORS, RADIUS, SHADOWS, LAYOUT, SPACING, MOTION


class SidebarItem(QPushButton):
    """Individual navigation item in sidebar."""
    
    def __init__(self, icon_path: str = "", text: str = "", tooltip: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarItem")
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(44)
        self._tooltip_text = tooltip
        self._is_collapsed = True
        
        # Layout
        self.item_layout = QHBoxLayout(self)
        self.item_layout.setContentsMargins(SPACING.MD, SPACING.SM, SPACING.MD, SPACING.SM)
        self.item_layout.setSpacing(SPACING.MD)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setObjectName("sidebarItemIcon")
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path:
            self.set_icon(icon_path)
        self.item_layout.addWidget(self.icon_label)
        
        # Text label
        self.text_label = QLabel(text)
        self.text_label.setObjectName("sidebarItemText")
        self.text_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.text_label.hide()  # Hidden when collapsed
        self.item_layout.addWidget(self.text_label)
        self.item_layout.addStretch()
        
        # Active indicator (cyan rail)
        self.active_indicator = QWidget()
        self.active_indicator.setObjectName("sidebarActiveIndicator")
        self.active_indicator.setFixedWidth(3)
        self.active_indicator.hide()
        self.item_layout.addWidget(self.active_indicator)
        
        # Tooltip for collapsed state
        self.setToolTip(tooltip)
        
    def set_icon(self, icon_path: str):
        """Set icon from file path."""
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(
                24, 24, Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def set_collapsed(self, collapsed: bool):
        """Update visibility for collapsed/expanded state."""
        self._is_collapsed = collapsed
        self.text_label.setVisible(not collapsed)
        self.setToolTip(self._tooltip_text if collapsed else "")
        self.updateGeometry()
    
    def set_active(self, active: bool):
        """Update active indicator."""
        self.active_indicator.setVisible(active)
        self.setChecked(active)
    
    def enterEvent(self, event):
        """Show tooltip immediately on hover in collapsed state."""
        if self._is_collapsed and self._tooltip_text:
            QToolTip.showText(QCursor.pos(), self._tooltip_text, self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)


class SidebarSection(QWidget):
    """Section container with optional header label."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarSection")
        
        self.section_layout = QVBoxLayout(self)
        self.section_layout.setContentsMargins(SPACING.SM, SPACING.XS, SPACING.SM, SPACING.XS)
        self.section_layout.setSpacing(SPACING.XS)
        
        if title:
            self.header_label = QLabel(title.upper())
            self.header_label.setObjectName("sidebarSectionHeader")
            self.header_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            self.header_label.hide()  # Hidden when collapsed
            self.section_layout.addWidget(self.header_label)
        
        self._is_collapsed = True
    
    def add_item(self, item: SidebarItem):
        self.section_layout.addWidget(item)
    
    def add_stretch(self):
        self.section_layout.addStretch()
    
    def set_collapsed(self, collapsed: bool):
        self._is_collapsed = collapsed
        if hasattr(self, 'header_label'):
            self.header_label.setVisible(not collapsed)
        # Update all child items
        for i in range(self.section_layout.count()):
            widget = self.section_layout.itemAt(i).widget()
            if isinstance(widget, SidebarItem):
                widget.set_collapsed(collapsed)


class Sidebar(QWidget):
    """
    Main Sidebar Component
    
    Structure:
    - Top: Logo zone (POP logo + name)
    - Middle: Navigation zone (scrollable sections)
    - Bottom: Account zone (user avatar + settings)
    - Collapse toggle button
    """
    
    # Signals
    navigation_clicked = pyqtSignal(str)  # route name
    collapse_toggled = pyqtSignal(bool)   # is_collapsed
    settings_clicked = pyqtSignal()
    profile_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(LAYOUT.SIDEBAR_COLLAPSED)
        
        # State
        self._is_collapsed = True
        self._is_pinned = False
        self._is_dragging = False
        self._is_loading = False
        self._active_route = "home"
        
        # Animations
        self._width_animation = QPropertyAnimation(self, b"minimumWidth")
        self._width_animation.setDuration(MOTION.NORMAL)
        self._width_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self._width_animation_max = QPropertyAnimation(self, b"maximumWidth")
        self._width_animation_max.setDuration(MOTION.NORMAL)
        self._width_animation_max.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Content opacity animation for smooth text fade
        self._content_opacity = 1.0
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """2.1 Structure - Build the sidebar layout."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # ===== TOP: LOGO ZONE =====
        self.logo_zone = QWidget()
        self.logo_zone.setObjectName("sidebarLogoZone")
        self.logo_zone.setFixedHeight(80)
        self.logo_layout = QHBoxLayout(self.logo_zone)
        self.logo_layout.setContentsMargins(SPACING.MD, SPACING.MD, SPACING.MD, SPACING.MD)
        self.logo_layout.setSpacing(SPACING.MD)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setObjectName("sidebarLogo")
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setScaledContents(True)
        self._load_logo()
        self.logo_layout.addWidget(self.logo_label)
        
        # App name
        self.app_name_label = QLabel("POP Assistant")
        self.app_name_label.setObjectName("sidebarAppName")
        self.app_name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.app_name_label.hide()  # Hidden when collapsed
        self.logo_layout.addWidget(self.app_name_label)
        self.logo_layout.addStretch()
        
        # Collapse/Expand toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("sidebarToggleButton")
        self.toggle_button.setFixedSize(28, 28)
        self.toggle_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_button.setToolTip("Mở rộng thanh bên")
        self.toggle_button.clicked.connect(self._on_toggle_clicked)
        self._update_toggle_icon()
        self.logo_layout.addWidget(self.toggle_button)
        
        self.main_layout.addWidget(self.logo_zone)
        
        # Divider
        self.top_divider = QFrame()
        self.top_divider.setObjectName("sidebarDivider")
        self.top_divider.setFrameShape(QFrame.Shape.HLine)
        self.top_divider.setFrameShadow(QFrame.Shadow.Plain)
        self.top_divider.setFixedHeight(1)
        self.main_layout.addWidget(self.top_divider)
        
        # ===== MIDDLE: NAVIGATION ZONE (Scrollable) =====
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setObjectName("sidebarNavScroll")
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.nav_container = QWidget()
        self.nav_container.setObjectName("sidebarNavContainer")
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(SPACING.XS, SPACING.SM, SPACING.XS, SPACING.SM)
        self.nav_layout.setSpacing(SPACING.SM)
        
        # Navigation sections
        self._create_navigation_sections()
        
        self.nav_scroll.setWidget(self.nav_container)
        self.main_layout.addWidget(self.nav_scroll, 1)  # Stretch factor 1
        
        # ===== BOTTOM: ACCOUNT ZONE =====
        self.bottom_divider = QFrame()
        self.bottom_divider.setObjectName("sidebarDivider")
        self.bottom_divider.setFrameShape(QFrame.Shape.HLine)
        self.bottom_divider.setFrameShadow(QFrame.Shadow.Plain)
        self.bottom_divider.setFixedHeight(1)
        self.main_layout.addWidget(self.bottom_divider)
        
        self.account_zone = QWidget()
        self.account_zone.setObjectName("sidebarAccountZone")
        self.account_zone.setFixedHeight(72)
        self.account_layout = QHBoxLayout(self.account_zone)
        self.account_layout.setContentsMargins(SPACING.MD, SPACING.SM, SPACING.MD, SPACING.SM)
        self.account_layout.setSpacing(SPACING.MD)
        
        # User avatar
        self.avatar_button = QPushButton()
        self.avatar_button.setObjectName("sidebarAvatar")
        self.avatar_button.setFixedSize(40, 40)
        self.avatar_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.avatar_button.setToolTip("Hồ sơ cá nhân")
        self.avatar_button.clicked.connect(self.profile_clicked.emit)
        self._setup_avatar()
        self.account_layout.addWidget(self.avatar_button)
        
        # User info
        self.user_info_widget = QWidget()
        self.user_info_widget.setObjectName("sidebarUserInfo")
        self.user_info_layout = QVBoxLayout(self.user_info_widget)
        self.user_info_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_layout.setSpacing(2)
        
        self.user_name_label = QLabel("Người dùng")
        self.user_name_label.setObjectName("sidebarUserName")
        self.user_name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.user_name_label.hide()
        self.user_info_layout.addWidget(self.user_name_label)
        
        self.user_status_label = QLabel("Sẵn sàng")
        self.user_status_label.setObjectName("sidebarUserStatus")
        self.user_status_label.setFont(QFont("Segoe UI", 10))
        self.user_status_label.hide()
        self.user_info_layout.addWidget(self.user_status_label)
        
        self.account_layout.addWidget(self.user_info_widget)
        self.account_layout.addStretch()
        
        # Settings button
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("sidebarSettingsButton")
        self.settings_button.setFixedSize(28, 28)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setToolTip("Cài đặt")
        self.settings_button.clicked.connect(self.settings_clicked.emit)
        self._setup_settings_icon()
        self.account_layout.addWidget(self.settings_button)
        
        self.main_layout.addWidget(self.account_zone)
    
    def _load_logo(self):
        """Load POP logo from assets."""
        logo_path = "assets/POP.png"
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(
                40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            # Fallback: draw a simple logo
            self.logo_label.setText("POP")
            self.logo_label.setStyleSheet(f"color: {COLORS.ACCENT_CYAN}; font-weight: bold; font-size: 16px;")
    
    def _setup_avatar(self):
        """Setup default avatar."""
        self.avatar_button.setText("👤")
        self.avatar_button.setFont(QFont("Segoe UI", 16))
    
    def _setup_settings_icon(self):
        """Setup settings icon."""
        self.settings_button.setText("⚙")
        self.settings_button.setFont(QFont("Segoe UI", 14))
    
    def _create_navigation_sections(self):
        """Create navigation sections with items."""
        # Section 1: Main Navigation
        self.main_section = SidebarSection("Chính")
        self.nav_layout.addWidget(self.main_section)
        
        self.nav_items = {}
        
        # Home
        self.nav_items["home"] = SidebarItem(
            icon_path="", text="Trang chủ", tooltip="Trang chủ",
            parent=self.main_section
        )
        self.nav_items["home"].clicked.connect(lambda: self._on_nav_clicked("home"))
        self.main_section.add_item(self.nav_items["home"])
        
        # Habits
        self.nav_items["habits"] = SidebarItem(
            icon_path="", text="Thói quen", tooltip="Thói quen",
            parent=self.main_section
        )
        self.nav_items["habits"].clicked.connect(lambda: self._on_nav_clicked("habits"))
        self.main_section.add_item(self.nav_items["habits"])
        
        # Analytics
        self.nav_items["analytics"] = SidebarItem(
            icon_path="", text="Phân tích", tooltip="Phân tích",
            parent=self.main_section
        )
        self.nav_items["analytics"].clicked.connect(lambda: self._on_nav_clicked("analytics"))
        self.main_section.add_item(self.nav_items["analytics"])
        
        # Section 2: Tools
        self.tools_section = SidebarSection("Công cụ")
        self.nav_layout.addWidget(self.tools_section)
        
        # Apps
        self.nav_items["apps"] = SidebarItem(
            icon_path="", text="Ứng dụng", tooltip="Ứng dụng",
            parent=self.tools_section
        )
        self.nav_items["apps"].clicked.connect(lambda: self._on_nav_clicked("apps"))
        self.tools_section.add_item(self.nav_items["apps"])
        
        # Files
        self.nav_items["files"] = SidebarItem(
            icon_path="", text="Tệp tin", tooltip="Tệp tin",
            parent=self.tools_section
        )
        self.nav_items["files"].clicked.connect(lambda: self._on_nav_clicked("files"))
        self.tools_section.add_item(self.nav_items["files"])
        
        # System
        self.nav_items["system"] = SidebarItem(
            icon_path="", text="Hệ thống", tooltip="Hệ thống",
            parent=self.tools_section
        )
        self.nav_items["system"].clicked.connect(lambda: self._on_nav_clicked("system"))
        self.tools_section.add_item(self.nav_items["system"])
        
        # Section 3: Settings & Help
        self.settings_section = SidebarSection("Khác")
        self.nav_layout.addWidget(self.settings_section)
        
        # Settings (duplicate in account zone for easy access)
        self.nav_items["settings_nav"] = SidebarItem(
            icon_path="", text="Cài đặt", tooltip="Cài đặt",
            parent=self.settings_section
        )
        self.nav_items["settings_nav"].clicked.connect(self.settings_clicked.emit)
        self.settings_section.add_item(self.nav_items["settings_nav"])
        
        # Help
        self.nav_items["help"] = SidebarItem(
            icon_path="", text="Trợ giúp", tooltip="Trợ giúp",
            parent=self.settings_section
        )
        self.nav_items["help"].clicked.connect(lambda: self._on_nav_clicked("help"))
        self.settings_section.add_item(self.nav_items["help"])
        
        # Stretch to push sections to top
        self.nav_layout.addStretch()
        
        # Set initial active
        self.set_active_route("home")
    
    def _on_nav_clicked(self, route: str):
        """Handle navigation item click."""
        self.set_active_route(route)
        self.navigation_clicked.emit(route)
    
    def _on_toggle_clicked(self):
        """Handle collapse/expand toggle."""
        self.toggle_collapse()
    
    def _update_toggle_icon(self):
        """Update toggle button icon based on state."""
        if self._is_collapsed:
            self.toggle_button.setText("▶")  # Right chevron
            self.toggle_button.setToolTip("Mở rộng thanh bên")
        else:
            self.toggle_button.setText("◀")  # Left chevron
            self.toggle_button.setToolTip("Thu gọn thanh bên")
    
    # ===== PUBLIC API =====
    
    def toggle_collapse(self):
        """Toggle between collapsed and expanded state with animation."""
        self._is_collapsed = not self._is_collapsed
        self._animate_width()
        self._update_toggle_icon()
        self.collapse_toggled.emit(self._is_collapsed)
    
    def set_collapsed(self, collapsed: bool):
        """Set collapsed state programmatically."""
        if self._is_collapsed != collapsed:
            self._is_collapsed = collapsed
            self._animate_width()
            self._update_toggle_icon()
            self.collapse_toggled.emit(self._is_collapsed)
    
    def is_collapsed(self) -> bool:
        return self._is_collapsed
    
    def _animate_width(self):
        """Animate sidebar width change."""
        target_width = LAYOUT.SIDEBAR_COLLAPSED if self._is_collapsed else LAYOUT.SIDEBAR_EXPANDED
        
        self._width_animation.stop()
        self._width_animation.setStartValue(self.width())
        self._width_animation.setEndValue(target_width)
        self._width_animation.start()
        
        self._width_animation_max.stop()
        self._width_animation_max.setStartValue(self.width())
        self._width_animation_max.setEndValue(target_width)
        self._width_animation_max.start()
        
        # Update child visibility with slight delay for smooth transition
        QTimer.singleShot(MOTION.FAST, lambda: self._update_children_visibility())
    
    def _update_children_visibility(self):
        """Update visibility of all child components."""
        # Logo zone
        self.app_name_label.setVisible(not self._is_collapsed)
        
        # Navigation sections
        for section in [self.main_section, self.tools_section, self.settings_section]:
            section.set_collapsed(self._is_collapsed)
        
        # Account zone
        self.user_name_label.setVisible(not self._is_collapsed)
        self.user_status_label.setVisible(not self._is_collapsed)
        
        # Update tooltips
        for item in self.nav_items.values():
            item.set_collapsed(self._is_collapsed)
        
        self.avatar_button.setToolTip("Hồ sơ cá nhân" if self._is_collapsed else "")
        self.settings_button.setToolTip("Cài đặt" if self._is_collapsed else "")
    
    def set_active_route(self, route: str):
        """Set active navigation route."""
        self._active_route = route
        for key, item in self.nav_items.items():
            is_active = (key == route) or (route == "settings" and key == "settings_nav")
            item.set_active(is_active)
    
    def get_active_route(self) -> str:
        return self._active_route
    
    def set_user_info(self, name: str, status: str = "Sẵn sàng", avatar_path: str = ""):
        """Update user info in account zone."""
        self.user_name_label.setText(name)
        self.user_status_label.setText(status)
        if avatar_path:
            pixmap = QPixmap(avatar_path)
            if not pixmap.isNull():
                self.avatar_button.setIcon(QIcon(pixmap))
                self.avatar_button.setIconSize(QSize(40, 40))
                self.avatar_button.setText("")
    
    def set_pinned(self, pinned: bool):
        """Set pinned state (prevents auto-collapse on hover leave)."""
        self._is_pinned = pinned
        self.setProperty("pinned", pinned)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self._is_loading = loading
        self.setProperty("loading", loading)
        self.style().unpolish(self)
        self.style().polish(self)
        # Disable interactions during loading
        self.nav_scroll.setEnabled(not loading)
        self.toggle_button.setEnabled(not loading)
        self.avatar_button.setEnabled(not loading)
        self.settings_button.setEnabled(not loading)
        for item in self.nav_items.values():
            item.setEnabled(not loading)
    
    def set_dragging(self, dragging: bool):
        """Set dragging state (for reordering)."""
        self._is_dragging = dragging
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def set_disabled(self, disabled: bool):
        """Set disabled state."""
        self.setEnabled(not disabled)
        self.setProperty("disabled", disabled)
        self.style().unpolish(self)
        self.style().polish(self)
    
    # ===== 2.2 Color & 2.3 Motion & 2.4 States - Applied via Stylesheet =====
    
    def _apply_styles(self):
        """Apply comprehensive stylesheet for Color, Motion, States."""
        self.setStyleSheet(f"""
            /* ===== BASE SIDEBAR ===== */
            #sidebar {{
                background-color: {COLORS.BG_OVERLAY};
                border-right: 1px solid {COLORS.BORDER_SUBTLE};
                border-bottom-left-radius: {RADIUS.MD}px;
            }}
            
            /* ===== LOGO ZONE ===== */
            #sidebarLogoZone {{
                background-color: transparent;
                border-bottom: 1px solid {COLORS.BORDER_SUBTLE};
            }}
            
            #sidebarLogo {{
                background-color: {COLORS.ACCENT_DIM};
                border-radius: {RADIUS.SM}px;
            }}
            
            #sidebarAppName {{
                color: {COLORS.TEXT_PRIMARY};
            }}
            
            #sidebarToggleButton {{
                background-color: transparent;
                border: none;
                color: {COLORS.TEXT_SECONDARY};
                font-size: 14px;
                border-radius: {RADIUS.SM}px;
            }}
            #sidebarToggleButton:hover {{
                background-color: {COLORS.BG_HOVER};
                color: {COLORS.ACCENT_CYAN};
            }}
            #sidebarToggleButton:pressed {{
                background-color: {COLORS.BG_ACTIVE};
            }}
            
            /* ===== DIVIDERS ===== */
            #sidebarDivider {{
                background-color: {COLORS.BORDER_SUBTLE};
                border: none;
            }}
            
            /* ===== NAVIGATION SCROLL AREA ===== */
            #sidebarNavScroll {{
                background-color: transparent;
                border: none;
            }}
            #sidebarNavScroll > QWidget > QWidget {{
                background-color: transparent;
            }}
            
            /* Scrollbar styling */
            #sidebarNavScroll QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
                margin: 0;
            }}
            #sidebarNavScroll QScrollBar::handle:vertical {{
                background-color: {COLORS.BORDER_DEFAULT};
                border-radius: 3px;
                min-height: 30px;
            }}
            #sidebarNavScroll QScrollBar::handle:vertical:hover {{
                background-color: {COLORS.BORDER_STRONG};
            }}
            #sidebarNavScroll QScrollBar::add-line:vertical,
            #sidebarNavScroll QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            #sidebarNavScroll QScrollBar::add-page:vertical,
            #sidebarNavScroll QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            #sidebarNavContainer {{
                background-color: transparent;
            }}
            
            /* ===== SECTION HEADERS ===== */
            #sidebarSectionHeader {{
                color: {COLORS.TEXT_MUTED};
                padding-left: {SPACING.MD}px;
                padding-bottom: {SPACING.XS}px;
            }}
            
            /* ===== NAVIGATION ITEMS ===== */
            #sidebarItem {{
                background-color: transparent;
                border: none;
                border-radius: {RADIUS.SM}px;
                color: {COLORS.TEXT_SECONDARY};
                text-align: left;
                padding: {SPACING.SM}px {SPACING.MD}px;
            }}
            #sidebarItem:hover {{
                background-color: {COLORS.BG_HOVER};
                color: {COLORS.TEXT_PRIMARY};
            }}
            #sidebarItem:pressed {{
                background-color: {COLORS.BG_ACTIVE};
            }}
            #sidebarItem:checked {{
                background-color: {COLORS.ACCENT_DIM};
                color: {COLORS.ACCENT_CYAN};
            }}
            #sidebarItem:disabled {{
                color: {COLORS.TEXT_MUTED};
                background-color: transparent;
            }}
            
            #sidebarItemIcon {{
                color: {COLORS.TEXT_SECONDARY};
            }}
            #sidebarItem:hover #sidebarItemIcon {{
                color: {COLORS.TEXT_PRIMARY};
            }}
            #sidebarItem:checked #sidebarItemIcon {{
                color: {COLORS.ACCENT_CYAN};
            }}
            
            #sidebarItemText {{
                color: {COLORS.TEXT_SECONDARY};
            }}
            #sidebarItem:hover #sidebarItemText {{
                color: {COLORS.TEXT_PRIMARY};
            }}
            #sidebarItem:checked #sidebarItemText {{
                color: {COLORS.ACCENT_CYAN};
                font-weight: 600;
            }}
            
            /* Active indicator (cyan rail) */
            #sidebarActiveIndicator {{
                background-color: {COLORS.ACCENT_CYAN};
                border-radius: 1px;
            }}
            
            /* ===== ACCOUNT ZONE ===== */
            #sidebarAccountZone {{
                background-color: transparent;
                border-top: 1px solid {COLORS.BORDER_SUBTLE};
            }}
            
            #sidebarAvatar {{
                background-color: {COLORS.ACCENT_DIM};
                border-radius: {RADIUS.FULL}px;
                color: {COLORS.ACCENT_CYAN};
                border: 2px solid {COLORS.BORDER_SUBTLE};
            }}
            #sidebarAvatar:hover {{
                border-color: {COLORS.ACCENT_CYAN};
                background-color: {COLORS.BG_HOVER};
            }}
            #sidebarAvatar:pressed {{
                background-color: {COLORS.BG_ACTIVE};
            }}
            
            #sidebarUserInfo {{
                background-color: transparent;
            }}
            
            #sidebarUserName {{
                color: {COLORS.TEXT_PRIMARY};
            }}
            
            #sidebarUserStatus {{
                color: {COLORS.TEXT_MUTED};
            }}
            
            #sidebarSettingsButton {{
                background-color: transparent;
                border: none;
                color: {COLORS.TEXT_SECONDARY};
                font-size: 14px;
                border-radius: {RADIUS.SM}px;
            }}
            #sidebarSettingsButton:hover {{
                background-color: {COLORS.BG_HOVER};
                color: {COLORS.ACCENT_CYAN};
            }}
            #sidebarSettingsButton:pressed {{
                background-color: {COLORS.BG_ACTIVE};
            }}
            
            /* ===== 2.4 STATES ===== */
            
            /* Collapsed state - handled by width animation */
            
            /* Expanded state - handled by width animation */
            
            /* Hovered state - on items */
            
            /* Active/Selected state */
            #sidebarItem[active="true"] {{
                background-color: {COLORS.ACCENT_DIM};
                color: {COLORS.ACCENT_CYAN};
            }}
            
            /* Pinned state */
            #sidebar[pinned="true"] {{
                border-right: 2px solid {COLORS.ACCENT_CYAN};
            }}
            
            /* Dragging state */
            #sidebar[dragging="true"] {{
                opacity: 0.8;
                border-right: 2px dashed {COLORS.ACCENT_CYAN};
            }}
            
            /* Disabled state */
            #sidebar[disabled="true"] {{
                opacity: 0.5;
            }}
            #sidebar[disabled="true"] #sidebarItem {{
                color: {COLORS.TEXT_MUTED};
            }}
            
            /* Loading state */
            #sidebar[loading="true"] {{
                opacity: 0.7;
            }}
            #sidebar[loading="true"] #sidebarNavScroll {{
                background-color: {COLORS.BG_OVERLAY};
            }}
            
            /* ===== 2.3 MOTION ===== */
            /* Width animation handled by QPropertyAnimation */
            
            /* Hover lift effect on items - handled by QPropertyAnimation on geometry */
            
            /* Active indicator glide - handled by QPropertyAnimation */
            
            /* Tooltip fade */
            QToolTip {{
                background-color: {COLORS.BG_FRAME};
                color: {COLORS.TEXT_PRIMARY};
                border: 1px solid {COLORS.BORDER_DEFAULT};
                border-radius: {RADIUS.SM}px;
                padding: {SPACING.SM}px {SPACING.MD}px;
                font-size: 12px;
            }}
            
            /* Scroll smoothing - handled by QScrollArea */
        """)


# ===== INTEGRATION HELPER =====

def create_sidebar(parent=None) -> Sidebar:
    """Factory function to create sidebar instance."""
    return Sidebar(parent)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test sidebar standalone
    sidebar = Sidebar()
    sidebar.show()
    
    # Test toggle after 2 seconds
    QTimer.singleShot(2000, sidebar.toggle_collapse)
    QTimer.singleShot(4000, sidebar.toggle_collapse)
    
    sys.exit(app.exec())