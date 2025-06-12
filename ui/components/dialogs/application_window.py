# ui\components\dialogs\application_window.py
"""
This module defines a custom application window with a frameless title bar.

The `TitleBar` class provides a custom title bar with buttons for standard
window operations (minimize, maximize/restore, close) and a sidebar toggle.
It allows the window to be moved by clicking and dragging.

The `ApplicationWindow` class is a QDialog that incorporates the custom
`TitleBar` and a main content area. It handles the window's core functionalities
like resizing, and managing the maximized/restored state.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout

from config import APPLICATION_WINDOW
from ui.widgets import CTToolButton
from ui.widgets.utils import ButtonEffects
from ui.animations.window_animator import WindowAnimator

# ── Constants ───────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]
ICONS = APPLICATION_WINDOW["ICONS"]

# ── Title Bar  ──────────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    """A custom title bar widget for frameless windows.

    Provides standard window control buttons (minimize, maximize, close)
    and a sidebar toggle button. Allows window dragging and maximizing
    via double-click.

    Attributes:
        sidebar_toggled (Signal): Emitted when the sidebar toggle button is clicked.
        close_clicked (Signal): Emitted when the close button is clicked.
        minimize_clicked (Signal): Emitted when the minimize button is clicked.
        maximize_clicked (Signal): Emitted when the maximize/restore button is clicked.
        old_pos (QPoint | None): Stores the last mouse position during a drag operation.
        lbl_title (QLabel): Label displaying the application title.
        btn_ico_toggle_sidebar (CTToolButton): Button to toggle the sidebar.
        btn_ico_minimize (CTToolButton): Button to minimize the window.
        btn_ico_maximize (CTToolButton): Button to maximize/restore the window.
        btn_ico_close (CTToolButton): Button to close the window.
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
        self.lbl_title.setObjectName("lbl_title")

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = CTToolButton(
            file_path  = ICONS["TOGGLE_SIDEBAR"]["PATH"],
            icon_size  = ICONS["TOGGLE_SIDEBAR"]["SIZE"],
            variant    = ICONS["TOGGLE_SIDEBAR"]["DYNAMIC"],
            checkable  = True,
        )
        self.btn_ico_toggle_sidebar.setFixedSize(SETTINGS["BTN_SIZE"])

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

        self._build_layout()  # build the layout for the title bar
        self._connect_signals() # connect button signals

    def _connect_signals(self):
        """Connects signals from buttons to the TitleBar's signals."""
        self.btn_ico_toggle_sidebar.clicked.connect(self.sidebar_toggled.emit)
        self.btn_ico_minimize.clicked.connect(lambda: self.minimize_clicked.emit())
        self.btn_ico_maximize.clicked.connect(lambda: self.maximize_clicked.emit())
        self.btn_ico_close.clicked.connect(lambda: self.close_clicked.emit())

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
            maximized (bool): True if the window is maximized, False otherwise.
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
        """
        Handles a double-click event on the title bar to trigger maximize/restore.
        """
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
        super().mouseDoubleClickEvent(event)

# ── Application Window ──────────────────────────────────────────────────────────
class ApplicationWindow(QDialog):
    """A custom QDialog with a frameless window and a custom title bar.

    This window provides basic functionalities like minimize, maximize/restore,
    and close, along with a content area for application-specific widgets.

    Attributes:
        title_bar (TitleBar): The custom title bar for the window.
        body (QWidget): The main content area of the window.
        content_layout (QVBoxLayout): The layout for the body widget.
        _is_maximized (bool): Tracks if the window is currently maximized.
        _normal_geometry (QRect): Stores the window geometry before maximization.
    """
    def __init__(
            self, 
            width: int = 600, 
            height: int = 400,
        ):
        """Initializes the ApplicationWindow.

        Args:
            width (int, optional): The initial width of the window.
                Defaults to 600.
            height (int, optional): The initial height of the window.
                Defaults to 400.
        """
        super().__init__()

        # ── Properties ──
        self.setObjectName("ApplicationWindow")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) # remove native title bar
        self.resize(int(width), int(height))  # set initial size

        # ── Central Layout ──
        central_layout = QVBoxLayout(self)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # ── Window Animator ──
        self.animator = WindowAnimator(self)

        # ── Instiate TileBar ──
        self.title_bar = TitleBar(self)
        self._is_maximized = False
        central_layout.addWidget(self.title_bar) 

        # ── Connect TitleBar Signals ──
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)

        # ── Body Container ──
        self.body = QWidget(self)
        self.body.setObjectName("Dialog")
        self.content_layout = QVBoxLayout(self.body)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)
        central_layout.addWidget(self.body)              
