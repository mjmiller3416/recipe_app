"""app/ui/components/containers/ingredient_container.py

Container widget for managing multiple IngredientWidget instances within a Card.
Handles adding, removing, and collecting ingredient data.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton

from app.style.icon import Name, Type
from app.ui.components.forms.ingredient_widget import IngredientWidget
from app.ui.components.layout.card import Card
from app.ui.components.widgets import ToolButton


# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientContainer(Card):
    """
    Container for managing ingredient widgets within a Card.
    Provides add/remove functionality and data collection.
    """

    ingredients_changed = Signal()  # Emitted when ingredients are added/removed

    def __init__(self, parent=None):
        """Initialize the ingredient container."""
        super().__init__(card_type="Default", parent=parent)

        self.setHeader("Ingredients")
        self.setSubHeader("List all the ingredients required for this recipe.")

        self.ingredient_widgets = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the container UI with initial ingredient and add button."""

        # Create container widget for ingredients
        self.ingredients_widget = QWidget()
        self.ingredients_layout = QVBoxLayout(self.ingredients_widget)
        self.ingredients_layout.setContentsMargins(0, 0, 0, 0)
        self.ingredients_layout.setSpacing(8)

        # Add the ingredients container to the card
        self.addWidget(self.ingredients_widget)

        # Add initial ingredient widget
        self._add_ingredient_widget()

        # Add button to card footer with left alignment and ADD icon
        self.addButton("Add Ingredient", icon=Name.ADD, alignment=Qt.AlignLeft)

        # Customize button icon size and connect click event
        if self.button:
            self.button.setIconSize(24, 24)  # Set custom icon size
            self.button.clicked.connect(self._add_ingredient_widget)

    def _add_ingredient_widget(self):
        """Add a new ingredient widget to the container."""
        ingredient_widget = IngredientWidget()
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        self.ingredient_widgets.append(ingredient_widget)
        self.ingredients_layout.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientWidget):
        """Remove an ingredient widget from the container."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.ingredients_layout.removeWidget(widget)
            widget.deleteLater()

        self.ingredients_changed.emit()

    def get_all_ingredients_data(self) -> list[dict]:
        """Collect data from all ingredient widgets."""
        ingredients_data = []

        for widget in self.ingredient_widgets:
            data = widget.get_ingredient_data()
            # Only include ingredients with at least a name
            if data.get("ingredient_name", "").strip():
                ingredients_data.append(data)

        return ingredients_data

    def clear_all_ingredients(self):
        """Clear all ingredient widgets and add one empty one."""
        # Remove all existing widgets
        for widget in self.ingredient_widgets:
            self.ingredients_layout.removeWidget(widget)
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()

    def get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)
