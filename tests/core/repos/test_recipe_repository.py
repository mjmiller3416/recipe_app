# tests/features/recipes/test_recipe_repository.py

from app.core.repos.recipe_repository import RecipeRepository
from app.core.models import Recipe

def test_get_all_recipes(session):
    # Arrange
    session.add_all([
        Recipe(recipe_name="Spaghetti", recipe_category="Pasta", meal_type="Dinner"),
        Recipe(recipe_name="Pancakes", recipe_category="Breakfast", meal_type="Breakfast"),
    ])
    session.commit()

    repo = RecipeRepository(session)

    # Act
    recipes = repo.get_all_recipes()

    # Assert
    assert len(recipes) == 2
    assert recipes[0].recipe_name == "Spaghetti"
    assert recipes[1].meal_type == "Breakfast"