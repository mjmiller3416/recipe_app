# tests/core/services/test_recipe_service.py

# ── Imports ─────────────────────────────────────────────────────────────
import uuid
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.models.ingredient import Ingredient


# ── Fixtures ────────────────────────────────────────────────────────────
@pytest.fixture
def sample_recipe_data(tmp_path) -> tuple[RecipeCreateDTO, Path]:
    unique_name = f"UnitTest Stew {uuid.uuid4()}"
    image_path = tmp_path / f"{uuid.uuid4().hex}.png"
    image_path.write_bytes(b"fake image content")

    dto = RecipeCreateDTO(
        recipe_name=unique_name,
        recipe_category="Chicken",
        meal_type="Dinner",
        total_time=45,
        servings=4,
        directions="Step1\nStep2",
        image_path=str(image_path),
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Chicken Breast",
                ingredient_category="Meat",
                quantity=1,
                unit="lb"
            ),
            RecipeIngredientDTO(
                ingredient_name="Salt",
                ingredient_category="Spices",
                quantity=1,
                unit="tsp"
            )
        ]
    )
    return dto, image_path

# ── Tests ───────────────────────────────────────────────────────────────
def test_create_recipe_with_ingredients(session: Session, sample_recipe_data):
    dto, img_path = sample_recipe_data
    service = RecipeService(session)

    recipe = service.create_recipe_with_ingredients(dto)

    # Confirm saved
    fetched = session.get(Recipe, recipe.id)
    assert fetched.recipe_name == dto.recipe_name
    assert fetched.recipe_category == dto.recipe_category
    assert fetched.directions == dto.directions
    assert fetched.servings == dto.servings
    assert Path(fetched.image_path).exists()

    # Confirm ingredients linked
    links = session.execute(
        select(RecipeIngredient).filter_by(recipe_id=recipe.id)
    ).unique().scalars().all()
    assert len(links) == 2

    ingredient_names = {
        session.get(Ingredient, link.ingredient_id).ingredient_name for link in links
    }
    assert "Chicken Breast" in ingredient_names
    assert "Salt" in ingredient_names


def test_favorite_toggle(session: Session, sample_recipe_data):
    dto, _ = sample_recipe_data
    service = RecipeService(session)
    recipe = service.create_recipe_with_ingredients(dto)

    assert not recipe.is_favorite
    updated = service.toggle_favorite(recipe.id)
    assert updated.is_favorite
    updated = service.toggle_favorite(recipe.id)
    assert not updated.is_favorite