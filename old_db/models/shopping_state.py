""" app/core/models/shopping_state.py

Tracks the 'checked' state of shopping list items from recipe sources.
Used to persist checkbox values across sessions while handling dynamic quantity updates.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sqlite3
from typing import Optional

from pydantic import Field, model_validator

from app.core.database.base import ModelBase
from app.core.database.db import get_connection
from dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingState(ModelBase):
    """
    ShoppingState model representing the state of items in a shopping list.
    Tracks quantity, unit, and checked status.
    """
    key: str
    quantity: float
    unit: str
    checked: bool = False

    @model_validator(mode="before")
    def normalize_key(cls, values):
        """
        Normalize the key and unit fields (trim, lowercase, strip punctuation).
        """
        key = values.get("key")
        unit = values.get("unit")
        if isinstance(key, str):
            values["key"] = key.strip().lower()
        if isinstance(unit, str):
            values["unit"] = unit.strip().lower().rstrip(".")
        return values

    @classmethod
    def get_state(
        cls,
        key: str,
        connection: Optional[sqlite3.Connection] = None
    ) -> Optional[ShoppingState]:
        """
        Fetch saved state by key, optionally within an existing transaction.
        """
        sql = f"SELECT * FROM {cls.table_name()} WHERE key = ?"
        results = cls.raw_query(sql, (key,), connection=connection)
        if results:
            state = results[0]
            DebugLogger.log(
                f"[ShoppingState] Loaded state for key: {key} → checked={state.checked}",
                "info"
            )
            return state
        DebugLogger.log(
            f"[ShoppingState] No saved state found for key: {key}",
            "info"
        )
        return None

    @classmethod
    def update_state(
        cls,
        key: str,
        quantity: float,
        unit: str,
        checked: bool,
        connection: Optional[sqlite3.Connection] = None
    ) -> ShoppingState:
        """
        Add or update the checkbox state for a shopping item.
        Executes within an optional transaction.
        """
        if connection is None:
            with get_connection() as conn:
                return cls.update_state(key, quantity, unit, checked, connection=conn)

        # Ensure normalized key/unit matching
        existing = cls.get_state(key, connection=connection)
        DebugLogger.log(
            f"[ShoppingState] Updating state → {key}: {quantity} {unit}, checked={checked}",
            "info"
        )
        if existing:
            existing.quantity = quantity
            existing.unit = unit
            existing.checked = checked
            existing.save(connection=connection)
            return existing

        DebugLogger.log(
            f"[ShoppingState] Saving new state → {key}: {quantity} {unit}, checked={checked}",
            "info"
        )
        new_state = cls(
            key=key,
            quantity=quantity,
            unit=unit,
            checked=checked
        ).save(connection=connection)
        return new_state
