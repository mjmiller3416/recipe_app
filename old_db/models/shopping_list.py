""" app/core/models/shopping_list.py

Structured data model for a shopping list item.
Combines ingredients from recipes and manual entries for unified display and processing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import TYPE_CHECKING, Optional

from pydantic import Field, model_validator
from app.core.utils.validators import strip_string_values

from app.core.database.base import ModelBase
from app.core.models.shopping_item import ShoppingItem

if TYPE_CHECKING:
    from app.core.models.shopping_item import ShoppingItem


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingList(ModelBase):
    id: Optional[int]        = None
    ingredient_name: str     = Field(..., min_length=1)
    quantity: float          = Field(..., ge=0)
    unit: str                = Field(..., min_length=1)
    have: bool               = False

    @model_validator(mode="before")
    def strip_strings(cls, values):
        """Strip whitespace from string fields before validation."""
        return strip_string_values(values, ("ingredient_name", "unit"))

    def label(self) -> str:
        """Return a checklist-style label for UI display."""
        icon = "✔" if self.have else "✖"
        return f"{icon} {self.ingredient_name}: {self.quantity} {self.unit}"
    
    def to_item(self) -> "ShoppingItem":
        """
        Convert this database row to a ShoppingItem (for unified display).

        Returns:
            ShoppingItem: A UI-friendly model with manual source.
        """
        from app.core.models.shopping_item import (
            ShoppingItem  # avoid circular import
        )

        return ShoppingItem(
            ingredient_name=self.ingredient_name,
            quantity=self.quantity,
            unit=self.unit,
            category=None,
            source="manual",
            have=self.have
        )
