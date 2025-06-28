"""app/ui/components/carousel/recipe_carousel.py

Animated carousel widget displaying up to three :class:`RecipeCard` widgets.
"""

from __future__ import annotations
from typing import Iterable, List

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame

from app.config import CAROUSEL
from app.ui.animations import Animator
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.recipe_card.constants import LayoutSize, LAYOUT_SIZE
from app.ui.widgets import CTToolButton


class RecipeCarousel(QFrame):
    """Carousel widget with left/right navigation and self-contained RecipeCards."""

    ANIM_DURATION = 300
    CARD_SPACING = 20

    # ── Signals ─────────────────────────────────────────────────────────────────────────
    current_recipe_changed = Signal(object)  # When center recipe changes via rotation

    def __init__(self, recipes: Iterable, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("RecipeCarousel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._recipes: List = list(recipes)
        self._current = 0
        self._is_animating = False

        self._init_buttons()
        self._init_cards()
        self._layout_widgets()
        self._update_cards()

    # ── Initialization ──────────────────────────────────────────────────────────────────
    def _init_buttons(self) -> None:
        """Create and configure navigation buttons."""
        left_config = CAROUSEL["LEFT"]
        right_config = CAROUSEL["RIGHT"]
        
        self.btn_left = CTToolButton(
            file_path=left_config["PATH"],
            icon_size=left_config["SIZE"],
            variant=left_config["DYNAMIC"],
            parent=self,
        )
        self.btn_right = CTToolButton(
            file_path=right_config["PATH"],
            icon_size=right_config["SIZE"],
            variant=right_config["DYNAMIC"],
            parent=self,
        )
        
        self.btn_left.clicked.connect(lambda: self.rotate(-1))
        self.btn_right.clicked.connect(lambda: self.rotate(1))

    def _init_cards(self) -> None:
        """Create recipe cards and set up their layout."""
        # Create three cards: medium, large (center), medium
        self.cards = [
            RecipeCard(LayoutSize.MEDIUM, self),
            RecipeCard(LayoutSize.MEDIUM, self),
            RecipeCard(LayoutSize.MEDIUM, self),
        ]
        
        # Connect navigation signals (cards handle their own recipe interactions)
        for i, card in enumerate(self.cards):
            card.card_clicked.connect(lambda recipe, pos=i: self._on_card_clicked(pos))
            card.add_meal_clicked.connect(lambda pos=i: self._on_card_clicked(pos))

        # Calculate positions and set card geometries
        sizes = [LAYOUT_SIZE["medium"], LAYOUT_SIZE["large"], LAYOUT_SIZE["medium"]]
        self._positions = self._calculate_positions(sizes)
        
        for card, rect in zip(self.cards, self._positions):
            card.setGeometry(rect)

        # Ensure center card draws on top
        self.cards[1].raise_()

        # Set carousel size based on card positions
        total_width = max(rect.right() for rect in self._positions) + 1
        total_height = max(rect.bottom() for rect in self._positions) + 1
        self.setFixedSize(total_width, total_height)

    def _layout_widgets(self) -> None:
        """Position navigation buttons beside the carousel."""
        button_spacing = 10
        center_y = self.height() // 2

        # Position left button
        left_x = -self.btn_left.width() - button_spacing
        left_y = center_y - self.btn_left.height() // 2
        self.btn_left.move(left_x, left_y)

        # Position right button
        right_x = self.width() + button_spacing
        right_y = center_y - self.btn_right.height() // 2
        self.btn_right.move(right_x, right_y)

    # ── Event Handlers ──────────────────────────────────────────────────────────────────
    def _on_card_clicked(self, card_position: int) -> None:
        """Handle card clicks for navigation. Cards handle their own recipe interactions."""
        if self._is_animating:
            return
            
        # Click side cards to center them
        if card_position == 0:  # Left card
            self.rotate(-1)
        elif card_position == 2:  # Right card
            self.rotate(1)
        # Center card interactions are handled by the RecipeCard itself

    # ── Helpers ─────────────────────────────────────────────────────────────────────────
    def _calculate_positions(self, sizes: List[QSize]) -> List[QRect]:
        """Calculate positions for the three cards."""
        left_size, center_size, right_size = sizes
        
        # Center the side cards vertically with the center card
        left_y_offset = (center_size.height() - left_size.height()) // 2
        right_y_offset = (center_size.height() - right_size.height()) // 2
        
        # Position cards with spacing
        x = 0
        left_rect = QRect(QPoint(x, left_y_offset), left_size)
        
        x += left_size.width() + self.CARD_SPACING
        center_rect = QRect(QPoint(x, 0), center_size)
        
        x += center_size.width() + self.CARD_SPACING
        right_rect = QRect(QPoint(x, right_y_offset), right_size)
        
        return [left_rect, center_rect, right_rect]

    def _update_button_states(self) -> None:
        """Enable/disable buttons based on recipe count and animation state."""
        has_multiple_recipes = len(self._recipes) > 1
        self.btn_left.setEnabled(has_multiple_recipes and not self._is_animating)
        self.btn_right.setEnabled(has_multiple_recipes and not self._is_animating)

    def _update_cards(self) -> None:
        """Update recipe content in all cards based on current position."""
        if not self._recipes:
            for card in self.cards:
                card.set_recipe(None)
            self._update_button_states()
            return

        n = len(self._recipes)
        indices = [
            (self._current - 1) % n,  # Left card
            self._current % n,        # Center card  
            (self._current + 1) % n,  # Right card
        ]

        for card, idx in zip(self.cards, indices):
            card.set_recipe(self._recipes[idx])
        
        self._update_button_states()
        
        # Emit when center recipe changes
        current_recipe = self.get_current_recipe()
        if current_recipe:
            self.current_recipe_changed.emit(current_recipe)

    # ── Navigation ──────────────────────────────────────────────────────────────────────
    def rotate(self, step: int) -> None:
        """Rotate the carousel by the given step."""
        if not self._recipes or self._is_animating:
            return
            
        self._is_animating = True
        self._update_button_states()
        
        self._current = (self._current + step) % len(self._recipes)
        
        # Reorder cards based on rotation direction
        if step > 0:  # Right rotation
            self.cards = [self.cards[1], self.cards[2], self.cards[0]]
        else:  # Left rotation
            self.cards = [self.cards[2], self.cards[0], self.cards[1]]

        # Animate cards to new positions
        sizes = [LAYOUT_SIZE["medium"], LAYOUT_SIZE["large"], LAYOUT_SIZE["medium"]]
        target_positions = self._calculate_positions(sizes)

        for card, target in zip(self.cards, target_positions):
            Animator.animate_geometry(card, card.geometry(), target, self.ANIM_DURATION)

        # Ensure center card is on top and update content when animation completes
        QTimer.singleShot(self.ANIM_DURATION // 2, self.cards[1].raise_)
        QTimer.singleShot(self.ANIM_DURATION, self._on_animation_finished)

    def _on_animation_finished(self) -> None:
        """Called when rotation animation completes."""
        self._is_animating = False
        self._update_cards()

    # ── Public API ──────────────────────────────────────────────────────────────────────
    def set_recipes(self, recipes: Iterable) -> None:
        """Update the carousel with new recipes."""
        self._recipes = list(recipes)
        self._current = 0
        self._update_cards()

    def get_current_recipe(self):
        """Get the currently centered recipe."""
        if not self._recipes:
            return None
        return self._recipes[self._current]

    def get_center_card(self) -> RecipeCard:
        """Get the center (featured) recipe card."""
        return self.cards[1]

    def get_all_cards(self) -> List[RecipeCard]:
        """Get all cards for parent widgets to connect signals."""
        return self.cards.copy()

    def navigate_to_recipe(self, recipe_id: int) -> bool:
        """Navigate to a specific recipe by ID. Returns True if found."""
        for i, recipe in enumerate(self._recipes):
            if hasattr(recipe, 'recipe_id') and recipe.recipe_id == recipe_id:
                if i != self._current:
                    steps_forward = (i - self._current) % len(self._recipes)
                    steps_backward = (self._current - i) % len(self._recipes)
                    
                    # Choose the shorter path
                    if steps_forward <= steps_backward:
                        for _ in range(steps_forward):
                            self.rotate(1)
                    else:
                        for _ in range(steps_backward):
                            self.rotate(-1)
                return True
        return False