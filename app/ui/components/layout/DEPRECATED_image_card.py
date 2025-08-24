"""app/ui/components/layout/image_card.py

ImageCard component for AI-generated recipe images.
Replaces manual upload with AI generation and thumbnail gallery display.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (QGridLayout, QLabel, QScrollArea, QVBoxLayout, 
                               QWidget, QFrame, QHBoxLayout)

from app.ui.components.layout.card import ActionCard
from app.ui.components.widgets import Button, RoundedImage
from app.style.icon.config import Name, Type


# ── ImageCard ────────────────────────────────────────────────────────────────────────────────
class ImageCard(ActionCard):
    """AI-powered image generation card for recipe images.

    Features:
    - AI image generation with "Generate Images" button
    - Thumbnail gallery display of generated images
    - Click to expand/preview functionality
    - Square (1:1) aspect ratio for recipe cards
    - Integrated with Card styling system
    """

    # Signals
    generate_images_requested = Signal(str)  # emits recipe name for AI generation
    image_selected = Signal(str)  # emits selected image path
    image_preview_requested = Signal(str)  # emits image path for full preview

    def __init__(self,
                 parent=None,
                 card_type: str = "Default"):
        """Initialize ImageCard for AI generation.

        Args:
            parent: Parent widget
            card_type: Card styling type
        """
        super().__init__(parent, card_type=card_type)

        # State
        self.recipe_name: Optional[str] = None
        self.generated_images: List[str] = []
        self.selected_image_path: Optional[str] = None

        # Set header
        self.setHeader("Recipe Images")
        
        self._build_ui()

    def _build_ui(self):
        """Build the UI components."""
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)

        # Generate button
        self.generate_button = Button("Generate Images", Type.PRIMARY, Name.SPARKLES)
        self.generate_button.setObjectName("GenerateImagesButton")
        self.generate_button.clicked.connect(self._on_generate_clicked)
        content_layout.addWidget(self.generate_button, 0, Qt.AlignCenter)

        # Instructions text
        instructions = QLabel("AI will generate multiple images\nClick any image to select it")
        instructions.setObjectName("InstructionsText")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        content_layout.addWidget(instructions)

        # Thumbnail gallery (initially hidden)
        self._create_thumbnail_gallery()
        content_layout.addWidget(self.gallery_frame)
        self.gallery_frame.hide()

        self.addWidget(content_widget)

    def _create_thumbnail_gallery(self):
        """Create the thumbnail gallery area."""
        self.gallery_frame = QFrame()
        self.gallery_frame.setObjectName("ThumbnailGallery")
        gallery_layout = QVBoxLayout(self.gallery_frame)
        gallery_layout.setContentsMargins(0, 0, 0, 0)
        gallery_layout.setSpacing(10)

        # Gallery label
        gallery_label = QLabel("Generated Images:")
        gallery_label.setObjectName("GalleryLabel")
        gallery_layout.addWidget(gallery_label)

        # Scroll area for thumbnails
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

    def set_recipe_name(self, recipe_name: str):
        """Set the recipe name for AI generation."""
        self.recipe_name = recipe_name
        self.generate_button.setEnabled(bool(recipe_name))

    def set_generated_images(self, image_paths: List[str]):
        """Set the list of generated image paths and display thumbnails."""
        self.generated_images = image_paths
        self._populate_thumbnails()
        
        if image_paths:
            self.gallery_frame.show()
        else:
            self.gallery_frame.hide()

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

        # Thumbnail image
        thumbnail_size = QSize(120, 120)
        thumbnail_image = RoundedImage(
            image_path=image_path,
            size=thumbnail_size,
            radii=8
        )
        thumbnail_image.setObjectName("ThumbnailImage")

        # Image filename label
        filename = Path(image_path).name
        filename_label = QLabel(filename[:20] + "..." if len(filename) > 20 else filename)
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

        # Double-click to preview (simplified as single click for now)
        self.image_preview_requested.emit(image_path)

    def _clear_selection_state(self):
        """Clear visual selection state from all thumbnails."""
        for i in range(self.thumbnails_layout.count()):
            item = self.thumbnails_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.setProperty("selected", "false")
                widget.style().polish(widget)

    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self.recipe_name:
            self.generate_button.setText("Generating...")
            self.generate_button.setEnabled(False)
            self.generate_images_requested.emit(self.recipe_name)

    def reset_generate_button(self):
        """Reset generate button to normal state."""
        self.generate_button.setText("Generate Images")
        self.generate_button.setEnabled(bool(self.recipe_name))

    def get_selected_image_path(self) -> Optional[str]:
        """Get the currently selected image path."""
        return self.selected_image_path

    def clear_images(self):
        """Clear all generated images and reset to initial state."""
        self.generated_images.clear()
        self.selected_image_path = None
        self.gallery_frame.hide()
        self.reset_generate_button()
        self.selection_info.setText("Click an image to select it")
