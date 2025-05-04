"""ui/iconkit/icon_widgets/tool_button_icon.py

Defines the ToolButtonIcon class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from ui.iconkit.base_button_icon import BaseButtonIcon

# ── Class Definition ────────────────────────────────────────────────
class ToolButtonIcon(QToolButton, BaseButtonIcon):
    """QToolButton variant with the themed-icon mix-in."""

    def __init__(
            self,
            file_name: str,
            size: QSize,
            variant: str = "default",
            object_name: str = "",
            checked: bool = False,
            parent=None
        ) -> None:
        """Initialize the ToolButtonIcon with a name and size.
        Args:
            name (str): The name of the icon.
            size (QSize): The size of the icon.
            variant (str): The variant of the icon. Defaults to "default".
            object_name (str): The object name of the icon. Defaults to "".
            checked (bool): Whether the icon is checked. Defaults to False.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)  

        if object_name:
            self.setObjectName(object_name)

        self.setCheckable(True)
        self.setChecked(checked)

        self._init_button_icon(file_name, size, variant)
