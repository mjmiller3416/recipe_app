# recipe_app/meal_planner/meal_planner.py
"""
Module: meal_planner.meal_planner

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# 🔸 Local Application Imports
from helpers.app_helpers.debug_logger import DebugLogger

from config.config import icon_path
# 🔸 Third-party Imports
from core.helpers.qt_imports import (QIcon, QSize, QTabWidget, QVBoxLayout,
                                     QWidget)
from core.helpers.ui_helpers import svg_loader

from .meal_helpers import load_meal_plan, save_all_meals, save_meal_plan
from .planner_layout import PlannerLayout


class MealPlanner(QWidget):
    """
    The MealPlanner class manages a tabbed interface for creating, editing,
    and saving meal plans within the application.

    Atributes:
        meal_tabs (QTabWidget): The tab widget to manage meal planning tabs.
        layout (QVBoxLayout): The main layout for the MealPlanner widget.
        tab_map (dict): Maps tab indices to their respective PlannerLayout and meal_id.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("MealPlanner")

        # Create a QTabWidget to manage multiple meal plan tabs
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(16, 16))
        self.meal_tabs.setTabsClosable(False)
        self.meal_tabs.setMovable(True)

        # Layout setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.meal_tabs)

        # Mapping of tab index to its layout and associated meal_id (if saved)
        self.tab_map = {}  # {index: {"layout": PlannerLayout, "meal_id": int or None}}

        self.init_ui()
        self.meal_tabs.tabBarClicked.connect(self.handle_tab_click)

    def init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self.add_meal_tab()  # Add the "+" tab (used to add new meals)
        if not load_meal_plan(callback=self.meal_tab):
            self.meal_tab()  # Load an empty meal tab if no saved meals found

    def add_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        plus_tab = QWidget()
        icon = svg_loader(icon_path("add"), "#949aa7", size=(16, 16), return_type=QIcon, source_color="#000")
        index = self.meal_tabs.addTab(plus_tab, icon, "")
        self.meal_tabs.setTabToolTip(index, "Add Meal")

    def handle_tab_click(self, index):
        """
        Check if '+' tab was clicked, and open a new meal tab if so.

        Args:
            index (int): The index of the clicked tab.
        """
        if index == self.meal_tabs.count() - 1:
            self.meal_tab()

    def meal_tab(self, meal_data=None, meal_id=None):
        """
        Create a new meal planning tab and insert it before the '+' tab.

        Args:
            meal_data (dict, optional): Pre-populated meal data to set in the new tab.
            meal_id (int, optional): Meal ID for existing meals to update.
        """
        layout = PlannerLayout()

        if meal_data:
            layout.set_meal_data(meal_data)

        insert_index = self.meal_tabs.count() - 1
        index = self.meal_tabs.insertTab(insert_index, layout, "Custom Meal")

        self.tab_map[index] = {"layout": layout, "meal_id": meal_id}
        self.meal_tabs.setCurrentIndex(index)

        DebugLogger.log(f"New meal tab added. Index: {index}, Meal ID: {meal_id}", "info")

    def save_meal_plan(self):
        """Save the list of currently open meal IDs to QSettings."""
        save_meal_plan(self.tab_map)

    def save_all_meals(self):
        """
        Save all open meals to the database.
        New meals are inserted, while existing ones are updated.
        """
        save_all_meals(self.tab_map)

    def get_current_meal_data(self):
        """
        Return meal data from the currently active tab, or None if unavailable.

        Returns:
            dict or None: The meal data from the currently active tab's PlannerLayout, or None if no valid layout is found.
        """
        index = self.meal_tabs.currentIndex()
        if index in self.tab_map:
            return self.tab_map[index]["layout"].get_meal_data()
        return None

    def clear_all_tabs(self):
        """Remove all meal tabs and reset internal state."""
        self.meal_tabs.clear()
        self.tab_map.clear()
        DebugLogger.log("All meal planner tabs cleared.", "warning")
