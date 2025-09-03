"""app/ui/views/full_recipe.py

FullRecipe view redesigned to match mock UI with:
- Title + recipe tags
- Banner image placeholder (fixed 2:1 aspect ratio)
- Horizontal info cards (time, servings, category, dietary)
- Single column layout with ingredients, directions, and notes
- Modern styling using material injection variables

Styling:
- Registers for component-specific QSS with Theme.register_widget(self, Qss.FULL_RECIPE)
- Uses material injection variables for consistent theming
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.core.models import Recipe
from app.core.utils.text_utils import sanitize_multiline_input, sanitize_form_input
from app.style import Qss, Theme
from app.style.icon import AppIcon, Icon
from app.style.icon.config import Name, Type
from app.ui.utils.layout_utils import setup_main_scroll_layout, create_form_grid_layout, create_two_column_layout
from app.ui.utils.event_utils import batch_connect_signals
from app.ui.utils.widget_utils import apply_object_name_pattern
from app.ui.components.composite.recipe_info_card import RecipeInfoCard
from app.ui.components.images.image import RecipeBanner
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.components.widgets.recipe_tag import RecipeTag
from app.ui.constants import LayoutConstants
from app.ui.services.navigation_service import NavigableView, RouteRegistry, ViewType
from _dev_tools.debug_logger import DebugLogger


# ── Ingredient List ──────────────────────────────────────────────────────────────────────────
class IngredientList(QWidget):
    """A list widget for displaying recipe ingredients with amounts and names."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(LayoutConstants.INGREDIENT_LIST_SPACING)

    def setIngredients(self, ingredient_details: Iterable):
        """Set the ingredients to display."""
        # Clear existing ingredients
        self._clearIngredients()

        # Add new ingredients
        for detail in ingredient_details:
            self._addIngredientItem(detail)

    def _clearIngredients(self):
        """Clear all ingredient items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addIngredientItem(self, detail):
        """Add a single ingredient item to the list."""
        # Create ingredient row widget with utility
        item_widget = QWidget()
        apply_object_name_pattern(item_widget, "Ingredient", "Item")

        # Create standardized grid layout
        item_layout = create_form_grid_layout(
            item_widget, margins=(0, 0, 0, 0), spacing=LayoutConstants.INGREDIENT_GRID_SPACING
        )
        item_layout.setVerticalSpacing(0)

        # Set column stretch: quantity (fixed), unit (fixed), name (expanding)
        item_layout.setColumnStretch(0, 0)  # Quantity column - fixed width
        item_layout.setColumnStretch(1, 0)  # Unit column - fixed width
        item_layout.setColumnStretch(2, 1)  # Name column - expanding

        # Get formatted ingredient details using new DTO properties
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""

        # Create labels with consistent patterns
        qty_label = self._create_ingredient_label(
            formatted_qty, "Ingredient", "Quantity",
            Qt.AlignRight | Qt.AlignVCenter, fixed_width=LayoutConstants.INGREDIENT_QTY_WIDTH
        )
        unit_label = self._create_ingredient_label(
            abbreviated_unit, "Ingredient", "Unit",
            Qt.AlignLeft | Qt.AlignVCenter, fixed_width=LayoutConstants.INGREDIENT_UNIT_WIDTH
        )
        name_label = self._create_ingredient_label(
            ingredient_name, "Ingredient", "Name",
            Qt.AlignLeft | Qt.AlignVCenter
        )

        # Add to grid: row 0, columns 0, 1, 2
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)

        # Add to main layout
        self.layout.addWidget(item_widget)

    def _create_ingredient_label(self, text: str, context: str, label_type: str,
                               alignment: Qt.AlignmentFlag, fixed_width: int = None) -> QLabel:
        """Create a standardized ingredient label with consistent styling."""
        label = QLabel(text)
        apply_object_name_pattern(label, context, label_type)
        label.setAlignment(alignment)
        if fixed_width:
            label.setFixedWidth(fixed_width)
        return label


# ── Directions List ──────────────────────────────────────────────────────────────────────────
class DirectionsList(QWidget):
    """A numbered list widget for displaying recipe directions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DirectionsList")

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(LayoutConstants.DIRECTIONS_LIST_SPACING)

    def setDirections(self, directions: str):
        """Set the directions to display."""
        # Clear existing directions
        self._clearDirections()

        # Parse directions using text sanitization utility
        sanitized_directions = sanitize_multiline_input(directions) if directions else ""
        steps = sanitized_directions.splitlines() if sanitized_directions else []

        if not steps:
            empty_label = QLabel("No directions available.")
            empty_label.setObjectName("EmptyDirections")
            empty_label.setWordWrap(True)
            self.layout.addWidget(empty_label)
        else:
            # Add numbered steps
            for i, step in enumerate(steps, start=1):
                self._addDirectionItem(i, step)

    def _clearDirections(self):
        """Clear all direction items from the layout."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _addDirectionItem(self, number: int, text: str):
        """Add a single direction item to the list."""
        # Create direction row widget with utility
        item_widget = QWidget()
        apply_object_name_pattern(item_widget, "Direction", "Item")

        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(LayoutConstants.DIRECTIONS_ITEM_SPACING)

        # Create standardized labels
        number_label = self._create_direction_label(
            f"{number}.", "Direction", "Number",
            Qt.AlignLeft | Qt.AlignTop, min_width=LayoutConstants.DIRECTIONS_NUMBER_WIDTH
        )
        text_label = self._create_direction_label(
            text, "Direction", "Text",
            Qt.AlignLeft | Qt.AlignTop, word_wrap=True
        )

        # Add to layout
        item_layout.addWidget(number_label)
        item_layout.addWidget(text_label, 1)

        # Add to main layout
        self.layout.addWidget(item_widget)

    def _create_direction_label(self, text: str, context: str, label_type: str,
                              alignment: Qt.AlignmentFlag, min_width: int = None,
                              word_wrap: bool = False) -> QLabel:
        """Create a standardized direction label with consistent styling."""
        label = QLabel(text)
        apply_object_name_pattern(label, context, label_type)
        label.setAlignment(alignment)
        if min_width:
            label.setMinimumWidth(min_width)
        if word_wrap:
            label.setWordWrap(True)
        return label


# ── FullRecipe View ─────────────────────────────────────────────────────────────────────────
@RouteRegistry.register("full_recipe", ViewType.SUB, cache_instance=False)
class FullRecipe(QWidget, NavigableView):
    """Full recipe detail view (visual-only, no editing/upload yet)."""

    back_clicked = Signal()

    def __init__(self, recipe: Recipe = None, navigation_service=None, parent: QWidget | None = None) -> None:
        QWidget.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)
        self.recipe = recipe

        # Register this view for component-scoped QSS.
        Theme.register_widget(self, Qss.FULL_RECIPE)

        self.setObjectName("FullRecipe")
        self._cached_recipe_data = None
        
        # Only build UI if recipe is provided directly (legacy mode)
        if self.recipe:
            self._build_ui()
    
    def on_enter(self, params: dict):
        """Handle navigation with recipe parameters."""
        recipe_id = params.get('recipe_id')
        if recipe_id:
            # Load recipe from service
            from app.core.services.recipe_service import RecipeService
            recipe_service = RecipeService()
            self.recipe = recipe_service.get_by_id(int(recipe_id))
            
            if self.recipe:
                # Clear cached data and rebuild UI
                self._cached_recipe_data = None
                self._build_ui()
            else:
                DebugLogger().log(f"Recipe {recipe_id} not found", "error")
        elif self.recipe:
            # Recipe already provided, just rebuild UI if needed
            self._build_ui()

    @property
    def recipe_data(self) -> dict:
        """Cache frequently accessed recipe attributes."""
        if self._cached_recipe_data is None:
            self._cached_recipe_data = self._extract_recipe_display_data()
        return self._cached_recipe_data

    def _extract_recipe_display_data(self) -> dict:
        """Extract and format recipe data with consistent fallbacks and sanitization."""
        return {
            "title": sanitize_form_input(getattr(self.recipe, "recipe_name", "")) or "Untitled Recipe",
            "recipe_name": sanitize_form_input(getattr(self.recipe, "recipe_name", "")),
            "meal_type": getattr(self.recipe, "meal_type", None) or "Dinner",
            "category": getattr(self.recipe, "recipe_category", None) or "Main Course",
            "diet_pref": getattr(self.recipe, "diet_pref", None) or "High-Protein",
            "total_time": str(getattr(self.recipe, "total_time", "")) or "2 hours 30 mins",
            "servings": str(getattr(self.recipe, "servings", "")) or "6",
            "directions": getattr(self.recipe, "directions", "") or "",
            "notes": getattr(self.recipe, "notes", None),
            "banner_image_path": getattr(self.recipe, "banner_image_path", None),
            "recipe_id": getattr(self.recipe, "id", None),
            "ingredient_details": getattr(self.recipe, "get_ingredient_details", lambda: [])()
        }

    # ── Layout ───────────────────────────────────────────────────────────────────────────────
    def _make_back_button(self):
        """Create a simple back button using custom Button class."""
        w = QWidget(self)
        w.setObjectName("BackBar")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        btn = Button("Back", Type.SECONDARY, Name.BACK)
        btn.setObjectName("BackButton")
        btn.clicked.connect(self._handle_back_clicked)

        row.addWidget(btn, 0, Qt.AlignLeft)
        row.addStretch(1)
        return w

    def _build_ui(self) -> None:
        """Build the main UI matching the mock design."""

        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

        self._create_header_section()
        self._create_banner_section()
        self._create_info_section()
        self._create_content_sections()

        # Bottom spacer
        self.scroll_layout.addStretch()

    def _create_header_section(self) -> None:
        """Create back button, title, and tags section."""
        # Back Button
        # TODO: Implement sticky back button that remains visible during scrolling
        # Requirements: Fixed position overlay, semi-transparent background, proper z-index
        back_bar = self._make_back_button()
        self.scroll_layout.addWidget(back_bar)

        # Title Section
        title = QLabel(self.recipe_data["title"])
        title.setObjectName("RecipeTitle")
        title.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(title)

        # Recipe Tags Row
        tags_container = QWidget()
        tags_container.setObjectName("RecipeTagsContainer")
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.addStretch()

        # Add recipe tags using centralized data
        tags_layout.addWidget(RecipeTag(Icon.MEAL_TYPE, self.recipe_data["meal_type"]))
        tags_layout.addSpacing(LayoutConstants.TAG_SPACING)
        tags_layout.addWidget(RecipeTag(Icon.CATEGORY, self.recipe_data["category"]))
        tags_layout.addSpacing(LayoutConstants.TAG_SPACING)
        tags_layout.addWidget(RecipeTag(Icon.DIET_PREF, self.recipe_data["diet_pref"]))
        tags_layout.addStretch()
        self.scroll_layout.addWidget(tags_container)

    def _create_banner_section(self) -> None:
        """Create and configure recipe banner with image handling."""
        self.recipe_banner = RecipeBanner()

        # Configure banner with recipe data
        if self.recipe_data["recipe_name"]:
            self.recipe_banner.set_recipe_name(self.recipe_data["recipe_name"])

        # Show existing banner image if recipe has one
        if self.recipe_data["banner_image_path"]:
            if Path(self.recipe_data["banner_image_path"]).exists():
                self.recipe_banner.set_banner_image_path(self.recipe_data["banner_image_path"])
                DebugLogger().log(f"Loaded recipe banner: {self.recipe_data['banner_image_path']}", "info")
            else:
                DebugLogger().log(f"Recipe banner path does not exist: {self.recipe_data['banner_image_path']}", "warning")

        # Connect signals using batch connection utility
        signal_connections = [
            (self.recipe_banner.generate_image_requested, self._on_generate_banner_requested),
            (self.recipe_banner.image_clicked, self._on_image_clicked)
        ]
        batch_connect_signals(signal_connections)

        # Connect AI service signals for async operations
        # TODO: enable after aI gen service is fixed
        #self.ai_service.generation_finished.connect(self._on_generation_finished)
        #self.ai_service.generation_failed.connect(self._on_generation_failed)

        self.scroll_layout.addWidget(self.recipe_banner)

    def _create_info_section(self) -> None:
        """Create recipe info cards section."""
        # Info Cards Container
        info_container = Card(content_layout="hbox")
        info_container.setObjectName("InfoContainer")
        info_container.setProperty("tag", "Container")
        info_container.expandWidth(True)
        info_container.setContentsMargins(*LayoutConstants.INFO_CONTAINER_MARGINS)
        info_container.setSpacing(LayoutConstants.INFO_CONTAINER_SPACING)

        # Create info card using centralized recipe data
        info_card = RecipeInfoCard(
            show_cards=["time", "servings", "category", "dietary"])
        info_card.setRecipe(self.recipe)
        info_container.addWidget(info_card)

        self.scroll_layout.addWidget(info_container)

    def _create_content_sections(self) -> None:
        """Create ingredients, directions, and notes sections using two-column layout."""
        # Left Column: Ingredients
        ingredients_list = IngredientList()
        ingredients_list.setIngredients(self.recipe_data["ingredient_details"])
        ingredients_card = self._create_recipe_section_card("Ingredients", Icon.INGREDIENTS, ingredients_list)

        # Right Column: Directions + Notes
        directions_list = DirectionsList()
        directions_list.setDirections(self.recipe_data["directions"])
        directions_card = self._create_recipe_section_card("Directions", Icon.DIRECTIONS, directions_list)

        right_column_widgets = [directions_card]

        # Add notes if present
        if self.recipe_data["notes"]:
            notes_text = QLabel(sanitize_form_input(self.recipe_data["notes"]))
            notes_text.setObjectName("NotesText")
            notes_text.setWordWrap(True)
            notes_card = self._create_recipe_section_card("Notes", Icon.NOTES, notes_text)
            right_column_widgets.append(notes_card)

        # Create two-column layout using utility (1/3 left, 2/3 right)
        content_layout = create_two_column_layout(
            left_widgets=[ingredients_card],
            right_widgets=right_column_widgets,
            left_weight=1,
            right_weight=2,
            spacing=LayoutConstants.CONTENT_SECTION_SPACING,
            alignment=Qt.AlignTop
        )

        # Add the content layout to main page layout
        self.scroll_layout.addLayout(content_layout)

    def _create_section_header(self, icon: Icon, title: str) -> QWidget:
        """Create a section header with icon and title."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(LayoutConstants.SECTION_HEADER_SPACING)

        # Icon
        header_icon = AppIcon(icon)
        header_icon.setFixedSize(QSize(*LayoutConstants.SECTION_ICON_SIZE))
        header_icon.setObjectName("SectionIcon")

        # Title
        header_title = QLabel(title)
        header_title.setObjectName("SectionHeader")

        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        return header_widget

    def _handle_banner_path_result(self, banner_path: str, recipe_name: str) -> bool:
        """Handle banner path validation and database update with consistent error handling."""
        if not banner_path:
            return False

        if Path(banner_path).exists():
            self.recipe_banner.set_banner_image_path(banner_path)
            DebugLogger().log(f"Banner image loaded for '{recipe_name}': {Path(banner_path).name}", "info")

            # Save to database if recipe has ID
            if self.recipe_data["recipe_id"]:
                try:
                    from app.core.services.recipe_service import RecipeService
                    recipe_service = RecipeService()
                    updated_recipe = recipe_service.update_recipe_banner_image_path(
                        self.recipe_data["recipe_id"], banner_path
                    )
                    if updated_recipe:
                        # Update the local recipe object
                        self.recipe.banner_image_path = banner_path
                        DebugLogger().log(f"Updated recipe {self.recipe_data['recipe_id']} with banner image path", "info")
                except Exception as e:
                    DebugLogger().log(f"Failed to save banner image path to database: {e}", "error")
            return True
        else:
            DebugLogger().log(f"Generated banner image not found: {banner_path}", "warning")
            return False

    def _reset_banner_to_placeholder(self):
        """Reset banner to placeholder state with consistent handling."""
        self.recipe_banner.show_placeholder_state()
        self.recipe_banner.reset_banner_button()

    def _create_recipe_section_card(self, title: str, icon: Icon, content_widget: QWidget = None) -> Card:
        """Create standardized recipe section card with consistent configuration."""
        card = Card(self.scroll_content, card_type="Primary")
        card.setHeader(title, icon)
        card.headerIcon.setSize(*LayoutConstants.CARD_ICON_SIZE)
        card.headerIcon.setColor("primary")
        card.setContentMargins(*LayoutConstants.CARD_MARGINS)
        card.setSpacing(LayoutConstants.CARD_SPACING)
        card.expandWidth(True)

        if content_widget:
            # Set standardized size policy for content widgets
            content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            card.addWidget(content_widget)

        return card

    def _on_generate_banner_requested(self, recipe_name: str):
        """Handle AI banner generation request using async generation."""
        if not self.ai_service.is_available():
            # TODO: Show toast notification for service unavailable
            print(f"AI Image Generation service not available")
            self.recipe_banner.reset_banner_button()
            return

        # Start async banner generation - UI will not block
        self.ai_service.generate_banner_image_async(recipe_name)

    def _on_generation_finished(self, recipe_name: str, result):
        """Handle successful AI banner generation."""
        banner_path = None

        # Extract banner path from different result formats
        if isinstance(result, str):
            banner_path = result
        elif result and hasattr(result, 'banner_path'):
            banner_path = str(result.banner_path)

        # Handle the banner path with consolidated error handling
        if banner_path and self._handle_banner_path_result(banner_path, recipe_name):
            # Success - banner was set successfully
            pass
        else:
            # Failed to load banner or no valid result
            self._reset_banner_to_placeholder()
            if not banner_path:
                DebugLogger().log(f"AI generation completed but no valid result for '{recipe_name}'", "warning")

    def _on_generation_failed(self, recipe_name: str, error_message: str):
        """Handle AI banner generation failure."""
        self._reset_banner_to_placeholder()
        # TODO: Show toast notification for generation failure
        DebugLogger().log(f"Failed to generate banner image for '{recipe_name}': {error_message}", "error")

    def _on_image_clicked(self):
        """Handle image click for full preview."""
        # TODO: Show full-size image preview dialog
        DebugLogger().log("Recipe banner image clicked for full preview", "debug")

    def _handle_back_clicked(self):
        """Handle back button click using NavigationService or fallback to signal."""
        if self.navigation_service:
            # Use NavigationService to go back
            if not self.navigation_service.go_back():
                # Fallback to view_recipes if no history
                self.navigation_service.navigate_to("view_recipes")
        else:
            # Fallback to original signal-based approach
            self.back_clicked.emit()



