"""
This module defines a custom application window with a frameless title bar.

The `TitleBar` class provides a custom title bar with buttons for standard
window operations (minimize, maximize/restore, close) and a sidebar toggle.
It allows the window to be moved by clicking and dragging.

The `ApplicationWindow` class is a QDialog that incorporates the custom
`TitleBar` and a main content area. It handles the window's core functionalities
like resizing, and managing the maximized/restored state.

The `CustomGrip` class provides invisible widgets for resizing the window
from its edges and corners.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QPoint, QRect, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QSizeGrip,
                               QVBoxLayout, QWidget)

from config import APPLICATION_WINDOW
from ui.animations.window_animator import WindowAnimator
from ui.widgets import CTToolButton
from ui.widgets.utils import ButtonEffects

# ── Constants ───────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]
ICONS = APPLICATION_WINDOW["ICONS"]

# ── Title Bar  ──────────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    """A custom title bar widget for frameless windows.

    Provides standard window control buttons (minimize, maximize, close)
    and a sidebar toggle button. Allows window dragging and maximizing
    via double-click.

    Attributes:
        sidebar_toggled: Signal emitted when the sidebar toggle button is clicked.
        close_clicked: Signal emitted when the close button is clicked.
        minimize_clicked: Signal emitted when the minimize button is clicked.
        maximize_clicked: Signal emitted when the maximize/restore button is clicked.
        old_pos: Stores the last mouse position during a drag operation.
        lbl_title: Label displaying the application title.
        btn_ico_toggle_sidebar: Button to toggle the sidebar.
        btn_ico_minimize: Button to minimize the window.
        btn_ico_maximize: Button to maximize/restore the window.
        btn_ico_close: Button to close the window.
    """


    # ── Signals ─────────────────────────────────────────────────────────────────────
    sidebar_toggled  = Signal()  # To toggle sidebar visibility
    close_clicked    = Signal()  # To signal a close event
    minimize_clicked = Signal()  # To signal a minimize event
    maximize_clicked = Signal()  # To signal a maximize/restore event

    def __init__(self, parent):
        """Initializes the TitleBar.

        Args:
            parent (QWidget): The parent widget.
        """
        # ── Properties ──
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(38)

        self.old_pos = None  # initialize old position for dragging

        # ── Title Label ──
        self.lbl_title = QLabel(SETTINGS["APP_NAME"], self)

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = CTToolButton(
            file_path = ICONS["TOGGLE_SIDEBAR"]["PATH"],
            icon_size = ICONS["TOGGLE_SIDEBAR"]["SIZE"],
            variant   = ICONS["TOGGLE_SIDEBAR"]["DYNAMIC"],
            checkable = True,
        )
        self.btn_ico_toggle_sidebar.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_toggle_sidebar.setObjectName("BtnToggleSidebar")

        # ── Minimize Button ──
        self.btn_ico_minimize = CTToolButton(
            file_path = ICONS["MINIMIZE"]["PATH"],
            icon_size = ICONS["MINIMIZE"]["SIZE"],
            variant   = ICONS["MINIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_minimize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Maximize/Restore Button ──
        self.btn_ico_maximize = CTToolButton(
            file_path = ICONS["MAXIMIZE"]["PATH"],
            icon_size = ICONS["MAXIMIZE"]["SIZE"],
            variant   = ICONS["MAXIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_maximize.setFixedSize(SETTINGS["BTN_SIZE"])
        
        # ── Close Button ──
        self.btn_ico_close = CTToolButton(
            file_path = ICONS["CLOSE"]["PATH"],
            icon_size = ICONS["CLOSE"]["SIZE"],
            variant   = ICONS["CLOSE"]["DYNAMIC"],
        )
        self.btn_ico_close.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_close.setObjectName("BtnClose")

        self._build_layout()  # build the layout for the title bar
        self._connect_signals() # connect button signals

    def _connect_signals(self):
        """Connects signals from buttons to the TitleBar's signals."""
        self.btn_ico_toggle_sidebar.clicked.connect(self.sidebar_toggled.emit)
        self.btn_ico_minimize.clicked.connect(self.minimize_clicked)
        self.btn_ico_maximize.clicked.connect(self.maximize_clicked)
        self.btn_ico_close.clicked.connect(self.close_clicked)

    def _build_layout(self):
        """Builds the layout for the title bar, arranging buttons and title."""
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.addWidget(self.btn_ico_toggle_sidebar)
        title_bar_layout.addWidget(self.lbl_title)
        title_bar_layout.addStretch(1)  # push buttons to the right
        title_bar_layout.addWidget(self.btn_ico_minimize)
        title_bar_layout.addWidget(self.btn_ico_maximize)
        title_bar_layout.addWidget(self.btn_ico_close)
        title_bar_layout.setContentsMargins(0, 0, 0, 0) 

    @property
    def buttons(self):
        """Returns a dictionary of the control buttons.

        Returns:
            dict: A dictionary mapping button names to their respective
                  CTToolButton instances.
        """
        return {
            "toggle_sidebar": self.btn_ico_toggle_sidebar,
            "minimize": self.btn_ico_minimize,
            "maximize": self.btn_ico_maximize,
            "close": self.btn_ico_close,
        }

    def update_maximize_icon(self, maximized: bool):
        """Updates the maximize/restore button icon based on window state.

        Args:
            maximized: True if the window is maximized, False otherwise.
        """
        target_path = (
            ICONS["RESTORE"]["PATH"] if maximized else ICONS["MAXIMIZE"]["PATH"]
        )

        # reapply hover effects with the correct base icon
        ButtonEffects.recolor(
            self.btn_ico_maximize,
            file_name=target_path,
            size=self.btn_ico_maximize.iconSize(),
            variant=SETTINGS["BTN_STYLE"]["DYNAMIC"],
        )

    def mousePressEvent(self, event):
        """Handles mouse press events to initiate window dragging.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        # Allow dragging only when the window is not maximized.
        if event.button() == Qt.LeftButton and not self.window()._is_maximized:
            self.old_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handles mouse move events to drag the window.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            win = self.window()
            win.move(win.x() + delta.x(), win.y() + delta.y())
            self.old_pos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handles mouse release events to stop dragging.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        self.old_pos = None
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handles a double-click event on the title bar.

        This triggers the maximize/restore functionality.

        Args:
            event (QMouseEvent): The mouse double-click event.
        """
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
        super().mouseDoubleClickEvent(event)

# ── Side Grip ──────────────────────────────────────────────────────────────────
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

# ── Application Window ──────────────────────────────────────────────────────────
class ApplicationWindow(QDialog):
    """A custom QDialog with a frameless window and a custom title bar.

    This window provides standard window functionalities like minimize,
    maximize, close, and resizing, but with a custom-drawn title bar
    and border.

    Attributes:
        start_geometry (QRect): The window's geometry at the start of a resize operation.
        animator (WindowAnimator): Handles window animations like minimize/maximize.
        title_bar (TitleBar): The custom title bar widget.
        _is_maximized (bool): Tracks if the window is currently maximized.
        body (QWidget): The main content area of the window.
        content_layout (QVBoxLayout): The layout for the main content area.
        grips (dict[str, CustomGrip]): A dictionary of CustomGrip widgets for resizing.
    """
    # ── Signals ─────────────────────────────────────────────────────────────────────
    sidebar_toggle_requested = Signal()

    def __init__(self, width: int = 600, height: int = 400):
        """Initializes the ApplicationWindow.

        Args:
            width (int, optional): The initial width of the window. Defaults to 600.
            height (int, optional): The initial height of the window. Defaults to 400.
        """
        super().__init__()
        # ── Properties ──
        self.setObjectName("ApplicationWindow")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 300)
        self.start_geometry = self.geometry()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        # ── Title Bar ──
        self.animator = WindowAnimator(self)
        self.title_bar = TitleBar(self)
        self._is_maximized = False
        self.central_layout.addWidget(self.title_bar)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # ── Window Body ──
        self.window_body = QWidget(self)
        self.window_body.setObjectName("ApplicationWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        # ── Content Area ──
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(1, 0, 0, 1)
        self.content_layout.setSpacing(8)
        self.body_layout.addWidget(self.content_area)
        self.central_layout.addWidget(self.window_body)

        # ── Create Grips ──
        self.grips = {}        
        grip_positions = [
            "top", "bottom", "left", "right",
            "top_left", "top_right", "bottom_left", "bottom_right"
        ]
        for pos in grip_positions:
            self.grips[pos] = CustomGrip(self, pos)
            self.grips[pos].raise_()

        self.resize(int(width), int(height))
        self.center_on_screen()

    def center_on_screen(self):
        """Centers the window on the screen."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        
        # calculate center position
        center_x = (screen_geometry.width() - window_geometry.width()) // 2
        center_y = (screen_geometry.height() - window_geometry.height()) // 2
        
        # move window to center
        self.move(center_x, center_y)

    def resizeEvent(self, event):
        """Handles window resize events.

        Repositions all custom size grips when the window is resized.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        grip_size = self.grips["top"].grip_size
        w, h = self.width(), self.height()

        self.grips["top"].setGeometry(grip_size, 0, w - 2 * grip_size, grip_size)
        self.grips["bottom"].setGeometry(grip_size, h - grip_size, w - 2 * grip_size, grip_size)
        self.grips["left"].setGeometry(0, grip_size, grip_size, h - 2 * grip_size)
        self.grips["right"].setGeometry(w - grip_size, grip_size, grip_size, h - 2 * grip_size)
        self.grips["top_left"].setGeometry(0, 0, grip_size, grip_size)
        self.grips["top_right"].setGeometry(w - grip_size, 0, grip_size, grip_size)
        self.grips["bottom_left"].setGeometry(0, h - grip_size, grip_size, grip_size)
        self.grips["bottom_right"].setGeometry(w - grip_size, h - grip_size, grip_size, grip_size)

    def resize_from_grip(self, position: str, delta: QPoint):
        """Resizes the window based on movement of a CustomGrip.

        Calculates the new window geometry based on which grip was moved and
        the mouse delta. Enforces minimum size constraints.

        Args:
            position (str): The position of the grip being dragged (e.g., "top_left").
            delta (QPoint): The change in mouse position since the drag started.
        """
        if self._is_maximized:
            return

        # start with the geometry from when the drag began
        new_rect = QRect(self.start_geometry)

        # adjust the rectangle's sides based on the grip's position
        if "left" in position:
            new_rect.setLeft(self.start_geometry.left() + delta.x())
        if "right" in position:
            new_rect.setRight(self.start_geometry.right() + delta.x())
        if "top" in position:
            new_rect.setTop(self.start_geometry.top() + delta.y())
        if "bottom" in position:
            new_rect.setBottom(self.start_geometry.bottom() + delta.y())

        # enforce minimum size constraints to prevent snapping
        min_size = self.minimumSize()
        if new_rect.width() < min_size.width():
            # which side was dragged? adjust the appropriate side.
            if "left" in position:
                new_rect.setLeft(new_rect.right() - min_size.width())
            else: # right side was dragged
                new_rect.setRight(new_rect.left() + min_size.width())
        
        if new_rect.height() < min_size.height():
            # which side was dragged? adjust the appropriate side.
            if "top" in position:
                new_rect.setTop(new_rect.bottom() - min_size.height())
            else: # bottom side was dragged
                new_rect.setBottom(new_rect.top() + min_size.height())

        self.setGeometry(new_rect)
