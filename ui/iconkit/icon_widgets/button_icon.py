"""ui/iconkit/icon_widgets/button_icon.py

Defines the ButtonIcon class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

from PySide6.QtCore import QSize
# ── Imports ────────────────────────────────────────────────────────
from PySide6.QtWidgets import QPushButton

from ui.iconkit.effects import ApplyHoverEffects
from ui.iconkit.icon_mixin import IconMixin


# ── Class Definition ────────────────────────────────────────────────────────────
class ButtonIcon(QPushButton, IconMixin):
    def __init__(
        self,
        file_name: str,
        size: QSize,
        variant: str = "default",
        label: str = "",
        object_name: str = "",
        checked: bool = False,
        hover_effects: bool = False,
        parent=None
    ):
        """
        Initializes a ButtonIcon instance.

        Args:
            file_name (str): The path to the SVG icon file.
            size (QSize): The size of the icon.
            variant (str, optional): The variant of the icon. Defaults to "default".
            label (str, optional): The text label for the button. Defaults to "".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checked (bool, optional): Whether the button is checked. Defaults to False.
            parent: The parent widget. Defaults to None.
        """
        super().__init__(label, parent)

        if object_name:
            self.setObjectName(object_name)

        self.setCheckable(True)
        self.setChecked(checked)

        self._use_hover_effects = hover_effects
        if hasattr(self, "_use_hover_effects") and self._use_hover_effects:
            ApplyHoverEffects.recolor(self, file_name, size, variant)
        
        self._init_themed_icon(file_name, size, variant)
