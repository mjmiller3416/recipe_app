"""app/ui/views/shopping_list.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from collections import defaultdict

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
    """Form for manually adding new items to the shopping list."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AddShoppingItem")

        # Create Layout
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # Create labels and inputs for shopping item details - labels above inputs
        # Item Name
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

        # add labels and widgets to the form layout - two column layout with labels above inputs
        # Row 0: Item Name (full width)
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
    """Demo version of collapsible category widget."""

    # Signals
    toggled = Signal(bool)
    itemChecked = Signal(str, bool)

    def __init__(self, category_name, parent=None, start_expanded=False):
        super().__init__(parent)

        # Set initial values
        self._category_name = category_name
        self._is_expanded = start_expanded
        self._items = []

        self._setup_header()
        self._setup_content_area()
        self._setup_animation()

        # Force initial collapsed state to ensure proper height
        if not start_expanded:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)

        self._update_expand_state(animate=False)

    def _setup_header(self):
        """Create the category header."""
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

        # Make header clickable
        self._header_widget.mousePressEvent = lambda e: self.toggle()
        self._header_widget.setCursor(Qt.PointingHandCursor)

        self.addWidget(self._header_widget)

    def _setup_content_area(self):
        """Create the collapsible content area."""
        self._content_container = QWidget()
        self._content_container.setObjectName("ContentContainer")

        self._items_layout = QVBoxLayout(self._content_container)
        self._items_layout.setContentsMargins(16, 8, 16, 12)
        self._items_layout.setSpacing(8)

        self.addWidget(self._content_container)

    def _setup_animation(self):
        """Setup animation for expand/collapse."""
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(LayoutConstants.EXPAND_COLLAPSE_DURATION)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def _update_expand_state(self, animate=True):
        """Update visual state based on expansion."""
        if self._is_expanded:
            self._expand_content(animate)
        else:
            self._collapse_content(animate)

        self._update_expand_button()

    def _expand_content(self, animate=True):
        """Expand the content area."""
        self._content_container.setVisible(True)

        if animate:
            # Calculate natural height while still collapsed to avoid flash
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
        """Collapse the content area."""
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
        """Update expand button icon."""
        if self._is_expanded:
            icon_name = Icon.ANGLE_DOWN
            self._header_widget.setProperty("is_expanded", "True")
        else:
            icon_name = Icon.ANGLE_RIGHT
            self._header_widget.setProperty("is_expanded", "False")
        BaseButton.setIcon(self._expand_button, icon_name)

        # Force Qt to re-evaluate the stylesheet after property change
        self._header_widget.style().polish(self._header_widget)

        self._expand_button.setStateIconSize(24, 24)

    @property
    def category_name(self):
        return self._category_name

    @property
    def is_expanded(self):
        return self._is_expanded

    def toggle(self):
        """Toggle expansion state."""
        self._is_expanded = not self._is_expanded
        self._update_expand_state(animate=True)
        self.toggled.emit(self._is_expanded)

    def expand(self):
        """Expand the category."""
        if not self._is_expanded:
            self.toggle()

    def collapse(self):
        """Collapse the category."""
        if self._is_expanded:
            self.toggle()

    def addItem(self, item_name):
        """Add a simple checkbox item to the category."""
        checkbox = QCheckBox(item_name)
        checkbox.stateChanged.connect(lambda state: self.itemChecked.emit(item_name, state == Qt.Checked))
        self._items_layout.addWidget(checkbox)
        self._items.append(checkbox)
        return checkbox

    def addShoppingItem(self, shopping_item_widget):
        """Add a ShoppingItem widget to the category."""
        self._items_layout.addWidget(shopping_item_widget)
        self._items.append(shopping_item_widget)

    def setAllItemsChecked(self, checked):
        """Check or uncheck all items in this category."""
        for item in self._items:
            if isinstance(item, QCheckBox):
                item.setChecked(checked)
            elif hasattr(item, 'checkbox'):
                item.checkbox.setChecked(checked)

    def getCheckedItems(self):
        """Return a list of checked item names."""
        checked_items = []
        for item in self._items:
            if isinstance(item, QCheckBox) and item.isChecked():
                checked_items.append(item.text())
            elif hasattr(item, 'checkbox') and item.checkbox.isChecked():
                if hasattr(item, 'item') and hasattr(item.item, 'ingredient_name'):
                    checked_items.append(item.item.ingredient_name)
        return checked_items

    def cleanup(self):
        """Clean up all item widgets to prevent memory leaks."""
        for item in self._items:
            if hasattr(item, 'cleanup'):
                item.cleanup()
        self._items.clear()

class ShoppingItem(QWidget):
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

        # Configure widgets
        unit_display = f" {self.item.unit}" if self.item.unit else ""
        self.plain_text = f"{self.item.ingredient_name}: {self.item.formatted_quantity()}{unit_display}"

        self.label.setTextFormat(Qt.RichText)

        self.checkbox.setChecked(self.item.have)
        self._update_label_style() # set initial style after checkbox state is set
        self._set_tooltip_if_needed() # set tooltip after label text is finalized

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

    def cleanup(self):
        """Clean up signal connections to prevent memory leaks."""
        for signal, slot in self._signal_connections:
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass  # Signal already disconnected or object deleted
        self._signal_connections.clear()

    def _update_label_style(self):
        """Apply or remove strike-through based on checkbox state."""
        if self.checkbox.isChecked():
            self.label.setText(f"<s>{self.plain_text}</s>")
        else:
            self.label.setText(self.plain_text)

        # Always ensure tooltip is set after text change
        self._set_tooltip_if_needed()

    def _set_tooltip_if_needed(self):
        """Sets the recipe breakdown tooltip."""
        if self.item.source == "recipe":
            parts = self.breakdown_map.get(self.item.key(), [])
            if parts:
                # Create a more readable tooltip format
                header = f"Used in {len(parts)} recipe(s):"
                recipe_lines = [f"• {qty} {unit} - {name}" for name, qty, unit in parts]
                text = f"{header}\n" + "\n".join(recipe_lines)
                self.label.setToolTip(text)

    def onToggled(self, state):
        """Handle the toggle action."""
        if self.view_model:
            self.view_model.toggle_item_status(self.item.id)
        self._update_label_style()

        # Emit signal for category management
        self.itemChecked.emit(self.item.ingredient_name, self.checkbox.isChecked())


# ── View ────────────────────────────────────────────────────────────────────────────────────────────────────
class ShoppingList(ScrollableNavView):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        ScrollableNavView.__init__(self, parent)
        DebugLogger.log("Initializing ShoppingList page", "info")
        self.setObjectName("ShoppingList")
        Theme.register_widget(self, Qss.SHOPPING_LIST)

        # Initialize ViewModel
        self.view_model = ShoppingListViewModel()

        # Connect ViewModel signals
        self._connect_view_model_signals()

        # State tracking
        self.active_recipe_ids: list[int] = []

    def _connect_view_model_signals(self):
        """Connect ViewModel signals to UI update methods."""
        self.view_model.list_updated.connect(self._on_list_updated)
        self.view_model.manual_item_added.connect(self._on_manual_item_added)
        self.view_model.error_occurred.connect(self._on_error_occurred)
        self.view_model.validation_failed.connect(self._on_validation_failed)
        self.view_model.processing_state_changed.connect(self._on_processing_state_changed)
        self.view_model.loading_state_changed.connect(self._on_loading_state_changed)

    def _build_ui(self):
        """Setup the UI components for the ShoppingList view."""

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

    def _create_list_container(self):
        """Setup the UI components for the List Container."""
        list_container = Card()
        list_container.setObjectName("ListContainer")
        list_container.setHeader("Auto Generated Ingredients")
        list_container.setSubHeader("from this weeks meal plan")
        list_container.setSpacing(10)
        return list_container

    def _create_entry_card(self):
        """Setup the UI components for the Entry Card."""
        self.add_item_form = AddItemForm()
        entry_card = ActionCard()
        entry_card.setObjectName("EntryCard")
        entry_card.expandHeight(False)
        entry_card.setHeader("Add Item")
        entry_card.setSubHeader("Add item to your list")
        entry_card.addButton("Add", alignment=Qt.AlignRight, callback=self._on_add_manual)

        entry_card.addWidget(self.add_item_form) # add the form to the card
        return entry_card

    def _on_add_manual(self):
        """Handle the addition of a manual item to the shopping list."""
        name = self.add_item_form.le_item_name.text()
        qty = self.add_item_form.le_item_qty.text()
        unit = self.add_item_form.cb_item_unit.currentText()
        category = self.add_item_form.cb_item_category.currentText()

        # Add manual item via ViewModel
        success = self.view_model.add_manual_item(name, qty, unit, category)

        if success:
            # Clear form on successful addition
            self.add_item_form.le_item_name.clear()
            self.add_item_form.le_item_qty.clear()
            self.add_item_form.cb_item_unit.clearSelection()
            self.add_item_form.cb_item_category.clearSelection()

    def _render_category_columns(self, grouped: dict, manual_items: list) -> None:
        """
        Renders all category sections in a single column using CollapsibleCategory widgets.

        Args:
            grouped (dict): Dict of {category: [ShoppingItem]}
            manual_items (list): List of manual entry ShoppingItems
        """
        all_sections = list(grouped.items())
        if manual_items:
            all_sections.append(("Manual Entries", manual_items))

        for category, items in all_sections:
            category_widget = self._create_category_section(category, items)
            self.list_container.addWidget(category_widget)

    def _create_category_section(self, title: str, items: list) -> CollapsibleCategory:
        """Creates a CollapsibleCategory widget and populates it with ShoppingItem widgets."""
        category_widget = CollapsibleCategory(title, start_expanded=False)

        # Get breakdown map from ViewModel
        breakdown_map = self.view_model.get_breakdown_map()

        for item in items:
            item_widget = ShoppingItem(item, self.view_model, breakdown_map)
            category_widget.addShoppingItem(item_widget)

        return category_widget

    def loadShoppingList(self, recipe_ids: list[int]):
        """
        Generate and display a categorized shopping list based on provided recipe IDs.

        Args:
            recipe_ids (list[int]): List of recipe IDs to generate the shopping list from.
        """
        self.active_recipe_ids = recipe_ids
        DebugLogger.log(f"ShoppingList.loadShoppingList: recipe_ids={recipe_ids}", "debug")

        self._prepare_ui_for_refresh()
        self._refresh_shopping_data(recipe_ids)

    def _prepare_ui_for_refresh(self):
        """Prepare UI for shopping list refresh by clearing current content."""
        # Clean up existing widgets to prevent memory leaks
        self._cleanup_existing_widgets()
        self.list_container.clear()

    def _cleanup_existing_widgets(self):
        """Clean up existing shopping item widgets to prevent memory leaks."""
        # Find all CollapsibleCategory widgets and clean them up
        for i in range(self.list_container.layout().count()):
            item = self.list_container.layout().itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'cleanup'):
                item.widget().cleanup()

    def _refresh_shopping_data(self, recipe_ids: list[int]):
        """Refresh shopping data using the ViewModel."""
        self.view_model.generate_shopping_list(recipe_ids)

    # ── ViewModel Signal Handlers ──────────────────────────────────────────────────────────────────────────

    def _on_list_updated(self, grouped_items: dict, manual_items: list):
        """Handle shopping list update from ViewModel."""
        DebugLogger.log("Shopping list updated by ViewModel", "debug")
        self._render_category_columns(grouped_items, manual_items)

    def _on_manual_item_added(self, message: str):
        """Handle successful manual item addition."""
        DebugLogger.log(f"Manual item added: {message}", "info")
        self.show_success_message(message)

    def _on_error_occurred(self, error_type: str, error_message: str):
        """Handle error from ViewModel."""
        DebugLogger.log(f"ViewModel error [{error_type}]: {error_message}", "error")
        self.show_error_message(error_message)

    def _on_validation_failed(self, errors: list):
        """Handle validation errors from ViewModel."""
        error_message = "; ".join(errors)
        DebugLogger.log(f"Validation failed: {error_message}", "warning")
        self.show_validation_error(error_message)

    def _on_processing_state_changed(self, is_processing: bool):
        """Handle processing state change from ViewModel."""
        if is_processing:
            DebugLogger.log("ViewModel processing started", "debug")
            # Optionally disable UI during processing
        else:
            DebugLogger.log("ViewModel processing completed", "debug")

    def _on_loading_state_changed(self, is_loading: bool, operation: str):
        """Handle loading state change from ViewModel."""
        if is_loading:
            DebugLogger.log(f"ViewModel loading: {operation}", "debug")
            # Optionally show loading indicator
        else:
            DebugLogger.log("ViewModel loading completed", "debug")

    # ── User Feedback Methods ───────────────────────────────────────────────────────────────────────────────────

    def show_success_message(self, message: str):
        """Show success message using Toast notification."""
        toast = Toast(message, self, success=True)
        toast.show_toast()

    def show_error_message(self, message: str):
        """Show error message using Toast notification."""
        toast = Toast(message, self, success=False)
        toast.show_toast()

    def show_validation_error(self, message: str):
        """Show validation error message using Toast notification."""
        toast = Toast(f"Validation Error: {message}", self, success=False)
        toast.show_toast()
