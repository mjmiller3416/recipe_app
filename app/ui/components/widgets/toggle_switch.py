"""app/ui/components/inputs/toggle_switch.py

Custom toggle switch widget with smooth animations and Material Design styling.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from app.style import Theme
from app.style.theme.config import Qss


# ── Toggle Switch ───────────────────────────────────────────────────────────────────────────────────────────
class ToggleSwitch(QWidget):
    """
    A custom toggle switch widget with smooth animations.

    Emits:
        toggled(bool): When the switch state changes (True=on, False=off)
    """

    toggled = Signal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setObjectName("ToggleSwitch")

        # Register for component-specific styling
        Theme.register_widget(self, Qss.TOGGLE_SWITCH)

        # State management
        self._checked = checked
        self._sliderX = 5
        self.isHover = False
        self.isPressed = False

        # Size and geometry
        self.setFixedSize(42, 22)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Animation setup
        self._animation = QPropertyAnimation(self, b"sliderX")
        self._animation.setDuration(120)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

        # Initialize position based on checked state
        self._sliderX = 25 if checked else 5

        # Set property for QSS styling
        self.setProperty("checked", str(checked).lower())

    @Property(float)
    def sliderX(self):
        """Get the current slider position for animation."""
        return self._sliderX

    @sliderX.setter
    def sliderX(self, x):
        """Set the slider position and trigger repaint."""
        self._sliderX = max(x, 5)
        self.update()

    def isChecked(self) -> bool:
        """Returns True if the switch is in the 'on' position."""
        return self._checked

    def setChecked(self, checked: bool):
        """Sets the switch state without emitting the toggled signal."""
        if self._checked != checked:
            self._checked = checked
            self.setProperty("checked", str(checked).lower())
            self.style().unpolish(self)
            self.style().polish(self)
            self._animate_to_position()

    def toggle(self):
        """Toggles the switch state and emits the toggled signal."""
        self._checked = not self._checked
        self.setProperty("checked", str(self._checked).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self._animate_to_position()
        self.toggled.emit(self._checked)

    def _animate_to_position(self):
        """Animates the slider to the correct position based on checked state."""
        end_position = 25 if self._checked else 5

        self._animation.setStartValue(self._sliderX)
        self._animation.setEndValue(end_position)
        self._animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press to toggle the switch."""
        if event.button() == Qt.LeftButton:
            self.isPressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to toggle the switch."""
        if event.button() == Qt.LeftButton:
            self.isPressed = False
            self.toggle()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.isHover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave for hover effect."""
        self.isHover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Custom paint event to draw the toggle switch."""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        self._drawBackground(painter)
        self._drawCircle(painter)

    def _drawBackground(self, painter):
        """Draw the background track."""
        r = self.height() / 2
        painter.setPen(self._borderColor())
        painter.setBrush(self._backgroundColor())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), r, r)

    def _drawCircle(self, painter):
        """Draw the slider circle."""
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._sliderColor())
        painter.drawEllipse(int(self.sliderX), 5, 12, 12)

    def _backgroundColor(self):
        """Get background color based on state."""
        if self._checked:
            if not self.isEnabled():
                return QColor(255, 255, 255, 41)
            if self.isPressed:
                return self.palette().highlight().color().lighter(120)
            elif self.isHover:
                return self.palette().highlight().color().lighter(110)
            return self.palette().highlight().color()
        else:
            if not self.isEnabled():
                return QColor(0, 0, 0, 0)
            if self.isPressed:
                return QColor(255, 255, 255, 18)
            elif self.isHover:
                return QColor(255, 255, 255, 10)
            return QColor(0, 0, 0, 0)

    def _borderColor(self):
        """Get border color based on state."""
        if self._checked:
            return self._backgroundColor() if self.isEnabled() else QColor(0, 0, 0, 0)
        else:
            if self.isEnabled():
                return QColor(128, 128, 128, 153)
            return QColor(128, 128, 128, 56)

    def _sliderColor(self):
        """Get slider color based on state."""
        if self._checked:
            if self.isEnabled():
                return QColor(Qt.white)
            return QColor(255, 255, 255, 77)
        else:
            if self.isEnabled():
                return QColor(128, 128, 128, 201)
            return QColor(128, 128, 128, 96)
