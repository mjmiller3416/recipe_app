"""app/style/animation/flip_animations.py

This module contains classes and helpers specifically for page flip animations.
Provides FlipAnimationHelper for managing flip transformations and PageFlipContainer
for widgets that need flip transition capabilities.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Property, QEasingCurve, QObject, Signal
from PySide6.QtWidgets import QFrame


# ── Flip Animation Helper ───────────────────────────────────────────────────────────────────────────────────
class FlipAnimationHelper(QObject):
    """Helper class to provide QObject functionality for page flip animations."""

    animation_finished = Signal()

    def __init__(self, target_widget, parent=None):
        super().__init__(parent)
        self.target_widget = target_widget
        self._rotation_y = 0
        self._opacity = 1.0
        self._scale_x = 1.0
        self._scale_y = 1.0

        # ── Attributes ──
        self.duration = 800
        self.easing_curve = QEasingCurve.InOutQuad
        self.flip_axis = 'y'  # 'x' or 'y'
        self.fade_during_flip = True
        self.scale_during_flip = True

    @Property(float)
    def rotation_y(self):
        return self._rotation_y

    @rotation_y.setter
    def rotation_y(self, value):
        self._rotation_y = value
        self._apply_transform()

    @Property(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        if hasattr(self.target_widget, 'setWindowOpacity'):
            self.target_widget.setWindowOpacity(value)

    @Property(float)
    def scale_x(self):
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value):
        self._scale_x = value
        self._apply_transform()

    @Property(float)
    def scale_y(self):
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value):
        self._scale_y = value
        self._apply_transform()

    def _apply_transform(self):
        """Apply the current transformation to the target widget."""
        if not self.target_widget:
            return

        # calculate scale factor based on rotation
        if self.scale_during_flip:
            # create a "3D flip" effect by scaling width/height based on rotation
            if self.flip_axis == 'y':
                # horizontal flip - scale width
                scale_factor = abs(1.0 - abs(self._rotation_y) / 90.0)
                if abs(self._rotation_y) > 90:
                    scale_factor = abs(abs(self._rotation_y) - 180) / 90.0

                # apply width scaling
                original_width = getattr(self.target_widget, '_original_width', self.target_widget.width())
                if not hasattr(self.target_widget, '_original_width'):
                    self.target_widget._original_width = self.target_widget.width()

                new_width = max(1, int(original_width * scale_factor))
                self.target_widget.setFixedWidth(new_width)

            elif self.flip_axis == 'x':
                # vertical flip - scale height
                scale_factor = abs(1.0 - abs(self._rotation_y) / 90.0)
                if abs(self._rotation_y) > 90:
                    scale_factor = abs(abs(self._rotation_y) - 180) / 90.0

                # apply height scaling
                original_height = getattr(self.target_widget, '_original_height', self.target_widget.height())
                if not hasattr(self.target_widget, '_original_height'):
                    self.target_widget._original_height = self.target_widget.height()

                new_height = max(1, int(original_height * scale_factor))
                self.target_widget.setFixedHeight(new_height)

        # apply opacity effect if fade is enabled
        if self.fade_during_flip:
            # calculate opacity based on rotation
            opacity_factor = 1.0 - (abs(self._rotation_y) / 180.0) * 0.3  # Fade to 70% minimum
            self.target_widget.setWindowOpacity(max(0.3, opacity_factor * self._opacity))

        # handle visibility for back side - this is where the widget swap happens
        if abs(self._rotation_y) > 90:
            self.target_widget.setVisible(False)
        else:
            self.target_widget.setVisible(True)


class PageFlipContainer(QFrame):
    """A container widget that supports page flip animations between child widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_widget = None
        self.next_widget = None
        self.animation_helper = None

        # animation configuration
        self.flip_duration = 800
        self.flip_easing = QEasingCurve.InOutQuad
        self.flip_axis = 'y'  # 'x' for vertical flip, 'y' for horizontal flip
        self.fade_during_flip = True
        self.scale_during_flip = True

    def set_current_widget(self, widget):
        """Set the current widget without animation."""
        if self.current_widget:
            self.current_widget.setParent(None)
        self.current_widget = widget
        if widget:
            widget.setParent(self)
            widget.show()

    def flip_to_widget(self, widget, callback=None):
        """Flip to a new widget with animation."""
        if not self.current_widget:
            self.set_current_widget(widget)
            return

        self.next_widget = widget
        widget.setParent(self)
        widget.hide()

        # import here to avoid circular imports
        from PySide6.QtCore import QPropertyAnimation, QTimer

        # create animation helper for this flip
        self.animation_helper = FlipAnimationHelper(self.current_widget, self)

        # configure animation helper
        self.animation_helper.duration = self.flip_duration
        self.animation_helper.easing_curve = self.flip_easing
        self.animation_helper.flip_axis = self.flip_axis
        self.animation_helper.fade_during_flip = self.fade_during_flip
        self.animation_helper.scale_during_flip = self.scale_during_flip

        # create the flip animation
        flip_animation = QPropertyAnimation(self.animation_helper, b"rotation_y")
        flip_animation.setDuration(self.flip_duration)
        flip_animation.setStartValue(0)
        flip_animation.setEndValue(180)
        flip_animation.setEasingCurve(self.flip_easing)

        # function to handle the midpoint of the flip (swap widgets)
        def handle_flip_midpoint():
            # hide current widget and show next widget
            self.current_widget.hide()
            self.next_widget.show()

            # update the animation helper to target the next widget
            self.animation_helper.target_widget = self.next_widget

            # reset the next widget's dimensions if they were modified
            if hasattr(self.next_widget, '_original_width'):
                self.next_widget.setFixedWidth(self.next_widget._original_width)
            if hasattr(self.next_widget, '_original_height'):
                self.next_widget.setFixedHeight(self.next_widget._original_height)

            # start the second half of the animation
            second_half_animation = QPropertyAnimation(self.animation_helper, b"rotation_y")
            second_half_animation.setDuration(self.flip_duration // 2)
            second_half_animation.setStartValue(180)
            second_half_animation.setEndValue(0)
            second_half_animation.setEasingCurve(self.flip_easing)

            # handle completion
            def on_animation_complete():
                # reset opacity and dimensions
                self.next_widget.setWindowOpacity(1.0)
                if hasattr(self.next_widget, '_original_width'):
                    self.next_widget.setFixedWidth(self.next_widget._original_width)
                if hasattr(self.next_widget, '_original_height'):
                    self.next_widget.setFixedHeight(self.next_widget._original_height)

                # swap the widgets
                old_current = self.current_widget
                self.current_widget = self.next_widget
                self.next_widget = None

                # clean up old widget
                if old_current:
                    old_current.setParent(None)

                # call callback if provided
                if callback:
                    callback()

            second_half_animation.finished.connect(on_animation_complete)
            second_half_animation.start()

            # store animation to prevent garbage collection
            self._second_half_animation = second_half_animation

        # schedule the midpoint swap
        QTimer.singleShot(self.flip_duration // 2, handle_flip_midpoint)

        # start the first half of the animation
        flip_animation.start()

        # store animation to prevent garbage collection
        self._flip_animation = flip_animation

    def configure_animation(self, **kwargs):
        """
        Configure flip animation settings.

        Args:
            **kwargs: Animation settings:
                - duration (int): Animation duration in milliseconds
                - easing (QEasingCurve): Easing curve
                - flip_axis (str): 'x' or 'y' for flip direction
                - fade_during_flip (bool): Whether to fade during flip
                - scale_during_flip (bool): Whether to scale during flip
        """
        for key, value in kwargs.items():
            if key == 'duration':
                self.flip_duration = value
            elif key == 'easing':
                self.flip_easing = value
            elif key == 'flip_axis':
                self.flip_axis = value
            elif key == 'fade_during_flip':
                self.fade_during_flip = value
            elif key == 'scale_during_flip':
                self.scale_during_flip = value
