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
from app.style.icon.config import Name, State, Type
from app.style.icon.loader import IconLoader
from app.style.icon.svg_loader import SVGLoader

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
            width (int): Width in pixels (1-512).
            height (int): Height in pixels (1-512).

        Raises:
            TypeError: If width or height are not integers.
            ValueError: If width or height are outside valid range.
        """
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Size parameters must be integers, got width={type(width)}, height={type(height)}")

        # Validate and clamp size bounds with warnings
        original_width, original_height = width, height
        width = max(1, min(width, 512))  # reasonable limits
        height = max(1, min(height, 512))

        if width != original_width or height != original_height:
            DebugLogger.log(f"Size clamped from ({original_width}, {original_height}) to ({width}, {height})", "warning")

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

        # debounce timer for theme updates (reused to prevent memory accumulation)
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_theme_refresh)

        # register for theme updates
        IconLoader.register(self)

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            # Stop and cleanup timer first
            if hasattr(self, '_refresh_timer') and self._refresh_timer:
                self._refresh_timer.stop()
                self._refresh_timer.deleteLater()

            # Unregister from IconLoader
            IconLoader.unregister(self)
        except (AttributeError, RuntimeError, TypeError) as e:
            # IconLoader might already be destroyed during application shutdown
            # or object might be in an invalid state
            DebugLogger.log(f"ThemedIcon cleanup warning: {e}", "debug")
        except Exception as e:
            # Log any unexpected exceptions for debugging
            DebugLogger.log(f"Unexpected error during ThemedIcon cleanup: {e}", "warning")

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
        # debounce rapid theme changes using reused timer
        if self._refresh_timer.isActive():
            self._refresh_timer.stop()

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


# ── AppIcon ─────────────────────────────────────────────────────────────────────────────────────
class AppIcon(QLabel):
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

        # Make StateIcon transparent to mouse events so parent button can detect hover properly
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        DebugLogger.log(f"StateIcon init - WA_TransparentForMouseEvents set to {self.testAttribute(Qt.WA_TransparentForMouseEvents)}", "debug")

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

        # track which states have been accessed for lazy loading
        self._accessed_states = {State.DEFAULT}  # Always need default state

        # performance tracking for optimization
        self._render_count = 0

        # internal label for displaying pixmaps
        self._label = QLabel(self)
        # Ensure the internal label is also transparent to mouse events
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        DebugLogger.log(f"StateIcon._label - WA_TransparentForMouseEvents set to {self._label.testAttribute(Qt.WA_TransparentForMouseEvents)}", "debug")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self._label.setAlignment(Qt.AlignCenter)

        # lazy render - only render DEFAULT state initially
        self._render_state(State.DEFAULT)
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

        Raises:
            TypeError: If color is not a string.
            ValueError: If color is empty.
        """
        # Validate color parameter
        if not isinstance(color, str):
            raise TypeError(f"Color must be a string, got {type(color)}")

        if not color.strip():
            raise ValueError("Color cannot be empty")

        # Check if color role exists in palette (warning only)
        if not color.startswith("#"):
            palette = IconLoader.get_palette()
            if palette and color not in palette:
                DebugLogger.log(f"Color role '{color}' not found in current palette", "warning")

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

        Raises:
            TypeError: If state is not a State enum.
            ValueError: If color_role is empty or invalid.
        """
        # Validate state parameter
        if not isinstance(state, State):
            raise TypeError(f"State must be a State enum, got {type(state)}")

        # Validate color_role parameter
        if not isinstance(color_role, str):
            raise TypeError(f"Color role must be a string, got {type(color_role)}")

        if not color_role.strip():
            raise ValueError("Color role cannot be empty")

        # Check if color role exists in palette (warning only)
        palette = IconLoader.get_palette()
        if palette and color_role not in palette and not color_role.startswith("#"):
            DebugLogger.log(f"Color role '{color_role}' not found in current palette", "warning")

        self._state_overrides[state] = color_role
        self._render_state(state)
        if self._current_state == state:
            self._update_display()

    def clearStateOverride(self, state: State):
        """Clear a specific state's override, restoring type default or global color.

        Args:
            state (State): Which state to clear.

        Raises:
            TypeError: If state is not a State enum.
        """
        # Validate state parameter
        if not isinstance(state, State):
            raise TypeError(f"State must be a State enum, got {type(state)}")

        if state in self._state_overrides:
            del self._state_overrides[state]
            self._render_state(state)
            if self._current_state == state:
                self._update_display()
        else:
            DebugLogger.log(f"No override found for state {state.name}, ignoring clear request", "debug")

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


    def updateState(self, state: State):
        """Force the icon to switch to a specific state.

        Args:
            state (State): State to switch to (e.g. HOVER).

        Raises:
            TypeError: If state is not a State enum.
        """
        # Validate state parameter
        if not isinstance(state, State):
            raise TypeError(f"State must be a State enum, got {type(state)}")

        if state != self._current_state:
            DebugLogger.log(f"StateIcon updateState - changing from {self._current_state.name} to {state.name}", "debug")
            self._current_state = state
            # Track that this state has been accessed
            self._accessed_states.add(state)
            # ensure the new state is rendered if needed
            if state not in self._state_pixmaps:
                self._render_state(state)
            self._update_display()
        else:
            DebugLogger.log(f"StateIcon updateState - no change, staying in {state.name}", "debug")

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

        DebugLogger.log(f"StateIcon autoDetectState - checked={checked}, hovered={hovered}, enabled={enabled} -> {new_state.name}", "debug")

        if new_state != self._current_state:
            DebugLogger.log(f"StateIcon autoDetectState - changing from {self._current_state.name} to {new_state.name}", "debug")
            self._current_state = new_state
            # Track that this state has been accessed
            self._accessed_states.add(new_state)
            # ensure the new state is rendered if needed
            if new_state not in self._state_pixmaps:
                self._render_state(new_state)
            self._update_display()
        else:
            DebugLogger.log(f"StateIcon autoDetectState - no change, staying in {new_state.name}", "debug")

    def _resolve_color_for_state(self, state: State) -> str:
        """Resolve the color for a given state with proper precedence.

        Priority order (highest to lowest):
        1. State-specific override (via setStateColor)
        2. Global custom color (via setGlobalColor)
        3. Type-based default (from Type.state_map)
        4. Fallback color (safety net)

        Args:
            state (State): The state to resolve color for

        Returns:
            str: Resolved hex color string
        """
        # Validate inputs
        if not isinstance(state, State):
            DebugLogger.log(f"Invalid state type: {type(state)}, using DEFAULT", "warning")
            state = State.DEFAULT

        palette = IconLoader.get_palette()
        if not palette:
            DebugLogger.log("No palette available, using fallback color", "warning")
            return FALLBACK_COLOR

        resolved_color = None
        resolution_source = "unknown"

        # Priority 1: State-specific override
        if state in self._state_overrides:
            palette_role = self._state_overrides[state]
            resolved_color = palette.get(palette_role, FALLBACK_COLOR)
            resolution_source = f"state override ({palette_role})"

        # Priority 2: Global custom color
        elif self._global_custom_color:
            if self._global_custom_color.startswith("#"):
                resolved_color = self._global_custom_color
                resolution_source = "global hex color"
            else:
                resolved_color = palette.get(self._global_custom_color, FALLBACK_COLOR)
                resolution_source = f"global palette role ({self._global_custom_color})"

        # Priority 3: Type-based default
        else:
            state_colors = self._type.state_map
            palette_role = state_colors.get(state, "on_surface")
            resolved_color = palette.get(palette_role, FALLBACK_COLOR)
            resolution_source = f"type default ({palette_role})"

        # Final validation
        if not resolved_color or not resolved_color.startswith("#"):
            DebugLogger.log(f"Color resolution failed for {state.name}, using fallback. Source was: {resolution_source}", "warning")
            resolved_color = FALLBACK_COLOR

        # Debug logging for color resolution (only in debug mode)
        DebugLogger.log(f"StateIcon color resolved: {state.name} -> {resolved_color} (from {resolution_source})", "debug")

        return resolved_color

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
            self._render_count += 1

            # Debug logging for lazy loading
            from dev_tools import DebugLogger
            DebugLogger.log(f"StateIcon rendered {state.name} (total renders: {self._render_count})", "debug")

        except Exception as e:
            from dev_tools import DebugLogger
            DebugLogger.log(f"Failed to render state {state.name} for icon {self._themed_icon._icon_enum.name}: {e}", "warning")

    def _render_needed_states(self):
        """Render only the states that have been accessed (lazy loading optimization)."""
        # Clear cache and render only accessed states
        self._state_pixmaps.clear()

        # Render all states that have been accessed so far
        for state in self._accessed_states:
            self._render_state(state)

        # Debug logging for lazy loading performance
        from dev_tools import DebugLogger
        DebugLogger.log(f"StateIcon lazy render: rendered {len(self._accessed_states)} states out of {len(State)}", "debug")

    def _update_display(self):
        """Update the displayed pixmap based on current state."""
        pixmap = None

        if self._current_state in self._state_pixmaps:
            pixmap = self._state_pixmaps[self._current_state]
            DebugLogger.log(f"StateIcon _update_display - using cached pixmap for {self._current_state.name}", "debug")
        elif State.DEFAULT in self._state_pixmaps:
            # fallback to DEFAULT if current state isn't rendered
            pixmap = self._state_pixmaps[State.DEFAULT]
            DebugLogger.log(f"StateIcon _update_display - falling back to DEFAULT for {self._current_state.name}", "debug")
        else:
            # last resort - render on demand
            DebugLogger.log(f"StateIcon _update_display - rendering {self._current_state.name} on demand", "debug")
            self._render_state(self._current_state)
            pixmap = self._state_pixmaps.get(self._current_state)

        if pixmap:
            self._label.setPixmap(pixmap)
            DebugLogger.log(f"StateIcon _update_display - pixmap set successfully for {self._current_state.name}", "debug")
        else:
            DebugLogger.log(f"StateIcon _update_display - NO PIXMAP FOUND for {self._current_state.name}", "debug")

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

    def get_performance_stats(self) -> dict:
        """Get performance statistics for lazy loading optimization.

        Returns:
            dict: Performance metrics including render count and accessed states
        """
        return {
            'total_renders': self._render_count,
            'accessed_states': len(self._accessed_states),
            'total_states': len(State),
            'efficiency_ratio': len(self._accessed_states) / len(State),
            'cached_pixmaps': len(self._state_pixmaps)
        }

    def objectName(self) -> str:
        """Return object name for IconLoader protocol."""
        return super().objectName()
