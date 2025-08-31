"""app/styyle/animation/animator.py

AnimationManager provides methods for animating widgets using QPropertyAnimation.
Supports width animations, fade effects, cross-fading between stacked widgets, and page flip animations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


# ── Animator ────────────────────────────────────────────────────────────────────────────────────────────────
class Animator:
    active_animations = []  # store animations to prevent garbage collection

    @staticmethod
    def animate_width(
        widget: QWidget,
        start: int,
        end: int,
        duration: int
    ) -> QPropertyAnimation:

        """Animate a widget's maximumWidth from start to end."""
        animation = QPropertyAnimation(widget, b"maximumWidth")
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        animation.start()

        Animator.active_animations.append(animation)

        def cleanup():
            if animation in Animator.active_animations:
                Animator.active_animations.remove(animation)

        animation.finished.connect(cleanup)
        return animation

    @staticmethod
    def animate_height(
        widget: QWidget,
        start: int,
        end: int,
        duration: int
    ) -> QPropertyAnimation:
        """Animate a widget's maximumHeight from start to end."""
        animation = QPropertyAnimation(widget, b"maximumHeight")
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        animation.start()

        Animator.active_animations.append(animation)

        def cleanup():
            if animation in Animator.active_animations:
                Animator.active_animations.remove(animation)

        animation.finished.connect(cleanup)
        return animation


    @staticmethod
    def animate_pos(
        widget,
        start_pos: QPoint,
        end_pos: QPoint,
        duration: int):
        """Animate a widget's position from start_pos to end_pos."""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        animation.start()

        Animator.active_animations.append(animation)

        def cleanup():
            if animation in Animator.active_animations:
                Animator.active_animations.remove(animation)

        animation.finished.connect(cleanup)
        return animation

    @staticmethod
    def fade_widget(widget, duration=300, start=1.0, end=0.0):
        """
        Fade a widget from `start` opacity to `end` opacity.

        Args:
            widget (QWidget): The widget to be faded.
            duration (int): Duration of the fade animation in milliseconds. Default is 300ms.
            start (float): Starting opacity value (0.0 to 1.0). Default is 1.0 (fully opaque).
            end (float): Ending opacity value (0.0 to 1.0). Default is 0.0 (fully transparent).
        """
        if not widget.isVisible():
            widget.setVisible(True)  # force visibility if hidden

        # store effect on widget to prevent GC and reuse it
        if not hasattr(widget, "_fade_effect"):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            widget._fade_effect = effect  # cache it on the widget
        else:
            effect = widget._fade_effect

        # set initial opacity directly before animating
        effect.setOpacity(start)

        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        return anim

    @staticmethod
    def transition_stack(current_widget, next_widget, stacked_widget, duration=300):
        """
        Cross-fade between two widgets in a stacked widget.

        Args:
            current_widget (QWidget): The widget currently displayed.
            next_widget (QWidget): The widget to be displayed next.
            stacked_widget (QStackedWidget): The stacked widget managing the two widgets.
            duration (int): Duration of the fade animation in milliseconds. Default is 300ms.
        """
        fade_out = Animator.fade_widget(current_widget, duration, 1.0, 0.0)
        fade_in = Animator.fade_widget(next_widget, duration, 0.0, 1.0)

        # make sure fade-in is ready
        if not next_widget.isVisible():
            next_widget.setVisible(True)
        next_widget.repaint()

        # delay fade-in just slightly (e.g. 100–150ms into fade-out)
        def start_fade_in():
            stacked_widget.setCurrentWidget(next_widget)
            fade_in.start()

        QTimer.singleShot(duration // 3, start_fade_in)  # e.g. 100ms into 300ms fade-out

        # keep both animations alive
        Animator.active_animations.extend([fade_out, fade_in])

        def cleanup():
            for anim in [fade_out, fade_in]:
                if anim in Animator.active_animations:
                    Animator.active_animations.remove(anim)

        fade_in.finished.connect(cleanup)
        fade_out.start()

    @staticmethod
    def animate_page_flip(current_widget, next_widget, animation_helper, callback=None):
        """
        Animate a page flip between two widgets using the provided animation helper.

        Args:
            current_widget (QWidget): The widget currently displayed
            next_widget (QWidget): The widget to flip to
            animation_helper (FlipAnimationHelper): Helper object for animations
            callback (callable): Optional callback when animation completes
        """
        # set up animation helper
        animation_helper.target_widget = current_widget
        duration = animation_helper.duration
        easing = animation_helper.easing_curve

        # create the flip animation
        flip_animation = QPropertyAnimation(animation_helper, b"rotation_y")
        flip_animation.setDuration(duration)
        flip_animation.setStartValue(0)
        flip_animation.setEndValue(180)
        flip_animation.setEasingCurve(easing)

        # fade animation if enabled
        fade_animation = None
        if animation_helper.fade_during_flip:
            fade_animation = QPropertyAnimation(animation_helper, b"opacity")
            fade_animation.setDuration(duration // 2)
            fade_animation.setStartValue(1.0)
            fade_animation.setEndValue(0.5)
            fade_animation.setEasingCurve(easing)

        # handle the flip midpoint (when to show next widget)
        def on_flip_midpoint():
            current_widget.hide()
            next_widget.show()
            animation_helper.target_widget = next_widget

            # start the second half of the animation
            second_half = QPropertyAnimation(animation_helper, b"rotation_y")
            second_half.setDuration(duration // 2)
            second_half.setStartValue(180)
            second_half.setEndValue(0)
            second_half.setEasingCurve(easing)

            # fade back in if enabled
            if fade_animation:
                fade_in = QPropertyAnimation(animation_helper, b"opacity")
                fade_in.setDuration(duration // 2)
                fade_in.setStartValue(0.5)
                fade_in.setEndValue(1.0)
                fade_in.setEasingCurve(easing)
                fade_in.start()
                Animator.active_animations.append(fade_in)

            # handle completion
            def on_complete():
                if callback:
                    callback()
                # clean up animations
                animations_to_remove = [flip_animation, second_half]
                if fade_animation:
                    animations_to_remove.extend([fade_animation])
                    if 'fade_in' in locals():
                        animations_to_remove.append(fade_in)
                for anim in animations_to_remove:
                    if anim in Animator.active_animations:
                        Animator.active_animations.remove(anim)

            second_half.finished.connect(on_complete)
            second_half.start()
            Animator.active_animations.append(second_half)

        # start the flip midpoint at halfway through
        QTimer.singleShot(duration // 2, on_flip_midpoint)

        # start animations
        flip_animation.start()
        if fade_animation:
            fade_animation.start()
            Animator.active_animations.append(fade_animation)

        Animator.active_animations.append(flip_animation)

    @staticmethod
    def create_flip_container(parent=None):
        """
        Create a new PageFlipContainer with default settings.

        Args:
            parent (QWidget): Parent widget

        Returns:
            PageFlipContainer: A new container ready for page flip animations
        """
        from app.style.animation.flip_animations import PageFlipContainer
        return PageFlipContainer(parent)

    @staticmethod
    def configure_flip_animation(container, **kwargs):
        """
        Configure flip animation settings on a PageFlipContainer.

        Args:
            container (PageFlipContainer): The container to configure
            **kwargs: Animation settings:
                - duration (int): Animation duration in milliseconds
                - easing (QEasingCurve): Easing curve
                - flip_axis (str): 'x' or 'y' for flip direction
                - fade_during_flip (bool): Whether to fade during flip
                - scale_during_flip (bool): Whether to scale during flip
        """
        if hasattr(container, 'configure_animation'):
            container.configure_animation(**kwargs)

    @staticmethod
    def animate_widget_flip(widget, duration=800, flip_axis='y', fade=True, scale=True, callback=None):
        """
        Animate a single widget flip (useful for refresh/reload animations).

        Args:
            widget (QWidget): Widget to animate
            duration (int): Animation duration in milliseconds
            flip_axis (str): 'x' or 'y' for flip direction
            fade (bool): Whether to fade during flip
            scale (bool): Whether to scale during flip
            callback (callable): Optional callback when animation completes
        """
        from app.style.animation.flip_animations import FlipAnimationHelper

        helper = FlipAnimationHelper(widget)
        helper.duration = duration
        helper.flip_axis = flip_axis
        helper.fade_during_flip = fade
        helper.scale_during_flip = scale

        # create animation
        animation = QPropertyAnimation(helper, b"rotation_y")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(360)  # full rotation
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        # handle completion
        def on_complete():
            if callback:
                callback()
            if animation in Animator.active_animations:
                Animator.active_animations.remove(animation)

        animation.finished.connect(on_complete)
        animation.start()
        Animator.active_animations.append(animation)
