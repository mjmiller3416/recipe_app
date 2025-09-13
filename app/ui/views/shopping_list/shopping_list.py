"""app/ui/views/shopping_list/shopping_list.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list
"""

# ── Imports ──
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

from _dev_tools import DebugLogger
from app.core.services import ShoppingService
from app.ui.components.layout.card import ActionCard, Card
from app.ui.utils import create_two_column_layout
from app.ui.views.base import BaseView

from ._add_item_form import AddItemForm
from ._collapsible_category import CollapsibleCategory
from ._shopping_item import ShoppingItem


class ShoppingList(BaseView):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ShoppingList")

        DebugLogger.log("Initializing ShoppingList page", "info")

        self.active_recipe_ids: list[int] = []  # store latest recipe list
        self.shopping_svc = None  # initialize shopping service
        self._breakdown_map = {}  # initialize breakdown map

        self._build_ui()

    def _build_ui(self) -> None:
        """Setup the UI components for the ShoppingList view.

        Creates two-column layout with shopping list on left and
        add item form on right.
        """
        self.list_container = self._create_list_container()
        self.entry_card = self._create_entry_card()

        # IMPORTANT: Set size policies to allow proper expansion
        # The list container should expand vertically as content is added
        self.list_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Entry card should maintain its natural size
        self.entry_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        column_layout = create_two_column_layout(
            left_widgets   = [self.list_container],
            right_widgets  = [self.entry_card],
            left_ratio    = 3,
            right_ratio   = 1,
            match_heights = False  # Important: Don't force matching heights
        )

        # Remove the minimum height constraint - let content determine height
        # self.list_container.setMinimumHeight(self.entry_card.sizeHint().height())

        self.content_layout.addLayout(column_layout)

        # Add stretch at the bottom to push content up when list is small
        self.content_layout.addStretch()

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

        # Ensure the card can expand its height based on content
        list_container.expandHeight(False)  # Don't force expansion, let content determine

        return list_container

    def _create_entry_card(self) -> ActionCard:
        """Create the card for manually adding items.

        Returns:
            ActionCard with embedded AddItemForm.
        """
        self.add_item_form = AddItemForm()
        entry_card = ActionCard()
        entry_card.setObjectName("EntryCard")
        entry_card.expandHeight(False)  # Keep natural height
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

            # Ensure category widgets can expand properly
            category_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

            self.list_container.addWidget(category_widget)

    def _build_category_section(self, title: str, items: list) -> CollapsibleCategory:
        """Creates a CollapsibleCategory widget and populates it with ShoppingItem widgets."""
        # Start with categories collapsed to avoid initial squishing
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
        self.list_container.clear()

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

        if hasattr(self, 'scroll_area'):
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._render_category_columns(grouped, manual_items) # render the list

        # Force the scroll area to update its size after loading content
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
