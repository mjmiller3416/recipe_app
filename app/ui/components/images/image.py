"""app/ui/components/images/recipe_image_standard.py

RecipeImage component - Standard recipe image generation and display.
Used in AddRecipes view for default recipe images.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Optional
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QSizePolicy, QVBoxLayout,
    QWidget, QLabel, QStackedWidget)

from app.core.utils.image_utils import img_validate_path
from app.style import Qss, Theme, Type
from app.style.icon.config import Icon, Name, Path as IconPath
from app.style.icon.icon import AppIcon
from app.ui.components.layout.card import BaseCard
from app.ui.components.widgets import Button, RoundedImage


# ── Base Image ───────────────────────────────────────────────────────────────────────────────
class BaseImage(BaseCard):
    """Base class for all recipe image components.

    Provides shared functionality including:
    - Image display management
    - Placeholder states
    - Loading/generating states
    - File path validation
    - Basic UI structure
    """

    # Shared signals
    image_clicked = Signal()  # emits when image is clicked for preview
    generate_image_requested = Signal(str)  # emits recipe name for generation

    def __init__(self, parent=None, image_type="default"):
        """Initialize BaseImage component.

        Args:
            parent: Parent widget
            image_type: Type identifier for this image component
        """
        super().__init__(parent)

        # Configuration
        self.image_type = image_type

        # State management
        self.recipe_name: Optional[str] = None
        self.current_image_path: Optional[str] = None
        self.is_generating: bool = False

        # UI components
        self.stack: Optional[QStackedWidget] = None
        self.image_display: Optional[RoundedImage] = None
        self.generate_button: Optional[Button] = None

        self._build_base_ui()

    def _build_base_ui(self):
        """Build the base UI structure with stacked widget."""
        # Create stacked widget for state management
        self.stack = QStackedWidget()
        self.addWidget(self.stack)

        # Create base states (subclasses will add more)
        self._create_placeholder_state()
        self._create_generating_state()

        # Start with placeholder
        self.stack.setCurrentIndex(0)

    def _create_placeholder_state(self):
        """Create placeholder state with generate button."""
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        placeholder_layout.setContentsMargins(40, 40, 40, 40)

        # Icon
        icon_size = self._get_icon_size()
        icon = AppIcon(Icon.PHOTO)
        icon.setSize(icon_size, icon_size)
        icon.setObjectName("RecipePlaceholderIcon")

        # Main text
        main_text = QLabel(self._get_placeholder_text())
        main_text.setObjectName("RecipePlaceholderText")
        main_text.setAlignment(Qt.AlignCenter)

        # Generate button
        self.generate_button = Button(
            self._get_button_text(),
            Type.PRIMARY,
            self._get_button_icon()
        )
        self.generate_button.setObjectName("GenerateImageButton")
        self.generate_button.setEnabled(False)  # Disabled until recipe name is set
        self.generate_button.clicked.connect(self._on_generate_clicked)

        # Sub text
        sub_text = QLabel(self._get_sub_text())
        sub_text.setObjectName("RecipeSubText")
        sub_text.setAlignment(Qt.AlignCenter)
        sub_text.setWordWrap(True)

        # Add to layout
        placeholder_layout.addWidget(icon, 0, Qt.AlignCenter)
        placeholder_layout.addSpacing(20)
        placeholder_layout.addWidget(main_text)
        placeholder_layout.addSpacing(10)
        placeholder_layout.addWidget(self.generate_button, 0, Qt.AlignCenter)
        placeholder_layout.addSpacing(10)
        placeholder_layout.addWidget(sub_text)

        self.stack.addWidget(placeholder_widget)  # Index 0

    def _create_generating_state(self):
        """Create generating state with loading indicator."""
        generating_widget = QWidget()
        generating_layout = QVBoxLayout(generating_widget)
        generating_layout.setAlignment(Qt.AlignCenter)

        # Loading icon
        loading_icon = AppIcon(Icon.SPINNER)
        loading_icon.setSize(60, 60)

        # Loading text
        loading_text = QLabel(self._get_loading_text())
        loading_text.setObjectName("GeneratingText")
        loading_text.setAlignment(Qt.AlignCenter)

        generating_layout.addWidget(loading_icon, 0, Qt.AlignCenter)
        generating_layout.addSpacing(20)
        generating_layout.addWidget(loading_text)

        self.stack.addWidget(generating_widget)  # Index 1

    # ── Abstract methods for subclasses to override ──

    def _get_icon_size(self) -> int:
        """Get the icon size for placeholder state."""
        return 60  # Default size, subclasses can override

    def _get_placeholder_text(self) -> str:
        """Get placeholder text."""
        return "No Image"

    def _get_button_text(self) -> str:
        """Get generate button text."""
        return "Generate AI Image"

    def _get_button_icon(self):
        """Get generate button icon."""
        from app.style.icon.config import Name
        return Name.SPARKLES

    def _get_sub_text(self) -> str:
        """Get subtext for placeholder."""
        return "Click to generate AI image"

    def _get_loading_text(self) -> str:
        """Get loading state text."""
        return "Generating AI Image..."

    # ── Public API ──

    def set_recipe_name(self, recipe_name: str):
        """Set the recipe name for AI generation."""
        self.recipe_name = recipe_name.strip() if recipe_name else None
        # Enable generate button if we have a recipe name
        if self.generate_button:
            self.generate_button.setEnabled(bool(self.recipe_name))

    def setImagePath(self, image_path: str):
        """Set and display an image from path."""
        if not img_validate_path(image_path):
            self.show_placeholder_state()
            return

        self.current_image_path = image_path
        self._display_image(image_path)

    def clearImage(self):
        """Clear current image and return to placeholder state."""
        self.current_image_path = None
        if self.image_display:
            self.image_display.clearImage()
        self.show_placeholder_state()

    def show_placeholder_state(self):
        """Show the placeholder state."""
        self.is_generating = False
        self.stack.setCurrentIndex(0)

    def show_generating_state(self):
        """Show the generating state."""
        self.is_generating = True
        self.stack.setCurrentIndex(1)

    def reset_generate_button(self):
        """Reset generate button to normal state."""
        if self.generate_button:
            self.generate_button.setText(self._get_button_text())
            self.generate_button.setEnabled(bool(self.recipe_name))

    def get_current_image_path(self) -> Optional[str]:
        """Get the currently displayed image path."""
        return self.current_image_path

    # ── Internal methods ──

    def _display_image(self, image_path: str):
        """Display an image - to be implemented by subclasses."""
        # Base implementation just sets the path
        # Subclasses should override to actually display the image
        self.current_image_path = image_path

    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self.recipe_name:
            # Show generating state immediately
            self.show_generating_state()
            # Emit signal for actual generation
            self.generate_image_requested.emit(self.recipe_name)

    def _validate_image_path(self, image_path: str) -> bool:
        """Validate that an image path exists and is readable."""
        return img_validate_path(image_path)


# ── Recipe Banner  ───────────────────────────────────────────────────────────────────────────
class RecipeBanner(BaseImage):
    """Banner recipe image component with single large display.

    Features:
    - Single banner image generation
    - Large banner display
    - View/regenerate functionality
    - Used in FullRecipe view
    """

    def __init__(self, parent=None):
        """Initialize RecipeBanner component."""
        # Initialize base with banner image type
        super().__init__(parent, image_type="banner")

        # Setup object names and properties
        self.setObjectName("RecipeBanner")
        self.setProperty("tag", "RecipeBanner")
        Theme.register_widget(self, Qss.RECIPE_BANNER)

        # Banner UI components
        self.image_widget: Optional[QWidget] = None
        self.regenerate_button: Optional[Button] = None
        self.view_button: Optional[Button] = None

        # Configure dimensions and create banner display
        self._configure_dimensions()
        self._create_banner_image_state()

    def _configure_dimensions(self):
        """Configure widget dimensions for banner mode."""
        # Banner mode: ~3:2 aspect ratio for wide display
        self.setFixedHeight(400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ── Override base methods for banner-specific behavior ──

    def _get_icon_size(self) -> int:
        return 80  # Larger icon for banner mode

    def _get_placeholder_text(self) -> str:
        return "No Recipe Banner"

    def _get_button_text(self) -> str:
        return "Generate AI Banner"

    def _get_sub_text(self) -> str:
        return "AI-generated banner image for recipe"

    def _get_loading_text(self) -> str:
        return "Generating AI Banner..."

    def _display_image(self, image_path: str):
        """Display image in banner mode."""
        if not img_validate_path(image_path):
            self.show_placeholder_state()
            return

        self.current_image_path = image_path

        # Create or update image display
        if self.image_display:
            self.image_display.setImagePath(image_path)
        else:
            # Calculate size for banner display
            target_height = 350  # Leave room for buttons
            self.image_display = RoundedImage(
                image_path=image_path,
                size=QSize(600, target_height),  # Will maintain aspect ratio
                radii=12
            )
            self.image_display.setObjectName("RecipeBannerImage")
            self.image_display.setCursor(Qt.PointingHandCursor)

            # Make image clickable
            self.image_display.mousePressEvent = lambda e: self.image_clicked.emit()

            # Insert at top of layout (before buttons)
            self.image_widget.layout().insertWidget(0, self.image_display)

        # Switch to image state
        self.stack.setCurrentIndex(2)

    # ── Banner-specific methods ──

    def _create_banner_image_state(self):
        """Create banner image display state for single image."""
        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Image display will be created when needed
        # (self.image_display created in _display_image)

        # Action buttons row
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(10, 5, 10, 5)

        # Regenerate button
        self.regenerate_button = Button("Regenerate", Type.SECONDARY, Name.REFRESH)
        self.regenerate_button.clicked.connect(self._on_generate_clicked)

        # View full size button
        self.view_button = Button("View Full Size", Type.SECONDARY, Name.EXPAND)
        self.view_button.clicked.connect(self._on_view_clicked)

        buttons_layout.addWidget(self.regenerate_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.view_button)

        image_layout.addWidget(buttons_widget)

        self.stack.addWidget(self.image_widget)  # Index 2

    def _on_view_clicked(self):
        """Handle view button click."""
        self.image_clicked.emit()

    def set_banner_image_path(self, image_path: str):
        """Set and display a banner image from path."""
        self.setImagePath(image_path)  # Use base class method

    def get_banner_image_path(self) -> Optional[str]:
        """Get the currently displayed banner image path."""
        return self.get_current_image_path()

    def clear_banner_image(self):
        """Clear banner image and return to placeholder state."""
        self.clearImage()  # Use base class method

    def reset_banner_button(self):
        """Reset banner generate button to normal state."""
        self.reset_generate_button()  # Use base class method


# ── Recipe Image ─────────────────────────────────────────────────────────────────────────────
class RecipeImage(BaseImage):
    """Default recipe image component with single image display.

    Features:
    - Single default image generation
    - Default image display with regenerate/view options
    - Used in AddRecipes view
    """

    # Additional signals specific to standard images
    image_selected = Signal(str)  # emits selected image path

    def __init__(self, parent=None):
        """Initialize RecipeImage component.

        Args:
            parent: Parent widget
        """
        # Initialize base with default image type
        super().__init__(parent, image_type="default")

        # Setup object names and properties
        self.setObjectName("RecipeImage")
        self.setProperty("tag", "RecipeImage")
        Theme.register_widget(self, Qss.RECIPE_BANNER)  # Use same styling

        # Default image UI components
        self.image_widget: Optional[QWidget] = None
        self.regenerate_button: Optional[Button] = None
        self.view_button: Optional[Button] = None

        # Configure dimensions and create image display
        self._configure_dimensions()
        self._create_image_display_state()

    def _configure_dimensions(self):
        """Configure widget dimensions for default image mode."""
        # Default image mode: Fixed height similar to banner but smaller
        self.setFixedHeight(300)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    # ── Override base methods for default image behavior ──

    def _get_placeholder_text(self) -> str:
        return "No Recipe Image"

    def _get_button_text(self) -> str:
        return "Generate AI Image"

    def _get_sub_text(self) -> str:
        return "AI will generate a default recipe image"

    def _get_loading_text(self) -> str:
        return "Generating AI Image..."

    def _display_image(self, image_path: str):
        """Display image in default mode."""
        if not img_validate_path(image_path):
            self.show_placeholder_state()
            return

        self.current_image_path = image_path

        # Create or update image display
        if self.image_display:
            self.image_display.setImagePath(image_path)
        else:
            # Calculate size for default display
            target_height = 250  # Leave room for buttons
            self.image_display = RoundedImage(
                image_path=image_path,
                size=QSize(400, target_height),  # Will maintain aspect ratio
                radii=12
            )
            self.image_display.setObjectName("RecipeDefaultImage")
            self.image_display.setCursor(Qt.PointingHandCursor)

            # Make image clickable
            self.image_display.mousePressEvent = lambda e: self.image_clicked.emit()

            # Insert at top of layout (before buttons)
            self.image_widget.layout().insertWidget(0, self.image_display)

        # Switch to image state
        self.stack.setCurrentIndex(2)

    # ── Default image methods ──

    def _create_image_display_state(self):
        """Create default image display state for single image."""
        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Image display will be created when needed
        # (self.image_display created in _display_image)

        # Action buttons row
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(10, 5, 10, 5)

        # Regenerate button
        self.regenerate_button = Button("Regenerate", Type.SECONDARY, Name.REFRESH)
        self.regenerate_button.clicked.connect(self._on_generate_clicked)

        # View full size button
        self.view_button = Button("View Full Size", Type.SECONDARY, Name.EXPAND)
        self.view_button.clicked.connect(self._on_view_clicked)

        buttons_layout.addWidget(self.regenerate_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.view_button)

        image_layout.addWidget(buttons_widget)

        self.stack.addWidget(self.image_widget)  # Index 2

    def _on_view_clicked(self):
        """Handle view button click."""
        self.image_clicked.emit()

    def set_default_image_path(self, image_path: str):
        """Set and display a default image from path."""
        self.setImagePath(image_path)  # Use base class method

    def get_default_image_path(self) -> Optional[str]:
        """Get the currently displayed default image path."""
        result = self.get_current_image_path()

        from dev_tools.debug_logger import DebugLogger
        DebugLogger.log(f"[RecipeImage] get_default_image_path() returning: '{result}'", "info")
        return result

    def clear_default_image(self):
        """Clear default image and return to placeholder state."""
        self.clearImage()  # Use base class method

    def reset_default_button(self):
        """Reset default generate button to normal state."""
        self.reset_generate_button()  # Use base class method
