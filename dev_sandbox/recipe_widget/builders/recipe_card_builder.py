# recipe_widget/builders/recipe_card_builder.py
from __future__ import annotations

#🔸Standard Library
from dataclasses import dataclass

#🔸Third-party
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from core.helpers.debug_logger import DebugLogger
from core.modules.recipe_module import Recipe
from helpers.icons.widgets import IconLabel
from helpers.ui_helpers import Separator, create_rounded_image

#🔸Local Imports
from ..constants import ICON_COLOR, LAYOUT_SIZE, LayoutSize

#🔸Constants
ICON_SIZE = QSize(30, 30)
# ────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class RecipeCardBuilder:
    """
    Builds a *fixed-size* QFrame for a recipe card in one of three layouts
    (SMALL, MEDIUM, LARGE).

    Parameters
    ----------
    size   : LayoutSize
        Target card size.
    recipe : Recipe
        Data model instance to render.
    """
    size:   LayoutSize
    recipe: Recipe

    # ── public ──────────────────────────────────────────────────────────────────────
    def build(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("layout_size", self.size.value) # for CSS styling

        match self.size:
            case LayoutSize.SMALL:  self._build_small(frame)
            case LayoutSize.MEDIUM: self._build_medium(frame)
            case LayoutSize.LARGE:  self._build_large(frame)
            case _:                 raise ValueError(f"Unsupported size: {self.size}")

        # apply fixed geometry
        frame.setFixedSize(LAYOUT_SIZE[self.size.value])
        return frame

    # ── private ─────────────────────────────────────────────────────────────────────
    def _build_small(self, parent: QFrame):
        """
        Build the small layout for the recipe card.

        This layout includes the recipe image and name.

        args:
            parent (QFrame): The parent frame to which the layout will be added.
            recipe (Recipe): The recipe object containing the data to display.
        """
        # ── main layout ──
        lyt_main = QHBoxLayout(parent)
        lyt_main.setContentsMargins(0, 0, 0, 0)
        lyt_main.setSpacing(0)

        # recipe image
        lbl_image = create_rounded_image(
            image_path=(self.recipe.image_path),
            dimension=100,
            radii=(10, 0, 0, 10)
        )
        lyt_main.addWidget(lbl_image)

        # recipe name
        lbl_name = QLabel(self.recipe.name) 
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        lyt_main.addWidget(lbl_name)

    # --------------------------------------------------------------------------------
    def _build_medium(self, parent: QFrame):
        """
        Build the medium layout for the recipe card.

        This layout includes the recipe image, name, servings, and time.

        Args:   
            parent (QFrame): The parent frame to which the layout will be added.
            recipe (Recipe): The recipe object containing the data to display.
        """
        # ── main layout ──
        lyt_main = QVBoxLayout(parent)
        lyt_main.setContentsMargins(0, 0, 0, 0)
        lyt_main.setSpacing(0)

        # recipe image
        lbl_image = create_rounded_image(
            image_path=(self.recipe.image_path), 
            dimension=280,
            radii=(10, 10, 0, 0)
        )
        lyt_main.addWidget(lbl_image)  
        
        # recipe name
        lbl_name = QLabel(self.recipe.name) 
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        lyt_main.addWidget(lbl_name)

        # ── meta-data row ──
        lyt_meta = QHBoxLayout()
        lyt_meta.setContentsMargins(0, 0, 0, 8)
        lyt_meta.setSpacing(0)

        lyt_meta.addLayout(
            self._create_meta_section(
                icon_name="servings.svg",
                heading="Servings",
                value=self.recipe.formatted_servings(),
            )
        )

        lyt_meta.addWidget(Separator(), 0, Qt.AlignVCenter)

        lyt_meta.addLayout(
            self._create_meta_section(
                icon_name="total_time.svg",
                heading="Time",
                value=self.recipe.formatted_total_time(),
            )
        )

        lyt_main.addLayout(lyt_meta)

    # --------------------------------------------------------------------------------
    def _build_large(self, parent: QFrame):
        """
        Build the large layout for the recipe card.

        This layout includes the recipe image, name, servings, and time.

        Args:
            parent (QFrame): The parent frame to which the layout will be added.
            recipe (Recipe): The recipe object containing the data to display.
        """
        raise NotImplementedError("Large frame layout is not yet implemented.")
    
    # --------------------------------------------------------------------------------
    def _create_meta_section(
        self, *, icon_name: str, heading: str, value: str
    ) -> QVBoxLayout:
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(2)

        # icon
        lbl_icon = IconLabel(
            name=icon_name,
            size=ICON_SIZE,
            color=ICON_COLOR,
            source="#000",
        )

        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setContentsMargins(0, 0, 0, 4)

        # heading
        lbl_heading = QLabel(heading)
        lbl_heading.setProperty("label_text", True)
        lbl_heading.setAlignment(Qt.AlignCenter)

        # value
        lbl_value = QLabel(value)
        lbl_value.setProperty("value_text", True)
        lbl_value.setAlignment(Qt.AlignCenter)

        lyt.addWidget(lbl_icon)
        lyt.addWidget(lbl_heading)
        lyt.addWidget(lbl_value)
        return lyt
