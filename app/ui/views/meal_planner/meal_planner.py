"""app/ui/views/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ───
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMenu, QStackedWidget, QTabWidget, QWidget

from _dev_tools import DebugLogger
from app.core.services import PlannerService
from app.core.utils import (create_error_context, error_boundary,
                            safe_execute_with_fallback)
from app.style import Qss
from app.style.icon import AppIcon, Icon
from app.ui.utils import (apply_object_name_pattern, register_widget_for_theme,
                          setup_main_scroll_layout)
from app.ui.views.base import BaseView
from app.ui.views.recipe_selection import RecipeSelection

from .meal_widget import MealWidget

# ── Constants ──
TAB_ICON_SIZE = QSize(32, 32)
ADD_TAB_TOOLTIP = "Add Meal"


class MealPlanner(BaseView):
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
        # Initialize PlannerService
        self.planner_service = PlannerService()

        self._setup_widget_properties()
        DebugLogger.log("Initializing MealPlanner page", "info")

        self.tab_map = {}  # {tab_index: MealWidget}
        # context for in-page recipe selection (widget, slot_key)
        self._selection_context = None

        self._build_ui()
        self._init_ui()

    def _build_ui(self):
        """Build the main UI layout using consistent scroll pattern."""
        # Create Planner & Selection Widgets
        self.meal_tabs = self._create_meal_tabs_widget()
        self.meal_tabs.setIconSize(TAB_ICON_SIZE)

        # create the in-page recipe selection view
        self.selection_page = RecipeSelection(self)
        # handle when a recipe is selected from the selection page
        self.selection_page.recipe_selected.connect(self._finish_recipe_selection)

        # stacked widget to switch between planner tabs and selection page
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.meal_tabs)
        self.stack.addWidget(self.selection_page)

        # Add stack to scroll layout with center alignment
        self.content_layout.addWidget(self.stack, 0, Qt.AlignHCenter | Qt.AlignTop)

        # show the planner view by default
        self.stack.setCurrentIndex(0)

    def _setup_widget_properties(self):
        """Setup widget properties and theme registration."""
        apply_object_name_pattern(self, "MealPlanner")
        register_widget_for_theme(self, Qss.MEAL_PLANNER)

    def _create_meal_tabs_widget(self) -> QTabWidget:
        """Create and configure the meal tabs widget."""
        tabs = QTabWidget()
        tabs.setTabsClosable(False)
        tabs.setMovable(True)
        tabs.setContextMenuPolicy(Qt.CustomContextMenu)

        # Connect signals
        tabs.tabBarClicked.connect(self._handle_tab_click)
        tabs.customContextMenuRequested.connect(self._show_context_menu)

        return tabs

    def _init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self._new_meal_tab()  # add the "+" tab (used to add new meals)

        def _load_saved_meals():
            meal_ids = self.planner_service.load_saved_meal_ids()
            DebugLogger.log(f"[MealPlanner] Restoring saved meal IDs: {meal_ids}", "info")

            for meal_id in meal_ids:
                self._add_meal_tab(meal_id=meal_id)

            if not meal_ids:
                self._add_meal_tab()

        # Use safe_execute_with_fallback to handle errors gracefully
        safe_execute_with_fallback(
            _load_saved_meals,
            fallback=lambda: self._add_meal_tab(),  # fallback to empty tab
            error_context="meal_planner_initialization",
            logger_func=DebugLogger.log
        )

    def _add_meal_tab(self, meal_id: int = None):
        widget = MealWidget(self.planner_service)
        if meal_id:
            widget.load_meal(meal_id)

        # Connect recipe selection signal
        selection_handler = self._create_recipe_selection_callback(widget)
        widget.recipe_selection_requested.connect(selection_handler)

        insert_index = self.meal_tabs.count() - 1
        index = self.meal_tabs.insertTab(insert_index, widget, "Custom Meal")
        self.tab_map[index] = widget
        self.meal_tabs.setCurrentIndex(index)

    def _create_recipe_selection_callback(self, meal_widget):
        """Create recipe selection callback for meal widget."""
        def callback(key: str):
            DebugLogger.log(f"Recipe selection requested for key: {key}", "info")
            self._start_recipe_selection(meal_widget, key)
        return callback

    def _new_meal_tab(self):
        """Add the last "+" tab to create new custom meals."""
        tab_widget = QWidget()
        apply_object_name_pattern(tab_widget, "NewMealTab")

        icon_asset = AppIcon(Icon.ADD)
        icon_asset.setSize(TAB_ICON_SIZE.width(), TAB_ICON_SIZE.height())
        icon = icon_asset.pixmap()

        index = self.meal_tabs.addTab(tab_widget, icon, "")
        self.meal_tabs.setTabToolTip(index, ADD_TAB_TOOLTIP)

    def _handle_tab_click(self, index: int):
        """Handle when the '+' tab is clicked to add a new tab."""
        if index == self.meal_tabs.count() - 1:
            self._add_meal_tab()

    def _start_recipe_selection(self, widget, slot_key: str):
        """Begin in-page recipe selection for the given meal slot."""
        DebugLogger.log(f"Starting recipe selection for slot: {slot_key}", "info")
        # Store Context
        self._selection_context = (widget, slot_key)

        # Reset selection browser with error handling
        def _load_recipes():
            DebugLogger.log("Loading recipes in selection page browser", "info")
            self.selection_page.browser.load_recipes()

        error_context = create_error_context(
            "recipe_selection_init",
            {"slot_key": slot_key},
            {"component": "MealPlanner"}
        )
        safe_execute_with_fallback(
            _load_recipes,
            fallback=None,  # Continue even if loading fails
            error_context="recipe_browser_load",
            logger_func=DebugLogger.log
        )

        # Show Selection Page
        DebugLogger.log("Switching to selection page (index 1)", "info")
        self.stack.setCurrentIndex(1)

    def _finish_recipe_selection(self, recipe_id: int):
        """Handle recipe selected from the selection page."""
        if not self._selection_context:
            return
        widget, slot_key = self._selection_context
        widget.update_recipe_selection(slot_key, recipe_id)
        self._return_to_planner_view()

    def _return_to_planner_view(self):
        """Return to planner view and clear selection context."""
        self.stack.setCurrentIndex(0)
        self._selection_context = None

    def _show_context_menu(self, position):
        """Show context menu for meal tabs."""
        tab_index = self._get_valid_tab_index(position)
        if tab_index is None:
            return

        context_menu = self._create_tab_context_menu(tab_index)
        context_menu.exec(self.meal_tabs.mapToGlobal(position))

    def _get_valid_tab_index(self, position) -> int | None:
        """Get valid tab index for context menu operations."""
        tab_bar = self.meal_tabs.tabBar()
        tab_index = tab_bar.tabAt(position)

        # don't show context menu for the '+' tab (last tab) or invalid positions
        if tab_index == -1 or tab_index == self.meal_tabs.count() - 1:
            return None

        # only show context menu if this tab has a meal widget
        if tab_index not in self.tab_map:
            return None

        return tab_index

    def _create_tab_context_menu(self, tab_index: int) -> QMenu:
        """Create context menu for tab operations."""
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete Meal")
        delete_action.triggered.connect(lambda: self._delete_meal_tab(tab_index))
        return context_menu

    def _delete_meal_tab(self, tab_index: int):
        """Delete a meal tab and remove the meal from the database if saved."""
        if tab_index not in self.tab_map:
            return

        meal_widget = self.tab_map[tab_index]

        # Delete from database if saved meal
        if meal_widget._meal_model and meal_widget._meal_model.id:
            meal_id = meal_widget._meal_model.id
            if not self.planner_service.delete_meal_selection(meal_id):
                DebugLogger.log(f"Failed to delete meal with ID {meal_id} from database", "error")
                return
            DebugLogger.log(f"Successfully deleted saved meal with ID {meal_id}", "info")
        else:
            DebugLogger.log("Removing unsaved meal tab", "info")

        # Determine new tab selection if deleting current tab
        current_tab = self.meal_tabs.currentIndex()
        new_selected_index = None
        if tab_index == current_tab:
            total_meal_tabs = len(self.tab_map)
            if tab_index > 0:
                new_selected_index = tab_index - 1
            elif total_meal_tabs > 1:
                new_selected_index = 0

        # Remove tab and update indices
        self.meal_tabs.removeTab(tab_index)
        new_tab_map = {}
        for idx, widget in self.tab_map.items():
            if idx < tab_index:
                new_tab_map[idx] = widget
            elif idx > tab_index:
                new_tab_map[idx - 1] = widget
        self.tab_map = new_tab_map

        # Select new tab if needed
        if new_selected_index is not None:
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

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
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

