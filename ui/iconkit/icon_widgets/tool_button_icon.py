"""ui/iconkit/icon_widgets/tool_button_icon.py

Defines the ToolButtonIcon class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

from PySide6.QtCore import QSize
# ── Imports ────────────────────────────────────────────────────────
from PySide6.QtWidgets import QToolButton

from ui.iconkit.effects import ApplyHoverEffects
from ui.iconkit.icon_mixin import IconMixin


class ToolButtonIcon(QToolButton, IconMixin):
    def __init__(
        self,
        file_name: str,
        size: QSize,
        variant: str = "default",
        object_name: str = "",
        checked: bool = False,
        hover_effects: bool = False,
        parent=None
    ):
        """
        Initializes a ToolButtonIcon instance.

        Args:
            file_name (str): The path to the SVG icon file.
            size (QSize): The size of the icon.
            variant (str, optional): The variant of the icon. Defaults to "default".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        self.setCheckable(True)
        self.setChecked(checked)

        self._use_hover_effects = hover_effects
        if self._use_hover_effects:
            ApplyHoverEffects.recolor(self, file_name, size, variant)

        self._init_themed_icon(file_name, size, variant)
