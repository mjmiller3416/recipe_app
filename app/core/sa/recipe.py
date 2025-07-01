from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)

    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
