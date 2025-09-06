"""app/ui/views/add_recipes/cards.py

Contains custom Card classes for the AddRecipes view, including IngredientsCard and DirectionsNotesCard.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QWidget

from app.style.icon.config import Name
from app.ui.components.layout.card import ActionCard, Card
from app.ui.components.widgets.button import Button, Type
from ..add_recipes.ingredient_form import IngredientForm

class IngredientsCard(ActionCard):
    """
    Container for managing ingredient widgets within a Card.
    Provides add/remove functionality and data collection.
    """

    ingredients_changed = Signal()  # Emitted when ingredients are added/removed

    def __init__(self, ingredient_view_model=None, parent=None):
        """Initialize the ingredient container."""
        super().__init__(card_type="Default", parent=parent)

        self.setHeader("Ingredients")
        self.setSubHeader("List all the ingredients required for this recipe.")

        self.ingredient_view_model = ingredient_view_model
        self.ingredient_widgets = []
        self._build_ui()

    def _build_ui(self):
        """Set up the container UI with initial ingredient and add button."""

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
        ingredient_widget = IngredientForm(ingredient_view_model=self.ingredient_view_model)
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        self.ingredient_widgets.append(ingredient_widget)
        self.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientForm):
        """Remove an ingredient widget from the container with proper cleanup."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.removeWidget(widget)

            # Performance optimization: cleanup resources before deletion
            widget.cleanup()
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
        """Clear all ingredient widgets with proper cleanup and add one empty one."""
        # Performance optimization: cleanup resources before removal
        for widget in self.ingredient_widgets:
            self.removeWidget(widget)
            widget.cleanup()  # Clean up resources before deletion
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()

    def get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)

class DirectionsNotesCard(Card):
    """Custom card with toggle between Directions and Notes content."""

    def __init__(self, parent=None):
        super().__init__(card_type="Default")
        self.setHeader("Directions & Notes")
        self.setMinimumHeight(600)  # set minimum height to ensure enough space for content

        # Create toggle buttons container
        self.toggle_container = QWidget()
        self.toggle_container.setObjectName("ToggleContainer")
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(1, 1, 1, 1)
        toggle_layout.setSpacing(0)

        # Create toggle buttons using custom Button class
        self.btn_directions = Button("Directions", Type.PRIMARY)
        self.btn_notes = Button("Notes", Type.SECONDARY)

        # Set object names for styling
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")

        # Add buttons to toggle layout
        toggle_layout.addWidget(self.btn_directions)
        toggle_layout.addWidget(self.btn_notes)

        # Create content areas
        self.te_directions = QTextEdit()
        self.te_directions.setObjectName("DirectionsTextEdit")
        self.te_directions.setPlaceholderText("Enter cooking directions here...")

        self.te_notes = QTextEdit()
        self.te_notes.setObjectName("NotesTextEdit")
        self.te_notes.setPlaceholderText("Add any additional notes here...")

        # Add components to card
        self.addWidget(self.toggle_container)
        self.addWidget(self.te_directions)
        self.addWidget(self.te_notes)

        # Initially show directions, hide notes
        self.te_notes.hide()

        # Connect signals
        self.btn_directions.clicked.connect(self._show_directions)
        self.btn_notes.clicked.connect(self._show_notes)

    def _show_directions(self):
        """Show directions content and update button states."""
        self.te_directions.show()
        self.te_notes.hide()
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")
        self._refresh_button_styles()

    def _show_notes(self):
        """Show notes content and update button states."""
        self.te_directions.hide()
        self.te_notes.show()
        self.btn_directions.setObjectName("ToggleButtonInactive")
        self.btn_notes.setObjectName("ToggleButtonActive")
        self._refresh_button_styles()

    def _refresh_button_styles(self):
        """Force refresh of button styles after state change."""
        for btn in [self.btn_directions, self.btn_notes]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
