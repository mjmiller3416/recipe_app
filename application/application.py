from qt_imports import (
    Qt, QMainWindow, QVBoxLayout, QHBoxLayout, QFrame, QWidget, 
    QStackedWidget, QApplication, QLabel, QPropertyAnimation,
    QEasingCurve)

# 🔹 Local Imports
from app.application.title_bar import TitleBar
from app.application.sidebar_widget import SidebarWidget
from app.dashboard.dashboard import Dashboard
from meal_planner.meal_planner import MealPlanner
from app.view_recipes.view_recipes import ViewRecipes
from app.shopping_list.shopping_list import ShoppingList
from add_recipes.add_recipes import AddRecipes
from app.widgets.search_widget import SearchWidget
from app.helpers.ui_helpers import SidebarAnimator
from animation_manager import AnimationManager
from debug_logger import DebugLogger

class Application(QMainWindow):
    """
    Main application window with a custom title bar, sidebar, header, and dynamic stacked content.
    Applies custom styling and manages navigation.
    """
    def __init__(self):
        super().__init__()

        self.setObjectName("Application")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1280, 720) # Set minimum size for the window
        self.sidebar_is_expanded = True

        # 🔹 Outer Wrapper for styling (rounded corners, shadows)
        self.wrapper = QFrame()
        self.wrapper.setObjectName("ApplicationWrapper")
        self.setCentralWidget(self.wrapper)

        self.outer_layout = QVBoxLayout(self.wrapper)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # 🔹 Custom Title Bar
        self.title_bar = TitleBar(self)
        self.outer_layout.addWidget(self.title_bar)
        self.title_bar.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)

        # 🔹 Main App Layout (Sidebar + Content)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.outer_layout.addLayout(self.main_layout)

        # 🔹 Sidebar
        self.sidebar = SidebarWidget()
        self.main_layout.addWidget(self.sidebar)

        # 🔹 Main Content Container (Header + Pages)
        self.content_wrapper = QVBoxLayout()
        self.content_wrapper.setContentsMargins(0, 0, 0, 0)
        self.content_wrapper.setSpacing(0)
        self.main_layout.addLayout(self.content_wrapper)

        # 🔹 Header
        self.header = QWidget()
        self.header.setObjectName("Header")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(20, 12, 20, 12)
        self.header_layout.setSpacing(20)

        # 🔹 Welcome Message Group
        self.greeting_container = QWidget(self.header) # Create a container for the greeting labels
        self.greeting_container.setObjectName("greeting_container")

        greeting_layout = QVBoxLayout(self.greeting_container) # Use a vertical layout for the greeting labels
        greeting_layout.setContentsMargins(0, 0, 0, 0)
        greeting_layout.setSpacing(0)

        self.lbl_greeting = QLabel("Welcome Back,", self.greeting_container) # Greeting label
        self.lbl_greeting.setObjectName("lbl_greeting")

        self.lbl_username = QLabel("MARYANN", self.greeting_container) # Username label
        self.lbl_username.setObjectName("lbl_username")

        greeting_layout.addWidget(self.lbl_greeting) # Add labels to the layout
        greeting_layout.addWidget(self.lbl_username)

        self.header_layout.addWidget(self.greeting_container) # Add the greeting container to the header layout

        self.search_widget = SearchWidget()
        self.search_widget.setMaximumHeight(36)
        self.search_widget.setFixedWidth(300)
        self.header_layout.addWidget(self.search_widget, alignment=Qt.AlignRight)

        self.content_wrapper.addWidget(self.header)

        # 🔹 Stacked Pages
        self.sw_pages = QStackedWidget()
        self.content_wrapper.addWidget(self.sw_pages)

        self.page_instances = self.build_pages() # Build page instances

        for name, page in self.page_instances.items():
            self.sw_pages.addWidget(page)

        self.connect_navigation()
        self.switch_page("dashboard")

    def build_pages(self):
        """Instantiate and return all page instances for the stacked widget."""
        return {
            "dashboard": Dashboard(),
            "meal_planner": MealPlanner(),
            "view_recipes": ViewRecipes(),
            "shopping_list": ShoppingList(),
            "add_recipe": AddRecipes(),
        }

    def connect_navigation(self):
        """Connect sidebar navigation buttons to stacked widget."""
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
                button.clicked.connect(lambda _, p=page_name: self.switch_page(p))

        # Exit button
        self.sidebar.buttons["btn_exit"].clicked.connect(self.handle_close)

        # TitleBar close override
        self.title_bar.btn_close.clicked.disconnect()
        self.title_bar.btn_close.clicked.connect(self.handle_close)

    def switch_page(self, page_name):
        """Switch stacked widget to the given page.

        Args:
            page_name (str): The name of the page to switch to. Must match the keys in page_instances.
        
        """
        if page_name in self.page_instances:
            next_widget = self.page_instances[page_name]
            current_widget = self.sw_pages.currentWidget()

            if current_widget != next_widget:
                AnimationManager.transition_stack(current_widget, next_widget, self.sw_pages)
    
    def toggle_sidebar(self):
        """ Toggle the sidebar's expanded/collapsed state with animation."""
        collapsed_width = 0
        expanded_width = 215

        start_width = self.sidebar.width()
        end_width = collapsed_width if self.sidebar_is_expanded else expanded_width

        self.sidebar_animator = SidebarAnimator(self.sidebar)

        self.sidebar_animation = QPropertyAnimation(self.sidebar_animator, b"value")
        self.sidebar_animation.setDuration(500)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.OutExpo)

        self.sidebar_animation.start()
        self.sidebar_is_expanded = not self.sidebar_is_expanded

    def handle_close(self):
        """Custom logic before application closes."""
        self.page_instances["meal_planner"].save_all_meals()
        self.page_instances["meal_planner"].save_meal_plan()
        QApplication.quit()

    
