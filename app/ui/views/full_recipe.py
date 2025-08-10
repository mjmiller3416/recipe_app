"""app/ui/views/full_recipe.py

FullRecipe view — matches the mock UI with Cards for:
- Title + chips
- Banner placeholder (1200×600)
- Meta summary (time, servings, category, dietary)
- Ingredients
- Directions
- Notes

Styling:
- Registers for component-specific QSS with Theme.register_widget(self, Qss.FULLRECIPE)
- Expect an external stylesheet to target objectNames/properties set here.
"""
from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QSpacerItem,
    QScrollArea,
)

# ── App Imports ──────────────────────────────────────────────────────────────────────────────
# Icons
from app.style.icon import AppIcon  # QLabel-based themed icon widget
from app.style.icon.config import Name  # Icon enum

# Theme hook (component registration)
from app.style import Theme, Qss

# Card container
from app.ui.components.layout.card import Card

# Data model
from app.core.models import Recipe


# ── Helpers ──────────────────────────────────────────────────────────────────────────────────
class BannerPlaceholder(QFrame):
    """Simple banner placeholder (1200×600) until upload/cropping is implemented."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BannerPlaceholder")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(360)  # keeps a nice aspect on most windows
        self.setProperty("tag", "Banner")  # style hook

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("1200 × 600", self)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("BannerText")
        lyt.addWidget(lbl)


class Chip(QFrame):
    """A tiny pill chip with an icon + label."""

    def __init__(self, icon: Name, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Chip")
        self.setProperty("tag", "Chip")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(10, 4, 10, 4)
        lyt.setSpacing(8)

        icn = AppIcon(icon)
        # slightly smaller icon for chips
        icn.setFixedSize(QSize(18, 18))

        lbl = QLabel(text)
        lbl.setObjectName("ChipText")

        lyt.addWidget(icn)
        lyt.addWidget(lbl)


def _kv_row(icon: Name, title: str, value: str) -> QWidget:
    """Meta metric (icon + small title + value)."""
    w = QWidget()
    w.setObjectName("MetaCell")
    col = QVBoxLayout(w)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(4)

    icn = AppIcon(icon)
    icn.setFixedSize(QSize(22, 22))
    icn.setObjectName("MetaIcon")

    t = QLabel(title)
    t.setObjectName("MetaTitle")
    t.setProperty("typo", "label")

    v = QLabel(value)
    v.setObjectName("MetaValue")
    v.setProperty("typo", "value")

    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    row.addWidget(icn)
    row.addWidget(t)
    row.addStretch(1)

    col.addLayout(row)
    col.addWidget(v)
    return w


# ── FullRecipe View ─────────────────────────────────────────────────────────────────────────
class FullRecipe(QWidget):
    """Full recipe detail view (visual-only, no editing/upload yet)."""

    back_clicked = Signal()

    def __init__(self, recipe: Recipe, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.recipe = recipe

        # Register this view for component-scoped QSS.
        Theme.register_widget(self, Qss.FULL_RECIPE)

        self.setObjectName("FullRecipe")
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────────────────────
    def _make_back_button(self):
        """Create a simple back button; styled via QSS."""
        from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget

        w = QWidget(self)
        w.setObjectName("BackBar")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        btn = QPushButton("Back")
        btn.setObjectName("BackButton")
        btn.clicked.connect(self.back_clicked.emit)

        row.addWidget(btn, 0, Qt.AlignLeft)
        row.addStretch(1)
        return w

    def _build_ui(self) -> None:
    # Root layout holds a single scroll area (avoid multiple nested scrolls)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setObjectName("FullRecipeScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(scroll)

        # Scroll content
        content = QWidget()
        content.setObjectName("FullRecipeContent")
        scroll.setWidget(content)

        page = QVBoxLayout(content)
        page.setContentsMargins(24, 24, 24, 24)
        page.setSpacing(24)

        # Back bar
        page.addWidget(self._make_back_button())

        # ── Title Card
        card_title = Card(content)
        card_title.setObjectName("CardTitle")
        card_title.expandWidth(True)
        title_layout = card_title.getLayout()
        title_layout.setSpacing(12)

        title = QLabel(self.recipe.recipe_name or "Untitled Recipe")
        title.setObjectName("RecipeTitle")
        title.setAlignment(Qt.AlignHCenter)
        title.setProperty("typo", "display")
        title_layout.addWidget(title)

        chips_row = QHBoxLayout()
        chips_row.setContentsMargins(0, 0, 0, 0)
        chips_row.setSpacing(8)
        chips_row.setAlignment(Qt.AlignHCenter)
        chips_row.addWidget(Chip(Name.MEAL_TYPE, self.recipe.meal_type or "Dinner"))
        chips_row.addWidget(Chip(Name.CATEGORY, self.recipe.recipe_category or "Beef"))
        chips_row.addWidget(Chip(Name.DIET_PREF, getattr(self.recipe, "diet_pref", None) or "High-Protein"))
        title_layout.addLayout(chips_row)
        page.addWidget(card_title)

        # ── Banner Card
        card_banner = Card(content)
        card_banner.setObjectName("CardBanner")
        card_banner.expandWidth(True)
        banner_layout = card_banner.getLayout()
        banner_layout.setContentsMargins(16, 16, 16, 16)
        banner_layout.addWidget(BannerPlaceholder(card_banner))
        page.addWidget(card_banner)

        # ── Meta Summary Card
        card_meta = Card(content)
        card_meta.setObjectName("CardMeta")
        card_meta.expandWidth(True)

        grid = QGridLayout()
        grid.setContentsMargins(16, 10, 16, 10)
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        total_time = str(getattr(self.recipe, "total_time", "")) or "—"
        servings   = str(getattr(self.recipe, "servings", "")) or "—"
        category   = getattr(self.recipe, "recipe_category", "") or "—"
        diet       = getattr(self.recipe, "diet_pref", "") or "—"

        cells = [
            _kv_row(Name.TOTAL_TIME, "Total Time", total_time),
            _kv_row(Name.SERVINGS, "Servings", servings),
            _kv_row(Name.CATEGORY, "Category", category),
            _kv_row(Name.DIET_PREF, "Dietary", diet),
        ]
        for i, cell in enumerate(cells):
            grid.addWidget(cell, 0, i)

        card_meta.addWidget(QWidget())
        card_meta.getLayout().addLayout(grid)
        page.addWidget(card_meta)

        # ── Content Row: Ingredients + Directions
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(24)

        card_ingredients = Card(content)
        card_ingredients.setObjectName("CardIngredients")
        col_ing = card_ingredients.getLayout()
        col_ing.setSpacing(12)
        ing_title = QLabel("Ingredients")
        ing_title.setObjectName("SectionTitle")
        col_ing.addWidget(ing_title)
        col_ing.addLayout(self._build_ingredient_grid())
        row.addWidget(card_ingredients, 1)

        card_directions = Card(content)
        card_directions.setObjectName("CardDirections")
        col_dir = card_directions.getLayout()
        col_dir.setSpacing(12)
        dir_title = QLabel("Directions")
        dir_title.setObjectName("SectionTitle")
        col_dir.addWidget(dir_title)
        col_dir.addLayout(self._build_directions_block())
        row.addWidget(card_directions, 1)

        page.addLayout(row)

        # ── Notes (optional)
        notes = getattr(self.recipe, "notes", None)
        if notes:
            card_notes = Card(content)
            card_notes.setObjectName("CardNotes")
            col_notes = card_notes.getLayout()
            col_notes.setSpacing(12)
            notes_title = QLabel("Notes")
            notes_title.setObjectName("SectionTitle")
            col_notes.addWidget(notes_title)
            lbl = QLabel(notes)
            lbl.setWordWrap(True)
            lbl.setObjectName("NotesText")
            col_notes.addWidget(lbl)
            page.addWidget(card_notes)

        # bottom spacer so last card clears shadow
        page.addItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))


    # ── Builders ─────────────────────────────────────────────────────────────────────────────
    def _build_ingredient_grid(self) -> QGridLayout:
        """Two-column grid (qty/unit | ingredient name)."""
        grid = QGridLayout()
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)

        # header row (styled via QSS)
        h1 = QLabel(" ")
        h2 = QLabel(" ")
        h1.setObjectName("IngredientsLeftHeader")
        h2.setObjectName("IngredientsRightHeader")
        grid.addWidget(h1, 0, 0)
        grid.addWidget(h2, 0, 1)

        # rows
        row = 1
        details: Iterable = getattr(self.recipe, "get_ingredient_details", lambda: [])()
        for d in details:
            qty = f"{getattr(d, 'quantity', '') or ''}"
            unit = f"{getattr(d, 'unit', '') or ''}"
            left = " ".join(x for x in [qty, unit] if x).strip()
            right = getattr(d, "ingredient_name", "") or ""

            l_lbl = QLabel(left)
            r_lbl = QLabel(right)
            l_lbl.setObjectName("IngredientQty")
            r_lbl.setObjectName("IngredientName")

            grid.addWidget(l_lbl, row, 0, Qt.AlignLeft)
            grid.addWidget(r_lbl, row, 1, Qt.AlignLeft)
            row += 1

        return grid

    def _build_directions_block(self) -> QVBoxLayout:
        """Numbered step list."""
        col = QVBoxLayout()
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(10)

        raw = getattr(self.recipe, "directions", "") or ""
        steps = [s.strip() for s in raw.splitlines() if s.strip()]

        if not steps:
            empty = QLabel("No directions available.")
            empty.setWordWrap(True)
            empty.setObjectName("EmptyDirections")
            col.addWidget(empty)
            return col

        for i, step in enumerate(steps, start=1):
            line = QWidget()
            line.setObjectName("DirectionLine")
            h = QHBoxLayout(line)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(12)

            num = QLabel(f"{i}.")
            num.setObjectName("DirectionNumber")

            txt = QLabel(step)
            txt.setWordWrap(True)
            txt.setObjectName("DirectionText")

            h.addWidget(num, 0, Qt.AlignTop)
            h.addWidget(txt, 1)

            col.addWidget(line)

        return col
