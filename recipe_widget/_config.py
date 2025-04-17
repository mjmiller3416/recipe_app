# 🔸 Third-party Imports
from PySide6.QtCore import QSize

# 🔹 Card Dimensions
FULL_CARD_WIDTH = 280
FULL_CARD_HEIGHT = 420
FULL_IMAGE_HEIGHT = 280
MINI_CARD_WIDTH = 280
MINI_CARD_HEIGHT = 100
MINI_IMAGE_SIZE = QSize(100, 100)

# 🔹 Layout Spacing & Margins
FULL_LAYOUT_SPACING = 8           # Spacing between image/title/meta
FULL_LAYOUT_MARGIN_LEFT = 0       # Image flush left
FULL_LAYOUT_MARGIN_TOP = 0        # Image flush top
FULL_LAYOUT_MARGIN_RIGHT = 0      # Image flush right
FULL_LAYOUT_MARGIN_BOTTOM = 0     # Space below meta row
META_LAYOUT_SPACING = 0           # Spacing within meta row (handled by stretch)
META_LAYOUT_MARGIN_LEFT = 16      # Horizontal padding
META_LAYOUT_MARGIN_TOP = 0        # Internal top padding within the meta container
META_LAYOUT_MARGIN_RIGHT = 16     # Horizontal padding
META_LAYOUT_MARGIN_BOTTOM = 8     # Increased bottom padding
SERVINGS_TIME_LAYOUT_SPACING = 5  # Adjusted spacing within servings/time blocks 
SERVINGS_VALUE_ROW_SPACING = 4    # Spacing between icon and text
MINI_LAYOUT_SPACING = 8           # Space between image and title
MINI_LAYOUT_MARGIN_LEFT = 0       # Image flush left
MINI_LAYOUT_MARGIN_TOP = 0        # Image flush top
MINI_LAYOUT_MARGIN_RIGHT = 8      # Space right of title
MINI_LAYOUT_MARGIN_BOTTOM = 0     # Image flush bottom
