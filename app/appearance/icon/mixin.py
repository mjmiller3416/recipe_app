"""app/theme_manager/icon/mixin.py

This module provides a mixin for QAbstractButton widgets to handle themed icons
with state management.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon

from app.config import FALLBACK_COLOR
from app.appearance.icon.config import Name, State, Type
from app.appearance.icon.loader import IconLoader
from app.appearance.icon.svg_loader import SVGLoader


# ── Icon Mixin ───────────────────────────────────────────────────────────────────────────────
class IconMixin:
    """A mixin to provide theme-aware, stateful icon logic to QAbstractButton widgets."""
    def _init_icon(self, icon_enum: Name, type: Type = Type.DEFAULT):
        """Initializes the icon states, caches them, and registers for theme updates."""
        self._icon_enum = icon_enum
        self._icon_spec = icon_enum.spec
        self._type = type
        self._icons: dict[State, QIcon] = {}
        self._state_overrides: dict[State, str] = {}

        self.setIconSize(self._icon_spec.size.value)

        IconLoader.register(self)

        # Ensure icons are immediately available even if palette is empty
        if not self._icons:
            palette = IconLoader.get_palette()
            if palette:
                self.refresh_theme(palette)

    def setIconFromName(self, icon_enum: Name):
        """Sets the icon for this button from a Name enum."""
        # Get type from button class (should be set during button initialization)
        button_type = getattr(self, '_button_type', Type.DEFAULT)
        self._init_icon(icon_enum, button_type)

    def setStateDefault(self, color_role: str):
        """Override the default state color with a specific palette role."""
        if not hasattr(self, '_state_overrides'):
            self._state_overrides = {}
        self._state_overrides[State.DEFAULT] = color_role
        self._refresh_if_ready()

    def setStateHover(self, color_role: str):
        """Override the hover state color with a specific palette role."""
        if not hasattr(self, '_state_overrides'):
            self._state_overrides = {}
        self._state_overrides[State.HOVER] = color_role
        self._refresh_if_ready()

    def setStateChecked(self, color_role: str):
        """Override the checked state color with a specific palette role."""
        if not hasattr(self, '_state_overrides'):
            self._state_overrides = {}
        self._state_overrides[State.CHECKED] = color_role
        self._refresh_if_ready()

    def setStateDisabled(self, color_role: str):
        """Override the disabled state color with a specific palette role."""
        if not hasattr(self, '_state_overrides'):
            self._state_overrides = {}
        self._state_overrides[State.DISABLED] = color_role
        self._refresh_if_ready()

    def clearStateOverride(self, state: State):
        """Clear a specific state override, reverting to the Type default."""
        if state in self._state_overrides:
            del self._state_overrides[state]
            self._refresh_if_ready()

    def clearAllStateOverrides(self):
        """Clear all state overrides, reverting to Type defaults."""
        self._state_overrides.clear()
        self._refresh_if_ready()

    def _refresh_if_ready(self):
        """Refresh icons if the button is initialized and has a palette."""
        if hasattr(self, '_icon_enum') and IconLoader.get_palette():
            palette = IconLoader.get_palette()
            self.refresh_theme(palette)

    def _resolve_color_for_state(self, state: State) -> str:
        """Resolve the color for a given state based on overrides or button type."""
        palette = IconLoader.get_palette()
        
        # Check for state override first
        if hasattr(self, '_state_overrides') and state in self._state_overrides:
            palette_role = self._state_overrides[state]
        else:
            # Fall back to Type defaults
            state_colors = self._type.state_map
            palette_role = state_colors.get(state, "on_surface")
        
        return palette.get(palette_role, FALLBACK_COLOR)

    def refresh_theme(self, palette: dict) -> None:
        """Called by IconLoader. Regenerates all icon states and applies the correct one."""
        # Cache clearing is now handled centrally by IconLoader

        # use the custom size if it's been set, otherwise use the default from the spec
        render_size = self._custom_icon_size if self._custom_icon_size else self._icon_spec.size.value

        # generate icons for each state using the simplified approach
        self._icons = {}
        for state in State:
            color = self._resolve_color_for_state(state)
            icon = SVGLoader.load(
                file_path=self._icon_spec.name.path,
                color=color,
                size=self._icon_spec.size.value,
                as_icon=True
            )
            self._icons[state] = icon

        self._update_icon()

    def _update_icon(self) -> None:
        """Applies the correct icon from the cache based on the button's current state."""
        from PySide6.QtWidgets import QAbstractButton

        # Ensure icons are loaded before trying to use them
        if not self._icons:
            return

        if not self.isEnabled():
            icon = self._icons.get(State.DISABLED)
        elif self.isChecked():
            icon = self._icons.get(State.CHECKED)
        else:
            icon = self._icons.get(State.DEFAULT)

        # Only set icon if we have a valid one
        if icon is not None:
            QAbstractButton.setIcon(self, icon)

    def enterEvent(self, event: QEvent) -> None:
        """Handle icon state change on mouse enter. Override in concrete classes to call parent."""
        if self.isEnabled() and not self.isChecked() and self._icons:
            from PySide6.QtWidgets import QAbstractButton
            hover_icon = self._icons.get(State.HOVER)
            if hover_icon is not None:
                QAbstractButton.setIcon(self, hover_icon)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle icon state change on mouse leave. Override in concrete classes to call parent."""
        if self.isEnabled() and not self.isChecked():
            self._update_icon()

    def changeEvent(self, event: QEvent) -> None:
        """Handle icon state change on widget state changes. Override in concrete classes to call parent."""
        if event.type() == QEvent.Type.EnabledChange:
            self._update_icon()
