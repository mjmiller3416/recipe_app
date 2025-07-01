"""app/core/data/models/recipe_ingredient.py

Association table between recipes and ingredients.
"""

# ── Imports ────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .ingredient import Ingredient
    from .recipe import Recipe

from app.core.data.sqlalchemy_base import Base


# ── Model Definition ───────────────────────────────────────────────────────
class RecipeIngredient(Base):
    """Association object linking a recipe to an ingredient."""

    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), primary_key=True)
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")

