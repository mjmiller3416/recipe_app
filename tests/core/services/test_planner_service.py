# tests/core/services/test_planner_service.py

import pytest

from app.core.dtos.planner_dtos import (MealSelectionCreateDTO,
                                        MealSelectionUpdateDTO)
from app.core.models.meal_selection import MealSelection
from app.core.models.recipe import Recipe
from app.core.services.planner_service import PlannerService


def test_get_saved_meal_plan_empty(session):
    """Test getting saved meal plan when none exists."""
    service = PlannerService(session)

    meal_plan = service.get_saved_meal_plan()

    assert meal_plan == []


def test_create_meal_selection_success(session):
    """Test creating a new meal selection successfully."""
    # Create recipes
    main_recipe = Recipe(recipe_name="Main Dish", recipe_category="Test", meal_type="Dinner")
    side_recipe = Recipe(recipe_name="Side Dish", recipe_category="Test", meal_type="Dinner")
    session.add_all([main_recipe, side_recipe])
    session.commit()

    service = PlannerService(session)

    create_dto = MealSelectionCreateDTO(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=side_recipe.id
    )

    result = service.create_meal_selection(create_dto)

    assert result is not None
    assert result.meal_name == "Test Meal"
    assert result.main_recipe_id == main_recipe.id
    assert result.side_recipe_1_id == side_recipe.id
    assert result.id is not None


def test_create_meal_selection_invalid_main_recipe(session):
    """Test creating meal selection with invalid main recipe ID."""
    service = PlannerService(session)

    create_dto = MealSelectionCreateDTO(
        meal_name="Test Meal",
        main_recipe_id=999  # Non-existent recipe
    )

    result = service.create_meal_selection(create_dto)

    assert result is None


def test_create_meal_selection_invalid_side_recipe(session):
    """Test creating meal selection with invalid side recipe ID."""
    # Create only main recipe
    main_recipe = Recipe(recipe_name="Main Dish", recipe_category="Test", meal_type="Dinner")
    session.add(main_recipe)
    session.commit()

    service = PlannerService(session)

    create_dto = MealSelectionCreateDTO(
        meal_name="Test Meal",
        main_recipe_id=main_recipe.id,
        side_recipe_1_id=999  # Non-existent recipe
    )

    result = service.create_meal_selection(create_dto)

    assert result is None


def test_get_meal_selection_success(session):
    """Test getting an existing meal selection."""
    # Create recipe and meal
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()

    service = PlannerService(session)

    result = service.get_meal_selection(meal.id)

    assert result is not None
    assert result.id == meal.id
    assert result.meal_name == "Test Meal"


def test_get_meal_selection_not_found(session):
    """Test getting a non-existent meal selection."""
    service = PlannerService(session)

    result = service.get_meal_selection(999)

    assert result is None


def test_update_meal_selection_success(session):
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

    service = PlannerService(session)

    update_dto = MealSelectionUpdateDTO(
        meal_name="Updated Meal",
        main_recipe_id=recipe2.id
    )

    result = service.update_meal_selection(meal.id, update_dto)

    assert result is not None
    assert result.meal_name == "Updated Meal"
    assert result.main_recipe_id == recipe2.id


def test_update_meal_selection_not_found(session):
    """Test updating a non-existent meal selection."""
    service = PlannerService(session)

    update_dto = MealSelectionUpdateDTO(meal_name="Updated Meal")

    result = service.update_meal_selection(999, update_dto)

    assert result is None


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

    service = PlannerService(session)

    results = service.get_all_meal_selections()

    assert len(results) == 2
    meal_names = {result.meal_name for result in results}
    assert meal_names == {"Meal 1", "Meal 2"}


def test_delete_meal_selection_success(session):
    """Test deleting an existing meal selection."""
    # Create recipe and meal
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()
    meal_id = meal.id

    service = PlannerService(session)

    result = service.delete_meal_selection(meal_id)

    assert result is True

    # Verify deletion
    deleted_meal = service.get_meal_selection(meal_id)
    assert deleted_meal is None


def test_delete_meal_selection_not_found(session):
    """Test deleting a non-existent meal selection."""
    service = PlannerService(session)

    result = service.delete_meal_selection(999)

    assert result is False


def test_save_meal_plan(session):
    """Test saving a meal plan."""
    # Create recipes and meals
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    meal1 = MealSelection(meal_name="Meal 1", main_recipe_id=recipe1.id)
    meal2 = MealSelection(meal_name="Meal 2", main_recipe_id=recipe2.id)
    session.add_all([meal1, meal2])
    session.commit()

    service = PlannerService(session)

    # Save meal plan
    result = service.saveMealPlan([meal1.id, meal2.id])

    assert result.success is True
    assert result.saved_count == 2

    # Verify saved plan
    saved_plan = service.get_saved_meal_plan()
    assert len(saved_plan) == 2


def test_clear_meal_plan(session):
    """Test clearing the meal plan."""
    # Create and save a meal plan first
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal = MealSelection(meal_name="Test Meal", main_recipe_id=recipe.id)
    session.add(meal)
    session.commit()

    service = PlannerService(session)
    service.saveMealPlan([meal.id])

    # Verify plan exists
    assert len(service.get_saved_meal_plan()) == 1

    # Clear plan
    result = service.clear_meal_plan()

    assert result is True

    # Verify plan is cleared
    assert len(service.get_saved_meal_plan()) == 0


def test_search_meals_by_recipe(session):
    """Test searching meals by recipe ID."""
    # Create recipes
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    # Create meals with recipe1 as main and side
    meal1 = MealSelection(meal_name="Meal 1", main_recipe_id=recipe1.id)
    meal2 = MealSelection(meal_name="Meal 2", main_recipe_id=recipe2.id, side_recipe_1_id=recipe1.id)
    session.add_all([meal1, meal2])
    session.commit()

    service = PlannerService(session)

    # Search for meals containing recipe1
    results = service.search_meals_by_recipe(recipe1.id)

    assert len(results) == 2  # Both meals contain recipe1
    meal_names = {result.meal_name for result in results}
    assert meal_names == {"Meal 1", "Meal 2"}


def test_search_meals_by_name(session):
    """Test searching meals by name pattern."""
    # Create recipe and meals
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    meal1 = MealSelection(meal_name="Italian Dinner", main_recipe_id=recipe.id)
    meal2 = MealSelection(meal_name="Chinese Dinner", main_recipe_id=recipe.id)
    meal3 = MealSelection(meal_name="Italian Lunch", main_recipe_id=recipe.id)
    session.add_all([meal1, meal2, meal3])
    session.commit()

    service = PlannerService(session)

    # Search for meals with "Italian" in name
    results = service.search_meals_by_name("Italian")

    assert len(results) == 2
    meal_names = {result.meal_name for result in results}
    assert meal_names == {"Italian Dinner", "Italian Lunch"}


def test_validate_meal_plan(session):
    """Test validating a meal plan."""
    # Create recipes and meals
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    meal1 = MealSelection(meal_name="Meal 1", main_recipe_id=recipe1.id)
    meal2 = MealSelection(meal_name="Meal 2", main_recipe_id=recipe2.id)
    session.add_all([meal1, meal2])
    session.commit()

    service = PlannerService(session)

    # Validate valid meal plan
    validation = service.validate_meal_plan([meal1.id, meal2.id])

    assert validation.is_valid is True
    assert validation.total_meals == 2
    assert validation.invalid_meal_ids == []

    # Validate invalid meal plan
    validation = service.validate_meal_plan([meal1.id, 999])

    assert validation.is_valid is False
    assert validation.total_meals == 2
    assert 999 in validation.invalid_meal_ids
