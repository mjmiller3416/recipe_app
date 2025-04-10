"""
Custom title bar widget for the MealGenie application.

Includes:
- Application title display
- Minimize, maximize/restore, and close buttons
- Window drag behavior for frameless windows

Class:
    TitleBar(QWidget)
"""

from core.helpers.qt_imports import Qt, QWidget, QLabel, QHBoxLayout, QSize, QPushButton, Signal, QIcon

# 🔹 Local Imports
from core.helpers import svg_loader
from core.managers.style_manager import ICON_DEFAULT_COLOR

class TitleBar(QWidget):
    """
    Custom title bar widget for a frameless application window.

    Features:
        - Displays the application title
        - Minimize, maximize/restore, and close window buttons
        - Click-and-drag functionality to move the window

    Emits:
        - sidebarToggled: Signal emitted when the sidebar toggle button is clicked.
    """

    sidebarToggled = Signal() 

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(38)

        icon_size = QSize(12, 12)
        self.old_pos = None # Initialize old position for dragging

        # 🔹 Load Icons
        self.icon_minimize = svg_loader(":/icons/window_minimize.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon)
        self.icon_maximize = svg_loader(":/icons/window_maximize.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon)
        self.icon_restore = svg_loader(":/icons/window_restore.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon)  
        self.icon_restore = svg_loader(":/icons/window_restore.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon)
        self.icon_close = svg_loader(":/icons/window_close.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon)
        self.icon_sidebar_toggle = svg_loader(":/icons/sidebar_toggle.svg", ICON_DEFAULT_COLOR, size=icon_size, return_type=QIcon) 

        # 🔹 Title Label
        self.lbl_title = QLabel("MealGenie", self)
        self.lbl_title.setObjectName("lbl_title")

        # 🔹 Sidebar Toggle Button
        self.btn_toggle_sidebar = QPushButton(self) 
        self.btn_toggle_sidebar.setObjectName("btn_toggle_sidebar")
        self.btn_toggle_sidebar.setFixedSize(38, 38)
        self.btn_toggle_sidebar.setIcon(self.icon_sidebar_toggle)
        self.btn_toggle_sidebar.setIconSize(QSize(20,20))  # Set icon size for the button
        self.btn_toggle_sidebar.clicked.connect(self.sidebarToggled.emit)

        # 🔹 Minimize Button
        self.btn_minimize = QPushButton(self)
        self.btn_minimize.setObjectName("btn_minimize")
        self.btn_minimize.setFixedSize(38, 38)
        self.btn_minimize.setIcon(self.icon_minimize)
        self.btn_minimize.setIconSize(icon_size)
        self.btn_minimize.clicked.connect(lambda: self.window().showMinimized())

        # 🔹 Maximize/Restore Button
        self.btn_maximize = QPushButton(self)
        self.btn_maximize.setObjectName("btn_maximize")
        self.btn_maximize.setFixedSize(38, 38)
        self.btn_maximize.setIcon(self.icon_maximize)
        self.btn_maximize.setIconSize(icon_size)
        self.btn_maximize.clicked.connect(self.toggle_maximize_restore)

        # 🔹 Close Button
        self.btn_close = QPushButton(self)
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setFixedSize(38, 38)
        self.btn_close.setIcon(self.icon_close)
        self.btn_close.setIconSize(icon_size)
        self.btn_close.clicked.connect(self.close)

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
        """
        return {
            "toggle_sidebar": self.btn_toggle_sidebar,
            "minimize": self.btn_minimize,
            "maximize": self.btn_maximize,
            "close": self.btn_close,
        }

    def toggle_maximize_restore(self):
        """
        Toggle the window between maximized and normal state,
        and update the maximize button icon accordingly.
        """
        window = self.window()
        if window.isMaximized():
            window.showNormal()
            self.btn_maximize.setIcon(self.icon_maximize)
        else:
            window.showMaximized()
            self.btn_maximize.setIcon(self.icon_restore)

    def mouseMoveEvent(self, event):
        """
        Moves the main window based on the change in mouse position.
        Only active while dragging with the left mouse button held down.
        """
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            main_window = self.window()
            main_window.move(main_window.x() + delta.x(), main_window.y() + delta.y())
            self.old_pos = event.globalPos()

    def mousePressEvent(self, event):
        """
        Records the initial global mouse position when the left button is pressed.
        Used to enable window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(Qt.SizeAllCursor)

    def mouseReleaseEvent(self, event):
        """
        Clears the stored position when the mouse button is released,
        ending the window drag behavior.
        """
        self.old_pos = None
        self.setCursor(Qt.ArrowCursor)
