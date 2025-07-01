"""app/core/data/models/recipe.py

SQLAlchemy ORM model for recipes.
"""

# ── Imports ──────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class Recipe(Base):
    """Represents a recipe stored in the database."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("recipe_name", String, nullable=False)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


