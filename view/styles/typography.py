"""Typography System - Noto Sans (Vietnamese-friendly), DejaVu Sans, JetBrains Mono."""

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import QFile, QIODevice


class Typography:
    """Typography system with font scales and weights."""
    
    # Font families - dùng font có sẵn trên hệ thống, hỗ trợ tiếng Việt tốt
    PRIMARY = "Noto Sans"
    SECONDARY = "DejaVu Sans"
    MONO = "JetBrains Mono"
    
    # Weights
    LIGHT = QFont.Weight.Light
    REGULAR = QFont.Weight.Normal
    MEDIUM = QFont.Weight.Medium
    SEMIBOLD = QFont.Weight.DemiBold
    BOLD = QFont.Weight.Bold
    
    @classmethod
    def _load_fonts(cls):
        """Load custom fonts if available."""
        # Fonts should be loaded at app startup
        pass
    
    @classmethod
    def _font(cls, family: str, size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        font = QFont(family, size)
        font.setWeight(weight)
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        return font
    
    # Display
    @classmethod
    def display_lg(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 48, weight)
    
    @classmethod
    def display_md(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 36, weight)
    
    @classmethod
    def display_sm(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 28, weight)
    
    # Headings
    @classmethod
    def h1(cls, weight: QFont.Weight = SEMIBOLD) -> QFont:
        return cls._font(cls.PRIMARY, 24, weight)
    
    @classmethod
    def h2(cls, weight: QFont.Weight = SEMIBOLD) -> QFont:
        return cls._font(cls.PRIMARY, 20, weight)
    
    @classmethod
    def h3(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 18, weight)
    
    @classmethod
    def h4(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 16, weight)
    
    # Body
    @classmethod
    def body_lg(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 16, weight)
    
    @classmethod
    def body(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 14, weight)
    
    @classmethod
    def body_sm(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 13, weight)
    
    @classmethod
    def body_xs(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 12, weight)
    
    # Caption
    @classmethod
    def caption(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 11, weight)
    
    @classmethod
    def caption_sm(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.PRIMARY, 10, weight)
    
    # Code
    @classmethod
    def code(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.MONO, 13, weight)
    
    @classmethod
    def code_sm(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.MONO, 12, weight)
    
    @classmethod
    def mono(cls, weight: QFont.Weight = REGULAR) -> QFont:
        return cls._font(cls.MONO, 14, weight)
    
    # UI
    @classmethod
    def button(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 14, weight)
    
    @classmethod
    def label(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        return cls._font(cls.PRIMARY, 12, weight)
    
    @classmethod
    def overline(cls, weight: QFont.Weight = MEDIUM) -> QFont:
        font = cls._font(cls.PRIMARY, 10, weight)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        return font