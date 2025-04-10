# Package: app

# Description: This file contains the StyleManager class, which is responsible for managing the styling of the application.
# The StyleManager class applies styles to the application's UI elements, including buttons, labels, and icons. It also
# handles hover effects for buttons and dynamically changes the color of SVG icons. The StyleManager class is initialized
# with an Application instance and automatically applies styles when initialized.

#🔸System Imports
import os

#🔸Third-party Imports 
from core.helpers.qt_imports import(
    QSize, QPushButton, QGraphicsDropShadowEffect, QColor, QVBoxLayout, 
    QMainWindow, QWidget, QApplication, QPixmap, QIcon, QToolButton)

#🔸Local Imports
from functools import partial
from core.helpers import svg_loader

#🔹STATIC COLORS
TITLEBAR_ICON_COLOR = "#949aa7"  
TITLEBAR_ICON_HOVER = "#03B79E"  # Color for hover state of title bar icons
ICON_DEFAULT_COLOR = "#949aa7"
ICON_HOVER_COLOR = "#03B79E"
ICON_CHECKED_COLOR = "#03B79E"
LOGO_COLOR = "#949aa7"

#🔹DIALOG COLORS
SUCCESS_COLOR = "#5cde42"
ERROR_COLOR = "#ff4d4d"
WARNING_COLOR = "#ffcc00"
INFO_COLOR = "#03B79E"

#🔹MARGINS        ←  ↑  →  ↓
SIDEBAR_MARGINS = 0, 18, 0, 18

class StyleLoader:
    """
    Loads and concatenates QSS stylesheets from the /styles directory.
    """

    def __init__(self, style_dir=None):
        """
        Initialize StyleLoader with a default relative path to the styles directory.
        """
        if style_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.style_dir = os.path.join(current_dir, "styles")
        else:
            self.style_dir = style_dir

    def load_styles(self, *files):
        """
        Loads specific .qss files from the style directory.

        Args:
            *files (str): One or more stylesheet filenames (without extension).

        Returns:
            str: Combined QSS content.
        """
        stylesheet = ""
        for file in files:
            path = os.path.join(self.style_dir, f"{file}.qss")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    stylesheet += f.read() + "\n"
            else:
                print(f"[StyleLoader] ⚠️ File not found: {path}")
        return stylesheet

    def load_all_styles(self):
        """
        Loads all .qss files from the style directory.

        Returns:
            str: Combined QSS content.
        """
        stylesheet = ""
        for filename in os.listdir(self.style_dir):
            if filename.endswith(".qss"):
                path = os.path.join(self.style_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    stylesheet += f.read() + "\n"
        return stylesheet

class StyleManager:
    """
    A helper class to manage UI styling, including button hover effects and SVG color changes.
    Automatically applies styles when initialized with an Application instance.
    """

    def __init__(self, app_instance):
        """
        Initialize StyleManager and apply styles to the given application instance.

        Args:
            app_instance (Application): The main application instance.
        """
        from style_manager import StyleLoader

        self.style_loader = StyleLoader()

        self.app = app_instance
        self.apply_styles()

    def apply_styles(self):
        """
        Applies base QSS styles + widget-specific enhancements.
        """
        from core.helpers.ui_helpers import get_all_buttons

        # Load and apply stylesheets (global styles)
        base_stylesheet = self.style_loader.load_styles("base")  
        
        application_stylesheet = self.style_loader.load_styles("application")
        dashboard_stylesheet = self.style_loader.load_styles("dashboard")
        meal_planner_stylesheet = self.style_loader.load_styles("meal_planner")
        view_recipes_stylesheet = self.style_loader.load_styles("view_recipes")
        shopping_list_stylesheet = self.style_loader.load_styles("shopping_list")
        add_recipes_stylesheet = self.style_loader.load_styles("add_recipes")
        recipe_card_stylesheet = self.style_loader.load_styles("recipe_card")
        dialog_widget_stylesheet = self.style_loader.load_styles("dialog_widget")

        combined_styles = ( 
            base_stylesheet + application_stylesheet + dashboard_stylesheet + 
            meal_planner_stylesheet + view_recipes_stylesheet + shopping_list_stylesheet + 
            add_recipes_stylesheet + recipe_card_stylesheet + dialog_widget_stylesheet
        )

        app_instance = QApplication.instance()
        if app_instance:
            app_instance.setStyleSheet(combined_styles)

        # Style for SidebarWidget
        if isinstance(self.app, QWidget) and self.app.objectName() == "SidebarWidget":
            # Change the logo color
            if hasattr(self.app, 'lbl_logo'):
                img_logo = svg_loader(":/logo/logo.svg", LOGO_COLOR, size=self.app.lbl_logo.size(), return_type=QPixmap, crisp=False)
                self.app.lbl_logo.setPixmap(img_logo)

            # Apply sidebar margins
            layout = self.app.layout()
            if isinstance(layout, QVBoxLayout):
                layout.setContentsMargins(*SIDEBAR_MARGINS)

            # Apply hover effects to all buttons
            StyleManager.apply_hover_effects(get_all_buttons(self.app), (24, 24))

        elif isinstance(self.app, QWidget) and self.app.objectName() == "SearchWidget":

            if hasattr(self.app, 'btn_clear'):
                StyleManager.apply_hover_effects(self.app.btn_clear, (18, 18))

        # Optional future styling for main QMainWindow
        elif isinstance(self.app, QMainWindow):
            pass

    @staticmethod
    def shadow_effect(widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(80)  # exaggerated for testing
        shadow.setXOffset(20)
        shadow.setYOffset(20)
        shadow.setColor(QColor(255, 0, 0, 160))  # bright red shadow for visibility
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def apply_hover_effects(buttons, size=None):
        """
        Applies hover effects to QPushButton(s) by changing their icons dynamically.

        Args:
            buttons (QPushButton | list[QPushButton] | dict): A single button, list of buttons, or dictionary of buttons.
            size (tuple, optional): Icon size as (width, height). Defaults to None.
        """
        from core.helpers.ui_helpers import get_button_icons, svg_loader

        # Ensure buttons is iterable
        if isinstance(buttons, (QPushButton, QToolButton)):
            buttons = [buttons]
        elif isinstance(buttons, dict):
            buttons = list(buttons.values())

        icon_paths = get_button_icons({btn.objectName(): btn for btn in buttons})

        for button in buttons:
            name = button.objectName()
            svg_path = icon_paths.get(name)

            if not svg_path:
                continue  # Skip buttons without valid icons

            # Load default, hover, and checked icons
            original_icon = svg_loader(svg_path, ICON_DEFAULT_COLOR, size, return_type=QIcon)
            hover_icon = svg_loader(svg_path, ICON_HOVER_COLOR, size, return_type=QIcon)
            checked_icon = svg_loader(svg_path, ICON_CHECKED_COLOR, size, return_type=QIcon)

            if original_icon.isNull() or hover_icon.isNull():
                continue  # Skip if icons fail to load

            # Apply the default or checked icon
            button.setIcon(checked_icon if button.isChecked() else original_icon)
            if size:
                button.setIconSize(QSize(*size))

            # Enable mouse tracking on button
            button.setMouseTracking(True)  

            # Define hover functions
            def change_to_hover(event, btn=button, icon=hover_icon):
                print(f"[Hover ON] {btn.objectName()}")
                if not btn.isChecked():
                    btn.setIcon(icon)

            def restore_original(event, btn=button, icon=original_icon):
                print(f"[Hover OFF] {btn.objectName()}")
                if not btn.isChecked():
                    btn.setIcon(icon)

            # Hook up hover events
            button.enterEvent = partial(change_to_hover)
            button.leaveEvent = partial(restore_original)

            # Also update on toggle change
            def update_icon(checked, btn=button, orig=original_icon, chk=checked_icon):
                btn.setIcon(chk if checked else orig)

            button.toggled.connect(update_icon)

