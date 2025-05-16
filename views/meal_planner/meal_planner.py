""" views/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from core.helpers import DebugLogger
from ui.iconkit import ThemedIcon
from .planner_layout import PlannerLayout
from config import MEAL_PLANNER
from services.meal_planner_service import (
    get_saved_meal_ids,
    get_meal_by_id,
    save_meal,
    update_meal,
    save_active_meal_ids,
)

# ── Class Definition ────────────────────────────────────────────────────────────
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

        # ── Create QTab Widget ──
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(16, 16))
        self.meal_tabs.setTabsClosable(False)
        self.meal_tabs.setMovable(True)

        # ── Layout Setup ──
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.meal_tabs)

        # ── Map Tab Index ──
        self.tab_map = {}  # {index: {"layout": PlannerLayout, "meal_id": int or None}}

        self.init_ui()
        self.meal_tabs.tabBarClicked.connect(self.handle_tab_click)

    def init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self.add_meal_tab()  # add the "+" tab (used to add new meals)

        loaded = False
        meal_ids = get_saved_meal_ids()
        DebugLogger.log(f"[MealPlanner.init_ui] Loaded saved meal IDs: {meal_ids}", "info")
        for meal_id in get_saved_meal_ids():
            data = get_meal_by_id(meal_id)
            self.meal_tab(meal_data=data, meal_id=meal_id)
            loaded = True

        if not loaded:
            self.meal_tab()  # load a blank custom meal tab

    def add_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        plus_tab = QWidget()
        icon_asset = ThemedIcon(
            file_path = MEAL_PLANNER["ICON_ADD"],
            size      = MEAL_PLANNER["ICON_SIZE"],
            variant   = MEAL_PLANNER["VARIANT"]
        )
        icon = icon_asset.pixmap()
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

    def save_all_meals(self):
        """
        Save all open meals to the database.
        New meals are inserted, while existing ones are updated.
        """
        for index, tab_info in self.tab_map.items():
            layout = tab_info["layout"]
            meal_id = tab_info.get("meal_id")
            data = layout.get_meal_data()

            if not data.get("main"):
                DebugLogger.log(f"[MealPlanner] Skipped saving tab {index}: No main recipe selected.", "warning")
                continue

            if meal_id is None:
                new_id = save_meal(data)
                self.tab_map[index]["meal_id"] = new_id
                DebugLogger.log(f"[MealPlanner] Created meal ID: {new_id} for tab {index}", "success")
            else:
                update_meal(meal_id, data)
                DebugLogger.log(f"[MealPlanner] Updated meal ID: {meal_id} for tab {index}", "info")

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

    def save_meal_plan(self):
        """
        Save currently open meal IDs to persistent storage for restoration.
        """

        meal_ids = [
            tab_info["meal_id"]
            for tab_info in self.tab_map.values()
            if tab_info.get("meal_id") is not None
        ]
        save_active_meal_ids(meal_ids)
        DebugLogger.log(f"[MealPlanner] Saved tab meal IDs: {meal_ids}", "info")