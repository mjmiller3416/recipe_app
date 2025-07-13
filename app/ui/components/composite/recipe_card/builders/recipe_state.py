"""app/ui/components/recipe_card/builders/recipe_card.py

Defines the RecipeCard class for generating recipe card layouts (small, medium, large).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.config.app_icon import AppIcon, ICON_SPECS
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.components.layout import Separator
from app.ui.components.widgets import CTIcon, CTToolButton, RoundedImage
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
            service = RecipeService()
            updated_recipe = service.toggle_favorite(recipe_id)

            # update the button icon based on the new favorite state
            from app.config.app_icon import ICON_SPECS
            from app.style_manager.icons.factory import IconFactory

            new_icon = AppIcon.FAVORITE if updated_recipe.is_favorite else AppIcon.UNFAVORITE
            spec = ICON_SPECS[new_icon]

            # create new themed icon and apply it
            icon_factory = IconFactory(spec.path, spec.size, spec.variant)
            button.setIcon(icon_factory.icon())

        except Exception:
            pass

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        """Build and return a QFrame layout based on the specified card size.

        Returns:
            QFrame: The fully constructed recipe card widget.
        """
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

        # ⚠️ temporary fix for transparency
        frame.setStyleSheet("background-color: #1B1D23; border-radius: 10px;")

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
        initial_icon = AppIcon.FAVORITE if self.recipe.is_favorite else AppIcon.UNFAVORITE
        btn_fav = CTToolButton(
            initial_icon,
            checkable = True,
        )
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
                AppIcon.SERVINGS,
                heading="Servings",
                value=self.recipe.formatted_servings(),
            )
        )

        # separator
        lyt_meta.addWidget(Separator.vertical(70), 0, Qt.AlignVCenter)

        # add total time
        lyt_meta.addLayout(
            self._create_meta_section(
                AppIcon.TOTAL_TIME,
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

        Raises:
            NotImplementedError: Always raised since large layout is not yet implemented.
        """
        raise NotImplementedError("Large frame layout is not yet implemented.")

    def _create_meta_section(self, icon_enum: AppIcon, heading: str, value: str) -> QVBoxLayout:
        """Create a vertical layout section for displaying metadata with an icon, heading, and value.

        Args:
            file_path (path): File path of the icon to display (e.g., "servings.svg").
            heading (str): Label heading (e.g., "Servings", "Time").
            value (str): Value associated with the heading (e.g., "4", "30 min").

        Returns:
            QVBoxLayout: Layout containing the icon, heading, and value widgets.
        """
        # ── Create Layout ──
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(2)

        # icon
        # use centralized icon specs from AppIcon enum
        spec = ICON_SPECS[icon_enum]
        ico_meta = CTIcon(
            icon_or_path=spec.path,
            icon_size=spec.size,
            variant=spec.variant,
        )
        ico_meta.setAlignment(Qt.AlignCenter)
        lyt.addWidget(ico_meta, 0, Qt.AlignCenter) # add to layout

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
