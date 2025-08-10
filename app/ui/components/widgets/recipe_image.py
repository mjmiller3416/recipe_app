"""app/ui/components/widgets/recipe_image.py

RecipeImage component - A recipe banner image with fixed aspect ratio.
Shows a styled placeholder when no image is uploaded.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap

from app.style import Theme, Qss
from app.style.icon import AppIcon
from app.style.icon.config import Icon


class RecipeImage(QFrame):
    """Recipe banner image component with fixed 2:1 aspect ratio (1200x600)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeBanner")
        self.setProperty("tag", "RecipeBanner")

        # register for component-specific styling
        Theme.register_widget(self, Qss.RECIPE_BANNER)

        # Fixed aspect ratio (2:1 - 1200x600)
        self.setFixedHeight(600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # Placeholder content
        self._create_placeholder()

    def _create_placeholder(self):
        """Create placeholder content for when no banner image is uploaded."""
        # Icon
        self.placeholder_icon = AppIcon(Icon.PHOTO)
        self.placeholder_icon.setSize(120, 120)
        self.placeholder_icon.setObjectName("RecipeBannerPlaceholderIcon")

        # Text
        self.placeholder_text = QLabel("No image uploaded")
        self.placeholder_text.setObjectName("RecipeBannerPlaceholderText")
        self.placeholder_text.setAlignment(Qt.AlignCenter)

        # Dimensions text
        self.dimensions_text = QLabel("1200 × 600")
        self.dimensions_text.setObjectName("RecipeBannerDimensionsText")
        self.dimensions_text.setAlignment(Qt.AlignCenter)

        # Add to layout
        self.layout().addWidget(self.placeholder_icon, 0, Qt.AlignCenter)
        self.layout().addSpacing(40)
        self.layout().addWidget(self.placeholder_text)
        self.layout().addWidget(self.dimensions_text)

    def setImage(self, pixmap: QPixmap):
        """Set the recipe banner image (future implementation)."""
        # TODO: Implement actual image display
        # For now, keep placeholder
        pass

    def clearImage(self):
        """Clear the image and show placeholder."""
        # Placeholder is always shown for now
        pass
