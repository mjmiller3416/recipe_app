# File: ui/dialogs/full_recipe_dialog.py (Example path)

# ── Imports ─────────────────────────────────────────────────────────────────────
import sys

from PySide6.QtWidgets import (QApplication, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.application.config import ICON_COLOR, ICON_SIZE
from core.modules.recipe_module import Recipe
from database import DB_INSTANCE
from helpers.icon_helpers import Icon
from helpers.app_helpers.base_dialog import BaseDialog
from helpers.ui_helpers import rounded_image

# ── Class Definition ────────────────────────────────────────────────────────────
class FullRecipe(BaseDialog):
    """
    A dialog to display a full recipe, mimicking the provided screenshot layout.
    Inherits from BaseDialog for custom window chrome.
    """
    def __init__(self, recipe: Recipe, parent=None):
        super().__init__(parent)
        self.recipe = Recipe(recipe)  # Ensure recipe is a Recipe object
        self._setup_ui()

    def _setup_ui(self):
        """Creates and arranges the widgets."""

        # ── Window Properties ──
        self.window().setWindowTitle(f"{self.recipe.name or 'Recipe Details'}")
        self.resize(750, 650)
        self.title_bar.btn_maximize.setVisible(False)
        self.title_bar.btn_toggle_sidebar.setVisible(False)

        # ── Fonts ──
        font_recipe_title = QFont()
        font_recipe_title.setPointSize(26)
        font_recipe_title.setFamily("Times New Roman")
        font_recipe_title.setWeight(QFont.Bold) # If title should be bold

        font_section_title = QFont()
        font_section_title.setPointSize(16)
        font_section_title.setBold(True)

        # ── Main Recipe Title ──
        lbl_recipe_title = QLabel(self.recipe.name or "Untitled Recipe")
        lbl_recipe_title.setObjectName("recipeDisplayTitle")
        lbl_recipe_title.setFont(font_recipe_title)
        lbl_recipe_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_recipe_title.setStyleSheet("padding-bottom: 10px; margin-left: 5px;") # Add some spacing

        # ── Recipe Image ──
        img_label = self._create_recipe_image()
        img_label.setAlignment(Qt.AlignCenter)

        # ── Ingredients Section ──
        lbl_ingredients_title = QLabel("Ingredients")
        lbl_ingredients_title.setObjectName("sectionTitle")
        lbl_ingredients_title.setFont(font_section_title)

        # ingredients text area
        txt_ingredients = QTextEdit()
        txt_ingredients.setObjectName("recipeText")
        txt_ingredients.setReadOnly(True)
        txt_ingredients.setHtml(self._format_ingredients())
        txt_ingredients.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        txt_ingredients.setMinimumHeight(150)

        # ── Metadata Section ──
        meta_layout = self._create_metadata_layout()
        meta_widget = QWidget() # wrapper for metadata
        meta_widget.setLayout(meta_layout) # add layout to widget
        meta_widget.setObjectName("metadataBox")

        # Example styling (adjust as needed):
        meta_widget.setStyleSheet("#metadataBox { background-color: #f0f0f0; border-radius: 5px; }")


        # ── Directions Section ──
        lbl_directions_title = QLabel("Directions")
        lbl_directions_title.setObjectName("sectionTitle")
        lbl_directions_title.setFont(font_section_title)

        txt_directions = QTextEdit()
        txt_directions.setObjectName("recipeText")
        txt_directions.setReadOnly(True)
        txt_directions.setHtml(self._format_directions())
        txt_directions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ── Layouts ──

        # Left Column Layout (Image + Ingredients)
        left_col_layout = QVBoxLayout()
        left_col_layout.addWidget(img_label, 0, Qt.AlignCenter)
        left_col_layout.addSpacing(15)
        left_col_layout.addWidget(lbl_ingredients_title)
        left_col_layout.addWidget(txt_ingredients, 1) # Allow ingredients to stretch


        # Right Column Layout (Metadata + Directions)
        right_col_layout = QVBoxLayout()
        right_col_layout.addWidget(meta_widget)
        right_col_layout.addSpacing(15)
        right_col_layout.addWidget(lbl_directions_title)
        right_col_layout.addWidget(txt_directions, 1) # Allow directions to stretch


        # Main Horizontal Split Layout
        main_split_layout = QHBoxLayout()
        main_split_layout.setSpacing(20) # Space between left and right columns
        # Add layouts with stretch factors to approximate screenshot proportions
        main_split_layout.addLayout(left_col_layout, 3) # Left takes ~30-40%
        main_split_layout.addLayout(right_col_layout, 5) # Right takes ~60-70%

        # Add widgets to the BaseDialog's content_layout
        # (Inherited from BaseDialog - add widgets here)
        self.content_layout.addWidget(lbl_recipe_title)
        self.content_layout.addLayout(main_split_layout)


    def _create_recipe_image(self) -> QLabel:
        """Creates the recipe image label using the helper function."""
        if self.recipe.has_image():
            try:
                # Ensure the rounded_image function is available
                if 'rounded_image' in globals() and callable(rounded_image):
                     img_lbl = rounded_image(
                         image_path=self.recipe.image_path,
                         dimension=180,
                         radii=(12, 12, 12, 12), # Rounded corners
                     )
                     return img_lbl
                else:
                     raise NameError("rounded_image function not found")
            except Exception as e:
                print(f"Error loading recipe image '{self.recipe.image_path}': {e}")
                # Fallback to placeholder if loading fails
        return self._create_placeholder_image(180)


    def _create_placeholder_image(self, dimension: int) -> QLabel:
        """Creates a styled placeholder label for when the image is missing/failed."""
        lbl = QLabel(f"Image\nNot Available")
        lbl.setFixedSize(dimension, dimension)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: #f0f0f0;
                border: 1px dashed #cccccc;
                border-radius: 12px;
                color: #888888;
                font-size: 11px;
            }}
        """)
        return lbl

    def _create_metadata_layout(self) -> QVBoxLayout:
        """Creates the vertical layout for category, time, and servings."""
        layout = QVBoxLayout()
        layout.setSpacing(8) # Spacing between metadata items
        layout.setContentsMargins(5, 5, 5, 5) # Padding inside the metadata area

        # Category
        if self.recipe.category:
            layout.addLayout(self._create_icon_text_row("category.svg", self.recipe.category))

        # Total Time
        if self.recipe.total_time:
             time_str = self.recipe.formatted_total_time()
             if time_str: # Only add if time is valid
                layout.addLayout(self._create_icon_text_row("total_time.svg", time_str))

        # Servings
        if self.recipe.servings:
            servings_str = self.recipe.formatted_servings()
            if servings_str: # Only add if servings is valid
                layout.addLayout(self._create_icon_text_row("servings.svg", servings_str))

        layout.addStretch(1) # Push items to the top
        return layout


    def _create_icon_text_row(self, icon_name: str, text: str) -> QHBoxLayout:
        """Helper to create a horizontal layout with an icon and text."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(8) # Space between icon and text

        try:
            # Ensure Icon class is available
            if 'Icon' in globals() and callable(Icon):
                 icon_widget = Icon(
                    name=icon_name,
                    size=ICON_SIZE,
                    color=ICON_COLOR,
                    source="#000", # Or remove if your Icon class doesn't need source
                 )
                 row_layout.addWidget(icon_widget)
            else:
                 raise NameError("Icon class not found")
        except Exception as e:
            print(f"Error creating icon '{icon_name}': {e}")
            # Placeholder if icon fails
            row_layout.addWidget(QLabel("?"))

        lbl_text = QLabel(text)
        row_layout.addWidget(lbl_text)
        row_layout.addStretch(1) # Push icon/text to the left
        return row_layout

    def _format_ingredients(self) -> str:
        """Formats the ingredients list as an HTML bulleted list."""
        if not self.recipe.ingredients:
            return "<p>No ingredients listed.</p>"

        html = "<ul style='margin-left: 0px; padding-left: 20px;'>" # Basic list styling
        for ingredient in self.recipe.ingredients:
            # Using str() assumes RecipeIngredient has a __str__ method
            # that returns the desired text (e.g., "12 oz spaghetti")
            html += f"<li>{str(ingredient)}</li>"
        html += "</ul>"
        return html

    def _format_directions(self) -> str:
        """Formats the directions as an HTML numbered list."""
        if not self.recipe.directions or not str(self.recipe.directions).strip():
            return "<p>No directions provided.</p>"

        # Treat directions as potentially multi-line string. Split into steps.
        steps = str(self.recipe.directions).strip().split('\n')

        # Filter out empty lines and remove potential leading/trailing whitespace
        cleaned_steps = [step.strip() for step in steps if step.strip()]

        if not cleaned_steps:
             return "<p>No directions provided.</p>"

        # Check if steps look like they are already numbered (e.g., "1.", "2. ")
        # This is a basic check and might need refinement
        already_numbered = all(step[0].isdigit() and step[1] in ['.', ')'] for step in cleaned_steps if len(step) > 1)

        if already_numbered:
            # Just wrap existing lines in paragraph tags for spacing
             html = "".join(f"<p style='margin-bottom: 8px;'>{step}</p>" for step in cleaned_steps)

        else:
            # Create an ordered list
            html = "<ol style='margin-left: 0px; padding-left: 20px;'>"
            for step in cleaned_steps:
                html += f"<li style='margin-bottom: 8px;'>{step}</li>" # Add space between items
            html += "</ol>"
        return html


