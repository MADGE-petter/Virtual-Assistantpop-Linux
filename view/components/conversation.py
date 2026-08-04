"""Conversation Area - Message list with model selector."""

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QScrollArea, QScrollBar, QSizePolicy)
from view.styles.colors import COLORS
from view.styles.typography import Typography
from view.components.message_bubble import MessageBubble


class ModelSelector(QWidget):
    """Model selector dropdown in conversation area."""
    
    model_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # Model label
        self.model_label = QLabel("Model")
        self.model_label.setFont(Typography.caption(QFont.Weight.Medium))
        self.model_label.setStyleSheet(f"color: {COLORS['text_muted'].name()};")
        layout.addWidget(self.model_label)
        
        # Model dropdown
        self.combo = QComboBox()
        self.combo.addItems(["GPT-4o", "GPT-4o-mini", "Claude-3.5-Sonnet", "Gemini-1.5-Pro"])
        self.combo.setFont(Typography.body_sm(QFont.Weight.Medium))
        self.combo.setFixedHeight(32)
        self.combo.setMinimumWidth(180)
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg_card'].name()};
                border: 1px solid {COLORS['border'].name()};
                border-radius: 8px;
                color: {COLORS['text_primary'].name()};
                padding: 0 12px;
                font-family: "Noto Sans", "DejaVu Sans", sans-serif;
            }}
            QComboBox:hover {{
                border-color: {COLORS['border_light'].name()};
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent_start'].name()};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text_secondary'].name()};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS['bg_card'].name()};
                border: 1px solid {COLORS['border'].name()};
                border-radius: 8px;
                color: {COLORS['text_primary'].name()};
                selection-background-color: {COLORS['bg_hover'].name()};
                padding: 4px;
            }}
        """)
        self.combo.currentTextChanged.connect(self.model_changed.emit)
        layout.addWidget(self.combo)
        
        layout.addStretch()
        
    def current_model(self) -> str:
        return self.combo.currentText()
    
    def set_model(self, model: str):
        index = self.combo.findText(model)
        if index >= 0:
            self.combo.setCurrentIndex(index)


class ConversationArea(QWidget):
    """Conversation area with model selector and message list."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {COLORS['bg_deep'].name()}; border: none;")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ── Model Selector Bar ──
        self.model_selector = ModelSelector()
        self.model_selector.model_changed.connect(self._on_model_changed)
        layout.addWidget(self.model_selector)
        
        # ── Separator ──
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background: {COLORS['border'].name()};")
        layout.addWidget(separator)
        
        # ── Message List ──
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border'].name()};
                border-radius: 4px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['border_light'].name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        
        self.message_container = QWidget()
        self.message_container.setStyleSheet("background: transparent;")
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(24, 24, 24, 24)
        self.message_layout.setSpacing(16)
        self.message_layout.addStretch()
        
        self.scroll_area.setWidget(self.message_container)
        layout.addWidget(self.scroll_area, stretch=1)
        
    def _on_model_changed(self, model: str):
        # Can be connected to controller
        pass
    
    def add_message(self, text: str, is_user: bool = False):
        """Add a message bubble to the conversation."""
        # Remove stretch
        self.message_layout.takeAt(self.message_layout.count() - 1)
        
        bubble = MessageBubble(text, is_user)
        self.message_layout.addWidget(bubble)
        
        # Add stretch back
        self.message_layout.addStretch()
        
        # Scroll to bottom
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self._scroll_to_bottom)
        
    def _scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    def current_model(self) -> str:
        return self.model_selector.current_model()
    
    def set_model(self, model: str):
        self.model_selector.set_model(model)
    
    def verticalScrollBar(self):
        return self.scroll_area.verticalScrollBar()