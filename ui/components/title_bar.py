"""ui/components/title_bar.py

Defines the TitleBar class, a custom title bar for a frameless application window.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from config import TITLE_BAR
from ui.iconkit import ThemedIcon, ToolButtonIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    """
    Custom title bar widget for a frameless application window.

    Features:
        - Displays the application title
        - Minimize, maximize/restore, and close window buttons
        - Click-and-drag functionality to move the window

    Attributes:
        sidebarToggled (Signal): Emitted when the sidebar toggle button is clicked.
        lbl_title (QLabel): Displays the app name.
        btn_ico_toggle_sidebar (QPushButton): Toggles sidebar visibility.
        btn_ico_minimize (QPushButton): Minimizes the window.
        btn_ico_maximize (QPushButton): Maximizes or restores the window.
        btn_ico_close (QPushButton): Closes the application.
    """

    # ── Signals ─────────────────────────────────────────────────────────────────────
    sidebar_toggled  = Signal()  # To toggle sidebar visibility
    close_clicked    = Signal()  # To signal a close event
    minimize_clicked = Signal()  # To signal a minimize event
    maximize_clicked = Signal()  # To signal a maximize/restore event

    def __init__(self, parent):
        """
        Initializes the custom title bar widget and sets up UI components.

        Args:
            parent (QWidget): The parent widget of the title bar.
        """
        # ── Properties ──
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(38)

        self.old_pos = None  # Initialize old position for dragging

        # ── Title Label ──
        self.lbl_title = QLabel(TITLE_BAR["APP_NAME"], self)
        self.lbl_title.setObjectName("lbl_title")

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = ToolButtonIcon(
            file_path=TITLE_BAR["ICON_TOGGLE_SIDEBAR"],
            size=QSize(20, 20),
            variant=TITLE_BAR["VARIANT"],
            checkable=True,
        )
        self.btn_ico_toggle_sidebar.setFixedSize(TITLE_BAR["BUTTON_SIZE"])
        self.btn_ico_toggle_sidebar.clicked.connect(self.sidebar_toggled.emit)

        # ── Minimize Button ──
        self.btn_ico_minimize = ToolButtonIcon(
            file_path=TITLE_BAR["ICON_MINIMIZE"],
            size=TITLE_BAR["ICON_SIZE"],
            variant=TITLE_BAR["VARIANT"],
        )
        self.btn_ico_minimize.setFixedSize(TITLE_BAR["BUTTON_SIZE"])
        self.btn_ico_minimize.clicked.connect(lambda: self.minimize_clicked.emit())

        # ── Maximize/Restore Button ──
        self.btn_ico_maximize = ToolButtonIcon(
            file_path=TITLE_BAR["ICON_MAXIMIZE"],
            size=TITLE_BAR["ICON_SIZE"],
            variant=TITLE_BAR["VARIANT"],
        )
        self.btn_ico_maximize.setFixedSize(TITLE_BAR["BUTTON_SIZE"])
        self.btn_ico_maximize.clicked.connect(lambda: self.maximize_clicked.emit())

        # ── Close Button ──
        self.btn_ico_close = ToolButtonIcon(
            file_path=TITLE_BAR["ICON_CLOSE"],
            size=TITLE_BAR["ICON_SIZE"],
            variant=TITLE_BAR["VARIANT"],
        )
        self.btn_ico_close.setFixedSize(TITLE_BAR["BUTTON_SIZE"])
        self.btn_ico_close.clicked.connect(lambda: self.close_clicked.emit())

        # 🔹 Layout For Title Bar
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.addWidget(self.btn_ico_toggle_sidebar)
        title_bar_layout.addWidget(self.lbl_title)
        title_bar_layout.addStretch(1)  # Push buttons to the right
        title_bar_layout.addWidget(self.btn_ico_minimize)
        title_bar_layout.addWidget(self.btn_ico_maximize)
        title_bar_layout.addWidget(self.btn_ico_close)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def buttons(self):
        """
        Exposes title bar buttons for external use.

        Returns:
            dict: A dictionary of QPushButton widgets.
        """
        return {
            "toggle_sidebar": self.btn_ico_toggle_sidebar,
            "minimize": self.btn_ico_minimize,
            "maximize": self.btn_ico_maximize,
            "close": self.btn_ico_close,
        }

    
    def update_maximize_icon(self, maximized: bool):
        target_path = (
            TITLE_BAR["ICON_RESTORE"] if maximized else TITLE_BAR["ICON_MAXIMIZE"]
        )

        icon = ThemedIcon(
            file_path=target_path,
            size=self.btn_ico_maximize.size(),
            variant=TITLE_BAR["VARIANT"],
        ).icon()

        self.btn_ico_maximize.setIcon(icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(Qt.SizeAllCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            win = self.window()
            win.move(win.x() + delta.x(), win.y() + delta.y())
            self.old_pos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
