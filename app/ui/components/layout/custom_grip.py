"""app/ui/components/layout/custom_grip.py

Tool for creating custom grips on a window for resizing functionality.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


# ── Class Definition ────────────────────────────────────────────────────────────
class CustomGrip(QWidget):
    """A custom, invisible widget for resizing from window edges and corners.

    Attributes:
        parent_widget (QWidget): The parent window this grip belongs to.
        position (str): The position of the grip (e.g., "top", "bottom_left").
        grip_size (int): The thickness of the grip area.
        mouse_press_pos (QPoint | None): The global mouse position when a drag starts.
    """

    def __init__(self, parent, position: str):
        """Initializes the CustomGrip.

        Args:
            parent (QWidget): The parent widget (the window to be resized).
            position (str): A string indicating the grip's position
                (e.g., "top", "bottom_left").
        """
        super().__init__(parent)
        # ── Properties ──
        self.parent_widget = parent
        self.position = position
        self.grip_size = 8
        self.setStyleSheet("background-color: transparent;")

        # ── Cursor Setup ──
        cursors = {
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top_left": Qt.SizeFDiagCursor,
            "top_right": Qt.SizeBDiagCursor,
            "bottom_left": Qt.SizeBDiagCursor,
            "bottom_right": Qt.SizeFDiagCursor,
        }
        self.setCursor(cursors.get(self.position, Qt.ArrowCursor))
        self.mouse_press_pos = None

    def mousePressEvent(self, event):
        """Records mouse position and window geometry on left-button press.

        This prepares for a resize operation.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos() 
            self.parent_widget.start_geometry = self.parent_widget.geometry()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Resizes the parent window based on mouse movement.

        Calculates the change in mouse position and instructs the parent
        window to resize accordingly.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.mouse_press_pos is not None:
            delta = event.globalPos() - self.mouse_press_pos
            self.parent_widget.resize_from_grip(self.position, delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Resets the stored mouse position on button release.

        This ends the resize operation.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        self.mouse_press_pos = None
        super().mouseReleaseEvent(event)