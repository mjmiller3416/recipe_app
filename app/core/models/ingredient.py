"""app/core/features/ingredients/ingredient_model.py

SQLAlchemy model for the Ingredient table.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

if TYPE_CHECKING:
    from .recipe_ingredient import RecipeIngredient


# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class Ingredient(Base):
    """SQLAlchemy model for Ingredient."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingredient_name: Mapped[str] = mapped_column(String, nullable=False)
    ingredient_category: Mapped[str] = mapped_column(String, nullable=False)

    # ── Relationships ────────────────────────────────────────────────────────────────────────
    recipe_links: Mapped[list[RecipeIngredient]] = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    # ── Display Methods ──────────────────────────────────────────────────────────────────────
    def display_label(self) -> str:
        """Return a human-friendly label for this ingredient."""
        return f"{self.ingredient_name} ({self.ingredient_category})"

