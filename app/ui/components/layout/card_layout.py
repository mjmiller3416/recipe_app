"""app/ui/components/layout/card_layout.py

Specialized layout manager for Card widgets with declarative API.
Provides complete control over card sizing, proportions, and alignment.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Union
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout, QHBoxLayout, QVBoxLayout, QWidget, 
    QSizePolicy, QSpacerItem
)

from app.ui.components.layout.card import Card


class Direction(Enum):
    """Layout direction for CardLayout."""
    HORIZONTAL = QBoxLayout.LeftToRight
    VERTICAL = QBoxLayout.TopToBottom


class HeightMode(Enum):
    """Height behavior for cards in layout."""
    MATCH = "match"          # All cards match height of tallest
    CONTENT = "content"      # Cards size to their content
    FIXED = "fixed"          # Cards maintain fixed height


class AlignmentMode(Enum):
    """Vertical alignment for cards."""
    STRETCH = "stretch"      # Cards stretch to fill available height
    TOP = "top"             # Cards align to top
    CENTER = "center"       # Cards align to center
    BOTTOM = "bottom"       # Cards align to bottom


class CardLayout(QBoxLayout):
    """Specialized layout manager for Card widgets with declarative API.
    
    This layout manager provides complete control over Card widget behavior
    including proportional sizing, height matching, and alignment control.
    
    Features:
    - Proportional sizing with simple API
    - Automatic height matching or content-based sizing
    - Flexible alignment options
    - Responsive gap control
    - Card grouping capabilities
    - Clean, declarative syntax
    
    Example:
        layout = CardLayout(Direction.HORIZONTAL)
        layout.addCard(card1, proportion=2)  # Takes 2/3 of space
        layout.addCard(card2, proportion=1)  # Takes 1/3 of space
        layout.setHeightMode(HeightMode.MATCH)
    """
    
    def __init__(
        self, 
        direction: Direction = Direction.VERTICAL,
        parent: Optional[QWidget] = None
    ):
        """Initialize CardLayout with specified direction.
        
        Args:
            direction: Layout direction (HORIZONTAL or VERTICAL)
            parent: Optional parent widget
        """
        super().__init__(direction.value, parent)
        
        self._cards: List[Card] = []
        self._proportions: Dict[Card, int] = {}
        self._alignment_mode = AlignmentMode.STRETCH
        self._height_mode = HeightMode.CONTENT
        self._card_spacing = 16
        self._groups: Dict[str, List[Card]] = {}
        
        # Set default layout properties
        self.setSpacing(self._card_spacing)
        self.setContentsMargins(0, 0, 0, 0)  # No margins by default
    
    # ── Core Card Management ────────────────────────────────────────────────
    def addCard(
        self, 
        card: Card, 
        proportion: Optional[int] = None,
        align: Optional[AlignmentMode] = None
    ) -> 'CardLayout':
        """Add a card to the layout with optional proportion and alignment.
        
        Args:
            card: Card widget to add
            proportion: Proportional size (None for content-based sizing)
            align: Override alignment for this specific card
            
        Returns:
            Self for method chaining
        """
        if not isinstance(card, Card):
            raise TypeError("CardLayout only accepts Card widgets")
        
        self._cards.append(card)
        
        # Set proportion if specified
        if proportion is not None:
            self._proportions[card] = proportion
            stretch = proportion
        else:
            stretch = 0
        
        # Configure size policy based on proportion and direction
        if proportion is not None:
            if self.direction() == QBoxLayout.LeftToRight:
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            else:
                card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        else:
            # For non-proportional cards, ensure they don't get cut off
            if self.direction() == QBoxLayout.LeftToRight:
                card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            else:
                card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # Ensure minimum size is respected
        card.setMinimumSize(card.sizeHint())
        
        # Add to layout with stretch factor
        self.addWidget(card, stretch)
        
        # Apply current layout settings
        self._update_card_behaviors()
        
        return self
    
    def removeCard(self, card: Card) -> 'CardLayout':
        """Remove a card from the layout.
        
        Args:
            card: Card widget to remove
            
        Returns:
            Self for method chaining
        """
        if card in self._cards:
            self._cards.remove(card)
            self._proportions.pop(card, None)
            self.removeWidget(card)
            self._update_card_behaviors()
        
        return self
    
    def clearCards(self) -> 'CardLayout':
        """Remove all cards from the layout.
        
        Returns:
            Self for method chaining
        """
        for card in self._cards.copy():
            self.removeCard(card)
        return self
    
    # ── Proportion Management ───────────────────────────────────────────────
    def setProportions(self, *proportions: int) -> 'CardLayout':
        """Set proportions for all cards in order.
        
        Args:
            *proportions: Proportion values for each card in order
            
        Returns:
            Self for method chaining
            
        Example:
            layout.setProportions(2, 1, 1)  # First card gets 2/4, others get 1/4 each
        """
        for i, proportion in enumerate(proportions):
            if i < len(self._cards):
                card = self._cards[i]
                self._proportions[card] = proportion
                self.setStretch(i, proportion)
                
                # Update size policy for proportional cards
                if self.direction() == QBoxLayout.LeftToRight:
                    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                else:
                    card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self._update_card_behaviors()
        return self
    
    def setCardProportion(self, card: Card, proportion: int) -> 'CardLayout':
        """Set proportion for a specific card.
        
        Args:
            card: Card to modify
            proportion: New proportion value
            
        Returns:
            Self for method chaining
        """
        if card in self._cards:
            index = self._cards.index(card)
            self._proportions[card] = proportion
            self.setStretch(index, proportion)
            
            # Update size policy
            if self.direction() == QBoxLayout.LeftToRight:
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            else:
                card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        return self
    
    # ── Layout Behavior Control ─────────────────────────────────────────────
    def setHeightMode(self, mode: HeightMode) -> 'CardLayout':
        """Set how cards handle height sizing.
        
        Args:
            mode: Height behavior mode
            
        Returns:
            Self for method chaining
        """
        self._height_mode = mode
        self._update_card_behaviors()
        return self
    
    def setAlignmentMode(self, mode: AlignmentMode) -> 'CardLayout':
        """Set vertical alignment for all cards.
        
        Args:
            mode: Alignment mode
            
        Returns:
            Self for method chaining
        """
        self._alignment_mode = mode
        self._update_card_behaviors()
        return self
    
    def setCardSpacing(self, spacing: int) -> 'CardLayout':
        """Set spacing between cards.
        
        Args:
            spacing: Spacing in pixels
            
        Returns:
            Self for method chaining
        """
        self._card_spacing = spacing
        self.setSpacing(spacing)
        return self
    
    def setMargins(self, left: int, top: int, right: int, bottom: int) -> 'CardLayout':
        """Set layout margins to prevent card cutoff.
        
        Args:
            left: Left margin
            top: Top margin  
            right: Right margin
            bottom: Bottom margin
            
        Returns:
            Self for method chaining
        """
        self.setContentsMargins(left, top, right, bottom)
        return self
    
    def createContainer(self, parent: Optional[QWidget] = None) -> QWidget:
        """Create a properly configured container widget for this layout.
        
        This handles the common case where you need a widget to hold the layout
        with proper size policies to prevent card cutoff issues.
        
        Args:
            parent: Optional parent widget
            
        Returns:
            QWidget configured with this layout and proper size policies
        """
        container = QWidget(parent)
        container.setLayout(self)
        
        # Set appropriate size policy based on direction
        if self.direction() == QBoxLayout.LeftToRight:
            container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        else:
            container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # Ensure container respects content size
        container.setMinimumSize(container.sizeHint())
        
        return container
    
    # ── Advanced Features ───────────────────────────────────────────────────
    def groupCards(self, cards: List[Card], group_name: str, proportion: Optional[int] = None) -> 'CardLayout':
        """Group multiple cards to be treated as a single unit.
        
        Args:
            cards: List of cards to group
            group_name: Name for the group
            proportion: Optional proportion for the entire group
            
        Returns:
            Self for method chaining
        """
        self._groups[group_name] = cards
        
        if proportion is not None:
            # Calculate individual proportions within the group
            individual_proportion = proportion // len(cards)
            for card in cards:
                if card in self._cards:
                    self.setCardProportion(card, individual_proportion)
        
        return self
    
    def autoSize(self) -> 'CardLayout':
        """Automatically calculate optimal proportions based on content.
        
        Returns:
            Self for method chaining
        """
        # This could analyze card content and set intelligent defaults
        # For now, set equal proportions for all cards
        if self._cards:
            equal_proportion = 1
            for card in self._cards:
                self._proportions[card] = equal_proportion
                index = self._cards.index(card)
                self.setStretch(index, equal_proportion)
        
        return self
    
    def addStretch(self, stretch: int = 1) -> 'CardLayout':
        """Add stretchable space to the layout.
        
        Args:
            stretch: Stretch factor
            
        Returns:
            Self for method chaining
        """
        super().addStretch(stretch)
        return self
    
    def addSpacing(self, spacing: int) -> 'CardLayout':
        """Add fixed spacing to the layout.
        
        Args:
            spacing: Spacing in pixels
            
        Returns:
            Self for method chaining
        """
        super().addSpacing(spacing)
        return self
    
    # ── Internal Methods ────────────────────────────────────────────────────
    def _update_card_behaviors(self):
        """Apply current height and alignment settings to all cards."""
        for card in self._cards:
            self._apply_height_mode(card)
            self._apply_alignment_mode(card)
    
    def _apply_height_mode(self, card: Card):
        """Apply height mode to a specific card."""
        current_h_policy = card.sizePolicy().horizontalPolicy()
        
        if self._height_mode == HeightMode.MATCH:
            card.setSizePolicy(current_h_policy, QSizePolicy.Expanding)
        elif self._height_mode == HeightMode.CONTENT:
            card.setSizePolicy(current_h_policy, QSizePolicy.Preferred)
        elif self._height_mode == HeightMode.FIXED:
            card.setSizePolicy(current_h_policy, QSizePolicy.Fixed)
    
    def _apply_alignment_mode(self, card: Card):
        """Apply alignment mode to a specific card."""
        # Alignment is handled by the layout itself through widget alignment
        # Individual card alignment would require wrapper widgets
        pass
    
    # ── Properties ──────────────────────────────────────────────────────────
    @property
    def cards(self) -> List[Card]:
        """Get list of all cards in the layout."""
        return self._cards.copy()
    
    @property
    def proportions(self) -> Dict[Card, int]:
        """Get current proportions for all cards."""
        return self._proportions.copy()
    
    @property
    def height_mode(self) -> HeightMode:
        """Get current height mode."""
        return self._height_mode
    
    @property
    def alignment_mode(self) -> AlignmentMode:
        """Get current alignment mode."""
        return self._alignment_mode
    
    @property
    def card_spacing(self) -> int:
        """Get current card spacing."""
        return self._card_spacing


# ── Convenience Functions ──────────────────────────────────────────────────
def HorizontalCardLayout(parent: Optional[QWidget] = None) -> CardLayout:
    """Create a horizontal CardLayout.
    
    Args:
        parent: Optional parent widget
        
    Returns:
        CardLayout configured for horizontal direction
    """
    return CardLayout(Direction.HORIZONTAL, parent)


def VerticalCardLayout(parent: Optional[QWidget] = None) -> CardLayout:
    """Create a vertical CardLayout.
    
    Args:
        parent: Optional parent widget
        
    Returns:
        CardLayout configured for vertical direction
    """
    return CardLayout(Direction.VERTICAL, parent)