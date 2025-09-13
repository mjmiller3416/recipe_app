"""app/ui/components/composite/recipe_tags_row.py

A reusable component for displaying recipe tags (meal type, category, dietary preference)
in a horizontal row layout. Extracted from ViewRecipe for use in multiple contexts.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.core.models.recipe import Recipe
from app.style.icon import Icon
from app.ui.components.widgets.tag import Tag


# ── Recipe Tags Row ─────────────────────────────────────────────────────────────────────────────────────────
class RecipeTagsRow(QWidget):
    """A horizontal row of recipe tags showing meal type, category, and dietary preference."""

    # Default values for tags
    DEFAULTS = {
        'meal_type': 'Dinner',
        'category': 'Main Course',
        'diet_pref': 'High-Protein'
    }

    # Tag configurations
    TAG_CONFIG = [
        ('meal_type_tag', Icon.MEAL_TYPE, 'meal_type'),
        ('category_tag', Icon.CATEGORY, 'category'),
        ('diet_pref_tag', Icon.DIET_PREF, 'diet_pref')
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeTagsRow")

        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # Tag widgets
        self.meal_type_tag = None
        self.category_tag = None
        self.diet_pref_tag = None

        # Current alignment
        self._alignment = "center"

        # Set initial layout with center alignment
        self._setupLayout()

    def setRecipe(self, recipe: Recipe):
        """Set the recipe and update the tags display."""
        # Extract values from recipe with fallbacks
        values = {
            'meal_type': getattr(recipe, 'meal_type', None),
            'category': getattr(recipe, 'recipe_category', None),
            'diet_pref': getattr(recipe, 'diet_pref', None)
        }
        self._updateTags(**values)

    def setTags(self, meal_type: str = None, category: str = None, diet_pref: str = None):
        """Set tags directly with string values (alternative to setRecipe)."""
        self._updateTags(meal_type=meal_type, category=category, diet_pref=diet_pref)

    def setAlignment(self, alignment):
        """Set the alignment of the tags within the row."""
        if alignment not in ("left", "right", "center"):
            alignment = "center"
        self._alignment = alignment
        self._setupLayout()

    def _updateTags(self, **kwargs):
        """Update tags with provided values or defaults."""
        # Clear existing tags
        self._clearTags()

        # Create tags with provided values or defaults
        for attr_name, icon, value_key in self.TAG_CONFIG:
            value = kwargs.get(value_key) or self.DEFAULTS[value_key]
            setattr(self, attr_name, Tag(icon, value))

        # Rebuild layout with tags
        self._setupLayout()

    def _clearTags(self):
        """Clear all existing tags from the layout."""
        # Remove all items from layout
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            if item.widget() and item.widget() not in (self.meal_type_tag, self.category_tag, self.diet_pref_tag):
                item.widget().deleteLater()

    def _setupLayout(self):
        """Setup the layout based on current alignment and tags."""
        # Clear the layout first
        while self.layout.count() > 0:
            self.layout.takeAt(0)

        # Add stretches and tags based on alignment
        if self._alignment == "left":
            self._addTags()
            self.layout.addStretch()
        elif self._alignment == "right":
            self.layout.addStretch()
            self._addTags()
        else:  # center (default)
            self.layout.addStretch()
            self._addTags()
            self.layout.addStretch()

    def _addTags(self):
        """Add tag widgets to the layout with spacing."""
        if not self.meal_type_tag:
            return

        tags = [self.meal_type_tag, self.category_tag, self.diet_pref_tag]
        for i, tag in enumerate(tags):
            if tag:
                self.layout.addWidget(tag)
                # Add spacing between tags (but not after the last one)
                if i < len(tags) - 1:
                    self.layout.addSpacing(20)
