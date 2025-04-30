"""recipe_widget/builders/recipe_card_builder.py

Defines the RecipeCardBuilder class for generating recipe card layouts (small, medium, large).
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from core.helpers.debug_logger import DebugLogger
from database.modules.recipe_module import Recipe
from helpers.icon_helpers.widgets import Icon
from helpers.ui_helpers import RoundedImage, Separator

from ..constants import ICON_COLOR, LAYOUT_SIZE, LayoutSize

# ── Constants ───────────────────────────────────────────────────────────────────
ICON_SIZE = QSize(30, 30)

# ── Class Definition ────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class RecipeCardBuilder:
    """Builds a fixed-size QFrame representing a recipe card.

    Attributes:
        size (LayoutSize): Target card size (small, medium, large).
        recipe (Recipe): Data model instance containing recipe information.
    """

    size:   LayoutSize
    recipe: Recipe

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        """Build and return a QFrame layout based on the specified card size.

        Returns:
            QFrame: The fully constructed recipe card widget.
        """
        # ── Create Frame ──
        frame = QFrame()
        frame.setProperty("layout_size", self.size.value)

        # ── Set Frame Properties ──
        match self.size:
            case LayoutSize.SMALL:  self._build_small(frame)
            case LayoutSize.MEDIUM: self._build_medium(frame)
            case LayoutSize.LARGE:  self._build_large(frame)
            case _:                 raise ValueError(f"Unsupported size: {self.size}")

        frame.setFixedSize(LAYOUT_SIZE[self.size.value]) # apply fixed geometry

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
        lbl_image = RoundedImage(
            image_path=(self.recipe.image_path),
            size=100,
            radii=(10, 0, 0, 10)
        )
        lyt.addWidget(lbl_image) # add to layout

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
            image_path=(self.recipe.image_path),
            size=280,
            radii=(10, 10, 0, 0)
        )
        lyt.addWidget(img_recipe) # add to layout

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
                icon_name="servings.svg",
                heading="Servings",
                value=self.recipe.formatted_servings(),
            )
        )

        # separator
        lyt_meta.addWidget(Separator.vertical(70), 0, Qt.AlignVCenter)

        # add total time
        lyt_meta.addLayout(
            self._create_meta_section(
                icon_name="total_time.svg",
                heading="Time",
                value=self.recipe.formatted_total_time(),
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

    def _create_meta_section(self, *, icon_name: str, heading: str, value: str) -> QVBoxLayout:
        """Create a vertical layout section for displaying metadata with an icon, heading, and value.

        Args:
            icon_name (str): Filename of the icon to display (e.g., "servings.svg").
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
        ico_meta = Icon(
            name=icon_name,
            size=ICON_SIZE,
            color=ICON_COLOR,
            source="#000",
        )
        ico_meta.setContentsMargins(0, 0, 0, 4)
        lyt.addWidget(ico_meta) # add to layout

        # heading
        lbl_heading = QLabel(heading)
        lbl_heading.setProperty("label_text", True)
        lbl_heading.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_heading) # add to layout

        # value
        lbl_value = QLabel(value)
        lbl_value.setProperty("value_text", True)
        lbl_value.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_value) # add to layout

        return lyt
