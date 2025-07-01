"""app/core/data/models/ingredient.py

SQLAlchemy ORM model for ingredients.
"""

# ── Imports ────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe_ingredient import RecipeIngredient

from app.core.data.sqlalchemy_base import Base


# ── Model Definition ───────────────────────────────────────────────────────
class Ingredient(Base):
    """Database model representing an ingredient."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_name: Mapped[str] = mapped_column(String, nullable=False)
    ingredient_category: Mapped[str] = mapped_column(String, nullable=False)

    recipes: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )

