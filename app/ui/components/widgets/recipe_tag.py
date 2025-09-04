"""app/ui/components/widgets/recipe_tag.py

RecipeTag component - A pill-shaped tag with icon and text for recipe metadata.
Used for meal types, categories, dietary preferences, etc.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from app.style import Qss, Theme
from app.style.icon import AppIcon
from app.style.icon.config import Icon

# ── Recipe Tag ──────────────────────────────────────────────────────────────────────────────────────────────
class RecipeTag(QFrame):
    """A pill-shaped tag widget with icon and text for recipe metadata."""

    def __init__(self, icon: Icon, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeTag")
        self.setProperty("tag", "RecipeTag")

        # register for component-specific styling
        Theme.register_widget(self, Qss.RECIPE_TAG)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        # Icon
        self.icon_widget = AppIcon(icon)
        self.icon_widget.setSize(24, 24)
        self.icon_widget.setColor("primary")
        self.icon_widget.setObjectName("RecipeTagIcon")

        # Text
        self.text_label = QLabel(text)
        self.text_label.setObjectName("RecipeTagText")

        # Add to layout
        layout.addWidget(self.icon_widget)
        layout.addWidget(self.text_label)

    def setText(self, text: str):
        """Update the tag text."""
        self.text_label.setText(text)

    def setIcon(self, icon: Icon):
        """Update the tag icon."""
        self.icon_widget.setIcon(icon)
