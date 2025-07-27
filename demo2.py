# File: app/ui/demo2.py

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import sys
from collections import namedtuple
from enum import Enum, auto

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QGraphicsBlurEffect,
                               QGraphicsDropShadowEffect,
                               QGraphicsOpacityEffect, QGridLayout, QLabel,
                               QMainWindow, QVBoxLayout, QWidget)

# ── Shadow Effect Enum ───────────────────────────────────────────────────────────────────────
ShadowStyle = namedtuple("ShadowStyle", "color blur_radius offset_x offset_y")

class Shadow(Enum):
    """
    Predefined shadow styles for elevation effects.

    - ELEVATION_0: No shadow, flat appearance.
    - ELEVATION_1: Subtle shadow for resting cards.
    - ELEVATION_3: More pronounced shadow for hover/active states.
    - ELEVATION_6: Stronger shadow for floating cards.
    - ELEVATION_12: Heaviest shadow for dialogs/modals.
    """
    ELEVATION_0 = ShadowStyle(QColor(0, 0, 0, 0), 0.0, 0.0, 0.0)
    ELEVATION_1 = ShadowStyle(QColor(0, 0, 0, 40), 8.0, 0.0, 2.0)
    ELEVATION_3 = ShadowStyle(QColor(0, 0, 0, 60), 12.0, 0.0, 4.0)
    ELEVATION_6 = ShadowStyle(QColor(0, 0, 0, 80), 16.0, 0.0, 6.0)
    ELEVATION_12 = ShadowStyle(QColor(0, 0, 0, 100), 24.0, 0.0, 8.0)


# ── Glow Effect Enum ─────────────────────────────────────────────────────────────────────────
GlowStyle = namedtuple("GlowStyle", "color blur_radius")

class Glow(Enum):
    CYAN = GlowStyle(QColor(0, 255, 255, 200), 60.0)
    PINK = GlowStyle(QColor(255, 0, 255, 220), 50.0)
    GOLD = GlowStyle(QColor(255, 215, 0, 180), 40.0)
    ERROR = GlowStyle(QColor(255, 0, 0, 150), 30.0)
    PRIMARY = GlowStyle(QColor(100, 149, 237, 180), 45.0)  # Cornflower Blue-ish


# ── Widget Effects ───────────────────────────────────────────────────────────────────────────
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


# ── Enums for styling properties ─────────────────────────────────────────────────────────────
class WidgetType(Enum):
    CARD = auto()

class FontType(Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()


# ── StyledWidget Base Class ──────────────────────────────────────────────────────────────────
class StyledWidget(QWidget):
    def setType(self, widget_type: WidgetType):
        self.setProperty("widgetType", widget_type.name)
        return self

class StyledLabel(QLabel):
    def setFontType(self, font_type: FontType):
        self.setProperty("fontType", font_type.name)
        return self

# ── Custom CardWidget ────────────────────────────────────────────────────────────────────────
class CardWidget(StyledWidget):
    def __init__(self, title: str = "", body: str = "", footer: str = "", parent=None):
        super().__init__(parent)
        self.setType(WidgetType.CARD)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(100)
        self.setMinimumWidth(150)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(12, 12, 12, 12)

        self.header = StyledLabel(title)
        self.header.setFontType(FontType.HEADER)

        self.body = StyledLabel(body)
        self.body.setFontType(FontType.BODY)
        self.body.setWordWrap(False)

        self.footer = StyledLabel(footer)
        self.footer.setFontType(FontType.FOOTER)

        self._layout.addWidget(self.header)
        self._layout.addWidget(self.body)
        self._layout.addWidget(self.footer)

    def setContentsMargins(self, left: int, top: int, right: int, bottom: int) -> None:
        """
        Override setContentsMargins to control the internal layout margins.
        """
        self._layout.setContentsMargins(left, top, right, bottom)


# ── Main Window ──────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Styled Card Example")

        card = CardWidget(title="Primary")
        Effects.apply_shadow(card, Shadow.ELEVATION_6)
        card.setType(WidgetType.CARD)
        card2 = CardWidget(title="Secondary")
        card2.setType(WidgetType.CARD)
        card3 = CardWidget(title="Tertiary")
        card3.setType(WidgetType.CARD)

        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(30)  # Add space between cards for glow effects
        layout.setContentsMargins(40, 40, 40, 40)  # Add margins for glow effects
        layout.addWidget(card, 0, 0)
        layout.addWidget(card2, 0, 1)
        layout.addWidget(card3, 0, 2)
        layout.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(container)
        self.setMinimumSize(400, 200)

        # Apply styles
        self.setStyleSheet(qss)

# ── QSS Styling ──
qss = """
QMainWindow { background-color: #585858; }

/* Base Card Styling */
CardWidget[widgetType="CARD"] {
    background-color: #242424;
    border-radius: 12px;
    border: 1px solid #444;
}

/* Header */
[fontType="HEADER"] {
    font-size: 18px;
    font-weight: bold;
    padding-bottom: 8px;
    color: #FFD700; /* Gold color for header text */
}

/* Body */
[fontType="BODY"] {
    font-size: 14px;
    padding: 4px 0;
    color: #DDD;
}

/* Footer */
[fontType="FOOTER"] {
    font-size: 12px;
    color: gray;
    padding-top: 8px;
}
"""

# ── Entry Point ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
