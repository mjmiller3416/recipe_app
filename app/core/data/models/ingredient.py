"""app/core/data/models/ingredient.py

SQLAlchemy ORM model for ingredients.
"""

# ── Imports ──────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class Ingredient(Base):
    """Represents a single ingredient."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("ingredient_name", String, nullable=False)

    recipes: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )

