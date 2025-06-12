"""
This module provides the WindowAnimator class for animating window state changes.
"""
from PySide6.QtCore import (
    QPropertyAnimation,
    QVariantAnimation,
    QEasingCurve,
    QRect,
    QPoint,
    QObject,
)
from PySide6.QtGui import QGuiApplication

from ui.helpers.platform_utils import get_taskbar_rect


def lerp(a, b, t):
    """Linearly interpolate between two values."""
    return a + (b - a) * t


class WindowAnimator(QObject):
    """
    Handles the animations for a QDialog, including maximizing, restoring,
    and minimizing effects.
    """
    def __init__(self, window, duration=350):
        super().__init__(window)
        self.window = window
        self.duration = duration
        self.easing_curve = QEasingCurve.InOutQuad

    # --- animate_toggle_maximize and _on_maximize_finished remain the same ---
    def animate_toggle_maximize(self):
        start_geometry = self.window.geometry()
        if not self.window._is_maximized:
            self.window._normal_geometry = start_geometry
            end_geometry = QGuiApplication.primaryScreen().availableGeometry()
        else:
            if hasattr(self.window, "_normal_geometry"):
                end_geometry = self.window._normal_geometry
            else:
                screen = QGuiApplication.primaryScreen().availableGeometry()
                end_geometry = QRect(screen.center().x() - 400, screen.center().y() - 300, 800, 600)
        self.geom_animation = QPropertyAnimation(self.window, b"geometry", self)
        self.geom_animation.setDuration(self.duration)
        self.geom_animation.setStartValue(start_geometry)
        self.geom_animation.setEndValue(end_geometry)
        self.geom_animation.setEasingCurve(self.easing_curve)
        self.geom_animation.finished.connect(self._on_maximize_finished)
        self.geom_animation.start(QPropertyAnimation.DeleteWhenStopped)

    def _on_maximize_finished(self):
        self.window._is_maximized = not self.window._is_maximized
        self.window.title_bar.update_maximize_icon(self.window._is_maximized)

    # --- This is the updated minimize animation method ---
    def animate_minimize(self):
        """
        Animates the window shrinking towards a fixed point at the
        bottom-center of the screen.
        """
        # --- Define Start and End States ---
        self.start_geometry = self.window.geometry()
        start_center_pos = self.start_geometry.center()
        
        # --- NEW: Calculate the FIXED screen-center target ---
        # Get the available screen geometry (the area not covered by taskbars)
        screen_rect = QGuiApplication.primaryScreen().availableGeometry()
        
        # The target's X coordinate is now always the horizontal center of the screen.
        target_x = screen_rect.center().x()
        
        # The target's Y coordinate is the bottom of the screen, or preferably,
        # the taskbar's vertical center for better accuracy.
        target_y = screen_rect.bottom()
        taskbar_coords = get_taskbar_rect()
        if taskbar_coords:
            left, top, right, bottom = taskbar_coords
            taskbar_rect = QRect(left, top, right - left, bottom - top)
            target_y = taskbar_rect.center().y()
        
        # This is our new fixed target position.
        end_target_pos = QPoint(target_x, target_y)

        # --- The rest of the animation logic is unchanged ---
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(self.easing_curve)
        self.anim.setDuration(self.duration)

        self.anim.valueChanged.connect(
            lambda p: self._update_minimize_frame(p, self.start_geometry, start_center_pos, end_target_pos)
        )
        self.anim.finished.connect(
            lambda: self._on_minimize_finished(self.start_geometry)
        )
        self.anim.start(QVariantAnimation.DeleteWhenStopped)

    def _update_minimize_frame(self, progress: float, start_geom: QRect, start_pos: QPoint, end_pos: QPoint):
        """
        Calculates and sets the window geometry/opacity for a single frame.
        """
        current_center_x = lerp(start_pos.x(), end_pos.x(), progress)
        current_center_y = lerp(start_pos.y(), end_pos.y(), progress)

        scale_factor = 1.0 - progress
        warp_factor = 1.0 - pow(progress, 0.5)
        current_w = start_geom.width() * warp_factor
        current_h = start_geom.height() * scale_factor

        top_left_x = current_center_x - current_w / 2
        top_left_y = current_center_y - current_h / 2

        current_opacity = 1.0 - pow(progress, 3)

        self.window.setGeometry(int(top_left_x), int(top_left_y), int(current_w), int(current_h))
        self.window.setWindowOpacity(current_opacity)

    def _on_minimize_finished(self, original_geometry: QRect):
        self.window.showMinimized()
        self.window.setWindowOpacity(1.0)
        self.window.setGeometry(original_geometry)