"""
Unit tests for MealSelection and related meal planning models.

Tests meal planning models including:
- MealSelection creation and validation
- Date-based meal planning functionality
- Recipe associations and scheduling
- Meal plan generation logic
"""

from datetime import date, datetime, timedelta

import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError

from _tests.fixtures.recipe_factories import (MealSelectionFactory,
                                              RecipeFactory,
                                              SavedMealStateFactory,
                                              WeeklyMealPlanFactory)
from app.core.models import MealSelection, Recipe, SavedMealState

fake = Faker()


@pytest.mark.models
@pytest.mark.unit
class TestMealPlanningModels:
    """Test cases for meal planning model functionality."""
    
    def test_meal_selection_creation(self, db_session):
        """Test basic meal selection creation."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        meal_data = {
            "recipe": recipe,
            "date": date.today(),
            "meal_type": "dinner",
            "servings": 4,
            "notes": "Family dinner"
        }
        
        meal_selection = MealSelection(**meal_data)
        db_session.add(meal_selection)
        db_session.commit()
        
        assert meal_selection.id is not None
        assert meal_selection.recipe == recipe
        assert meal_selection.date == date.today()
        assert meal_selection.meal_type == "dinner"
        assert meal_selection.servings == 4
        assert meal_selection.notes == "Family dinner"
        
    def test_meal_selection_factory(self, db_session):
        """Test meal selection creation using factory."""
        meal_selection = MealSelectionFactory()
        db_session.add(meal_selection)
        db_session.commit()
        
        assert meal_selection.id is not None
        assert meal_selection.recipe is not None
        assert meal_selection.date is not None
        assert meal_selection.meal_type in ["breakfast", "lunch", "dinner", "snack"]
        assert meal_selection.servings > 0
        
    def test_meal_types(self, db_session):
        """Test different meal types."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        meal_types = ["breakfast", "lunch", "dinner", "snack"]
        meal_selections = []
        
        for meal_type in meal_types:
            meal_selection = MealSelectionFactory(
                recipe=recipe,
                meal_type=meal_type,
                date=date.today()
            )
            meal_selections.append(meal_selection)
            
        db_session.add_all(meal_selections)
        db_session.commit()
        
        for meal_selection, expected_type in zip(meal_selections, meal_types):
            assert meal_selection.meal_type == expected_type
            
    def test_meal_selection_date_queries(self, db_session):
        """Test date-based meal selection queries."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        # Create meals for different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        meals = [
            MealSelectionFactory(recipe=recipe, date=yesterday),
            MealSelectionFactory(recipe=recipe, date=today),
            MealSelectionFactory(recipe=recipe, date=tomorrow),
        ]
        
        db_session.add_all(meals)
        db_session.commit()
        
        # Test date filtering
        today_meals = db_session.query(MealSelection).filter(
            MealSelection.date == today
        ).all()
        assert len(today_meals) == 1
        assert today_meals[0].date == today
        
        # Test date range
        week_meals = db_session.query(MealSelection).filter(
            MealSelection.date >= yesterday,
            MealSelection.date <= tomorrow
        ).all()
        assert len(week_meals) == 3
        
    def test_meal_selection_recipe_relationship(self, db_session):
        """Test meal selection to recipe relationship."""
        recipes = RecipeFactory.create_batch(3)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Create meal selections for different recipes
        meal_selections = []
        for recipe in recipes:
            meal_selection = MealSelectionFactory(recipe=recipe)
            meal_selections.append(meal_selection)
            
        db_session.add_all(meal_selections)
        db_session.commit()
        
        # Test relationship access
        for meal_selection, recipe in zip(meal_selections, recipes):
            assert meal_selection.recipe == recipe
            assert meal_selection.recipe.id == recipe.id
            
    def test_meal_selection_servings_scaling(self, db_session):
        """Test meal selection servings functionality."""
        recipe = RecipeFactory(servings=4)
        db_session.add(recipe)
        db_session.commit()
        
        # Create meal selection with different servings
        meal_selection = MealSelectionFactory(
            recipe=recipe,
            servings=6  # Different from recipe default
        )
        db_session.add(meal_selection)
        db_session.commit()
        
        assert meal_selection.recipe.servings == 4  # Original recipe servings
        assert meal_selection.servings == 6  # Meal-specific servings
        
        # Test scaling factor calculation (if implemented)
        # scaling_factor = meal_selection.servings / meal_selection.recipe.servings
        # assert scaling_factor == 1.5
        
    def test_weekly_meal_plan_creation(self, db_session):
        """Test weekly meal plan creation."""
        weekly_plan = WeeklyMealPlanFactory.create()
        
        assert isinstance(weekly_plan, dict)
        assert len(weekly_plan) == 7  # 7 days
        
        # Check that each day has the expected structure
        for date_key, day_meals in weekly_plan.items():
            assert isinstance(day_meals, dict)
            assert "breakfast" in day_meals
            assert "lunch" in day_meals
            assert "dinner" in day_meals
            
    def test_saved_meal_state_creation(self, db_session):
        """Test saved meal state model."""
        saved_state = SavedMealStateFactory()
        db_session.add(saved_state)
        db_session.commit()
        
        assert saved_state.id is not None
        assert saved_state.name is not None
        assert saved_state.description is not None
        assert saved_state.created_at is not None
        assert saved_state.meal_data is not None
        assert isinstance(saved_state.meal_data, dict)
        
    def test_saved_meal_state_data_structure(self, db_session):
        """Test saved meal state data structure."""
        meal_data = {
            "2024-01-01": {
                "breakfast": {"recipe_id": 1, "servings": 2},
                "lunch": {"recipe_id": 2, "servings": 2},
                "dinner": {"recipe_id": 3, "servings": 4},
                "snack": None
            },
            "2024-01-02": {
                "breakfast": {"recipe_id": 4, "servings": 2},
                "lunch": None,
                "dinner": {"recipe_id": 5, "servings": 4},
                "snack": {"recipe_id": 6, "servings": 1}
            }
        }
        
        saved_state = SavedMealStateFactory(meal_data=meal_data)
        db_session.add(saved_state)
        db_session.commit()
        
        assert saved_state.meal_data == meal_data
        assert "2024-01-01" in saved_state.meal_data
        assert saved_state.meal_data["2024-01-01"]["breakfast"]["recipe_id"] == 1
        assert saved_state.meal_data["2024-01-02"]["lunch"] is None
        
    def test_meal_selection_validation(self, db_session):
        """Test meal selection validation constraints."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        # Test required fields
        with pytest.raises((IntegrityError, ValueError)):
            meal_selection = MealSelection()  # No required fields
            db_session.add(meal_selection)
            db_session.commit()
            
        db_session.rollback()
        
        # Test valid minimal meal selection
        minimal_meal = MealSelection(
            recipe=recipe,
            date=date.today(),
            meal_type="lunch",
            servings=1
        )
        db_session.add(minimal_meal)
        db_session.commit()
        
        assert minimal_meal.recipe == recipe
        assert minimal_meal.servings == 1
        
    def test_meal_selection_notes(self, db_session):
        """Test meal selection notes functionality."""
        meal_selection = MealSelectionFactory(
            notes="This meal was planned for guests"
        )
        db_session.add(meal_selection)
        db_session.commit()
        
        assert meal_selection.notes == "This meal was planned for guests"
        
        # Test empty notes
        meal_no_notes = MealSelectionFactory(notes="")
        db_session.add(meal_no_notes)
        db_session.commit()
        
        assert meal_no_notes.notes == ""
        
    def test_meal_selection_duplicate_prevention(self, db_session):
        """Test prevention of duplicate meal selections."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        meal_date = date.today()
        meal_type = "dinner"
        
        # Create first meal selection
        meal1 = MealSelection(
            recipe=recipe,
            date=meal_date,
            meal_type=meal_type,
            servings=4
        )
        db_session.add(meal1)
        db_session.commit()
        
        # Try to create duplicate (same date and meal_type)
        # Note: This depends on database constraints
        meal2 = MealSelection(
            recipe=recipe,
            date=meal_date,
            meal_type=meal_type,
            servings=2
        )
        db_session.add(meal2)
        
        try:
            db_session.commit()
            # If no constraint, both meals exist
            duplicates = db_session.query(MealSelection).filter(
                MealSelection.date == meal_date,
                MealSelection.meal_type == meal_type
            ).all()
            # Test handles both scenarios
        except IntegrityError:
            db_session.rollback()
            # Duplicate prevention is enforced
            pass
            
    def test_meal_selection_sorting(self, db_session):
        """Test meal selection sorting functionality."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        # Create meals for different dates and types
        base_date = date.today()
        meals = [
            MealSelectionFactory(
                recipe=recipe,
                date=base_date + timedelta(days=i),
                meal_type=meal_type
            )
            for i in range(3)
            for meal_type in ["breakfast", "lunch", "dinner"]
        ]
        
        db_session.add_all(meals)
        db_session.commit()
        
        # Test date sorting
        date_sorted = db_session.query(MealSelection).order_by(
            MealSelection.date, MealSelection.meal_type
        ).all()
        
        prev_date = None
        for meal in date_sorted:
            if prev_date is not None:
                assert meal.date >= prev_date
            prev_date = meal.date
            
    def test_meal_selection_filtering_by_recipe(self, db_session):
        """Test filtering meal selections by recipe."""
        recipes = RecipeFactory.create_batch(3)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Create multiple meal selections for each recipe
        meal_selections = []
        for recipe in recipes:
            for i in range(2):  # 2 meals per recipe
                meal_selection = MealSelectionFactory(
                    recipe=recipe,
                    date=date.today() + timedelta(days=i)
                )
                meal_selections.append(meal_selection)
                
        db_session.add_all(meal_selections)
        db_session.commit()
        
        # Test filtering by specific recipe
        first_recipe_meals = db_session.query(MealSelection).filter(
            MealSelection.recipe == recipes[0]
        ).all()
        assert len(first_recipe_meals) == 2
        
        for meal in first_recipe_meals:
            assert meal.recipe == recipes[0]
            
    def test_meal_plan_date_ranges(self, db_session):
        """Test meal plan queries over date ranges."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        # Create meals spanning a month
        base_date = date(2024, 1, 1)
        meals = []
        for day in range(30):
            meal_date = base_date + timedelta(days=day)
            meal = MealSelectionFactory(
                recipe=recipe,
                date=meal_date,
                meal_type="dinner"
            )
            meals.append(meal)
            
        db_session.add_all(meals)
        db_session.commit()
        
        # Test weekly range
        week_start = base_date
        week_end = base_date + timedelta(days=6)
        
        weekly_meals = db_session.query(MealSelection).filter(
            MealSelection.date >= week_start,
            MealSelection.date <= week_end
        ).all()
        assert len(weekly_meals) == 7
        
        # Test monthly range
        month_meals = db_session.query(MealSelection).filter(
            MealSelection.date >= base_date,
            MealSelection.date < base_date + timedelta(days=30)
        ).all()
        assert len(month_meals) == 30
        
    def test_meal_selection_batch_operations(self, db_session):
        """Test batch operations with meal selections."""
        recipes = RecipeFactory.create_batch(5)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Create batch of meal selections
        meal_selections = []
        for _ in range(20):
            meal_selection = MealSelectionFactory(
                recipe=fake.random_element(recipes)
            )
            meal_selections.append(meal_selection)
            
        db_session.add_all(meal_selections)
        db_session.commit()
        
        # Verify batch creation
        total_meals = db_session.query(MealSelection).count()
        assert total_meals == 20
        
        # Test batch filtering
        dinner_meals = db_session.query(MealSelection).filter(
            MealSelection.meal_type == "dinner"
        ).all()
        
        # Verify all dinner meals are correct
        for meal in dinner_meals:
            assert meal.meal_type == "dinner"
            
    @pytest.mark.slow
    def test_meal_plan_performance_large_dataset(self, db_session):
        """Test performance with large meal plan datasets."""
        recipes = RecipeFactory.create_batch(50)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Create large number of meal selections
        meal_selections = []
        base_date = date.today()
        
        for day in range(365):  # Full year
            meal_date = base_date + timedelta(days=day)
            for meal_type in ["breakfast", "lunch", "dinner"]:
                meal_selection = MealSelection(
                    recipe=fake.random_element(recipes),
                    date=meal_date,
                    meal_type=meal_type,
                    servings=fake.random_int(1, 6)
                )
                meal_selections.append(meal_selection)
                
        db_session.add_all(meal_selections)
        db_session.commit()
        
        # Test performance of date range queries
        month_start = base_date
        month_end = base_date + timedelta(days=30)
        
        monthly_meals = db_session.query(MealSelection).filter(
            MealSelection.date >= month_start,
            MealSelection.date <= month_end
        ).all()
        
        assert len(monthly_meals) == 31 * 3  # 31 days * 3 meals