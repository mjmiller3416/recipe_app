from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.data.sqlalchemy_base import Base


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), primary_key=True)
    quantity: Mapped[str] = mapped_column(String(50), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")
