"""app/ui/views/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMenu,
    QStackedWidget,
    QTabWidget,
    QWidget,
)

from _dev_tools import DebugLogger
from app.core.services.planner_service import PlannerService
from app.core.services.recipe_service import RecipeService
from app.core.utils.error_utils import (
    create_error_context,
    error_boundary,
    safe_execute_with_fallback,
)
from app.style import Qss
from app.style.icon import AppIcon, Icon
from app.ui.utils.widget_utils import (
    apply_object_name_pattern,
    register_widget_for_theme,
)
from app.ui.view_models.meal_planner_view_model import MealPlannerViewModel
from app.ui.view_models.meal_widget_view_model import MealWidgetViewModel
from app.ui.views.base import ScrollableNavView
from app.ui.views.meal_planner.config import MealPlannerConfig
from app.ui.views.recipe_selection import RecipeSelection
from ..meal_planner.meal_widget import MealWidget

# ── Meal Planner View ───────────────────────────────────────────────────────────────────────────────────────
class MealPlanner(ScrollableNavView):
    """
    The MealPlanner class manages a tabbed interface for creating, editing,
    and saving meal plans within the application.

    Attributes:
        meal_tabs (QTabWidget): The tab widget to manage meal planning tabs.
        layout (QVBoxLayout): The main layout for the MealPlanner widget.
        tab_map (dict): Maps tab indices to their respective MealWidget and meal_id.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        DebugLogger.log("Initializing MealPlanner page", "info")

        # Create services and ViewModel FIRST, before calling super().__init__
        # because parent class will call _connect_view_model_signals()
        self.planner_service = PlannerService()
        self.recipe_service = RecipeService()
        self.planner_view_model = MealPlannerViewModel(self.planner_service, self.recipe_service)

        # Initialize state variables
        self.tab_map: Dict[int, QWidget] = {}  # {tab_index: MealWidget}
        self._selection_context: Optional[Tuple[QWidget, str]] = None # (MealWidget, slot_key) during recipe selection

        # Now call parent constructor (which will call _build_ui and _connect_view_model_signals)
        super().__init__(parent)

        self.setObjectName("MealPlanner")
        self._setup_widget_properties()

        # Initialize UI with saved meals
        self._init_ui()

    def _build_ui(self) -> None:
        """Build the main UI layout using consistent scroll pattern."""

        # Create Planner & Selection Widgets
        self.meal_tabs = self._create_meal_tabs_widget()
        self.meal_tabs.setIconSize(MealPlannerConfig.TAB_ICON_SIZE)

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
        self.scroll_layout.addWidget(self.stack, 0, Qt.AlignHCenter | Qt.AlignTop)

        # show the planner view by default
        self.stack.setCurrentIndex(0)

    def _setup_widget_properties(self) -> None:
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

    def _connect_view_model_signals(self) -> None:
        """Connect MealPlannerViewModel signals to UI updates."""
        # Meal loaded signal
        self.planner_view_model.meal_loaded.connect(self._on_meal_loaded)

        # Meal saved signal
        self.planner_view_model.meal_saved.connect(self._on_meal_saved)

        # Recipe selection workflow signals
        self.planner_view_model.recipe_selection_started.connect(self._on_recipe_selection_started)
        self.planner_view_model.recipe_selection_finished.connect(self._on_recipe_selection_finished)

        # Tab state changes
        self.planner_view_model.tab_state_changed.connect(self._on_tab_state_changed)

    def _init_ui(self):
        """Initialize UI by adding the '+' tab and loading saved meals."""
        self._new_meal_tab()  # add the "+" tab (used to add new meals)

        def _load_saved_meals():
            meal_ids = self.planner_view_model.load_saved_meal_ids()
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

    def _add_meal_tab(self, meal_id: Optional[int] = None) -> None:
        """Add a new meal tab to the planner."""
        # Create MealWidgetViewModel with injected services
        meal_widget_vm = MealWidgetViewModel(self.planner_service, self.recipe_service)
        widget = MealWidget(meal_widget_vm)

        if meal_id:
            widget.load_meal(meal_id)

        # Connect recipe selection signal
        selection_handler = self._create_recipe_selection_callback(widget)
        widget.recipe_selection_requested.connect(selection_handler)

        insert_index = self.meal_tabs.count() - MealPlannerConfig.ADD_TAB_INDEX_OFFSET
        index = self.meal_tabs.insertTab(insert_index, widget, MealPlannerConfig.NEW_MEAL_TAB_TITLE)
        self.tab_map[index] = widget
        self.meal_tabs.setCurrentIndex(index)

    def _create_recipe_selection_callback(self, meal_widget: MealWidget) -> callable:
        """Create recipe selection callback for meal widget."""
        def callback(key: str) -> None:
            DebugLogger.log(f"Recipe selection requested for key: {key}", "info")
            self._start_recipe_selection(meal_widget, key)
        return callback

    def _new_meal_tab(self) -> None:
        """Add the last "+" tab to create new custom meals."""
        tab_widget = QWidget()
        apply_object_name_pattern(tab_widget, "NewMealTab")

        icon_asset = AppIcon(Icon.ADD)
        icon_asset.setSize(MealPlannerConfig.TAB_ICON_SIZE.width(), MealPlannerConfig.TAB_ICON_SIZE.height())
        icon = icon_asset.pixmap()

        index = self.meal_tabs.addTab(tab_widget, icon, "")
        self.meal_tabs.setTabToolTip(index, MealPlannerConfig.ADD_TAB_TOOLTIP)

    def _handle_tab_click(self, index: int) -> None:
        """Handle when the '+' tab is clicked to add a new tab."""
        if index == self.meal_tabs.count() - MealPlannerConfig.ADD_TAB_INDEX_OFFSET:
            self._add_meal_tab()

    def _start_recipe_selection(self, widget: MealWidget, slot_key: str) -> None:
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

    def _finish_recipe_selection(self, recipe_id: int) -> None:
        """Handle recipe selected from the selection page."""
        if not self._selection_context:
            return
        widget, slot_key = self._selection_context
        widget.update_recipe_selection(slot_key, recipe_id)
        self._return_to_planner_view()

    def _return_to_planner_view(self) -> None:
        """Return to planner view and clear selection context."""
        self.stack.setCurrentIndex(0)
        self._selection_context = None

    def _show_context_menu(self, position) -> None:
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
        if tab_index == -1 or tab_index == self.meal_tabs.count() - MealPlannerConfig.ADD_TAB_INDEX_OFFSET:
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

    def _delete_meal_tab(self, tab_index: int) -> None:
        """Delete a meal tab and remove the meal from the database if saved."""
        if tab_index not in self.tab_map:
            return

        meal_widget = self.tab_map[tab_index]

        # Delete from database if saved meal
        meal_id = meal_widget.get_meal_id()
        if meal_id:
            if not self.planner_view_model.delete_meal_selection(meal_id):
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
            meal_id = widget.get_meal_id()
            if meal_id:
                ids.append(meal_id)
        return ids

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
    def save_meal_plan(self) -> None:
        """Save all meals and their corresponding tab state using ViewModel."""
        # First save all individual meals
        for widget in self.tab_map.values():
            widget.save_meal()

        # Then save the meal plan with collected IDs
        saved_ids = self._get_active_meal_ids()
        success = self.planner_view_model.save_meal_plan(saved_ids)

        if success:
            DebugLogger.log("[MealPlanner] Meal plan saved successfully", "info")
        else:
            DebugLogger.log("[MealPlanner] Failed to save meal plan", "error")

    # ── ViewModel Signal Handlers ───────────────────────────────────────────────────────────────────────────────────

    def _on_meal_loaded(self, meal_dto) -> None:
        """Handle meal loaded signal from ViewModel."""
        DebugLogger.log(f"Meal loaded: {meal_dto.meal_name}", "info")

    def _on_meal_saved(self, message: str) -> None:
        """Handle meal saved signal from ViewModel."""
        DebugLogger.log(f"Meal saved: {message}", "info")

    def _on_recipe_selection_started(self, meal_widget_id: str, slot_key: str) -> None:
        """Handle recipe selection started signal from ViewModel."""
        DebugLogger.log(f"Recipe selection started for {meal_widget_id}.{slot_key}", "debug")

    def _on_recipe_selection_finished(self, recipe_id: int) -> None:
        """Handle recipe selection finished signal from ViewModel."""
        DebugLogger.log(f"Recipe selection finished with recipe {recipe_id}", "debug")

    def _on_tab_state_changed(self, tab_state_data: Dict[str, Any]) -> None:
        """Handle tab state changes from ViewModel."""
        DebugLogger.log(f"Tab state changed: {tab_state_data.get('total_tabs', 0)} tabs active", "debug")

    def closeEvent(self, event):
        # persist planner state before closing
        super().closeEvent(event)

