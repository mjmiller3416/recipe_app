"""app/ui/pages/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QStackedWidget

from app.config import AppIcon
from app.core.services.planner_service import PlannerService
from app.ui.components.composite import MealWidget
from app.theme_manager.icon import Icon
from dev_tools import DebugLogger, StartupTimer
from app.ui.views.recipe_selection import RecipeSelection


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
        # initialize PlannerService; session managed internally
        self.planner_service = PlannerService()

        self.setObjectName("MealPlanner")
        DebugLogger.log("Initializing MealPlanner page", "debug")

        # ── Create planner and selection widgets ──
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(16, 16))
        self.meal_tabs.setTabsClosable(False)
        self.meal_tabs.setMovable(True)
        self.meal_tabs.tabBarClicked.connect(self.handle_tab_click)
        # create the in-page recipe selection view
        self.selection_page = RecipeSelection(self)
        # handle when a recipe is selected from the selection page
        self.selection_page.recipe_selected.connect(self._finish_recipe_selection)

        # stacked widget to switch between planner tabs and selection page
        self.stack = QStackedWidget()
        self.stack.addWidget(self.meal_tabs)
        self.stack.addWidget(self.selection_page)

        # ── Layout ──
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.stack)
        # show the planner view by default
        self.stack.setCurrentIndex(0)

        self.tab_map = {}  # {tab_index: MealWidget}
        # context for in-page recipe selection (widget, slot_key)
        self._selection_context = None

        self.init_ui()

    def init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self.new_meal_tab()  # add the "+" tab (used to add new meals)

        try:
            meal_ids = self.planner_service.load_saved_meal_ids()
            DebugLogger.log(f"[MealPlanner] Restoring saved meal IDs: {meal_ids}", "info")

            for meal_id in meal_ids:
                self.add_meal_tab(meal_id=meal_id)

            if not meal_ids:
                self.add_meal_tab()
        except Exception as e:
            DebugLogger.log(f"[MealPlanner] Error loading saved meals: {e}", "error")
            self.add_meal_tab()  # Fallback to empty tab

    def new_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        new_meal_tab = QWidget()
        icon_asset = Icon(AppIcon.MEAL_PLANNER_ADD)
        icon = icon_asset.pixmap()

        index = self.meal_tabs.addTab(new_meal_tab, icon, "")
        self.meal_tabs.setTabToolTip(index, "Add Meal")

    def add_meal_tab(self, meal_id: int = None):
        widget = MealWidget(self.planner_service)  # pass the service here
        if meal_id:
            widget.load_meal(meal_id)
        # hook into slot add events to open selection page
        widget.recipe_selection_requested.connect(
            lambda key, w=widget: self._start_recipe_selection(w, key)
        )

        insert_index = self.meal_tabs.count() - 1
        index = self.meal_tabs.insertTab(insert_index, widget, "Custom Meal")
        self.tab_map[index] = widget
        self.meal_tabs.setCurrentIndex(index)

    def handle_tab_click(self, index: int):
        """Handle when the '+' tab is clicked to add a new tab."""
        if index == self.meal_tabs.count() - 1:
            self.add_meal_tab()

    def _start_recipe_selection(self, widget, slot_key: str):
        """Begin in-page recipe selection for the given meal slot."""
        # Store context for callback
        self._selection_context = (widget, slot_key)
        # Reset selection browser
        try:
            self.selection_page.browser.load_recipes()
        except Exception:
            pass
        # Show selection page
        self.stack.setCurrentIndex(1)

    def _finish_recipe_selection(self, recipe_id: int):
        """Handle recipe selected from the selection page."""
        if not self._selection_context:
            return
        widget, slot_key = self._selection_context
        widget.update_recipe_selection(slot_key, recipe_id)
        # Return to planner view
        self.stack.setCurrentIndex(0)
        self._selection_context = None

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
        result = self.planner_service.save_meal_plan(saved_ids)

        if result.success:
            DebugLogger.log(f"[MealPlanner] {result.message}", "info")
        else:
            DebugLogger.log(f"[MealPlanner] Failed to save: {result.message}", "error")

    def closeEvent(self, event):
        # persist planner state before closing
        super().closeEvent(event)

