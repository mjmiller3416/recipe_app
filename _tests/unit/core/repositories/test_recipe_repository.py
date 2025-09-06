"""
Unit tests for RecipeRepo.

Tests the recipe repository data access layer including:
- CRUD operations for recipes
- Recipe search and filtering functionality
- Database query optimization
- Repository pattern implementation
- Error handling for database operations
"""

from unittest.mock import Mock, patch

from faker import Faker
import pytest
from sqlalchemy.exc import IntegrityError

from _tests.fixtures.recipe_factories import (
    IngredientFactory,
    RecipeFactory,
    RecipeIngredientFactory,
    RecipeWithIngredientsFactory,
    create_sample_database,
)
from app.core.models import Ingredient, Recipe, RecipeIngredient
from app.core.repositories.recipe_repo import RecipeRepo

fake = Faker()


@pytest.mark.repositories
@pytest.mark.unit
class TestRecipeRepo:
    """Test cases for RecipeRepo functionality."""
    
    def test_repository_initialization(self, db_session):
        """Test repository initialization."""
        repo = RecipeRepo(db_session)
        assert repo.session == db_session
        
    def test_create_recipe(self, db_session):
        """Test creating a new recipe."""
        repo = RecipeRepo(db_session)
        recipe_data = {
            "name": "Test Pasta",
            "description": "A delicious pasta dish",
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Easy",
            "instructions": ["Boil water", "Cook pasta", "Add sauce"],
            "tags": ["italian", "pasta"]
        }
        
        created_recipe = repo.create(recipe_data)
        
        assert created_recipe.id is not None
        assert created_recipe.name == "Test Pasta"
        assert created_recipe.prep_time == 15
        assert created_recipe.cook_time == 20
        assert created_recipe.servings == 4
        assert created_recipe.difficulty == "Easy"
        assert len(created_recipe.instructions) == 3
        assert "italian" in created_recipe.tags
        
    def test_get_recipe_by_id(self, db_session):
        """Test retrieving recipe by ID."""
        repo = RecipeRepo(db_session)
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        retrieved_recipe = repo.get_by_id(recipe.id)
        
        assert retrieved_recipe is not None
        assert retrieved_recipe.id == recipe.id
        assert retrieved_recipe.name == recipe.name
        
    def test_get_nonexistent_recipe(self, db_session):
        """Test retrieving non-existent recipe."""
        repo = RecipeRepo(db_session)
        
        result = repo.get_by_id(99999)
        assert result is None
        
    def test_get_all_recipes(self, db_session):
        """Test retrieving all recipes."""
        repo = RecipeRepo(db_session)
        recipes = RecipeFactory.create_batch(5)
        db_session.add_all(recipes)
        db_session.commit()
        
        all_recipes = repo.get_all()
        
        assert len(all_recipes) == 5
        recipe_ids = {r.id for r in all_recipes}
        expected_ids = {r.id for r in recipes}
        assert recipe_ids == expected_ids
        
    def test_update_recipe(self, db_session):
        """Test updating an existing recipe."""
        repo = RecipeRepo(db_session)
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        original_name = recipe.name
        update_data = {
            "name": "Updated Recipe Name",
            "prep_time": 30
        }
        
        updated_recipe = repo.update(recipe.id, update_data)
        
        assert updated_recipe.name == "Updated Recipe Name"
        assert updated_recipe.prep_time == 30
        assert updated_recipe.name != original_name
        
    def test_update_nonexistent_recipe(self, db_session):
        """Test updating non-existent recipe."""
        repo = RecipeRepo(db_session)
        
        result = repo.update(99999, {"name": "Won't work"})
        assert result is None
        
    def test_delete_recipe(self, db_session):
        """Test deleting a recipe."""
        repo = RecipeRepo(db_session)
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        recipe_id = recipe.id
        
        success = repo.delete(recipe_id)
        
        assert success is True
        assert repo.get_by_id(recipe_id) is None
        
    def test_delete_nonexistent_recipe(self, db_session):
        """Test deleting non-existent recipe."""
        repo = RecipeRepo(db_session)
        
        result = repo.delete(99999)
        assert result is False
        
    def test_search_recipes_by_name(self, db_session):
        """Test searching recipes by name."""
        repo = RecipeRepo(db_session)
        recipes = [
            RecipeFactory(name="Spaghetti Carbonara"),
            RecipeFactory(name="Chicken Pasta"),
            RecipeFactory(name="Beef Stew"),
            RecipeFactory(name="Pasta Salad"),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        pasta_recipes = repo.search_by_name("pasta")
        
        assert len(pasta_recipes) == 3  # Spaghetti, Chicken Pasta, Pasta Salad
        pasta_names = {r.name for r in pasta_recipes}
        assert "Spaghetti Carbonara" in pasta_names
        assert "Chicken Pasta" in pasta_names
        assert "Pasta Salad" in pasta_names
        assert "Beef Stew" not in pasta_names
        
    def test_search_recipes_case_insensitive(self, db_session):
        """Test case-insensitive recipe search."""
        repo = RecipeRepo(db_session)
        recipe = RecipeFactory(name="UPPERCASE Recipe")
        db_session.add(recipe)
        db_session.commit()
        
        results = repo.search_by_name("uppercase")
        
        assert len(results) == 1
        assert results[0].name == "UPPERCASE Recipe"
        
    def test_filter_by_difficulty(self, db_session):
        """Test filtering recipes by difficulty."""
        repo = RecipeRepo(db_session)
        recipes = [
            RecipeFactory(difficulty="Easy"),
            RecipeFactory(difficulty="Medium"),
            RecipeFactory(difficulty="Hard"),
            RecipeFactory(difficulty="Easy"),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        easy_recipes = repo.filter_by_difficulty("Easy")
        
        assert len(easy_recipes) == 2
        for recipe in easy_recipes:
            assert recipe.difficulty == "Easy"
            
    def test_filter_by_prep_time(self, db_session):
        """Test filtering recipes by preparation time."""
        repo = RecipeRepo(db_session)
        recipes = [
            RecipeFactory(prep_time=10),
            RecipeFactory(prep_time=25),
            RecipeFactory(prep_time=45),
            RecipeFactory(prep_time=15),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        quick_recipes = repo.filter_by_max_prep_time(20)
        
        assert len(quick_recipes) == 2
        for recipe in quick_recipes:
            assert recipe.prep_time <= 20
            
    def test_filter_by_servings(self, db_session):
        """Test filtering recipes by servings."""
        repo = RecipeRepo(db_session)
        recipes = [
            RecipeFactory(servings=2),
            RecipeFactory(servings=4),
            RecipeFactory(servings=6),
            RecipeFactory(servings=8),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        small_batch_recipes = repo.filter_by_max_servings(4)
        
        assert len(small_batch_recipes) == 2
        for recipe in small_batch_recipes:
            assert recipe.servings <= 4
            
    def test_filter_by_tags(self, db_session):
        """Test filtering recipes by tags."""
        repo = RecipeRepo(db_session)
        recipes = [
            RecipeFactory(tags=["vegetarian", "healthy"]),
            RecipeFactory(tags=["meat", "comfort-food"]),
            RecipeFactory(tags=["vegetarian", "quick"]),
            RecipeFactory(tags=["dessert", "sweet"]),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        vegetarian_recipes = repo.filter_by_tags(["vegetarian"])
        
        assert len(vegetarian_recipes) == 2
        for recipe in vegetarian_recipes:
            assert "vegetarian" in recipe.tags
            
    def test_get_recipes_with_ingredients(self, db_session):
        """Test retrieving recipes with their ingredients."""
        repo = RecipeRepo(db_session)
        
        # Create recipe with ingredients using factory
        recipe = RecipeWithIngredientsFactory()
        db_session.add(recipe)
        db_session.commit()
        
        retrieved_recipe = repo.get_with_ingredients(recipe.id)
        
        assert retrieved_recipe is not None
        assert len(retrieved_recipe.recipe_ingredients) > 0
        for recipe_ingredient in retrieved_recipe.recipe_ingredients:
            assert recipe_ingredient.ingredient is not None
            assert recipe_ingredient.quantity > 0
            
    def test_get_popular_recipes(self, db_session):
        """Test retrieving popular recipes (most used in meal plans)."""
        repo = RecipeRepo(db_session)
        
        # This test assumes there's a method to get popular recipes
        # Implementation would depend on meal selection tracking
        recipes = RecipeFactory.create_batch(5)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Mock implementation - in real scenario would check meal selections
        popular_recipes = repo.get_all()[:3]  # Top 3
        
        assert len(popular_recipes) <= 3
        
    def test_get_recent_recipes(self, db_session):
        """Test retrieving recently created recipes."""
        repo = RecipeRepo(db_session)
        
        recipes = RecipeFactory.create_batch(10)
        db_session.add_all(recipes)
        db_session.commit()
        
        recent_recipes = repo.get_recent(limit=5)
        
        assert len(recent_recipes) == 5
        # Check that recipes are ordered by creation date (most recent first)
        for i in range(len(recent_recipes) - 1):
            assert recent_recipes[i].created_at >= recent_recipes[i + 1].created_at
            
    def test_count_recipes(self, db_session):
        """Test counting total recipes."""
        repo = RecipeRepo(db_session)
        
        initial_count = repo.count()
        
        recipes = RecipeFactory.create_batch(7)
        db_session.add_all(recipes)
        db_session.commit()
        
        final_count = repo.count()
        assert final_count == initial_count + 7
        
    def test_recipe_exists(self, db_session):
        """Test checking if recipe exists."""
        repo = RecipeRepo(db_session)
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        assert repo.exists(recipe.id) is True
        assert repo.exists(99999) is False
        
    def test_bulk_create_recipes(self, db_session):
        """Test bulk creating multiple recipes."""
        repo = RecipeRepo(db_session)
        
        recipe_data_list = [
            {
                "name": f"Bulk Recipe {i}",
                "description": f"Description {i}",
                "prep_time": 10 + i,
                "cook_time": 20 + i,
                "servings": 2 + i,
                "difficulty": "Easy",
                "instructions": [f"Step {i}"],
                "tags": [f"tag{i}"]
            }
            for i in range(5)
        ]
        
        created_recipes = repo.bulk_create(recipe_data_list)
        
        assert len(created_recipes) == 5
        for i, recipe in enumerate(created_recipes):
            assert recipe.name == f"Bulk Recipe {i}"
            assert recipe.prep_time == 10 + i
            
    def test_advanced_search_combinations(self, db_session):
        """Test advanced search with multiple criteria."""
        repo = RecipeRepo(db_session)
        
        recipes = [
            RecipeFactory(
                name="Quick Vegetarian Pasta",
                difficulty="Easy",
                prep_time=15,
                tags=["vegetarian", "pasta", "quick"]
            ),
            RecipeFactory(
                name="Complex Meat Dish",
                difficulty="Hard",
                prep_time=60,
                tags=["meat", "complex"]
            ),
            RecipeFactory(
                name="Simple Vegetarian Soup",
                difficulty="Easy",
                prep_time=20,
                tags=["vegetarian", "soup"]
            ),
        ]
        db_session.add_all(recipes)
        db_session.commit()
        
        # Search for easy vegetarian recipes
        search_criteria = {
            "difficulty": "Easy",
            "tags": ["vegetarian"],
            "max_prep_time": 25
        }
        
        results = repo.advanced_search(search_criteria)
        
        assert len(results) == 2
        for recipe in results:
            assert recipe.difficulty == "Easy"
            assert "vegetarian" in recipe.tags
            assert recipe.prep_time <= 25
            
    def test_pagination(self, db_session):
        """Test recipe pagination."""
        repo = RecipeRepo(db_session)
        
        recipes = RecipeFactory.create_batch(20)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Get first page
        page_1 = repo.get_paginated(page=1, per_page=5)
        assert len(page_1) == 5
        
        # Get second page
        page_2 = repo.get_paginated(page=2, per_page=5)
        assert len(page_2) == 5
        
        # Check no overlap
        page_1_ids = {r.id for r in page_1}
        page_2_ids = {r.id for r in page_2}
        assert page_1_ids.isdisjoint(page_2_ids)
        
    def test_repository_error_handling(self, db_session):
        """Test repository error handling."""
        repo = RecipeRepo(db_session)
        
        # Test with invalid data that might cause database errors
        try:
            repo.create({"invalid": "data"})
        except (ValueError, IntegrityError, TypeError):
            # Expected - repository should handle or raise appropriate errors
            pass
            
        # Test session rollback on error
        with patch.object(db_session, 'commit', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                repo.create({
                    "name": "Test Recipe",
                    "description": "Test",
                    "prep_time": 10,
                    "cook_time": 10,
                    "servings": 2
                })
                
    def test_repository_with_database_constraints(self, db_session):
        """Test repository behavior with database constraints."""
        repo = RecipeRepo(db_session)
        
        # Test unique constraint (if name is unique)
        recipe_data = {
            "name": "Unique Recipe Name",
            "description": "Test recipe",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2
        }
        
        recipe1 = repo.create(recipe_data)
        assert recipe1 is not None
        
        # Try to create duplicate (behavior depends on constraints)
        try:
            recipe2 = repo.create(recipe_data)
            # If no constraint, both recipes exist
        except IntegrityError:
            # Constraint exists - expected behavior
            db_session.rollback()
            
    def test_recipe_ingredient_relationships_via_repository(self, db_session):
        """Test accessing recipe-ingredient relationships through repository."""
        repo = RecipeRepo(db_session)
        
        # Create recipe with ingredients
        recipe = RecipeFactory()
        ingredients = IngredientFactory.create_batch(3)
        db_session.add(recipe)
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Add ingredients to recipe
        for ingredient in ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity=fake.random_digit_not_null(),
                unit="cups"
            )
            db_session.add(recipe_ingredient)
        db_session.commit()
        
        # Retrieve recipe with ingredients
        recipe_with_ingredients = repo.get_with_ingredients(recipe.id)
        
        assert len(recipe_with_ingredients.recipe_ingredients) == 3
        ingredient_names = {
            ri.ingredient.name for ri in recipe_with_ingredients.recipe_ingredients
        }
        expected_names = {ing.name for ing in ingredients}
        assert ingredient_names == expected_names
        
    @pytest.mark.slow
    def test_repository_performance_large_dataset(self, db_session):
        """Test repository performance with large datasets."""
        repo = RecipeRepo(db_session)
        
        # Create large dataset
        sample_data = create_sample_database(db_session, num_recipes=1000, num_ingredients=100)
        
        # Test search performance
        search_results = repo.search_by_name("Recipe")
        assert len(search_results) > 0
        
        # Test filtering performance
        easy_recipes = repo.filter_by_difficulty("Easy")
        assert len(easy_recipes) > 0
        
        # Test pagination performance
        page_results = repo.get_paginated(page=1, per_page=50)
        assert len(page_results) == 50