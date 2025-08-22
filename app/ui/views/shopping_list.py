"""app/ui/views/shopping_list/shopping_list.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from collections import defaultdict

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QScrollArea, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS
from app.core.services.shopping_service import ShoppingService
from app.style import Icon, Qss, Theme, Type
from app.ui.components.layout.card import ActionCard, BaseCard, Card
from app.ui.components.widgets import BaseButton, ComboBox, ToolButton
from app.ui.helpers.ui_helpers import set_fixed_height_for_layout_widgets
from dev_tools import DebugLogger

# ── Constants ────────────────────────────────────────────────────────────────────────────────
FIXED_HEIGHT = 60  # fixed height for input fields in the recipe form

# ── Add Item Form ────────────────────────────────────────────────────────────────────────────
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
        self.le_item_name.setObjectName("ItemNameLineEdit")

        # Qty.
        self.lbl_item_qty = QLabel("Qty.")
        self.le_item_qty = QLineEdit()
        self.le_item_qty.setPlaceholderText("e.g. 2")
        self.le_item_qty.setObjectName("QtyLineEdit")

        # Unit
        self.lbl_item_unit = QLabel("Unit")
        self.cb_item_unit = ComboBox(list_items=MEASUREMENT_UNITS, placeholder="e.g. bottle")
        self.cb_item_unit.setObjectName("ComboBox")
        self.cb_item_unit.setProperty("context", "shopping_item")

        # Category
        self.lbl_item_category = QLabel("Category")
        self.cb_item_category = ComboBox(list_items=INGREDIENT_CATEGORIES, placeholder="Select category")
        self.cb_item_category.setObjectName("ComboBox")
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
            height = FIXED_HEIGHT,
            skip   = (QLabel,)
        )

# ── Collapsible Category ─────────────────────────────────────────────────────────────────────
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
        self._animation.setDuration(250)
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
                lambda: self._content_container.setMaximumHeight(16777215),
                Qt.SingleShotConnection
            )
            self._animation.start()
        else:
            self._content_container.setMaximumHeight(16777215)

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

# ── Shopping Item ────────────────────────────────────────────────────────────────────────────
class ShoppingItem(QWidget):
    itemChecked = Signal(str, bool)

    def __init__(self, item, shopping_svc, breakdown_map, parent=None):
        """Initialize the ShoppingItem.

        Args:
            item: The shopping item data object.
            shopping_svc: Service to manage shopping list operations.
            breakdown_map: Mapping of recipe ingredients for tooltips.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.item = item
        self.shopping_svc = shopping_svc
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
        DebugLogger.log(f"Setting tooltip for ingredient {self.item.ingredient_name}, source: {self.item.source}, key: {self.item.key()}", "debug")

        if self.item.source == "recipe":
            parts = self.breakdown_map.get(self.item.key(), [])
            DebugLogger.log(f"Found {len(parts)} parts in breakdown_map for ingredient", "debug")
            if parts:
                # Create a more readable tooltip format
                header = f"Used in {len(parts)} recipe(s):"
                recipe_lines = [f"• {qty} {unit} - {name}" for name, qty, unit in parts]
                text = f"{header}\n" + "\n".join(recipe_lines)
                DebugLogger.log(f"Setting ingredient tooltip: {text}", "debug", text=text)
                self.label.setToolTip(text)
            else:
                DebugLogger.log("No recipe parts found for ingredient, skipping tooltip", "debug")
        else:
            DebugLogger.log("Non-recipe shopping item, no tooltip needed", "debug")

    def onToggled(self, state):
        """Handle the toggle action."""
        if self.shopping_svc:
            self.shopping_svc.toggle_item_status(self.item.id)
        self._update_label_style()

        # Emit signal for category management
        self.itemChecked.emit(self.item.ingredient_name, self.checkbox.isChecked())

# ── Shopping List View ───────────────────────────────────────────────────────────────────────
class ShoppingList(QWidget):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ShoppingList")
        # register for component-specific styling
        Theme.register_widget(self, Qss.SHOPPING_LIST)

        DebugLogger.log("Initializing ShoppingList page", "info")

        self.active_recipe_ids: list[int] = []  # store latest recipe list
        self.shopping_svc = None  # initialize shopping service
        self._breakdown_map = {}  # initialize breakdown map

        self._build_ui()

    def _build_ui(self):
        """Setup the UI components for the ShoppingList screen."""
        # Main layout for the entire widget
        self.lyt_main = QVBoxLayout(self)
        self.lyt_main.setContentsMargins(0, 0, 0, 0)
        self.lyt_main.setSpacing(0)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create content widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(30)
        self.scroll_layout.setContentsMargins(140, 40, 140, 40)
        self.scroll_content.setObjectName("ShoppingListContent")

        # Set the content widget to the scroll area
        self.scroll_area.setWidget(self.scroll_content)
        self.lyt_main.addWidget(self.scroll_area)

        # Shopping container card (2/3 width)
        self.shopping_container = Card()
        self.shopping_container.setObjectName("ListContainer")
        self.shopping_container.setHeader("Auto Generated Ingredients")
        self.shopping_container.setSubHeader("from this weeks meal plan")
        self.shopping_container.setSpacing(10)

        # Add item card (1/3 width)
        add_item_card = ActionCard()
        add_item_card.setObjectName("AddItemCard")
        add_item_card.expandHeight(False)  # Prevent vertical expansion to maintain natural size

        # Add Item Form to action card
        self.add_item_form = AddItemForm()
        add_item_card.addWidget(self.add_item_form)
        add_item_card.setHeader("Manual Add")
        add_item_card.setSubHeader("Add item to your list")
        add_item_card.addButton("Add", alignment=Qt.AlignRight, callback=self._on_add_manual)

        # Add widgets to horizontal layout - shopping list takes 4/7, add form takes 3/7
        self.scroll_layout.addWidget(self.shopping_container, stretch=5)
        self.scroll_layout.addWidget(add_item_card, stretch=3, alignment=Qt.AlignTop)

    def _on_add_manual(self):
        """Handle the addition of a manual item to the shopping list."""
        try:
            name = self.add_item_form.le_item_name.text().strip()
            qty = float(self.add_item_form.le_item_qty.text().strip())
            unit = self.add_item_form.cb_item_unit.currentText()
            category = self.add_item_form.cb_item_category.currentText()

            if not name:
                return  # optionally show error

            # add manual item via service with DTO
            from app.core.dtos.shopping_dtos import ManualItemCreateDTO
            svc = ShoppingService()
            dto = ManualItemCreateDTO(
                ingredient_name=name,
                quantity=qty,
                unit=unit,
                category=category
            )
            svc.add_manual_item(dto)
            self.add_item_form.le_item_name.clear()
            self.add_item_form.le_item_qty.clear()
            self.add_item_form.cb_item_unit.clearSelection()
            self.add_item_form.cb_item_category.clearSelection()
            self.loadShoppingList(self.active_recipe_ids)  # refresh list

        except ValueError:
            pass  # optionally show "Invalid quantity" feedback

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
            category_widget = self._build_category_section(category, items)
            self.shopping_container.addWidget(category_widget)

    def _build_category_section(self, title: str, items: list) -> CollapsibleCategory:
        """Creates a CollapsibleCategory widget and populates it with ShoppingItem widgets."""
        category_widget = CollapsibleCategory(title, start_expanded=False)

        # Ensure we have a shopping service
        shopping_svc = getattr(self, 'shopping_svc', None)
        # Ensure we have a breakdown map
        breakdown_map = getattr(self, '_breakdown_map', {})

        for item in items:
            item_widget = ShoppingItem(item, shopping_svc, breakdown_map)
            category_widget.addShoppingItem(item_widget)

        return category_widget

    def loadShoppingList(self, recipe_ids: list[int]):
        """
        Generate and display a categorized shopping list based on provided recipe IDs.

        Args:
            recipe_ids (list[int]): List of recipe IDs to generate the shopping list from.
        """
        self.active_recipe_ids = recipe_ids  # store active recipe IDs
        DebugLogger.log(f"ShoppingList.loadShoppingList: recipe_ids={recipe_ids}", "debug")

        # Clear current shopping container content
        self.shopping_container.clear()

        # generate/update shopping list in database
        shopping_svc = ShoppingService()
        self.shopping_svc = shopping_svc
        shopping_svc.generate_shopping_list(recipe_ids)
        # fetch all shopping items (models) for display
        ingredients = shopping_svc.shopping_repo.get_all_shopping_items()
        DebugLogger.log(f"ShoppingList.load_shopping_list: fetched {len(ingredients)} items", "debug")
        # get raw breakdown mapping for tooltips
        self._breakdown_map = shopping_svc.shopping_repo.get_ingredient_breakdown(recipe_ids)

        # Initialize empty breakdown map if None
        if self._breakdown_map is None:
            self._breakdown_map = {}

        # Group ingredients by category
        grouped = defaultdict(list)
        manual_items = []

        for item in ingredients:
            if item.source == "manual":
                manual_items.append(item)
            else:
                category = item.category or "Other"
                grouped[category].append(item)

        self._render_category_columns(grouped, manual_items) # render the list
