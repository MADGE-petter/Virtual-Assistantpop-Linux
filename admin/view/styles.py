#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Admin Panel Styles (Modern Redesign 2026)
Clean, professional dark theme with sidebar navigation
"""

# ═══════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════
PRIMARY = "#6366f1"        # Indigo
PRIMARY_LIGHT = "#818cf8"
PRIMARY_DARK = "#4f46e5"
ACCENT = "#06b6d4"         # Cyan
ACCENT_LIGHT = "#22d3ee"
SUCCESS = "#10b981"        # Emerald
WARNING = "#f59e0b"        # Amber
DANGER = "#ef4444"         # Red
INFO = "#3b82f6"           # Blue

BG_DARKEST = "#0f1117"
BG_DARK = "#161822"
BG_SIDEBAR = "#12141e"
BG_CARD = "#1a1d2e"
BG_CARD_HOVER = "#1e2138"
BG_INPUT = "#1e2030"

TEXT_PRIMARY = "#e2e8f0"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"
BORDER = "#1e293b"
BORDER_ACTIVE = "#6366f1"

# ═══════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════
MAIN_WINDOW = f"""
QMainWindow {{
    background-color: {BG_DARKEST};
    color: {TEXT_PRIMARY};
}}
QWidget {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', sans-serif;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 6px;
    margin: 0;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {TEXT_MUTED};
    min-height: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_SECONDARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_DARK};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {TEXT_MUTED};
    min-width: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {TEXT_SECONDARY};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
"""

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
SIDEBAR = f"""
QFrame#sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
    border-radius: 0px;
}}
"""

SIDEBAR_LOGO = f"""
QLabel {{
    color: {PRIMARY_LIGHT};
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 8px 0px;
}}
"""

SIDEBAR_SUBTITLE = f"""
QLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    letter-spacing: 0.5px;
}}
"""

SIDEBAR_BUTTON = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: rgba(99, 102, 241, 0.1);
    color: {TEXT_PRIMARY};
}}
QPushButton:checked {{
    background-color: rgba(99, 102, 241, 0.15);
    color: {PRIMARY_LIGHT};
    font-weight: 600;
    border-left: 3px solid {PRIMARY};
}}
"""

SIDEBAR_BUTTON_DANGER = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: rgba(239, 68, 68, 0.1);
    color: {DANGER};
}}
"""

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
HEADER_FRAME = f"""
QFrame#header {{
    background-color: {BG_DARK};
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
}}
"""

HEADER_TITLE = f"""
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 18px;
    font-weight: 600;
}}
"""

HEADER_BREADCRUMB = f"""
QLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
"""

HEADER_TIME = f"""
QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
    background-color: {BG_CARD};
    border-radius: 8px;
    padding: 6px 14px;
}}
"""

HEADER_STATUS = f"""
QLabel {{
    color: {SUCCESS};
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 20px;
    padding: 6px 16px;
}}
"""

# ═══════════════════════════════════════════════════════════
# CONTENT AREA
# ═══════════════════════════════════════════════════════════
CONTENT_AREA = f"""
QFrame#content {{
    background-color: {BG_DARKEST};
    border: none;
}}
"""

# ═══════════════════════════════════════════════════════════
# STATS CARDS (Dashboard)
# ═══════════════════════════════════════════════════════════
def stats_card_style(color):
    return f"""
QFrame#statsCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 0px;
}}
QFrame#statsCard:hover {{
    background-color: {BG_CARD_HOVER};
    border: 1px solid {color};
}}
"""

STATS_CARD_VALUE = f"""
QLabel {{
    font-size: 32px;
    font-weight: 700;
    background: transparent;
    border: none;
    padding: 0px;
}}
"""

STATS_CARD_LABEL = f"""
QLabel {{
    font-size: 12px;
    color: {TEXT_MUTED};
    font-weight: 500;
    background: transparent;
    border: none;
    padding: 0px;
}}
"""

STATS_CARD_ICON = f"""
QLabel {{
    font-size: 24px;
    background: transparent;
    border: none;
    padding: 0px;
}}
"""

# ═══════════════════════════════════════════════════════════
# TABLES
# ═══════════════════════════════════════════════════════════
TABLE_WIDGET = f"""
QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    gridline-color: {BORDER};
    color: {TEXT_PRIMARY};
    selection-background-color: rgba(99, 102, 241, 0.15);
    outline: none;
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid rgba(30, 41, 59, 0.5);
    color: {TEXT_PRIMARY};
    background: transparent;
}}
QTableWidget::item:selected {{
    background-color: rgba(99, 102, 241, 0.2);
    color: #ffffff;
}}
QTableWidget::item:hover {{
    background-color: rgba(99, 102, 241, 0.08);
}}
QHeaderView::section {{
    background-color: {BG_DARK};
    color: {TEXT_SECONDARY};
    padding: 12px 14px;
    border: none;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border-right: 1px solid {BORDER};
    border-bottom: 2px solid {BORDER};
}}
QHeaderView::section:last {{
    border-right: none;
}}
"""

# ═══════════════════════════════════════════════════════════
# BUTTONS
# ═══════════════════════════════════════════════════════════
def button_style(bg_color, hover_color, text_color="#ffffff"):
    return f"""
QPushButton {{
    background-color: {bg_color};
    color: {text_color};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {hover_color};
}}
QPushButton:pressed {{
    background-color: {bg_color};
}}
QPushButton:disabled {{
    background-color: {BG_CARD};
    color: {TEXT_MUTED};
}}
"""

BUTTON_PRIMARY = button_style(PRIMARY, PRIMARY_DARK)
BUTTON_SUCCESS = button_style(SUCCESS, "#059669")
BUTTON_DANGER = button_style(DANGER, "#dc2626")
BUTTON_WARNING = button_style(WARNING, "#d97706")
BUTTON_INFO = button_style(INFO, "#2563eb")
BUTTON_ACCENT = button_style(ACCENT, "#0891b2")

BUTTON_LOGOUT = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: rgba(239, 68, 68, 0.1);
    color: {DANGER};
    border: 1px solid rgba(239, 68, 68, 0.3);
}}
"""

# Legacy aliases for backward compatibility
BUTTON_GREEN = BUTTON_SUCCESS
BUTTON_RED = BUTTON_DANGER
BUTTON_BLUE = BUTTON_PRIMARY
BUTTON_ORANGE = BUTTON_WARNING
BUTTON_PURPLE = button_style("#8b5cf6", "#7c3aed")

# ═══════════════════════════════════════════════════════════
# INPUTS
# ═══════════════════════════════════════════════════════════
INPUT_STYLE = f"""
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {PRIMARY};
    background-color: {BG_INPUT};
}}
QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}
"""

COMBO_BOX = f"""
QComboBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    min-height: 20px;
}}
QComboBox:hover {{
    border: 1px solid {PRIMARY};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border-left: 1px solid {BORDER};
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_MUTED};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    selection-background-color: rgba(99, 102, 241, 0.15);
    selection-color: {TEXT_PRIMARY};
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    min-height: 28px;
    border-radius: 6px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: rgba(99, 102, 241, 0.1);
}}
"""

# ═══════════════════════════════════════════════════════════
# TEXT EDIT / LOG
# ═══════════════════════════════════════════════════════════
LOG_TEXT = f"""
QTextEdit {{
    background-color: {BG_DARK};
    color: {ACCENT_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
    font-family: 'Cascadia Code', 'Consolas', 'Fira Code', monospace;
    font-size: 12px;
    selection-background-color: rgba(6, 182, 212, 0.2);
}}
"""

# ═══════════════════════════════════════════════════════════
# CARDS & FRAMES
# ═══════════════════════════════════════════════════════════
CARD_FRAME = f"""
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px;
}}
"""

INFO_FRAME = f"""
QFrame#infoFrame {{
    background-color: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 12px;
    padding: 16px;
}}
"""

INFO_LABEL = f"""
QLabel {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
    padding: 4px;
    line-height: 1.6;
}}
"""

# ═══════════════════════════════════════════════════════════
# GROUP BOX
# ═══════════════════════════════════════════════════════════
GROUP_BOX = f"""
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    margin-top: 18px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 6px 16px;
    background-color: {PRIMARY};
    border-radius: 8px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
"""

# ═══════════════════════════════════════════════════════════
# PROGRESS BAR
# ═══════════════════════════════════════════════════════════
def progress_bar_style(color=PRIMARY):
    return f"""
QProgressBar {{
    background-color: {BG_DARK};
    border: 1px solid {BORDER};
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 10px;
    font-weight: 600;
}}
QProgressBar::chunk {{
    background-color: {color};
    border-radius: 5px;
}}
"""

PROGRESS_GREEN = progress_bar_style(SUCCESS)
PROGRESS_YELLOW = progress_bar_style(WARNING)
PROGRESS_RED = progress_bar_style(DANGER)

# ═══════════════════════════════════════════════════════════
# SECTION TITLE
# ═══════════════════════════════════════════════════════════
SECTION_TITLE = f"""
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.3px;
    padding: 0px;
    border: none;
    background: transparent;
}}
"""

SECTION_SUBTITLE = f"""
QLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.2px;
    padding: 0px;
    border: none;
    background: transparent;
}}
"""

# ═══════════════════════════════════════════════════════════
# SEPARATOR
# ═══════════════════════════════════════════════════════════
SEPARATOR = f"""
QFrame {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}
"""

# ═══════════════════════════════════════════════════════════
# DIALOG
# ═══════════════════════════════════════════════════════════
DIALOG_MAIN = f"""
QDialog {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {PRIMARY};
}}
"""

DIALOG_CONVERSATION = f"""
QDialog {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    padding: 4px;
}}
QTextEdit {{
    background-color: {BG_DARKEST};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QPushButton {{
    background-color: {PRIMARY};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {PRIMARY_DARK};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QFrame {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px;
    margin: 4px;
}}
"""

CONVERSATION_HEADER = f"""
QFrame {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 16px;
}}
"""

# ═══════════════════════════════════════════════════════════
# ONLINE BADGE
# ═══════════════════════════════════════════════════════════
ONLINE_BADGE = f"""
QLabel {{
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
    color: {SUCCESS};
}}
"""

# ═══════════════════════════════════════════════════════════
# TAB WIDGET (for sub-tabs within pages)
# ═══════════════════════════════════════════════════════════
TAB_WIDGET = f"""
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_CARD};
    border-radius: 12px;
    padding: 16px;
    margin-top: -1px;
}}
QTabBar::tab {{
    background-color: {BG_DARK};
    color: {TEXT_SECONDARY};
    padding: 10px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid {BORDER};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {PRIMARY_LIGHT};
    border-bottom: 2px solid {PRIMARY};
}}
QTabBar::tab:hover:!selected {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_PRIMARY};
}}
"""

# ═══════════════════════════════════════════════════════════
# BADGE / TAG
# ═══════════════════════════════════════════════════════════
def badge_style(color):
    return f"""
QLabel {{
    background-color: rgba({_hex_to_rgb_str(color)}, 0.15);
    color: {color};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}
"""

def _hex_to_rgb_str(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    return "99, 102, 241"

# ═══════════════════════════════════════════════════════════
# Legacy glass_card for backward compatibility
# ═══════════════════════════════════════════════════════════
def glass_card(accent_color=PRIMARY, alpha=0.06):
    r, g, b = int(accent_color[1:3], 16), int(accent_color[3:5], 16), int(accent_color[5:7], 16)
    return f"""
QFrame {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba({r}, {g}, {b}, {alpha}),
                   stop:0.5 rgba({r}, {g}, {b}, {alpha * 0.5}),
                   stop:1 rgba({r}, {g}, {b}, {alpha * 0.3}));
    border: 1px solid rgba({r}, {g}, {b}, 0.18);
    border-radius: 14px;
    padding: 16px;
}}
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
    border: none;
}}
"""

# Legacy stats card colors
STATS_CARD_BLUE = f"color: {INFO};"
STATS_CARD_GREEN = f"color: {SUCCESS};"
STATS_CARD_ORANGE = f"color: {WARNING};"
STATS_CARD_RED = f"color: {DANGER};"

# Legacy footer
FOOTER_FRAME = f"""
QFrame {{
    background-color: {BG_DARK};
    border-top: 1px solid {BORDER};
    border-radius: 0px;
    padding: 8px 16px;
}}
"""

FOOTER_INFO = f"""
QLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    letter-spacing: 0.3px;
}}
"""
