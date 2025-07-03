# tests/features/recipes/test_recipe_repo.py

from app.core.repos.recipe_repo import RecipeRepo
from app.core.models import Recipe

def test_get_all_recipes(session):
    # Arrange
    session.add_all([
        Recipe(recipe_name="Spaghetti", recipe_category="Pasta", meal_type="Dinner"),
        Recipe(recipe_name="Pancakes", recipe_category="Breakfast", meal_type="Breakfast"),
    ])
    session.commit()

    repo = RecipeRepo(session)

    # Act
    recipes = repo.get_all_recipes()

    # Assert
    assert len(recipes) == 2
    assert recipes[0].recipe_name == "Spaghetti"
    assert recipes[1].meal_type == "Breakfast"