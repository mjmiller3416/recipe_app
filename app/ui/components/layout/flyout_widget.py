"""app/ui/components/widgets/flyout_widget.py

Defines a FlyoutWidget that overlays content with flexible anchoring options
and slide-in/out animations in four directions.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Union

from PySide6.QtCore import QEvent, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (QApplication, QFrame, QMainWindow, QVBoxLayout,
                               QWidget)

from _dev_tools import DebugLogger
from app.style.animation.animator import Animator


# ── FlyoutWidget ─────────────────────────────────────────────────────────────────────────────
class FlyoutWidget(QFrame):
    """Overlay widget that slides in/out with flexible anchoring options."""
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

    # Anchor modes
    ANCHOR_WIDGET = "widget"
    ANCHOR_POINT = "point"
    ANCHOR_EDGE = "edge"
    ANCHOR_CUSTOM = "custom"

    # Edge constants for edge anchoring
    EDGE_LEFT = "left"
    EDGE_RIGHT = "right"
    EDGE_TOP = "top"
    EDGE_BOTTOM = "bottom"

    def __init__(
        self,
        anchor: Union[QWidget, QPoint, str, dict] = None,
        direction: int = RIGHT,
        content: QWidget = None,
        parent: QWidget = None,
        duration: int = 300,
        margin: int = 5,
        anchor_mode: str = None,
    ):
        """
        Initialize FlyoutWidget with flexible anchoring options.

        Args:
            anchor: Anchor reference - can be:
                - QWidget: Traditional widget anchoring
                - QPoint: Specific coordinate point
                - str: Edge name ("left", "right", "top", "bottom")
                - dict: Custom positioning with start/end points
            direction: Animation direction (TOP, RIGHT, BOTTOM, LEFT)
            content: Widget to display in flyout
            parent: Parent widget (auto-detected if None)
            duration: Animation duration in milliseconds
            margin: Distance from anchor point
            anchor_mode: Force specific anchor mode or auto-detect
        """
        # Auto-detect anchor mode if not specified
        if anchor_mode is None:
            anchor_mode = self._detect_anchor_mode(anchor)

        # Determine parent widget
        if parent is None:
            if anchor_mode == self.ANCHOR_WIDGET and isinstance(anchor, QWidget):
                parent = anchor.window()
            else:
                # Use the active window or main window
                parent = QApplication.activeWindow() or QApplication.topLevelWidgets()[0]

        super().__init__(parent, Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("FlyoutWidget")

        # Store configuration
        self.anchor = anchor
        self.anchor_mode = anchor_mode
        self.direction = direction
        self.duration = duration
        self.margin = margin

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if content:
            layout.addWidget(content)
        self.setLayout(layout)

        # State tracking
        self._visible = False
        self._animation = None

    def _detect_anchor_mode(self, anchor) -> str:
        """Auto-detect the appropriate anchor mode based on anchor type."""
        if isinstance(anchor, QWidget):
            return self.ANCHOR_WIDGET
        elif isinstance(anchor, QPoint):
            return self.ANCHOR_POINT
        elif isinstance(anchor, str):
            return self.ANCHOR_EDGE
        elif isinstance(anchor, dict):
            return self.ANCHOR_CUSTOM
        else:
            raise ValueError(f"Unsupported anchor type: {type(anchor)}")

    def set_anchor(self, anchor, anchor_mode: str = None):
        """Update the anchor and optionally the anchor mode."""
        if anchor_mode is None:
            anchor_mode = self._detect_anchor_mode(anchor)

        self.anchor = anchor
        self.anchor_mode = anchor_mode

    def toggle_flyout(self):
        """Toggle flyout visibility with animation."""
        self.setVisibleAnimated(not self._visible)

    def setVisibleAnimated(self, visible: bool):
        """Animate the flyout showing or hiding based on anchor configuration."""
        if visible == self._visible:
            return
        self._visible = visible

        self.adjustSize()
        w = self.width()
        h = self.height()

        # Calculate positions based on anchor mode
        start, end = self._calculate_positions(w, h)

        if visible:
            self.move(start)
            self.show()
            self._animation = Animator.animate_pos(self, start, end, self.duration)
        else:
            anim = Animator.animate_pos(self, end, start, self.duration)
            anim.finished.connect(self.hide)

    def _calculate_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate start and end positions based on anchor mode and direction."""
        if self.anchor_mode == self.ANCHOR_WIDGET:
            return self._calculate_widget_positions(width, height)
        elif self.anchor_mode == self.ANCHOR_POINT:
            return self._calculate_point_positions(width, height)
        elif self.anchor_mode == self.ANCHOR_EDGE:
            return self._calculate_edge_positions(width, height)
        elif self.anchor_mode == self.ANCHOR_CUSTOM:
            return self._calculate_custom_positions(width, height)
        else:
            raise ValueError(f"Unknown anchor mode: {self.anchor_mode}")

    def _calculate_widget_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate positions for widget-based anchoring."""
        # Get the anchor widget's global position correctly
        anchor_global_pos = self.anchor.mapToGlobal(QPoint(0, 0))
        anchor_size = self.anchor.size()
        anchor_global = QRect(anchor_global_pos, anchor_size)

        if self.direction == self.RIGHT:
            end_x = anchor_global.right() + self.margin
            end_y = anchor_global.top()
            start = QPoint(end_x + width, end_y)
            end = QPoint(end_x, end_y)
        elif self.direction == self.LEFT:
            end_x = anchor_global.left() - width - self.margin
            end_y = anchor_global.top()
            start = QPoint(end_x - width, end_y)
            end = QPoint(end_x, end_y)
        elif self.direction == self.BOTTOM:
            end_x = anchor_global.left()
            end_y = anchor_global.bottom() + self.margin
            start = QPoint(end_x, end_y + height)
            end = QPoint(end_x, end_y)
        else:  # TOP
            end_x = anchor_global.left()
            end_y = anchor_global.top() - height - self.margin
            start = QPoint(end_x, end_y - height)
            end = QPoint(end_x, end_y)

        return start, end

    def _calculate_point_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate positions for point-based anchoring."""
        anchor_point = self.anchor

        if self.direction == self.RIGHT:
            end_x = anchor_point.x() + self.margin
            end_y = anchor_point.y()
            start = QPoint(end_x + width, end_y)
            end = QPoint(end_x, end_y)
        elif self.direction == self.LEFT:
            end_x = anchor_point.x() - width - self.margin
            end_y = anchor_point.y()
            start = QPoint(end_x - width, end_y)
            end = QPoint(end_x, end_y)
        elif self.direction == self.BOTTOM:
            end_x = anchor_point.x()
            end_y = anchor_point.y() + self.margin
            start = QPoint(end_x, end_y + height)
            end = QPoint(end_x, end_y)
        else:  # TOP
            end_x = anchor_point.x()
            end_y = anchor_point.y() - height - self.margin
            start = QPoint(end_x, end_y - height)
            end = QPoint(end_x, end_y)

        return start, end

    def _calculate_edge_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate positions for edge-based anchoring (off-screen sliding)."""
        # Always use the application window as the reference for edge anchoring
        app_window = self._get_application_window()

        if app_window:
            # Get the application window's geometry in global coordinates
            window_rect = app_window.geometry()
            # Convert window's position to global coordinates
            window_global_pos = app_window.mapToGlobal(QPoint(0, 0))
            bounds = QRect(window_global_pos, window_rect.size())
        else:
            # Fallback to screen geometry if no app window found
            screen = QApplication.primaryScreen()
            bounds = screen.geometry()

        edge = self.anchor.lower()

        if edge == self.EDGE_LEFT:
            # Slide in from left edge of application window
            end_x = bounds.left() + self.margin
            end_y = bounds.top() + (bounds.height() - height) // 2  # Center vertically
            start = QPoint(bounds.left() - width, end_y)  # Start off-screen to the left
            end = QPoint(end_x, end_y)
        elif edge == self.EDGE_RIGHT:
            # Slide in from right edge of application window
            end_x = bounds.right() - width - self.margin
            end_y = bounds.top() + (bounds.height() - height) // 2  # Center vertically
            start = QPoint(bounds.right(), end_y)  # Start off-screen to the right
            end = QPoint(end_x, end_y)
        elif edge == self.EDGE_TOP:
            # Slide in from top edge of application window
            end_x = bounds.left() + (bounds.width() - width) // 2  # Center horizontally
            end_y = bounds.top() + self.margin
            start = QPoint(end_x, bounds.top() - height)  # Start off-screen above
            end = QPoint(end_x, end_y)
        elif edge == self.EDGE_BOTTOM:
            # Slide in from bottom edge of application window
            end_x = bounds.left() + (bounds.width() - width) // 2  # Center horizontally
            end_y = bounds.bottom() - height - self.margin
            start = QPoint(end_x, bounds.bottom())  # Start off-screen below
            end = QPoint(end_x, end_y)
        else:
            raise ValueError(f"Unknown edge: {edge}")

        return start, end

    def recalculate_position(self):
        """Recalculate and update flyout position - useful for edge anchoring when window moves/resizes."""
        if self._visible and self.anchor_mode == self.ANCHOR_EDGE:
            # Recalculate positions based on current window state
            self.adjustSize()
            w = self.width()
            h = self.height()
            start, end = self._calculate_positions(w, h)

            # Move to the new end position immediately (no animation for repositioning)
            self.move(end)

    def enable_auto_repositioning(self):
        """Enable automatic repositioning for edge-anchored flyouts when the window moves/resizes."""
        if self.anchor_mode == self.ANCHOR_EDGE:
            app_window = self._get_application_window()
            if app_window and hasattr(app_window, 'installEventFilter'):
                # Install event filter to monitor window events
                app_window.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Event filter to handle window resize/move events for auto-repositioning."""
        if (self.anchor_mode == self.ANCHOR_EDGE and
            self._visible and
            obj == self._get_application_window()):

            if event.type() in (QEvent.Resize, QEvent.Move):
                # Use a timer to avoid excessive updates during dragging
                if not hasattr(self, '_reposition_timer'):
                    self._reposition_timer = QTimer()
                    self._reposition_timer.setSingleShot(True)
                    self._reposition_timer.timeout.connect(self.recalculate_position)

                self._reposition_timer.start(50)  # 50ms delay to batch updates

        return False  # Don't consume the event

    def _get_application_window(self):
        """Get the main application window for consistent edge anchoring."""
        # First, try to get the parent window if it's a main window
        current_parent = self.parent()
        while current_parent:
            if isinstance(current_parent, QMainWindow):
                return current_parent
            current_parent = current_parent.parent()

        # If no main window parent found, look for any QMainWindow in the app
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow) and widget.isVisible():
                return widget

        # Fallback to active window
        active_window = QApplication.activeWindow()
        if active_window:
            return active_window

        # Last resort: use the first top-level widget
        top_level_widgets = QApplication.topLevelWidgets()
        if top_level_widgets:
            return top_level_widgets[0]

        return None

    def _calculate_custom_positions(self, width: int, height: int) -> tuple[QPoint, QPoint]:
        """Calculate positions for custom anchoring with explicit start/end points."""
        config = self.anchor

        # Support both explicit start/end points and calculated positions
        if "start" in config and "end" in config:
            start = QPoint(config["start"]["x"], config["start"]["y"])
            end = QPoint(config["end"]["x"], config["end"]["y"])
        elif "anchor_point" in config:
            # Calculate from anchor point similar to point mode but with custom offsets
            anchor_point = QPoint(config["anchor_point"]["x"], config["anchor_point"]["y"])
            offset_x = config.get("offset_x", 0)
            offset_y = config.get("offset_y", 0)
            slide_distance = config.get("slide_distance", width if self.direction in [self.LEFT, self.RIGHT] else height)

            end = QPoint(anchor_point.x() + offset_x, anchor_point.y() + offset_y)

            if self.direction == self.RIGHT:
                start = QPoint(end.x() + slide_distance, end.y())
            elif self.direction == self.LEFT:
                start = QPoint(end.x() - slide_distance, end.y())
            elif self.direction == self.BOTTOM:
                start = QPoint(end.x(), end.y() + slide_distance)
            else:  # TOP
                start = QPoint(end.x(), end.y() - slide_distance)
        else:
            raise ValueError("Custom anchor must specify either 'start'/'end' or 'anchor_point'")

        return start, end

    def setContent(self, content):
        """Replace the flyout's content widget."""
        layout = self.layout()
        # clear existing items
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        layout.addWidget(content)
        self.adjustSize()

    # ── Convenience Methods ──────────────────────────────────────────────────
    def is_edge_anchored(self) -> bool:
        """Check if this flyout is using edge anchoring."""
        return self.anchor_mode == self.ANCHOR_EDGE

    def get_anchor_info(self) -> dict:
        """Get information about the current anchor configuration."""
        return {
            "mode": self.anchor_mode,
            "anchor": self.anchor,
            "direction": self.direction,
            "margin": self.margin,
            "duration": self.duration,
            "visible": self._visible
        }

    # ── Factory Methods ──────────────────────────────────────────────────────
    @classmethod
    def from_widget(cls, anchor_widget: QWidget, direction: int = RIGHT, content: QWidget = None, **kwargs):
        """Create flyout anchored to a widget (traditional mode)."""
        return cls(anchor=anchor_widget, direction=direction, content=content,
                  anchor_mode=cls.ANCHOR_WIDGET, **kwargs)

    @classmethod
    def from_point(cls, x: int, y: int, direction: int = RIGHT, content: QWidget = None, **kwargs):
        """Create flyout anchored to a specific point."""
        return cls(anchor=QPoint(x, y), direction=direction, content=content,
                  anchor_mode=cls.ANCHOR_POINT, **kwargs)

    @classmethod
    def from_edge(cls, edge: str, content: QWidget = None, auto_reposition: bool = True, **kwargs):
        """Create flyout that slides in from screen/window edge."""
        flyout = cls(anchor=edge, direction=cls.RIGHT, content=content,
                    anchor_mode=cls.ANCHOR_EDGE, **kwargs)

        if auto_reposition:
            flyout.enable_auto_repositioning()

        return flyout

    @classmethod
    def from_custom(cls, start_point: QPoint, end_point: QPoint, content: QWidget = None, **kwargs):
        """Create flyout with custom start and end positions."""
        custom_config = {
            "start": {"x": start_point.x(), "y": start_point.y()},
            "end": {"x": end_point.x(), "y": end_point.y()}
        }
        return cls(anchor=custom_config, direction=cls.RIGHT, content=content,
                  anchor_mode=cls.ANCHOR_CUSTOM, **kwargs)

    @classmethod
    def sidebar_style(cls, parent: QWidget, content: QWidget = None, from_left: bool = True, **kwargs):
        """Create a sidebar-style flyout that slides from window edge."""
        edge = cls.EDGE_LEFT if from_left else cls.EDGE_RIGHT
        return cls.from_edge(edge, content=content, parent=parent, **kwargs)


# Example usage:
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow,
                                   QPushButton, QVBoxLayout)

    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setGeometry(100, 100, 600, 400)
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)

    # Traditional widget anchoring
    button1 = QPushButton("Widget Anchor Flyout")
    layout.addWidget(button1)
    label1 = QLabel("Traditional widget anchoring")
    flyout1 = FlyoutWidget.from_widget(button1, FlyoutWidget.RIGHT, label1)
    button1.clicked.connect(flyout1.toggle_flyout)

    # Point anchoring
    button2 = QPushButton("Point Anchor Flyout")
    layout.addWidget(button2)
    label2 = QLabel("Anchored to specific coordinates")
    flyout2 = FlyoutWidget.from_point(300, 200, FlyoutWidget.BOTTOM, label2)
    button2.clicked.connect(flyout2.toggle_flyout)

    # Edge anchoring (sidebar style)
    button3 = QPushButton("Edge Anchor Flyout")
    layout.addWidget(button3)
    label3 = QLabel("Slides from window edge")
    flyout3 = FlyoutWidget.from_edge("left", label3, parent=window)
    button3.clicked.connect(flyout3.toggle_flyout)

    # Custom anchoring
    button4 = QPushButton("Custom Anchor Flyout")
    layout.addWidget(button4)
    label4 = QLabel("Custom start/end points")
    start = QPoint(100, 100)
    end = QPoint(200, 150)
    flyout4 = FlyoutWidget.from_custom(start, end, label4)
    button4.clicked.connect(flyout4.toggle_flyout)

    window.show()
    sys.exit(app.exec())
