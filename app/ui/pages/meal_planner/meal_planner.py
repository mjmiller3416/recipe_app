"""app/ui/pages/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from app.config import MEAL_PLANNER
from app.core.services.planner_service import PlannerService
from app.core.dev_tools import DebugLogger, StartupTimer
from app.ui.components.widgets import CTIcon

from .meal_widget import MealWidget


# ── Class Definition ────────────────────────────────────────────────────────────
class MealPlanner(QWidget):
    """
    The MealPlanner class manages a tabbed interface for creating, editing,
    and saving meal plans within the application.

    Atributes:
        meal_tabs (QTabWidget): The tab widget to manage meal planning tabs.
        layout (QVBoxLayout): The main layout for the MealPlanner widget.
        tab_map (dict): Maps tab indices to their respective MealWidget and meal_id.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MealPlanner")

        DebugLogger.log("Initializing MealPlanner page", "debug")

        # ── Create Layout ──
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(16, 16))
        self.meal_tabs.setTabsClosable(False)
        self.meal_tabs.setMovable(True)
        self.meal_tabs.tabBarClicked.connect(self.handle_tab_click)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.meal_tabs)

        self.tab_map = {} # {tab_index: MealWidget}

        self.init_ui()

    def init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self.new_meal_tab()  # add the "+" tab (used to add new meals)

        meal_ids = PlannerService.load_saved_meal_ids()
        DebugLogger.log(f"[MealPlanner] Restoring saved meal IDs: {meal_ids}", "info")

        for meal_id in meal_ids:
            self.add_meal_tab(meal_id=meal_id)

        if not meal_ids:
            self.add_meal_tab()

    def new_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        new_meal_tab = QWidget()
        icon_asset = CTIcon(
            file_path = MEAL_PLANNER["ICON_ADD"],
            icon_size      = MEAL_PLANNER["ICON_SIZE"],
            variant   = MEAL_PLANNER["STATIC"]
        )
        icon = icon_asset.pixmap()

        index = self.meal_tabs.addTab(new_meal_tab, icon, "")
        self.meal_tabs.setTabToolTip(index, "Add Meal")

    def add_meal_tab(self, meal_id: int = None):
        """
        Add a new MealWidget tab just before the '+' tab.

        Args:
            meal_id (int, optional): If provided, loads the meal with this ID.
        """
        widget = MealWidget()
        if meal_id:
            widget.load_meal(meal_id)

        insert_index = self.meal_tabs.count() - 1
        index = self.meal_tabs.insertTab(insert_index, widget, "Custom Meal")
        self.tab_map[index] = widget
        self.meal_tabs.setCurrentIndex(index)

    def handle_tab_click(self, index: int):
        """Handle when the '+' tab is clicked to add a new tab."""
        if index == self.meal_tabs.count() - 1:
            self.add_meal_tab()

    def get_active_meal_ids(self) -> list[int]:
        """
        Collect and return all valid meal IDs from current tabs.

        Returns:
            list[int]: List of meal IDs currently active in the planner.
        """
        ids = []
        for widget in self.tab_map.values():
            if widget._meal_model and widget._meal_model.id:
                ids.append(widget._meal_model.id)
        return ids

    def save_meal_plan(self):
        """Save all meals and their corresponding tab state."""
        for widget in self.tab_map.values():
            widget.save_meal()

        saved_ids = self.get_active_meal_ids()
        PlannerService.save_active_meal_ids(saved_ids)
        DebugLogger.log(f"[MealPlanner] Saved planner state with meal IDs: {saved_ids}", "info")

    