# 🔸 Third-party Imports
from PySide6.QtWidgets import (
    QFrame, QWidget, QLabel, QVBoxLayout, QGridLayout, QSizePolicy,
    QSpacerItem, QDialog, QScrollArea, QTextEdit, QHBoxLayout, QLayout
)
from PySide6.QtGui import QPixmap, QMouseEvent, QFont
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

# 🔸 Local Imports
from core.modules.recipe_module import Recipe
from core.helpers.ui_helpers import set_scaled_image
from core.helpers import svg_loader, wrap_layout
from core.helpers.config import icon_path, ICON_COLOR, ICON_SIZE
from core.helpers.debug_logger import DebugLogger
from core.application.title_bar import TitleBar


class RecipeCard(QFrame):
    """
    A reusable card widget to preview recipe data.

    Supports two visual layout modes ("full" and "mini") and
    an optional meal selection mode that alters interaction behavior.

    Args:
        recipe (Recipe): The Recipe model instance to render.
        layout_mode (str): Layout variant, either "full" or "mini".
        is_meal_selection (bool): Whether this card is in meal selection context.
        parent (QWidget, optional): Parent widget for proper styling context.

    Attributes:
        recipe (Recipe): The Recipe model instance.
        recipe_id (int): The ID of the recipe.
        layout_mode (str): Current layout mode ("full" or "mini").
        is_meal_selection (bool): Flag for meal selection context.

    Raises:
        ValueError: If an invalid layout mode is provided.
    """

    # 🔹 Constants
    FULL_IMAGE_SIZE = QSize(280, 280)
    MINI_IMAGE_SIZE = QSize(20, 20)

    # 🔹 Signals
    recipe_clicked = Signal(int)       # Emitted when card is clicked in default mode
    recipe_selected = Signal(dict)     # Emitted when selected in meal planner mode

    def __init__(self, recipe: Recipe, layout_mode="full", meal_selection=False, parent=None):
        super().__init__(parent)

        # 🔹 Store state and recipe info
        self.recipe = recipe
        self.recipe_id = recipe.id
        self.layout_mode = layout_mode                  # "full" or "mini"
        self.is_meal_selection = meal_selection         # Toggle between selection and display

        # 🔹 Setup styling
        self.setObjectName("RecipeCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 🔹 Build and populate UI
        self.build_ui()
        self.populate()

    def build_ui(self):
        """
        Constructs the appropriate UI layout based on layout_mode.
        Routes layout setup to the correct internal method.
        """
        if self.layout_mode == "mini":
            self._build_mini_layout()
        else:
            self._build_full_layout()

    from core.helpers.ui_helpers import wrap_layout

    def _build_full_layout(self):
        """
        Builds the 'full' layout for the RecipeCard.
        This includes a larger image, stacked metadata, and vertical arrangement.
        """
        self.setFixedSize(QSize(280, 420))

        # 🔹 Image
        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("CardImageFull")
        self.lbl_image.setFixedSize(280, 280)
        self.lbl_image.setScaledContents(True)
        self.lbl_image.setContentsMargins(0, 0, 0, 0)

        # 🔹 Title
        self.lbl_name = QLabel()
        self.lbl_name.setObjectName("CardTitle")
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setContentsMargins(0, 0, 0, 0)

        # ───── Servings Block ─────
        self.lbl_servings_title = QLabel("Servings")
        self.lbl_servings_title.setObjectName("ServingsTitle")
        self.lbl_servings_title.setAlignment(Qt.AlignLeft)
        self.lbl_servings_title.setContentsMargins(0, 0, 0, 0)

        self.servings_icon = QLabel()
        self.servings_icon.setPixmap(
            svg_loader(
                icon_path("servings"), 
                ICON_COLOR, 
                QSize(40, 40), 
                return_type=QPixmap,
                source_color="#000"
            )
        )
        self.servings_icon.setObjectName("ServingsIcon")
        self.servings_icon.setAlignment(Qt.AlignLeft)
        self.servings_icon.setFixedSize(40, 40)
        self.servings_icon.setContentsMargins(0, 0, 0, 0)

        self.lbl_servings = QLabel()
        self.lbl_servings.setObjectName("ServingsLabel")
        self.lbl_servings.setAlignment(Qt.AlignLeft)
        self.lbl_servings.setContentsMargins(0, 0, 0, 0)

        servings_value_row = QHBoxLayout()
        servings_value_row.setContentsMargins(0, 0, 0, 0)
        servings_value_row.setSpacing(4)
        servings_value_row.setAlignment(Qt.AlignLeft)
        servings_value_row.addWidget(self.servings_icon)
        servings_value_row.addWidget(self.lbl_servings)

        servings_layout = QVBoxLayout()
        servings_layout.setContentsMargins(0, 0, 0, 0)
        servings_layout.setSpacing(2)
        servings_layout.setAlignment(Qt.AlignLeft)
        servings_layout.addWidget(self.lbl_servings_title)
        servings_layout.addLayout(servings_value_row)

        # ───── Time Block ─────
        self.lbl_time_title = QLabel("Time")
        self.lbl_time_title.setObjectName("TimeTitle")
        self.lbl_time_title.setAlignment(Qt.AlignRight)
        self.lbl_time_title.setContentsMargins(0, 0, 0, 0)

        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("TimeLabel")
        self.lbl_time.setAlignment(Qt.AlignRight)
        self.lbl_time.setContentsMargins(0, 0, 0, 0)

        time_layout = QVBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(2)
        time_layout.setAlignment(Qt.AlignRight)
        time_layout.addWidget(self.lbl_time_title)
        time_layout.addWidget(self.lbl_time)

        # ───── Metadata Row (Servings + Time) ─────
        meta_container, meta_layout = wrap_layout(QHBoxLayout, "CardMetaRow")
        meta_layout.setContentsMargins(12, 0, 12, 4)
        meta_layout.setSpacing(0)
        meta_layout.addLayout(servings_layout)
        meta_layout.addStretch()
        meta_layout.addLayout(time_layout)

        # ───── Full Layout Wrapper ─────
        full_container, full_layout = wrap_layout(QVBoxLayout, "FullLayoutRoot")
        full_layout.setSpacing(4)
        full_layout.addWidget(self.lbl_image)
        full_layout.addWidget(self.lbl_name)
        full_layout.addWidget(meta_container)

        # ───── Main Layout ─────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(full_container)

    def _build_mini_layout(self):
        """
        Builds the 'mini' layout for the RecipeCard.
        Used in side dish / compact display areas like the meal planner.
        """
        self.setFixedSize(300, 100)

        # 🔹 Image
        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("CardImageMini")
        self.lbl_image.setFixedSize(100, 100)
        self.lbl_image.setScaledContents(True)
        self.lbl_image.setContentsMargins(0, 0, 0, 0)

        # 🔹 Title
        self.lbl_name = QLabel()
        self.lbl_name.setObjectName("CardTitleMini")
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setContentsMargins(0, 0, 0, 0)

        # ───── Mini Layout Wrapper ─────
        mini_container, mini_layout = wrap_layout(QHBoxLayout, "MiniLayoutRoot")
        mini_layout.setSpacing(0)
        mini_layout.addWidget(self.lbl_image)
        mini_layout.addWidget(self.lbl_name)

        # ───── Main Layout ─────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(mini_container)


    def populate(self):
        if self.layout_mode == "mini":
            self._populate_mini()
        elif self.layout_mode == "full":
            self._populate_full()
        else:
            raise ValueError("Invalid layout mode. Use 'full' or 'mini'.")

    def _populate_full(self):
        self.lbl_name.setText(self.recipe.name)
        self.lbl_servings.setText(self.recipe.formatted_servings())
        self.lbl_time.setText(self.recipe.formatted_time())
        self.set_image(self.recipe.image_path)

    def _populate_mini(self):
        self.lbl_name.setText(self.recipe.name)
        self.set_image(self.recipe.image_path)


    def set_image(self, image_path):
        """
        Sets the image for the RecipeCard based on the provided path.
        
        Args:
            image_path (str): The path to the recipe image file.
        """
        size = QSize(100, 100) if self.layout_mode == "mini" else QSize(280, 280)
        set_scaled_image(self.lbl_image, image_path, size)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles clicks based on is_meal_selection flag:
        - If False (default), opens FullRecipe
        - If True, emits recipe_selected

        Args:
            event (QMouseEvent): Mouse click event
        """
        pass  # TODO: Route behavior based on is_meal_selection

    def show_full_recipe(self):
        """
        Opens the FullRecipe dialog using the current recipe model.
        """
        pass  # TODO: Initialize and exec FullRecipe

    def emit_selection(self):
        """
        Emits the recipe_selected signal to notify caller.
        """
        pass  # TODO: Hook up selection logic

    def set_meal_selection(self, enabled: bool):
        """
        Updates whether the card should behave in meal selection mode.

        Args:
            enabled (bool): Toggle meal selection logic
        """
        self.is_meal_selection = enabled


