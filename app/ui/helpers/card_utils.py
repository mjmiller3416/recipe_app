"""app/ui/helpers/card_utils.py

Clean utility functions for working with Card widgets in layouts.
All functions preserve card shadow effects by avoiding wrapper containers that clip shadows.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import List, Optional

from PySide6.QtWidgets import QHBoxLayout, QLayout, QVBoxLayout

from app.ui.components.layout.card import Card


def add_cards_horizontal(
    parent_layout: QLayout,
    cards: List[Card],
    proportions: Optional[List[int]] = None,
    spacing: int = 16,
    match_heights: bool = True
) -> None:
    """Add cards horizontally to an existing layout (preserves shadow effects).

    Intelligently adds cards directly when possible to avoid shadow clipping.

    Args:
        parent_layout: The layout to add cards to (QHBoxLayout or QVBoxLayout)
        cards: List of Card widgets
        proportions: Optional list of stretch factors
        spacing: Spacing between cards
        match_heights: Whether cards should match each other's height
    """
    if isinstance(parent_layout, QHBoxLayout):
        # Direct horizontal addition - no wrapper needed
        for i, card in enumerate(cards):
            stretch = proportions[i] if proportions and i < len(proportions) else 0

            if stretch > 0:
                card.expandWidth(True)

            if match_heights:
                card.expandHeight(True)

            # Add spacing before card (except for first card)
            if i > 0:
                parent_layout.addSpacing(spacing)

            parent_layout.addWidget(card, stretch)

    elif isinstance(parent_layout, QVBoxLayout):
        # Create minimal horizontal sub-layout only when necessary
        h_layout = QHBoxLayout()
        h_layout.setSpacing(spacing)
        h_layout.setContentsMargins(0, 0, 0, 0)

        for i, card in enumerate(cards):
            stretch = proportions[i] if proportions and i < len(proportions) else 0

            if stretch > 0:
                card.expandWidth(True)

            if match_heights:
                card.expandHeight(True)

            h_layout.addWidget(card, stretch)

        parent_layout.addLayout(h_layout)

    else:
        raise TypeError("Parent layout must be QHBoxLayout or QVBoxLayout")


def add_cards_vertical(
    parent_layout: QLayout,
    cards: List[Card],
    proportions: Optional[List[int]] = None,
    spacing: int = 16
) -> None:
    """Add cards vertically to a layout (preserves shadow effects).

    Args:
        parent_layout: The layout to add cards to
        cards: List of Card widgets
        proportions: Optional list of stretch factors
        spacing: Spacing between cards
    """
    for i, card in enumerate(cards):
        stretch = proportions[i] if proportions and i < len(proportions) else 0

        if stretch > 0:
            card.expandHeight(True)

        # Add spacing before card (except for first card)
        if i > 0:
            parent_layout.addSpacing(spacing)

        parent_layout.addWidget(card, stretch)


def add_two_column(
    parent_layout: QLayout,
    left_card: Card,
    right_card: Card,
    left_proportion: int = 2,
    right_proportion: int = 1,
    spacing: int = 16,
    match_heights: bool = True
) -> None:
    """Add two cards horizontally to a layout (preserves shadow effects).

    Args:
        parent_layout: The layout to add cards to
        left_card: Card for left column
        right_card: Card for right column
        left_proportion: Stretch factor for left card
        right_proportion: Stretch factor for right card
        spacing: Spacing between cards
        match_heights: Whether cards should match height
    """
    add_cards_horizontal(
        parent_layout,
        [left_card, right_card],
        [left_proportion, right_proportion],
        spacing,
        match_heights
    )


def add_three_column(
    parent_layout: QLayout,
    left_card: Card,
    center_card: Card,
    right_card: Card,
    proportions: List[int] = [1, 2, 1],
    spacing: int = 16,
    match_heights: bool = True
) -> None:
    """Add three cards horizontally to a layout (preserves shadow effects).

    Args:
        parent_layout: The layout to add cards to
        left_card: Card for left column
        center_card: Card for center column
        right_card: Card for right column
        proportions: Stretch factors for [left, center, right]
        spacing: Spacing between cards
        match_heights: Whether cards should match height
    """
    add_cards_horizontal(
        parent_layout,
        [left_card, center_card, right_card],
        proportions,
        spacing,
        match_heights
    )


# Utility functions for card configuration
def setup_proportional_cards(cards: List[Card], proportions: List[int], direction: str = "horizontal") -> None:
    """Configure cards for proportional sizing.

    Args:
        cards: List of Card widgets
        proportions: List of proportion values
        direction: "horizontal" or "vertical"
    """
    for i, card in enumerate(cards):
        if i < len(proportions) and proportions[i] > 0:
            if direction == "horizontal":
                card.expandWidth(True)
            else:
                card.expandHeight(True)


def match_card_heights(cards: List[Card]) -> None:
    """Make all cards expand to match each other's height.

    Args:
        cards: List of Card widgets to match heights
    """
    for card in cards:
        card.expandHeight(True)


def match_card_widths(cards: List[Card]) -> None:
    """Make all cards expand to match each other's width.

    Args:
        cards: List of Card widgets to match widths
    """
    for card in cards:
        card.expandWidth(True)
