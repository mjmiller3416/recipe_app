"""app/ui/components/composite/recipe_info_cards.py

A reusable component for displaying recipe information cards (time, servings, category, dietary)
in a horizontal row layout. Extracted from FullRecipe for use in multiple contexts.
"""

from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.core.models.recipe import Recipe
from app.style.icon import Icon
from app.ui.components.widgets.info_card import InfoCard


class RecipeInfoCards(QWidget):
    """A horizontal row of info cards showing recipe metadata."""

    def __init__(self, show_cards: list = None, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeInfoCards")

        # Default cards to show if none specified
        self.show_cards = show_cards or ["time", "servings", "category", "dietary"]

        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)

        # Info card widgets (will be populated when recipe is set)
        self.time_card = None
        self.servings_card = None
        self.category_card = None
        self.dietary_card = None

    def setRecipe(self, recipe: Recipe):
        """Set the recipe and update the info cards display."""
        # Clear existing cards
        self._clearCards()

        # Get recipe data with fallbacks
        total_time = str(getattr(recipe, "total_time", "")) or "2 hours 30 mins"
        servings = str(getattr(recipe, "servings", "")) or "6"
        category = getattr(recipe, "recipe_category", "") or "Main Course"
        diet_pref = getattr(recipe, "diet_pref", "") or "High-Protein"

        # Create and add cards based on show_cards configuration
        for card_type in self.show_cards:
            if card_type == "time":
                self.time_card = InfoCard(Icon.TOTAL_TIME, "Total Time", total_time)
                self.layout.addWidget(self.time_card)
            elif card_type == "servings":
                self.servings_card = InfoCard(Icon.SERVINGS, "Servings", servings)
                self.layout.addWidget(self.servings_card)
            elif card_type == "category":
                self.category_card = InfoCard(Icon.CATEGORY, "Category", category)
                self.layout.addWidget(self.category_card)
            elif card_type == "dietary":
                self.dietary_card = InfoCard(Icon.DIET_PREF, "Dietary", diet_pref)
                self.layout.addWidget(self.dietary_card)

    def setInfoData(self, total_time: str = None, servings: str = None,
                   category: str = None, diet_pref: str = None):
        """Set info card data directly with string values (alternative to setRecipe)."""
        # Clear existing cards
        self._clearCards()

        # Use provided values or defaults
        total_time = total_time or "2 hours 30 mins"
        servings = servings or "6"
        category = category or "Main Course"
        diet_pref = diet_pref or "High-Protein"

        # Create and add cards based on show_cards configuration
        for card_type in self.show_cards:
            if card_type == "time":
                self.time_card = InfoCard(Icon.TOTAL_TIME, "Total Time", total_time)
                self.layout.addWidget(self.time_card)
            elif card_type == "servings":
                self.servings_card = InfoCard(Icon.SERVINGS, "Servings", servings)
                self.layout.addWidget(self.servings_card)
            elif card_type == "category":
                self.category_card = InfoCard(Icon.CATEGORY, "Category", category)
                self.layout.addWidget(self.category_card)
            elif card_type == "dietary":
                self.dietary_card = InfoCard(Icon.DIET_PREF, "Dietary", diet_pref)
                self.layout.addWidget(self.dietary_card)

    def _clearCards(self):
        """Clear all existing cards from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def setCardsToShow(self, cards: list):
        """Update which cards should be displayed."""
        self.show_cards = cards

    def setSpacing(self, spacing: int):
        """Set the spacing between info cards."""
        self.layout.setSpacing(spacing)

    def setCompactMode(self, compact: bool = True):
        """Toggle compact mode for smaller card spacing."""
        if compact:
            self.layout.setSpacing(10)
            # Could also adjust card sizes here if InfoCard supports it
        else:
            self.layout.setSpacing(20)
