"""Premium Color System - Inspired by Apple, OpenAI, Linear, Arc Browser."""

from PyQt6.QtGui import QColor


# Core Colors
BG_DEEP = QColor("#0F1117")        # Background
BG_SURFACE = QColor("#171A24")     # Surface
BG_CARD = QColor("#1B2230")        # Card
BG_HOVER = QColor("#1E2736")       # Hover state
BG_ACTIVE = QColor("#232D3D")      # Active/pressed state

# Gradient Colors
ACCENT_START = QColor("#00FFAA")   # Primary gradient start
ACCENT_END = QColor("#00CCFF")     # Primary gradient end
ACCENT_MID = QColor("#6464FF")     # Gradient middle

# Border Colors
BORDER = QColor("#263244")         # Default border
BORDER_LIGHT = QColor("#334155")   # Light border
BORDER_FOCUS = QColor("#00FFAA")   # Focus border

# Text Colors
TEXT_PRIMARY = QColor("#F8FAFC")   # Primary text
TEXT_SECONDARY = QColor("#94A3B8") # Secondary text
TEXT_MUTED = QColor("#64748B")     # Muted text
TEXT_INVERSE = QColor("#0F1117")   # On accent backgrounds

# Semantic Colors
SUCCESS = QColor("#20E3B2")        # Success
WARNING = QColor("#FFC857")        # Warning
ERROR = QColor("#FF5C7A")          # Error

# Glass Effects
GLASS_SUBTLE = QColor(255, 255, 255, 8)      # Subtle glass
GLASS_NORMAL = QColor(255, 255, 255, 16)     # Normal glass
GLASS_STRONG = QColor(255, 255, 255, 24)     # Strong glass

# Shadow
SHADOW_COLOR = QColor(0, 0, 0, 60)           # Base shadow
SHADOW_HOVER = QColor(0, 0, 0, 100)          # Hover shadow


# Export dictionary for backward compatibility
COLORS = {
    'bg_deep': BG_DEEP,
    'bg_surface': BG_SURFACE,
    'bg_card': BG_CARD,
    'bg_hover': BG_HOVER,
    'bg_active': BG_ACTIVE,
    'accent_start': ACCENT_START,
    'accent_end': ACCENT_END,
    'accent_mid': ACCENT_MID,
    'border': BORDER,
    'border_light': BORDER_LIGHT,
    'border_focus': BORDER_FOCUS,
    'text_primary': TEXT_PRIMARY,
    'text_secondary': TEXT_SECONDARY,
    'text_muted': TEXT_MUTED,
    'text_inverse': TEXT_INVERSE,
    'success': SUCCESS,
    'warning': WARNING,
    'error': ERROR,
    'glass_subtle': GLASS_SUBTLE,
    'glass_normal': GLASS_NORMAL,
    'glass_strong': GLASS_STRONG,
    'shadow': SHADOW_COLOR,
    'shadow_hover': SHADOW_HOVER,
}


def gradient_primary(vertical: bool = False) -> str:
    """Return CSS gradient string for primary gradient."""
    if vertical:
        return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00FFAA, stop:1 #00CCFF)"
    return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFAA, stop:1 #00CCFF)"


def gradient_vertical() -> str:
    """Vertical primary gradient."""
    return gradient_primary(vertical=True)


def gradient_radial(center_x: float = 0.5, center_y: float = 0.5, radius: float = 0.5) -> str:
    """Radial gradient for backgrounds."""
    return f"qradialgradient(cx:{center_x}, cy:{center_y}, radius:{radius}, fx:{center_x}, fy:{center_y}, stop:0 #00FFAA, stop:1 #00CCFF)"
