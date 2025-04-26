# helpers/icons/widgets/icon_label.py
#🔸Third-party
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel

from core.application.config import ICON_COLOR
from core.helpers.debug_logger import DebugLogger

#🔸Local Imports
from ..loader import SVGLoader, icon_path

# ────────────────────────────────────────────────────────────────────────────────


class IconLabel(QLabel):
    """Docstring as before…"""
    def __init__(self, name: str, size: QSize, color: str = ICON_COLOR, source: str = "#000", parent=None):
        super().__init__(parent)

        resolved_path = icon_path(name)
        if not resolved_path:
            DebugLogger.log(f"Icon path for '{name}' could not be resolved.", "error")
            return

        pix = SVGLoader.load(resolved_path, color, size, source, as_icon=False)


        self.setPixmap(pix)
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0,0,0,4)
        self.setStyleSheet("background:transparent;")