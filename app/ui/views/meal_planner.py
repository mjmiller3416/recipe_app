"""app/ui/pages/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMenu, QStackedWidget, QTabWidget, QVBoxLayout, QWidget

from app.core.services.planner_service import PlannerService
from app.style.icon import AppIcon, Icon
from app.style import Theme, Qss
from app.ui.components.composite import MealWidget
from app.ui.views.recipe_selection import RecipeSelection
from dev_tools import DebugLogger


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
        # register for component-specific styling
        Theme.register_widget(self, Qss.MEAL_PLANNER)
        DebugLogger.log("Initializing MealPlanner page", "info")

        # ── Create planner and selection widgets ──
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(32, 32))  # Increase icon size
        self.meal_tabs.setTabsClosable(False)
        self.meal_tabs.setMovable(True)
        self.meal_tabs.tabBarClicked.connect(self._handle_tab_click)
        self.meal_tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.meal_tabs.customContextMenuRequested.connect(self._show_context_menu)
        # create the in-page recipe selection view
        self.selection_page = RecipeSelection(self)
        # handle when a recipe is selected from the selection page
        self.selection_page.recipe_selected.connect(self._finish_recipe_selection)

        # stacked widget to switch between planner tabs and selection page
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.meal_tabs)
        self.stack.addWidget(self.selection_page)

        # ── Layout ──
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(140, 40, 140, 40)
        self.layout.addWidget(self.stack, 0, Qt.AlignHCenter)
        # show the planner view by default
        self.stack.setCurrentIndex(0)

        self.tab_map = {}  # {tab_index: MealWidget}
        # context for in-page recipe selection (widget, slot_key)
        self._selection_context = None

        self._init_ui()

    def _init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self._new_meal_tab()  # add the "+" tab (used to add new meals)

        try:
            meal_ids = self.planner_service.load_saved_meal_ids()
            DebugLogger.log(f"[MealPlanner] Restoring saved meal IDs: {meal_ids}", "info")

            for meal_id in meal_ids:
                self._add_meal_tab(meal_id=meal_id)

            if not meal_ids:
                self._add_meal_tab()
        except Exception as e:
            DebugLogger.log(f"[MealPlanner] Error loading saved meals: {e}", "error")
            self._add_meal_tab()  # Fallback to empty tab

    def _add_meal_tab(self, meal_id: int = None):
        widget = MealWidget(self.planner_service)  # pass the service here
        if meal_id:
            widget.load_meal(meal_id)
        # hook into slot add events to open selection page
        def make_selection_callback(meal_widget):
            def callback(key):
                DebugLogger.log(f"Recipe selection requested for key: {key}", "info")
                self._start_recipe_selection(meal_widget, key)
            return callback
        widget.recipe_selection_requested.connect(make_selection_callback(widget))

        insert_index = self.meal_tabs.count() - 1
        index = self.meal_tabs.insertTab(insert_index, widget, "Custom Meal")
        self.tab_map[index] = widget
        self.meal_tabs.setCurrentIndex(index)

    def _new_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        _new_meal_tab = QWidget()
        icon_asset = AppIcon(Icon.ADD)
        icon_asset.setSize(32, 32)  # Set custom size before getting pixmap
        icon = icon_asset.pixmap()

        index = self.meal_tabs.addTab(_new_meal_tab, icon, "")
        self.meal_tabs.setTabToolTip(index, "Add Meal")

    def _handle_tab_click(self, index: int):
        """Handle when the '+' tab is clicked to add a new tab."""
        if index == self.meal_tabs.count() - 1:
            self._add_meal_tab()

    def _start_recipe_selection(self, widget, slot_key: str):
        """Begin in-page recipe selection for the given meal slot."""
        DebugLogger.log(f"Starting recipe selection for slot: {slot_key}", "info")
        # Store context for callback
        self._selection_context = (widget, slot_key)
        # Reset selection browser
        try:
            DebugLogger.log("Loading recipes in selection page browser", "info")
            self.selection_page.browser.load_recipes()
        except Exception as e:
            DebugLogger.log(f"Error loading recipes: {e}", "error")
        # Show selection page
        DebugLogger.log("Switching to selection page (index 1)", "info")
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

    def _show_context_menu(self, position):
        """Show context menu for meal tabs."""
        tab_bar = self.meal_tabs.tabBar()
        tab_index = tab_bar.tabAt(position)

        # Don't show context menu for the '+' tab (last tab) or invalid positions
        if tab_index == -1 or tab_index == self.meal_tabs.count() - 1:
            return

        # Only show context menu if this tab has a meal widget
        if tab_index not in self.tab_map:
            return

        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete Meal")
        delete_action.triggered.connect(lambda: self._delete_meal_tab(tab_index))

        # Show context menu at the cursor position
        context_menu.exec(self.meal_tabs.mapToGlobal(position))

    def _delete_meal_tab(self, tab_index: int):
        """Delete a meal tab and remove the meal from the database if saved."""
        if tab_index not in self.tab_map:
            return

        meal_widget = self.tab_map[tab_index]

        # Check if this is a saved meal that needs database deletion
        if meal_widget._meal_model and meal_widget._meal_model.id:
            meal_id = meal_widget._meal_model.id

            # Delete from database
            success = self.planner_service.delete_meal_selection(meal_id)

            if success:
                DebugLogger.log(f"Successfully deleted saved meal with ID {meal_id}", "info")
            else:
                DebugLogger.log(f"Failed to delete meal with ID {meal_id} from database", "error")
                return  # Don't remove tab if database deletion failed
        else:
            # Unsaved meal - just log that we're removing the tab
            DebugLogger.log("Removing unsaved meal tab", "info")

        # Check if we're deleting the currently selected tab
        current_tab = self.meal_tabs.currentIndex()
        was_current_tab = (tab_index == current_tab)

        # Determine which tab to select after deletion
        new_selected_index = None
        if was_current_tab:
            # If deleting the current tab, select the tab to the left if possible
            # Otherwise select the tab to the right (which will shift left after deletion)
            total_meal_tabs = len(self.tab_map)  # Excluding the '+' tab

            if tab_index > 0:
                # Select the tab to the left
                new_selected_index = tab_index - 1
            elif total_meal_tabs > 1:
                # Select the tab that will be at position 0 after deletion
                new_selected_index = 0
            # If only one meal tab exists, it will be deleted and '+' tab will remain

        # Remove the tab from UI
        self.meal_tabs.removeTab(tab_index)

        # Update tab_map indices after removal
        new_tab_map = {}
        for idx, widget in self.tab_map.items():
            if idx < tab_index:
                new_tab_map[idx] = widget
            elif idx > tab_index:
                new_tab_map[idx - 1] = widget

        self.tab_map = new_tab_map

        # Set the new selected tab if needed
        if was_current_tab and new_selected_index is not None:
            self.meal_tabs.setCurrentIndex(new_selected_index)
            DebugLogger.log(f"Auto-selected tab at index {new_selected_index} after deletion", "info")

    def _get_active_meal_ids(self) -> list[int]:
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

    def saveMealPlan(self):
        """Save all meals and their corresponding tab state."""
        for widget in self.tab_map.values():
            widget.save_meal()

        saved_ids = self._get_active_meal_ids()
        result = self.planner_service.saveMealPlan(saved_ids)

        if result.success:
            DebugLogger.log(f"[MealPlanner] {result.message}", "info")
        else:
            DebugLogger.log(f"[MealPlanner] Failed to save: {result.message}", "error")

    def closeEvent(self, event):
        # persist planner state before closing
        super().closeEvent(event)

