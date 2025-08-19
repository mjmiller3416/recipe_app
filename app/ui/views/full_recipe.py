"""app/ui/views/full_recipe.py

FullRecipe view redesigned to match mock UI with:
- Title + recipe tags
- Banner image placeholder (fixed 2:1 aspect ratio)
- Horizontal info cards (time, servings, category, dietary)
- Single column layout with ingredients, directions, and notes
- Modern styling using material injection variables

Styling:
- Registers for component-specific QSS with Theme.register_widget(self, Qss.FULL_RECIPE)
- Uses material injection variables for consistent theming
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
from app.style.icon import Icon, AppIcon
from app.style.icon.config import Name, Type

# Theme hook (component registration)
from app.style import Theme, Qss

# Card container
from app.ui.components.layout.card import Card

# Custom components
from app.ui.components.widgets.button import Button
from app.ui.components.widgets.recipe_tag import RecipeTag
from app.ui.components.widgets.info_card import InfoCard
from app.ui.components.images.recipe_image import RecipeImage

# Data model
from app.core.models import Recipe


# ── Helper Classes ──────────────────────────────────────────────────────────────────────────
class IngredientList(QWidget):
    """A list widget for displaying recipe ingredients with amounts and names."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    def setIngredients(self, ingredient_details: Iterable):
        """Set the ingredients to display."""
        # Clear existing ingredients
        self._clearIngredients()

        # Add new ingredients
        for detail in ingredient_details:
            self._addIngredientItem(detail)

    def _clearIngredients(self):
        """Clear all ingredient items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addIngredientItem(self, detail):
        """Add a single ingredient item to the list."""
        # Create ingredient row widget
        item_widget = QWidget()
        item_widget.setObjectName("IngredientItem")

        # Use QGridLayout for precise alignment
        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setHorizontalSpacing(10)
        item_layout.setVerticalSpacing(0)

        # Set column stretch: quantity (fixed), unit (fixed), name (expanding)
        item_layout.setColumnStretch(0, 0)  # Quantity column - fixed width
        item_layout.setColumnStretch(1, 0)  # Unit column - fixed width
        item_layout.setColumnStretch(2, 1)  # Name column - expanding

        # Get formatted ingredient details using new DTO properties
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""

        # Quantity label (right-aligned, fixed width)
        qty_label = QLabel(formatted_qty)
        qty_label.setObjectName("IngredientQuantity")
        qty_label.setMinimumWidth(60)
        qty_label.setMaximumWidth(60)
        qty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Unit label (left-aligned, fixed width)
        unit_label = QLabel(abbreviated_unit)
        unit_label.setObjectName("IngredientUnit")
        unit_label.setMinimumWidth(50)
        unit_label.setMaximumWidth(50)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Ingredient name label (left-aligned, expanding)
        name_label = QLabel(ingredient_name)
        name_label.setObjectName("IngredientName")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add to grid: row 0, columns 0, 1, 2
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)

        # Add to main layout
        self.layout.addWidget(item_widget)


class DirectionsList(QWidget):
    """A numbered list widget for displaying recipe directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DirectionsList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

    def setDirections(self, directions: str):
        """Set the directions to display."""
        # Clear existing directions
        self._clearDirections()

        # Parse directions
        steps = [s.strip() for s in directions.splitlines() if s.strip()] if directions else []

        if not steps:
            empty_label = QLabel("No directions available.")
            empty_label.setObjectName("EmptyDirections")
            empty_label.setWordWrap(True)
            self.layout.addWidget(empty_label)
        else:
            # Add numbered steps
            for i, step in enumerate(steps, start=1):
                self._addDirectionItem(i, step)

    def _clearDirections(self):
        """Clear all direction items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addDirectionItem(self, number: int, text: str):
        """Add a single direction item to the list."""
        # Create direction row widget
        item_widget = QWidget()
        item_widget.setObjectName("DirectionItem")

        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(12)

        # Number label
        number_label = QLabel(f"{number}.")
        number_label.setObjectName("DirectionNumber")
        number_label.setMinimumWidth(30)
        number_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Text label
        text_label = QLabel(text)
        text_label.setObjectName("DirectionText")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Add to layout
        item_layout.addWidget(number_label)
        item_layout.addWidget(text_label, 1)

        # Add to main layout
        self.layout.addWidget(item_widget)


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
        """Create a simple back button using custom Button class."""
        w = QWidget(self)
        w.setObjectName("BackBar")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        btn = Button("Back", Type.SECONDARY, Name.BACK)
        btn.setObjectName("BackButton")
        btn.clicked.connect(self.back_clicked.emit)

        row.addWidget(btn, 0, Qt.AlignLeft)
        row.addStretch(1)
        return w

    def _build_ui(self) -> None:
        """Build the main UI matching the mock design."""
        # Root layout holds a single scroll area
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
        content.setContentsMargins(100, 0, 100, 0)
        content.setObjectName("FullRecipeContent")
        scroll.setWidget(content)

        page = QVBoxLayout(content)
        page.setContentsMargins(30, 30, 30, 30)
        page.setSpacing(25)

        # ── Back Button
        # TODO: Implement sticky back button that remains visible during scrolling
        # Requirements: Fixed position overlay, semi-transparent background, proper z-index
        back_bar = self._make_back_button()
        page.addWidget(back_bar)

        # ── Title Section
        title = QLabel(self.recipe.recipe_name or "Untitled Recipe")
        title.setObjectName("RecipeTitle")
        title.setAlignment(Qt.AlignCenter)
        page.addWidget(title)

        # ── Recipe Tags Row
        tags_container = QWidget()
        tags_container.setObjectName("RecipeTagsContainer")
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.addStretch()

        # Add recipe tags with proper icons
        meal_type = getattr(self.recipe, "meal_type", None) or "Dinner"
        category = getattr(self.recipe, "recipe_category", None) or "Main Course"
        diet_pref = getattr(self.recipe, "diet_pref", None) or "High-Protein"

        tags_layout.addWidget(RecipeTag(Icon.MEAL_TYPE, meal_type))
        tags_layout.addSpacing(20)
        tags_layout.addWidget(RecipeTag(Icon.CATEGORY, category))
        tags_layout.addSpacing(20)
        tags_layout.addWidget(RecipeTag(Icon.DIET_PREF, diet_pref))
        tags_layout.addStretch()
        page.addWidget(tags_container)

        # ── Recipe Image
        recipe_image = RecipeImage()
        page.addWidget(recipe_image)

        # ── Info Cards Container
        # TODO: Update to new Card API pattern (info_container.addWidget) once card styling variants are implemented
        info_container = Card(content_layout="hbox")
        info_container.setObjectName("InfoContainer")
        info_container.setProperty("tag", "Container")
        info_container.expandWidth(True)
        info_container.setContentsMargins(20, 10, 20, 10)
        info_container.setSpacing(40)

        # Get recipe data with fallbacks
        total_time = str(getattr(self.recipe, "total_time", "")) or "2 hours 30 mins"
        servings = str(getattr(self.recipe, "servings", "")) or "6"
        category = getattr(self.recipe, "recipe_category", "") or "Main Course"
        diet_pref = getattr(self.recipe, "diet_pref", "") or "High-Protein"

        # Add info cards
        info_container.addWidget(InfoCard(Icon.TOTAL_TIME, "Total Time", total_time))
        info_container.addWidget(InfoCard(Icon.SERVINGS, "Servings", servings))
        info_container.addWidget(InfoCard(Icon.CATEGORY, "Category", category))
        info_container.addWidget(InfoCard(Icon.DIET_PREF, "Dietary", diet_pref))

        page.addWidget(info_container)

        # ── Content Layout: Left Column (Ingredients) + Right Column (Directions + Notes)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(30)

        # ── Left Column: Ingredients (1/3 width)
        ingredients_card = Card(content, card_type="Primary")
        ingredients_card.setHeader("Ingredients", Icon.INGREDIENTS)
        ingredients_card.headerIcon.setSize(30, 30)
        ingredients_card.headerIcon.setColor("primary")
        ingredients_card.setContentMargins(25, 25, 25, 25)
        ingredients_card.setSpacing(15)
        ingredients_card.expandWidth(True)  # Allow width expansion

        # Ingredients list
        ingredients_list = IngredientList()
        ingredients_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        ingredient_details = getattr(self.recipe, "get_ingredient_details", lambda: [])()
        ingredients_list.setIngredients(ingredient_details)
        ingredients_card.addWidget(ingredients_list)

        # Add ingredients to left column with stretch factor 1 and top alignment
        content_layout.addWidget(ingredients_card, 1, Qt.AlignTop)

        # ── Right Column: Directions + Notes (2/3 width)
        right_column_widget = QWidget()
        right_column_layout = QVBoxLayout(right_column_widget)
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(25)

        # ── Directions Section
        directions_card = Card(content, card_type="Primary")
        directions_card.setHeader("Directions", Icon.DIRECTIONS)
        directions_card.headerIcon.setSize(30, 30)
        directions_card.headerIcon.setColor("primary")
        directions_card.setContentMargins(25, 25, 25, 25)
        directions_card.setSpacing(15)
        directions_card.expandWidth(True)  # Allow width expansion

        # Directions list
        directions_list = DirectionsList()
        directions_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        recipe_directions = getattr(self.recipe, "directions", "") or ""
        directions_list.setDirections(recipe_directions)
        directions_card.addWidget(directions_list)

        # Add directions to right column
        right_column_layout.addWidget(directions_card)

        # TODO: Fix line spacing
        # ── Notes Section (optional)
        notes = getattr(self.recipe, "notes", None)
        if notes:
            notes_card = Card(content, card_type="Primary")
            notes_card.setHeader("Notes", Icon.NOTES)
            notes_card.headerIcon.setSize(30, 30)
            notes_card.headerIcon.setColor("primary")
            notes_card.setContentMargins(25, 25, 25, 25)
            notes_card.setSpacing(15)
            notes_card.expandWidth(True)  # Allow width expansion

            # Notes text
            notes_text = QLabel(notes)
            notes_text.setObjectName("NotesText")
            notes_text.setWordWrap(True)
            notes_card.addWidget(notes_text)

            # Add notes to right column
            right_column_layout.addWidget(notes_card)

        # Add right column widget to main content layout with stretch factor 2 and top alignment
        content_layout.addWidget(right_column_widget, 2, Qt.AlignTop)

        # Add the content layout to main page layout
        page.addLayout(content_layout)

        # Bottom spacer
        page.addStretch()

    def _create_section_header(self, icon: Icon, title: str) -> QWidget:
        """Create a section header with icon and title."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Icon
        header_icon = AppIcon(icon)
        header_icon.setFixedSize(QSize(24, 24))
        header_icon.setObjectName("SectionIcon")

        # Title
        header_title = QLabel(title)
        header_title.setObjectName("SectionHeader")

        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        return header_widget


