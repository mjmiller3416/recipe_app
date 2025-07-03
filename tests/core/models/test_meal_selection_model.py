# tests/core/models/test_meal_selection_model.py

import pytest
from app.core.models.meal_selection import MealSelection
from app.core.models.recipe import Recipe


def test_meal_selection_creation(session):
    """Test creating a basic meal selection."""
    # Create recipes first
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    side_recipe = Recipe(recipe_name="Side Recipe", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side_recipe])
    session.commit()

    # Create meal selection
    meal = MealSelection(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side_recipe.id
    )
    session.add(meal)
    session.commit()

    assert meal.id is not None
    assert meal.meal_name == "Test Meal"
    assert meal.main_recipe_id == main_recipe.id
    assert meal.side_recipe_1_id == side_recipe.id


def test_meal_selection_relationships(session):
    """Test meal selection relationships with recipes."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    side1_recipe = Recipe(recipe_name="Side 1 Recipe", recipe_category="Test", meal_type="Dinner")
    side2_recipe = Recipe(recipe_name="Side 2 Recipe", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side1_recipe, side2_recipe])
    session.commit()

    # Create meal selection
    meal = MealSelection(
        meal_name="Full Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side1_recipe.id,
        side_recipe_2_id=side2_recipe.id
    )
    session.add(meal)
    session.commit()

    # Test relationships
    assert meal.main_recipe.recipe_name == "Main Recipe"
    assert meal.side_recipe_1.recipe_name == "Side 1 Recipe"
    assert meal.side_recipe_2.recipe_name == "Side 2 Recipe"
    assert meal.side_recipe_3 is None


def test_meal_selection_get_side_recipes(session):
    """Test getting side recipes as a list."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    side1_recipe = Recipe(recipe_name="Side 1 Recipe", recipe_category="Test", meal_type="Dinner")
    side3_recipe = Recipe(recipe_name="Side 3 Recipe", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side1_recipe, side3_recipe])
    session.commit()

    # Create meal selection with non-consecutive sides
    meal = MealSelection(
        meal_name="Partial Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side1_recipe.id,
        side_recipe_3_id=side3_recipe.id
    )
    session.add(meal)
    session.commit()

    side_recipes = meal.get_side_recipes()

    assert len(side_recipes) == 2
    side_names = {recipe.recipe_name for recipe in side_recipes}
    assert side_names == {"Side 1 Recipe", "Side 3 Recipe"}


def test_meal_selection_get_all_recipes(session):
    """Test getting all recipes (main + sides) as a list."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    side_recipe = Recipe(recipe_name="Side Recipe", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side_recipe])
    session.commit()

    # Create meal selection
    meal = MealSelection(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side_recipe.id
    )
    session.add(meal)
    session.commit()

    all_recipes = meal.get_all_recipes()

    assert len(all_recipes) == 2
    recipe_names = {recipe.recipe_name for recipe in all_recipes}
    assert recipe_names == {"Main Recipe", "Side Recipe"}


def test_meal_selection_side_recipe_ids_property(session):
    """Test the side_recipe_ids property."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    side1_recipe = Recipe(recipe_name="Side 1 Recipe", recipe_category="Test", meal_type="Dinner")
    side3_recipe = Recipe(recipe_name="Side 3 Recipe", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side1_recipe, side3_recipe])
    session.commit()

    # Create meal selection with gaps in side recipes
    meal = MealSelection(
        meal_name="Gapped Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side1_recipe.id,
        side_recipe_3_id=side3_recipe.id
    )
    session.add(meal)
    session.commit()

    side_ids = meal.side_recipe_ids

    assert len(side_ids) == 2
    assert set(side_ids) == {side1_recipe.id, side3_recipe.id}


def test_meal_selection_string_representation(session):
    """Test meal selection string representation."""
    # Create recipe
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(main_recipe)
    session.commit()

    # Create meal selection
    meal = MealSelection(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id
    )
    session.add(meal)
    session.commit()

    repr_str = repr(meal)
    assert "Test Meal" in repr_str
    assert str(meal.id) in repr_str
    assert str(main_recipe.id) in repr_str


def test_meal_selection_cascade_delete(session):
    """Test that meal selection can be deleted without affecting recipes."""
    # Create recipe
    main_recipe = Recipe(recipe_name="Main Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(main_recipe)
    session.commit()

    # Create meal selection
    meal = MealSelection(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id
    )
    session.add(meal)
    session.commit()
    meal_id = meal.id

    # Delete meal selection
    session.delete(meal)
    session.commit()

    # Verify meal is deleted but recipe remains
    deleted_meal = session.get(MealSelection, meal_id)
    assert deleted_meal is None

    existing_recipe = session.get(Recipe, main_recipe.id)
    assert existing_recipe is not None
