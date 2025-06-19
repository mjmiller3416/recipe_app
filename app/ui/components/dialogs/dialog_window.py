"""app/ui/components/dialog_window.py

Custom Dialog Window with Title Bar
A base QDialog with a frameless window and a custom title bar.
Provides close button and dragging functionality.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QPoint, QRect, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QSizeGrip,
                               QVBoxLayout, QWidget)

from app.config import APPLICATION_WINDOW
from app.ui.widgets import CTToolButton
from app.ui.widgets.helpers import ButtonEffects

# ── Constants ───────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]
ICONS = APPLICATION_WINDOW["ICONS"]

# ── Title Bar  ──────────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    """A custom title bar widget for frameless dialogs.

    Provides a close button and supports window dragging.

    Attributes:
        close_clicked: Signal emitted when the close button is clicked.
        old_pos: Stores the last mouse position during a drag operation.
        lbl_title: Label displaying the dialog title.
        btn_ico_close: Button to close the dialog.
    """


    # ── Signals ─────────────────────────────────────────────────────────────────────
    close_clicked = Signal()  # Signal emitted when close button is clicked

    def __init__(self, parent, window_title: str = SETTINGS["APP_NAME"]):
        """Initializes the TitleBar.

        Args:
            parent (QWidget): The parent widget.
            window_title (str): The title text to display.
        """
        # ── Properties ──
        super().__init__(parent)
        self.setObjectName("TitleBar") 
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(38)

        self.old_pos = None  # initialize old position for dragging

        # ── Title Label ──
        self.lbl_title = QLabel(window_title, self)
        
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
        self.btn_ico_close.clicked.connect(self.close_clicked)

    def _build_layout(self):
        """Builds the layout for the title bar, arranging buttons and title."""
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.addWidget(self.lbl_title)
        title_bar_layout.addStretch(1)  # push buttons to the right
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
            "close": self.btn_ico_close,
        }

    def mousePressEvent(self, event):
        """Handles mouse press events to initiate window dragging.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        # Allow dragging of dialog window
        if event.button() == Qt.LeftButton:
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

# ── Application Window ──────────────────────────────────────────────────────────
class DialogWindow(QDialog):
    """Base dialog class with frameless window and custom title bar.

    Provides a close button and dragging support. Content widgets
    should be added to the content_area layout.

    Attributes:
        title_bar: The custom title bar widget.
        window_body: The main dialog body widget.
        content_area: The widget holding main content.
        content_layout: Layout for adding content widgets.
        central_layout: Main layout for the dialog.
        start_geometry: Initial geometry of the dialog.
    """

    def __init__(self, width: int = 1330, height: int = 800, window_title: str =""):
        """Initializes the DialogWindow.

        Args:
            width (int, optional): Initial width of the dialog. Defaults to 1330.
            height (int, optional): Initial height of the dialog. Defaults to 800.
        """
        super().__init__()
        # ── Properties ──
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 300)
        self.setObjectName("Dialog")
        self.start_geometry = self.geometry()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        # ── Title Bar ──
        self.title_bar = TitleBar(self)
        self.title_bar.lbl_title.setText(window_title)
        self.central_layout.addWidget(self.title_bar)
        # Connect title bar signals for dialog behavior
        self.title_bar.close_clicked.connect(self.close)

        # ── Window Body ──
        self.window_body = QWidget(self)
        self.window_body.setObjectName("DialogWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        # ── Content Area ──
        self.content_area = QWidget()
        self.content_area.setObjectName("DialogLayout")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.body_layout.addWidget(self.content_area)
        self.central_layout.addWidget(self.window_body)

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

