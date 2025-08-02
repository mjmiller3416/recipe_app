"""app/ui/views/add_recipes.py

Defines the AddRecipes view for the recipe application.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.appearance import Theme, Qss
from app.ui.components.layout.card import Card
from app.ui.components.forms.recipe_form import RecipeForm

class AddRecipes(QWidget):
    """Placeholder class for the AddRecipes screen."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize & Setup UI
        self.setObjectName("AddRecipes")
        #Theme.register_widget(self, Qss.ADD_RECIPE)


        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Example Card
        card = Card(header="Add New Recipe", subheader="Fill in the details below")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setSpacing(36)
        summary_label = QLabel("This is a placeholder for add recipe content.")
        summary_label.setProperty("font", "Body")
        summary_label.setWordWrap(True)
        card.content_area.addWidget(summary_label)
        self.layout.addWidget(card)

        # Add stretch to push content to top
        self.layout.addStretch()
