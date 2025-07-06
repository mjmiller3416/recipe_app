# tests/core/repos/test_planner_repo.py

import pytest

from app.core.models.meal_selection import MealSelection
from app.core.models.recipe import Recipe
from app.core.models.saved_meal_state import SavedMealState
from app.core.repos.planner_repo import PlannerRepo


def test_get_saved_meal_ids_empty(session):
    """Test getting saved meal IDs when none exist."""
    repo = PlannerRepo(session)

    meal_ids = repo.get_saved_meal_ids()

    assert meal_ids == []


def test_save_active_meal_ids(session):
    """Test saving active meal IDs."""
    # Create some recipes and meal selections first
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    meal1 = MealSelection(meal_name="Meal 1", main_recipe_id=recipe1.id)
    meal2 = MealSelection(meal_name="Meal 2", main_recipe_id=recipe2.id)
    session.add_all([meal1, meal2])
    session.commit()

    repo = PlannerRepo(session)

    # Save meal IDs
    repo.save_active_meal_ids([meal1.id, meal2.id])

    # Verify they were saved
    saved_ids = repo.get_saved_meal_ids()
    assert set(saved_ids) == {meal1.id, meal2.id}


def test_clear_saved_meal_states(session):
    """Test clearing all saved meal states."""
    # Create and save some meal states
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()

    state = SavedMealState(meal_id=meal.id)
    session.add(state)
    session.commit()

    repo = PlannerRepo(session)

    # Verify state exists
    assert len(repo.get_saved_meal_ids()) == 1

    # Clear states
    repo.clear_saved_meal_states()

    # Verify states are cleared
    assert len(repo.get_saved_meal_ids()) == 0


def test_create_meal_selection(session):
    """Test creating a new meal selection."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Dish", recipe_category="Test", meal_type="Dinner")
    side_recipe = Recipe(recipe_name="Side Dish", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side_recipe])
    session.commit()

    repo = PlannerRepo(session)

    # Create meal selection
    meal = MealSelection(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side_recipe.id
    )

    created_meal = repo.create_meal_selection(meal)

    assert created_meal.id is not None
    assert created_meal.meal_name == "Test Meal"
    assert created_meal.main_recipe_id == main_recipe.id
    assert created_meal.side_recipe_1_id == side_recipe.id


def test_get_meal_selection_by_id(session):
    """Test getting a meal selection by ID."""
    # Create recipe and meal
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()

    repo = PlannerRepo(session)

    # Retrieve meal
    retrieved_meal = repo.get_meal_selection_by_id(meal.id)

    assert retrieved_meal is not None
    assert retrieved_meal.id == meal.id
    assert retrieved_meal.meal_name == "Test Meal"


def test_get_meal_selection_by_id_not_found(session):
    """Test getting a meal selection by ID that doesn't exist."""
    repo = PlannerRepo(session)

    retrieved_meal = repo.get_meal_selection_by_id(999)

    assert retrieved_meal is None


def test_get_all_meal_selections(session):
    """Test getting all meal selections."""
    # Create recipes and meals
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    meal1 = MealSelection(meal_name="Meal 1", main_recipe_id=recipe1.id)
    meal2 = MealSelection(meal_name="Meal 2", main_recipe_id=recipe2.id)
    session.add_all([meal1, meal2])
    session.commit()

    repo = PlannerRepo(session)

    meals = repo.get_all_meal_selections()

    assert len(meals) == 2
    meal_names = {meal.meal_name for meal in meals}
    assert meal_names == {"Meal 1", "Meal 2"}


def test_delete_meal_selection(session):
    """Test deleting a meal selection."""
    # Create recipe and meal
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()
    meal_id = meal.id

    repo = PlannerRepo(session)

    # Delete meal
    result = repo.delete_meal_selection(meal_id)

    assert result is True

    # Verify deletion
    deleted_meal = repo.get_meal_selection_by_id(meal_id)
    assert deleted_meal is None


def test_update_meal_selection(session):
    """Test updating an existing meal selection."""
    # Create recipes
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    # Create meal
    meal = MealSelection(meal_name="Original Meal", main_recipe_id=recipe1.id)
    session.add(meal)
    session.commit()

    repo = PlannerRepo(session)

    # Update meal
    meal.meal_name = "Updated Meal"
    meal.main_recipe_id = recipe2.id

    updated_meal = repo.update_meal_selection(meal)

    assert updated_meal.meal_name == "Updated Meal"
    assert updated_meal.main_recipe_id == recipe2.id
