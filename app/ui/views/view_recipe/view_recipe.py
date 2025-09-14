"""app/ui/views/view_recipe.py

ViewRecipe view redesigned to match mock UI with:
- Title + recipe tags
- Banner image placeholder (fixed 2:1 aspect ratio)
- Horizontal info cards (time, servings, category, dietary)
- Single column layout with ingredients, directions, and notes
- Modern styling using material injection variables

Styling:
- Registers for component-specific QSS with Theme.register_widget(self, Qss.FULL_RECIPE)
- Uses material injection variables for consistent theming
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from _dev_tools.debug_logger import DebugLogger
from app.core.models import Recipe
from app.core.utils import sanitize_form_input
from app.style import Name, Type
from app.style.icon import AppIcon, Icon
from app.ui.components.composite.recipe_info_widget import RecipeInfoWidget
from app.ui.components.widgets.image import RecipeBanner
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.components.widgets.tag import Tag
from app.ui.utils import create_two_column_layout, setup_main_scroll_layout
from ._directions_list import DirectionsList
from ._ingredients_list import IngredientList


class ViewRecipe(QWidget):
    """Full recipe detail view (visual-only, no editing/upload yet)."""

    back_clicked = Signal()

    def __init__(self, recipe: Recipe, navigation_service=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.recipe = recipe
        self.navigation_service = navigation_service

        self.setObjectName("ViewRecipe")
        self._cached_recipe_data = None
        self._build_ui()

    @property
    def recipe_data(self) -> dict:
        """Cache frequently accessed recipe attributes."""
        if self._cached_recipe_data is None:
            self._cached_recipe_data = self._extract_recipe_display_data()
        return self._cached_recipe_data

    def _extract_recipe_display_data(self) -> dict:
        """Extract and format recipe data with consistent fallbacks and sanitization."""
        return {
            "title": sanitize_form_input(getattr(self.recipe, "recipe_name", "")) or "Untitled Recipe",
            "recipe_name": sanitize_form_input(getattr(self.recipe, "recipe_name", "")),
            "meal_type": getattr(self.recipe, "meal_type", None) or "Dinner",
            "category": getattr(self.recipe, "recipe_category", None) or "Main Course",
            "diet_pref": getattr(self.recipe, "diet_pref", None) or "High-Protein",
            "total_time": str(getattr(self.recipe, "total_time", "")) or "2 hours 30 mins",
            "servings": str(getattr(self.recipe, "servings", "")) or "6",
            "directions": getattr(self.recipe, "directions", "") or "",
            "notes": getattr(self.recipe, "notes", None),
            "banner_image_path": getattr(self.recipe, "banner_image_path", None),
            "recipe_id": getattr(self.recipe, "id", None),
            "ingredient_details": getattr(self.recipe, "get_ingredient_details", lambda: [])()
        }

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
        btn.clicked.connect(self._handle_back_clicked)

        row.addWidget(btn, 0, Qt.AlignLeft)
        row.addStretch(1)
        return w

    def _build_ui(self) -> None:
        """Build the main UI matching the mock design."""

        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

        self._create_header_section()
        self._create_banner_section()
        self._create_info_section()
        self._create_content_sections()

        # Bottom spacer
        self.scroll_layout.addStretch()

    def _create_header_section(self) -> None:
        """Create back button, title, and tags section."""
        # Back Button
        # TODO: Implement sticky back button that remains visible during scrolling
        # Requirements: Fixed position overlay, semi-transparent background, proper z-index
        back_bar = self._make_back_button()
        self.scroll_layout.addWidget(back_bar)

        # Title Section
        title = QLabel(self.recipe_data["title"])
        title.setObjectName("RecipeTitle")
        title.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(title)

        # Recipe Tags Row
        tags_container = QWidget()
        tags_container.setObjectName("RecipeTagsContainer")
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.addStretch()

        # Add recipe tags using centralized data
        tags_layout.addWidget(Tag(Icon.MEAL_TYPE, self.recipe_data["meal_type"]))
        tags_layout.addSpacing(20)
        tags_layout.addWidget(Tag(Icon.CATEGORY, self.recipe_data["category"]))
        tags_layout.addSpacing(20)
        tags_layout.addWidget(Tag(Icon.DIET_PREF, self.recipe_data["diet_pref"]))
        tags_layout.addStretch()
        self.scroll_layout.addWidget(tags_container)

    def _create_banner_section(self) -> None:
        """Create and configure recipe banner with image handling."""
        self.recipe_banner = RecipeBanner()

        # Configure banner with recipe data
        if self.recipe_data["recipe_name"]:
            self.recipe_banner.set_recipe_name(self.recipe_data["recipe_name"])

        # Show existing banner image if recipe has one
        if self.recipe_data["banner_image_path"]:
            if Path(self.recipe_data["banner_image_path"]).exists():
                self.recipe_banner.set_banner_image_path(self.recipe_data["banner_image_path"])
                DebugLogger().log(f"Loaded recipe banner: {self.recipe_data['banner_image_path']}", "info")
            else:
                DebugLogger().log(f"Recipe banner path does not exist: {self.recipe_data['banner_image_path']}", "warning")

        # Connect AI service signals for async operations
        # TODO: enable after aI gen service is fixed
        #self.ai_service.generation_finished.connect(self._on_generation_finished)
        #self.ai_service.generation_failed.connect(self._on_generation_failed)

        self.scroll_layout.addWidget(self.recipe_banner)

    def _create_info_section(self) -> None:
        """Create recipe info cards section."""
        # Info Cards Container
        info_container = Card(content_layout="hbox")
        info_container.setObjectName("InfoContainer")
        info_container.setProperty("tag", "Container")
        info_container.expandWidth(True)
        info_container.setContentsMargins(20, 10, 20, 10)
        info_container.setSpacing(40)

        # Create info card using centralized recipe data
        info_card = RecipeInfoWidget(
            show_cards=["time", "servings", "category", "dietary"])
        info_card.setRecipe(self.recipe)
        info_container.addWidget(info_card)

        self.scroll_layout.addWidget(info_container)

    def _create_content_sections(self) -> None:
        """Create ingredients, directions, and notes sections using two-column layout."""
        # Left Column: Ingredients
        ingredients_list = IngredientList()
        ingredients_list.setIngredients(self.recipe_data["ingredient_details"])
        ingredients_card = self._create_recipe_section_card("Ingredients", Icon.INGREDIENTS, ingredients_list)

        # Right Column: Directions + Notes
        directions_list = DirectionsList()
        directions_list.setDirections(self.recipe_data["directions"])
        directions_card = self._create_recipe_section_card("Directions", Icon.DIRECTIONS, directions_list)

        right_column_widgets = [directions_card]

        # Add notes if present
        if self.recipe_data["notes"]:
            notes_text = QLabel(sanitize_form_input(self.recipe_data["notes"]))
            notes_text.setObjectName("NotesText")
            notes_text.setWordWrap(True)
            notes_card = self._create_recipe_section_card("Notes", Icon.NOTES, notes_text)
            right_column_widgets.append(notes_card)

        # Create two-column layout using utility (1/3 left, 2/3 right)
        column_layout = create_two_column_layout(
            left_widgets  = [ingredients_card],
            right_widgets = right_column_widgets,
            left_ratio    = 1,
            right_ratio   = 2,
        )
        self.scroll_layout.addLayout(column_layout)


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

    def _create_recipe_section_card(self, title: str, icon: Icon, content_widget: QWidget = None) -> Card:
        """Create standardized recipe section card with consistent configuration."""
        card = Card(self.scroll_content, card_type="Primary")
        card.setHeader(title, icon)
        card.headerIcon.setSize(30, 30)
        card.headerIcon.setColor("primary")
        card.setContentMargins(25, 25, 25, 25)
        card.setSpacing(15)
        card.expandWidth(True)

        if content_widget:
            # Set standardized size policy for content widgets
            content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            card.addWidget(content_widget)

        return card

    def _on_image_clicked(self):
        """Handle image click for full preview."""
        # TODO: Show full-size image preview dialog
        DebugLogger().log("Recipe banner image clicked for full preview", "debug")

    def _handle_back_clicked(self):
        """Handle back button click by emitting signal."""
        # Emit signal for navigation service to handle
        self.back_clicked.emit()



