"""app/core/models/saved_meal_state.py

SQLAlchemy ORM model for storing the state of saved meals in the database.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database.base import Base

if TYPE_CHECKING:
    from app.core.models.meal_selection import MealSelection


# ── Saved Meal State Model ───────────────────────────────────────────────────────────────────
class SavedMealState(Base):
    __tablename__ = "saved_meal_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meal_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("meal_selections.id", ondelete="CASCADE"), 
        nullable=False
    )

    # ── Relationships ────────────────────────────────────────────────────────────────────────
    meal_selection: Mapped["MealSelection"] = relationship(
        "MealSelection",
        foreign_keys=[meal_id]
    )

    # ── String Representation ────────────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<SavedMealState(id={self.id}, meal_id={self.meal_id})>"