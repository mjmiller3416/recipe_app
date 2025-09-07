"""app/ui/views/recipe_browser/recipe_card_pool.py

Manages a pool of recipe card widgets to optimize performance by reusing them.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from collections import deque
from typing import Deque, List

from app.ui.components.composite.recipe_card import LayoutSize
from app.ui.components.composite.recipe_card import create_recipe_card
from _dev_tools.debug_logger import DebugLogger

from PySide6.QtWidgets import QWidget


class RecipeCardPool:
    """Object pool for recipe cards to reduce creation/destruction overhead."""

    def __init__(self, card_size: LayoutSize, max_pool_size: int = 50):
        self.card_size = card_size
        self.available_cards: Deque = deque(maxlen=max_pool_size)
        self.in_use_cards: List = []
        self.max_pool_size = max_pool_size
        self.parent_widget = None

    def set_parent_widget(self, parent: QWidget):
        """Set parent widget for creating new cards."""
        self.parent_widget = parent

    def get_card(self):
        """Get a recipe card from pool or create new one."""
        if self.available_cards:
            card = self.available_cards.popleft()
            self.in_use_cards.append(card)

            # Reset card state
            card.setVisible(True)
            card.set_recipe(None)  # Reset to empty state

            DebugLogger.log(f"Reused card from pool (pool size: {len(self.available_cards)})", "debug")
            return card

        # Create new card if pool is empty
        if self.parent_widget:
            card = create_recipe_card(self.card_size, parent=self.parent_widget)
            self.in_use_cards.append(card)
            DebugLogger.log(f"Created new card (in use: {len(self.in_use_cards)})", "debug")
            return card

        return None

    def return_card(self, card):
        """Return card to pool for reuse."""
        if card in self.in_use_cards:
            self.in_use_cards.remove(card)

            # Reset card state for reuse
            card.setVisible(False)
            card.set_recipe(None)

            # Add to pool if not at capacity
            if len(self.available_cards) < self.max_pool_size:
                self.available_cards.append(card)
                DebugLogger.log(f"Returned card to pool (pool size: {len(self.available_cards)})", "debug")
            else:
                # Pool full - delete card
                card.deleteLater()
                DebugLogger.log("Pool full, deleted excess card", "debug")

    def return_all_cards(self):
        """Return all in-use cards to the pool."""
        cards_to_return = self.in_use_cards.copy()
        for card in cards_to_return:
            self.return_card(card)

    def clear_pool(self):
        """Clear all cards from pool."""
        # Delete available cards
        while self.available_cards:
            card = self.available_cards.popleft()
            card.deleteLater()

        # Delete in-use cards
        for card in self.in_use_cards:
            card.deleteLater()
        self.in_use_cards.clear()

        DebugLogger.log("Recipe card pool cleared", "debug")
