# tests/core/test_full_integration.py

import pytest

from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.models import Ingredient, Recipe
from app.core.services.recipe_service import RecipeService


def test_full_recipe_creation_flow(session):
    """Test the complete flow of creating a recipe with ingredients."""
    # Arrange
    service = RecipeService(session)
    
    recipe_dto = RecipeCreateDTO(
        recipe_name="Integration Test Recipe",
        recipe_category="Test",
        meal_type="Dinner",
        total_time=30,
        servings=4,
        directions="Step 1\nStep 2\nStep 3",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Test Ingredient 1",
                ingredient_category="Test Category",
                quantity=1.0,
                unit="cup"
            ),
            RecipeIngredientDTO(
                ingredient_name="Test Ingredient 2", 
                ingredient_category="Test Category",
                quantity=2.0,
                unit="tbsp"
            )
        ]
    )
    
    # Act
    created_recipe = service.create_recipe_with_ingredients(recipe_dto)
    
    # Assert
    assert created_recipe.recipe_name == "Integration Test Recipe"
    assert created_recipe.recipe_category == "Test"
    assert created_recipe.meal_type == "Dinner"
    assert created_recipe.total_time == 30
    assert created_recipe.servings == 4
    assert len(created_recipe.ingredients) == 2
    
    # Verify ingredients were created
    ingredient_names = [ing.ingredient.ingredient_name for ing in created_recipe.ingredients]
    assert "Test Ingredient 1" in ingredient_names
    assert "Test Ingredient 2" in ingredient_names
    
    # Verify quantities and units
    for recipe_ingredient in created_recipe.ingredients:
        if recipe_ingredient.ingredient.ingredient_name == "Test Ingredient 1":
            assert recipe_ingredient.quantity == 1.0
            assert recipe_ingredient.unit == "cup"
        elif recipe_ingredient.ingredient.ingredient_name == "Test Ingredient 2":
            assert recipe_ingredient.quantity == 2.0
            assert recipe_ingredient.unit == "tbsp"


def test_duplicate_ingredient_handling(session):
    """Test that ingredients are reused when they already exist."""
    # Arrange
    service = RecipeService(session)
    
    # Create first recipe
    recipe_dto_1 = RecipeCreateDTO(
        recipe_name="Recipe 1",
        recipe_category="Test",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Shared Ingredient",
                ingredient_category="Shared Category",
                quantity=1.0,
                unit="cup"
            )
        ]
    )
    
    recipe_dto_2 = RecipeCreateDTO(
        recipe_name="Recipe 2", 
        recipe_category="Test",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Shared Ingredient",
                ingredient_category="Shared Category",
                quantity=2.0,
                unit="tbsp"
            )
        ]
    )
    
    # Act
    recipe_1 = service.create_recipe_with_ingredients(recipe_dto_1)
    recipe_2 = service.create_recipe_with_ingredients(recipe_dto_2)
    
    # Assert
    ingredient_1 = recipe_1.ingredients[0].ingredient
    ingredient_2 = recipe_2.ingredients[0].ingredient
    
    # Same ingredient should be reused
    assert ingredient_1.id == ingredient_2.id
    assert ingredient_1.ingredient_name == "Shared Ingredient"
    
    # But different quantities in each recipe
    assert recipe_1.ingredients[0].quantity == 1.0
    assert recipe_1.ingredients[0].unit == "cup"
    assert recipe_2.ingredients[0].quantity == 2.0
    assert recipe_2.ingredients[0].unit == "tbsp"
