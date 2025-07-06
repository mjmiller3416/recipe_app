# tests/core/repos/test_ingredient_repository_basic.py

from app.core.dtos.ingredient_dtos import IngredientCreateDTO
from app.core.models import Ingredient
from app.core.repos.ingredient_repo import IngredientRepo


def test_get_all_ingredients(session):
    # Arrange
    session.add_all([
        Ingredient(ingredient_name="Salt", ingredient_category="Spices"),
        Ingredient(ingredient_name="Pepper", ingredient_category="Spices"),
    ])
    session.commit()

    repo = IngredientRepo(session)

    # Act
    ingredients = repo.get_all()

    # Assert
    assert len(ingredients) == 2
    assert ingredients[0].ingredient_name == "Salt"
    assert ingredients[1].ingredient_category == "Spices"

def test_get_or_create_ingredient(session):
    # Arrange
    repo = IngredientRepo(session)
    dto = IngredientCreateDTO(
        ingredient_name="Chicken Breast",
        ingredient_category="Meat"
    )

    # Act
    ingredient1 = repo.get_or_create(dto)
    ingredient2 = repo.get_or_create(dto)  # Should return same instance

    # Assert
    assert ingredient1.ingredient_name == "Chicken Breast"
    assert ingredient1.ingredient_category == "Meat"
    assert ingredient1.id == ingredient2.id  # Same instance returned
    
    # Verify only one instance in database
    all_ingredients = repo.get_all()
    chicken_ingredients = [ing for ing in all_ingredients if ing.ingredient_name == "Chicken Breast"]
    assert len(chicken_ingredients) == 1
