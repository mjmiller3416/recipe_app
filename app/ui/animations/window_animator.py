"""
This module provides the WindowAnimator class for animating window state changes.
"""
from PySide6.QtCore import (QEasingCurve, QObject, QParallelAnimationGroup,
                            QPoint, QPropertyAnimation, QRect, QSize)
from PySide6.QtGui import QGuiApplication

from app.core.utils.platform_utils import get_taskbar_rect


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

    def _stop_current_animation(self):
        """Stops any animation that is currently in progress."""
        if self.animation_group and self.animation_group.state() == QPropertyAnimation.Running:
            self.animation_group.stop()

    def animate_toggle_maximize(self):
        """Animates the window between maximized and normal (restored) states."""
        self._stop_current_animation() # prevent animation conflicts

        start_geometry = self.window.geometry()
        
        if not self.window._is_maximized:
            self.window._normal_geometry = start_geometry
            end_geometry = QGuiApplication.primaryScreen().availableGeometry()
        else:
            # use saved normal geometry or a default centered one
            end_geometry = getattr(self.window, "_normal_geometry", 
                                   QRect(QGuiApplication.primaryScreen().availableGeometry().center() - QPoint(400, 300), 
                                         QSize(800, 600)))

        # use a single animation group for consistency
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
        self.window._is_maximized = not self.window._is_maximized
        self.window.title_bar.update_maximize_icon(self.window._is_maximized)
        self.animation_group = None

    def animate_minimize(self):
        """Animates the window shrinking to the taskbar.

        The window fades out and shrinks towards the center of the taskbar
        or the bottom center of the screen if taskbar information is unavailable.
        """
        self._stop_current_animation() # Prevent animation conflicts

        # capture the starting geometry
        start_geometry = self.window.geometry()
        
        # calculate the target position (taskbar center or screen bottom center)
        screen_rect = QGuiApplication.primaryScreen().availableGeometry()
        target_x = screen_rect.center().x()
        target_y = screen_rect.bottom() # Default target Y
        
        taskbar_coords = get_taskbar_rect()
        if taskbar_coords:
            taskbar_rect = QRect(QPoint(taskbar_coords[0], taskbar_coords[1]), QPoint(taskbar_coords[2], taskbar_coords[3]))
            target_y = taskbar_rect.center().y()
            
        # the animation ends with a zero-sized rectangle at the target
        end_geometry = QRect(target_x, target_y, 0, 0)

        # animation group to handle multiple properties
        self.animation_group = QParallelAnimationGroup(self)

        # geometry Animation
        geom_anim = QPropertyAnimation(self.window, b"geometry")
        geom_anim.setStartValue(start_geometry)
        geom_anim.setEndValue(end_geometry)
        geom_anim.setEasingCurve(self.easing_curve)
        geom_anim.setDuration(self.duration)
        
        # opacity Animation
        opacity_anim = QPropertyAnimation(self.window, b"windowOpacity")
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(QEasingCurve.InQuad) # Fade out quickly
        opacity_anim.setDuration(self.duration)

        self.animation_group.addAnimation(geom_anim)
        self.animation_group.addAnimation(opacity_anim)
        
        self.animation_group.finished.connect(
            lambda: self._on_minimize_finished(start_geometry)
        )
        self.animation_group.start(QPropertyAnimation.DeleteWhenStopped)

    def _on_minimize_finished(self, original_geometry: QRect):
        """Finalizes state after minimize animation completes.

        Hides the window, resets its opacity and geometry to their pre-animation
        values, and then shows the window in a minimized state.

        Args:
            original_geometry (QRect): The geometry of the window before the
                minimize animation started.
        """
        self.window.showMinimized()
        # reset properties now that it's hidden
        self.window.setWindowOpacity(1.0)
        self.window.setGeometry(original_geometry)
        self.animation_group = None