"""app/ui/components/images/recipe_image.py

RecipeImage component - Unified AI-powered image generation for recipes.
Supports both banner mode (FullRecipe) and gallery mode (AddRecipe).
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, 
                               QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget)

from app.style import Qss, Theme, Type
from app.style.icon import AppIcon
from app.style.icon.config import Icon, Name
from app.ui.components.layout.card import BaseCard
from app.ui.components.widgets import Button, RoundedImage


class RecipeImage(BaseCard):
    """Unified AI-powered image generation component for recipes.
    
    Supports two modes:
    - banner: Single large image display (FullRecipe view)
    - gallery: Multiple thumbnail selection (AddRecipe view)
    """

    # Signals
    generate_image_requested = Signal(str)  # emits recipe name for generation
    image_clicked = Signal()  # emits when image is clicked for preview
    image_selected = Signal(str)  # emits selected image path (gallery mode)

    def __init__(self, parent=None, mode="banner", multi_generation=True):
        """Initialize RecipeImage component.
        
        Args:
            parent: Parent widget
            mode: "banner" for single large image, "gallery" for thumbnail grid
            multi_generation: Generate multiple images vs single image
        """
        super().__init__(parent)
        
        # Configuration
        self.mode = mode
        self.multi_generation = multi_generation
        
        # Setup object names and properties
        if mode == "banner":
            self.setObjectName("RecipeBanner") 
            self.setProperty("tag", "RecipeBanner")
            Theme.register_widget(self, Qss.RECIPE_BANNER)
        else:
            self.setObjectName("RecipeGallery")
            self.setProperty("tag", "RecipeGallery") 
            Theme.register_widget(self, Qss.RECIPE_BANNER)  # Use same styling for now

        # Configure dimensions based on mode
        self._configure_dimensions()

        # State
        self.recipe_name: Optional[str] = None
        self.current_image_path: Optional[str] = None
        self.generated_images: List[str] = []
        self.selected_image_path: Optional[str] = None

        self._build_ui()

    def _configure_dimensions(self):
        """Configure widget dimensions based on mode."""
        if self.mode == "banner":
            # Banner mode: ~3:2 aspect ratio for wide display
            self.setFixedHeight(400)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            # Gallery mode: Fixed height to prevent layout shifts
            self.setFixedHeight(350)  # Fixed height to prevent shrinking during state changes
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def _build_ui(self):
        """Build the UI with stacked widget for different states."""
        # Stacked widget to switch between placeholder and image states
        self.stack = QStackedWidget()
        
        # Use BaseCard's addWidget method instead of setting layout directly
        self.addWidget(self.stack)

        # Create states based on mode
        self._create_placeholder_state()
        self._create_generating_state()
        
        if self.mode == "banner":
            self._create_banner_image_state()
        else:
            self._create_gallery_state()

        # Start with placeholder
        self.stack.setCurrentIndex(0)

    def _create_placeholder_state(self):
        """Create placeholder state with generate button."""
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        placeholder_layout.setContentsMargins(40, 40, 40, 40)

        # Icon - adjust size based on mode
        icon_size = 80 if self.mode == "banner" else 60
        icon = AppIcon(Icon.PHOTO)
        icon.setSize(icon_size, icon_size)
        icon.setObjectName("RecipePlaceholderIcon")

        # Main text - mode-specific
        if self.mode == "banner":
            main_text = QLabel("No Recipe Image")
            button_text = "Generate AI Image"
            sub_text = QLabel("AI-generated banner image")
        else:
            main_text = QLabel("No Recipe Images")
            button_text = "Generate AI Images" 
            sub_text = QLabel("AI will generate multiple images\nClick any image to select it")

        main_text.setObjectName("RecipePlaceholderText")
        main_text.setAlignment(Qt.AlignCenter)

        # Generate button - disabled by default
        self.generate_button = Button(button_text, Type.PRIMARY, Name.SPARKLES)
        self.generate_button.setObjectName("GenerateImageButton")
        self.generate_button.setEnabled(False)  # Disabled until recipe name is set
        self.generate_button.clicked.connect(self._on_generate_clicked)

        # Sub text
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

        # Loading icon (spinning)
        loading_icon = AppIcon(Icon.SPINNER)
        loading_icon.setSize(60, 60)

        # Loading text - mode-specific
        if self.mode == "banner":
            loading_text = QLabel("Generating AI Image...")
        else:
            loading_text = QLabel("Generating AI Images...")
            
        loading_text.setObjectName("GeneratingText")
        loading_text.setAlignment(Qt.AlignCenter)

        generating_layout.addWidget(loading_icon, 0, Qt.AlignCenter)
        generating_layout.addSpacing(20)
        generating_layout.addWidget(loading_text)

        self.stack.addWidget(generating_widget)  # Index 1

    def _create_banner_image_state(self):
        """Create banner image display state for single image."""
        self.image_widget = QWidget()
        image_layout = QVBoxLayout(self.image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Image display will be created when needed
        self.image_display: Optional[RoundedImage] = None

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

    def _create_gallery_state(self):
        """Create gallery state for multiple image selection."""
        gallery_widget = QWidget()
        gallery_layout = QVBoxLayout(gallery_widget)
        gallery_layout.setContentsMargins(10, 10, 10, 10)
        gallery_layout.setSpacing(15)

        # Action buttons row at top
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Regenerate button
        self.regenerate_button = Button("Generate More", Type.SECONDARY, Name.REFRESH)
        self.regenerate_button.clicked.connect(self._on_generate_clicked)

        buttons_layout.addWidget(self.regenerate_button)
        buttons_layout.addStretch()

        gallery_layout.addWidget(buttons_widget)

        # Gallery label
        gallery_label = QLabel("Generated Images:")
        gallery_label.setObjectName("GalleryLabel")
        gallery_layout.addWidget(gallery_label)

        # Scroll area for thumbnails
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(300)

        # Grid container for thumbnails
        self.thumbnails_widget = QWidget()
        self.thumbnails_layout = QGridLayout(self.thumbnails_widget)
        self.thumbnails_layout.setSpacing(8)
        self.thumbnails_layout.setContentsMargins(5, 5, 5, 5)

        scroll_area.setWidget(self.thumbnails_widget)
        gallery_layout.addWidget(scroll_area)

        # Selected image info
        self.selection_info = QLabel("Click an image to select it")
        self.selection_info.setObjectName("SelectionInfo")
        self.selection_info.setAlignment(Qt.AlignCenter)
        gallery_layout.addWidget(self.selection_info)

        self.stack.addWidget(gallery_widget)  # Index 2

    def set_recipe_name(self, recipe_name: str):
        """Set the recipe name for AI generation."""
        self.recipe_name = recipe_name
        # Enable generate button if we have a recipe name
        if hasattr(self, 'generate_button'):
            self.generate_button.setEnabled(bool(recipe_name))

    def set_image_path(self, image_path: str):
        """Set and display an image from path (banner mode only)."""
        if self.mode != "banner":
            return
            
        if not Path(image_path).exists():
            return

        self.current_image_path = image_path

        # Create or update image display for banner mode
        if self.image_display:
            self.image_display.set_image_path(image_path)
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

    def set_generated_images(self, image_paths: List[str]):
        """Set the list of generated image paths and display thumbnails (gallery mode only)."""
        if self.mode != "gallery":
            return
            
        self.generated_images = image_paths
        self._populate_thumbnails()
        
        # Switch to gallery state
        self.stack.setCurrentIndex(2)

    def _populate_thumbnails(self):
        """Populate the thumbnail grid with generated images."""
        # Clear existing thumbnails
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add thumbnails in 2-column grid
        for i, image_path in enumerate(self.generated_images):
            if not Path(image_path).exists():
                continue

            # Create clickable thumbnail
            thumbnail = self._create_thumbnail(image_path)
            row = i // 2
            col = i % 2
            self.thumbnails_layout.addWidget(thumbnail, row, col)

    def _create_thumbnail(self, image_path: str) -> QWidget:
        """Create a clickable thumbnail widget."""
        container = QFrame()
        container.setObjectName("ThumbnailContainer")
        container.setCursor(Qt.PointingHandCursor)
        container.setProperty("selected", "false")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Thumbnail image (square for consistency)
        thumbnail_size = QSize(120, 120)
        thumbnail_image = RoundedImage(
            image_path=image_path,
            size=thumbnail_size,
            radii=8
        )
        thumbnail_image.setObjectName("ThumbnailImage")

        # Image filename label
        filename = Path(image_path).name
        filename_label = QLabel(filename[:15] + "..." if len(filename) > 15 else filename)
        filename_label.setObjectName("ThumbnailLabel")
        filename_label.setAlignment(Qt.AlignCenter)
        filename_label.setWordWrap(True)

        layout.addWidget(thumbnail_image)
        layout.addWidget(filename_label)

        # Make container clickable
        container.mousePressEvent = lambda e: self._on_thumbnail_clicked(image_path, container)

        return container

    def _on_thumbnail_clicked(self, image_path: str, container: QFrame):
        """Handle thumbnail click."""
        # Update selection visual state
        self._clear_selection_state()
        container.setProperty("selected", "true")
        container.style().polish(container)

        # Update selected image
        self.selected_image_path = image_path
        
        # Update info label
        filename = Path(image_path).name
        self.selection_info.setText(f"Selected: {filename}")

        # Emit signals
        self.image_selected.emit(image_path)

    def _clear_selection_state(self):
        """Clear visual selection state from all thumbnails."""
        for i in range(self.thumbnails_layout.count()):
            item = self.thumbnails_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.setProperty("selected", "false")
                widget.style().polish(widget)

    def show_generating_state(self):
        """Show the generating state."""
        self.stack.setCurrentIndex(1)

    def show_placeholder_state(self):
        """Show the placeholder state."""
        self.stack.setCurrentIndex(0)

    def clear_images(self):
        """Clear all images and return to placeholder state."""
        self.current_image_path = None
        self.generated_images.clear()
        self.selected_image_path = None
        
        if self.image_display:
            self.image_display.clear_image()
        
        # Reset generate button
        if hasattr(self, 'generate_button'):
            self.generate_button.setText("Generate AI Images" if self.mode == "gallery" else "Generate AI Image")
            self.generate_button.setEnabled(bool(self.recipe_name))
            
        self.show_placeholder_state()

    def get_selected_image_path(self) -> Optional[str]:
        """Get the currently selected image path."""
        if self.mode == "banner":
            return self.current_image_path
        else:
            return self.selected_image_path

    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self.recipe_name:
            # Immediately show generating state BEFORE emitting signal
            self.show_generating_state()
            
            # Emit the signal (this will trigger the actual generation)
            self.generate_image_requested.emit(self.recipe_name)

    def _on_view_clicked(self):
        """Handle view button click (banner mode only)."""
        self.image_clicked.emit()

    def reset_generate_button(self):
        """Reset generate button to normal state."""
        if hasattr(self, 'generate_button'):
            if self.mode == "gallery":
                self.generate_button.setText("Generate AI Images")
            else:
                self.generate_button.setText("Generate AI Image")
            self.generate_button.setEnabled(bool(self.recipe_name))
