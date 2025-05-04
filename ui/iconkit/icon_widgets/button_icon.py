"""ui/iconkit/icon_widgets/button_icon.py

Defines the ButtonIcon class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton
from ui.iconkit.base_button_icon import BaseButtonIcon

# ── Class Definition ────────────────────────────────────────────────
class ButtonIcon(QPushButton, BaseButtonIcon):
    def __init__(
        self,
        file_name: str,
        size: QSize,
        variant: str = "default",
        label: str = "",
        object_name: str = "",
        checked: bool = False,
        parent=None
    ):
        """
        Flexible QPushButton that supports SVG icons, theming, labels, and object naming.

        Args:
            file_name (str): The name of the SVG file.
            size (QSize): The size of the icon.
            variant (str): The color variant to use (e.g., "default", "nav", "error").
            label (str): Optional button label (for sidebar or general use).
            object_name (str): Optional objectName for styling and querying.
            checked (bool): Initial checked state (for toggle-style buttons).
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(label, parent)

        if object_name:
            self.setObjectName(object_name)

        self.setCheckable(True)
        self.setChecked(checked)

        self._init_button_icon(file_name, size, variant)
