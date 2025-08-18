"""app/ui/components/layout/collapsible_card.py

A Card widget with collapsible functionality using a sliding blinds effect.
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from typing import Optional

from app.config import CARD
from app.style.icon import Type, Name
from app.style.animation.animator import Animator
from app.ui.components.widgets.button import ToolButton
from dev_tools.debug_logger import DebugLogger
from .card import Card


# ── Collapsible Card Widget ──────────────────────────────────────────────────────────────────
class CollapsibleCard(Card):
    """A Card widget with collapsible functionality using a sliding blinds effect.

    This class extends the standard Card widget with collapsible behavior that
    animates the content area, sliding up from the bottom like window blinds.
    The header remains visible with a toggle button for expand/collapse control.
    """

    def __init__(self, parent=None, content_layout: str = "vbox", card_type: str = "Default"):
        """Initialize the CollapsibleCard widget.

        Args:
            parent: Optional parent widget.
            content_layout: Initial layout type: "vbox" (default), "hbox", or "grid".
            card_type: Card styling type for QSS (default: "Default").
        """
        super().__init__(parent, content_layout, card_type)

        self.setObjectName("CollapsibleCard")

        # Collapsible state
        self._is_expanded = True
        self._collapse_button = None
        self._content_height = 0  # Store original content height
        self._animation_duration = 300  # Default animation duration

        # Store original content container for height calculations
        self._original_content_container = self._content_container

    def _add_collapse_button_to_header(self):
        """Add the collapse button to the right side of the header."""
        if not self._header_row_layout or not self._collapse_button:
            return

        # Add stretch to push button to the right
        self._header_row_layout.addStretch()

        # Add the collapse button aligned to the right
        self._header_row_layout.addWidget(
            self._collapse_button,
            0,
            Qt.AlignVCenter | Qt.AlignRight
        )

    def _create_collapse_button(self):
        """Create the collapse/expand toggle button."""
        if self._collapse_button:
            return

        self._collapse_button = ToolButton(Type.DEFAULT, Name.ANGLE_DOWN)
        self._collapse_button.setObjectName("CollapseButton")
        self._collapse_button.clicked.connect(self.toggle)
        self._collapse_button.setFixedSize(24, 24)

        DebugLogger.log("Created collapse button for collapsible card", "debug")

    def _store_content_height(self):
        """Store the current content height before animation."""
        if self._content_container and self._is_expanded:
            # Force layout update to get accurate measurements
            self._content_container.updateGeometry()
            self._content_container.adjustSize()
            
            # Use the actual height rather than sizeHint for more accuracy
            self._content_height = self._content_container.height()
            
            # Fallback to sizeHint if height is still invalid
            if self._content_height <= 0:
                self._content_height = self._content_container.sizeHint().height()

        DebugLogger.log(f"Stored content height: {self._content_height}", "debug")

    def _update_collapse_button_icon(self):
        """Update the collapse button icon based on expanded state."""
        if not self._collapse_button:
            return

        from app.ui.components.widgets.button import BaseButton

        icon_name = Name.ANGLE_DOWN if self._is_expanded else Name.ANGLE_RIGHT

        # Use BaseButton's setIcon method explicitly (same pattern as titlebar)
        BaseButton.setIcon(self._collapse_button, icon_name)


    # ── Public API ───────────────────────────────────────────────────────────────────────────────
    @property
    def is_expanded(self) -> bool:
        """Check if the card is currently expanded."""
        return self._is_expanded

    @property
    def animation_duration(self) -> int:
        """Get the current animation duration."""
        return self._animation_duration

    def setAnimationDuration(self, duration: int):
        """Set the animation duration for expand/collapse.

        Args:
            duration: Animation duration in milliseconds.
        """
        self._animation_duration = duration

    def setExpanded(self, expanded: bool, animate: bool = True):
        """Programmatically set the expanded state.

        Args:
            expanded: Whether the card should be expanded.
            animate: Whether to animate the state change.
        """
        if self._is_expanded == expanded:
            return  # Already in the desired state

        if animate:
            self.toggle()
        else:
            # Set state without animation
            self._is_expanded = expanded
            self._update_collapse_button_icon()

            if self._content_container:
                if expanded:
                    if self._content_height <= 0:
                        self._store_content_height()
                    self._content_container.setMaximumHeight(self._content_height)
                else:
                    self._content_container.setMaximumHeight(0)

    def setHeader(self, text: str, icon: Optional[object] = None):
        """Override setHeader to add collapse button to header.

        Args:
            text: Header text.
            icon: Optional icon (Name enum or QWidget).
        """
        # Call parent setHeader first
        super().setHeader(text, icon)

        # Add collapse button to header
        self._create_collapse_button()
        self._add_collapse_button_to_header()

    def toggle(self):
        """Toggle the collapsed/expanded state with sliding blinds animation."""
        if not self._content_container:
            DebugLogger.log("No content container to animate", "warning")
            return

        DebugLogger.log(
            f"Toggling collapsible card: currently {'expanded' if self._is_expanded else 'collapsed'}"
        )

        # Store content height if expanding or if we haven't stored it yet
        if not self._is_expanded or self._content_height <= 0:
            self._store_content_height()

        # Get header height to determine how much to collapse
        if self._header_container:
            self._header_container.updateGeometry()
            header_height = self._header_container.sizeHint().height()
            if header_height <= 0:
                header_height = self._header_container.height()
        else:
            header_height = 0
        
        # Determine animation parameters
        if self._is_expanded:
            # Collapsing: animate from current height to just header height
            start_height = self.height()
            end_height = header_height
        else:
            # Expanding: animate from header height to full height
            start_height = header_height
            end_height = header_height + self._content_height

        DebugLogger.log(f"Animating card height from {start_height} to {end_height}")

        # Store current sizes to prevent layout recalculation during animation
        if self._header_container:
            header_current_height = self._header_container.height()
            self._header_container.setFixedHeight(header_current_height)
        
        if self._content_container:
            content_current_height = self._content_container.height()
            self._content_container.setFixedHeight(content_current_height)

        # Create and start the animation on the card itself
        animation = Animator.animate_height(
            widget=self,
            start=start_height,
            end=end_height,
            duration=self._animation_duration
        )

        # Only restore flexible sizing when expanding, not when collapsing
        def on_animation_finished():
            if self._is_expanded:
                # Only restore flexible sizing when expanded
                if self._header_container:
                    self._header_container.setMinimumHeight(0)
                    self._header_container.setMaximumHeight(16777215)
                if self._content_container:
                    self._content_container.setMinimumHeight(0)
                    self._content_container.setMaximumHeight(16777215)
                self.setMaximumHeight(16777215)
            # When collapsed, keep everything fixed - don't restore flexible sizing

        animation.finished.connect(on_animation_finished)

        # Update state and button icon
        self._is_expanded = not self._is_expanded
        self._update_collapse_button_icon()

        return animation

