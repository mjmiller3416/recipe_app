# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from database.base_model import ModelBase


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingList(ModelBase):
    id: Optional[int]        = None
    ingredient_name: str     = Field(..., min_length=1)
    quantity: float          = Field(..., ge=0)
    unit: str                = Field(..., min_length=1)
    have: bool               = False

    @model_validator(mode="before")
    def strip_strings(cls, values):
        for fld in ("ingredient_name", "unit"):
            v = values.get(fld)
            if isinstance(v, str):
                values[fld] = v.strip()
        return values

    def label(self) -> str:
        """Return a checklist-style label for UI display."""
        icon = "✔" if self.have else "✖"
        return f"{icon} {self.ingredient_name}: {self.quantity} {self.unit}"
