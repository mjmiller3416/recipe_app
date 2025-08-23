"""app/ui/components/recipe_card/builders/recipe_card.py

Defines the RecipeCard class for generating recipe card layouts (small, medium, large).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.style import Theme
from app.style.icon import AppIcon
from app.style.icon.config import Name, Type
from app.style.theme.config import Qss
from app.ui.components.layout import Separator
from app.ui.components.widgets import RoundedImage, ToolButton
from app.ui.helpers.ui_helpers import make_overlay

from ..constants import LAYOUT_SIZE, LayoutSize


# ── Class Definition ────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class RecipeCard:
    """Builds a fixed-size QFrame representing a recipe card.

    Attributes:
        size (LayoutSize): Target card size (small, medium, large).
        recipe (Recipe): Data model instance containing recipe information.
    """

    size:   LayoutSize
    recipe: Recipe

    def _toggle_favorite_with_icon_update(self, button, recipe_id: int) -> None:
        """Helper to toggle favorite status and update the button icon."""
        try:
            from app.ui.components.widgets.button import BaseButton

            service = RecipeService()
            print(f"\\n=== TOGGLING FAVORITE ===\\nRecipe ID: {recipe_id}\\nBefore toggle - Current recipe.is_favorite: {self.recipe.is_favorite}")
            
            updated_recipe = service.toggle_favorite(recipe_id)
            
            # CRITICAL: Update the card's recipe object with the new state
            self.recipe.is_favorite = updated_recipe.is_favorite
            
            print(f"After toggle - updated_recipe.is_favorite: {updated_recipe.is_favorite}")
            print(f"After toggle - self.recipe.is_favorite: {self.recipe.is_favorite}")
            
            BaseButton.swapIcon(button, updated_recipe.is_favorite, Name.FAV_FILLED, Name.FAV)
            print(f"Icon swapped to: {'FAV_FILLED' if updated_recipe.is_favorite else 'FAV'}\\n")

        except Exception as e:
            print(f"Error in _toggle_favorite_with_icon_update: {e}")
            pass

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        """Build and return a QFrame layout based on the specified card size.

        Returns:
            QFrame: The fully constructed recipe card widget.
        """
        # DEBUG: Track recipe state at card creation
        print(f"\n=== BUILDING CARD ===\nRecipe: {self.recipe.recipe_name}\nSize: {self.size}\nRecipe ID: {self.recipe.id}\nis_favorite: {self.recipe.is_favorite}\n")
        
        # ── Create Frame ──
        frame = QFrame()
        frame.setProperty("layout_size", self.size.value)
        frame.setAttribute(Qt.WA_StyledBackground, True)
        frame.setObjectName("RecipeCard")

        # ── Set Frame Properties ──
        match self.size:
            case LayoutSize.SMALL:  self._build_small(frame)
            case LayoutSize.MEDIUM: self._build_medium(frame)
            case LayoutSize.LARGE:  self._build_large(frame)
            case _:                 raise ValueError(f"Unsupported size: {self.size}")

        frame.setFixedSize(LAYOUT_SIZE[self.size.value]) # apply fixed geometry

        Theme.register_widget(frame, Qss.RECIPE_CARD) # register for component-specific styling


        return frame

    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _build_small(self, parent: QFrame):
        """Construct the small layout for the recipe card.

        Args:
            parent (QFrame): The parent frame where the small layout will be added.
        """
        # ── Layout ──
        lyt = QHBoxLayout(parent)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(0)

        # recipe image
        img_recipe = RoundedImage(
            image_path=(self.recipe.image_path),
            size=100,
            radii=(10, 0, 0, 10)
        )
        lyt.addWidget(img_recipe) # add to layout

        # recipe name
        lbl_name = QLabel(self.recipe.recipe_name)
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_name) # add to layout

    def _build_medium(self, parent: QFrame):
        """Construct the medium layout for the recipe card.

        Args:
            parent (QFrame): The parent frame where the medium layout will be added.
        """
        # ── Layout ──
        lyt = QVBoxLayout(parent)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(0)

        # recipe image
        img_recipe = RoundedImage(
            image_path=self.recipe.image_path,
            size=280,
            radii=(10, 10, 0, 0)
        )

        # favorite button - choose initial icon based on favorite state
        print(f"[MEDIUM CARD] Recipe '{self.recipe.recipe_name}' - is_favorite: {self.recipe.is_favorite}")
        initial_icon = Name.FAV_FILLED if self.recipe.is_favorite else Name.FAV
        print(f"[MEDIUM CARD] Selected icon: {initial_icon}")
        btn_fav = ToolButton(Type.DEFAULT, initial_icon)
        btn_fav.setIconSize(24, 24)
        btn_fav.setObjectName("btn_favorite")
        btn_fav.setCheckable(True)
        btn_fav.setCursor(Qt.PointingHandCursor)
        btn_fav.setChecked(bool(self.recipe.is_favorite)) # set initial state
        btn_fav.toggled.connect(
            lambda checked, rid=self.recipe.id: self._toggle_favorite_with_icon_update(btn_fav, rid)
        )

        # create overlay
        overlay = make_overlay(img_recipe, btn_fav)
        lyt.addWidget(overlay) # add to layout

        # recipe name
        lbl_name = QLabel(self.recipe.recipe_name)
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_name) # add to layout

        # ── MetaData Section ──
        lyt_meta = QHBoxLayout()
        lyt_meta.setContentsMargins(0, 0, 0, 8)
        lyt_meta.setSpacing(0)

        # add servings
        lyt_meta.addLayout(
            self._create_meta_section(
                AppIcon(Name.SERVINGS),
                heading="Servings",
                value=self.recipe.formatted_servings(),
            )
        )

        # separator
        lyt_meta.addWidget(Separator.vertical(70), 0, Qt.AlignVCenter)

        # add total time
        lyt_meta.addLayout(
            self._create_meta_section(
                AppIcon(Name.TOTAL_TIME),
                heading="Time",
                value=self.recipe.formatted_time(),
            )
        )

        # ── add meta to layout ──
        lyt.addLayout(lyt_meta)

    def _build_large(self, parent: QFrame):
        """Construct the large layout for the recipe card.

        Args:
            parent (QFrame): The parent frame where the large layout will be added.
        """
        from app.ui.components.composite.ingredients_preview import \
            IngredientsPreview
        from app.ui.components.composite.recipe_info_cards import \
            RecipeInfoCards
        from app.ui.components.composite.recipe_tags_row import RecipeTagsRow

        # Main layout
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(12, 12, 12, 12)  # Reduced margins from 15 to 12
        main_layout.setSpacing(10)  # Reduced spacing from 12 to 10

        # ── Recipe Title ──
        title_label = QLabel(self.recipe.recipe_name or "Untitled Recipe")
        title_label.setObjectName("LargeCardTitle")
        title_label.setProperty("title_text", "true")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        main_layout.addWidget(title_label)

        # ── Content Layout: Image (left) + Info Panel (right) ──
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)  # Reduced spacing from 15 to 12

        # ── Left Side: Recipe Image ──
        img_recipe = RoundedImage(
            image_path=self.recipe.image_path,
            size=200,  # Reduced from 280 to 200 to give more space to info panel
            radii=(10, 10, 10, 10)
        )

        # Favorite button overlay
        print(f"[LARGE CARD] Recipe '{self.recipe.recipe_name}' - is_favorite: {self.recipe.is_favorite}")
        initial_icon = Name.FAV_FILLED if self.recipe.is_favorite else Name.FAV
        print(f"[LARGE CARD] Selected icon: {initial_icon}")
        btn_fav = ToolButton(Type.DEFAULT, initial_icon)
        btn_fav.setIconSize(24, 24)
        btn_fav.setObjectName("btn_favorite")
        btn_fav.setCheckable(True)
        btn_fav.setCursor(Qt.PointingHandCursor)
        btn_fav.setChecked(bool(self.recipe.is_favorite))
        btn_fav.toggled.connect(
            lambda checked, rid=self.recipe.id: self._toggle_favorite_with_icon_update(btn_fav, rid)
        )

        # Create image with overlay
        image_overlay = make_overlay(img_recipe, btn_fav)
        content_layout.addWidget(image_overlay, 0)  # Fixed size for image

        # ── Right Side: Info Panel ──
        info_panel = QVBoxLayout()
        info_panel.setSpacing(8)  # Reduced spacing to fit more content

        # Recipe Tags Row
        tags_row = RecipeTagsRow()
        tags_row.setRecipe(self.recipe)
        tags_row.setAlignment("left")  # Left-align for the large card
        info_panel.addWidget(tags_row)

        # Info Cards Row (compact mode for large card)
        info_cards = RecipeInfoCards(show_cards=["time", "servings"])
        info_cards.setRecipe(self.recipe)
        info_cards.setCompactMode(True)
        info_panel.addWidget(info_cards)

        # Add some spacing
        info_panel.addSpacing(6)

        # Ingredients Preview
        ingredients_preview = IngredientsPreview(max_preview_items=5)  # Reduced from 6 to 5
        ingredient_details = getattr(self.recipe, "get_ingredient_details", lambda: [])()
        ingredients_preview.setIngredients(ingredient_details)
        info_panel.addWidget(ingredients_preview)

        # Add stretch to push content to top
        info_panel.addStretch()

        # Add info panel to content layout with more space
        content_layout.addLayout(info_panel, 2)  # Give it 2x more space than the image

        # Add content to main layout
        main_layout.addLayout(content_layout)

        # ── Bottom Info Section ──
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        # Recipe metadata using existing meta section helper
        bottom_layout.addLayout(
            self._create_meta_section(
                AppIcon(Name.SERVINGS),
                heading="Servings",
                value=self.recipe.formatted_servings(),
            )
        )

        # Separator
        bottom_layout.addWidget(Separator.vertical(50), 0, Qt.AlignVCenter)

        # Total time
        bottom_layout.addLayout(
            self._create_meta_section(
                AppIcon(Name.TOTAL_TIME),
                heading="Time",
                value=self.recipe.formatted_time(),
            )
        )

        # Add stretch to center the bottom info
        bottom_layout.insertStretch(0)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def _create_meta_section(self, icon_widget: AppIcon, heading: str, value: str) -> QVBoxLayout:
        """Create a vertical layout section for displaying metadata with an icon, heading, and value.

        Args:
            icon_widget (AppIcon): The AppIcon widget to display.
            heading (str): Label heading (e.g., "Servings", "Time").
            value (str): Value associated with the heading (e.g., "4", "30 min").

        Returns:
            QVBoxLayout: Layout containing the icon, heading, and value widgets.
        """
        # ── Create Layout ──
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(2)

        # icon - use the provided icon widget directly
        icon_widget.setAlignment(Qt.AlignCenter)
        lyt.addWidget(icon_widget, 0, Qt.AlignCenter) # add to layout

        # heading
        lbl_heading = QLabel(heading)
        lbl_heading.setProperty("label_text", True)
        lbl_heading.setAlignment(Qt.AlignCenter)
        lbl_heading.setContentsMargins(0, 4, 0, 0) # remove margins
        lyt.addWidget(lbl_heading) # add to layout

        # value
        lbl_value = QLabel(value)
        lbl_value.setProperty("value_text", True)
        lbl_value.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_value) # add to layout

        return lyt
