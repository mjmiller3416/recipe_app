"""app/appearance/animation/window_animator.py

This module provides the WindowAnimator class for animating window state changes.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import sys

from PySide6.QtCore import (QEasingCurve, QObject, QParallelAnimationGroup,
                            QPoint, QPropertyAnimation, QRect, QSize)
from PySide6.QtGui import QGuiApplication


# ── WindowAnimator ───────────────────────────────────────────────────────────────────────────
class WindowAnimator(QObject):
    """Handles animations for a QDialog, like maximize, restore, and minimize.

    This class provides methods to smoothly animate window transitions between
    different states (e.g., normal, maximized, minimized) using QPropertyAnimation.

    Attributes:
        window (QDialog): The window to be animated.
        duration (int): The duration of the animations in milliseconds.
        easing_curve (QEasingCurve.Type): The easing curve used for animations.
        animation_group (QParallelAnimationGroup | None): Manages currently running animations.
    """
    def __init__(self, window, duration=350):
        """Initializes the WindowAnimator.

        Args:
            window (QDialog): The QDialog instance to animate.
            duration (int, optional): The duration for animations in milliseconds.
                Defaults to 350.
        """
        super().__init__(window)
        self.window = window
        self.duration = duration
        self.easing_curve = QEasingCurve.InOutQuad
        self.animation_group = None # to manage running animations
        self._is_maximized = False

    def _stop_current_animation(self):
        """Stops any animation that is currently in progress."""
        if not self.animation_group:
            return
        if hasattr(self.animation_group, "state") and self.animation_group.state() == QPropertyAnimation.Running:
            self.animation_group.stop()
        self.animation_group = None  # force cleanup

    def animate_toggle_maximize(self):
        """Animates the window between maximized and normal (restored) states."""
        self._stop_current_animation()

        start_geometry = self.window.geometry()

        if not self._is_maximized:
            self.window._normal_geometry = start_geometry
            end_geometry = QGuiApplication.primaryScreen().availableGeometry()
        else:
            end_geometry = getattr(
                self.window, "_normal_geometry",
                QRect(QGuiApplication.primaryScreen().availableGeometry().center() - QPoint(400, 300), QSize(800, 600))
            )

        self.animation_group = QParallelAnimationGroup(self)

        geom_animation = QPropertyAnimation(self.window, b"geometry", self)
        geom_animation.setDuration(self.duration)
        geom_animation.setStartValue(start_geometry)
        geom_animation.setEndValue(end_geometry)
        geom_animation.setEasingCurve(self.easing_curve)

        self.animation_group.addAnimation(geom_animation)
        self.animation_group.finished.connect(self._on_maximize_finished)
        self.animation_group.start(QPropertyAnimation.DeleteWhenStopped)

    def _on_maximize_finished(self):
        """Finalizes state after maximize/restore animation completes."""
        self._is_maximized = not self._is_maximized
        self.window.title_bar.update_maximize_icon(self._is_maximized)
        self.animation_group = None

    def animate_minimize(self):
        """Minimize window using native Qt minimize (no custom animation).
        
        Custom geometry animations can conflict with FramelessWindow's window management,
        so we use the native minimize behavior instead.
        """
        self._stop_current_animation()  # Stop any running animations
        self.window.showMinimized()


