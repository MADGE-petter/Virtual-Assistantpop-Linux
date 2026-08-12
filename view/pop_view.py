#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PopView - Main application shell for Pop Assistant.
Defines the overall structure, layout, and chrome of the desktop application.
"""

from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem,
)
from PyQt6.QtGui import QMouseEvent, QCursor

from utils.logger import get_logger
from view.styles.theme import COLORS, RADIUS, SHADOWS, LAYOUT, MOTION, get_app_stylesheet
from view.components.sidebar import Sidebar

logger = get_logger(__name__)


class PopView(QWidget):
    """
    The main application shell, providing the desktop application frame,
    window chrome, and slots for content regions.
    """
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Window movement and resize variables
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_corner = ""
        self.border_width = 8
        
        self.init_ui()
        self.setMouseTracking(True)

    def set_controller(self, controller):
        """Set the controller reference for the view."""
        self.controller = controller

    def init_ui(self):
        """Initializes the structural UI components for the app shell."""
        self.setWindowTitle("POP Assistant")
        self.setMinimumSize(LAYOUT.MIN_WIDTH, LAYOUT.MIN_HEIGHT)
        self.resize(1200, 800)

        self.setWindowOpacity(0.0)

        # Animations
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(MOTION.WINDOW_FADE_IN)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.maximize_restore_animation = QPropertyAnimation(self, b"geometry")
        self.maximize_restore_animation.setDuration(MOTION.MAXIMIZE_RESTORE)
        self.maximize_restore_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.normal_geometry = self.geometry()

        # Apply Stylesheet
        self.setStyleSheet(get_app_stylesheet(COLORS, RADIUS, SHADOWS, LAYOUT))

        # Main window container layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Outer frame wrapper (for rounded border and shadow)
        self.outer_frame = QWidget(self)
        self.outer_frame.setObjectName("outerFrame")
        self.outer_frame.setProperty("activeWindow", "true")
        self.outer_frame_layout = QVBoxLayout(self.outer_frame)
        self.outer_frame_layout.setContentsMargins(1, 1, 1, 1)
        self.outer_frame_layout.setSpacing(0)

        # Main content area within the outer frame
        self.main_content_area = QWidget(self.outer_frame)
        self.main_content_area.setObjectName("mainContentArea")
        self.main_content_layout = QVBoxLayout(self.main_content_area)
        self.main_content_layout.setContentsMargins(0, 0, 0, 0) # No margins
        self.main_content_layout.setSpacing(0)

        # 1. Window Chrome Area (Title Bar)
        self.window_chrome_area = QWidget(self.main_content_area)
        self.window_chrome_area.setObjectName("windowChromeArea")
        self.window_chrome_area.setFixedHeight(36) # Defined in LayoutTokens
        self.chrome_layout = QHBoxLayout(self.window_chrome_area)
        self.chrome_layout.setContentsMargins(10, 0, 10, 0)
        self.chrome_layout.setSpacing(5)

        self.logo_label = QLabel(self.window_chrome_area)
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setFixedSize(24, 24) # Placeholder for logo
        self.chrome_layout.addWidget(self.logo_label)

        self.title_label = QLabel("POP Assistant", self.window_chrome_area)
        self.title_label.setObjectName("titleLabel")
        self.chrome_layout.addWidget(self.title_label)
        self.chrome_layout.addStretch()

        self.minimize_button = QPushButton("-", self.window_chrome_area)
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(30, 24)
        self.chrome_layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("[]", self.window_chrome_area)
        self.maximize_button.setObjectName("maximizeButton")
        self.maximize_button.setFixedSize(30, 24)
        self.chrome_layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("X", self.window_chrome_area)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(30, 24)
        self.chrome_layout.addWidget(self.close_button)

        self.main_content_layout.addWidget(self.window_chrome_area)

        # 2. Content Region (Sidebar + Main Workspace)
        self.content_region = QWidget(self.main_content_area)
        self.content_region.setObjectName("contentRegion")
        self.content_h_layout = QHBoxLayout(self.content_region)
        self.content_h_layout.setContentsMargins(0, 0, 0, 0)
        self.content_h_layout.setSpacing(0)

        # 2.1. Sidebar Component (replaces sidebar_slot)
        self.sidebar = Sidebar(self.content_region)
        self.content_h_layout.addWidget(self.sidebar)

        # 2.2. Main Workspace Area (Header + Main Content)
        self.main_workspace_area = QWidget(self.content_region)
        self.main_workspace_area.setObjectName("mainWorkspaceArea")
        self.main_workspace_v_layout = QVBoxLayout(self.main_workspace_area)
        self.main_workspace_v_layout.setContentsMargins(0, 0, 0, 0)
        self.main_workspace_v_layout.setSpacing(0)

        # 2.2.1. Header Slot
        self.header_slot = QWidget(self.main_workspace_area)
        self.header_slot.setObjectName("headerSlot")
        self.header_slot.setFixedHeight(LAYOUT.HEADER_HEIGHT)
        self.main_workspace_v_layout.addWidget(self.header_slot)

        # 2.2.2. Main Workspace Slot
        self.main_workspace_slot = QWidget(self.main_workspace_area)
        self.main_workspace_slot.setObjectName("mainWorkspaceSlot")
        self.main_workspace_v_layout.addWidget(self.main_workspace_slot)

        self.content_h_layout.addWidget(self.main_workspace_area)
        self.main_content_layout.addWidget(self.content_region)

        # Overlay slot (positioned absolutely, on top of everything)
        # For now, just a placeholder QWidget. Will be styled/managed for visibility later.
        self.overlay_slot = QWidget(self) # Parented to PopView for absolute positioning
        self.overlay_slot.setObjectName("overlaySlot")
        self.overlay_slot.hide() # Hidden by default
        # No layout for overlay_slot yet, it will cover the entire window

        self.outer_frame_layout.addWidget(self.main_content_area)
        self.main_layout.addWidget(self.outer_frame)

        # Connect window control buttons (basic functionality for now)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.close_application)

    def close_application(self):
        """Properly close the application."""
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def toggle_maximize_restore(self):
        """Toggle between maximized and normal window states with animation."""
        # Stop any ongoing animation first
        self.maximize_restore_animation.stop()
        
        if self.isMaximized() or self.isFullScreen():
            # Restore to normal - use stored geometry
            self.showNormal()
            # Restore to the stored normal geometry after showNormal
            QTimer.singleShot(0, lambda: self.setGeometry(self.normal_geometry))
            self.maximize_button.setText("[]")
        else:
            # Store current geometry before maximizing
            self.normal_geometry = self.geometry()
            # Maximize to full screen
            self.showMaximized()
            self.maximize_button.setText("O")

    def changeEvent(self, event):
        """Handle window state changes (Active, Inactive, etc.)."""
        if event.type() == event.Type.ActivationChange:
            if self.isActiveWindow():
                self.outer_frame.setProperty("activeWindow", "true")
            else:
                self.outer_frame.setProperty("activeWindow", "false")
            self.outer_frame.style().unpolish(self.outer_frame)
            self.outer_frame.style().polish(self.outer_frame)
        super().changeEvent(event)

    def set_loading(self, is_loading: bool):
        """Toggle the loading state for the app shell."""
        if is_loading:
            self.overlay_slot.show()
            self.main_content_area.setEnabled(False)
        else:
            self.overlay_slot.hide()
            self.main_content_area.setEnabled(True)

    def update_bot_text(self, text: str):
        """Update bot text in the UI (placeholder for now)."""
        logger.debug("[Bot] %s", text)
        # TODO: Implement actual UI update when chat area is built

    def update_user_text(self, text: str):
        """Update user text in the UI (placeholder for now)."""
        logger.debug("[User] %s", text)
        # TODO: Implement actual UI update when chat area is built

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_in_animation.start()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging and resizing."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.pos()
            self._resizing = False
            # Check if resizing from borders
            if self.is_at_border(event.pos()):
                self._resizing = True
                self._resize_corner = self.get_resize_corner(event.pos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging, resizing, and cursor changes."""
        # Update cursor for resizing feedback
        if not self.isMaximized() and not self.isFullScreen():
            if self.is_at_border(event.pos()):
                self.setCursor(self.get_resize_cursor(event.pos()))
            else:
                self.unsetCursor() # Restore default cursor

        # Dragging
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position and not self._resizing:
            if not self.isMaximized(): # Cannot drag when maximized
                self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        # Resizing
        elif event.buttons() == Qt.MouseButton.LeftButton and self._resizing:
            if not self.isMaximized(): # Cannot resize when maximized
                self.resize_window(event)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to stop dragging/resizing."""
        self._drag_position = QPoint()
        self._resizing = False
        self._resize_corner = ""
        event.accept()

    def is_at_border(self, pos: QPoint):
        """Check if mouse is at the window border for resizing."""
        rect = self.rect()
        return (pos.x() < self.border_width or
                pos.x() > rect.width() - self.border_width or
                pos.y() < self.border_width or
                pos.y() > rect.height() - self.border_width)

    def get_resize_corner(self, pos: QPoint):
        """Determine which corner/edge the mouse is over for resizing."""
        rect = self.rect()
        x_at_left = pos.x() < self.border_width
        x_at_right = pos.x() > rect.width() - self.border_width
        y_at_top = pos.y() < self.border_width
        y_at_bottom = pos.y() > rect.height() - self.border_width

        if x_at_left and y_at_top: return "top_left"
        if x_at_right and y_at_top: return "top_right"
        if x_at_left and y_at_bottom: return "bottom_left"
        if x_at_right and y_at_bottom: return "bottom_right"
        if y_at_top: return "top"
        if y_at_bottom: return "bottom"
        if x_at_left: return "left"
        if x_at_right: return "right"
        return ""

    def get_resize_cursor(self, pos: QPoint):
        """Return the appropriate cursor for resizing."""
        corner = self.get_resize_corner(pos)
        if corner == "top_left" or corner == "bottom_right":
            return Qt.CursorShape.SizeFDiagCursor
        if corner == "top_right" or corner == "bottom_left":
            return Qt.CursorShape.SizeBDiagCursor
        if corner == "top" or corner == "bottom":
            return Qt.CursorShape.SizeVerCursor
        if corner == "left" or corner == "right":
            return Qt.CursorShape.SizeHorCursor
        return Qt.CursorShape.ArrowCursor # Default

    def resize_window(self, event: QMouseEvent):
        """Perform window resizing based on drag and corner."""
        current_pos = event.globalPosition().toPoint()
        old_pos = self.pos()
        old_size = self.size()
        new_x, new_y, new_width, new_height = old_pos.x(), old_pos.y(), old_size.width(), old_size.height()

        delta_x = current_pos.x() - event.screenPos().toPoint().x() # event.screenPos() is from mousePressEvent
        delta_y = current_pos.y() - event.screenPos().toPoint().y()

        # This part requires careful calculation based on which edge/corner is being dragged.
        # For simplicity, I'm providing a basic structure. Full implementation
        # of all 8 resize directions is complex and might need a dedicated helper class.
        # Here's a simplified example for one corner:
        if self._resize_corner == "bottom_right":
            new_width = max(self.minimumWidth(), current_pos.x() - old_pos.x())
            new_height = max(self.minimumHeight(), current_pos.y() - old_pos.y())
        elif self._resize_corner == "bottom_left":
            new_width = max(self.minimumWidth(), old_size.width() - delta_x)
            new_x = old_pos.x() + delta_x
            new_height = max(self.minimumHeight(), current_pos.y() - old_pos.y())
        # ... other corners/edges ...

        self.setGeometry(new_x, new_y, new_width, new_height)

    # Override resizeEvent to handle overlay resizing
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position and size the overlay_slot to cover the entire window
        if hasattr(self, 'overlay_slot'):
            self.overlay_slot.setGeometry(self.rect())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = PopView()
    window.show()
    sys.exit(app.exec())
