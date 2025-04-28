# File: ui/dialogs/full_recipe_dialog.py (Example path)

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSizePolicy, QFrame, QSpacerItem, QScrollArea,
)
from PySide6.QtCore import Qt, QSize

from core.helpers.debug_layout import DebugLayout
from core.modules.recipe_module import Recipe
from database import DB_INSTANCE
from helpers.icon_helpers import Icon
from helpers.app_helpers.base_dialog import BaseDialog
from helpers.ui_helpers import Image, Separator

# ── Constants ───────────────────────────────────────────────────────────────────
ICON_SIZE = QSize(30,30)
ICON_COLOR = "#3B575B"  # Example color, adjust as needed
# ── Class Definition ────────────────────────────────────────────────────────────
class RecipeDialogBuilder(BaseDialog):
    """
    A dialog to display a full recipe, mimicking the provided screenshot layout.
    Inherits from BaseDialog for custom window chrome.
    """
    def __init__(self, recipe: Recipe, parent=None):
        super().__init__(parent)
        self.recipe = recipe

        # ── Window Properties ──
        self.setFixedSize(760, 983.25)  # roughly 8.5 x 10.35 inches at 96 DPI
        self.title_bar.btn_maximize.setVisible(False)
        self.title_bar.btn_toggle_sidebar.setVisible(False)
        self.setObjectName("RecipeDialog")

        # ── Setup UI ──
        self._setup_ui()
        self.overlay = DebugLayout(self)

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        """Builds the main UI layout."""
        # ── Create Main Layout ──
        self.lyt_main = QVBoxLayout()
        self.lyt_main.setSpacing(30)
        self.lyt_main.setContentsMargins(20, 20, 20, 20)

        # ── Add Header ──
        self.header_frame = self.build_header_frame()
        self.lyt_main.addWidget(self.header_frame, 0) # add header to main layout

        # ── Add Left & Right Columns ──
        self.lyt_body = QHBoxLayout()
        self.left_column = self._build_left_column()
        self.right_column = self._build_right_column()
        self.lyt_body.addLayout(self.left_column, 2)
        self.lyt_body.addLayout(self.right_column, 3)
        self.lyt_main.addLayout(self.lyt_body, 1)

        # ── Add Header & Columns ──
        self.content_layout.addLayout(self.lyt_main)

    def build_header_frame(self) -> QFrame:
        """Creates the recipe image widget."""
        # create frame
        self.header_frame, lyt_header = self._create_framed_layout(line_width=0)

        # recipe name
        self.lbl_recipe_name = QLabel(self.recipe.name)
        self.lbl_recipe_name.setObjectName("RecipeName")
        self.lbl_recipe_name.setAlignment(Qt.AlignCenter)
        lyt_header.addWidget(self.lbl_recipe_name) # add recipe name to layout

        # separator
        self.separator = Separator.horizontal(690) # intentionally omitted for now
        lyt_header.addWidget(self.separator, 0, Qt.AlignCenter) # add separator to layout

        return self.header_frame

    def build_image_frame(self) -> QFrame:
        """Creates the recipe image widget."""
        # create frame
        self.image_frame, lyt_image = self._create_framed_layout(line_width=0)

        # add image to layout
        self.recipe_image = Image(self.recipe.image_path, 280, self.image_frame)
        lyt_image.addWidget(self.recipe_image, 0, Qt.AlignCenter)

        return self.image_frame

    def build_meta_frame(self) -> QFrame:
        """Creates the meta information widget."""
        # create frame
        self.meta_info_widget, lyt_meta = self._create_framed_layout(line_width=0)

        # add meta info to layout
        lyt_meta.addWidget(self._build_meta_row("servings.svg", str(self.recipe.servings)))
        lyt_meta.addWidget(self._build_meta_row("total_time.svg", str(self.recipe.total_time)))
        lyt_meta.addWidget(self._build_meta_row("category.svg", self.recipe.category))

        return self.meta_info_widget

    def build_ingredients_frame(self) -> QFrame:
        """Creates the ingredients list widget."""
        # create frame
        self.ingredients_widget, lyt_ingredients = self._create_framed_layout()

        #TODO: Add ingredients list
        # add ingredients to layout

        return self.ingredients_widget

    def build_directions_frame(self) -> QFrame:
        """Creates the directions list widget."""
        # create frame
        self.directions_widget, lyt_directions = self._create_framed_layout()

        #TODO: Add directions list
        # add directions to layout

        return self.directions_widget

    # ── Private Methods ─────────────────────────────────────────────────────────────
    def _create_framed_layout(
    self,
    frame_shape:  QFrame.Shape = QFrame.Box,
    frame_shadow: QFrame.Shadow = QFrame.Plain,
    line_width:   int = 1,
    size_policy:  tuple = (QSizePolicy.Expanding, QSizePolicy.Expanding),
    margins:      tuple = (0, 0, 0, 0),
    spacing:      int = 0,
) -> tuple[QFrame, QVBoxLayout]:
        """
        Creates a QFrame with a QVBoxLayout inside, with standardized styling.

        Returns:
            Tuple containing (QFrame, QVBoxLayout).
        """
        frame = QFrame()
        frame.setFrameShape(frame_shape)
        frame.setFrameShadow(frame_shadow)
        frame.setLineWidth(line_width)
        frame.setSizePolicy(*size_policy)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)

        return frame, layout


    def _build_left_column(self) -> QVBoxLayout:
        """Constructs the left side of the dialog (Image + Ingredients)."""
        lyt = QVBoxLayout()
        lyt.setSpacing(30)

        lyt.addWidget(self.build_image_frame(),1)
        lyt.addWidget(self.build_ingredients_frame(),2)

        return lyt

    def _build_right_column(self) -> QVBoxLayout:
        """Constructs the right side of the dialog (Meta Info + Directions)."""
        lyt = QVBoxLayout()
        lyt.setSpacing(30)

        lyt.addWidget(self.build_meta_frame(),1)
        lyt.addWidget(self.build_directions_frame(),3)

        return lyt

    def _build_meta_row(self, icon_name: str, text: str) -> QWidget:
        """Helper to create a row with an icon and label, nicely spaced."""
        container = QWidget()
        lyt = QHBoxLayout(container)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(20)

        icon = Icon(icon_name, ICON_SIZE, ICON_COLOR)
        lbl = QLabel(text)
        lbl.setProperty("metaTitle", True)
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lyt.addWidget(icon)
        lyt.addWidget(lbl)
        lyt.addStretch()

        return container


