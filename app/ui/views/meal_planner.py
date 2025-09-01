"""app/ui/pages/meal_planner/meal_planner.py

This module defines the MealPlanner class, which provides a tabbed interface for meal planning.
It allows users to create, edit, and save meal plans. The MealPlanner uses QTabWidget to manage
multiple meal planning tabs and integrates with the database to load and save meal data.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt, Signal, QEvent
from PySide6.QtWidgets import QMenu, QStackedWidget, QTabWidget, QVBoxLayout, QHBoxLayout,QWidget, QToolTip

from app.core.dtos.planner_dtos import MealSelectionCreateDTO, MealSelectionUpdateDTO
from app.core.models.meal_selection import MealSelection
from app.core.services.planner_service import PlannerService
from app.core.services.recipe_service import RecipeService
from app.core.utils.error_utils import (
    log_and_handle_exception, safe_execute_with_fallback,
    error_boundary, create_error_context)
from app.ui.utils.layout_utils import setup_main_scroll_layout
from app.style.icon import AppIcon, Icon
from app.style import Theme, Qss
from app.ui.components.composite.recipe_card import LayoutSize, create_recipe_card
from app.ui.views.recipe_selection import RecipeSelection
from _dev_tools import DebugLogger


# ── Meal Widget ──────────────────────────────────────────────────────────────────────────────
class MealWidget(QWidget):
    """
    A QWidget layout that organizes a main dish and side dish RecipeViewers.
    Handles layout creation, user interaction, and internal meal state tracking.
    """

    # signal emitted when a recipe slot requests selection; passes the slot key (e.g., 'main', 'side1')
    recipe_selection_requested = Signal(str)
    def __init__(self, planner_service: PlannerService, parent=None):
        super().__init__(parent)
        self.planner_service = planner_service
        self.recipe_service = RecipeService() # for loading recipe details
        self._meal_model: MealSelection | None = None
        self.meal_slots = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """
        Setup the UI layout for the MealWidget.

        This method initializes the layout with a large main dish card and 3 small side dishes.
        Following the new design: large card on top, 3 small cards in a row below.
        """
        self.setObjectName("MealWidget")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)

        # Main Dish (Large Card)
        self.main_slot = create_recipe_card(LayoutSize.LARGE)
        self.meal_slots["main"] = self.main_slot
        self.main_layout.addWidget(self.main_slot, 0, Qt.AlignHCenter | Qt.AlignTop)

        # Side Dishes Row
        self.side_layout = QHBoxLayout()
        self.side_layout.setSpacing(15)

        for i in range(1, 4):
            side_slot = create_recipe_card(LayoutSize.SMALL)
            side_slot.setEnabled(False) # initially disabled
            side_slot.setToolTip("Select a main dish first") # tooltip for disabled state
            self.side_layout.addWidget(side_slot)
            self.meal_slots[f"side{i}"] = side_slot

        self.main_layout.addLayout(self.side_layout)

    def _connect_signals(self):
        """
        Connect signal from RecipeViewer to the update_recipe_selection method.
        """
        for key, slot in self.meal_slots.items():
            slot.recipe_selected.connect(lambda rid, k=key: self.update_recipe_selection(k, rid))
            # when an empty slot's add button is clicked, request recipe selection
            def make_add_meal_callback(slot_key):
                def callback():
                    DebugLogger.log(f"Add meal clicked for slot: {slot_key}", "info")
                    self.recipe_selection_requested.emit(slot_key)
                return callback
            slot.add_meal_clicked.connect(make_add_meal_callback(key))

    def update_recipe_selection(self, key: str, recipe_id: int) -> None:
        """
        Update the meal model with the selected recipe ID.

        Args:
            key (str): The key representing the recipe slot (main, side1, side2, side3).
            recipe_id (int): The ID of the selected recipe.
        """
        if not self._meal_model:
            self._meal_model = MealSelection(
                meal_name="Custom Meal",  # or dynamic name later
                main_recipe_id=recipe_id if key == "main" else 0
            )

        # Update Internal Model
        if key == "main":
            self._meal_model.main_recipe_id = recipe_id
            # Enable Side Slots
            for side in ("side1", "side2", "side3"):
                self.meal_slots[side].setEnabled(True)
                self.meal_slots[side].setToolTip("")
        else:
            # Side Slot Update
            setattr(self._meal_model, f"side_recipe_{key[-1]}_id", recipe_id)
        # fetch recipe and update the slot UI, but block signals to avoid recursion
        slot = self.meal_slots.get(key)
        if slot is not None:
            recipe = self.recipe_service.get_recipe(recipe_id)
            slot.blockSignals(True)
            slot.set_recipe(recipe)
            slot.blockSignals(False)

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
    def save_meal(self):
        if not self._meal_model:
            return

        if self._meal_model.id is None:
            create_dto = MealSelectionCreateDTO(
                meal_name=self._meal_model.meal_name,
                main_recipe_id=self._meal_model.main_recipe_id,
                side_recipe_1_id=self._meal_model.side_recipe_1_id,
                side_recipe_2_id=self._meal_model.side_recipe_2_id,
                side_recipe_3_id=self._meal_model.side_recipe_3_id
            )
            response_dto = self.planner_service.create_meal_selection(create_dto)
            if response_dto:
                self._meal_model.id = response_dto.id
        else:
            update_dto = MealSelectionUpdateDTO(
                meal_name=self._meal_model.meal_name,
                main_recipe_id=self._meal_model.main_recipe_id,
                side_recipe_1_id=self._meal_model.side_recipe_1_id,
                side_recipe_2_id=self._meal_model.side_recipe_2_id,
                side_recipe_3_id=self._meal_model.side_recipe_3_id
            )
            self.planner_service.update_meal_selection(self._meal_model.id, update_dto)

    @error_boundary(fallback=None, logger_func=DebugLogger.log)
    def load_meal(self, meal_id: int):
        """
        Load a meal by its ID and populate the RecipeViewers.
        """
        response_dto = self.planner_service.get_meal_selection(meal_id)
        if not response_dto:
            error_context = create_error_context(
                "meal_load",
                {"meal_id": meal_id},
                {"component": "MealWidget"}
            )
            log_and_handle_exception(
                "meal_load_not_found",
                ValueError(f"No meal found with ID {meal_id}"),
                DebugLogger.log,
                error_context
            )
            return

        self._meal_model = MealSelection(
            id=response_dto.id,
            meal_name=response_dto.meal_name,
            main_recipe_id=response_dto.main_recipe_id,
            side_recipe_1_id=response_dto.side_recipe_1_id,
            side_recipe_2_id=response_dto.side_recipe_2_id,
            side_recipe_3_id=response_dto.side_recipe_3_id
        )

        # Load Recipes
        main = self.recipe_service.get_recipe(self._meal_model.main_recipe_id)
        self.main_slot.set_recipe(main)
        for idx in (1, 2, 3):
            rid = getattr(self._meal_model, f"side_recipe_{idx}_id")
            slot = self.meal_slots.get(f"side{idx}")
            recipe = self.recipe_service.get_recipe(rid) if rid else None
            slot.set_recipe(recipe)


    def eventFilter(self, obj, event):
        """
        Show tooltip on disabled RecipeViewers.

        Args:
            obj: The object receiving the event.
            event: The event itself.
        """
        if event.type() == QEvent.ToolTip and not obj.isEnabled():
            QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
            return True
        return super().eventFilter(obj, event)


# ── Meal Planner ─────────────────────────────────────────────────────────────────────────────
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
        # Initialize PlannerService
        self.planner_service = PlannerService()

        self.setObjectName("MealPlanner")
        Theme.register_widget(self, Qss.MEAL_PLANNER) # register QSS theme
        DebugLogger.log("Initializing MealPlanner page", "info")

        self.tab_map = {}  # {tab_index: MealWidget}
        # context for in-page recipe selection (widget, slot_key)
        self._selection_context = None

        self._build_ui()
        self._init_ui()

    def _build_ui(self):
        """Build the main UI layout using consistent scroll pattern."""
        # Use setup_main_scroll_layout for consistency with other views
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

        # Create Planner & Selection Widgets
        self.meal_tabs = QTabWidget()
        self.meal_tabs.setIconSize(QSize(32, 32))  # increase icon size
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

        # Add stack to scroll layout with center alignment
        self.scroll_layout.addWidget(self.stack, 0, Qt.AlignHCenter | Qt.AlignTop)

        # show the planner view by default
        self.stack.setCurrentIndex(0)

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
        icon_asset.setSize(32, 32)  # set custom size before getting pixmap
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
        # return to planner view
        self.stack.setCurrentIndex(0)
        self._selection_context = None

    def _show_context_menu(self, position):
        """Show context menu for meal tabs."""
        tab_bar = self.meal_tabs.tabBar()
        tab_index = tab_bar.tabAt(position)

        # don't show context menu for the '+' tab (last tab) or invalid positions
        if tab_index == -1 or tab_index == self.meal_tabs.count() - 1:
            return

        # only show context menu if this tab has a meal widget
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

        # check if this is a saved meal that needs database deletion
        if meal_widget._meal_model and meal_widget._meal_model.id:
            meal_id = meal_widget._meal_model.id

            # Delete From Database
            success = self.planner_service.delete_meal_selection(meal_id)

            if success:
                DebugLogger.log(f"Successfully deleted saved meal with ID {meal_id}", "info")
            else:
                DebugLogger.log(f"Failed to delete meal with ID {meal_id} from database", "error")
                return  # don't remove tab if database deletion failed
        else:
            # unsaved meal - just log that we're removing the tab
            DebugLogger.log("Removing unsaved meal tab", "info")

        # check if we're deleting the currently selected tab
        current_tab = self.meal_tabs.currentIndex()
        was_current_tab = (tab_index == current_tab)

        # determine which tab to select after deletion
        new_selected_index = None
        if was_current_tab:
            # if deleting the current tab, select the tab to the left if possible
            # otherwise select the tab to the right (which will shift left after deletion)
            total_meal_tabs = len(self.tab_map)  # Excluding the '+' tab

            if tab_index > 0:
                # select the tab to the left
                new_selected_index = tab_index - 1
            elif total_meal_tabs > 1:
                # select the tab that will be at position 0 after deletion
                new_selected_index = 0
            # if only one meal tab exists, it will be deleted and '+' tab will remain

        # Remove Tab From UI
        self.meal_tabs.removeTab(tab_index)

        # Update Tab Map
        new_tab_map = {}
        for idx, widget in self.tab_map.items():
            if idx < tab_index:
                new_tab_map[idx] = widget
            elif idx > tab_index:
                new_tab_map[idx - 1] = widget

        self.tab_map = new_tab_map

        # set the new selected tab if needed
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

