"""app/ui/style/animations/flow_animator.py

Animation handler for FlowLayout widgets with cascading effect.
"""

from typing import Dict, Optional, List, Tuple
from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QSequentialAnimationGroup, QParallelAnimationGroup, QTimer, QObject, Signal
from PySide6.QtWidgets import QWidget
import math


class FlowAnimator(QObject):
    """Handles cascading animations for FlowLayout widgets."""

    # Signal emitted when all animations complete
    animations_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animations: Dict[QWidget, QPropertyAnimation] = {}
        self._duration = 250  # Duration for each widget
        self._cascade_delay = 30  # Delay between each widget animation
        self._easing_curve = QEasingCurve.Type.OutCubic
        self._enabled = False

        # Animation mode
        self._cascade_mode = 'wave'  # 'wave', 'row', 'diagonal', 'radial', 'random'

        # Current animation group
        self._current_animation_group = None

        # Position tracking for cascade calculation
        self._widget_positions: Dict[QWidget, QRect] = {}

    def enable(self, enabled: bool = True):
        """Enable or disable animations."""
        self._enabled = enabled
        if not enabled:
            self.clear()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_cascade_mode(self, mode: str):
        """
        Set the cascade animation mode.

        Modes:
        - 'wave': Left to right, top to bottom
        - 'row': Animate row by row
        - 'diagonal': Diagonal wave from top-left
        - 'radial': Radiate from center
        - 'random': Random order with stagger
        """
        self._cascade_mode = mode

    def set_animation_params(self, duration: int, cascade_delay: int, easing: QEasingCurve.Type):
        """Set animation parameters."""
        self._duration = duration
        self._cascade_delay = cascade_delay
        self._easing_curve = easing

    def add_widget(self, widget: QWidget) -> Optional[QPropertyAnimation]:
        """Add animation for a widget."""
        if not self._enabled:
            return None

        if widget in self._animations:
            return self._animations[widget]

        animation = QPropertyAnimation(widget, b'geometry')
        animation.setDuration(self._duration)
        animation.setEasingCurve(self._easing_curve)

        # Initialize with current geometry
        current_geometry = widget.geometry()
        if not current_geometry.isValid():
            current_geometry = QRect(QPoint(0, 0), widget.sizeHint())
        animation.setStartValue(current_geometry)
        animation.setEndValue(current_geometry)

        self._animations[widget] = animation
        return animation

    def remove_widget(self, widget: QWidget):
        """Remove animation for a widget."""
        if widget not in self._animations:
            return

        animation = self._animations.pop(widget)
        animation.stop()
        animation.deleteLater()
        self._widget_positions.pop(widget, None)

    def update_positions(self, widget_positions: Dict[QWidget, QRect]) -> bool:
        """
        Update widget positions with cascading animation.

        Args:
            widget_positions: Dictionary mapping widgets to their target positions

        Returns:
            True if any animations were started, False otherwise
        """
        if not self._enabled:
            # Just set positions directly
            for widget, rect in widget_positions.items():
                widget.setGeometry(rect)
            return False

        # Stop any running animations
        if self._current_animation_group:
            self._current_animation_group.stop()
            self._current_animation_group.deleteLater()

        # Calculate animation order based on cascade mode
        ordered_widgets = self._calculate_animation_order(widget_positions)

        if not ordered_widgets:
            return False

        # Create the cascading animation
        self._current_animation_group = self._create_cascade_animation(ordered_widgets)

        # Connect finish signal
        self._current_animation_group.finished.connect(self.animations_finished.emit)

        # Start the animation
        self._current_animation_group.start()

        # Update stored positions
        self._widget_positions = widget_positions.copy()

        return True

    def _calculate_animation_order(self, widget_positions: Dict[QWidget, QRect]) -> List[Tuple[QWidget, QRect, int]]:
        """
        Calculate the order and delay for widget animations based on cascade mode.

        Returns:
            List of tuples (widget, target_rect, delay_ms)
        """
        widgets_with_delay = []

        if self._cascade_mode == 'wave':
            # Sort by position: top to bottom, left to right
            sorted_widgets = sorted(
                widget_positions.items(),
                key=lambda item: (item[1].y(), item[1].x())
            )
            for i, (widget, rect) in enumerate(sorted_widgets):
                delay = i * self._cascade_delay
                widgets_with_delay.append((widget, rect, delay))

        elif self._cascade_mode == 'row':
            # Group by rows, animate each row together
            rows = {}
            for widget, rect in widget_positions.items():
                row_y = rect.y()
                if row_y not in rows:
                    rows[row_y] = []
                rows[row_y].append((widget, rect))

            delay = 0
            for row_y in sorted(rows.keys()):
                for widget, rect in rows[row_y]:
                    widgets_with_delay.append((widget, rect, delay))
                delay += self._cascade_delay * 2  # Larger delay between rows

        elif self._cascade_mode == 'diagonal':
            # Calculate diagonal distance from top-left
            sorted_widgets = sorted(
                widget_positions.items(),
                key=lambda item: item[1].x() + item[1].y()
            )
            for i, (widget, rect) in enumerate(sorted_widgets):
                delay = i * self._cascade_delay
                widgets_with_delay.append((widget, rect, delay))

        elif self._cascade_mode == 'radial':
            # Calculate distance from center
            if widget_positions:
                # Find center point
                min_x = min(rect.x() for rect in widget_positions.values())
                max_x = max(rect.right() for rect in widget_positions.values())
                min_y = min(rect.y() for rect in widget_positions.values())
                max_y = max(rect.bottom() for rect in widget_positions.values())
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2

                # Sort by distance from center
                sorted_widgets = sorted(
                    widget_positions.items(),
                    key=lambda item: math.sqrt(
                        (item[1].center().x() - center_x) ** 2 +
                        (item[1].center().y() - center_y) ** 2
                    )
                )
                for i, (widget, rect) in enumerate(sorted_widgets):
                    delay = i * self._cascade_delay
                    widgets_with_delay.append((widget, rect, delay))

        elif self._cascade_mode == 'random':
            # Random order with consistent stagger
            import random
            items = list(widget_positions.items())
            random.shuffle(items)
            for i, (widget, rect) in enumerate(items):
                delay = i * self._cascade_delay
                widgets_with_delay.append((widget, rect, delay))

        else:  # Default to wave
            sorted_widgets = sorted(
                widget_positions.items(),
                key=lambda item: (item[1].y(), item[1].x())
            )
            for i, (widget, rect) in enumerate(sorted_widgets):
                delay = i * self._cascade_delay
                widgets_with_delay.append((widget, rect, delay))

        return widgets_with_delay

    def _create_cascade_animation(self, ordered_widgets: List[Tuple[QWidget, QRect, int]]) -> QParallelAnimationGroup:
        """
        Create a parallel animation group with delayed starts for cascade effect.

        Args:
            ordered_widgets: List of (widget, target_rect, delay) tuples

        Returns:
            QParallelAnimationGroup with all animations
        """
        group = QParallelAnimationGroup(self)

        for widget, target_rect, delay in ordered_widgets:
            # Ensure widget has an animation
            if widget not in self._animations:
                self.add_widget(widget)

            animation = self._animations[widget]

            # Create a sequential group for delay + animation
            seq_group = QSequentialAnimationGroup(self)

            # Add delay if needed
            if delay > 0:
                # Create a pause by using a dummy animation
                pause = QPropertyAnimation(widget, b'geometry')
                pause.setDuration(delay)
                pause.setStartValue(widget.geometry())
                pause.setEndValue(widget.geometry())
                seq_group.addAnimation(pause)

            # Configure the actual animation
            animation = QPropertyAnimation(widget, b'geometry')
            animation.setDuration(self._duration)
            animation.setEasingCurve(self._easing_curve)
            animation.setStartValue(widget.geometry())
            animation.setEndValue(target_rect)

            # Add optional effects based on mode
            if self._cascade_mode in ['wave', 'diagonal']:
                # Add a subtle fade-in effect by starting slightly offset
                start_rect = widget.geometry()
                offset_start = QRect(start_rect)
                offset_start.moveTop(start_rect.top() - 10)  # Start 10px higher
                animation.setStartValue(offset_start)

            seq_group.addAnimation(animation)
            group.addAnimation(seq_group)

        return group

    def force_complete(self):
        """Force all animations to complete immediately."""
        if self._current_animation_group:
            self._current_animation_group.stop()
            # Jump to end positions
            for widget, rect in self._widget_positions.items():
                widget.setGeometry(rect)

    def clear(self):
        """Clear all animations."""
        if self._current_animation_group:
            self._current_animation_group.stop()
            self._current_animation_group.deleteLater()
            self._current_animation_group = None

        for animation in self._animations.values():
            animation.stop()
            animation.deleteLater()

        self._animations.clear()
        self._widget_positions.clear()
