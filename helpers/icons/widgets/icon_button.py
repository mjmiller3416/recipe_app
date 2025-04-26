# helpers/icons/widgets/icon_button.py
#🔸Third-party
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from core.application.config import (ICON_COLOR, ICON_COLOR_CHECKED,
                                     ICON_COLOR_HOVER)

from ..effects import ApplyHoverEffects
#🔸Local Imports
from ..factory import IconFactory


class IconButton(QPushButton):
    """Docstring as before…"""
    def __init__(
        self,
        path: str,
        size: QSize,
        default_color: str = ICON_COLOR,
        hover_color:   str = ICON_COLOR_HOVER,
        checked_color: str = ICON_COLOR_CHECKED,
        parent=None
    ):
        super().__init__(parent)
        default_i, hover_i, checked_i = IconFactory.make_icons(
            path, size, default_color, hover_color, checked_color
        )
        self.setIcon(default_i if not self.isChecked() else checked_i)
        self.setIconSize(size)
        self.setStyleSheet("background:transparent; border:none;")
        ApplyHoverEffects.apply(self, default_i, hover_i, checked_i)