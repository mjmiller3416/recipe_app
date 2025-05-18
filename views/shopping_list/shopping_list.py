
# ── Imports ─────────────────────────────────────────────────────────────────────
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from config import MEASUREMENT_UNITS
from database.models.meal_selection import MealSelection
from services.shopping_service import ShoppingService


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingList(QWidget):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.setObjectName("ShoppingList")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumSize(984, 818)

        self.active_recipe_ids: list[int] = []  # store latest recipe list

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components for the ShoppingList screen."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # ── Manual Add Section ──
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

        # ── Scrollable List Section ──
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
        self.active_recipe_ids = recipe_ids # store active recipe IDs

        # ── Clear Current List ──
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        ingredients = ShoppingService.generate_shopping_list(recipe_ids) # fetch ingredients from the service

        # ── Group By Category ──
        grouped = defaultdict(list)
        manual_items = []

        for item in ingredients:
            if item.source == "manual":
                manual_items.append(item)
            else:
                category = item.category or "Other"
                grouped[category].append(item)

        # ── Display Recipe Ingredients ──
        for category in sorted(grouped.keys()):
            self._render_two_column_section(category, grouped[category], is_manual=False)

        # ── Display Manual Items ──
        if manual_items:
            self._render_two_column_section("Manual Entries", manual_items, is_manual=True)

        self.scroll_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _on_add_manual(self):
        """Handle the addition of a manual item to the shopping list."""
        try:
            name = self.input_name.text().strip()
            qty = float(self.input_qty.text().strip())
            unit = self.input_unit.currentText()

            if not name:
                return  # Optionally show error

            ShoppingService.add_manual_item(name, qty, unit)
            self.input_name.clear()
            self.input_qty.clear()
            self.load_shopping_list(self.active_recipe_ids)  # Refresh list

        except ValueError:
            pass  # Optionally show “Invalid quantity” feedback

    def _render_two_column_section(self, title: str, items: list, is_manual: bool = False) -> None:
        """
        Render a section with a two-column layout of ingredients.

        Args:
            title (str): Section title to display above the group.
            items (list): List of ShoppingItem instances.
            is_manual (bool): Whether to wire up toggle/save logic for manual items.
        """
        header = QLabel(title.title())
        header.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
        self.scroll_layout.addWidget(header)

        row_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        midpoint = (len(items) + 1) // 2
        left_items = items[:midpoint]
        right_items = items[midpoint:]

        for column, col_items in zip((left_column, right_column), (left_items, right_items)):
            for item in col_items:
                checkbox = QCheckBox(item.label())
                checkbox.setChecked(item.have)

                if is_manual:
                    def on_toggle(state, i=item):
                        i.toggle_have()
                        model = i.to_model()
                        model.save()
                    checkbox.stateChanged.connect(on_toggle)

                column.addWidget(checkbox)

        row_layout.addLayout(left_column)
        row_layout.addSpacing(40)
        row_layout.addLayout(right_column)
        self.scroll_layout.addLayout(row_layout)
