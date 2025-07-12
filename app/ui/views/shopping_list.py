"""app/ui/pages/shopping_list/shopping_list.py

This module defines the ShoppingList screen, which allows users to view and manage their
shopping list. It includes functionality to add manual items, categorize ingredients, and
display them in a scrollable list
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
    )

from app.config import MEASUREMENT_UNITS
from app.core.services.shopping_service import ShoppingService
from app.ui.components.composite.shopping_item import ShoppingItemWidget
from dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingList(QWidget):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ShoppingList")

        DebugLogger.log("Initializing ShoppingList page", "debug")

        self.active_recipe_ids: list[int] = []  # store latest recipe list
        self.shopping_svc = None  # initialize shopping service
        self._breakdown_map = {}  # initialize breakdown map

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components for the ShoppingList screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # ── Manual Entry Bar ──
        add_bar = QHBoxLayout()

        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Qty")
        self.input_qty.setFixedWidth(60)

        self.input_unit = QComboBox()
        self.input_unit.addItems(MEASUREMENT_UNITS)
        self.input_unit.setFixedWidth(80)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ingredient name")

        self.btn_add = QPushButton("Add")
        self.btn_add.setFixedWidth(60)

        add_bar.addWidget(self.input_qty)
        add_bar.addWidget(self.input_unit)
        add_bar.addWidget(self.input_name)
        add_bar.addWidget(self.btn_add)

        main_layout.addLayout(add_bar)

        # ── Scrollable Area ──
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(12)

        scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(scroll_area)

        self.btn_add.clicked.connect(self._on_add_manual)

    def load_shopping_list(self, recipe_ids: list[int]):
        """
        Generate and display a categorized shopping list based on provided recipe IDs.

        Args:
            recipe_ids (list[int]): List of recipe IDs to generate the shopping list from.
        """
        self.active_recipe_ids = recipe_ids  # store active recipe IDs
        DebugLogger.log(f"ShoppingList.load_shopping_list: recipe_ids={recipe_ids}", "debug")

        # ── Clear Current List ──
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

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

        # ── Group By Category ──
        grouped = defaultdict(list)
        manual_items = []

        for item in ingredients:
            if item.source == "manual":
                manual_items.append(item)
            else:
                category = item.category or "Other"
                grouped[category].append(item)

        self._render_category_columns(grouped, manual_items) # render the list

        self.scroll_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _on_add_manual(self):
        """Handle the addition of a manual item to the shopping list."""
        try:
            name = self.input_name.text().strip()
            qty = float(self.input_qty.text().strip())
            unit = self.input_unit.currentText()

            if not name:
                return  # optionally show error

            # add manual item via service with DTO
            from app.core.dtos.shopping_dtos import ManualItemCreateDTO
            svc = ShoppingService()
            dto = ManualItemCreateDTO(
                ingredient_name=name,
                quantity=qty,
                unit=unit,
            )
            svc.add_manual_item(dto)
            self.input_name.clear()
            self.input_qty.clear()
            self.load_shopping_list(self.active_recipe_ids)  # refresh list

        except ValueError:
            pass  # optionally show “Invalid quantity” feedback

    def _render_category_columns(self, grouped: dict, manual_items: list) -> None:
        """
        Renders all category sections in two vertical columns, splitting by category (not by ingredient).

        Args:
            grouped (dict): Dict of {category: [ShoppingItem]}
            manual_items (list): List of manual entry ShoppingItems
        """
        column_layout = QHBoxLayout()

        left_container = QWidget()
        left_column = QVBoxLayout(left_container)
        left_column.setAlignment(Qt.AlignTop)

        right_container = QWidget()
        right_column = QVBoxLayout(right_container)
        right_column.setAlignment(Qt.AlignTop)

        all_sections = list(grouped.items())
        if manual_items:
            all_sections.append(("Manual Entries", manual_items))

        midpoint = (len(all_sections) + 1) // 2
        left_sections = all_sections[:midpoint]
        right_sections = all_sections[midpoint:]

        for target_column, section_group in ((left_column, left_sections), (right_column, right_sections)):
            for category, items in section_group:
                target_column.addLayout(self._build_category_section(category, items))

        # make columns expand evenly
        left_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        column_layout.addWidget(left_container)
        column_layout.addSpacing(40)
        column_layout.addWidget(right_container)
        self.scroll_layout.addLayout(column_layout)


    def _build_category_section(self, title: str, items: list) -> QVBoxLayout:
        """Creates a category header and its associated items as a vertical layout."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel(title.title()))

        # Ensure we have a shopping service
        shopping_svc = getattr(self, 'shopping_svc', None)
        # Ensure we have a breakdown map
        breakdown_map = getattr(self, '_breakdown_map', {})

        for item in items:
            item_widget = ShoppingItemWidget(item, shopping_svc, breakdown_map)
            layout.addWidget(item_widget)

        return layout
