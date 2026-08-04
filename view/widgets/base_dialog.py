"""
Base dialog class for Pop Assistant dialogs.
"""
from PyQt6.QtWidgets import QDialog


class FooterDialog(QDialog):
    """Base class for all dialogs that use a footer watermark."""

    def resizeEvent(self, event):
        super().resizeEvent(event)
