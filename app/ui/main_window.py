"""app/ui/main_window.py

Defines the main application window, including the custom title bar and sidebar.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, QSize, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QButtonGroup, QDialog, QHBoxLayout, QLabel,
                               QSizePolicy, QSpacerItem, QStackedWidget,
                               QVBoxLayout, QWidget)

from app.config import APPLICATION_WINDOW, SIDEBAR
from app.core.utils import DebugLogger
from app.style_manager import ThemeController
from app.ui.animations import Animator, WindowAnimator
from app.ui.components import CustomGrip, NavButton
from app.ui.components.image import AvatarLoader
from app.ui.helpers.ui_helpers import create_fixed_wrapper
from app.ui.widgets import CTIcon, CTToolButton
from app.ui.widgets.helpers import ButtonEffects

if TYPE_CHECKING:
    from app.core.services import NavigationService
    from app.style_manager import ThemeController

# ── Constants ───────────────────────────────────────────────────────────────────
SETTINGS = APPLICATION_WINDOW["SETTINGS"]
APP_ICONS = APPLICATION_WINDOW["ICONS"]
SIDEBAR_ICONS = SIDEBAR["ICONS"]
START = SIDEBAR["SETTINGS"]["EXPANDED_WIDTH"]
END = SIDEBAR["SETTINGS"]["COLLAPSED_WIDTH"]
DURATION = SIDEBAR["SETTINGS"]["DURATION"]

# ── Application Window ──────────────────────────────────────────────────────────
class MainWindow(QDialog):
    """The main application window, orchestrating the title bar, sidebar, and content pages.

    This class serves as the central hub of the user interface. It's a frameless QDialog
    that incorporates a custom `TitleBar` for window controls, a collapsible `Sidebar` for
    navigation, and a `QStackedWidget` to display different application views (pages).
    It handles window resizing, positioning, and connects user actions from the UI
    (like button clicks in the sidebar) to the `NavigationService`.

    Attributes:
        start_geometry (QRect): The window's geometry at the start of a resize operation.
        animator (WindowAnimator): Handles window animations like minimize/maximize.
        title_bar (TitleBar): The custom title bar widget.
        sidebar (Sidebar): The navigation sidebar widget.
        sw_pages (QStackedWidget): The widget that holds and switches between different pages.
        navigation (NavigationService): The service responsible for page management and navigation.
        _is_maximized (bool): Tracks if the window is currently maximized.
        grips (dict[str, CustomGrip]): A dictionary of CustomGrip widgets for resizing.
    
    Signals:
        sidebar_toggle_requested: Emitted when the sidebar toggle button is clicked in the title bar.
    """
    # ── Signals ───────────────────────────────────────────────────────────────────────
    sidebar_toggle_requested = Signal()

    def __init__(
            self, 
            theme_controller: 'ThemeController', 
            navigation_service_factory: Callable[[QStackedWidget], 'NavigationService']
    ):
        """Initializes the MainWindow.

        Args:
            theme_controller (ThemeController): The controller for managing application themes.
            navigation_service_factory (callable): A factory function that creates an instance
                                                 of NavigationService, pre-configured with the
                                                 page container (QStackedWidget).
        """
        super().__init__()
        # ── Window Properties ──
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(800, 360)
        self.setObjectName("App")
        self.start_geometry = self.geometry()
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.resize(int(SETTINGS["WINDOW_WIDTH"]), int(SETTINGS["WINDOW_HEIGHT"]))
        self.center_on_screen()
        
        # ── Theme & Services ──
        self.theme_controller = theme_controller
        self.theme_controller.apply_full_theme()

        # ── Title Bar ──
        self.animator = WindowAnimator(self)
        self.title_bar = TitleBar(self)
        self._is_maximized = False
        self.central_layout.addWidget(self.title_bar)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.animator.animate_minimize)
        self.title_bar.maximize_clicked.connect(self.animator.animate_toggle_maximize)
        self.title_bar.sidebar_toggled.connect(self.sidebar_toggle_requested.emit)

        # ── Body Layout ──
        self.window_body = QWidget(self) 
        self.window_body.setObjectName("ApplicationWindow")
        self.body_layout = QHBoxLayout(self.window_body)
        self.body_layout.setContentsMargins(1, 0, 1, 1)
        self.body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar_toggle_requested.connect(self.sidebar.toggle)
        self.body_layout.addWidget(self.sidebar) # add sidebar to body layout

        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.body_layout.addWidget(self.content_area)
        self.central_layout.addWidget(self.window_body)

        # ── Stacked Pages ──
        self.sw_pages = QStackedWidget()
        self.content_layout.addWidget(self.sw_pages)

        # ── Initialize & Connect Navigation Service ──
        self.navigation: 'NavigationService' = navigation_service_factory(self.sw_pages)
        self.navigation.build_and_register_pages()
        self._connect_navigation_signals()

        # ── Create Grips ──
        self.grips = {}        
        grip_positions = [
            "top", "bottom", "left", "right",
            "top_left", "top_right", "bottom_left", "bottom_right"
        ]
        for pos in grip_positions:
            self.grips[pos] = CustomGrip(self, pos)
            self.grips[pos].raise_()
        
        self.navigation.switch_to("dashboard") # set initial page
        self.sidebar.buttons["btn_dashboard"].setChecked(True)
        
    def _connect_navigation_signals(self):
        """Connects the navigation buttons in the sidebar to the NavigationService's switch_to method."""
        # This logic is simplified from app.py
        button_map = {
            "btn_dashboard": "dashboard",
            "btn_meal_planner": "meal_planner",
            "btn_view_recipes": "view_recipes",
            "btn_shopping_list": "shopping_list",
            "btn_add_recipes": "add_recipe",
        }

        for btn_name, page_name in button_map.items():
            button = self.sidebar.buttons.get(btn_name)
            if button:
                # connect to the service, not a local method!
                button.clicked.connect(lambda _, p=page_name: self.navigation.switch_to(p))

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

        if self.animator.animation_group and self.animator.animation_group.state() == QPropertyAnimation.Running:
            return

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

# ── Title Bar  ──────────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    """A custom title bar for the frameless main window.

    Provides window control buttons (minimize, maximize, close), a sidebar toggle button,
    the application logo, and title. It also handles window dragging and maximizing on double-click.

    Attributes:
        old_pos (QPoint | None): Stores the last mouse position during a drag operation.
        logo (CTIcon): The application logo icon.
        title (QLabel): Label displaying the application title.
        btn_ico_toggle_sidebar (CTToolButton): Button to toggle the sidebar.
        btn_ico_minimize (CTToolButton): Button to minimize the window.
        btn_ico_maximize (CTToolButton): Button to maximize/restore the window.
        btn_ico_close (CTToolButton): Button to close the window.

    Signals:
        sidebar_toggled: Emitted when the sidebar toggle button is clicked.
        close_clicked: Emitted when the close button is clicked.
        minimize_clicked: Emitted when the minimize button is clicked.
        maximize_clicked: Emitted when the maximize/restore button is clicked.
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
        self.setFixedHeight(60)

        self.old_pos = None  # initialize old position for dragging

        # ── Title Label ──
        self.logo = CTIcon(
            file_path = APP_ICONS["LOGO"]["PATH"],
            icon_size = APP_ICONS["LOGO"]["SIZE"],
            variant   = APP_ICONS["LOGO"]["STATIC"],
        )
        self.logo.setFixedSize(32,32)
        self.logo.setObjectName("AppLogo")
        self.title = QLabel(SETTINGS["APP_NAME"])

        # ── Sidebar Toggle Button ──
        self.btn_ico_toggle_sidebar = CTToolButton(
            file_path = APP_ICONS["TOGGLE_SIDEBAR"]["PATH"],
            icon_size = APP_ICONS["TOGGLE_SIDEBAR"]["SIZE"],
            variant   = APP_ICONS["TOGGLE_SIDEBAR"]["DYNAMIC"],
            checkable = True,
        )
        self.btn_ico_toggle_sidebar.setFixedSize(SETTINGS["BTN_SIZE"])
        self.btn_ico_toggle_sidebar.setObjectName("BtnToggleSidebar")

        # ── Minimize Button ──
        self.btn_ico_minimize = CTToolButton(
            file_path = APP_ICONS["MINIMIZE"]["PATH"],
            icon_size = APP_ICONS["MINIMIZE"]["SIZE"],
            variant   = APP_ICONS["MINIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_minimize.setFixedSize(SETTINGS["BTN_SIZE"])

        # ── Maximize/Restore Button ──
        self.btn_ico_maximize = CTToolButton(
            file_path = APP_ICONS["MAXIMIZE"]["PATH"],
            icon_size = APP_ICONS["MAXIMIZE"]["SIZE"],
            variant   = APP_ICONS["MAXIMIZE"]["DYNAMIC"],
        )
        self.btn_ico_maximize.setFixedSize(SETTINGS["BTN_SIZE"])
        
        # ── Close Button ──
        self.btn_ico_close = CTToolButton(
            file_path = APP_ICONS["CLOSE"]["PATH"],
            icon_size = APP_ICONS["CLOSE"]["SIZE"],
            variant   = APP_ICONS["CLOSE"]["DYNAMIC"],
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
        title_bar_layout.addWidget(self.logo)
        title_bar_layout.addWidget(self.title)
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
            APP_ICONS["RESTORE"]["PATH"] if maximized else APP_ICONS["MAXIMIZE"]["PATH"]
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

# ── Sidebar ─────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """A collapsible sidebar widget for navigation.

    Provides the user avatar, username, and a vertical stack of navigation buttons
    (e.g., Dashboard, Meal Planner, Settings). It can be expanded or collapsed.

    Attributes:
        nav_button_group (QButtonGroup): Ensures that only one navigation button is active at a time.
        _is_expanded (bool): Tracks the current state (expanded or collapsed).
    """

    def __init__(self, parent=None):
        """Initializes the Sidebar.

        Args:
            parent (QWidget, optional): parent widget. Defaults to None.
        """
        super().__init__(parent)
        # properties
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(0)
        self.setMaximumWidth(START)  # start expanded
        self._is_expanded = True

        # main layout setup
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # avatar and username
        self._create_avatar()

        # navigation buttons
        self.nav_button_group = QButtonGroup(self) # button group for exclusive selection
        self.nav_button_group.setExclusive(True)
        self.btn_dashboard = self._create_nav_button("Dashboard")
        self.btn_meal_planner = self._create_nav_button("Meal Planner")
        self.btn_view_recipes = self._create_nav_button("View Recipes")
        self.btn_shopping_list = self._create_nav_button("Shopping List")
        self.btn_add_recipes = self._create_nav_button("Add Recipes")

        # bottom spacer to push settings/exit to the bottom
        self.mainLayout.addItem(QSpacerItem(212, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # settings and exit buttons
        self.btn_settings = self._create_nav_button("Settings", is_checkable=False)
        self.btn_exit = self._create_nav_button("Exit", is_checkable=False)

    @property
    def buttons(self) -> dict[str, NavButton]:
        """Provides access to all buttons in the sidebar.

        Returns:
            dict[str, NavButton]: A mapping of button object names to their NavButton instances.
        """
        return {
            "btn_dashboard": self.btn_dashboard,
            "btn_meal_planner": self.btn_meal_planner,
            "btn_view_recipes": self.btn_view_recipes,
            "btn_shopping_list": self.btn_shopping_list,
            "btn_add_recipes": self.btn_add_recipes,
            "btn_settings": self.btn_settings,
            "btn_exit": self.btn_exit,
        }
    
    @property
    def is_expanded(self) -> bool:
        """Check if the sidebar is currently expanded.

        Returns:
            bool: True if expanded, False if collapsed.
        """
        return self._is_expanded
    
    def toggle(self):
        """Toggle the sidebar's expanded/collapsed state."""
        DebugLogger.log(f"Toggling sidebar: currently {'expanded' if self._is_expanded else 'collapsed'}")

        start = self.maximumWidth()
        end = END if self._is_expanded else START
        duration = DURATION

        Animator.animate_width(self, start, end, duration)

        self._is_expanded = not self._is_expanded
        
    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _create_nav_button(
            self, 
            label: str, 
            is_checkable: bool = True
    ) -> NavButton:
        """Creates and configures a single navigation button.

        The button's icon is determined by its label, which must correspond to an
        entry in the `SIDEBAR["ICONS"]` configuration.

        Args:
            label (str): The text label for the button (e.g., "Dashboard").
            is_checkable (bool): If True, the button is added to an exclusive button group.

        Returns:
            NavButton: The newly created navigation button.
        """
        icon_info = SIDEBAR_ICONS[label.replace(" ", "_").upper()]
        object_name = f"{label.replace(' ', '_')}Button"

        button = NavButton(
            file_path = icon_info["PATH"],
            icon_size = icon_info["SIZE"],
            variant   = icon_info["DYNAMIC"],
            text      = label,
            checkable = is_checkable,
            height    = 82,
        )
        button.setObjectName(object_name)
        self.mainLayout.addWidget(button)

        if is_checkable:
            self.nav_button_group.addButton(button)

        return button
    
    def _create_avatar(self) -> AvatarLoader:
        """Creates and adds the avatar and username section to the sidebar."""
        avatar = AvatarLoader(size=QSize(240, 240))
        username = QLabel("@username")  # placeholder for username, set dynamically
        username.setObjectName("UsernameLabel")
        username.setAlignment(Qt.AlignCenter)
        avatar_wrapper = create_fixed_wrapper(
            widgets     = [avatar, username],
            fixed_width = self.width(),
            alignment   = Qt.AlignHCenter,
            direction   = "vertical",
            margins= (0, 40, 0, 30)
        )
        self.mainLayout.addWidget(avatar_wrapper)

