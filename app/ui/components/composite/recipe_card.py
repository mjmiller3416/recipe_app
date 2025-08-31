"""Recipe Card Components

This module provides a consolidated recipe card system built on BaseCard architecture.
Replaces the previous multi-file package structure with a single, maintainable file
containing all recipe card variants and state management.

Classes:
    BaseRecipeCard: Core recipe card functionality inheriting from BaseCard
    SmallRecipeCard: Horizontal layout variant (image + name)
    MediumRecipeCard: Vertical layout variant (image + overlay + metadata)
    LargeRecipeCard: Complex layout variant (title + image/info panel + metadata)
    LayoutSize: Enum defining card size variants

Functions:
    create_recipe_card: Factory function for creating appropriate card size
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from enum import Enum
from typing import Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QStackedWidget, QVBoxLayout, QWidget)

from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.style import Theme
from app.style.icon import AppIcon, Name, Type
from app.style.theme.config import Qss
from app.ui.components.layout.card import BaseCard
from app.ui.components.composite.recipe_info_card import RecipeInfoCard
from app.ui.components.layout import Separator
from app.ui.components.widgets import RoundedImage, ToolButton
from app.ui.helpers.ui_helpers import make_overlay
from _dev_tools.debug_logger import DebugLogger


# ── Constants ────────────────────────────────────────────────────────────────────────────────
LAYOUT_SIZE = {
    "small": QSize(300, 120),
    "medium": QSize(280, 420),
    "large": QSize(1200, 600),
}
ICON_COLOR = "#6ad7ca"


# ── Enums ────────────────────────────────────────────────────────────────────────────────────
class LayoutSize(Enum):
    """Enum to define the target layout size for the RecipeCard when displaying a recipe."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# ── Base Recipe Card ─────────────────────────────────────────────────────────────────────────
class BaseRecipeCard(BaseCard):
    """Base class for all recipe card variants with shared business logic.

    Provides common functionality for recipe display, state management, and user interactions
    while allowing size-specific subclasses to implement their own layout strategies.

    This class inherits from BaseCard to leverage the established card architecture including
    theming integration, layout management, and consistent styling patterns.

    Attributes:
        _size (LayoutSize): The card's size category
        _recipe (Optional[Recipe]): Currently displayed recipe
        _stack (QStackedWidget): Widget stack for different states
        _selection_mode (bool): Whether card is in selection mode
        _recipe_selection_dialog (Optional[QDialog]): Dialog for recipe selection

    Signals:
        add_meal_clicked(): Emitted when empty state button is clicked
        card_clicked(object): Emitted when recipe card is clicked (passes recipe)
        delete_clicked(int): Emitted for delete actions (passes recipe_id)
        recipe_selected(int): Emitted when recipe is set (passes recipe_id)
    """

    # ── Signals ──────────────────────────────────────────────────────────────────────────────
    add_meal_clicked = Signal()
    card_clicked = Signal(object)     # recipe instance
    delete_clicked = Signal(int)      # recipe_id
    recipe_selected = Signal(int)     # recipe_id

    def __init__(self, size: LayoutSize, parent: QWidget | None = None):
        """Initialize the BaseRecipeCard with size category and stacked widget management.

        Args:
            size (LayoutSize): The size category for this card
            parent (QWidget | None): Parent widget, if any
        """
        super().__init__(parent, content_layout="vbox", card_type="Recipe")

        self.setObjectName("RecipeCard")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Core properties
        self._size: LayoutSize = size
        self._recipe: Optional[Recipe] = None
        self._recipe_selection_dialog: Optional[QDialog] = None
        self._selection_mode: bool = False  # When True, prevents FullRecipe dialog from opening

        # Set fixed size based on size category
        self.setFixedSize(LAYOUT_SIZE[size.value])

        # Create stacked widget for different states
        self._stack = QStackedWidget(self)
        self.addWidget(self._stack)

        # Setup states
        self._setup_stacked_widget()

        # Register for theming
        Theme.register_widget(self, Qss.RECIPE_CARD)

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def set_recipe(self, recipe: Recipe | None) -> None:
        """Load or clear a recipe in this RecipeCard.

        Args:
            recipe (Recipe | None): The Recipe object to display.
                None → revert to the empty state.
        """
        if recipe is None:
            self._recipe = None
            self._stack.setCurrentIndex(0)  # show empty state
            return

        # Build recipe card
        self._recipe = recipe
        try:
            new_frame = self._build_recipe_layout()
            self._swap_recipe_state(new_frame)
            self._stack.setCurrentIndex(1)  # show recipe state

            # Wire click handler
            new_frame.mousePressEvent = self._emit_card_clicked

            # Emit recipe ID
            rid = getattr(recipe, "id", getattr(recipe, "recipe_id", None))
            if rid is not None:
                self.recipe_selected.emit(rid)

        except Exception as exc:
            DebugLogger.log("RecipeCard failed to build card: {exc}", "error", exc=exc)
            self._stack.setCurrentIndex(2)  # show error state

    def set_selection_mode(self, selection_mode: bool) -> None:
        """Set whether this card is in selection mode.

        Args:
            selection_mode (bool): If True, clicking the card won't open FullRecipe dialog.
        """
        self._selection_mode = selection_mode

    def recipe(self) -> Recipe | None:
        """Return the currently displayed recipe (or None)."""
        return self._recipe

    # ── Abstract Method ──────────────────────────────────────────────────────────────────────
    def _build_recipe_layout(self) -> QWidget:
        """Build the recipe-specific layout for this card size.

        This method must be implemented by size-specific subclasses to define
        their unique layout and content organization.

        Returns:
            QWidget: The widget containing the recipe layout

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _build_recipe_layout")

    # ── State Management ─────────────────────────────────────────────────────────────────────
    def _setup_stacked_widget(self) -> None:
        """Initialize the stacked widget with empty, recipe, and error states."""
        # Add states to stack
        self._stack.addWidget(self._create_empty_state())    # index 0
        self._stack.addWidget(QFrame())                      # placeholder for recipe (index 1)
        self._stack.addWidget(self._create_error_state())    # index 2

        # Set initial state
        self._stack.setCurrentIndex(0)

    def _create_empty_state(self) -> QWidget:
        """Create empty state widget with Add Meal button.

        Returns:
            QWidget: Widget containing centered 'Add Meal' button
        """
        frame = QFrame()
        frame.setObjectName("EmptyStateFrame")
        frame.setProperty("layout_size", self._size.value)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add meal button
        btn_add = ToolButton(Type.DEFAULT, Name.ADD_RECIPES)
        btn_add.setObjectName("AddMealButton")  # RecipeCard looks for this
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._handle_add_meal_click)

        layout.addWidget(btn_add, 0, Qt.AlignCenter)

        return frame

    def _create_error_state(self, message: str = "Failed to load recipe.") -> QWidget:
        """Create error state widget with error message.

        Args:
            message (str): Error message to display

        Returns:
            QWidget: Widget containing centered error label
        """
        frame = QFrame()
        frame.setObjectName("ErrorStateFrame")
        frame.setProperty("layout_size", self._size.value)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)

        # Error message
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color: red;")

        layout.addWidget(label)

        return frame

    # ── Business Logic ───────────────────────────────────────────────────────────────────────
    def _toggle_favorite_with_icon_update(self, button, recipe_id: int) -> None:
        """Helper to toggle favorite status and update the button icon.

        Args:
            button: The button widget to update
            recipe_id (int): ID of the recipe to toggle
        """
        try:
            from app.ui.components.widgets.button import BaseButton

            service = RecipeService()
            updated_recipe = service.toggle_favorite(recipe_id)

            # Update the card's recipe object with the new state
            if self._recipe:
                self._recipe.is_favorite = updated_recipe.is_favorite

            BaseButton.swapIcon(button, updated_recipe.is_favorite, Name.FAV_FILLED, Name.FAV)

        except Exception:
            pass

    def _create_meta_section(self, icon_widget: AppIcon, heading: str, value: str) -> QVBoxLayout:
        """Create a vertical layout section for displaying metadata with an icon, heading, and value.

        Args:
            icon_widget (AppIcon): The AppIcon widget to display.
            heading (str): Label heading (e.g., "Servings", "Time").
            value (str): Value associated with the heading (e.g., "4", "30 min").

        Returns:
            QVBoxLayout: Layout containing the icon, heading, and value widgets.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Icon
        icon_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_widget, 0, Qt.AlignCenter)

        # Heading
        lbl_heading = QLabel(heading)
        lbl_heading.setProperty("label_text", True)
        lbl_heading.setAlignment(Qt.AlignCenter)
        lbl_heading.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(lbl_heading)

        # Value
        lbl_value = QLabel(value)
        lbl_value.setProperty("value_text", True)
        lbl_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_value)

        return layout

    # ── Private Methods ──────────────────────────────────────────────────────────────────────
    def _swap_recipe_state(self, new_frame: QFrame) -> None:
        """Replace the existing recipe page (index 1) with a fresh one.

        Args:
            new_frame (QFrame): New frame to insert at index 1
        """
        # Remove old frame and delete it
        old = self._stack.widget(1)
        self._stack.removeWidget(old)
        old.deleteLater()

        new_frame.setObjectName("RecipeCard")
        new_frame.setAttribute(Qt.WA_StyledBackground, True)

        # Insert new frame at index 1
        self._stack.insertWidget(1, new_frame)

    def _emit_card_clicked(self, event) -> None:
        """Emit the card_clicked signal when card is clicked.

        Args:
            event: Mouse press event
        """
        if event.button() == Qt.LeftButton and self._recipe:
            self.card_clicked.emit(self._recipe)

    def _handle_add_meal_click(self):
        """Handle the click event for the 'Add Meal' button in the empty state."""
        DebugLogger.log("Add Meal button clicked in RecipeCard", "info")
        self.add_meal_clicked.emit()


# ── Small Recipe Card ────────────────────────────────────────────────────────────────────────
class SmallRecipeCard(BaseRecipeCard):
    """Small recipe card with horizontal layout: image + name.

    Provides a compact horizontal layout suitable for list views or
    situations where vertical space is limited.
    """

    def _build_recipe_layout(self) -> QWidget:
        """Build the small layout for the recipe card.

        Returns:
            QWidget: Frame containing horizontal image + name layout
        """
        frame = QFrame()
        frame.setProperty("layout_size", self._size.value)
        frame.setAttribute(Qt.WA_StyledBackground, True)
        frame.setObjectName("RecipeCard")

        # Horizontal layout
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Recipe image
        img_recipe = RoundedImage(
            image_path=self._recipe.reference_image_path,
            size=120,
            radii=(10, 0, 0, 10)
        )
        layout.addWidget(img_recipe)

        # Recipe name
        lbl_name = QLabel(self._recipe.recipe_name)
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_name)

        return frame


# ── Medium Recipe Card ───────────────────────────────────────────────────────────────────────
class MediumRecipeCard(BaseRecipeCard):
    """Medium recipe card with vertical layout: image + overlay + name + metadata.

    Provides a standard card layout with recipe image, favorite button overlay,
    recipe name, and basic metadata (servings and time).
    """

    def _build_recipe_layout(self) -> QWidget:
        """Build the medium layout for the recipe card.

        Returns:
            QWidget: Frame containing vertical image + metadata layout
        """
        frame = QFrame()
        frame.setProperty("layout_size", self._size.value)
        frame.setAttribute(Qt.WA_StyledBackground, True)
        frame.setObjectName("RecipeCard")

        # Vertical layout
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Recipe image
        img_recipe = RoundedImage(
            image_path=self._recipe.reference_image_path,
            size=280,
            radii=(10, 10, 0, 0)
        )

        # Favorite button - choose initial icon based on favorite state
        initial_icon = Name.FAV_FILLED if self._recipe.is_favorite else Name.FAV
        btn_fav = ToolButton(Type.DEFAULT, initial_icon)
        btn_fav.setIconSize(24, 24)
        btn_fav.setObjectName("btn_favorite")
        btn_fav.setCheckable(True)
        btn_fav.setCursor(Qt.PointingHandCursor)
        btn_fav.setChecked(bool(self._recipe.is_favorite))
        btn_fav.toggled.connect(
            lambda checked, rid=self._recipe.id: self._toggle_favorite_with_icon_update(btn_fav, rid)
        )

        # Create overlay
        overlay = make_overlay(img_recipe, btn_fav)
        layout.addWidget(overlay)

        # Recipe name
        lbl_name = QLabel(self._recipe.recipe_name)
        lbl_name.setProperty("title_text", "true")
        lbl_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_name)

        # Metadata section
        meta_layout = QHBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 8)
        meta_layout.setSpacing(0)

        # Add servings
        meta_layout.addLayout(
            self._create_meta_section(
                AppIcon(Name.SERVINGS),
                heading="Servings",
                value=self._recipe.formatted_servings(),
            )
        )

        # Separator
        meta_layout.addWidget(Separator.vertical(70), 0, Qt.AlignVCenter)

        # Add total time
        meta_layout.addLayout(
            self._create_meta_section(
                AppIcon(Name.TOTAL_TIME),
                heading="Time",
                value=self._recipe.formatted_time(),
            )
        )

        layout.addLayout(meta_layout)

        return frame


# ── Large Recipe Card ────────────────────────────────────────────────────────────────────────
class LargeRecipeCard(BaseRecipeCard):
    """Large recipe card with complex layout: title + image/info panel + metadata.

    Provides a comprehensive card layout with recipe title, image with overlay,
    detailed info panel with tags and ingredients preview, and metadata sections.
    """

    def _build_recipe_layout(self) -> QWidget:
        """Build the large layout for the recipe card.

        Returns:
            QWidget: Frame containing complex multi-section layout
        """
        # register for component-specific styling
        frame = QFrame()
        frame.setProperty("layout_size", self._size.value)
        frame.setAttribute(Qt.WA_StyledBackground, True)
        frame.setObjectName("RecipeCard")

        from app.ui.components.composite.ingredients_preview import IngredientsPreview
        from app.ui.components.composite.recipe_info_card import RecipeInfoCard
        from app.ui.components.composite.recipe_tags_row import RecipeTagsRow

        # Main layout
        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(12, 20, 12, 12)
        main_layout.setSpacing(10)

        # Content Layout: Image (left) + Info Panel (right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        # Left Side: Recipe Image
        img_recipe = RoundedImage(
            image_path=self._recipe.reference_image_path,
            size=400,
            radii=(10, 10, 10, 10)
        )

        # Favorite button overlay
        initial_icon = Name.FAV_FILLED if self._recipe.is_favorite else Name.FAV
        btn_fav = ToolButton(Type.DEFAULT, initial_icon)
        btn_fav.setIconSize(24, 24)
        btn_fav.setObjectName("btn_favorite")
        btn_fav.setCheckable(True)
        btn_fav.setCursor(Qt.PointingHandCursor)
        btn_fav.setChecked(bool(self._recipe.is_favorite))
        btn_fav.toggled.connect(
            lambda checked, rid=self._recipe.id: self._toggle_favorite_with_icon_update(btn_fav, rid)
        )
        image_overlay = make_overlay(img_recipe, btn_fav) # create image overlay

        # Info Cards Row (compact mode for large card)
        info_cards = RecipeInfoCard(
            show_cards=["time", "servings"])
        info_cards.setRecipe(self._recipe)
        info_cards.setCompactMode(True)
        info_cards.setSpacing(8)

        left_panel.addWidget(image_overlay, 0)
        left_panel.addWidget(info_cards)

        # Add left panel to content layout with more space
        content_layout.addLayout(left_panel)

        # Right Side: Info Panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        # Recipe Title
        title_label = QLabel(self._recipe.recipe_name or "Untitled Recipe")
        title_label.setObjectName("LargeCardTitle")
        title_label.setProperty("title_text", "true")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        right_panel.addWidget(title_label)
        right_panel.addSpacing(6)

        # Recipe Tags Row
        tags_row = RecipeTagsRow()
        tags_row.setRecipe(self._recipe)
        tags_row.setAlignment("center")
        right_panel.addWidget(tags_row)
        # Add some spacing
        right_panel.addSpacing(12)


        # Ingredients Preview (simple scrollable 2-column layout)
        ingredients_preview = IngredientsPreview()
        ingredient_details = getattr(self._recipe, "get_ingredient_details", lambda: [])()
        ingredients_preview.setIngredients(ingredient_details)
        right_panel.addWidget(ingredients_preview, 1)  # Give it stretch to fill space

        # Add small stretch at bottom for spacing
        right_panel.addStretch(0)

        # Add right panel to content layout
        content_layout.addLayout(right_panel, 1)

        # Add content to main layout
        main_layout.addLayout(content_layout)


        return frame


# ── Factory Function ─────────────────────────────────────────────────────────────────────────
def create_recipe_card(size: LayoutSize, parent: QWidget | None = None) -> BaseRecipeCard:
    """Factory function to create appropriate recipe card size.

    Args:
        size (LayoutSize): The size category for the recipe card
        parent (QWidget | None): Parent widget, if any

    Returns:
        BaseRecipeCard: Appropriate card instance for the requested size

    Raises:
        ValueError: If an unsupported size is provided
    """
    size_map = {
        LayoutSize.SMALL: SmallRecipeCard,
        LayoutSize.MEDIUM: MediumRecipeCard,
        LayoutSize.LARGE: LargeRecipeCard,
    }

    if size not in size_map:
        raise ValueError(f"Unsupported size: {size}")

    return size_map[size](size, parent)


