"""app/ui/views/shopping_list/view.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list.

The view follows the MVVM pattern with clear separation between UI presentation (View)
and business logic (ViewModel). Shopping items are organized by category in collapsible
sections for improved user experience.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger
from app.core.events import get_recipe_event_manager
from app.style import Qss, Theme

from ...components.layout.card import ActionCard, Card
from ...components.widgets import Toast
from ...utils.layout_utils import create_two_column_layout
from ...view_models import ShoppingListViewModel
from ...views.base import ScrollableNavView
from ._add_item_form import AddItemForm
from ._collapsible_category import CollapsibleCategory
from ._shopping_item import ShoppingItem

class ShoppingList(ScrollableNavView):
    """Main shopping list view for managing shopping items.

    Displays shopping items organized by category with functionality to:
    - Generate lists from meal plans
    - Add manual items
    - Mark items as obtained
    - View recipe breakdowns

    Follows MVVM pattern with ShoppingListViewModel handling business logic.
    """


    def __init__(self, parent=None):
        """Initialize the shopping list view.

        Args:
            parent: Optional parent widget.
        """
        # Initialize ViewModels BEFORE super() - required by _build_ui()
        self.view_model = ShoppingListViewModel()

        super().__init__(parent)
        DebugLogger.log("Initializing ShoppingList page", "info")
        self.setObjectName("ShoppingList")
        Theme.register_widget(self, Qss.SHOPPING_LIST)

        # Track currently loaded meals for refresh operations
        self.active_meal_ids: list[int] = []

        # CRITICAL: Connect ViewModel signals to view handlers
        self._connect_view_model_signals()

        # Connect to meal plan updates
        event_manager = get_recipe_event_manager()
        event_manager.meal_plan_updated.connect(self._on_meal_plan_updated)
        DebugLogger.log("ShoppingList: Connected to meal plan update events", "info")

        # Load existing shopping items from database on initialization
        self.view_model.load_existing_shopping_items()


    # ── Initialization ──────────────────────────────────────────────────────────────────────────────────────
    def _connect_view_model_signals(self) -> None:
        """Connect ViewModel signals to UI update methods.

        Establishes communication between ViewModel and View for
        data updates, errors, and state changes.
        """
        self.view_model.list_updated.connect(self._on_list_updated)
        self.view_model.manual_item_added.connect(self._on_manual_item_added)
        self.view_model.error_occurred.connect(self._on_error_occurred)
        self.view_model.validation_failed.connect(self._on_validation_failed)
        self.view_model.processing_state_changed.connect(self._on_processing_state_changed)
        self.view_model.loading_state_changed.connect(self._on_loading_state_changed)

    # ── UI Setup ────────────────────────────────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        """Setup the UI components for the ShoppingList view.

        Creates two-column layout with shopping list on left and
        add item form on right.
        """
        self.list_container = self._create_list_container()
        self.entry_card = self._create_entry_card()

        column_layout = create_two_column_layout(
            left_widgets=[self.list_container],
            right_widgets=[self.entry_card],
            left_weight=3,
            right_weight=1
        )
        self.list_container.setMinimumHeight(self.entry_card.sizeHint().height())
        self.scroll_layout.addLayout(column_layout)

    def _create_list_container(self) -> Card:
        """Create the main container for shopping list items.

        Returns:
            Card widget configured for shopping list display.
        """
        list_container = Card()
        list_container.setObjectName("ListContainer")
        list_container.setHeader("Auto Generated Ingredients")
        list_container.setSubHeader("from this weeks meal plan")
        list_container.setSpacing(10)
        return list_container

    def _create_entry_card(self) -> ActionCard:
        """Create the card for manually adding items.

        Returns:
            ActionCard with embedded AddItemForm.
        """
        self.add_item_form = AddItemForm()
        entry_card = ActionCard()
        entry_card.setObjectName("EntryCard")
        entry_card.expandHeight(False)
        entry_card.setHeader("Add Item")
        entry_card.setSubHeader("Add item to your list")
        entry_card.addButton("Add", alignment=Qt.AlignRight, callback=self._on_add_manual)

        entry_card.addWidget(self.add_item_form)
        return entry_card

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────
    def _on_add_manual(self) -> None:
        """Handle the addition of a manual item to the shopping list.

        Collects form data, validates via ViewModel, and clears form on success.
        """
        # Collect form data
        name = self.add_item_form.le_item_name.text()
        qty = self.add_item_form.le_item_qty.text()
        unit = self.add_item_form.cb_item_unit.currentText()
        category = self.add_item_form.cb_item_category.currentText()

        # Delegate to ViewModel for validation and persistence
        success = self.view_model.add_manual_item(name, qty, unit, category)

        if success:
            # Clear form inputs for next entry
            self.add_item_form.le_item_name.clear()
            self.add_item_form.le_item_qty.clear()
            self.add_item_form.cb_item_unit.clearSelection()
            self.add_item_form.cb_item_category.clearSelection()

    # ── UI Rendering ────────────────────────────────────────────────────────────────────────────────────────
    def _render_category_columns(self, grouped: dict, manual_items: list) -> None:
        """Render all category sections in the shopping list.

        Args:
            grouped: Dict mapping category names to lists of ShoppingItems.
            manual_items: List of manually added ShoppingItems.
        """
        DebugLogger.log(f"_render_category_columns called with grouped={list(grouped.keys())}, manual_items={len(manual_items)}", "info")

        all_sections = list(grouped.items())
        if manual_items:
            all_sections.append(("Manual Entries", manual_items))

        DebugLogger.log(f"Total sections to render: {len(all_sections)}", "info")

        for category, items in all_sections:
            DebugLogger.log(f"Rendering category '{category}' with {len(items)} items", "info")
            category_widget = self._create_category_section(category, items)
            self.list_container.addWidget(category_widget)

    def _create_category_section(self, title: str, items: list) -> CollapsibleCategory:
        """Create a collapsible section for a category of items.

        Args:
            title: Category name for the section header.
            items: List of shopping items in this category.

        Returns:
            Populated CollapsibleCategory widget.
        """
        category_widget = CollapsibleCategory(title, start_expanded=False)

        # Get breakdown map from ViewModel
        breakdown_map = self.view_model.get_breakdown_map()

        for item in items:
            item_widget = ShoppingItem(item, self.view_model, breakdown_map)
            category_widget.addShoppingItem(item_widget)

        return category_widget

    # ── Public Interface ────────────────────────────────────────────────────────────────────────────────────
    def loadShoppingList(self, meal_ids: list[int]) -> None:
        """Generate and display a categorized shopping list from meals.

        Args:
            meal_ids: List of meal IDs to generate the shopping list from.
        """
        self.active_meal_ids = meal_ids
        DebugLogger.log(f"ShoppingList.loadShoppingList: meal_ids={meal_ids}", "debug")

        self._prepare_ui_for_refresh()
        self._refresh_shopping_data(meal_ids)

    # ── Private Helper Methods ──────────────────────────────────────────────────────────────────────────────
    def _prepare_ui_for_refresh(self) -> None:
        """Prepare UI for shopping list refresh by clearing current content.

        Ensures proper cleanup of existing widgets before loading new data.
        """
        self._cleanup_existing_widgets()
        self.list_container.clear()

    def _cleanup_existing_widgets(self) -> None:
        """Clean up existing shopping item widgets to prevent memory leaks.

        Iterates through all category widgets and calls their cleanup methods
        to properly disconnect signals and free resources.
        """
        for i in range(self.list_container.layout().count()):
            item = self.list_container.layout().itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'cleanup'):
                item.widget().cleanup()

    def _refresh_shopping_data(self, meal_ids: list[int]) -> None:
        """Refresh shopping data using the ViewModel.

        Args:
            meal_ids: Meal IDs to generate shopping list from.
        """
        self.view_model.generate_shopping_list(meal_ids)

    # ── ViewModel Signal Handlers ───────────────────────────────────────────────────────────────────────────
    def _on_list_updated(self, grouped_items: dict, manual_items: list) -> None:
        """Handle shopping list update from ViewModel.

        Args:
            grouped_items: Items grouped by category.
            manual_items: Manually added items.
        """
        DebugLogger.log(f"Shopping list updated by ViewModel: {len(grouped_items)} categories, {len(manual_items)} manual items", "info")
        self._render_category_columns(grouped_items, manual_items)

    def _on_manual_item_added(self, message: str) -> None:
        """Handle successful manual item addition.

        Args:
            message: Success message to display.
        """
        DebugLogger.log(f"Manual item added: {message}", "info")
        self._show_success_message(message)

    def _on_error_occurred(self, error_type: str, error_message: str) -> None:
        """Handle error from ViewModel.

        Args:
            error_type: Category of error for logging.
            error_message: User-friendly error description.
        """
        DebugLogger.log(f"ViewModel error [{error_type}]: {error_message}", "error")
        self._show_error_message(error_message)

    def _on_validation_failed(self, errors: list) -> None:
        """Handle validation errors from ViewModel.

        Args:
            errors: List of validation error messages.
        """
        error_message = "; ".join(errors)
        DebugLogger.log(f"Validation failed: {error_message}", "warning")
        self._show_validation_error(error_message)

    def _on_processing_state_changed(self, is_processing: bool) -> None:
        """Handle processing state change from ViewModel.

        Args:
            is_processing: Whether ViewModel is currently processing.
        """
        if is_processing:
            DebugLogger.log("ViewModel processing started", "debug")
            # TODO: Consider disabling UI controls during processing
        else:
            DebugLogger.log("ViewModel processing completed", "debug")

    def _on_loading_state_changed(self, is_loading: bool, operation: str) -> None:
        """Handle loading state change from ViewModel.

        Args:
            is_loading: Whether data is currently loading.
            operation: Description of the loading operation.
        """
        if is_loading:
            DebugLogger.log(f"ViewModel loading: {operation}", "debug")
            # TODO: Consider showing loading spinner or progress indicator
        else:
            DebugLogger.log("ViewModel loading completed", "debug")

    # ── User Feedback Methods ───────────────────────────────────────────────────────────────────────────────
    def _show_success_message(self, message: str) -> None:
        """Show success message using Toast notification.

        Args:
            message: Success message to display.
        """
        toast = Toast(message, self, success=True)
        toast.show_toast()

    def _show_error_message(self, message: str) -> None:
        """Show error message using Toast notification.

        Args:
            message: Error message to display.
        """
        toast = Toast(message, self, success=False)
        toast.show_toast()

    def _show_validation_error(self, message: str) -> None:
        """Show validation error message using Toast notification.

        Args:
            message: Validation error details to display.
        """
        toast = Toast(f"Validation Error: {message}", self, success=False)
        toast.show_toast()

    def _on_meal_plan_updated(self, meal_ids: list[int]) -> None:
        """Handle meal plan update event from MealPlanner.

        Args:
            meal_ids: List of meal IDs in the updated meal plan.
        """
        DebugLogger.log(f"ShoppingList: Received meal plan update with {len(meal_ids)} meals", "info")
        if meal_ids:
            self.loadShoppingList(meal_ids)
        else:
            # Empty meal plan - clear shopping list
            self.view_model.clear_shopping_list()
