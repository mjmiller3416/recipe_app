# tests/core/models/test_recipe_model.py

import pytest
from datetime import datetime
from app.core.models.recipe import Recipe
from app.core.models.ingredient import Ingredient
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.models.recipe_history import RecipeHistory


def test_recipe_creation(session):
    """Test creating a basic recipe."""
    recipe = Recipe(
        recipe_name="Test Recipe",
        recipe_category="Test Category",
        meal_type="Dinner",
        total_time=30,
        servings=4,
        directions="Step 1\nStep 2"
    )
    session.add(recipe)
    session.commit()

    assert recipe.id is not None
    assert recipe.recipe_name == "Test Recipe"
    assert recipe.created_at is not None
    assert recipe.is_favorite is False


def test_recipe_relationships(session):
    """Test recipe relationships with ingredients and history."""
    # Create recipe
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    # Create ingredient
    ingredient = Ingredient(ingredient_name="Test Ingredient", ingredient_category="Test")
    session.add(ingredient)
    session.commit()

    # Create recipe-ingredient relationship
    recipe_ing = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity=1.0,
        unit="cup"
    )
    session.add(recipe_ing)
    session.commit()

    # Create recipe history
    history = RecipeHistory(recipe_id=recipe.id)
    session.add(history)
    session.commit()

    # Test relationships
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0].ingredient.ingredient_name == "Test Ingredient"
    assert len(recipe.history) == 1
    assert recipe.history[0].recipe_id == recipe.id


def test_recipe_formatted_time(session):
    """Test formatted time display."""
    # Test with hours and minutes
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner", total_time=125)
    assert recipe1.formatted_time() == "2h 5m"

    # Test with only minutes
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner", total_time=45)
    assert recipe2.formatted_time() == "45m"

    # Test with no time
    recipe3 = Recipe(recipe_name="Recipe 3", recipe_category="Test", meal_type="Dinner")
    assert recipe3.formatted_time() == ""


def test_recipe_formatted_servings(session):
    """Test formatted servings display."""
    # Test with servings
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner", servings=4)
    assert recipe1.formatted_servings() == "4"

    # Test without servings
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    assert recipe2.formatted_servings() == ""


def test_recipe_get_directions_list(session):
    """Test getting directions as a list."""
    # Test with multiple lines
    recipe1 = Recipe(
        recipe_name="Recipe 1",
        recipe_category="Test",
        meal_type="Dinner",
        directions="Step 1\nStep 2\n\nStep 3"
    )
    directions = recipe1.get_directions_list()
    assert directions == ["Step 1", "Step 2", "Step 3"]

    # Test with no directions
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    assert recipe2.get_directions_list() == []


def test_recipe_string_representation(session):
    """Test recipe string representation."""
    recipe = Recipe(
        recipe_name="Test Recipe",
        recipe_category="Test Category",
        meal_type="Dinner",
        total_time=30,
        servings=4,
        is_favorite=True
    )
    session.add(recipe)
    session.commit()

    repr_str = repr(recipe)
    assert "Test Recipe" in repr_str
    assert "Test Category" in repr_str
    assert "Dinner" in repr_str
    assert "30" in repr_str
    assert "4" in repr_str
    assert "True" in repr_str
