"""database/models/shopping_state.py

Tracks the 'checked' state of shopping list items from recipe sources.
Used to persist checkbox values across sessions while handling dynamic quantity updates.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations
from typing import Optional
from pydantic import Field, model_validator
from database.base_model import ModelBase
from core.helpers.debug_logger import DebugLogger

# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingState(ModelBase):
    """ShoppingState model representing the state of items in a shopping list.
    This model is used to track the quantity, unit, and checked status of items.
    """
    key: str    
    quantity: float
    unit: str
    checked: bool = False

    @model_validator(mode="before")
    def normalize_key(cls, values):
        """
        Normalize the key and unit field formatting.
        """
        key = values.get("key")
        unit = values.get("unit")
        if isinstance(key, str):
            values["key"] = key.strip().lower()
        if isinstance(unit, str):
            values["unit"] = unit.strip().lower().rstrip(".")
        return values

    @classmethod
    def get_state(cls, key: str) -> Optional[ShoppingState]:
        """
        Fetch saved state by key (e.g. "milk::cup").

        Args:
            key (str): The normalized ingredient key.

        Returns:
            Optional[ShoppingState]: Matching state or None.
        """
        result = cls.first(key=key)
        if result:
            DebugLogger.log(f"[ShoppingState] Loaded state for key: {key} → checked={result.checked}", "info")
        else:
            DebugLogger.log(f"[ShoppingState] No saved state found for key: {key}", "info")
        return result

    @classmethod
    def update_state(cls, key: str, quantity: float, unit: str, checked: bool) -> None:
        """
        Add or update the checkbox state for a shopping item.

        Args:
            key (str): Normalized ingredient key.
            quantity (float): Last known quantity.
            unit (str): Unit of measurement.
            checked (bool): Whether it was checked.
        """
        existing = cls.get_state(key)
        DebugLogger.log(f"[ShoppingState] Updating state → {key}: {quantity} {unit}, checked={checked}", "info")
        if existing:
            existing.quantity = quantity
            existing.unit = unit
            existing.checked = checked
            existing.save()
        else:
            DebugLogger.log(f"[ShoppingState] Saving new state → {key}: {quantity} {unit}, checked={checked}", "info")
            cls(key=key, quantity=quantity, unit=unit, checked=checked).save()