# Package: app

# Description: This file contains the StyleManager class, which is responsible for managing the styling of the application.
# The StyleManager class applies styles to the application's UI elements, including buttons, labels, and icons. It also
# handles hover effects for buttons and dynamically changes the color of SVG icons. The StyleManager class is initialized
# with an Application instance and automatically applies styles when initialized.

from functools import partial
#🔸Standard Library
from typing import Union

#🔸Third-party
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QGraphicsDropShadowEffect,
                               QMainWindow, QPushButton, QToolButton,
                               QVBoxLayout, QWidget)

from core.application.config import (ICON_COLOR, ICON_COLOR_CHECKED,
                                     ICON_COLOR_HOVER, LOGO_COLOR, image_path)
#🔸Local Imports
from core.helpers.style_loader import StyleLoader

#🔹MARGINS        ←  ↑  →  ↓
SIDEBAR_MARGINS = 0, 18, 0, 18

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

        self.style_loader = StyleLoader()
        self.app = app_instance
        self.apply_styles()

    def apply_styles(self):
        """
        Applies base QSS styles + widget-specific enhancements.
        """
        from core.helpers.ui_helpers import \
            get_all_buttons  # Local import for button icons⚠️⚠️⚠️
        from core.helpers.ui_helpers import \
            svg_loader  # Local import for SVG loader⚠️⚠️⚠️

        # Load and apply stylesheets (global styles)
        base_stylesheet = self.style_loader.load_styles("base")

        application_stylesheet = self.style_loader.load_styles("application")
        dashboard_stylesheet = self.style_loader.load_styles("dashboard")
        meal_planner_stylesheet = self.style_loader.load_styles("meal_planner")
        view_recipes_stylesheet = self.style_loader.load_styles("view_recipes")
        shopping_list_stylesheet = self.style_loader.load_styles("shopping_list")
        add_recipes_stylesheet = self.style_loader.load_styles("add_recipes")
        recipe_widget_stylesheet = self.style_loader.load_styles("recipe_widget")
        dialog_widget_stylesheet = self.style_loader.load_styles("dialog_widget")

        combined_styles = (
            base_stylesheet + application_stylesheet + dashboard_stylesheet +
            meal_planner_stylesheet + view_recipes_stylesheet + shopping_list_stylesheet +
            add_recipes_stylesheet + recipe_widget_stylesheet + dialog_widget_stylesheet
        )

        app_instance = QApplication.instance()
        if app_instance:
            app_instance.setStyleSheet(combined_styles)

        # Style for SidebarWidget
        if isinstance(self.app, QWidget) and self.app.objectName() == "SidebarWidget":
            # Change the logo color
            if hasattr(self.app, 'lbl_logo'):
                img_logo = svg_loader(
                    image_path("logo"), LOGO_COLOR, size=self.app.lbl_logo.size(),
                    return_type=QPixmap, source_color="#000"
                    )
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
    def apply_hover_effects(
        buttons: QPushButton | QToolButton |list | dict,
        size: tuple[int, int] | QSize | None = None,
        default_color: str = ICON_COLOR,
        hover_color: str   = ICON_COLOR_HOVER,
        checked_color: str = ICON_COLOR_CHECKED,
    ) -> None:
        """
        Applies hover effects to QPushButton(s) by swapping icons on enter/leave and toggle.

        Args:
            buttons: Single button, list of buttons, or dict of buttons.
            size:    Icon size as (width, height) or QSize. If provided, sets iconSize.
            default_color: Color for the normal state.
            hover_color:   Color for the hover state.
            checked_color: Color when button.isChecked() == True.
        """
        from core.helpers.ui_helpers import \
            get_button_icons  # Local import for button icons⚠️⚠️⚠️
        from core.helpers.ui_helpers import \
            svg_loader  # Local import for SVG loader⚠️⚠️⚠️

        # normalize buttons into a list
        if isinstance(buttons, (QPushButton, QToolButton)):
            buttons = [buttons]
        elif isinstance(buttons, dict):
            buttons = list(buttons.values())

        icon_paths = get_button_icons({btn.objectName(): btn for btn in buttons})

        for btn in buttons:
            name = btn.objectName()
            svg_path = icon_paths.get(name)
            if not svg_path:
                continue

            # build all three icons with the passed-in colors
            orig_icon = svg_loader(svg_path, default_color, size, return_type=QIcon, source_color="#000")
            hov_icon  = svg_loader(svg_path, hover_color,   size, return_type=QIcon, source_color="#000")
            chk_icon  = svg_loader(svg_path, checked_color, size, return_type=QIcon, source_color="#000")

            if orig_icon.isNull() or hov_icon.isNull():
                continue

            # set initial icon & size
            btn.setIcon(chk_icon if btn.isChecked() else orig_icon)
            if size:
                btn.setIconSize(QSize(*size) if isinstance(size, tuple) else size)

            # needed for enter/leave events
            btn.setMouseTracking(True)

            # hover handlers
            def on_enter(event, b=btn, ic=hov_icon):
                if not b.isChecked():
                    b.setIcon(ic)
            def on_leave(event, b=btn, ic=orig_icon):
                if not b.isChecked():
                    b.setIcon(ic)

            btn.enterEvent = partial(on_enter)
            btn.leaveEvent = partial(on_leave)

            # toggle handler
            btn.toggled.connect(lambda checked, b=btn, o=orig_icon, c=chk_icon: b.setIcon(c if checked else o))

