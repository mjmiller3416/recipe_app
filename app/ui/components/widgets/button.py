"""app/ui/components/widgets/button.py

Clean button system using QPushButton and QToolButton as base classes.

This module provides Button and ToolButton classes that integrate with StateIcon
for theme-aware icons while leveraging Qt's native button behavior.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, QEvent, Qt
from PySide6.QtWidgets import QPushButton, QToolButton, QHBoxLayout, QLabel, QSizePolicy, QApplication

from app.appearance.icon.config import Name, Type
from app.appearance.icon.icon import StateIcon


# ── Shared Helper Functions ──────────────────────────────────────────────────────────────────────
def _calculate_button_size(widget, custom_size_width=None, custom_size_height=None):
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


def _ensure_layout_updated(widget):
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
            from dev_tools import DebugLogger
            DebugLogger.log(f"Warning: Layout appears empty after synchronization for {widget.objectName()}", "warning")


class _StateIconMixin:
    """Mixin class providing state override methods for StateIcon integration."""
    
    def setStateHover(self, role: str):
        """Override the color role used for the hover state."""
        if hasattr(self, 'state_icon') and self.state_icon:
            self.state_icon.setStateHover(role)

    def setStateDefault(self, role: str):
        """Override the default icon color role."""
        if hasattr(self, 'state_icon') and self.state_icon:
            self.state_icon.setStateDefault(role)

    def setStateChecked(self, role: str):
        """Override the checked icon color role."""
        if hasattr(self, 'state_icon') and self.state_icon:
            self.state_icon.setStateChecked(role)

    def setStateDisabled(self, role: str):
        """Override the disabled icon color role."""
        if hasattr(self, 'state_icon') and self.state_icon:
            self.state_icon.setStateDisabled(role)

    def clearAllStateOverrides(self):
        """Clears all icon state color overrides, restoring type-based defaults."""
        if hasattr(self, 'state_icon') and self.state_icon:
            self.state_icon.clearAllStateOverrides()

    def icon(self) -> StateIcon:
        """Returns the StateIcon widget used in the button."""
        return getattr(self, 'state_icon', None)


# ── Button ───────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton, _StateIconMixin):
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
        super().__init__(label, parent)

        self._type = type
        self._icon_spacing = 6
        self.state_icon = None
        self._has_custom_button_size = False

        # setup layout if we have an icon
        if icon:
            self._setup_layout_with_icon(label, icon)

        # connect state change signals for icon sync
        self.toggled.connect(self._sync_icon_state)

    def _setup_layout_with_icon(self, label: str, icon: Name):
        """Setup layout with icon and text."""
        # clear the default text since we'll use a layout
        self.setText("")

        # create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(self._icon_spacing)

        # add icon
        self.state_icon = StateIcon(icon, self._type)
        layout.addWidget(self.state_icon)

        # add label
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._sync_icon_state()

    def _sync_icon_state(self):
        """Synchronize StateIcon with current button state."""
        if self.state_icon:
            self.state_icon.autoDetectState(
                checked=self.isChecked(),
                hovered=self.underMouse(),
                enabled=self.isEnabled()
            )

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        super().enterEvent(event)
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        super().leaveEvent(event)
        self._sync_icon_state()

    def changeEvent(self, event):
        """Handle enabled/disabled state changes."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._sync_icon_state()

    def setButtonSize(self, width: int, height: int):
        """Set a fixed size for the entire button widget.

        Args:
            width (int): Button width in pixels (1-2048).
            height (int): Button height in pixels (1-2048).
            
        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Button size parameters must be integers, got width={type(width)}, height={type(height)}")
        
        # Validate reasonable bounds
        if width < 1 or height < 1 or width > 2048 or height > 2048:
            from dev_tools import DebugLogger
            DebugLogger.log(f"Button size ({width}, {height}) outside recommended bounds (1-2048)", "warning")
        # calculate minimum required size to prevent content clipping
        if self.layout():
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            min_width = layout_hint.width() + margins.left() + margins.right()
            min_height = layout_hint.height() + margins.top() + margins.bottom()

            # use the larger of requested size or minimum required size
            final_width = max(width, min_width)
            final_height = max(height, min_height)

            self.setFixedSize(final_width, final_height)
        else:
            self.setFixedSize(width, height)

        self._has_custom_button_size = True

    def setIconSize(self, width: int, height: int):
        """Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels (1-512).
            height (int): Icon height in pixels (1-512).
            
        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Icon size parameters must be integers, got width={type(width)}, height={type(height)}")
        
        # Validate and clamp size bounds
        original_width, original_height = width, height
        width = max(1, min(width, 512))
        height = max(1, min(height, 512))
        
        if width != original_width or height != original_height:
            from dev_tools import DebugLogger
            DebugLogger.log(f"Icon size clamped from ({original_width}, {original_height}) to ({width}, {height})", "warning")
        if self.state_icon:
            self.state_icon.setSize(width, height)
            # if no custom button size is set, allow button to resize automatically
            if not self._has_custom_button_size:
                # clear any fixed size constraints and let the layout determine size
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)  # Qt's default max size
                self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                # ensure layout calculations are synchronized
                _ensure_layout_updated(self)
            self.updateGeometry()
            # force a repaint to ensure visual update
            self.update()

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

    def text(self) -> str:
        """Get the current text label.

        Returns:
            str: Current button text.
        """
        if hasattr(self, 'label') and self.label:
            return self.label.text()
        else:
            return super().text()

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

    # state override methods for icon
    def setStateHover(self, role: str):
        """Override the color role used for the hover state."""
        if self.state_icon:
            self.state_icon.setStateHover(role)

    def setStateDefault(self, role: str):
        """Override the default icon color role."""
        if self.state_icon:
            self.state_icon.setStateDefault(role)

    def setStateChecked(self, role: str):
        """Override the checked icon color role."""
        if self.state_icon:
            self.state_icon.setStateChecked(role)

    def setStateDisabled(self, role: str):
        """Override the disabled icon color role."""
        if self.state_icon:
            self.state_icon.setStateDisabled(role)

    def clearAllStateOverrides(self):
        """Clears all icon state color overrides, restoring type-based defaults."""
        if self.state_icon:
            self.state_icon.clearAllStateOverrides()

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

    def icon(self) -> StateIcon:
        """Returns the StateIcon widget used in the button.

        Returns:
            StateIcon: The button's internal themed icon widget.
        """
        return self.state_icon


# ── ToolButton ───────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, _StateIconMixin):
    """A QToolButton with integrated StateIcon support.

    Icon-only button that leverages QToolButton's native behavior while
    providing StateIcon integration for theme-aware icons.
    """

    def __init__(self, icon: Name, type: Type = Type.DEFAULT, parent=None):
        """Create a compact icon-only tool button.

        Args:
            icon (Name): The icon to display.
            type (Type): Visual style type (defines icon color map).
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._type = type
        self.state_icon = None
        self._has_custom_button_size = False

        # setup layout with StateIcon
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self.state_icon = StateIcon(icon, type)
        layout.addWidget(self.state_icon)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # connect state change signals
        self.toggled.connect(self._sync_icon_state)

        # initialize state sync
        self._sync_icon_state()

    def _sync_icon_state(self):
        """Synchronize StateIcon with current button state."""
        if self.state_icon:
            self.state_icon.autoDetectState(
                checked=self.isChecked(),
                hovered=self.underMouse(),
                enabled=self.isEnabled()
            )

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        super().enterEvent(event)
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        super().leaveEvent(event)
        self._sync_icon_state()

    def changeEvent(self, event):
        """Handle enabled/disabled state changes."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._sync_icon_state()

    def setButtonSize(self, width: int, height: int):
        """Set a fixed size for the entire button widget.

        Args:
            width (int): Button width in pixels (1-2048).
            height (int): Button height in pixels (1-2048).
            
        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Button size parameters must be integers, got width={type(width)}, height={type(height)}")
        
        # Validate reasonable bounds
        if width < 1 or height < 1 or width > 2048 or height > 2048:
            from dev_tools import DebugLogger
            DebugLogger.log(f"Button size ({width}, {height}) outside recommended bounds (1-2048)", "warning")
        # calculate minimum required size to prevent content clipping
        if self.layout():
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            min_width = layout_hint.width() + margins.left() + margins.right()
            min_height = layout_hint.height() + margins.top() + margins.bottom()

            # use the larger of requested size or minimum required size
            final_width = max(width, min_width)
            final_height = max(height, min_height)

            self.setFixedSize(final_width, final_height)
        else:
            self.setFixedSize(width, height)

        self._has_custom_button_size = True

    def setIconSize(self, width: int, height: int):
        """Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels (1-512).
            height (int): Icon height in pixels (1-512).
            
        Raises:
            TypeError: If width or height are not integers.
        """
        # Validate input types
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Icon size parameters must be integers, got width={type(width)}, height={type(height)}")
        
        # Validate and clamp size bounds
        original_width, original_height = width, height
        width = max(1, min(width, 512))
        height = max(1, min(height, 512))
        
        if width != original_width or height != original_height:
            from dev_tools import DebugLogger
            DebugLogger.log(f"Icon size clamped from ({original_width}, {original_height}) to ({width}, {height})", "warning")
        if self.state_icon:
            self.state_icon.setSize(width, height)
            # if no custom button size is set, auto-resize ToolButton to fit icon exactly
            if not self._has_custom_button_size:
                # get the actual size needed by asking the layout
                layout = self.layout()
                if layout:
                    # ensure layout calculations are synchronized
                    _ensure_layout_updated(self)

                    # get the layout's size hint (which should include the StateIcon's size)
                    layout_size = layout.sizeHint()
                    margins = self.contentsMargins()

                    new_width = layout_size.width() + margins.left() + margins.right()
                    new_height = layout_size.height() + margins.top() + margins.bottom()

                    # set the calculated size using min/max to preserve hover effects
                    self.setMinimumSize(new_width, new_height)
                    self.setMaximumSize(new_width, new_height)
                    self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.updateGeometry()
            # force a repaint to ensure visual update
            self.update()

    def setIcon(self, icon: Name):
        """Change the tool button's icon.

        Args:
            icon (Name): The new icon to display.
        """
        if self.state_icon:
            # replace existing icon
            layout = self.layout()
            layout.removeWidget(self.state_icon)
            self.state_icon.deleteLater()

        # create new icon
        self.state_icon = StateIcon(icon, self._type)
        self.layout().addWidget(self.state_icon)
        self._sync_icon_state()

    # State override methods inherited from _StateIconMixin

    def setCheckable(self, checkable: bool):
        """Override setCheckable to handle sizing issues with checkable tool buttons.
        
        Args:
            checkable (bool): Whether the button should be checkable.
        """
        super().setCheckable(checkable)
        
        if checkable and self.state_icon and not self._has_custom_button_size:
            # Apply proper sizing when button becomes checkable
            # This ensures checkable buttons without explicit setIconSize() calls get proper sizing
            layout = self.layout()
            if layout:
                # Ensure layout calculations are synchronized
                _ensure_layout_updated(self)
                
                # Get the actual required size
                layout_size = layout.sizeHint()
                margins = self.contentsMargins()
                
                required_width = layout_size.width() + margins.left() + margins.right()
                required_height = layout_size.height() + margins.top() + margins.bottom()
                
                # Set exact size to prevent Qt from adding extra padding for checkable buttons
                # Ensure minimum size for proper hover detection
                min_button_size = max(required_width, 24)  # At least 24px wide
                min_button_height = max(required_height, 24)  # At least 24px tall
                
                self.setMinimumSize(min_button_size, min_button_height)
                self.setMaximumSize(min_button_size, min_button_height)
                self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

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
