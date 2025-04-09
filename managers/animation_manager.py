"""
AnimationManager provides methods for fading widgets in and out using QPropertyAnimation.

Class Methods:
    - fade_widget: Fades a given widget from a specified start opacity to an end opacity.
    - transition_stack: Manages cross-fading between two stacked widgets.
 """

from qt_imports import QGraphicsOpacityEffect, QPropertyAnimation, QEasingCurve, QTimer, QParallelAnimationGroup

class AnimationManager:
    active_animations = []  # Store animations to prevent garbage collection

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
            widget.setVisible(True)  # Force visibility if hidden

        # ✅ Store effect on widget to prevent GC and reuse it
        if not hasattr(widget, "_fade_effect"):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            widget._fade_effect = effect  # Cache it on the widget
        else:
            effect = widget._fade_effect

        # 🧯 Safety check — set initial opacity directly before animating
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
        fade_out = AnimationManager.fade_widget(current_widget, duration, 1.0, 0.0)
        fade_in = AnimationManager.fade_widget(next_widget, duration, 0.0, 1.0)

        # Make sure fade-in is ready
        if not next_widget.isVisible():
            next_widget.setVisible(True)
        next_widget.repaint()

        # ⏱️ Delay fade-in just slightly (e.g. 100–150ms into fade-out)
        def start_fade_in():
            stacked_widget.setCurrentWidget(next_widget)
            fade_in.start()

        QTimer.singleShot(duration // 3, start_fade_in)  # e.g. 100ms into 300ms fade-out

        # Keep both animations alive
        AnimationManager.active_animations.extend([fade_out, fade_in])

        def cleanup():
            for anim in [fade_out, fade_in]:
                if anim in AnimationManager.active_animations:
                    AnimationManager.active_animations.remove(anim)

        fade_in.finished.connect(cleanup)
        fade_out.start()