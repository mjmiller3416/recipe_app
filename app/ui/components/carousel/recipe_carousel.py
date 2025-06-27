"""app/ui/components/carousel/recipe_carousel.py

Animated carousel widget displaying up to three :class:`RecipeCard` widgets.
"""

from __future__ import annotations

from typing import Iterable, List

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtWidgets import QFrame

from app.config import CAROUSEL
from app.ui.animations import Animator
from app.ui.components.recipe_card import RecipeCard
from app.ui.components.recipe_card.constants import LayoutSize, LAYOUT_SIZE
from app.ui.widgets import CBToolButton


class RecipeCarousel(QFrame):
    """Carousel widget with left/right navigation."""

    ANIM_DURATION = 300

    def __init__(self, recipes: Iterable, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("RecipeCarousel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._recipes: List = list(recipes)
        self._current = 0

        self._init_buttons()
        self._init_cards()
        self._layout_widgets()
        self._update_cards()

    # ── Initialization ──────────────────────────────────────────────────────
    def _init_buttons(self) -> None:
        left = CAROUSEL["LEFT"]
        right = CAROUSEL["RIGHT"]
        self.btn_left = CBToolButton(
            file_path=left["PATH"],
            icon_size=left["SIZE"],
            variant=left["DYNAMIC"],
            parent=self,
        )
        self.btn_right = CBToolButton(
            file_path=right["PATH"],
            icon_size=right["SIZE"],
            variant=right["DYNAMIC"],
            parent=self,
        )
        self.btn_left.clicked.connect(lambda: self.rotate(-1))
        self.btn_right.clicked.connect(lambda: self.rotate(1))

    def _init_cards(self) -> None:
        self.cards = [
            RecipeCard(LayoutSize.MEDIUM, self),
            RecipeCard(LayoutSize.LARGE, self),
            RecipeCard(LayoutSize.MEDIUM, self),
        ]
        for card in self.cards:
            card.setParent(self)
            card.setAttribute(Qt.WA_StyledBackground, True)

        sizes = [LAYOUT_SIZE["medium"], LAYOUT_SIZE["large"], LAYOUT_SIZE["medium"]]
        self._positions = self._calc_positions(sizes)
        for card, rect in zip(self.cards, self._positions):
            card.setGeometry(rect)

        # layering so center card draws on top
        self.cards[1].raise_()

        container_width = max(r.right() for r in self._positions) + 1
        container_height = max(r.bottom() for r in self._positions) + 1
        self.setFixedSize(container_width, container_height)

    def _layout_widgets(self) -> None:
        # place buttons beside the carousel frame
        spacing = 10
        self.btn_left.move(0 - self.btn_left.width() - spacing, self.height() // 2 - self.btn_left.height() // 2)
        self.btn_right.move(self.width() + spacing, self.height() // 2 - self.btn_right.height() // 2)

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _calc_positions(self, sizes: List[QSize]) -> List[QRect]:
        spacing = 20
        left_size, center_size, right_size = sizes
        y_offset = (center_size.height() - left_size.height()) // 2
        x = 0
        rect_left = QRect(QPoint(x, y_offset), left_size)
        x += left_size.width() + spacing
        rect_center = QRect(QPoint(x, 0), center_size)
        x += center_size.width() + spacing
        y_offset_r = (center_size.height() - right_size.height()) // 2
        rect_right = QRect(QPoint(x, y_offset_r), right_size)
        return [rect_left, rect_center, rect_right]

    # ── Card Updates ────────────────────────────────────────────────────────
    def _update_cards(self) -> None:
        if not self._recipes:
            for card in self.cards:
                card.set_recipe(None)
            return

        n = len(self._recipes)
        left_idx = (self._current - 1) % n
        center_idx = self._current % n
        right_idx = (self._current + 1) % n

        self.cards[0].set_recipe(self._recipes[left_idx])
        self.cards[1].set_recipe(self._recipes[center_idx])
        self.cards[2].set_recipe(self._recipes[right_idx])

    # ── Navigation ─────────────────────────────────────────────────────────-
    def rotate(self, step: int) -> None:
        if not self._recipes:
            return
        self._current = (self._current + step) % len(self._recipes)
        # rotate card widgets
        if step > 0:
            self.cards = [self.cards[1], self.cards[2], self.cards[0]]
        else:
            self.cards = [self.cards[2], self.cards[0], self.cards[1]]

        sizes = [LAYOUT_SIZE["medium"], LAYOUT_SIZE["large"], LAYOUT_SIZE["medium"]]
        target_rects = self._calc_positions(sizes)

        for card, target in zip(self.cards, target_rects):
            Animator.animate_geometry(card, card.geometry(), target, self.ANIM_DURATION)

        # ensure center card on top
        QTimer.singleShot(self.ANIM_DURATION // 2, self.cards[1].raise_)
        QTimer.singleShot(self.ANIM_DURATION, self._update_cards)

    # exposed for tests
    def set_recipes(self, recipes: Iterable) -> None:
        self._recipes = list(recipes)
        self._current = 0
        self._update_cards()
