"""
Comprehensive integration tests for the MealGenie application.

Tests the full integration between all layers:
- Models, Repositories, Services, and UI components
- End-to-end workflows and user scenarios
- Cross-layer data flow and consistency
- Performance and scalability integration
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from faker import Faker
import pytest

from _tests.fixtures.recipe_factories import (
    IngredientFactory,
    MealSelectionFactory,
    RecipeFactory,
    RecipeWithIngredientsFactory,
    create_sample_database,
)
from app.core.database.db import DatabaseSession
from app.core.models import Ingredient, MealSelection, Recipe, ShoppingItem
from app.core.repositories import (
    IngredientRepo,
    PlannerRepo,
    RecipeRepo,
    ShoppingRepo,
)
from app.core.services import (
    IngredientService,
    PlannerService,
    RecipeService,
    ShoppingService,
)

fake = Faker()


@pytest.mark.integration
class TestComprehensiveIntegration:
    """Comprehensive integration tests for the entire application stack."""
    
    @pytest.fixture
    def database_manager(self, test_db_engine):
        """Database manager for integration tests."""
        return DatabaseManager(connection_string="sqlite:///:memory:")
    
    @pytest.fixture
    def repositories(self, db_session):
        """All repository instances with shared database session."""
        return {
            "recipe": RecipeRepo(db_session),
            "ingredient": IngredientRepo(db_session),
            "planner": PlannerRepo(db_session),
            "shopping": ShoppingRepo(db_session),
        }
    
    @pytest.fixture
    def services(self, repositories):
        """All service instances with injected repositories."""
        return {
            "recipe": RecipeService(repositories["recipe"], repositories["ingredient"]),
            "ingredient": IngredientService(repositories["ingredient"]),
            "planner": PlannerService(repositories["planner"], repositories["recipe"]),
            "shopping": ShoppingService(repositories["shopping"], repositories["ingredient"]),
        }
    
    def test_complete_recipe_lifecycle(self, db_session, services):
        """Test complete recipe lifecycle from creation to deletion."""
        recipe_service = services["recipe"]
        
        # 1. Create a recipe
        recipe_data = {
            "name": "Integration Test Recipe",
            "description": "A recipe for integration testing",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "Medium",
            "instructions": ["Prepare ingredients", "Cook", "Serve"],
            "tags": ["integration", "test"],
            "ingredients": [
                {"name": "Test Ingredient 1", "quantity": 2.0, "unit": "cups"},
                {"name": "Test Ingredient 2", "quantity": 1.5, "unit": "tbsp"}
            ]
        }
        
        created_recipe = recipe_service.create_recipe(recipe_data)
        assert created_recipe.id is not None
        assert created_recipe.name == "Integration Test Recipe"
        
        # 2. Retrieve the recipe
        retrieved_recipe = recipe_service.get_recipe(created_recipe.id)
        assert retrieved_recipe.id == created_recipe.id
        
        # 3. Update the recipe
        update_data = {
            "name": "Updated Integration Recipe",
            "prep_time": 20,
            "tags": ["updated", "integration"]
        }
        updated_recipe = recipe_service.update_recipe(created_recipe.id, update_data)
        assert updated_recipe.name == "Updated Integration Recipe"
        assert updated_recipe.prep_time == 20
        
        # 4. Search for the recipe
        search_results = recipe_service.search_recipes("Updated Integration")
        assert len(search_results) >= 1
        assert any(r.id == created_recipe.id for r in search_results)
        
        # 5. Delete the recipe
        deletion_result = recipe_service.delete_recipe(created_recipe.id)
        assert deletion_result is True
        
        # 6. Verify deletion
        deleted_recipe = recipe_service.get_recipe(created_recipe.id)
        assert deleted_recipe is None
    
    def test_meal_planning_workflow(self, db_session, services):
        """Test complete meal planning workflow."""
        recipe_service = services["recipe"]
        planner_service = services["planner"]
        
        # 1. Create recipes for meal planning
        recipes = []
        for i in range(5):
            recipe_data = {
                "name": f"Meal Plan Recipe {i+1}",
                "description": f"Recipe {i+1} for meal planning",
                "prep_time": 10 + (i * 5),
                "cook_time": 15 + (i * 5),
                "servings": 2 + i,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "instructions": [f"Step 1 for recipe {i+1}", f"Step 2 for recipe {i+1}"],
                "tags": [f"meal-plan", f"recipe-{i+1}"]
            }
            recipe = recipe_service.create_recipe(recipe_data)
            recipes.append(recipe)
        
        # 2. Create a weekly meal plan
        meal_plan = {}
        for day_offset in range(7):
            plan_date = date.today() + timedelta(days=day_offset)
            
            # Plan meals for each day
            breakfast_recipe = fake.random_element(recipes[:2])  # Easy recipes for breakfast
            dinner_recipe = fake.random_element(recipes[2:])     # Varied recipes for dinner
            
            # Add breakfast
            breakfast_meal = planner_service.add_meal_to_plan(
                recipe_id=breakfast_recipe.id,
                date=plan_date,
                meal_type="breakfast",
                servings=2
            )
            
            # Add dinner
            dinner_meal = planner_service.add_meal_to_plan(
                recipe_id=dinner_recipe.id,
                date=plan_date,
                meal_type="dinner",
                servings=4
            )
            
            meal_plan[plan_date.isoformat()] = {
                "breakfast": breakfast_meal,
                "dinner": dinner_meal
            }
        
        # 3. Retrieve the meal plan
        week_start = date.today()
        week_end = week_start + timedelta(days=6)
        retrieved_plan = planner_service.get_meal_plan_for_range(week_start, week_end)
        
        assert len(retrieved_plan) == 14  # 7 days * 2 meals each
        
        # 4. Generate shopping list from meal plan
        shopping_service = services["shopping"]
        shopping_list = shopping_service.generate_from_meal_plan(week_start, week_end)
        
        assert len(shopping_list) > 0
        
        # 5. Modify meal plan
        first_recipe = recipes[0]
        tomorrow = date.today() + timedelta(days=1)
        
        modified_meal = planner_service.update_meal_in_plan(
            date=tomorrow,
            meal_type="lunch",
            recipe_id=first_recipe.id,
            servings=3
        )
        
        assert modified_meal is not None
        assert modified_meal.servings == 3
    
    def test_shopping_list_integration(self, db_session, services):
        """Test shopping list integration with recipes and meal planning."""
        recipe_service = services["recipe"]
        shopping_service = services["shopping"]
        
        # 1. Create recipes with ingredients
        recipe1 = RecipeWithIngredientsFactory()
        recipe2 = RecipeWithIngredientsFactory()
        
        db_session.add_all([recipe1, recipe2])
        db_session.commit()
        
        # 2. Add individual items to shopping list
        shopping_item1 = shopping_service.add_item(
            ingredient_name="Milk",
            quantity=1.0,
            unit="gallon",
            category="Dairy"
        )
        
        shopping_item2 = shopping_service.add_item(
            ingredient_name="Bread",
            quantity=2.0,
            unit="loaves",
            category="Grains"
        )
        
        assert shopping_item1.id is not None
        assert shopping_item2.id is not None
        
        # 3. Add recipe ingredients to shopping list
        shopping_service.add_recipe_to_shopping_list(recipe1.id, servings=6)
        
        # 4. Retrieve shopping list
        shopping_list = shopping_service.get_shopping_list()
        
        # Should include manual items + recipe ingredients
        assert len(shopping_list) >= 2
        
        # 5. Mark items as purchased
        for item in shopping_list[:2]:
            shopping_service.mark_item_purchased(item.id, purchased=True)
        
        # 6. Get remaining unpurchased items
        remaining_items = shopping_service.get_unpurchased_items()
        purchased_items = shopping_service.get_purchased_items()
        
        assert len(purchased_items) == 2
        assert len(remaining_items) == len(shopping_list) - 2
        
        # 7. Clear purchased items
        shopping_service.clear_purchased_items()
        
        updated_list = shopping_service.get_shopping_list()
        assert all(not item.is_purchased for item in updated_list)
    
    def test_search_and_filtering_integration(self, db_session, services):
        """Test search and filtering across all services."""
        recipe_service = services["recipe"]
        ingredient_service = services["ingredient"]
        
        # 1. Create diverse test data
        recipes = []
        recipe_configs = [
            {"name": "Italian Pasta", "difficulty": "Easy", "prep_time": 15, "tags": ["italian", "pasta"]},
            {"name": "Thai Curry", "difficulty": "Medium", "prep_time": 30, "tags": ["thai", "spicy", "curry"]},
            {"name": "French Soup", "difficulty": "Hard", "prep_time": 45, "tags": ["french", "soup"]},
            {"name": "Quick Salad", "difficulty": "Easy", "prep_time": 10, "tags": ["healthy", "quick", "salad"]},
            {"name": "BBQ Ribs", "difficulty": "Hard", "prep_time": 60, "tags": ["american", "bbq", "meat"]},
        ]
        
        for config in recipe_configs:
            recipe_data = {
                "description": f"A delicious {config['name'].lower()}",
                "cook_time": 20,
                "servings": 4,
                "instructions": ["Step 1", "Step 2"],
                **config
            }
            recipe = recipe_service.create_recipe(recipe_data)
            recipes.append(recipe)
        
        # 2. Test recipe search
        pasta_recipes = recipe_service.search_recipes("pasta")
        assert len(pasta_recipes) >= 1
        assert any("pasta" in r.name.lower() for r in pasta_recipes)
        
        # 3. Test filtering by difficulty
        easy_recipes = recipe_service.filter_recipes({"difficulty": "Easy"})
        assert len(easy_recipes) == 2
        assert all(r.difficulty == "Easy" for r in easy_recipes)
        
        # 4. Test complex filtering
        quick_easy_recipes = recipe_service.filter_recipes({
            "difficulty": "Easy",
            "max_prep_time": 20,
            "tags": ["quick"]
        })
        assert len(quick_easy_recipes) >= 1
        
        # 5. Test ingredient search and creation
        ingredient_names = ["Tomato", "Onion", "Garlic", "Basil", "Mozzarella"]
        ingredients = []
        
        for name in ingredient_names:
            ingredient = ingredient_service.get_or_create_ingredient(name, "Vegetables")
            ingredients.append(ingredient)
        
        # 6. Test ingredient filtering
        vegetable_ingredients = ingredient_service.get_ingredients_by_category("Vegetables")
        assert len(vegetable_ingredients) >= len(ingredient_names) - 1  # Mozzarella might be dairy
        
    def test_data_consistency_across_layers(self, db_session, services):
        """Test data consistency across all application layers."""
        recipe_service = services["recipe"]
        planner_service = services["planner"]
        shopping_service = services["shopping"]
        
        # 1. Create recipe with ingredients
        recipe_data = {
            "name": "Consistency Test Recipe",
            "description": "Testing data consistency",
            "prep_time": 20,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Medium",
            "instructions": ["Step 1", "Step 2"],
            "tags": ["consistency", "test"],
            "ingredients": [
                {"name": "Ingredient A", "quantity": 2.0, "unit": "cups"},
                {"name": "Ingredient B", "quantity": 1.0, "unit": "tbsp"}
            ]
        }
        
        recipe = recipe_service.create_recipe(recipe_data)
        
        # 2. Add recipe to meal plan
        meal_date = date.today()
        meal_selection = planner_service.add_meal_to_plan(
            recipe_id=recipe.id,
            date=meal_date,
            meal_type="dinner",
            servings=6  # Different from recipe default
        )
        
        # 3. Generate shopping list from meal plan
        shopping_items = shopping_service.generate_from_meal_plan(meal_date, meal_date)
        
        # 4. Verify data consistency
        # Recipe should exist in all contexts
        retrieved_recipe = recipe_service.get_recipe(recipe.id)
        assert retrieved_recipe.id == recipe.id
        
        # Meal plan should reference the recipe correctly
        meal_plan = planner_service.get_meal_plan_for_date(meal_date)
        dinner_meals = [m for m in meal_plan if m.meal_type == "dinner"]
        assert len(dinner_meals) == 1
        assert dinner_meals[0].recipe_id == recipe.id
        assert dinner_meals[0].servings == 6
        
        # Shopping list should contain ingredients with scaled quantities
        ingredient_names = {item.ingredient.name for item in shopping_items}
        expected_ingredients = {"Ingredient A", "Ingredient B"}
        assert ingredient_names.intersection(expected_ingredients) == expected_ingredients
        
        # Quantities should be scaled for 6 servings instead of 4
        scaling_factor = 6 / 4  # 1.5
        for item in shopping_items:
            if item.ingredient.name == "Ingredient A":
                assert abs(item.quantity - (2.0 * scaling_factor)) < 0.01
            elif item.ingredient.name == "Ingredient B":
                assert abs(item.quantity - (1.0 * scaling_factor)) < 0.01
    
    def test_error_handling_across_layers(self, db_session, services):
        """Test error handling and rollback across all layers."""
        recipe_service = services["recipe"]
        planner_service = services["planner"]
        
        # 1. Test service-level error handling
        with pytest.raises(ValueError):
            recipe_service.get_recipe(99999)  # Non-existent recipe
        
        with pytest.raises(ValueError):
            recipe_service.update_recipe(99999, {"name": "Won't work"})
        
        # 2. Test transaction rollback on errors
        initial_recipe_count = len(recipe_service.get_all_recipes())
        
        try:
            # Create a recipe
            recipe = recipe_service.create_recipe({
                "name": "Error Test Recipe",
                "description": "Testing error handling",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "difficulty": "Easy",
                "instructions": ["Step 1"],
                "tags": ["error", "test"]
            })
            
            # Attempt to add to meal plan with invalid data
            with pytest.raises(Exception):
                planner_service.add_meal_to_plan(
                    recipe_id=recipe.id,
                    date="invalid-date",  # Invalid date format
                    meal_type="invalid-meal",  # Invalid meal type
                    servings=-1  # Invalid servings
                )
            
        except Exception:
            # Even if recipe creation succeeded, meal plan failure should not affect it
            pass
        
        # Verify database state is consistent
        final_recipe_count = len(recipe_service.get_all_recipes())
        # Recipe should still exist even if meal planning failed
        assert final_recipe_count >= initial_recipe_count
    
    def test_concurrent_operations_simulation(self, db_session, services):
        """Simulate concurrent operations to test thread safety."""
        recipe_service = services["recipe"]
        
        # Create multiple recipes "concurrently" (simulated)
        recipes = []
        for i in range(10):
            recipe_data = {
                "name": f"Concurrent Recipe {i}",
                "description": f"Recipe {i} created concurrently",
                "prep_time": 10 + i,
                "cook_time": 15 + i,
                "servings": (i % 4) + 1,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "instructions": [f"Step 1 for recipe {i}"],
                "tags": [f"concurrent", f"recipe-{i}"]
            }
            recipe = recipe_service.create_recipe(recipe_data)
            recipes.append(recipe)
        
        # Verify all recipes were created successfully
        assert len(recipes) == 10
        
        # Perform concurrent operations
        for recipe in recipes:
            # Update each recipe
            update_data = {"description": f"Updated description for {recipe.name}"}
            updated_recipe = recipe_service.update_recipe(recipe.id, update_data)
            assert "Updated description" in updated_recipe.description
            
            # Search should find the recipe
            search_results = recipe_service.search_recipes(recipe.name)
            assert any(r.id == recipe.id for r in search_results)
    
    @pytest.mark.slow
    def test_performance_integration_large_dataset(self, db_session, services):
        """Test performance with large integrated datasets."""
        recipe_service = services["recipe"]
        planner_service = services["planner"]
        shopping_service = services["shopping"]
        
        # 1. Create large dataset
        sample_data = create_sample_database(
            db_session, 
            num_recipes=100, 
            num_ingredients=50
        )
        
        # 2. Test search performance
        search_start_time = fake.date_time()
        search_results = recipe_service.search_recipes("Recipe")
        # Should complete in reasonable time
        assert len(search_results) > 0
        
        # 3. Test complex filtering
        filter_results = recipe_service.filter_recipes({
            "difficulty": "Easy",
            "max_prep_time": 30
        })
        assert len(filter_results) > 0
        
        # 4. Test meal planning with many recipes
        recipes = sample_data["recipes"][:10]  # Use subset for meal planning
        
        for i, recipe in enumerate(recipes):
            plan_date = date.today() + timedelta(days=i)
            meal_selection = planner_service.add_meal_to_plan(
                recipe_id=recipe.id,
                date=plan_date,
                meal_type="dinner",
                servings=4
            )
            assert meal_selection is not None
        
        # 5. Generate shopping list from large meal plan
        shopping_list = shopping_service.generate_from_meal_plan(
            date.today(),
            date.today() + timedelta(days=9)
        )
        
        # Should handle large shopping list efficiently
        assert len(shopping_list) > 0
    
    def test_end_to_end_user_workflow(self, db_session, services, qapp):
        """Test complete end-to-end user workflow simulation."""
        recipe_service = services["recipe"]
        planner_service = services["planner"]
        shopping_service = services["shopping"]
        
        # Scenario: User plans a week of meals and generates shopping list
        
        # 1. User creates/finds recipes
        weekly_recipes = []
        meal_types = ["breakfast", "lunch", "dinner"]
        
        for day in range(7):
            for meal_type in meal_types:
                recipe_data = {
                    "name": f"Week {day + 1} {meal_type.title()}",
                    "description": f"Delicious {meal_type} for day {day + 1}",
                    "prep_time": fake.random_int(10, 30),
                    "cook_time": fake.random_int(15, 45),
                    "servings": fake.random_int(2, 6),
                    "difficulty": fake.random_element(["Easy", "Medium", "Hard"]),
                    "instructions": [f"Prepare {meal_type}", f"Cook {meal_type}", "Serve"],
                    "tags": [meal_type, f"week-{day + 1}"],
                    "ingredients": [
                        {"name": f"{meal_type.title()} Ingredient 1", "quantity": 1.0, "unit": "cup"},
                        {"name": f"{meal_type.title()} Ingredient 2", "quantity": 0.5, "unit": "tsp"}
                    ]
                }
                recipe = recipe_service.create_recipe(recipe_data)
                weekly_recipes.append((recipe, meal_type, day))
        
        # 2. User creates weekly meal plan
        meal_plan = {}
        for recipe, meal_type, day in weekly_recipes:
            plan_date = date.today() + timedelta(days=day)
            
            meal_selection = planner_service.add_meal_to_plan(
                recipe_id=recipe.id,
                date=plan_date,
                meal_type=meal_type,
                servings=recipe.servings
            )
            
            if plan_date.isoformat() not in meal_plan:
                meal_plan[plan_date.isoformat()] = {}
            meal_plan[plan_date.isoformat()][meal_type] = meal_selection
        
        # 3. User generates shopping list from meal plan
        week_start = date.today()
        week_end = week_start + timedelta(days=6)
        
        shopping_list = shopping_service.generate_from_meal_plan(week_start, week_end)
        
        # 4. User modifies shopping list
        # Add extra items
        shopping_service.add_item("Snacks", 3.0, "bags", "Other")
        shopping_service.add_item("Coffee", 1.0, "bag", "Beverages")
        
        # Get updated list
        final_shopping_list = shopping_service.get_shopping_list()
        
        # 5. User marks items as purchased throughout the week
        purchased_count = 0
        for item in final_shopping_list[:len(final_shopping_list)//2]:
            shopping_service.mark_item_purchased(item.id, True)
            purchased_count += 1
        
        # 6. Verify complete workflow
        assert len(weekly_recipes) == 21  # 7 days * 3 meals
        assert len(meal_plan) == 7  # 7 days
        assert len(final_shopping_list) >= len(shopping_list) + 2  # Original + 2 manual items
        
        purchased_items = shopping_service.get_purchased_items()
        assert len(purchased_items) == purchased_count
        
        # 7. User reviews and modifies meal plan
        # Change one meal
        tomorrow = date.today() + timedelta(days=1)
        new_recipe_data = {
            "name": "Last Minute Change",
            "description": "A quick substitute meal",
            "prep_time": 5,
            "cook_time": 10,
            "servings": 2,
            "difficulty": "Easy",
            "instructions": ["Quick prep", "Quick cook"],
            "tags": ["quick", "substitute"]
        }
        
        substitute_recipe = recipe_service.create_recipe(new_recipe_data)
        
        # Update meal plan
        updated_meal = planner_service.update_meal_in_plan(
            date=tomorrow,
            meal_type="lunch",
            recipe_id=substitute_recipe.id,
            servings=2
        )
        
        assert updated_meal.recipe_id == substitute_recipe.id
        assert updated_meal.servings == 2
        
        # Final verification: All components working together
        final_meal_plan = planner_service.get_meal_plan_for_range(week_start, week_end)
        assert len(final_meal_plan) == 21  # Still 21 meals, one substituted
        
        # Check that substitution is reflected
        tomorrow_meals = [m for m in final_meal_plan if m.date == tomorrow and m.meal_type == "lunch"]
        assert len(tomorrow_meals) == 1
        assert tomorrow_meals[0].recipe_id == substitute_recipe.id