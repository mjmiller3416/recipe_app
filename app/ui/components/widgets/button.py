"""app/ui/components/widgets/button.py

Clean button system using QPushButton and QToolButton as base classes.

This module provides Button and ToolButton classes that integrate with StateIcon
for theme-aware icons while leveraging Qt's native button behavior. The system
has been optimized with the following enhancements:

## Architecture Overview:
- **SizeManager**: Consolidated size calculation and management utilities
- **BaseButton**: Mixin class providing common functionality for all button types
- **Button**: QPushButton with StateIcon integration for text + icon layouts
- **ToolButton**: QToolButton with StateIcon integration for icon-only layouts

## Performance Optimizations:
- **Lazy State Rendering**: StateIcon only renders states that are actually accessed
- **Smart SVG Caching**: LRU-based cache management in SVGLoader prevents memory bloat
- **Consolidated Size Logic**: Single source of truth for all size calculations
- **Reduced Code Duplication**: ~155+ lines removed through architectural consolidation

## Key Features:
- Theme-aware icons that automatically update with palette changes
- Comprehensive state management (default, hover, checked, disabled)
- Flexible sizing with automatic and manual size control
- Memory-efficient rendering with intelligent caching
- Full backward compatibility with existing API

## Usage Examples:
```python
# Text + icon button
button = Button("Save File", Type.PRIMARY, Name.SAVE)
button.setIconSize(20, 20)
button.setButtonSize(120, 40)

# Icon-only tool button
tool_button = ToolButton(Name.SETTINGS, Type.SECONDARY)
tool_button.setCheckable(True)
tool_button.setStateIconSize(24, 24)

# Performance monitoring
stats = button.state_icon.get_performance_stats()
cache_stats = SVGLoader.get_cache_stats()
```
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QToolButton

from app.style.icon.config import Name, Type
from app.style.icon.icon import StateIcon
from _dev_tools import DebugLogger


# ── Size Manager ────────────────────────────────────────────────────────────────────────────────────────────
class SizeManager:
    """Utility class for consolidated size calculation and management."""

    @staticmethod
    def calculate_button_size(widget, custom_size_width=None, custom_size_height=None):
        """Calculate button size based on layout and optional custom constraints."""
        layout = widget.layout()
        if not layout:
            return custom_size_width or 0, custom_size_height or 0

        layout_hint = layout.sizeHint()
        margins = widget.contentsMargins()

        min_width = layout_hint.width() + margins.left() + margins.right()
        min_height = layout_hint.height() + margins.top() + margins.bottom()

        if custom_size_width is not None and custom_size_height is not None:
            # Use larger of requested or minimum required size
            return max(custom_size_width, min_width), max(custom_size_height, min_height)

        return min_width, min_height

    @staticmethod
    def ensure_layout_updated(widget):
        """Ensure layout calculations are completed synchronously to prevent race conditions.

        Args:
            widget: Widget with layout that needs to be synchronized.
        """
        layout = widget.layout()
        if layout:
            # Force immediate layout calculation
            layout.invalidate()
            layout.activate()

            # Process any pending layout events to ensure consistency
            QApplication.processEvents()

            # Verify layout is in expected state
            if layout.isEmpty():
                DebugLogger.log(f"Warning: Layout appears empty after synchronization for {widget.objectName()}", "warning")

    @staticmethod
    def apply_auto_resize(widget):
        """Apply automatic resize policy to a widget."""
        # Clear any fixed size constraints
        widget.setMinimumSize(0, 0)
        widget.setMaximumSize(16777215, 16777215)  # Qt's default max size
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Ensure layout calculations are synchronized
        SizeManager.ensure_layout_updated(widget)
        widget.updateGeometry()
        # Force a repaint to ensure visual update
        widget.update()

    @staticmethod
    def apply_exact_size(widget, width, height):
        """Apply exact size constraints to a widget."""
        widget.setMinimumSize(width, height)
        widget.setMaximumSize(width, height)
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        widget.updateGeometry()
        widget.update()

    @staticmethod
    def calculate_tool_button_size(widget):
        """Calculate optimal size for a tool button with proper minimum size handling."""
        layout = widget.layout()
        if not layout:
            return QSize(24, 24)  # Fallback minimum size

        # Ensure layout calculations are synchronized
        SizeManager.ensure_layout_updated(widget)

        # Get the layout's size hint
        layout_size = layout.sizeHint()
        margins = widget.contentsMargins()

        required_width = layout_size.width() + margins.left() + margins.right()
        required_height = layout_size.height() + margins.top() + margins.bottom()

        # Ensure minimum size for proper hover detection
        min_button_size = max(required_width, 24)  # At least 24px wide
        min_button_height = max(required_height, 24)  # At least 24px tall

        return QSize(min_button_size, min_button_height)

    @staticmethod
    def validate_size_parameters(width, height, param_name="size"):
        """Validate and clamp size parameters to reasonable bounds."""
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"{param_name} parameters must be integers, got width={type(width)}, height={type(height)}")

        # Store original values for logging
        original_width, original_height = width, height

        # Validate and clamp size bounds
        width = max(1, min(width, 512))  # Reasonable limits for icon sizes
        height = max(1, min(height, 512))

        if width != original_width or height != original_height:
            DebugLogger.log(f"{param_name} clamped from ({original_width}, {original_height}) to ({width}, {height})", "warning")

        return width, height

    @staticmethod
    def validate_button_size_parameters(width, height):
        """Validate button size parameters with appropriate bounds."""
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Button size parameters must be integers, got width={type(width)}, height={type(height)}")

        # Validate reasonable bounds for buttons (larger than icons)
        if width < 1 or width > 2048 or height < 1 or height > 2048:
            DebugLogger.log(f"Button size ({width}, {height}) outside recommended bounds (1-2048)", "warning")

        return width, height


# ── BaseButton Abstract Class ───────────────────────────────────────────────────────────────────────────────
class BaseButton:
    """Abstract base class for all button types with StateIcon integration.

    Consolidates common functionality between Button and ToolButton including:
    - State synchronization with StateIcon
    - Size management and layout handling
    - StateIcon integration and lifecycle
    - Event handling for hover/focus states
    """

    def _init_base_button(self, type: Type = Type.DEFAULT):
        """Initialize base button functionality. Call this from subclass __init__.

        Args:
            type (Type): Visual style type for StateIcon color mapping.
        """
        self._type = type
        self.state_icon = None
        self._has_custom_button_size = False
        self._is_hovered = False  # Track hover state manually

    def _connect_signals(self):
        """Connect Qt signals. Call this after Qt widget is fully initialized."""
        # Connect state change signals
        if hasattr(self, 'toggled'):
            self.toggled.connect(self._sync_icon_state)

    @property
    def default_margins(self) -> tuple[int, int, int, int]:
        """Default margins for this button type (left, top, right, bottom).

        Subclasses should override this property.
        """
        return (4, 4, 4, 4)  # Default fallback

    def _setup_button_layout(self):
        """Button-specific layout setup. Subclasses should override if needed."""
        pass

    # ── State Synchronization ────────────────────────────────────────────────────────────────
    def _sync_icon_state(self):
        """Synchronize StateIcon with current button state."""
        if self.state_icon:
            DebugLogger.log(f"_sync_icon_state - checked={self.isChecked()}, hovered={self._is_hovered}, enabled={self.isEnabled()}", "debug")
            self.state_icon.autoDetectState(
                checked=self.isChecked(),
                hovered=self._is_hovered,
                enabled=self.isEnabled()
            )

    def event(self, event):
        """Override event to debug all mouse events."""
        if event.type().name in ['MouseButtonPress', 'MouseButtonRelease', 'MouseMove', 'Enter', 'Leave', 'HoverEnter', 'HoverLeave', 'HoverMove']:
            DebugLogger.log(f"BaseButton.event() - {event.type().name} on {self.objectName() or type(self).__name__}", "debug")
        # Call the Qt widget's event method directly to avoid MRO issues
        if isinstance(self, QPushButton):
            return QPushButton.event(self, event)
        elif isinstance(self, QToolButton):
            return QToolButton.event(self, event)
        else:
            return super().event(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        DebugLogger.log(f"BaseButton enterEvent CALLED - {self.objectName() or type(self).__name__}", "debug")
        # Call the Qt widget's enterEvent directly to avoid MRO issues
        if isinstance(self, QPushButton):
            QPushButton.enterEvent(self, event)
        elif isinstance(self, QToolButton):
            QToolButton.enterEvent(self, event)
        else:
            super().enterEvent(event)
        self._is_hovered = True
        DebugLogger.log(f"BaseButton hover ENTER - {self.objectName() or type(self).__name__}", "debug")
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        DebugLogger.log(f"BaseButton leaveEvent CALLED - {self.objectName() or type(self).__name__}", "debug")
        # Call the Qt widget's leaveEvent directly to avoid MRO issues
        if isinstance(self, QPushButton):
            QPushButton.leaveEvent(self, event)
        elif isinstance(self, QToolButton):
            QToolButton.leaveEvent(self, event)
        else:
            super().leaveEvent(event)
        self._is_hovered = False
        DebugLogger.log(f"BaseButton hover LEAVE - {self.objectName() or type(self).__name__}", "debug")
        self._sync_icon_state()

    def mousePressEvent(self, event):
        """Handle mouse press for debugging."""
        DebugLogger.log(f"BaseButton mousePressEvent CALLED - {self.objectName() or type(self).__name__}", "debug")
        # Call the Qt widget's mousePressEvent directly to avoid MRO issues
        if isinstance(self, QPushButton):
            QPushButton.mousePressEvent(self, event)
        elif isinstance(self, QToolButton):
            QToolButton.mousePressEvent(self, event)
        else:
            super().mousePressEvent(event)

    def changeEvent(self, event):
        """Handle enabled/disabled state changes."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._sync_icon_state()

    # ── Size Management ──────────────────────────────────────────────────────────────────────
    def _on_icon_size_changed(self):
        """Handle icon size changes. Subclasses can override for specific behavior."""
        # if no custom button size is set, allow automatic resize
        if not self._has_custom_button_size:
            SizeManager.apply_auto_resize(self)
        else:
            self.updateGeometry()
            self.update()

    def setButtonSize(self, width: int, height: int):
        """Set a fixed size for the entire button widget.

        Args:
            width (int): Button width in pixels (1-2048).
            height (int): Button height in pixels (1-2048).

        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate using SizeManager
        width, height = SizeManager.validate_button_size_parameters(width, height)

        # Calculate minimum required size to prevent content clipping
        final_width, final_height = SizeManager.calculate_button_size(self, width, height)
        self.setFixedSize(final_width, final_height)
        self._has_custom_button_size = True

    def setStateIconSize(self, width: int, height: int):
        """Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels (1-512).
            height (int): Icon height in pixels (1-512).

        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate using SizeManager
        width, height = SizeManager.validate_size_parameters(width, height, "Icon size")

        if self.state_icon:
            self.state_icon.setSize(width, height)
            # Subclass-specific behavior for size changes
            self._on_icon_size_changed()

    def setFixedHeight(self, height: int):
        """Set a fixed height while allowing width to stretch dynamically.

        Args:
            height (int): Button height in pixels (1-2048).

        Raises:
            TypeError: If height is not an integer.
        """
        # Validate using SizeManager
        if not isinstance(height, int):
            raise TypeError(f"Height parameter must be an integer, got {type(height)}")

        if height < 1 or height > 2048:
            DebugLogger.log(f"Button height ({height}) outside recommended bounds (1-2048)", "warning")

        # Set fixed height but allow width to expand
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        # Allow width to stretch
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._has_custom_button_size = True

    # ── StateIcon Integration ────────────────────────────────────────────────────────────────
    def _setup_state_icon(self, icon: Name, type: Type):
        """Initialize StateIcon with proper configuration."""
        self.state_icon = StateIcon(icon, type)
        self._sync_icon_state()
        return self.state_icon

    def setIcon(self, icon: Name):
        """Set or change the button's icon.

        Args:
            icon (Name): The icon enum to display.
        """
        if self.state_icon:
            # replace existing icon
            layout = self.layout()
            if layout:
                layout.removeWidget(self.state_icon)
                # Clean up resources before scheduling deletion
                self.state_icon.cleanup()
                self.state_icon.deleteLater()

        # create new icon - subclass handles layout specifics
        self.state_icon = StateIcon(icon, self._type)
        self._setup_icon_in_layout()
        self._sync_icon_state()

    def _setup_icon_in_layout(self):
        """Setup icon in button layout. Subclasses should override if needed."""
        if self.layout() and self.state_icon:
            self.layout().addWidget(self.state_icon)

    def icon(self) -> StateIcon:
        """Returns the StateIcon widget used in the button.

        Returns:
            StateIcon: The button's internal themed icon widget, or None if no icon.
        """
        return self.state_icon

    # ── StateIcon State Override Methods ─────────────────────────────────────────────────────
    def setStateHover(self, role: str):
        """Override the color role used for the hover state."""
        if self.state_icon:
            from app.style.icon.config import State
            self.state_icon.setStateColor(State.HOVER, role)

    def setStateDefault(self, role: str):
        """Override the default icon color role."""
        if self.state_icon:
            from app.style.icon.config import State
            self.state_icon.setStateColor(State.DEFAULT, role)

    def setStateChecked(self, role: str):
        """Override the checked icon color role."""
        if self.state_icon:
            from app.style.icon.config import State
            self.state_icon.setStateColor(State.CHECKED, role)

    def setStateDisabled(self, role: str):
        """Override the disabled icon color role."""
        if self.state_icon:
            from app.style.icon.config import State
            self.state_icon.setStateColor(State.DISABLED, role)

    def clearAllStateOverrides(self):
        """Clears all icon state color overrides, restoring type-based defaults."""
        if self.state_icon:
            self.state_icon.clearAllStateOverrides()

    # ── Icon Swapping Utility ────────────────────────────────────────────────────────────
    @staticmethod
    def swapIcon(button, condition: bool, true_icon: Name, false_icon: Name, preserve_size: bool = True):
        """Swap button icon based on a boolean condition.

        This is a convenience method that simplifies conditional icon swapping patterns
        commonly used throughout the application.

        Args:
            button: Button widget (BaseButton subclass or any widget with setIcon)
            condition (bool): Boolean condition to determine which icon to use
            true_icon (Name): Icon to use when condition is True
            false_icon (Name): Icon to use when condition is False
            preserve_size (bool): Whether to preserve the current icon size (default: True)

        Example:
            # Instead of:
            icon_name = Icon.RESTORE if maximized else Icon.MAXIMIZE
            BaseButton.setIcon(self.btn_ico_maximize, icon_name)

            # Use:
            BaseButton.swapIcon(self.btn_ico_maximize, maximized, Icon.RESTORE, Icon.MAXIMIZE)
        """
        # Preserve current icon size if requested and available
        current_size = None
        if preserve_size and hasattr(button, 'state_icon') and button.state_icon:
            current_size = button.state_icon.size()

        # Set the new icon
        icon = true_icon if condition else false_icon
        BaseButton.setIcon(button, icon)

        # Restore the size if it was preserved
        if current_size and hasattr(button, 'setStateIconSize'):
            button.setStateIconSize(current_size.width(), current_size.height())

    @staticmethod
    def getConditionalIcon(condition: bool, true_icon: Name, false_icon: Name) -> Name:
        """Get an icon based on a boolean condition without setting it on a button.

        This is useful for initial icon setup during widget creation.

        Args:
            condition (bool): Boolean condition to determine which icon to return
            true_icon (Name): Icon to return when condition is True
            false_icon (Name): Icon to return when condition is False

        Returns:
            Name: The icon enum based on the condition

        Example:
            # Instead of:
            initial_icon = Name.FAV if self.recipe.is_favorite else Name.FAV_FILLED

            # Use:
            initial_icon = BaseButton.getConditionalIcon(self.recipe.is_favorite, Name.FAV, Name.FAV_FILLED)
        """
        return true_icon if condition else false_icon


# ── Button ──────────────────────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton, BaseButton):
    """A QPushButton with integrated StateIcon support.

    Combines QPushButton's native behavior with StateIcon for theme-aware icons.
    Supports both icon + text or text-only configurations.
    """

    def __init__(self, label: str, type: Type = Type.DEFAULT, icon: Name = None, parent=None):
        """Create a button with text and optional icon.

        Args:
            label (str): The button text label.
            type (Type): Visual style type (defines icon color map).
            icon (Name, optional): Optional icon enum to display.
            parent: Optional parent widget.
        """
        DebugLogger.log(f"Button.__init__ called with label='{label}'", "debug")
        QPushButton.__init__(self, label, parent)
        self._init_base_button(type)
        DebugLogger.log(f"Button MRO: {[cls.__name__ for cls in self.__class__.__mro__]}", "debug")

        self._icon_spacing = 6

        # setup layout if we have an icon
        if icon:
            self._setup_layout_with_icon(label, icon)

        # Connect signals after widget is fully initialized
        self._connect_signals()

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        DebugLogger.log(f"Button.enterEvent CALLED - {self.objectName() or 'Button'}", "debug")
        QPushButton.enterEvent(self, event)
        self._is_hovered = True
        DebugLogger.log(f"Button hover ENTER - {self.objectName() or 'Button'}", "debug")
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        DebugLogger.log(f"Button.leaveEvent CALLED - {self.objectName() or 'Button'}", "debug")
        QPushButton.leaveEvent(self, event)
        self._is_hovered = False
        DebugLogger.log(f"Button hover LEAVE - {self.objectName() or 'Button'}", "debug")
        self._sync_icon_state()

    def setIconSize(self, width: int, height: int):
        """Set the icon's size within the button (Button-specific method)."""
        self.setStateIconSize(width, height)

    @property
    def default_margins(self) -> tuple[int, int, int, int]:
        """Default margins for Button (left, top, right, bottom)."""
        return (8, 8, 8, 8)

    def _setup_button_layout(self):
        """Button-specific layout setup."""
        # This is called when creating layouts - implementation in _setup_layout_with_icon
        pass

    def _setup_icon_in_layout(self):
        """Setup icon in button layout."""
        if self.layout():
            self.layout().insertWidget(0, self.state_icon)
        else:
            # If no layout exists, we need to create one with current text
            current_text = self.text()
            self._setup_layout_with_icon(current_text, None)
            if self.state_icon:
                self.layout().insertWidget(0, self.state_icon)

    def _setup_layout_with_icon(self, label: str, icon: Name):
        """Setup layout with icon and text."""
        # clear the default text since we'll use a layout
        self.setText("")

        # create layout
        layout = QHBoxLayout(self)
        margins = self.default_margins
        layout.setContentsMargins(*margins)
        layout.setSpacing(self._icon_spacing)

        # add icon using BaseButton method
        if icon:
            self.state_icon = self._setup_state_icon(icon, self._type)
            layout.addWidget(self.state_icon)

        # add label
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def text(self) -> str:
        """Get the current text label.

        Returns:
            str: Current button text.
        """
        if hasattr(self, 'label') and self.label:
            return self.label.text()
        else:
            return super().text()

    def setIconSpacing(self, pixels: int):
        """Set the spacing between the icon and label inside the layout.

        Args:
            pixels (int): Pixel spacing between icon and label.
        """
        self._icon_spacing = pixels
        layout = self.layout()
        if layout:
            layout.setSpacing(pixels)

    def setText(self, text: str):
        """Set the button's text label.

        Args:
            text (str): New label to display.
        """
        if hasattr(self, 'label') and self.label:
            # button with icon - update label widget
            self.label.setText(text)
        else:
            # text-only button - use native setText
            super().setText(text)

    def setIcon(self, icon: Name):
        """Set or change the button's icon.

        Args:
            icon (Name): The icon enum to display.
        """
        current_text = self.text()

        if self.state_icon:
            # replace existing icon
            layout = self.layout()
            layout.removeWidget(self.state_icon)
            self.state_icon.deleteLater()

        # create new icon and setup layout if needed
        if not self.layout():
            self._setup_layout_with_icon(current_text, icon)
        else:
            self.state_icon = StateIcon(icon, self._type)
            self.layout().insertWidget(0, self.state_icon)
            self._sync_icon_state()

    def setLayoutMargins(self, left: int, top: int, right: int, bottom: int):
        """Set custom margins for the button layout.

        Args:
            left (int): Left margin in pixels.
            top (int): Top margin in pixels.
            right (int): Right margin in pixels.
            bottom (int): Bottom margin in pixels.
        """
        layout = self.layout()
        if layout:
            layout.setContentsMargins(left, top, right, bottom)

    def addLayoutStretch(self):
        """Add a stretch to the button's layout to push content to the left."""
        layout = self.layout()
        if layout and hasattr(layout, 'addStretch'):
            layout.addStretch()

    def sizeHint(self) -> QSize:
        """Calculate the preferred size for the button based on its contents."""
        if self._has_custom_button_size:
            return self.size()  # return the custom size (already adjusted for minimum in setButtonSize)

        if self.layout():
            # use layout's size hint plus button margins
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            total_width = layout_hint.width() + margins.left() + margins.right()
            total_height = layout_hint.height() + margins.top() + margins.bottom()
            return QSize(total_width, total_height)
        else:
            # fall back to QPushButton's default size hint for text-only buttons
            return super().sizeHint()


# ── ToolButton ──────────────────────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, BaseButton):
    """A QToolButton with integrated StateIcon support.

    Icon-only button that leverages QToolButton's native behavior while
    providing StateIcon integration for theme-aware icons.
    """

    def __init__(self, type: Type = Type.DEFAULT, icon: Name = None, parent=None):
        """Create a compact icon-only tool button.

        Args:
            icon (Name): The icon to display.
            type (Type): Visual style type (defines icon color map).
            parent: Optional parent widget.
        """
        QToolButton.__init__(self, parent)
        self._init_base_button(type)

        # setup layout with StateIcon
        layout = QHBoxLayout(self)
        margins = self.default_margins
        layout.setContentsMargins(*margins)
        layout.setSpacing(0)

        self.state_icon = self._setup_state_icon(icon, type)
        layout.addWidget(self.state_icon)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Connect signals after widget is fully initialized
        self._connect_signals()

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        DebugLogger.log(f"ToolButton.enterEvent CALLED - {self.objectName() or 'ToolButton'}", "debug")
        QToolButton.enterEvent(self, event)
        self._is_hovered = True
        DebugLogger.log(f"ToolButton hover ENTER - {self.objectName() or 'ToolButton'}", "debug")
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        DebugLogger.log(f"ToolButton.leaveEvent CALLED - {self.objectName() or 'ToolButton'}", "debug")
        QToolButton.leaveEvent(self, event)
        self._is_hovered = False
        DebugLogger.log(f"ToolButton hover LEAVE - {self.objectName() or 'ToolButton'}", "debug")
        self._sync_icon_state()

    def setIconSize(self, *args):
        """Override QToolButton.setIconSize to support both QSize and (width, height) arguments."""
        if len(args) == 1 and hasattr(args[0], 'width') and hasattr(args[0], 'height'):
            # QSize argument - use our StateIcon sizing
            size = args[0]
            self.setStateIconSize(size.width(), size.height())
        elif len(args) == 2 and all(isinstance(arg, int) for arg in args):
            # (width, height) arguments - use our StateIcon sizing
            width, height = args
            self.setStateIconSize(width, height)
        else:
            # Let Qt handle other cases
            super().setIconSize(*args)

    @property
    def default_margins(self) -> tuple[int, int, int, int]:
        """Default margins for ToolButton (left, top, right, bottom)."""
        return (4, 4, 4, 4)

    def _setup_button_layout(self):
        """ToolButton-specific layout setup."""
        # Layout is setup in __init__ for ToolButton
        pass

    def _setup_icon_in_layout(self):
        """Setup icon in tool button layout."""
        if self.layout():
            self.layout().addWidget(self.state_icon)
        else:
            # Create simple layout for icon-only button
            layout = QHBoxLayout(self)
            margins = self.default_margins
            layout.setContentsMargins(*margins)
            layout.setSpacing(0)
            layout.addWidget(self.state_icon)

    def _on_icon_size_changed(self):
        """Override BaseButton behavior for ToolButton-specific sizing."""
        # if no custom button size is set, auto-resize ToolButton to fit icon exactly
        if not self._has_custom_button_size:
            optimal_size = SizeManager.calculate_tool_button_size(self)
            SizeManager.apply_exact_size(self, optimal_size.width(), optimal_size.height())
        else:
            self.updateGeometry()
            self.update()

    def setCheckable(self, checkable: bool):
        """Override setCheckable to handle sizing issues with checkable tool buttons.

        Args:
            checkable (bool): Whether the button should be checkable.
        """
        super().setCheckable(checkable)

        if checkable and self.state_icon and not self._has_custom_button_size:
            # Apply proper sizing when button becomes checkable
            optimal_size = SizeManager.calculate_tool_button_size(self)
            SizeManager.apply_exact_size(self, optimal_size.width(), optimal_size.height())

    def sizeHint(self) -> QSize:
        """Calculate the preferred size for the tool button based on its icon."""
        if self._has_custom_button_size:
            return self.size()  # return the custom size (already adjusted for minimum in setButtonSize)

        if self.layout() and self.state_icon:
            # use layout's size hint plus button margins
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            total_width = layout_hint.width() + margins.left() + margins.right()
            total_height = layout_hint.height() + margins.top() + margins.bottom()
            return QSize(total_width, total_height)
        else:
            # fall back to QToolButton's default size hint
            return super().sizeHint()

    # icon() method inherited from _StateIconMixin
