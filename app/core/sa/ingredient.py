from __future__ import annotations

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    recipes: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
