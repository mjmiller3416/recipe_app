"""database/models/shopping_item.py

Structured data model for a single shopping list ingredient.
Combines ingredients from recipes and manual entries for unified display and processing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import TYPE_CHECKING, Literal, Optional

from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from app.core.models.shopping_list import ShoppingList  # avoid circular import



# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingItem(BaseModel):
    ingredient_name: str = Field(..., min_length=1)
    quantity: float = Field(..., ge=0)
    unit: Optional[str] = None
    category: Optional[str] = None
    source: Literal["recipe", "manual"]
    have: bool = False

    @model_validator(mode="before")
    def strip_name(cls, values):
        name = values.get("ingredient_name")
        if isinstance(name, str):
            values["ingredient_name"] = name.strip()
        return values

    @model_validator(mode="before")
    def normalize_strings(cls, values):
        """
        Normalize string fields by stripping whitespace and converting to lowercase.

        Args:
            values (dict): The dictionary of field values.

        Returns:
            dict: The updated dictionary with normalized string values.
        """
        name = values.get("ingredient_name")
        unit = values.get("unit")

        if isinstance(name, str):
            values["ingredient_name"] = name.strip()

        if isinstance(unit, str):
            values["unit"] = unit.strip().lower().rstrip(".")  # "Tsp." → "tsp"

        return values

    def label(self) -> str:
        """
        Returns the formatted display label for this item.
        Example: "2 cups  •  Flour"
        """
        qty = int(self.quantity) if self.quantity.is_integer() else round(self.quantity, 2)
        unit = f"{self.unit} " if self.unit else ""
        return f"{qty} {unit} • {self.ingredient_name}"

    def toggle_have(self):
        """Toggle the 'have' status (used for checkbox state)."""
        self.have = not self.have

    def key(self) -> str:
        """
        A normalized key for grouping like ingredients (name + unit).
        """
        return f"{self.ingredient_name.lower()}::{self.unit or ''}"
    
    def to_model(self) -> "ShoppingList":
        """
        Convert this ShoppingItem back into a ShoppingList DB model (manual items only).
        """
        from app.core.models.shopping_list import (
            ShoppingList  # avoid circular import
        )

        if self.source != "manual":
            raise ValueError("Only manual items can be saved to the ShoppingList model.")
        
        return ShoppingList(
            ingredient_name=self.ingredient_name,
            quantity=self.quantity,
            unit=self.unit or "",
            have=self.have
        )
    