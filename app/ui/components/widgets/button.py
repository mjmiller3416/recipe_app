"""app/ui/components/widgets/ct_button.py

Defines the Custom-Themed Button class, a QPushButton subclass with theme-aware dynamic SVG icon states.
"""

# ── Imports ────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QPushButton
from app.theme_manager.icon.mixin import IconMixin
from app.theme_manager.icon import IconLoader, IconState
from app.theme_manager.icon.config import Name, Size, Type

# ── Class Definition ────────────────────────────────────────────────────────────────────────
class Button(QPushButton, IconMixin):
    def __init__(
        self,
        icon_name: Name,
        icon_size: Size = Size.MEDIUM,
        icon_type: Type = Type.DEFAULT,
        label: str = "",
        checkable: bool = True,
        hover_effects: bool = True,
        parent=None
    ):
        """
        Initializes a Button instance using enum-driven icon config.

        Args:
            icon_name (Name): Enum representing the icon file.
            icon_size (Size): Enum for icon dimensions.
            icon_type (Type): Enum for themed icon color behavior.
            label (str): Optional text label.
            checkable (bool): Whether the button is checkable.
            hover_effects (bool): Apply hover/checked effects.
            parent: Optional QWidget parent.
        """
        super().__init__(label, parent)
        self.setCheckable(checkable)

        # Apply dynamic recoloring (hover/checked/disabled states)
        if hover_effects and icon_type != Type.DEFAULT:
            IconState.recolor(
                button=self,
                icon_path=icon_name.path,
                size=icon_size.value,
                variant=icon_type.state_map
            )

        # Apply base icon (fallback/default state)
        self._init_themed_icon(icon_name, icon_size, icon_type)

        # Register with the IconLoader for theme refresh
        IconLoader.register(self)
