"""app/ui/views/full_recipe.py

Defines the FullRecipe class, a view for displaying full recipe details including
metadata, ingredients, and directions.
"""
# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget)

from app.core.models import Recipe
from app.style.icon import Icon, Name
from app.style import Theme, Qss
from app.ui.components.layout import Separator
from app.ui.components.widgets import RoundedImage
from app.ui.components.widgets.button import Button
from app.ui.helpers.ui_helpers import create_framed_layout
from app.style.icon.config import Type


# ── Full Recipe ──────────────────────────────────────────────────────────────────────────────
class FullRecipe(QWidget):
    """View for displaying a complete recipe with custom layout.

    Displays:
        - Back button to return to recipe list
        - Header with recipe name
        - Meta info (servings, time, category)
        - Ingredients list
        - Step-by-step directions
    """
    
    back_clicked = Signal()
    
    def __init__(self, recipe: Recipe, parent=None):
        super().__init__(parent)
        self.recipe = recipe

        # register for component-specific styling
        Theme.register_widget(self, Qss.FULL_RECIPE)

        # ── Widget Properties ──
        self.setObjectName("FullRecipeView")

        # ── Setup UI ──
        self.setup_ui()

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def setup_ui(self) -> None:
        """Set up the full view layout with back button, header, left, and right columns."""
        # ── Create Main Layout ──
        lyt_main = QVBoxLayout()
        lyt_main.setSpacing(30)
        lyt_main.setContentsMargins(20, 20, 20, 20)

        # ── Add Back Button ──
        back_button_layout = QHBoxLayout()
        self.btn_back = Button(
            label="Back to Recipes",
            type=Type.SECONDARY
        )
        self.btn_back.setIcon(Name.BACK)
        self.btn_back.clicked.connect(self.back_clicked.emit)
        back_button_layout.addWidget(self.btn_back)
        back_button_layout.addStretch()
        lyt_main.addLayout(back_button_layout)

        # add header
        header_frame = self.build_header_frame()
        lyt_main.addWidget(header_frame, 0) # add header to main layout

        # ── Add Left & Right Columns ──
        lyt_body = QHBoxLayout()
        left_column = self._build_left_column()
        right_column = self._build_right_column()
        lyt_body.addLayout(left_column, 2)
        lyt_body.addLayout(right_column, 3)
        lyt_main.addLayout(lyt_body, 1)

        # ── Set Main Layout ──
        self.setLayout(lyt_main)

    def build_header_frame(self) -> QFrame:
        """Creates the recipe image widget."""
        self.header_frame, lyt_header = create_framed_layout(line_width=0)

        # recipe name
        self.lbl_recipe_name = QLabel(self.recipe.recipe_name)
        self.lbl_recipe_name.setObjectName("RecipeName")
        self.lbl_recipe_name.setAlignment(Qt.AlignCenter)
        lyt_header.addWidget(self.lbl_recipe_name, 0, Qt.AlignHCenter) # add to layout
        # separator
        self.separator = Separator.horizontal(690)
        lyt_header.addWidget(self.separator, 0, Qt.AlignHCenter) # add to layout

        return self.header_frame

    def build_image_frame(self) -> QFrame:
        """Creates the recipe image widget."""
        self.image_frame, lyt_image = create_framed_layout(line_width=0)

        # add image to layout
        self.recipe_image = RoundedImage(
            image_path = (self.recipe.image_path),
            size = 280,
            radii= (0, 0, 0, 0)  # no rounded corners for full image
        )
        lyt_image.addWidget(self.recipe_image, 0, Qt.AlignCenter)

        return self.image_frame

    def build_meta_frame(self) -> QFrame:
        """Creates the meta information widget."""
        self.meta_info_widget, lyt_meta = create_framed_layout(line_width=0)

        # add meta info to layout using Name enum
        for icon_name, text in (
            (Name.SERVINGS, str(self.recipe.servings)),
            (Name.TOTAL_TIME, str(self.recipe.total_time)),
            (Name.CATEGORY, self.recipe.recipe_category),
            (Name.MEAL_TYPE, self.recipe.meal_type),
            (Name.DIET_PREF, self.recipe.diet_pref or "None"),
        ):
            lyt_meta.addWidget(
                self._build_meta_row(icon_name, text)
            )

        return self.meta_info_widget

    def build_ingredients_frame(self) -> QFrame:
        """Creates the ingredients list widget with bulleted items."""
        self.ingredients_widget, lyt_ingredients = create_framed_layout(line_width=0)

        # header
        lbl_ingredients_header = QLabel("Ingredients")
        lbl_ingredients_header.setProperty("textHeader", True)
        lyt_ingredients.addWidget(lbl_ingredients_header, 0, Qt.AlignTop) # add to layout

        # pull in the flattened details (quantity + unit + name)
        details = self.recipe.get_ingredient_details()

        if details:
            # format them into human‐readable strings:
            lines = []
            for d in details:
                qty = f"{d.quantity:g}" if d.quantity is not None else ""
                unit = d.unit or ""
                prefix = f"{qty} {unit}".strip()
                label = f"{prefix} - {d.ingredient_name}" if prefix else d.ingredient_name
                lines.append(label)

            ingredients_block = self.build_list_block(
                items=lines,
                bullet_symbol="•",
                bullet_color="#3B575B",
                margins=(12, 20, 4, 4),
                spacing=12,
                label_property="textIngredients",
            )
            lyt_ingredients.addWidget(ingredients_block)
        else:
            lyt_ingredients.addWidget(QLabel("No ingredients available."))

        # spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        lyt_ingredients.addItem(spacer) # add to layout

        return self.ingredients_widget

    def build_directions_frame(self) -> QFrame:
        """Creates the directions list widget with each step on its own line."""
        self.directions_widget, lyt_directions = create_framed_layout(line_width=0)
        self.directions_widget.setObjectName("DirectionsFrame")

        # ── Header ──
        lbl_directions_header = QLabel("Directions")
        lbl_directions_header.setProperty("textHeader", True)
        lyt_directions.addWidget(lbl_directions_header, 0, Qt.AlignTop)

        # ── Directions List ──
        directions = self.recipe.directions or ""
        lines = [line.strip() for line in directions.splitlines() if line.strip()]

        if lines:
            directions_block = self.build_list_block(
                items=lines,
                bullet_symbol= None,
                margins= (8, 20, 4, 4),
                spacing=20, # space between steps
                label_property="textDirections",
            )
            lyt_directions.addWidget(directions_block)
        else:
            lbl_empty = QLabel("No directions available.")
            lbl_empty.setWordWrap(True)
            lyt_directions.addWidget(lbl_empty, 0, Qt.AlignTop)

        # ── Spacer ──
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        lyt_directions.addItem(spacer)

        return self.directions_widget

    def build_list_block(
    self,
    items: list[str],
    bullet_symbol: str | None = "•",
    bullet_color: str = "#3B575B",
    margins: tuple = (4, 4, 4, 4),
    spacing: int = 6,
    label_property: str | None = None,
    property_value: any = True,
) -> QFrame:
        """
        Builds a styled QFrame containing a formatted list.

        Args:
            items (list[str]): List of strings to display.
            bullet_symbol (str | None, optional): Symbol to use as a bullet (e.g., '•', '1.', or None to disable).
                Use "numbers" to auto-number each line. Set to None or "" to omit bullets entirely.
            bullet_color (str, optional): Color of the bullet symbol (ignored if bullet_symbol is None).
            margins (tuple, optional): Layout margins (left, top, right, bottom).
            spacing (int, optional): Vertical spacing between list items (in pixels).

        Returns:
            QFrame: A framed widget containing the formatted list.
        """
        # ── Create sub-frame ──
        frame, layout = create_framed_layout(
            frame_shape=QFrame.NoFrame,
            margins=margins,
            spacing=0,
        )

        # ── Format list into RichText ──
        html = ""
        for idx, item in enumerate(items, start=1):
            if bullet_symbol == "numbers":
                bullet_html = f'<span style="color:{bullet_color};">{idx}.</span> '
            elif bullet_symbol:  # handles non-empty string like '•'
                bullet_html = f'<span style="color:{bullet_color};">{bullet_symbol}</span> '
            else:
                bullet_html = ""

            html += (
                f'<div style="margin-bottom:{spacing}px;">'
                f'{bullet_html}{item}'
                f'</div>'
            )

        # ── Create QLabel for RichText ──
        lbl_list = QLabel()
        lbl_list.setTextFormat(Qt.RichText)
        lbl_list.setText(html)
        lbl_list.setWordWrap(True)
        lbl_list.setStyleSheet("padding: 2px 4px;")

        # ── Optional QSS property ──
        if label_property:
            lbl_list.setProperty(label_property, property_value)

        layout.addWidget(lbl_list)

        return frame

    # ── Private Methods ─────────────────────────────────────────────────────────────────
    def _build_left_column(self) -> QVBoxLayout:
        """Constructs the left side of the view (Image + Ingredients)."""
        lyt = QVBoxLayout()
        lyt.setSpacing(30)

        lyt.addWidget(self.build_image_frame(),1)
        lyt.addWidget(self.build_ingredients_frame(),2)

        return lyt

    def _build_right_column(self) -> QVBoxLayout:
        """Constructs the right side of the view (Meta Info + Directions)."""
        lyt = QVBoxLayout()
        lyt.setSpacing(30)

        lyt.addWidget(self.build_meta_frame(),1)
        lyt.addWidget(self.build_directions_frame(),3)

        return lyt

    def _build_meta_row(self, icon_name: Name, text: str) -> QWidget:
        """Helper to create a row with an icon and label, nicely spaced."""
        # ── Create Row ──
        container = QWidget()
        lyt = QHBoxLayout(container)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(20)

        # ── Create Icon & Label ──
        icon = Icon(icon_name)
        lbl = QLabel(text)
        lbl.setProperty("metaTitle", True)
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # ── add widgets to layout ──
        lyt.addWidget(icon)
        lyt.addWidget(lbl)
        lyt.addStretch() # add stretch to push widgets to the left

        return container


