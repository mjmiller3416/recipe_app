"""app/ui/animations/widget_effects.py

Provides utility functions to apply QGraphicsEffects to QWidgets.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QWidget, QGraphicsDropShadowEffect, QGraphicsBlurEffect,
    QGraphicsColorizeEffect, QGraphicsOpacityEffect
)
from PySide6.QtGui import QColor


# ── Widget Effects ───────────────────────────────────────────────────────────────────────────
class WidgetEffects:
    """
    A collection of QGraphicsEffect class methods to apply visual effects to QWidgets.
    """

    @classmethod
    def apply_drop_shadow(
        cls,
        widget: QWidget,
        color: QColor = QColor(0, 0, 0, 150),
        blur_radius: float = 15.0,
        offset_x: float = 3.0,
        offset_y: float = 3.0
    ) -> None:
        """
        Applies a QGraphicsDropShadowEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color of the shadow. Default is semi-transparent black.
            blur_radius (float): The blur radius of the shadow.
            offset_x (float): The horizontal offset of the shadow.
            offset_y (float): The vertical offset of the shadow.
        """
        shadow_effect = QGraphicsDropShadowEffect(widget)
        shadow_effect.setColor(color)
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setOffset(offset_x, offset_y)
        widget.setGraphicsEffect(shadow_effect)
        widget.update()
        print(f"Applied Drop Shadow to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def apply_blur(cls, widget: QWidget, blur_radius: float = 10.0):
        """
        Applies a QGraphicsBlurEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            blur_radius (float): The blur radius of the effect.
        """
        blur_effect = QGraphicsBlurEffect(widget)
        blur_effect.setBlurRadius(blur_radius)
        widget.setGraphicsEffect(blur_effect)
        widget.update()
        print(f"Applied Blur to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def apply_colorize(
        cls, widget: QWidget,
        color: QColor = QColor(255, 0, 0, 100),
        strength: float = 0.5
    ) -> None:
        """
        Applies a QGraphicsColorizeEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color to tint the widget with. Default is semi-transparent red.
            strength (float): The strength of the colorization (0.0 to 1.0).
        """
        colorize_effect = QGraphicsColorizeEffect(widget)
        colorize_effect.setColor(color)
        colorize_effect.setStrength(strength)
        widget.setGraphicsEffect(colorize_effect)
        widget.update()
        print(f"Applied Colorize to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def apply_opacity(cls, widget: QWidget, opacity: float = 0.5):
        """
        Applies a QGraphicsOpacityEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            opacity (float): Opacity level
                (0.0 for fully transparent, 1.0 for fully opaque).
        """
        opacity_effect = QGraphicsOpacityEffect(widget)
        opacity_effect.setOpacity(opacity)
        widget.setGraphicsEffect(opacity_effect)
        widget.update()
        print(f"Applied Opacity to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def clear_effect(cls, widget: QWidget):
        """
        Clears any QGraphicsEffect applied to the given widget.

        Args:
            widget (QWidget): The widget to clear the effect from.
        """
        widget.setGraphicsEffect(None)
        widget.update()
        print(f"Cleared effect from "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )
