"""app/ui/components/composite/recipe_info_cards.py

A reusable component for displaying recipe information cards (time, servings, category, dietary)
in a horizontal row layout. Extracted from FullRecipe for use in multiple contexts.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel

from app.core.models.recipe import Recipe
from app.style.icon import Icon, AppIcon
from app.style import Qss, Theme


# ── Info Card ───────────────────────────────────────────────────────────────────────────────────────────────
class InfoCard(QWidget):
    """A vertical info card with icon, title, and value for recipe metadata."""

    def __init__(self, icon: Icon, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoCard")

        # Register for component-specific styling
        Theme.register_widget(self, Qss.INFO_CARD)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        # Icon
        self.icon_widget = AppIcon(icon)
        self.icon_widget.setSize(32, 32)
        self.icon_widget.setColor("tertiary")
        self.icon_widget.setObjectName("InfoCardIcon")

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("InfoCardTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setObjectName("InfoCardValue")
        self.value_label.setAlignment(Qt.AlignCenter)

        # Add to layout
        layout.addWidget(self.icon_widget, 0, Qt.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def setTitle(self, title: str):
        """Update the title text."""
        self.title_label.setText(title)

    def setValue(self, value: str):
        """Update the value text."""
        self.value_label.setText(value)

    def setIcon(self, icon: Icon):
        """Update the icon."""
        self.icon_widget.setIcon(icon)

    def setIconSize(self, size: int):
        """Update the icon size."""
        self.icon_widget.setSize(size, size)

    def setIconColor(self, color: str):
        """Update the icon color."""
        self.icon_widget.setColor(color)


# ── Recipe Info Card ────────────────────────────────────────────────────────────────────────────────────────
class RecipeInfoCard(QWidget):
    """A horizontal row of info cards showing recipe metadata."""

    def __init__(self, show_cards: list = None, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeInfoCard")

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

        # Default styling properties
        self.icon_size = 32, 32
        self.icon_color = "tertiary"

    def _applyCardStyling(self, card):
        """Apply current styling properties to a card."""
        card.setIconSize(self.icon_size[0])
        card.setIconColor(self.icon_color)

    def _clearCards(self):
        """Clear all existing cards from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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
                self._applyCardStyling(self.time_card)
                self.layout.addWidget(self.time_card)
            elif card_type == "servings":
                self.servings_card = InfoCard(Icon.SERVINGS, "Servings", servings)
                self._applyCardStyling(self.servings_card)
                self.layout.addWidget(self.servings_card)
            elif card_type == "category":
                self.category_card = InfoCard(Icon.CATEGORY, "Category", category)
                self._applyCardStyling(self.category_card)
                self.layout.addWidget(self.category_card)
            elif card_type == "dietary":
                self.dietary_card = InfoCard(Icon.DIET_PREF, "Dietary", diet_pref)
                self._applyCardStyling(self.dietary_card)
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
                self._applyCardStyling(self.time_card)
                self.layout.addWidget(self.time_card)
            elif card_type == "servings":
                self.servings_card = InfoCard(Icon.SERVINGS, "Servings", servings)
                self._applyCardStyling(self.servings_card)
                self.layout.addWidget(self.servings_card)
            elif card_type == "category":
                self.category_card = InfoCard(Icon.CATEGORY, "Category", category)
                self._applyCardStyling(self.category_card)
                self.layout.addWidget(self.category_card)
            elif card_type == "dietary":
                self.dietary_card = InfoCard(Icon.DIET_PREF, "Dietary", diet_pref)
                self._applyCardStyling(self.dietary_card)
                self.layout.addWidget(self.dietary_card)

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
        else:
            self.layout.setSpacing(20)

    def setIconSize(self, width: int, height: int):
        """Set the icon size for all info cards."""
        self.icon_size = width, height
        # Apply to existing cards
        for card in [self.time_card, self.servings_card, self.category_card, self.dietary_card]:
            if card:
                card.setIconSize(width)

    def setIconColor(self, color: str):
        """Set the icon color for all info cards."""
        self.icon_color = color
        # Apply to existing cards
        for card in [self.time_card, self.servings_card, self.category_card, self.dietary_card]:
            if card:
                card.setIconColor(color)
