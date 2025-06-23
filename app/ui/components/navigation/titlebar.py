"""app/ui/components/navigation/titlebar.py

Title bar component for the main application window.
"""

# ── Imports ───────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from app.config import APPLICATION_WINDOW
from app.ui.widgets import CTIcon, CTToolButton
from app.ui.widgets.helpers import ButtonEffects

# ── Constants ─────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]
APP_ICONS = APPLICATION_WINDOW["ICONS"]


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
        self.logo = CTIcon(
            file_path=APP_ICONS["LOGO"]["PATH"],
            icon_size=APP_ICONS["LOGO"]["SIZE"],
            variant=APP_ICONS["LOGO"]["STATIC"],
        )
        self.logo.setFixedSize(32, 32)
        self.logo.setObjectName("AppLogo")
        self.title = QLabel(SETTINGS["APP_NAME"])

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = CTToolButton(
            file_path=APP_ICONS["TOGGLE_SIDEBAR"]["PATH"],
            icon_size=APP_ICONS["TOGGLE_SIDEBAR"]["SIZE"],
            variant=APP_ICONS["TOGGLE_SIDEBAR"]["DYNAMIC"],
            checkable=True,
        )
        self.btn_ico_toggle_sidebar.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_toggle_sidebar.setObjectName("BtnToggleSidebar")

        # ── Minimize Button ──
        self.btn_ico_minimize = CTToolButton(
            file_path=APP_ICONS["MINIMIZE"]["PATH"],
            icon_size=APP_ICONS["MINIMIZE"]["SIZE"],
            variant=APP_ICONS["MINIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_minimize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Maximize/Restore Button ──
        self.btn_ico_maximize = CTToolButton(
            file_path=APP_ICONS["MAXIMIZE"]["PATH"],
            icon_size=APP_ICONS["MAXIMIZE"]["SIZE"],
            variant=APP_ICONS["MAXIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_maximize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Close Button ──
        self.btn_ico_close = CTToolButton(
            file_path=APP_ICONS["CLOSE"]["PATH"],
            icon_size=APP_ICONS["CLOSE"]["SIZE"],
            variant=APP_ICONS["CLOSE"]["DYNAMIC"],
        )
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
        target_path = (
            APP_ICONS["RESTORE"]["PATH"] if maximized else APP_ICONS["MAXIMIZE"]["PATH"]
        )
        ButtonEffects.recolor(
            self.btn_ico_maximize,
            file_name=target_path,
            size=self.btn_ico_maximize.iconSize(),
            variant=SETTINGS["BTN_STYLE"]["DYNAMIC"],
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.window().isMaximized():
            self.old_pos = event.globalPos()
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
        super().mouseDoubleClickEvent(event)
