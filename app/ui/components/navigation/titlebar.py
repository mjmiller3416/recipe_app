"""app/ui/components/navigation/titlebar.py

Title bar component for the main application window.
"""

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from qframelesswindow import FramelessWindow
# ── Imports ───────────────────────────────────────────────────────────────
from qframelesswindow.utils.win32_utils import WindowsMoveResize as MoveResize

from app.config import APPLICATION_WINDOW
from app.theme_manager.icon import Icon, Name, Type
from app.ui.components.widgets import ToolButton

# ── Constants ─────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]


class TitleBar(QWidget):
    """A custom title bar for the frameless main window."""

    # ── Signals ──
    sidebar_toggled = Signal()
    close_clicked = Signal()
    minimize_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(60)

        self.old_pos = None

        # ── Title Label ──
        self.logo = Icon(Name.LOGO)
        self.logo.setSize(32,32)
        self.logo.setObjectName("AppLogo")
        self.title = QLabel(SETTINGS["APP_NAME"])

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = ToolButton(Type.DEFAULT)
        self.btn_ico_toggle_sidebar.setIcon(Name.MENU)
        self.btn_ico_toggle_sidebar.setCheckable(True)

        self.btn_ico_toggle_sidebar.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_toggle_sidebar.setObjectName("BtnToggleSidebar")

        # ── Minimize Button ──
        self.btn_ico_minimize = ToolButton(Type.DEFAULT)
        self.btn_ico_minimize.setIcon(Name.MINIMIZE)
        self.btn_ico_minimize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Maximize/Restore Button ──
        self.btn_ico_maximize = ToolButton(Type.DEFAULT)
        self.btn_ico_maximize.setIcon(Name.MAXIMIZE)
        self.btn_ico_maximize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Close Button ──
        self.btn_ico_close = ToolButton(Type.DEFAULT)
        self.btn_ico_close.setIcon(Name.CROSS)
        self.btn_ico_close.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_close.setObjectName("BtnClose")

        self._build_layout()
        self._connect_signals()

    def _connect_signals(self):
        self.btn_ico_toggle_sidebar.clicked.connect(self.sidebar_toggled.emit)
        self.btn_ico_minimize.clicked.connect(self.minimize_clicked)
        self.btn_ico_maximize.clicked.connect(self.maximize_clicked)
        self.btn_ico_close.clicked.connect(self.close_clicked)

    def _build_layout(self):
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.addWidget(self.btn_ico_toggle_sidebar)
        title_bar_layout.addWidget(self.logo)
        title_bar_layout.addWidget(self.title)
        title_bar_layout.addStretch(1)
        title_bar_layout.addWidget(self.btn_ico_minimize)
        title_bar_layout.addWidget(self.btn_ico_maximize)
        title_bar_layout.addWidget(self.btn_ico_close)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def buttons(self):
        return {
            "toggle_sidebar": self.btn_ico_toggle_sidebar,
            "minimize": self.btn_ico_minimize,
            "maximize": self.btn_ico_maximize,
            "close": self.btn_ico_close,
        }

    def update_maximize_icon(self, maximized: bool):
        icon_name = Name.RESTORE if maximized else Name.MAXIMIZE
        self.btn_ico_maximize.setIcon(icon_name)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            global_pos: QPoint = event.globalPosition().toPoint()
            MoveResize.startSystemMove(self.window(), global_pos)
        super().mousePressEvent(event)
