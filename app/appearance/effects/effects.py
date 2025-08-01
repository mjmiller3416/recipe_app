"""app/appearance/effects/effects.py

Provides visual effects (shadows, glows, blurs, opacity) for QWidgets.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QGraphicsBlurEffect, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QWidget
)

from app.appearance.effects.config import Shadow, Glow


# ── Effects ──────────────────────────────────────────────────────────────────────────────────
class Effects:
    """
    A collection of QGraphicsEffect class methods to apply visual effects to QWidgets.
    """

    @classmethod
    def apply_shadow(
        cls,
        widget: QWidget,
        shadow: Shadow = Shadow.ELEVATION_1,
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
        _color = shadow.value.color
        _blur_radius = shadow.value.blur_radius
        _offset_x = shadow.value.offset_x
        _offset_y = shadow.value.offset_y

        shadow_effect = QGraphicsDropShadowEffect(widget)
        shadow_effect.setColor(_color)
        shadow_effect.setBlurRadius(_blur_radius)
        shadow_effect.setOffset(_offset_x, _offset_y)
        widget.setGraphicsEffect(shadow_effect)
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
    def apply_glow(
        cls,
        widget: QWidget,
        glow: Glow = Glow.PRIMARY,
    ) -> None:
        """
        Applies a "glow" effect to the given widget using QGraphicsDropShadowEffect.

        A glow is a shadow with zero offset, making it radiate from the center.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color of the glow.
            blur_radius (float): The blur radius of the glow.
        """
        _color = glow.value.color
        _blur_radius = glow.value.blur_radius

        glow_effect = QGraphicsDropShadowEffect(widget)
        glow_effect.setColor(_color)
        glow_effect.setBlurRadius(_blur_radius)

        # set offset to zero to create a centered glow
        glow_effect.setOffset(0, 0)

        widget.setGraphicsEffect(glow_effect)

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
