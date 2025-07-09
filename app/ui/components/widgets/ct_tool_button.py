"""app/ui/widgets/ct_tool_button.py

Defines the Custom-Themed ToolButton class, a QToolButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from app.config import AppIcon, ICON_SIZE
from app.style_manager import IconLoader

from app.style_manager.icons.mixin import IconMixin
from app.style_manager.icons.state import IconState

# ── Constants ───────────────────────────────────────────────────────────────────
PADDING = 4  # Padding around the icon

# ── Class Definition ────────────────────────────────────────────────────────────
class CTToolButton(QToolButton, IconMixin):
    def __init__(
        self,
        icon_or_path: AppIcon | str | Path,
        icon_size: QSize = ICON_SIZE,
        button_size: QSize = None,
        padding: int = PADDING,
        variant: str = "DEFAULT",
        object_name: str = "",
        checkable: bool = False,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a CTToolButton instance.

        Args:
            icon_or_path (AppIcon | str | Path): AppIcon enum or path to the SVG icon file.
            icon_size (QSize): The size of the icon. Defaults to ICON_SIZE.
            button_size (QSize, optional): The fixed size for the button. If None, uses icon size + padding.
            variant (str, optional): The variant of the icon. Defaults to "DEFAULT".
            object_name (str, optional): The object name for the widget. Defaults to "".
            checkable (bool, optional): Whether the button is checked. Defaults to False.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            parent: The parent widget. Defaults to None.
        """
        from app.config.app_icon import AppIcon, ICON_SPECS
        if isinstance(icon_or_path, AppIcon):
            spec = ICON_SPECS[icon_or_path]
            file_path = spec.path
            icon_size = spec.size
            variant = spec.variant
            # Prefer explicit button_size argument, else use from spec if present
            if button_size is None and hasattr(spec, "button_size"):
                button_size = getattr(spec, "button_size", None)
        else:
            file_path = icon_or_path

        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        elif not self.objectName():
            self.setObjectName(Path(file_path).stem)

        self.setCheckable(checkable)
        self.button_size = button_size

        if hover_effects:
            IconState.recolor(self, file_path, icon_size, variant)

        self._init_themed_icon(file_path, icon_size, variant)
        # Set fixed icon_size for the button, using button_size if provided
        if button_size is not None:
            self.setFixedSize(button_size)
        else:
            self.setFixedSize(icon_size.width() + padding, icon_size.height())

        # ── Register with IconLoader ──
        IconLoader().register(self)

    def set_icon_size(self, icon_size: QSize):
        """
        Dynamically update the icon icon_size and refresh the icon rendering.

        Args:
            size (QSize): New size for the icon.
        """
        self.setIconSize(icon_size)
        self._icon_size = icon_size
        self.update()
