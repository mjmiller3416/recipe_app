"""app/ui/components/widgets/toast.py

A reusable toast notification component that displays temporary messages
with smooth animations. Supports success/error states and customizable positioning.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget

from app.style import Theme
from app.style.theme.config import Qss


# ── Toast Notification ──────────────────────────────────────────────────────────────────────────────────────
class Toast(QLabel):
    """A toast notification widget that appears and disappears with animations."""

    def __init__(self, message: str, parent: QWidget, success: bool = True):
        """Initialize the toast notification.

        Args:
            message: The message to display
            parent: The parent widget
            success: True for success styling, False for error styling
        """
        super().__init__(message, parent)
        self.setObjectName("Toast")
        #self.setWordWrap(True)

        # Set success property for QSS styling
        self.setProperty("success", "true" if success else "false")

        # Register with theme manager for styling
        Theme.register_widget(self, Qss.TOAST)

        # Configure font
        self._setup_font()

        # Animation properties
        self.drop_animation: QPropertyAnimation = None
        self.hide_animation: QPropertyAnimation = None


    def _setup_font(self):
        """Configure the toast font."""
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)

    def show_toast(self, duration: int = 3000, offset_right: int = 50):
        """Show the toast with drop-down animation.

        Args:
            duration: How long to show the toast in milliseconds (default: 3000)
            offset_right: Pixels to offset from center to the right (default: 50)
        """
        # Calculate size and position
        self.adjustSize()
        parent_width = self.parent().width()

        # Use actual width needed for text, with reasonable max based on parent width
        max_toast_width = min(parent_width - 100, 600)  # Leave 50px margin on each side, max 600px
        toast_width = min(max_toast_width, self.width())
        toast_height = self.height()

        # Position: slightly right of center, starting above the window
        x_pos = (parent_width // 2) + offset_right - (toast_width // 2)
        start_y = -toast_height  # Start above window
        end_y = 20  # Drop down to 20px from top

        # Set initial position (hidden above window)
        self.setGeometry(x_pos, start_y, toast_width, toast_height)
        super().show()  # Call QLabel's show method

        # Create drop-down animation
        self.drop_animation = QPropertyAnimation(self, b"geometry")
        self.drop_animation.setDuration(300)  # 300ms animation
        self.drop_animation.setStartValue(QRect(x_pos, start_y, toast_width, toast_height))
        self.drop_animation.setEndValue(QRect(x_pos, end_y, toast_width, toast_height))
        self.drop_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Create slide-up animation (for hiding)
        self.hide_animation = QPropertyAnimation(self, b"geometry")
        self.hide_animation.setDuration(250)  # 250ms hide animation
        self.hide_animation.setStartValue(QRect(x_pos, end_y, toast_width, toast_height))
        self.hide_animation.setEndValue(QRect(x_pos, start_y, toast_width, toast_height))
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # Clean up after hide animation
        self.hide_animation.finished.connect(self.deleteLater)

        # Start the drop-down animation
        self.drop_animation.start()

        # Auto-hide after specified duration
        QTimer.singleShot(duration, self._start_hide_animation)

    def _start_hide_animation(self):
        """Start the hide animation."""
        if self.hide_animation:
            self.hide_animation.start()


# ── Convenience Function ────────────────────────────────────────────────────────────────────────────────────
def show_toast(
        parent: QWidget,
        message: str,
        success: bool = True,
        duration: int = 3000,
        offset_right: int = 50
) -> None:
    """Convenience function to show a toast notification.

    Args:
        parent: The parent widget to show the toast on
        message: The message to display
        success: True for success styling, False for error styling
        duration: How long to show the toast in milliseconds
        offset_right: Pixels to offset from center to the right
    """
    toast = Toast(message, parent, success)
    toast.show_toast(duration, offset_right)
