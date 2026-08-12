"""
POP Assistant - Design Tokens (Theme)
Single source of truth for all design values.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ColorTokens:
    """Color palette - 1.2 Color spec"""
    # Background layers
    BG_DEEP: Final[str] = "#0A0E12"           # Deep near-black background
    BG_FRAME: Final[str] = "#111820"          # Dark glass surface (main frame)
    BG_PANEL: Final[str] = "#0F161E"          # Inner panel surface
    BG_OVERLAY: Final[str] = "#0D131A"        # Overlay surface
    BG_HOVER: Final[str] = "#1A2330"          # Hover state
    BG_ACTIVE: Final[str] = "#202D3D"         # Active/pressed state
    BG_FOCUS: Final[str] = "#1E2A3A"          # Focus ring background

    # Borders
    BORDER_SUBTLE: Final[str] = "rgba(255, 255, 255, 0.06)"   # Low-opacity white
    BORDER_DEFAULT: Final[str] = "rgba(255, 255, 255, 0.10)"
    BORDER_STRONG: Final[str] = "rgba(255, 255, 255, 0.18)"
    BORDER_FOCUS: Final[str] = "#00CCFF"        # Cyan focus ring

    # Accent (cyan/teal derived)
    ACCENT_CYAN: Final[str] = "#00FFAA"         # Primary accent
    ACCENT_TEAL: Final[str] = "#00CCFF"         # Secondary accent
    ACCENT_DIM: Final[str] = "rgba(0, 255, 170, 0.15)"  # Dim accent for backgrounds
    ACCENT_GLOW: Final[str] = "rgba(0, 204, 255, 0.4)"   # Glow/shadow

    # Text
    TEXT_PRIMARY: Final[str] = "#E8F0F8"        # Primary text
    TEXT_SECONDARY: Final[str] = "#8BA4B8"      # Secondary text
    TEXT_MUTED: Final[str] = "#5A6E7E"          # Muted/disabled text
    TEXT_INVERSE: Final[str] = "#0A0E12"        # On accent

    # Semantic
    SUCCESS: Final[str] = "#00D47E"
    WARNING: Final[str] = "#FFB800"
    ERROR: Final[str] = "#FF4757"
    INFO: Final[str] = "#00CCFF"

    # Shadow
    SHADOW_SM: Final[str] = "rgba(0, 0, 0, 0.3)"
    SHADOW_MD: Final[str] = "rgba(0, 0, 0, 0.45)"
    SHADOW_LG: Final[str] = "rgba(0, 0, 0, 0.6)"
    SHADOW_ACCENT: Final[str] = "rgba(0, 204, 255, 0.25)"


@dataclass(frozen=True)
class SpacingTokens:
    """Spacing scale - 4px base unit"""
    XS: Final[int] = 4
    SM: Final[int] = 8
    MD: Final[int] = 12
    LG: Final[int] = 16
    XL: Final[int] = 24
    XXL: Final[int] = 32
    XXXL: Final[int] = 48


@dataclass(frozen=True)
class RadiusTokens:
    """Border radius scale"""
    NONE: Final[int] = 0
    SM: Final[int] = 6
    MD: Final[int] = 10
    LG: Final[int] = 14
    XL: Final[int] = 18
    FULL: Final[int] = 9999


@dataclass(frozen=True)
class ShadowTokens:
    """Shadow definitions"""
    SM: Final[str] = "0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)"
    MD: Final[str] = "0 4px 12px rgba(0, 0, 0, 0.4), 0 2px 6px rgba(0, 0, 0, 0.3)"
    LG: Final[str] = "0 12px 32px rgba(0, 0, 0, 0.5), 0 4px 16px rgba(0, 0, 0, 0.35)"
    XL: Final[str] = "0 24px 48px rgba(0, 0, 0, 0.55), 0 8px 24px rgba(0, 0, 0, 0.4)"
    ACCENT_GLOW: Final[str] = "0 0 24px rgba(0, 204, 255, 0.15), 0 0 48px rgba(0, 204, 255, 0.08)"


@dataclass(frozen=True)
class MotionTokens:
    """Motion/Animation tokens - 1.3 Motion spec"""
    # Durations (ms)
    FAST: Final[int] = 120
    NORMAL: Final[int] = 200
    SLOW: Final[int] = 320
    VERY_SLOW: Final[int] = 480

    # Easings (CSS cubic-bezier)
    EASE_OUT: Final[str] = "cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    EASE_IN_OUT: Final[str] = "cubic-bezier(0.4, 0, 0.2, 1)"
    EASE_SPRING: Final[str] = "cubic-bezier(0.34, 1.56, 0.64, 1)"
    EASE_GENTLE: Final[str] = "cubic-bezier(0.23, 1, 0.32, 1)"

    # Window animations
    WINDOW_FADE_IN: Final[int] = 200
    RESIZE_TRANSITION: Final[int] = 160
    MAXIMIZE_RESTORE: Final[int] = 240
    PANEL_ENTRANCE: Final[int] = 280


@dataclass(frozen=True)
class LayoutTokens:
    """Layout constants for App Shell"""
    # Sidebar widths
    SIDEBAR_COLLAPSED: Final[int] = 76
    SIDEBAR_EXPANDED: Final[int] = 260

    # Header height
    HEADER_HEIGHT: Final[int] = 56

    # Window chrome
    CHROME_HEIGHT: Final[int] = 36
    OUTER_BORDER_RADIUS: Final[int] = 14
    INNER_BORDER_RADIUS: Final[int] = 10

    # Minimum window size
    MIN_WIDTH: Final[int] = 900
    MIN_HEIGHT: Final[int] = 600


# Singleton instances
COLORS = ColorTokens()
SPACING = SpacingTokens()
RADIUS = RadiusTokens()
SHADOWS = ShadowTokens()
MOTION = MotionTokens()
LAYOUT = LayoutTokens()


def get_app_stylesheet(colors: ColorTokens, radius: RadiusTokens, shadows: ShadowTokens, layout: LayoutTokens) -> str:
    """Generates the global stylesheet for the POP Assistant application shell."""
    return f"""
        /* General Styles */
        * {{
            font-family: 'Segoe UI', 'Noto Sans', 'DejaVu Sans', sans-serif;
            font-size: 14px;
            color: {colors.TEXT_PRIMARY};
        }}

        /* Main Window (PopView) */
        PopView {{
            background-color: transparent; /* Handled by outerFrame */
            border-radius: {radius.LG}px;
        }}

        /* Outer Frame (for rounded border and subtle glass effect) */
        #outerFrame {{
            background-color: {colors.BG_FRAME}; /* Dark glass surface */
            border: 1px solid {colors.BORDER_SUBTLE}; /* Subtle border */
            border-radius: {radius.LG}px;
        }}

        #outerFrame[activeWindow="true"] {{
            border: 1px solid {colors.BORDER_FOCUS};
        }}

        /* Main Content Area (inner panel) */
        #mainContentArea {{
            background-color: {colors.BG_PANEL}; /* Inner panel surface */
            border-radius: {radius.MD}px; /* Slightly smaller radius than outer frame */
        }}

        /* Window Chrome Area (Title Bar) */
        #windowChromeArea {{
            background-color: {colors.BG_PANEL}; /* Same as inner panel or slightly different */
            border-top-left-radius: {radius.MD}px;
            border-top-right-radius: {radius.MD}px;
            border-bottom: 1px solid {colors.BORDER_SUBTLE};
        }}

        #titleLabel {{
            color: {colors.TEXT_SECONDARY};
            font-size: 15px;
            font-weight: 500;
        }}

        /* Control Buttons */
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {colors.TEXT_SECONDARY};
            font-weight: bold;
            border-radius: {radius.SM}px;
        }}
        QPushButton:hover {{
            background-color: {colors.BG_HOVER};
            color: {colors.TEXT_PRIMARY};
        }}
        QPushButton#closeButton:hover {{
            background-color: {colors.ERROR}; /* Specific hover for close */
            color: {colors.TEXT_PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {colors.BG_ACTIVE};
            color: {colors.TEXT_PRIMARY};
        }}


        /* Sidebar */
        #sidebarSlot {{
            background-color: {colors.BG_OVERLAY}; /* Separate surface color */
            border-right: 1px solid {colors.BORDER_SUBTLE};
            border-bottom-left-radius: {radius.MD}px;
        }}

        /* Header Slot */
        #headerSlot {{
            background-color: {colors.BG_PANEL}; /* Same as inner panel */
            border-bottom: 1px solid {colors.BORDER_SUBTLE};
        }}

        /* Main Workspace Slot */
        #mainWorkspaceSlot {{
            background-color: {colors.BG_PANEL}; /* Main content background */
            border-bottom-right-radius: {radius.MD}px;
        }}

        /* Overlay Slot */
        #overlaySlot {{
            background-color: {colors.BG_OVERLAY}; /* Overlay surface */
            border-radius: {radius.LG}px;
        }}
    """