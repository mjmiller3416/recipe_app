# File: app/ui/demo2.py

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMainWindow,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect,
    QGraphicsColorizeEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from enum import Enum, auto
import sys

# ── Widget Effects ───────────────────────────────────────────────────────────────────────────
class WidgetEffects:
    """
    A collection of QGraphicsEffect class methods to apply visual effects to QWidgets.
    """

    @classmethod
    def apply_shadow(
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


# ── Enums for styling properties ─────────────────────────────────────────────────────────────
class WidgetType(Enum):
    CARD = auto()

class FontType(Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()

class Theme(Enum):
    LIGHT = auto()
    DARK = auto()

class State(Enum):
    NORMAL = auto()
    DISABLED = auto()
    ACTIVE = auto()


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
    def __init__(self, title: str = "", body: str = "", footer: str = "Footer", parent=None):
        super().__init__(parent)
        self.setType(WidgetType.CARD)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(12, 12, 12, 12)

        self.header = StyledLabel(title)
        self.header.setFontType(FontType.HEADER)

        self.body = StyledLabel(body)
        self.body.setFontType(FontType.BODY)
        self.body.setWordWrap(True)

        self.footer = StyledLabel(footer)
        self.footer.setFontType(FontType.FOOTER)

        layout.addWidget(self.header)
        layout.addWidget(self.body)
        layout.addWidget(self.footer)


# ── Main Window ──────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Styled Card Example")

        card = CardWidget(
            title="Regular Card",
            body="This is a regular card without any effects applied.",
            footer="~ Powered by PySide6 ~"
        )

        card2 = CardWidget(
            title="Shadow Example",
            body="This card has a drop shadow effect applied.",
            footer="~ Powered by PySide6 ~"
        )
        WidgetEffects.apply_shadow(card2, blur_radius=20.0, offset_x=5.0, offset_y=5.0)

        card3 = CardWidget(
            title="Blur Example",
            body="This card has a blur effect applied.",
            footer="~ Powered by PySide6 ~"
        )
        WidgetEffects.apply_blur(card3, blur_radius=5.0)

        card4 = CardWidget(
            title="Opacity Example",
            body="This card has an opacity effect applied.",
            footer="~ Powered by PySide6 ~"
        )
        WidgetEffects.apply_opacity(card4, opacity=0.7)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(card)
        layout.addWidget(card2)
        layout.addWidget(card3)
        layout.addWidget(card4)
        layout.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(container)
        self.setMinimumSize(400, 200)

        # Apply styles
        self.setStyleSheet(qss)

# ── QSS Styling ──
qss = """
QMainWindow { background-color: #ff0000; }

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
    background-color: #1fdbb9;
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
