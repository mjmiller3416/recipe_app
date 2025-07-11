"""app/ui/widgets/ct_button.py

Defines the Custom-Themed Buttom class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

from app.config import AppIcon, ICON_SIZE
from app.style_manager.icons.loader import IconLoader

from app.style_manager.icons import IconState, IconMixin

# ── Class Definition ────────────────────────────────────────────────────────────
class CTButton(QPushButton, IconMixin):
    def __init__(
        self,
        icon_or_path: AppIcon | str | Path,
        icon_size: QSize = ICON_SIZE,
        variant: str = "DEFAULT",
        height: int = 55,
        label: str = "",
        checkable: bool = True,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a CTButton instance.

        Args:
            icon_or_path (AppIcon | str | Path): AppIcon enum or path to the SVG icon file.
            icon_size (QSize, optional): The size of the icon. Defaults to ICON_SIZE.
            variant (str, optional): The variant of the icon. Defaults to "DEFAULT".
            label (str, optional): The text label for the button. Defaults to "".
            checkable (bool, optional): Whether the button is checkable. Defaults to True.
            hover_effects (bool, optional): Whether to apply hover effects. Defaults to True.
            parent: The parent widget. Defaults to None.
        """
        # Support AppIcon enum or direct path
        from app.config.app_icon import AppIcon, ICON_SPECS
        if isinstance(icon_or_path, AppIcon):
            spec = ICON_SPECS[icon_or_path]
            file_path = spec.path
            icon_size = spec.size
            variant = spec.variant
            # Prefer explicit height argument, else use from spec if present
            if hasattr(spec, "button_size") and spec.button_size is not None:
                # Use the height of button_size if not explicitly set
                if height == 55:  # 55 is the default
                    height = spec.button_size.height()
        else:
            file_path = icon_or_path

        super().__init__(label, parent)

        self.setCheckable(checkable)
        self.setFixedHeight(height)

        if hover_effects:
            IconState.recolor(self, file_path, icon_size, variant)

        self._init_themed_icon(file_path, icon_size, variant)

        # ── Register with IconLoader ──
        IconLoader().register(self)
