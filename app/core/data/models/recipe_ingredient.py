"""app/core/data/models/recipe_ingredient.py

Association table linking recipes and ingredients.
"""

# ── Imports ──────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class RecipeIngredient(Base):
    """Join table between :class:`Recipe` and :class:`Ingredient`."""

    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id"), primary_key=True
    )
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")

