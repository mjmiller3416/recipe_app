"""app/ui/components/widgets/button.py

Clean button system using QPushButton and QToolButton as base classes.

This module provides Button and ToolButton classes that integrate with StateIcon
for theme-aware icons while leveraging Qt's native button behavior.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, QEvent, Qt
from PySide6.QtWidgets import QPushButton, QToolButton, QHBoxLayout, QLabel, QSizePolicy

from app.appearance.icon.config import Name, Type, State
from app.appearance.icon.icon import StateIcon

from dev_tools import DebugLogger


# ── Button ───────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton):
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

        # Setup layout if we have an icon
        if icon:
            self._setup_layout_with_icon(label, icon)
        
        # Connect state change signals for icon sync
        self.toggled.connect(self._sync_icon_state)

    def _setup_layout_with_icon(self, label: str, icon: Name):
        """Setup layout with icon and text."""
        # Clear the default text since we'll use a layout
        self.setText("")
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(self._icon_spacing)

        # Add icon
        self.state_icon = StateIcon(icon, self._type)
        layout.addWidget(self.state_icon)

        # Add label
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Set proper size policy to allow expansion
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # Initialize state sync
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
            width (int): Button width in pixels.
            height (int): Button height in pixels.
        """
        self.setFixedSize(width, height)
        self._has_custom_button_size = True

    def setIconSize(self, width: int, height: int):
        """Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels.
            height (int): Icon height in pixels.
        """
        if self.state_icon:
            self.state_icon.setSize(width, height)
            # If no custom button size is set, allow button to resize automatically
            if not self._has_custom_button_size:
                # Clear any fixed size constraints and let the layout determine size
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)  # Qt's default max size
                self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                # Force layout to recalculate
                layout = self.layout()
                if layout:
                    layout.invalidate()
                    layout.activate()
            self.updateGeometry()
            # Force a repaint to ensure visual update
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
            # Button with icon - update label widget
            self.label.setText(text)
        else:
            # Text-only button - use native setText
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
            # Replace existing icon
            layout = self.layout()
            layout.removeWidget(self.state_icon)
            self.state_icon.deleteLater()

        # Create new icon and setup layout if needed
        if not self.layout():
            self._setup_layout_with_icon(current_text, icon)
        else:
            self.state_icon = StateIcon(icon, self._type)
            self.layout().insertWidget(0, self.state_icon)
            self._sync_icon_state()

    # State override methods for icon
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
            return self.size()  # Return the explicitly set size
        
        if self.layout():
            # Use layout's size hint plus button margins
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            total_width = layout_hint.width() + margins.left() + margins.right()
            total_height = layout_hint.height() + margins.top() + margins.bottom()
            return QSize(total_width, total_height)
        else:
            # Fall back to QPushButton's default size hint for text-only buttons
            return super().sizeHint()

    def icon(self) -> StateIcon:
        """Returns the StateIcon widget used in the button.

        Returns:
            StateIcon: The button's internal themed icon widget.
        """
        return self.state_icon


# ── ToolButton ───────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton):
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

        # Setup layout with StateIcon
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self.state_icon = StateIcon(icon, type)
        layout.addWidget(self.state_icon)

        # Set proper size policy to allow the button to size itself naturally
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Connect state change signals
        self.toggled.connect(self._sync_icon_state)
        
        # Initialize state sync
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
            width (int): Button width in pixels.
            height (int): Button height in pixels.
        """
        self.setFixedSize(width, height)
        self._has_custom_button_size = True

    def setIconSize(self, width: int, height: int):
        """Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels.
            height (int): Icon height in pixels.
        """
        if self.state_icon:
            self.state_icon.setSize(width, height)
            # If no custom button size is set, allow button to resize automatically
            if not self._has_custom_button_size:
                # Clear any fixed size constraints and let the layout determine size
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)  # Qt's default max size
                self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                # Force layout to recalculate
                layout = self.layout()
                if layout:
                    layout.invalidate()
                    layout.activate()
            self.updateGeometry()
            # Force a repaint to ensure visual update
            self.update()

    def setIcon(self, icon: Name):
        """Change the tool button's icon.

        Args:
            icon (Name): The new icon to display.
        """
        if self.state_icon:
            # Replace existing icon
            layout = self.layout()
            layout.removeWidget(self.state_icon)
            self.state_icon.deleteLater()

        # Create new icon
        self.state_icon = StateIcon(icon, self._type)
        self.layout().addWidget(self.state_icon)
        self._sync_icon_state()

    # State override methods for icon
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
        """Calculate the preferred size for the tool button based on its icon."""
        if self._has_custom_button_size:
            return self.size()  # Return the explicitly set size
        
        if self.layout() and self.state_icon:
            # Use layout's size hint plus button margins
            layout_hint = self.layout().sizeHint()
            margins = self.contentsMargins()
            total_width = layout_hint.width() + margins.left() + margins.right()
            total_height = layout_hint.height() + margins.top() + margins.bottom()
            return QSize(total_width, total_height)
        else:
            # Fall back to QToolButton's default size hint
            return super().sizeHint()

    def icon(self) -> StateIcon:
        """Returns the StateIcon widget used in the button.

        Returns:
            StateIcon: The button's internal themed icon widget.
        """
        return self.state_icon
