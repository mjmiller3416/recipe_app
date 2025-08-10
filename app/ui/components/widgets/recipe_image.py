"""app/ui/components/widgets/recipe_image.py

RecipeImage component - A recipe banner image with fixed aspect ratio.
Shows a styled placeholder when no image is uploaded.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap

from app.style.icon import AppIcon
from app.style.icon.config import Icon


class RecipeImage(QFrame):
    """Recipe banner image component with fixed 2:1 aspect ratio (1200x600)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeImage")
        self.setProperty("tag", "RecipeImage")
        
        # Fixed aspect ratio (2:1 - 1200x600)
        self.setMinimumHeight(300)
        self.setMaximumHeight(400) 
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Placeholder content
        self._create_placeholder()
        
    def _create_placeholder(self):
        """Create placeholder content for when no image is uploaded."""
        # Icon
        self.placeholder_icon = AppIcon(Icon.PHOTO)
        self.placeholder_icon.setFixedSize(QSize(48, 48))
        self.placeholder_icon.setObjectName("RecipeImagePlaceholderIcon")
        
        # Text
        self.placeholder_text = QLabel("No image uploaded")
        self.placeholder_text.setObjectName("RecipeImagePlaceholderText")
        self.placeholder_text.setAlignment(Qt.AlignCenter)
        
        # Dimensions text
        self.dimensions_text = QLabel("1200 × 600")
        self.dimensions_text.setObjectName("RecipeImageDimensionsText")
        self.dimensions_text.setAlignment(Qt.AlignCenter)
        
        # Add to layout
        self.layout().addWidget(self.placeholder_icon, 0, Qt.AlignCenter)
        self.layout().addWidget(self.placeholder_text)
        self.layout().addWidget(self.dimensions_text)
        
    def setImage(self, pixmap: QPixmap):
        """Set the recipe image (future implementation)."""
        # TODO: Implement actual image display
        # For now, keep placeholder
        pass
        
    def clearImage(self):
        """Clear the image and show placeholder."""
        # Placeholder is always shown for now
        pass