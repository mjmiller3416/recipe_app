# tests/core/test_integration.py

import pytest
from app.core.services.recipe_service import RecipeService
from app.core.services.ingredient_service import IngredientService
from app.core.services.planner_service import PlannerService
from app.core.services.shopping_service import ShoppingService
from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.dtos.planner_dtos import MealSelectionCreateDTO
from app.core.dtos.shopping_dto import ShoppingListGenerationDTO


def test_full_workflow_integration(session):
    """Test a complete workflow from recipe creation to shopping list generation."""

    # Initialize services
    ingredient_service = IngredientService(session)
    recipe_service = RecipeService(session)
    planner_service = PlannerService(session)
    shopping_service = ShoppingService(session)

    # Step 1: Create a recipe with ingredients
    recipe_dto = RecipeCreateDTO(
        recipe_name="Integration Test Recipe",
        recipe_category="Test",
        meal_type="Dinner",
        total_time=45,
        servings=4,
        directions="Step 1: Prepare\nStep 2: Cook",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Chicken Breast",
                ingredient_category="Meat",
                quantity=2.0,
                unit="lb"
            ),
            RecipeIngredientDTO(
                ingredient_name="Rice",
                ingredient_category="Grains",
                quantity=1.0,
                unit="cup"
            ),
            RecipeIngredientDTO(
                ingredient_name="Onion",
                ingredient_category="Vegetables",
                quantity=1.0,
                unit="piece"
            )
        ]
    )

    created_recipe = recipe_service.create_recipe_with_ingredients(recipe_dto)
    assert created_recipe is not None
    assert created_recipe.recipe_name == "Integration Test Recipe"
    assert len(created_recipe.ingredients) == 3

    # Step 2: Create another recipe for variety
    recipe_dto2 = RecipeCreateDTO(
        recipe_name="Side Dish Recipe",
        recipe_category="Test",
        meal_type="Dinner",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Broccoli",
                ingredient_category="Vegetables",
                quantity=1.0,
                unit="head"
            ),
            RecipeIngredientDTO(
                ingredient_name="Garlic",
                ingredient_category="Vegetables",
                quantity=2.0,
                unit="cloves"
            )
        ]
    )

    side_recipe = recipe_service.create_recipe_with_ingredients(recipe_dto2)
    assert side_recipe is not None

    # Step 3: Create a meal selection combining both recipes
    meal_dto = MealSelectionCreateDTO(
        meal_name="Complete Test Meal",
        main_recipe_id=created_recipe.id,
        side_recipe_1_id=side_recipe.id
    )

    created_meal = planner_service.create_meal_selection(meal_dto)
    assert created_meal is not None
    assert created_meal.meal_name == "Complete Test Meal"

    # Step 4: Save the meal to the meal plan
    save_result = planner_service.save_meal_plan([created_meal.id])
    assert save_result.success is True
    assert save_result.saved_count == 1

    # Step 5: Generate shopping list from the meal plan
    saved_meals = planner_service.get_saved_meal_plan()
    meal_recipe_ids = []
    for meal in saved_meals:
        meal_recipe_ids.append(meal.main_recipe_id)
        if meal.side_recipe_1_id:
            meal_recipe_ids.append(meal.side_recipe_1_id)
        if meal.side_recipe_2_id:
            meal_recipe_ids.append(meal.side_recipe_2_id)
        if meal.side_recipe_3_id:
            meal_recipe_ids.append(meal.side_recipe_3_id)

    shopping_dto = ShoppingListGenerationDTO(
        recipe_ids=meal_recipe_ids,
        clear_existing=True
    )

    shopping_result = shopping_service.generate_shopping_list(shopping_dto)
    assert shopping_result.success is True
    assert shopping_result.items_created == 5  # 3 from main + 2 from side

    # Step 6: Verify the shopping list contains all ingredients
    shopping_list = shopping_service.get_shopping_list()
    ingredient_names = {item.ingredient_name for item in shopping_list.items}
    expected_ingredients = {"Chicken Breast", "Rice", "Onion", "Broccoli", "Garlic"}
    assert ingredient_names == expected_ingredients

    # Step 7: Test shopping list functionality
    # Mark some items as completed
    chicken_item = next(item for item in shopping_list.items if item.ingredient_name == "Chicken Breast")
    rice_item = next(item for item in shopping_list.items if item.ingredient_name == "Rice")

    shopping_service.toggle_item_status(chicken_item.id)
    shopping_service.toggle_item_status(rice_item.id)

    # Verify status changes
    updated_list = shopping_service.get_shopping_list()
    completed_items = [item for item in updated_list.items if item.have]
    assert len(completed_items) == 2

    completed_names = {item.ingredient_name for item in completed_items}
    assert completed_names == {"Chicken Breast", "Rice"}

    # Step 8: Test search functionality
    search_results = shopping_service.search_items("on")  # Should match "Onion"
    assert len(search_results) == 1
    assert search_results[0].ingredient_name == "Onion"

    # Step 9: Test meal plan modification
    # Create a new meal and add it to the plan
    recipe_dto3 = RecipeCreateDTO(
        recipe_name="Dessert Recipe",
        recipe_category="Dessert",
        meal_type="Dessert",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Chocolate",
                ingredient_category="Sweets",
                quantity=100.0,
                unit="g"
            )
        ]
    )

    dessert_recipe = recipe_service.create_recipe_with_ingredients(recipe_dto3)

    dessert_meal_dto = MealSelectionCreateDTO(
        meal_name="Dessert Meal",
        main_recipe_id=dessert_recipe.id
    )

    dessert_meal = planner_service.create_meal_selection(dessert_meal_dto)

    # Add to existing meal plan
    current_saved = planner_service.get_saved_meal_plan()
    current_ids = [meal.id for meal in current_saved]
    current_ids.append(dessert_meal.id)

    save_result = planner_service.save_meal_plan(current_ids)
    assert save_result.success is True
    assert save_result.saved_count == 2

    # Step 10: Final verification
    final_meal_plan = planner_service.get_saved_meal_plan()
    assert len(final_meal_plan) == 2

    meal_names = {meal.meal_name for meal in final_meal_plan}
    assert meal_names == {"Complete Test Meal", "Dessert Meal"}


def test_error_handling_integration(session):
    """Test error handling across services."""

    # Initialize services
    recipe_service = RecipeService(session)
    planner_service = PlannerService(session)
    shopping_service = ShoppingService(session)

    # Test 1: Try to create meal with non-existent recipe
    meal_dto = MealSelectionCreateDTO(
        meal_name="Invalid Meal",
        main_recipe_id=999  # Non-existent
    )

    result = planner_service.create_meal_selection(meal_dto)
    assert result is None

    # Test 2: Try to generate shopping list with non-existent recipes
    shopping_dto = ShoppingListGenerationDTO(recipe_ids=[999, 998])
    result = shopping_service.generate_shopping_list(shopping_dto)

    # Should succeed but create no items
    assert result.success is True
    assert result.items_created == 0

    # Test 3: Try to update non-existent shopping item
    result = shopping_service.toggle_item_status(999)
    assert result is False

    # Test 4: Try to delete non-existent meal
    result = planner_service.delete_meal_selection(999)
    assert result is False


def test_data_consistency_integration(session):
    """Test data consistency across related operations."""

    # Initialize services
    ingredient_service = IngredientService(session)
    recipe_service = RecipeService(session)

    # Create recipe with ingredients
    recipe_dto = RecipeCreateDTO(
        recipe_name="Consistency Test Recipe",
        recipe_category="Test",
        meal_type="Dinner",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Shared Ingredient",
                ingredient_category="Test",
                quantity=1.0,
                unit="cup"
            )
        ]
    )

    recipe1 = recipe_service.create_recipe_with_ingredients(recipe_dto)

    # Create another recipe with the same ingredient
    recipe_dto2 = RecipeCreateDTO(
        recipe_name="Another Recipe",
        recipe_category="Test",
        meal_type="Dinner",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Shared Ingredient",  # Same name and category
                ingredient_category="Test",
                quantity=2.0,
                unit="cup"
            )
        ]
    )

    recipe2 = recipe_service.create_recipe_with_ingredients(recipe_dto2)

    # Verify that the same ingredient entity is used
    all_ingredients = ingredient_service.get_all_ingredients()
    shared_ingredients = [ing for ing in all_ingredients if ing.ingredient_name == "Shared Ingredient"]
    assert len(shared_ingredients) == 1  # Should be only one ingredient entity

    # Verify both recipes reference the same ingredient
    ingredient_id = shared_ingredients[0].id
    assert recipe1.ingredients[0].ingredient_id == ingredient_id
    assert recipe2.ingredients[0].ingredient_id == ingredient_id

    # Verify different quantities are preserved
    assert recipe1.ingredients[0].quantity == 1.0
    assert recipe2.ingredients[0].quantity == 2.0
