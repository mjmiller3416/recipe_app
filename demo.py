import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect, QGraphicsColorizeEffect,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QSize

class WidgetEffects:
    """
    A collection of QGraphicsEffect class methods to apply visual effects to QWidgets.
    """

    @classmethod
    def apply_drop_shadow(cls, widget: QWidget, color: QColor = QColor(0, 0, 0, 150),
                          blur_radius: float = 15.0, offset_x: float = 3.0, offset_y: float = 3.0):
        """
        Applies a QGraphicsDropShadowEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color of the shadow. Default is semi-transparent black.
            blur_radius (float): The blur radius of the shadow.
            offset_x (float): The horizontal offset of the shadow.
            offset_y (float): The vertical offset of the shadow.
        """
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(color)
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setOffset(offset_x, offset_y)
        widget.setGraphicsEffect(shadow_effect)
        widget.update() # Explicitly request a repaint
        print(f"Applied Drop Shadow to {widget.objectName() if widget.objectName() else widget.__class__.__name__}")

    @classmethod
    def apply_blur(cls, widget: QWidget, blur_radius: float = 10.0):
        """
        Applies a QGraphicsBlurEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            blur_radius (float): The blur radius of the effect.
        """
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(blur_radius)
        widget.setGraphicsEffect(blur_effect)
        widget.update() # Explicitly request a repaint
        print(f"Applied Blur to {widget.objectName() if widget.objectName() else widget.__class__.__name__}")

    @classmethod
    def apply_colorize(cls, widget: QWidget, color: QColor = QColor(255, 0, 0, 100), strength: float = 0.5):
        """
        Applies a QGraphicsColorizeEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color to tint the widget with. Default is semi-transparent red.
            strength (float): The strength of the colorization (0.0 to 1.0).
        """
        colorize_effect = QGraphicsColorizeEffect()
        colorize_effect.setColor(color)
        colorize_effect.setStrength(strength)
        widget.setGraphicsEffect(colorize_effect)
        widget.update() # Explicitly request a repaint
        print(f"Applied Colorize to {widget.objectName() if widget.objectName() else widget.__class__.__name__}")

    @classmethod
    def apply_opacity(cls, widget: QWidget, opacity: float = 0.5):
        """
        Applies a QGraphicsOpacityEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            opacity (float): The opacity level (0.0 for fully transparent, 1.0 for fully opaque).
        """
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(opacity)
        widget.setGraphicsEffect(opacity_effect)
        widget.update() # Explicitly request a repaint
        print(f"Applied Opacity to {widget.objectName() if widget.objectName() else widget.__class__.__name__}")

    @classmethod
    def clear_effect(cls, widget: QWidget):
        """
        Clears any QGraphicsEffect applied to the given widget.

        Args:
            widget (QWidget): The widget to clear the effect from.
        """
        widget.setGraphicsEffect(None)
        widget.update() # Explicitly request a repaint
        print(f"Cleared effect from {widget.objectName() if widget.objectName() else widget.__class__.__name__}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Widget Effects Demo")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Create a label to demonstrate effects
        self.effect_label = QLabel("Hello, PySide6 Effects!")
        self.effect_label.setObjectName("EffectLabel")
        self.effect_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.effect_label.setStyleSheet("background-color: #87CEEB; padding: 20px; border-radius: 10px; color: #000080; border: 2px solid #4682B4;")
        self.effect_label.setAlignment(Qt.AlignCenter)
        self.effect_label.setFixedSize(QSize(350, 120)) # Slightly larger for better effect visibility
        layout.addWidget(self.effect_label, alignment=Qt.AlignCenter)

        # Buttons to apply effects
        btn_shadow = QPushButton("Apply Drop Shadow")
        btn_shadow.clicked.connect(lambda: WidgetEffects.apply_drop_shadow(self.effect_label))
        layout.addWidget(btn_shadow)

        btn_blur = QPushButton("Apply Blur")
        btn_blur.clicked.connect(lambda: WidgetEffects.apply_blur(self.effect_label))
        layout.addWidget(btn_blur)

        btn_colorize = QPushButton("Apply Colorize (Red)")
        btn_colorize.clicked.connect(lambda: WidgetEffects.apply_colorize(self.effect_label, QColor(255, 0, 0, 100), 0.6))
        layout.addWidget(btn_colorize)

        btn_opacity = QPushButton("Apply Opacity (50%)")
        btn_opacity.clicked.connect(lambda: WidgetEffects.apply_opacity(self.effect_label, 0.5))
        layout.addWidget(btn_opacity)

        btn_clear = QPushButton("Clear Effect")
        btn_clear.clicked.connect(lambda: WidgetEffects.clear_effect(self.effect_label))
        layout.addWidget(btn_clear)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
