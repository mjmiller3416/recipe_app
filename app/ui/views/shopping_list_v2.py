"""app/ui/views/shopping_list_v2.py

Shopping List view migrated to use the new navigation system with scrollable content.
"""

from collections import defaultdict

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QVBoxLayout, QWidget
)

from app.config import INGREDIENT_CATEGORIES, MEASUREMENT_UNITS
from app.core.services.shopping_service import ShoppingService
from app.style import Icon, Qss, Theme, Type
from app.ui.services.navigation_views_enhanced import ScrollableMainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType, RouteConstants
from app.ui.components.layout.card import ActionCard, BaseCard, Card
from app.ui.components.widgets import BaseButton, ComboBox, ToolButton
from app.ui.constants import LayoutConstants
from app.ui.utils.layout_utils import (
    set_fixed_height_for_layout_widgets,
    create_two_column_layout
)
from _dev_tools import DebugLogger

# Import the form and component classes from the original file
from .shopping_list import AddItemForm, CollapsibleCategory, ShoppingItem


@NavigationRegistry.register(
    path=RouteConstants.SHOPPING_LIST,
    view_type=ViewType.MAIN,
    title="Shopping List",
    description="View and manage your shopping list"
)
class ShoppingList(ScrollableMainView):
    """Shopping List view with route-based navigation and scrollable content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ShoppingList")
        
        # Register for component-specific styling
        Theme.register_widget(self, Qss.SHOPPING_LIST)
        
        DebugLogger.log("Initializing ShoppingList page (v2)", "info")

        # Initialize state
        self.active_recipe_ids: list[int] = []
        self.shopping_svc = None
        self._breakdown_map = {}

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
        
        # Add to the scroll layout (from ScrollableMainView)
        self.content_layout.addLayout(column_layout)

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

        entry_card.addWidget(self.add_item_form)
        return entry_card

    def _on_add_manual(self):
        """Handle the addition of a manual item to the shopping list."""
        try:
            name = self.add_item_form.le_item_name.text().strip()
            qty = float(self.add_item_form.le_item_qty.text().strip())
            unit = self.add_item_form.cb_item_unit.currentText()
            category = self.add_item_form.cb_item_category.currentText()

            if not name:
                return

            # Add manual item via service with DTO
            from app.core.dtos.shopping_dtos import ManualItemCreateDTO
            svc = ShoppingService()
            dto = ManualItemCreateDTO(
                ingredient_name=name,
                quantity=qty,
                unit=unit,
                category=category
            )
            svc.add_manual_item(dto)
            
            # Clear form
            self.add_item_form.le_item_name.clear()
            self.add_item_form.le_item_qty.clear()
            self.add_item_form.cb_item_unit.clearSelection()
            self.add_item_form.cb_item_category.clearSelection()
            
            # Refresh list
            self.loadShoppingList(self.active_recipe_ids)

        except ValueError:
            pass  # optionally show "Invalid quantity" feedback

    def _render_category_columns(self, grouped: dict, manual_items: list) -> None:
        """
        Renders all category sections using CollapsibleCategory widgets.

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

        shopping_svc = getattr(self, 'shopping_svc', None)
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
        self.active_recipe_ids = recipe_ids
        DebugLogger.log(f"ShoppingList.loadShoppingList: recipe_ids={recipe_ids}", "debug")

        # Clear current content
        self.list_container.clear()

        # Generate/update shopping list in database
        shopping_svc = ShoppingService()
        self.shopping_svc = shopping_svc
        shopping_svc.generate_shopping_list(recipe_ids)
        
        # Fetch all shopping items for display
        ingredients = shopping_svc.shopping_repo.get_all_shopping_items()
        DebugLogger.log(f"ShoppingList.load_shopping_list: fetched {len(ingredients)} items", "debug")
        
        # Get raw breakdown mapping for tooltips
        self._breakdown_map = shopping_svc.shopping_repo.get_ingredient_breakdown(recipe_ids)

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

        self._render_category_columns(grouped, manual_items)

    # Navigation lifecycle hooks
    def on_route_changed(self, path: str, params: dict):
        """Handle route changes."""
        DebugLogger.log(f"ShoppingList route changed: {path}", "info")
        # Handle any route-specific parameters if needed

    def before_navigate_to(self, path: str, params: dict) -> bool:
        """Called before navigating to shopping list."""
        DebugLogger.log("Preparing to show shopping list", "info")
        return True

    def after_navigate_to(self, path: str, params: dict):
        """Called after navigating to shopping list."""
        DebugLogger.log("Shopping list is now active", "info")
        
        # Load shopping list if we have active recipe IDs
        if self.active_recipe_ids:
            self.loadShoppingList(self.active_recipe_ids)

    def before_navigate_from(self, next_path: str, next_params: dict) -> bool:
        """Called before navigating away from shopping list."""
        DebugLogger.log(f"Leaving shopping list for: {next_path}", "info")
        
        # Save any pending state
        # Shopping list items are auto-saved when toggled, so no explicit save needed
        
        return True

    def after_navigate_from(self, next_path: str, next_params: dict):
        """Called after navigating away from shopping list."""
        DebugLogger.log("Left shopping list", "info")