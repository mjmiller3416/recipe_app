"""app/ui/components/layout/image_card.py

ImageCard component for displaying recipe images.
Pure display component without upload logic - handles image display only.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.components.layout.card import ActionCard
from app.ui.components.widgets import RoundedImage

# ── ImageCard ────────────────────────────────────────────────────────────────────────────────
class ImageCard(ActionCard):
    """Pure image display card component for recipe images.

    Features:
    - Display images with configurable aspect ratios
    - Square mode for thumbnails (AddRecipes)
    - Banner mode for recipe headers (FullRecipe)
    - Placeholder when no image is set
    - Integrated with Card styling system
    """

    image_changed = Signal(str)  # emits when image is set/changed

    def __init__(self,
                 parent=None,
                 aspect_ratio: str = "square",  # "square" or "banner"
                 card_type: str = "Default"):
        """Initialize ImageCard.

        Args:
            parent: Parent widget
            aspect_ratio: "square" (1:1) or "banner" (2:1)
            card_type: Card styling type
        """
        super().__init__(parent, card_type=card_type)

        self.aspect_ratio = aspect_ratio
        self.image_path: Optional[str] = None

        # Calculate dimensions based on aspect ratio
        self._calculate_dimensions()

        # Set appropriate header
        if aspect_ratio == "banner":
            self.setHeader("Recipe Photo")
        else:
            self.setHeader("Recipe Image")

        self._build_ui()

    def _calculate_dimensions(self):
        """Calculate widget dimensions based on aspect ratio."""
        if self.aspect_ratio == "banner":
            self.image_width = 400
            self.image_height = 200  # 2:1 ratio
        else:  # square
            self.image_width = 200
            self.image_height = 200  # 1:1 ratio

    def _build_ui(self):
        """Build the UI components."""
        # Container widget for the image area
        self.image_container = QWidget()
        self.image_container.setObjectName("ImageContainer")
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set fixed size for layout stability
        self.image_container.setFixedSize(self.image_width, self.image_height)

        # Initially show placeholder
        self._show_placeholder()

        # Add to card
        self.addWidget(self.image_container)

    def _show_placeholder(self):
        """Show placeholder when no image is set."""
        # Clear existing content
        self._clear_container()

        # Create placeholder
        self.placeholder_label = QLabel("No Image")
        self.placeholder_label.setObjectName("ImagePlaceholder")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet(f"""
            QLabel#ImagePlaceholder {{
                color: #666;
                font-style: italic;
                border: 2px dashed #ccc;
                border-radius: 8px;
                min-width: {self.image_width - 20}px;
                min-height: {self.image_height - 20}px;
            }}
        """)

        layout = self.image_container.layout()
        layout.addWidget(self.placeholder_label)

    def _show_image(self, image_path: str):
        """Display the image."""
        # Clear existing content
        self._clear_container()

        # Create RoundedImage
        image_size = QSize(self.image_width, self.image_height)
        radii = 15 if self.aspect_ratio == "square" else 12

        self.image_display = RoundedImage(
            image_path=image_path,
            size=image_size,
            radii=radii
        )
        self.image_display.setObjectName("RecipeImageDisplay")

        layout = self.image_container.layout()
        layout.addWidget(self.image_display)

    def _clear_container(self):
        """Clear all widgets from the image container."""
        layout = self.image_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_image_path(self, image_path: str):
        """Set image path and display the image.

        Args:
            image_path: Path to the image file
        """
        if image_path and Path(image_path).exists():
            self.image_path = image_path
            self._show_image(image_path)
            self.image_changed.emit(image_path)
        else:
            self.clear_image()

    def get_image_path(self) -> Optional[str]:
        """Get the current image path.

        Returns:
            Current image path or None if no image is set
        """
        return self.image_path

    def clear_image(self):
        """Clear the current image and show placeholder."""
        self.image_path = None
        self._show_placeholder()

    def set_aspect_ratio(self, aspect_ratio: str):
        """Change the aspect ratio of the image card.

        Args:
            aspect_ratio: "square" or "banner"
        """
        if aspect_ratio != self.aspect_ratio:
            self.aspect_ratio = aspect_ratio
            self._calculate_dimensions()

            # Update container size
            self.image_container.setFixedSize(self.image_width, self.image_height)

            # Refresh display
            if self.image_path:
                self._show_image(self.image_path)
            else:
                self._show_placeholder()
