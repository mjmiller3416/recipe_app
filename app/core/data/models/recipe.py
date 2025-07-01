"""app/core/data/models/recipe.py

SQLAlchemy ORM model for recipes.
"""

# ── Imports ────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .recipe_ingredient import RecipeIngredient

from app.core.data.sqlalchemy_base import Base


# ── Model Definition ───────────────────────────────────────────────────────
class Recipe(Base):
    """Database model representing a cooking recipe."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    recipe_category: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False, default="Dinner")
    total_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    directions: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)

    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )

