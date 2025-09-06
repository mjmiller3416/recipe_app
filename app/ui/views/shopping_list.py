"""app/ui/views/shopping_list.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list.

The view follows the MVVM pattern with clear separation between UI presentation (View)
and business logic (ViewModel). Shopping items are organized by category in collapsible
sections for improved user experience.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from _dev_tools import DebugLogger
from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS
from app.style import Icon, Qss, Theme, Type
from app.ui.components.layout.card import ActionCard, BaseCard, Card
from app.ui.components.widgets import BaseButton, ComboBox, ToolButton
from app.ui.components.widgets.toast import Toast
from app.ui.constants import LayoutConstants
from app.ui.utils.layout_utils import (
    create_two_column_layout,
    set_fixed_height_for_layout_widgets,
)
from app.ui.view_models.shopping_list_view_model import ShoppingListViewModel
from app.ui.views.base import ScrollableNavView

# ── Forms ───────────────────────────────────────────────────────────────────────────────────────────────────
class AddItemForm(QWidget):
    """Form widget for manually adding new items to the shopping list.

    Provides input fields for item name, quantity, unit, and category.
    Used within the AddItem card on the shopping list view.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the add item form.

        Args:
            parent: Optional parent widget for Qt hierarchy.
        """
        super().__init__(parent)
        self.setObjectName("AddShoppingItem")

        # Configure form layout with grid for responsive design
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # Create form controls with labels positioned above inputs for clarity
        self.lbl_item_name = QLabel("Item Name")
        self.le_item_name = QLineEdit()
        self.le_item_name.setPlaceholderText("e.g. Olive Oil")
        self.le_item_name.setObjectName("item_name_line_edit")

        # Qty.
        self.lbl_item_qty = QLabel("Qty.")
        self.le_item_qty = QLineEdit()
        self.le_item_qty.setPlaceholderText("e.g. 2")
        self.le_item_qty.setObjectName("quantity_line_edit")

        # Unit
        self.lbl_item_unit = QLabel("Unit")
        self.cb_item_unit = ComboBox(list_items=MEASUREMENT_UNITS, placeholder="e.g. bottle")
        self.cb_item_unit.setObjectName("unit_combo_box")
        self.cb_item_unit.setProperty("context", "shopping_item")

        # Category
        self.lbl_item_category = QLabel("Category")
        self.cb_item_category = ComboBox(list_items=INGREDIENT_CATEGORIES, placeholder="Select category")
        self.cb_item_category.setObjectName("category_combo_box")
        self.cb_item_category.setProperty("context", "shopping_item")

        # Arrange form controls in grid layout for optimal space usage
        self._layout.addWidget(self.lbl_item_name, 0, 0, 1, 2)
        self._layout.addWidget(self.le_item_name, 1, 0, 1, 2)

        # Row 2-3: Item Quantity (left) and Item Unit (right)
        self._layout.addWidget(self.lbl_item_qty, 2, 0, 1, 1)
        self._layout.addWidget(self.le_item_qty, 3, 0, 1, 1)
        self._layout.addWidget(self.lbl_item_unit, 2, 1, 1, 1)
        self._layout.addWidget(self.cb_item_unit, 3, 1, 1, 1)

        # Row 4-5: Item Category (left) and Item Unit (right)
        self._layout.addWidget(self.lbl_item_category, 4, 0, 1, 2)
        self._layout.addWidget(self.cb_item_category, 5, 0, 1, 2)

        set_fixed_height_for_layout_widgets(
            layout = self._layout,
            height = LayoutConstants.FIXED_INPUT_HEIGHT,
            skip   = (QLabel,)
        )


# ── Containers ──────────────────────────────────────────────────────────────────────────────────────────────
class CollapsibleCategory(BaseCard):
    """Collapsible category widget for organizing shopping items.

    Displays a category header that can be clicked to expand/collapse
    its contents. Contains shopping items grouped by category with
    smooth animation transitions.

    Signals:
        toggled: Emitted when expansion state changes.
        itemChecked: Emitted when an item's checkbox state changes.
    """
    toggled = Signal(bool)
    itemChecked = Signal(str, bool)

    def __init__(self, category_name, parent=None, start_expanded=False):
        """Initialize the collapsible category widget.

        Args:
            category_name: Display name for the category.
            parent: Optional parent widget.
            start_expanded: Whether to start in expanded state.
        """
        super().__init__(parent)
        self._category_name = category_name
        self._is_expanded = start_expanded
        self._items = []

        self._setup_header()
        self._setup_content_area()
        self._setup_animation()

        # Force initial collapsed state to prevent layout flash on load
        if not start_expanded:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)

        self._update_expand_state(animate=False)

    # ── UI Setup Methods ────────────────────────────────────────────────────────────────────────────────────

    def _setup_header(self):
        """Create the clickable category header with expand button."""
        self._header_widget = QWidget()
        self._header_widget.setObjectName("CategoryHeader")

        header_layout = QHBoxLayout(self._header_widget)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(8)

        # Category label
        self._category_label = QLabel(self._category_name)
        self._category_label.setObjectName("CategoryLabel")

        # Expand button
        self._expand_button = ToolButton(Type.PRIMARY, Icon.ANGLE_DOWN)
        self._expand_button.setIconSize(24, 24)
        self._expand_button.setObjectName("ExpandButton")
        self._expand_button.clicked.connect(self.toggle)

        header_layout.addWidget(self._category_label)
        header_layout.addStretch()
        header_layout.addWidget(self._expand_button)

        # Make entire header clickable for better UX
        self._header_widget.mousePressEvent = lambda e: self.toggle()
        self._header_widget.setCursor(Qt.PointingHandCursor)

        self.addWidget(self._header_widget)

    def _setup_content_area(self):
        """Create the collapsible content area for shopping items."""
        self._content_container = QWidget()
        self._content_container.setObjectName("ContentContainer")

        self._items_layout = QVBoxLayout(self._content_container)
        self._items_layout.setContentsMargins(16, 8, 16, 12)
        self._items_layout.setSpacing(8)

        self.addWidget(self._content_container)

    def _setup_animation(self):
        """Configure smooth animation for expand/collapse transitions."""
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(LayoutConstants.EXPAND_COLLAPSE_DURATION)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    # ── State Management ────────────────────────────────────────────────────────────────────────────────────

    def _update_expand_state(self, animate=True):
        """Update visual state based on expansion.

        Args:
            animate: Whether to animate the transition.
        """
        if self._is_expanded:
            self._expand_content(animate)
        else:
            self._collapse_content(animate)

        self._update_expand_button()

    def _expand_content(self, animate=True):
        """Expand the content area to show items.

        Args:
            animate: Whether to animate the expansion.
        """
        self._content_container.setVisible(True)

        if animate:
            # Calculate target height before animation to prevent visual glitches
            natural_height = self._content_container.sizeHint().height()

            self._animation.setStartValue(0)
            self._animation.setEndValue(natural_height)
            self._animation.finished.connect(
                lambda: self._content_container.setMaximumHeight(LayoutConstants.MAX_WIDGET_HEIGHT),
                Qt.SingleShotConnection
            )
            self._animation.start()
        else:
            self._content_container.setMaximumHeight(LayoutConstants.MAX_WIDGET_HEIGHT)

    def _collapse_content(self, animate=True):
        """Collapse the content area to hide items.

        Args:
            animate: Whether to animate the collapse.
        """
        if animate:
            current_height = self._content_container.height()
            self._animation.setStartValue(current_height)
            self._animation.setEndValue(0)
            self._animation.finished.connect(
                lambda: self._content_container.setVisible(False),
                Qt.SingleShotConnection
            )
            self._animation.start()
        else:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)

    def _update_expand_button(self):
        """Update expand button icon based on current state."""
        if self._is_expanded:
            icon_name = Icon.ANGLE_DOWN
            self._header_widget.setProperty("is_expanded", "True")
        else:
            icon_name = Icon.ANGLE_RIGHT
            self._header_widget.setProperty("is_expanded", "False")
        BaseButton.setIcon(self._expand_button, icon_name)

        # Qt workaround: force style refresh after property change
        self._header_widget.style().polish(self._header_widget)

        self._expand_button.setStateIconSize(24, 24)

    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────

    @property
    def category_name(self) -> str:
        """Get the category name."""
        return self._category_name

    @property
    def is_expanded(self) -> bool:
        """Check if category is currently expanded."""
        return self._is_expanded

    # ── Public Interface ────────────────────────────────────────────────────────────────────────────────────

    def toggle(self):
        """Toggle between expanded and collapsed states."""
        self._is_expanded = not self._is_expanded
        self._update_expand_state(animate=True)
        self.toggled.emit(self._is_expanded)

    def expand(self):
        """Expand the category if currently collapsed."""
        if not self._is_expanded:
            self.toggle()

    def collapse(self):
        """Collapse the category if currently expanded."""
        if self._is_expanded:
            self.toggle()

    def addItem(self, item_name: str) -> QCheckBox:
        """Add a simple checkbox item to the category.

        Args:
            item_name: Display text for the item.

        Returns:
            The created checkbox widget.
        """
        checkbox = QCheckBox(item_name)
        checkbox.stateChanged.connect(lambda state: self.itemChecked.emit(item_name, state == Qt.Checked))
        self._items_layout.addWidget(checkbox)
        self._items.append(checkbox)
        return checkbox

    def addShoppingItem(self, shopping_item_widget: QWidget) -> None:
        """Add a ShoppingItem widget to the category.

        Args:
            shopping_item_widget: The shopping item widget to add.
        """
        self._items_layout.addWidget(shopping_item_widget)
        self._items.append(shopping_item_widget)

    def setAllItemsChecked(self, checked: bool) -> None:
        """Check or uncheck all items in this category.

        Args:
            checked: Whether items should be checked.
        """
        for item in self._items:
            if isinstance(item, QCheckBox):
                item.setChecked(checked)
            elif hasattr(item, 'checkbox'):
                item.checkbox.setChecked(checked)

    def getCheckedItems(self) -> list[str]:
        """Get names of all checked items in this category.

        Returns:
            List of checked item names.
        """
        checked_items = []
        for item in self._items:
            if isinstance(item, QCheckBox) and item.isChecked():
                checked_items.append(item.text())
            elif hasattr(item, 'checkbox') and item.checkbox.isChecked():
                if hasattr(item, 'item') and hasattr(item.item, 'ingredient_name'):
                    checked_items.append(item.item.ingredient_name)
        return checked_items

    def cleanup(self) -> None:
        """Clean up all item widgets to prevent memory leaks.

        Called when the category is being destroyed or refreshed.
        Ensures proper cleanup of signal connections.
        """
        for item in self._items:
            if hasattr(item, 'cleanup'):
                item.cleanup()
        self._items.clear()

class ShoppingItem(QWidget):
    """Widget representing a single shopping list item.

    Displays item name, quantity, and unit with a checkbox for marking
    as obtained. Shows recipe breakdown in tooltip when applicable.

    Signals:
        itemChecked: Emitted when item's checkbox state changes.
    """

    itemChecked = Signal(str, bool)

    def __init__(self, item, view_model, breakdown_map, parent=None):
        """Initialize the ShoppingItem.

        Args:
            item: The shopping item data object.
            view_model: ViewModel to handle shopping operations.
            breakdown_map: Mapping of recipe ingredients for tooltips.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.item = item
        self.view_model = view_model
        self.breakdown_map = breakdown_map

        # Create widgets
        self.checkbox = QCheckBox()
        self.label = QLabel()
        self.label.setObjectName("ShoppingItem")

        # Configure display text with quantity and unit
        unit_display = f" {self.item.unit}" if self.item.unit else ""
        self.plain_text = f"{self.item.ingredient_name}: {self.item.formatted_quantity()}{unit_display}"

        self.label.setTextFormat(Qt.RichText)

        # Initialize checkbox state and apply styling
        self.checkbox.setChecked(self.item.have)
        self._update_label_style()  # Apply strikethrough if already obtained
        self._set_tooltip_if_needed()  # Add recipe breakdown tooltip

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)

        # Connections
        self.checkbox.stateChanged.connect(self.onToggled)

        # Track signal connections for cleanup
        self._signal_connections = [
            (self.checkbox.stateChanged, self.onToggled)
        ]

    # ── Lifecycle Methods ───────────────────────────────────────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Clean up signal connections to prevent memory leaks."""
        for signal, slot in self._signal_connections:
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass  # Signal already disconnected or object deleted
        self._signal_connections.clear()

    # ── Private Methods ─────────────────────────────────────────────────────────────────────────────────────

    def _update_label_style(self) -> None:
        """Apply or remove strike-through based on checkbox state."""
        if self.checkbox.isChecked():
            self.label.setText(f"<s>{self.plain_text}</s>")
        else:
            self.label.setText(self.plain_text)

        # Re-apply tooltip after text change to maintain consistency
        self._set_tooltip_if_needed()

    def _set_tooltip_if_needed(self) -> None:
        """Set recipe breakdown tooltip for recipe-sourced items.

        Shows which recipes use this ingredient and in what quantities.
        """
        if self.item.source == "recipe":
            parts = self.breakdown_map.get(self.item.key(), [])
            if parts:
                # Format tooltip with recipe breakdown for clarity
                header = f"Used in {len(parts)} recipe(s):"
                recipe_lines = [f"• {qty} {unit} - {name}" for name, qty, unit in parts]
                text = f"{header}\n" + "\n".join(recipe_lines)
                self.label.setToolTip(text)

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────

    def onToggled(self, state: int) -> None:
        """Handle checkbox toggle event.

        Args:
            state: Qt checkbox state value.
        """
        if self.view_model:
            self.view_model.toggle_item_status(self.item.id)
        self._update_label_style()

        # Notify parent category of state change
        self.itemChecked.emit(self.item.ingredient_name, self.checkbox.isChecked())


# ── View ────────────────────────────────────────────────────────────────────────────────────────────────────
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

        # Track currently loaded recipes for refresh operations
        self.active_recipe_ids: list[int] = []

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
        all_sections = list(grouped.items())
        if manual_items:
            all_sections.append(("Manual Entries", manual_items))

        for category, items in all_sections:
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
    def loadShoppingList(self, recipe_ids: list[int]) -> None:
        """Generate and display a categorized shopping list from recipes.

        Args:
            recipe_ids: List of recipe IDs to generate the shopping list from.
        """
        self.active_recipe_ids = recipe_ids
        DebugLogger.log(f"ShoppingList.loadShoppingList: recipe_ids={recipe_ids}", "debug")

        self._prepare_ui_for_refresh()
        self._refresh_shopping_data(recipe_ids)

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

    def _refresh_shopping_data(self, recipe_ids: list[int]) -> None:
        """Refresh shopping data using the ViewModel.

        Args:
            recipe_ids: Recipe IDs to generate shopping list from.
        """
        self.view_model.generate_shopping_list(recipe_ids)

    # ── ViewModel Signal Handlers ───────────────────────────────────────────────────────────────────────────
    def _on_list_updated(self, grouped_items: dict, manual_items: list) -> None:
        """Handle shopping list update from ViewModel.

        Args:
            grouped_items: Items grouped by category.
            manual_items: Manually added items.
        """
        DebugLogger.log("Shopping list updated by ViewModel", "debug")
        self._render_category_columns(grouped_items, manual_items)

    def _on_manual_item_added(self, message: str) -> None:
        """Handle successful manual item addition.

        Args:
            message: Success message to display.
        """
        DebugLogger.log(f"Manual item added: {message}", "info")
        self.show_success_message(message)

    def _on_error_occurred(self, error_type: str, error_message: str) -> None:
        """Handle error from ViewModel.

        Args:
            error_type: Category of error for logging.
            error_message: User-friendly error description.
        """
        DebugLogger.log(f"ViewModel error [{error_type}]: {error_message}", "error")
        self.show_error_message(error_message)

    def _on_validation_failed(self, errors: list) -> None:
        """Handle validation errors from ViewModel.

        Args:
            errors: List of validation error messages.
        """
        error_message = "; ".join(errors)
        DebugLogger.log(f"Validation failed: {error_message}", "warning")
        self.show_validation_error(error_message)

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
