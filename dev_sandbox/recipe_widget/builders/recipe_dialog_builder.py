# recipe_widget/builders/recipe_dialog_builder.py
from __future__ import annotations

#🔸Standard Library
from dataclasses import dataclass

#🔸Third-party 
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QSplitter,
                               QTextEdit, QVBoxLayout)

from core.application.config import icon_path
from core.modules.recipe_module import Recipe
from helpers.ui_helpers.rounded_image import create_rounded_image
from helpers.ui_helpers.svg_loader import svg_loader

#🔸Local Imports
from ..constants import ICON_COLOR

# ────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class RecipeDialogBuilder:
    """
    Builds a **modal QDialog** that shows the *full* recipe details.

    Parameters
    ----------
    recipe : Recipe
        Recipe model instance to render.
    """

    recipe: Recipe

    # ── public ──────────────────────────────────────────────────────────────────────
    def build(self, parent=None) -> QDialog:
        dlg = QDialog(parent)
        dlg.setObjectName("RecipeDialog")
        dlg.setWindowTitle(self.recipe.name)
        dlg.resize(800, 1000)
        dlg.setModal(True)

        root = QVBoxLayout(dlg)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # header
        header = QHBoxLayout()
        header.setSpacing(16)
        root.addLayout(header)

        # 1:1 image (optional)
        if self.recipe.image_path:
            img_lbl = create_rounded_image(
                image_path=self.recipe.image_path,
                dimension=180,
                radii=(12, 12, 12, 12),
            )
            header.addWidget(img_lbl, 0, Qt.AlignTop)

        # title & meta
        title_meta = QVBoxLayout()
        header.addLayout(title_meta, 1)

        lbl_title = QLabel(self.recipe.name)
        lbl_title.setProperty("title_text", True)
        lbl_title.setWordWrap(True)
        title_meta.addWidget(lbl_title)

        meta_row = self._build_meta_row()
        title_meta.addLayout(meta_row)

        # splitter
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        ing_frame = self._build_ingredients_frame()
        dir_frame = self._build_directions_frame()

        splitter.addWidget(ing_frame)
        splitter.addWidget(dir_frame)
        splitter.setSizes([250, 550])       # 1/3 vs 2/3 feel

        return dlg

    # ── private ─────────────────────────────────────────────────────────────────────
    def _build_meta_row(self) -> QHBoxLayout:
        lyt = QHBoxLayout()
        lyt.setSpacing(24)

        lyt.addLayout(
            self._make_meta_section(
                "servings",
                "Servings",
                self.recipe.formatted_servings(),
            )
        )
        lyt.addLayout(
            self._make_meta_section(
                "total_time",
                "Total Time",
                self.recipe.formatted_total_time(),
            )
        )
        if getattr(self.recipe, "category", None):
            lyt.addLayout(
                self._make_meta_section(
                    "category",
                    "Category",
                    self.recipe.category,
                )
            )
        lyt.addStretch(1)
        return lyt

    # --------------------------------------------------------------------------------
    def _make_meta_section(
        self,
        icon_name: str,
        heading:   str,
        value:     str,
    ) -> QVBoxLayout:
        lyt = QVBoxLayout()
        lyt.setSpacing(2)
        lyt.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(
            svg_loader(
                icon_path(icon_name),
                ICON_COLOR,
                QSize(28, 28),
                return_type=QPixmap,
                source_color="#000",
            )
        )
        lbl_icon.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_icon, 0, Qt.AlignLeft)

        lbl_heading = QLabel(heading)
        lbl_heading.setProperty("label_text", True)
        lyt.addWidget(lbl_heading, 0, Qt.AlignLeft)

        lbl_value = QLabel(value)
        lbl_value.setProperty("value_text", True)
        lyt.addWidget(lbl_value, 0, Qt.AlignLeft)

        return lyt

    # --------------------------------------------------------------------------------
    def _build_ingredients_frame(self) -> QFrame:
        frame = QFrame()
        lay   = QVBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Ingredients")
        lbl.setProperty("section_heading", True)
        lay.addWidget(lbl, 0, Qt.AlignTop)

        ing_text = "\n".join(
            f"{ing['quantity']} {ing['unit']}  –  {ing['ingredient_name']}"
            for ing in self.recipe["ingredients"]
        )
        text = QTextEdit(ing_text)
        text.setReadOnly(True)
        text.setFrameShape(QFrame.NoFrame)
        lay.addWidget(text, 1)

        return frame

    # --------------------------------------------------------------------------------
    def _build_directions_frame(self) -> QFrame:
        frame = QFrame()
        lay   = QVBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Directions")
        lbl.setProperty("section_heading", True)
        lay.addWidget(lbl, 0, Qt.AlignTop)

        text = QTextEdit(self.recipe["directions"])
        text.setReadOnly(True)
        text.setFrameShape(QFrame.NoFrame)
        lay.addWidget(text, 1)

        return frame
