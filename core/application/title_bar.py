# 🔸 Third-Party Import
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon

# 🔸 Local Application Imports
from core.helpers import svg_loader
from core.helpers.config import ICON_COLOR, icon_path

# 🔸 Constants
ICON_SIZE = QSize(12, 12)
BUTTON_SIZE = QSize(38, 38)

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
        btn_toggle_sidebar (QPushButton): Toggles sidebar visibility.
        btn_minimize (QPushButton): Minimizes the window.
        btn_maximize (QPushButton): Maximizes or restores the window.
        btn_close (QPushButton): Closes the application.
    """

    # 🔹 Signals
    sidebar_toggled = Signal()   # To toggle sidebar visibility
    close_clicked = Signal()     # To signal a close event
    minimize_clicked = Signal()  # To signal a minimize event
    maximize_clicked = Signal()  # To signal a maximize/restore event

    def __init__(self, parent):
        """
        Initializes the custom title bar widget and sets up UI components.

        Args:
            parent (QWidget): The parent widget of the title bar.
        """
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(38)

        self.old_pos = None  # Initialize old position for dragging

        # 🔹 Load Icons
        self.icon_minimize = svg_loader(icon_path("minimize"), ICON_COLOR, ICON_SIZE, return_type=QIcon, source_color="#000")
        self.icon_maximize = svg_loader(icon_path("maximize"), ICON_COLOR, ICON_SIZE, return_type=QIcon, source_color="#000")
        self.icon_restore = svg_loader(icon_path("restore"), ICON_COLOR, ICON_SIZE, return_type=QIcon, source_color="#000")
        self.icon_close = svg_loader(icon_path("close"), ICON_COLOR, ICON_SIZE, return_type=QIcon, source_color="#000")
        self.icon_toggle = svg_loader(icon_path("toggle"), ICON_COLOR, ICON_SIZE, return_type=QIcon, source_color="#000")

        # 🔹 Title Label
        self.lbl_title = QLabel("MealGenie", self)
        self.lbl_title.setObjectName("lbl_title")

        # 🔹 Sidebar Toggle Button
        self.btn_toggle_sidebar = QPushButton(self)
        self.btn_toggle_sidebar.setObjectName("btn_toggle_sidebar")
        self.btn_toggle_sidebar.setFixedSize(BUTTON_SIZE)
        self.btn_toggle_sidebar.setIcon(self.icon_toggle)
        self.btn_toggle_sidebar.setIconSize(QSize(20, 20))
        self.btn_toggle_sidebar.clicked.connect(self.sidebar_toggled.emit)

        # 🔹 Minimize Button
        self.btn_minimize = QPushButton(self)
        self.btn_minimize.setObjectName("btn_minimize")
        self.btn_minimize.setFixedSize(BUTTON_SIZE)
        self.btn_minimize.setIcon(self.icon_minimize)
        self.btn_minimize.setIconSize(ICON_SIZE)
        self.btn_minimize.clicked.connect(lambda: self.minimize_clicked.emit())

        # 🔹 Maximize/Restore Button
        self.btn_maximize = QPushButton(self)
        self.btn_maximize.setObjectName("btn_maximize")
        self.btn_maximize.setFixedSize(BUTTON_SIZE)
        self.btn_maximize.setIcon(self.icon_maximize)
        self.btn_maximize.setIconSize(ICON_SIZE)
        self.btn_maximize.clicked.connect(lambda: self.maximize_clicked.emit())

        # Close Button
        self.btn_close = QPushButton(self)
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setFixedSize(BUTTON_SIZE)
        self.btn_close.setIcon(self.icon_close)
        self.btn_close.setIconSize(ICON_SIZE)
        self.btn_close.clicked.connect(lambda: self.close_clicked.emit())

        # 🔹 Layout For Title Bar
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.addWidget(self.btn_toggle_sidebar)
        title_bar_layout.addWidget(self.lbl_title)
        title_bar_layout.addStretch(1)  # Push buttons to the right
        title_bar_layout.addWidget(self.btn_minimize)
        title_bar_layout.addWidget(self.btn_maximize)
        title_bar_layout.addWidget(self.btn_close)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def buttons(self):
        """
        Exposes title bar buttons for external use.

        Returns:
            dict: A dictionary of QPushButton widgets.
        """
        return {
            "toggle_sidebar": self.btn_toggle_sidebar,
            "minimize": self.btn_minimize,
            "maximize": self.btn_maximize,
            "close": self.btn_close,
        }

    def updateMaximizeIcon(self, maximized: bool):
        """
        Updates the maximize/restore icon based on the maximized state.
        
        Args:
            maximized (bool): True if the window is maximized, False otherwise.
        """
        if maximized:
            self.btn_maximize.setIcon(self.icon_restore)
        else:
            self.btn_maximize.setIcon(self.icon_maximize)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(Qt.SizeAllCursor)

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            # Let the parent window manage the drag action
            self.parent().move(self.parent().x() + delta.x(), self.parent().y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.setCursor(Qt.ArrowCursor)