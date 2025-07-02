"""app/core/features/recipes/recipe.py

SQLAlchemy model for recipes.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.utils import utcnow
from ..database.base import Base
from .recipe_ingredient import RecipeIngredient
from .recipe_history import RecipeHistory

# ── Recipe Model ─────────────────────────────────────────────────────────────────────────────
class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_name: Mapped[str] = mapped_column(String, nullable=False)
    recipe_category: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, default="Dinner", nullable=False)
    diet_pref: Mapped[Optional[str]] = mapped_column(String, default="None", nullable=True)
    total_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    directions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Relationships  ───────────────────────────────────────────────────────────────────────
    ingredients: Mapped[List[RecipeIngredient]] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    history: Mapped[List[RecipeHistory]] = relationship(
        "RecipeHistory",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    # ── Helper Methods ───────────────────────────────────────────────────────────────────────
    def formatted_time(self) -> str:
        """Return total_time formatted as "Xh Ym" or "Ym" if less than 1 hour."""
        if not self.total_time:
            return ""
        hrs, mins = divmod(self.total_time, 60)
        return f"{hrs}h {mins}m" if hrs else f"{mins}m"

    def formatted_servings(self) -> str:
        """Return servings with label."""
        return f"{self.servings}" if self.servings else ""

    def get_directions_list(self) -> list[str]:
        """Return each non-empty line as a step."""
        if not self.directions:
            return []
        return [line.strip() for line in self.directions.splitlines() if line.strip()]
    
    def __repr__(self) -> str:
        return (
            f"Recipe(id={self.id}, recipe_name={self.recipe_name}, "
            f"recipe_category={self.recipe_category}, meal_type={self.meal_type}, "
            f"total_time={self.total_time}, servings={self.servings}, "
            f"is_favorite={self.is_favorite})"
        )

# ── TODOs ───────────────────────────────────────────────────────────────────────────────
# • Create RecipeIngredient and RecipeHistory SQLAlchemy models ✅
# • Add foreign keys and back_populates ✅
# • Migrate last_cooked() to repository once RecipeHistory is live
# • Autogenerate Alembic migration after this file is in place ✅
