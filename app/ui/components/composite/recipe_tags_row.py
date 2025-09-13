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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeTagsRow")

        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # Add stretch to center the tags
        self.layout.addStretch()

        # Tag widgets (will be populated when recipe is set)
        self.meal_type_tag = None
        self.category_tag = None
        self.diet_pref_tag = None

        # Add stretch to center the tags
        self.layout.addStretch()

    def setRecipe(self, recipe: Recipe):
        """Set the recipe and update the tags display."""
        # Clear existing tags
        self._clearTags()

        # Get recipe data with fallbacks
        meal_type = getattr(recipe, "meal_type", None) or "Dinner"
        category = getattr(recipe, "recipe_category", None) or "Main Course"
        diet_pref = getattr(recipe, "diet_pref", None) or "High-Protein"

        # Create and add tags
        self.meal_type_tag = Tag(Icon.MEAL_TYPE, meal_type)
        self.category_tag = Tag(Icon.CATEGORY, category)
        self.diet_pref_tag = Tag(Icon.DIET_PREF, diet_pref)

        # Add to layout (insert before the final stretch)
        insert_index = self.layout.count() - 1
        self.layout.insertWidget(insert_index, self.meal_type_tag)
        self.layout.insertSpacing(insert_index + 1, 20)
        self.layout.insertWidget(insert_index + 2, self.category_tag)
        self.layout.insertSpacing(insert_index + 3, 20)
        self.layout.insertWidget(insert_index + 4, self.diet_pref_tag)

    def setTags(self, meal_type: str = None, category: str = None, diet_pref: str = None):
        """Set tags directly with string values (alternative to setRecipe)."""
        # Clear existing tags
        self._clearTags()

        # Use provided values or defaults
        meal_type = meal_type or "Dinner"
        category = category or "Main Course"
        diet_pref = diet_pref or "High-Protein"

        # Create and add tags
        self.meal_type_tag = Tag(Icon.MEAL_TYPE, meal_type)
        self.category_tag = Tag(Icon.CATEGORY, category)
        self.diet_pref_tag = Tag(Icon.DIET_PREF, diet_pref)

        # Add to layout (insert before the final stretch)
        insert_index = self.layout.count() - 1
        self.layout.insertWidget(insert_index, self.meal_type_tag)
        self.layout.insertSpacing(insert_index + 1, 20)
        self.layout.insertWidget(insert_index + 2, self.category_tag)
        self.layout.insertSpacing(insert_index + 3, 20)
        self.layout.insertWidget(insert_index + 4, self.diet_pref_tag)

    def _clearTags(self):
        """Clear all existing tags from the layout."""
        # Remove all widgets except the stretch items (first and last)
        while self.layout.count() > 2:
            item = self.layout.takeAt(1)  # Always take the second item (first is stretch)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                # Spacer items don't need explicit deletion
                pass

    def setAlignment(self, alignment):
        """Set the alignment of the tags within the row."""
        # Remove existing stretches
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            if item.widget():
                # Keep the tags, remove stretches
                continue

        # Re-add based on alignment
        if alignment == "left":
            # Tags on left, stretch on right
            if self.meal_type_tag:
                self.layout.addWidget(self.meal_type_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.category_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.diet_pref_tag)
            self.layout.addStretch()
        elif alignment == "right":
            # Stretch on left, tags on right
            self.layout.addStretch()
            if self.meal_type_tag:
                self.layout.addWidget(self.meal_type_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.category_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.diet_pref_tag)
        else:  # center (default)
            # Stretch on both sides
            self.layout.addStretch()
            if self.meal_type_tag:
                self.layout.addWidget(self.meal_type_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.category_tag)
                self.layout.addSpacing(20)
                self.layout.addWidget(self.diet_pref_tag)
            self.layout.addStretch()
