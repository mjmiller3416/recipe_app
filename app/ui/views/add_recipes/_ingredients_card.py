"""app/ui/views/add_recipes/_ingredients_card.py

This module defines the IngredientsCard class, which provides a container for managing
ingredient input forms within a card layout. It includes functionality to add and remove
ingredient forms dynamically and to collect ingredient data.
"""

# ── Imports ──
from PySide6.QtCore import Qt, Signal

from app.style import Name
from app.ui.components.layout.card import ActionCard
from ._ingredient_form import IngredientForm
from ..base import BaseView


class IngredientsCard(ActionCard):
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
        self._build_ui()


    # ── Private ──
    def _build_ui(self):
        """Set up the container UI with initial ingredient and add button."""
        # Add initial ingredient widget
        self._add_ingredient_widget()

        # Add button to card footer with left alignment and ADD icon
        self.addButton("Add Ingredient", icon=Name.ADD, alignment=Qt.AlignLeft)

        # Customize button icon size and connect click event
        if self.button:
            self.button.setIconSize(24, 24)
            # Connect to a method that adds AND focuses
            self.button.clicked.connect(self._on_add_button_clicked)

    def _on_add_button_clicked(self):
        """Handle add ingredient button click - add widget and set focus."""
        # Add the new ingredient
        self._add_ingredient_widget()

        # Get the newly added widget (last in the list)
        if self.ingredient_widgets:
            new_widget = self.ingredient_widgets[-1]
            # Set focus with a small delay to ensure rendering
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._focus_new_ingredient(new_widget))

    def _focus_new_ingredient(self, widget):
        """Set focus to the first input field of the ingredient widget."""
        if widget and hasattr(widget, 'cb_unit') and widget.cb_unit:
            widget.cb_unit.setFocus(Qt.TabFocusReason)

            # Update the parent's last_focused_widget tracker
            parent_view = self.parent()
            while parent_view and not isinstance(parent_view, BaseView):
                parent_view = parent_view.parent()

            if parent_view and hasattr(parent_view, 'last_focused_widget'):
                parent_view.last_focused_widget = widget.cb_unit

    def _get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)

    def _add_ingredient_widget(self):
        """Add a new ingredient widget to the container."""
        ingredient_widget = IngredientForm()
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        self.ingredient_widgets.append(ingredient_widget)
        self.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientForm):
        """Remove an ingredient widget from the container."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.removeWidget(widget)
            widget.deleteLater()

        self.ingredients_changed.emit()


    # ── Public ──
    def getAllIngredientsData(self) -> list[dict]:
        """Collect data from all ingredient widgets."""
        ingredients_data = []

        for widget in self.ingredient_widgets:
            data = widget.getIngredientData()
            # Only include ingredients with at least a name
            if data.get("ingredient_name", "").strip():
                ingredients_data.append(data)

        return ingredients_data

    def clearAllIngredients(self):
        """Clear all ingredient widgets and add one empty one."""
        # Remove all existing widgets
        for widget in self.ingredient_widgets:
            self.removeWidget(widget)
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()


