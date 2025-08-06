"""app/appearance/icon/icon.py

Consolidated icon system providing BaseIcon, ThemedIcon, Icon, and StateIcon classes.

This module replaces the previous icon.py and mixin.py files, providing a cleaner
hierarchy for theme-aware SVG icons with state management.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget, QSizePolicy, QVBoxLayout
from PySide6.QtGui import QIcon

from app.config import FALLBACK_COLOR
from app.appearance.icon.config import Name, State, Type
from app.appearance.icon.loader import IconLoader
from app.appearance.icon.svg_loader import SVGLoader

from dev_tools import DebugLogger


# ── BaseIcon ─────────────────────────────────────────────────────────────────────────────────
class BaseIcon:
    """Base class for all icon types providing core rendering logic.

    Handles size, color, and SVG rendering via SVGLoader.
    No theme awareness - meant to be subclassed.
    """

    def __init__(self, icon_enum: Name):
        """Initialize base icon with icon enum.

        Args:
            icon_enum (Name): The predefined icon enum to use.
        """
        self._icon_enum = icon_enum
        self._icon_spec = icon_enum.spec
        self._custom_size = None
        self._custom_color = None

        # default to spec size
        self._current_size = self._icon_spec.size.value

    def setSize(self, width: int, height: int):
        """Set a custom rendering size for the icon.

        Args:
            width (int): Width in pixels.
            height (int): Height in pixels.
        """
        # validate size bounds
        width = max(1, min(width, 512))  # reasonable limits
        height = max(1, min(height, 512))

        self._custom_size = QSize(width, height)
        self._current_size = self._custom_size
        self._render_icon()

    def setColor(self, color: str):
        """Set a custom color for rendering.

        Args:
            color (str): Hex value or theme role (e.g., "#FF0000" or "on_surface").
        """
        self._custom_color = color
        self._render_icon()

    def clearColor(self):
        """Clear the custom color and fall back to the default."""
        self._custom_color = None
        self._render_icon()

    def _get_color(self) -> str:
        """Determine the effective color for rendering.

        Returns:
            str: Final hex color to be applied.
        """
        if self._custom_color:
            if self._custom_color.startswith("#"):
                return self._custom_color
            else:
                # it's a palette role - subclasses should handle this
                return FALLBACK_COLOR
        return FALLBACK_COLOR

    def _get_size(self) -> QSize:
        """Determine the effective rendering size.

        Returns:
            QSize: Final QSize to render the icon with.
        """
        return self._current_size

    def _render_icon(self):
        """Trigger a re-render of the icon using the current size and color settings.

        Base implementation does nothing - subclasses should override.
        """
        pass


# ── ThemedIcon ───────────────────────────────────────────────────────────────────────────────
class ThemedIcon(BaseIcon):
    """Themed extension of BaseIcon with automatic palette updates.

    Adds theme-awareness and integrates with existing IconLoader protocol.
    Used by all theme-reactive icon widgets.
    """

    def __init__(self, icon_enum: Name):
        """Initialize themed icon.

        Args:
            icon_enum (Name): The predefined icon enum to use.
        """
        super().__init__(icon_enum)

        # callback for when theme changes - set by owner widget
        self._refresh_callback = None

        # debounce timer for theme updates
        self._refresh_timer = None

        # register for theme updates
        IconLoader.register(self)

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            IconLoader.unregister(self)
        except:
            pass  # iconLoader might already be destroyed

    def set_refresh_callback(self, callback):
        """Set callback function to call when theme refreshes.

        Args:
            callback: Function to call when theme changes.
        """
        self._refresh_callback = callback

    def refresh_theme(self, palette: dict[str, str]):
        """Called when the theme palette updates. Refreshes icon appearance.

        Compatible with existing IconLoader protocol. Includes debouncing to
        prevent excessive re-rendering during rapid theme switches.

        Args:
            palette (dict[str, str]): The current color map from ThemeManager.
        """
        # debounce rapid theme changes
        if self._refresh_timer:
            self._refresh_timer.stop()

        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_theme_refresh)
        self._refresh_timer.start(50)  # 50ms debounce

    def _do_theme_refresh(self):
        """Perform the actual theme refresh after debouncing."""
        if self._refresh_callback:
            self._refresh_callback()
        else:
            self._render_icon()

    def setSize(self, width: int, height: int):
        """Override to ensure theme refreshes are respected when size changes."""
        super().setSize(width, height)
        # trigger immediate update via callback
        if self._refresh_callback:
            self._refresh_callback()

    def setColor(self, color: str):
        """Override to update icon immediately with new theme role or static color."""
        super().setColor(color)
        # trigger immediate update via callback
        if self._refresh_callback:
            self._refresh_callback()

    def clearColor(self):
        """Clear any override and fallback to default color role."""
        super().clearColor()
        # trigger immediate update via callback
        if self._refresh_callback:
            self._refresh_callback()

    def _get_color(self) -> str:
        """Override to handle palette roles from theme."""
        if self._custom_color:
            if self._custom_color.startswith("#"):
                return self._custom_color
            else:
                # it's a palette role
                palette = IconLoader.get_palette()
                return palette.get(self._custom_color, FALLBACK_COLOR)
        else:
            # use default theme color
            palette = IconLoader.get_palette()
            return palette.get("on_surface", FALLBACK_COLOR)

    def as_qicon(self, state: State = State.DEFAULT) -> QIcon:
        """Render the icon as a QIcon for legacy widget compatibility.

        Args:
            state (State): Icon state to use when generating the QIcon.

        Returns:
            QIcon: The themed icon for the requested state.
        """
        color = self._get_color()
        size = self._get_size()

        return SVGLoader.load(
            file_path=self._icon_spec.name.path,
            color=color,
            size=size,
            as_icon=True
        )


# ── Icon ─────────────────────────────────────────────────────────────────────────────────────
class Icon(QLabel):
    """Standalone visual widget for themed SVG icons.

    QLabel-based icon widget that reflects theme changes and displays
    static or dynamic SVG content. Used in views, dashboards, cards, headers, etc.
    """

    def __init__(self, icon_enum: Name, parent=None):
        """Initialize icon widget.

        Args:
            icon_enum (Name): The icon to render.
            parent (QWidget): Optional parent widget.
        """
        super().__init__(parent)

        # initialize ThemedIcon functionality via composition
        self._themed_icon = ThemedIcon(icon_enum)

        # set callback so ThemedIcon can update this widget when theme changes
        self._themed_icon.set_refresh_callback(self._render_icon)

        # set up the widget
        self.setFixedSize(self._themed_icon._icon_spec.size.value)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(self._themed_icon._icon_spec.name.value)

        # initial render
        self._render_icon()

    def _render_icon(self):
        """Render the icon with current settings."""
        size = self._themed_icon._get_size()
        color = self._themed_icon._get_color()

        try:
            # load and set the pixmap
            pixmap = SVGLoader.load(
                file_path=self._themed_icon._icon_spec.name.path,
                color=color,
                size=size,
                as_icon=False
            )
            self.setPixmap(pixmap)
        except Exception as e:
            DebugLogger.log(f"Failed to render icon {self._themed_icon._icon_enum.name}: {e}", "warning")

    def setSize(self, width: int, height: int):
        """Set custom icon size."""
        self._themed_icon.setSize(width, height)
        self.setFixedSize(self._themed_icon._current_size)

    def setColor(self, color: str):
        """Set custom icon color."""
        self._themed_icon.setColor(color)

    def clearColor(self):
        """Clear custom color override."""
        self._themed_icon.clearColor()

    def objectName(self) -> str:
        """Return object name for IconLoader protocol."""
        return super().objectName()


# ── StateIcon ───────────────────────────────────────────────────────────────────────────────
class StateIcon(QWidget):
    """Button-bound icon with hover, checked, disabled states.

    Automatically updates appearance based on current state.
    Syncs with parent button via autoDetectState() calls.
    """

    def __init__(self, icon_enum: Name, type: Type = Type.DEFAULT):
        """Initialize state icon.

        Args:
            icon_enum (Name): Icon to display.
            type (Type): Button type to determine default state colors.
        """
        super().__init__()

        # initialize ThemedIcon functionality via composition
        self._themed_icon = ThemedIcon(icon_enum)

        # set callback so ThemedIcon can update this widget when theme changes
        self._themed_icon.set_refresh_callback(self._on_theme_refresh)

        self._type = type
        self._current_state = State.DEFAULT

        # separate custom colors from state overrides (fixes edge case)
        self._global_custom_color = None  # global custom color (like Icon class)
        self._state_overrides = {}  # per-state color overrides

        # set up widget
        self.setFixedSize(self._themed_icon._icon_spec.size.value)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # cache for rendered pixmaps by state
        self._state_pixmaps = {}

        # internal label for displaying pixmaps
        self._label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self._label.setAlignment(Qt.AlignCenter)

        # initial render
        self._render_needed_states()
        self._update_display()

    def setType(self, type: Type):
        """Set the visual type used for mapping state→colorRole.

        Args:
            type (Type): Predefined visual role type.
        """
        self._type = type
        self._render_needed_states()
        self._update_display()

    def setGlobalColor(self, color: str):
        """Set a global custom color for ALL states (like Icon class).

        This overrides the type-based colors but is separate from state overrides.

        Args:
            color (str): Hex color or theme role to use for all states.
        """
        self._global_custom_color = color
        self._render_needed_states()
        self._update_display()

    def clearGlobalColor(self):
        """Clear the global custom color, reverting to type-based defaults."""
        self._global_custom_color = None
        self._render_needed_states()
        self._update_display()

    def setStateColor(self, state: State, color_role: str):
        """Override the color role for a specific state.

        Args:
            state (State): Which state to override.
            color_role (str): Theme palette role string.
        """
        self._state_overrides[state] = color_role
        self._render_state(state)
        if self._current_state == state:
            self._update_display()

    def clearStateOverride(self, state: State):
        """Clear a specific state's override, restoring type default or global color.

        Args:
            state (State): Which state to clear.
        """
        if state in self._state_overrides:
            del self._state_overrides[state]
            self._render_state(state)
            if self._current_state == state:
                self._update_display()

    def clearAllStateOverrides(self):
        """Clear all state-specific overrides but PRESERVE global custom color."""
        self._state_overrides.clear()
        self._render_needed_states()
        self._update_display()

    def clearAll(self):
        """Clear EVERYTHING - both state overrides AND global custom color."""
        self._global_custom_color = None
        self._state_overrides.clear()
        self._render_needed_states()
        self._update_display()

    # legacy API compatibility - delegates to new methods
    def setStateDefault(self, color_role: str):
        """Legacy: Override the color role for default state."""
        self.setStateColor(State.DEFAULT, color_role)

    def setStateHover(self, color_role: str):
        """Legacy: Override the color role for hover state."""
        self.setStateColor(State.HOVER, color_role)

    def setStateChecked(self, color_role: str):
        """Legacy: Override the color role for checked state."""
        self.setStateColor(State.CHECKED, color_role)

    def setStateDisabled(self, color_role: str):
        """Legacy: Override the color role for disabled state."""
        self.setStateColor(State.DISABLED, color_role)

    def setColor(self, color: str):
        """Legacy: Set global custom color (for backwards compatibility)."""
        self.setGlobalColor(color)

    def clearColor(self):
        """Legacy: Clear global custom color (for backwards compatibility)."""
        self.clearGlobalColor()

    def updateState(self, state: State):
        """Force the icon to switch to a specific state.

        Args:
            state (State): State to switch to (e.g. HOVER).
        """
        if state != self._current_state:
            self._current_state = state
            # ensure the new state is rendered if needed
            if state not in self._state_pixmaps:
                self._render_state(state)
            self._update_display()

    def autoDetectState(self, checked: bool, hovered: bool, enabled: bool):
        """Set icon state automatically based on standard button logic.

        Called by parent BaseButton during state changes.

        Args:
            checked (bool): Whether button is checked.
            hovered (bool): Whether mouse is hovering.
            enabled (bool): Whether widget is enabled.
        """
        if not enabled:
            new_state = State.DISABLED
        elif checked:
            new_state = State.CHECKED
        elif hovered:
            new_state = State.HOVER
        else:
            new_state = State.DEFAULT

        if new_state != self._current_state:
            self._current_state = new_state
            # ensure the new state is rendered if needed
            if new_state not in self._state_pixmaps:
                self._render_state(new_state)
            self._update_display()

    def _resolve_color_for_state(self, state: State) -> str:
        """Resolve the color for a given state with proper precedence.

        Priority order:
        1. State-specific override
        2. Global custom color
        3. Type-based default
        """
        palette = IconLoader.get_palette()

        if state in self._state_overrides:
            # state-specific override takes highest priority
            palette_role = self._state_overrides[state]
            return palette.get(palette_role, FALLBACK_COLOR)

        elif self._global_custom_color:
            # global custom color applies to all states (unless overridden)
            if self._global_custom_color.startswith("#"):
                return self._global_custom_color
            else:
                return palette.get(self._global_custom_color, FALLBACK_COLOR)

        else:
            # fall back to Type defaults
            state_colors = self._type.state_map
            palette_role = state_colors.get(state, "on_surface")
            return palette.get(palette_role, FALLBACK_COLOR)

    def _render_state(self, state: State):
        """Render a specific state and cache the result."""
        color = self._resolve_color_for_state(state)
        size = self._themed_icon._get_size()

        try:
            pixmap = SVGLoader.load(
                file_path=self._themed_icon._icon_spec.name.path,
                color=color,
                size=size,
                as_icon=False
            )
            self._state_pixmaps[state] = pixmap
        except Exception as e:
            DebugLogger.log(f"Failed to render state {state.name} for icon {self._themed_icon._icon_enum.name}: {e}", "warning")

    def _render_needed_states(self):
        """Render only the states that might actually be used (performance optimization)."""
        # always render these base states
        base_states = [State.DEFAULT, State.HOVER, State.DISABLED]

        # only render CHECKED if parent is checkable (if we have a parent)
        if hasattr(self, 'parent') and self.parent():
            parent = self.parent()
            if hasattr(parent, 'isCheckable') and parent.isCheckable():
                base_states.append(State.CHECKED)
        else:
            # if no parent context, render CHECKED just in case
            base_states.append(State.CHECKED)

        # clear cache and render needed states
        self._state_pixmaps.clear()
        for state in base_states:
            self._render_state(state)

    def _update_display(self):
        """Update the displayed pixmap based on current state."""
        pixmap = None

        if self._current_state in self._state_pixmaps:
            pixmap = self._state_pixmaps[self._current_state]
        elif State.DEFAULT in self._state_pixmaps:
            # fallback to DEFAULT if current state isn't rendered
            pixmap = self._state_pixmaps[State.DEFAULT]
            DebugLogger.log(f"StateIcon falling back to DEFAULT state for {self._current_state.name}", "debug")
        else:
            # last resort - render on demand
            DebugLogger.log(f"StateIcon rendering {self._current_state.name} on demand", "debug")
            self._render_state(self._current_state)
            pixmap = self._state_pixmaps.get(self._current_state)

        if pixmap:
            self._label.setPixmap(pixmap)

    def _on_theme_refresh(self):
        """Called when theme changes - clear cache and re-render states."""
        # clear old pixmaps to free memory
        self._state_pixmaps.clear()

        # re-render needed states and update display
        self._render_needed_states()
        self._update_display()

    def sizeHint(self) -> QSize:
        """Return the preferred size for this StateIcon widget."""
        return self._themed_icon._current_size

    def setSize(self, width: int, height: int):
        """Override to update widget size and re-render."""
        self._themed_icon.setSize(width, height)
        self.setFixedSize(self._themed_icon._current_size)
        # theme icon size change will trigger callback, but let's be explicit
        self._render_needed_states()
        self._update_display()

    def objectName(self) -> str:
        """Return object name for IconLoader protocol."""
        return super().objectName()
