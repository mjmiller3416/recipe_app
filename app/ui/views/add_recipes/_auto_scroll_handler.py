"""app/ui/views/add_recipes/_auto_scroll_handler.py

Auto-scroll handler for AddRecipes view to improve navigation experience.
Provides automatic scrolling to position widgets appropriately when they receive focus.
"""

# ── Imports ──
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import QScrollArea, QWidget, QTextEdit
from app.ui.utils import global_signals


class AutoScrollHandler:
    """
    Handles automatic scrolling behavior for the AddRecipes view.

    Provides smooth scrolling to position focused widgets optimally:
    - Ingredient quantity fields: Scroll to center the widget vertically
    - Directions/Notes text edits: Scroll to bottom of the page
    """

    def __init__(self, scroll_area: QScrollArea, scroll_content: QWidget):
        """
        Initialize the auto-scroll handler.

        Args:
            scroll_area: The QScrollArea to control
            scroll_content: The content widget inside the scroll area
        """
        self.scroll_area = scroll_area
        self.scroll_content = scroll_content
        self.scroll_bar = scroll_area.verticalScrollBar()

        # Animation for smooth scrolling
        self.scroll_animation = QPropertyAnimation(self.scroll_bar, b"value")
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.scroll_animation.setDuration(500)  # 500ms for smooth animation

        # Connect to global auto-scroll signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect to global auto-scroll signals."""
        from _dev_tools import DebugLogger
        DebugLogger.log("[AutoScroll] Connecting to global signals", "debug")

        global_signals.scroll_to_middle_requested.connect(self.scroll_to_middle)
        global_signals.scroll_to_bottom_requested.connect(self.scroll_to_bottom)

    def scroll_to_middle(self, widget: QWidget):
        """
        Scroll to position the widget vertically in the middle of the viewport.

        Args:
            widget: The widget to center in the viewport
        """
        from _dev_tools import DebugLogger

        if not widget or not widget.isVisible():
            DebugLogger.log(f"[AutoScroll] Widget not visible, skipping scroll", "debug")
            return

        # Calculate widget position relative to scroll content
        widget_pos = widget.mapTo(self.scroll_content, widget.rect().topLeft())
        widget_center_y = widget_pos.y() + widget.height() // 2

        # Calculate viewport center
        viewport_height = self.scroll_area.viewport().height()
        viewport_center = viewport_height // 2

        # Calculate target scroll position to center the widget
        target_scroll = widget_center_y - viewport_center

        # Clamp to valid scroll range
        max_scroll = self.scroll_bar.maximum()
        min_scroll = self.scroll_bar.minimum()
        target_scroll = max(min_scroll, min(max_scroll, target_scroll))

        DebugLogger.log(f"[AutoScroll] Scrolling to middle - widget_y: {widget_center_y}, target: {target_scroll}, max: {max_scroll}", "debug")

        # Perform smooth scroll animation
        self._animate_scroll_to(target_scroll)

    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the scroll area.
        """
        from _dev_tools import DebugLogger
        DebugLogger.log("[AutoScroll] Scrolling to bottom", "debug")

        max_scroll = self.scroll_bar.maximum()
        self._animate_scroll_to(max_scroll)

    def _animate_scroll_to(self, target_value: int):
        """
        Animate scroll bar to target value.

        Args:
            target_value: Target scroll bar value
        """
        if self.scroll_animation.state() == QPropertyAnimation.State.Running:
            self.scroll_animation.stop()

        current_value = self.scroll_bar.value()

        # Only animate if there's a significant difference
        if abs(target_value - current_value) > 10:
            self.scroll_animation.setStartValue(current_value)
            self.scroll_animation.setEndValue(target_value)
            self.scroll_animation.start()
        else:
            # Small differences - just set directly
            self.scroll_bar.setValue(target_value)