"""
Login View - Styles
Centralized stylesheet for login components.
"""

from view.styles.theme import COLORS, SPACING, RADIUS


def get_login_dialog_qss() -> str:
    """Main login dialog stylesheet"""
    return f"""
QDialog#LoginDialog {{
    background: {COLORS.BG_DEEP};
    border: 1px solid {COLORS.BORDER_SUBTLE};
    border-radius: {RADIUS.LG}px;
}}

QDialog#LoginDialog QLabel#TitleLabel {{
    color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFAA, stop:1 #00CCFF);
    font-size: 28px;
    font-weight: 300;
    padding: 8px 0;
    background: transparent;
}}

QDialog#LoginDialog QLineEdit#InputField {{
    background: {COLORS.BG_FRAME};
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.LG}px;
    color: {COLORS.TEXT_PRIMARY};
    font-size: 14px;
    min-height: 20px;
}}

QDialog#LoginDialog QLineEdit#InputField:focus {{
    border-color: {COLORS.BORDER_FOCUS};
    background: {COLORS.BG_HOVER};
}}

QDialog#LoginDialog QPushButton#PrimaryButton {{
    background: {COLORS.ACCENT_DIM};
    border: 1px solid {COLORS.ACCENT_TEAL};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.XL}px;
    color: {COLORS.ACCENT_CYAN};
    font-size: 14px;
    font-weight: 600;
    min-height: 20px;
}}

QDialog#LoginDialog QPushButton#PrimaryButton:hover {{
    background: rgba(0, 204, 255, 0.25);
    border-color: {COLORS.ACCENT_CYAN};
    color: {COLORS.ACCENT_CYAN};
}}

QDialog#LoginDialog QPushButton#PrimaryButton:pressed {{
    background: rgba(0, 204, 255, 0.35);
}}

QDialog#LoginDialog QPushButton#SecondaryButton {{
    background: transparent;
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.XL}px;
    color: {COLORS.TEXT_SECONDARY};
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}}

QDialog#LoginDialog QPushButton#SecondaryButton:hover {{
    background: {COLORS.BG_HOVER};
    border-color: {COLORS.BORDER_STRONG};
    color: {COLORS.TEXT_PRIMARY};
}}

QDialog#LoginDialog QPushButton#DangerButton {{
    background: rgba(255, 71, 87, 0.15);
    border: 1px solid rgba(255, 71, 87, 0.4);
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.XL}px;
    color: #FF4757;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}}

QDialog#LoginDialog QPushButton#DangerButton:hover {{
    background: rgba(255, 71, 87, 0.25);
    border-color: #FF4757;
    color: #FF6B7A;
}}

QDialog#LoginDialog QLabel#LinkLabel {{
    color: {COLORS.ACCENT_CYAN};
    font-size: 13px;
    font-weight: 500;
    padding: {SPACING.SM}px;
}}

QDialog#LoginDialog QLabel#LinkLabel:hover {{
    color: {COLORS.ACCENT_TEAL};
}}
"""


def get_settings_dialog_qss() -> str:
    """Settings dialog stylesheet"""
    return f"""
QDialog#SettingsDialog {{
    background: {COLORS.BG_FRAME};
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.LG}px;
}}

QDialog#SettingsDialog QLabel {{
    color: {COLORS.TEXT_PRIMARY};
    font-size: 13px;
    padding: {SPACING.SM}px;
}}

QDialog#SettingsDialog QCheckBox {{
    color: {COLORS.TEXT_PRIMARY};
    font-size: 13px;
    padding: {SPACING.SM}px;
    spacing: {SPACING.SM}px;
}}

QDialog#SettingsDialog QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.SM}px;
    background: {COLORS.BG_PANEL};
}}

QDialog#SettingsDialog QCheckBox::indicator:checked {{
    background: {COLORS.ACCENT_CYAN};
    border-color: {COLORS.ACCENT_TEAL};
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IiMwQTBlMTIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
}}

QDialog#SettingsDialog QSpinBox {{
    background: {COLORS.BG_PANEL};
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.SM}px;
    padding: {SPACING.SM}px {SPACING.MD}px;
    color: {COLORS.TEXT_PRIMARY};
    font-size: 13px;
    min-width: 80px;
}}

QDialog#SettingsDialog QSpinBox:focus {{
    border-color: {COLORS.BORDER_FOCUS};
}}

QDialog#SettingsDialog QSlider::groove:horizontal {{
    height: 4px;
    background: {COLORS.BORDER_SUBTLE};
    border-radius: 2px;
}}

QDialog#SettingsDialog QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    margin: -6px 0;
    background: {COLORS.ACCENT_CYAN};
    border-radius: 8px;
}}

QDialog#SettingsDialog QSlider::handle:horizontal:hover {{
    background: {COLORS.ACCENT_TEAL};
}}

QDialog#SettingsDialog QPushButton#DialogButton {{
    background: {COLORS.ACCENT_DIM};
    border: 1px solid {COLORS.ACCENT_TEAL};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.SM}px {SPACING.LG}px;
    color: {COLORS.ACCENT_CYAN};
    font-size: 13px;
    font-weight: 600;
    min-width: 80px;
}}

QDialog#SettingsDialog QPushButton#DialogButton:hover {{
    background: rgba(0, 204, 255, 0.25);
}}

QDialog#SettingsDialog QPushButton#DialogButton:pressed {{
    background: rgba(0, 204, 255, 0.35);
}}

QDialog#SettingsDialog QPushButton#CancelButton {{
    background: transparent;
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.SM}px {SPACING.LG}px;
    color: {COLORS.TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 500;
    min-width: 80px;
}}

QDialog#SettingsDialog QPushButton#CancelButton:hover {{
    background: {COLORS.BG_HOVER};
    border-color: {COLORS.BORDER_STRONG};
    color: {COLORS.TEXT_PRIMARY};
}}
"""


def get_register_dialog_qss() -> str:
    """Register dialog stylesheet"""
    return f"""
QDialog#RegisterDialog {{
    background: {COLORS.BG_DEEP};
    border: 1px solid {COLORS.BORDER_SUBTLE};
    border-radius: {RADIUS.LG}px;
}}

QDialog#RegisterDialog QLabel#DialogTitle {{
    color: {COLORS.ACCENT_CYAN};
    font-size: 16px;
    font-weight: 600;
    padding: {SPACING.MD}px;
}}

QDialog#RegisterDialog QLineEdit#InputField {{
    background: {COLORS.BG_FRAME};
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.LG}px;
    color: {COLORS.TEXT_PRIMARY};
    font-size: 14px;
    min-height: 20px;
}}

QDialog#RegisterDialog QLineEdit#InputField:focus {{
    border-color: {COLORS.BORDER_FOCUS};
    background: {COLORS.BG_HOVER};
}}

QDialog#RegisterDialog QLineEdit#CaptchaInput {{
    background: {COLORS.BG_FRAME};
    border: 1px solid {COLORS.BORDER_DEFAULT};
    border-radius: {RADIUS.MD}px;
    padding: {SPACING.MD}px {SPACING.LG}px;
    color: {COLORS.TEXT_PRIMARY};
    font-size: 14px;
    min-height: 20px;
    max-width: 120px;
}}

QDialog#RegisterDialog QPushButton#CaptchaButton {{
    background: {COLORS.ACCENT_DIM};
    border: 1px solid {COLORS.ACCENT_TEAL};
    border-radius: {RADIUS.MD}px;
    color: {COLORS.ACCENT_CYAN};
    font-size: 16px;
    font-weight: bold;
    font-family: 'Courier New', monospace;
    padding: {SPACING.SM}px {SPACING.MD}px;
    min-width: 60px;
    max-width: 60px;
}}

QDialog#RegisterDialog QPushButton#CaptchaButton:hover {{
    background: rgba(0, 204, 255, 0.25);
    border-color: {COLORS.ACCENT_CYAN};
}}

QDialog#RegisterDialog QPushButton#CaptchaButton:pressed {{
    background: rgba(0, 204, 255, 0.35);
}}
"""


def get_toast_qss(is_success: bool = True) -> str:
    """Toast notification stylesheet"""
    if is_success:
        bg = "rgba(81, 207, 102, 0.9)"
        border = "rgba(81, 207, 102, 1.0)"
    else:
        bg = "rgba(255, 107, 107, 0.9)"
        border = "rgba(255, 107, 107, 1.0)"
    
    return f"""
QLabel#ToastLabel {{
    background: {bg};
    border: 1px solid {border};
    border-radius: {RADIUS.MD}px;
    color: white;
    font-size: 14px;
    font-weight: 500;
    padding: {SPACING.SM}px {SPACING.LG}px;
}}
"""


def get_all_login_qss() -> str:
    """Combine all login stylesheets"""
    return "\n".join([
        get_login_dialog_qss(),
        get_settings_dialog_qss(),
        get_register_dialog_qss(),
    ])