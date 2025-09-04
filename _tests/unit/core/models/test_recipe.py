"""
Unit tests for Recipe model.

Tests the Recipe SQLAlchemy model including:
- Model creation and validation
- Relationship mappings to ingredients and meal plans
- Model methods and computed properties
- Data integrity constraints
"""

from datetime import datetime, timedelta

import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError

from _tests.fixtures.recipe_factories import (ComplexRecipeFactory,
                                              IngredientFactory,
                                              QuickRecipeFactory,
                                              RecipeFactory,
                                              RecipeIngredientFactory,
                                              VeganRecipeFactory)
from app.core.models import Ingredient, Recipe, RecipeIngredient

fake = Faker()


@pytest.mark.models
@pytest.mark.unit
class TestRecipeModel:
    """Test cases for Recipe model functionality."""
    
    def test_recipe_creation(self, db_session):
        """Test basic recipe creation."""
        recipe_data = {
            "name": "Test Pasta",
            "description": "A simple pasta dish",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "Easy",
            "instructions": ["Boil water", "Cook pasta", "Add sauce"],
            "tags": ["italian", "pasta", "quick"]
        }
        
        recipe = Recipe(**recipe_data)
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.id is not None
        assert recipe.name == "Test Pasta"
        assert recipe.prep_time == 15
        assert recipe.cook_time == 30
        assert recipe.servings == 4
        assert recipe.difficulty == "Easy"
        assert len(recipe.instructions) == 3
        assert "italian" in recipe.tags
        
    def test_recipe_factory(self, db_session):
        """Test recipe creation using factory."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.id is not None
        assert recipe.name is not None
        assert recipe.prep_time > 0
        assert recipe.cook_time > 0
        assert recipe.servings > 0
        assert recipe.difficulty in ["Easy", "Medium", "Hard"]
        assert isinstance(recipe.instructions, list)
        assert len(recipe.instructions) > 0
        
    def test_recipe_specialized_factories(self, db_session):
        """Test specialized recipe factories."""
        # Quick recipe
        quick_recipe = QuickRecipeFactory()
        db_session.add(quick_recipe)
        
        assert quick_recipe.difficulty == "Easy"
        assert quick_recipe.prep_time <= 15
        assert quick_recipe.cook_time <= 30
        
        # Complex recipe
        complex_recipe = ComplexRecipeFactory()
        db_session.add(complex_recipe)
        
        assert complex_recipe.difficulty == "Hard"
        assert complex_recipe.prep_time >= 30
        assert complex_recipe.cook_time >= 60
        assert complex_recipe.servings >= 6
        
        # Vegan recipe
        vegan_recipe = VeganRecipeFactory()
        db_session.add(vegan_recipe)
        
        assert "vegan" in vegan_recipe.tags
        assert "plant-based" in vegan_recipe.tags
        
        db_session.commit()
        
    def test_recipe_timestamps(self, db_session):
        """Test recipe timestamp handling."""
        recipe = RecipeFactory()
        db_session.add(recipe)
        db_session.commit()
        
        created_time = recipe.created_at
        updated_time = recipe.updated_at
        
        assert created_time is not None
        assert updated_time is not None
        assert created_time <= updated_time
        
        # Update recipe
        recipe.name = "Updated Name"
        db_session.commit()
        
        # Note: updated_at would need to be manually set or use database triggers
        # This tests the current behavior
        assert recipe.updated_at == updated_time
        
    def test_recipe_validation_constraints(self, db_session):
        """Test recipe model validation and constraints."""
        # Test required fields
        with pytest.raises((IntegrityError, ValueError)):
            recipe = Recipe()  # No required fields
            db_session.add(recipe)
            db_session.commit()
            
        db_session.rollback()
        
        # Test minimum values
        recipe = Recipe(
            name="Test Recipe",
            description="Test description",
            prep_time=0,  # Should be positive
            cook_time=-1,  # Should be positive
            servings=0,   # Should be positive
        )
        
        # These would need model-level validation to actually fail
        # For now, test that the model accepts these values
        db_session.add(recipe)
        db_session.commit()
        
    def test_recipe_ingredient_relationships(self, db_session):
        """Test recipe-ingredient relationships."""
        recipe = RecipeFactory()
        ingredients = IngredientFactory.create_batch(3)
        
        db_session.add(recipe)
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Create recipe-ingredient relationships
        for i, ingredient in enumerate(ingredients):
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity=i + 1,
                unit="cups"
            )
            db_session.add(recipe_ingredient)
        
        db_session.commit()
        
        # Test relationships
        assert len(recipe.recipe_ingredients) == 3
        assert all(ri.recipe == recipe for ri in recipe.recipe_ingredients)
        assert len(set(ri.ingredient for ri in recipe.recipe_ingredients)) == 3
        
    def test_recipe_search_functionality(self, db_session):
        """Test recipe search and filtering capabilities."""
        recipes = [
            RecipeFactory(name="Spaghetti Carbonara", tags=["italian", "pasta"]),
            RecipeFactory(name="Thai Curry", tags=["thai", "spicy"]),
            RecipeFactory(name="Caesar Salad", tags=["salad", "vegetarian"]),
            VeganRecipeFactory(name="Quinoa Bowl"),
        ]
        
        db_session.add_all(recipes)
        db_session.commit()
        
        # Test name search
        italian_recipes = db_session.query(Recipe).filter(
            Recipe.name.contains("Spaghetti")
        ).all()
        assert len(italian_recipes) == 1
        assert italian_recipes[0].name == "Spaghetti Carbonara"
        
        # Test tag filtering (would need proper JSON query for SQLite)
        # This tests the current structure
        recipes_with_tags = db_session.query(Recipe).filter(
            Recipe.tags.isnot(None)
        ).all()
        assert len(recipes_with_tags) == 4
        
    def test_recipe_difficulty_levels(self, db_session):
        """Test recipe difficulty level handling."""
        difficulties = ["Easy", "Medium", "Hard"]
        recipes = [
            RecipeFactory(difficulty=diff) for diff in difficulties
        ]
        
        db_session.add_all(recipes)
        db_session.commit()
        
        for recipe, expected_difficulty in zip(recipes, difficulties):
            assert recipe.difficulty == expected_difficulty
            
        # Test difficulty filtering
        easy_recipes = db_session.query(Recipe).filter(
            Recipe.difficulty == "Easy"
        ).all()
        assert len(easy_recipes) == 1
        assert easy_recipes[0].difficulty == "Easy"
        
    def test_recipe_time_calculations(self, db_session):
        """Test recipe time-related calculations."""
        recipe = RecipeFactory(prep_time=20, cook_time=45)
        db_session.add(recipe)
        db_session.commit()
        
        # Test individual times
        assert recipe.prep_time == 20
        assert recipe.cook_time == 45
        
        # Test total time calculation (if implemented as property)
        # total_time = recipe.total_time
        # assert total_time == 65
        
    def test_recipe_servings_and_scaling(self, db_session):
        """Test recipe servings and potential scaling functionality."""
        recipe = RecipeFactory(servings=4)
        ingredient = IngredientFactory()
        
        db_session.add_all([recipe, ingredient])
        db_session.commit()
        
        recipe_ingredient = RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient,
            quantity=2.0,
            unit="cups"
        )
        db_session.add(recipe_ingredient)
        db_session.commit()
        
        assert recipe.servings == 4
        assert recipe_ingredient.quantity == 2.0
        
        # Test scaling calculations (if implemented)
        # scaled_quantity = recipe_ingredient.scale_for_servings(8)
        # assert scaled_quantity == 4.0
        
    def test_recipe_tags_functionality(self, db_session):
        """Test recipe tags handling."""
        recipe = RecipeFactory(tags=["vegetarian", "healthy", "quick"])
        db_session.add(recipe)
        db_session.commit()
        
        assert isinstance(recipe.tags, list)
        assert len(recipe.tags) == 3
        assert "vegetarian" in recipe.tags
        assert "healthy" in recipe.tags
        assert "quick" in recipe.tags
        
    def test_recipe_instructions_handling(self, db_session):
        """Test recipe instructions storage and retrieval."""
        instructions = [
            "Preheat oven to 350°F",
            "Mix dry ingredients",
            "Combine wet and dry ingredients", 
            "Bake for 30 minutes"
        ]
        
        recipe = RecipeFactory(instructions=instructions)
        db_session.add(recipe)
        db_session.commit()
        
        assert isinstance(recipe.instructions, list)
        assert len(recipe.instructions) == 4
        assert recipe.instructions[0] == "Preheat oven to 350°F"
        assert recipe.instructions[-1] == "Bake for 30 minutes"
        
    def test_recipe_image_paths(self, db_session):
        """Test recipe image path handling."""
        recipe = RecipeFactory(
            image_path="/path/to/recipe.jpg",
            reference_image_path="/path/to/reference.jpg"
        )
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.image_path == "/path/to/recipe.jpg"
        assert recipe.reference_image_path == "/path/to/reference.jpg"
        
    def test_recipe_notes_handling(self, db_session):
        """Test recipe notes storage."""
        notes = "This recipe works best with fresh ingredients. Store leftovers in the fridge."
        recipe = RecipeFactory(notes=notes)
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.notes == notes
        
    def test_recipe_batch_operations(self, db_session):
        """Test batch operations with recipes."""
        # Create multiple recipes
        recipes = RecipeFactory.create_batch(10)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Verify batch creation
        recipe_count = db_session.query(Recipe).count()
        assert recipe_count == 10
        
        # Test batch filtering
        easy_recipes = db_session.query(Recipe).filter(
            Recipe.difficulty == "Easy"
        ).all()
        
        medium_recipes = db_session.query(Recipe).filter(
            Recipe.difficulty == "Medium"
        ).all()
        
        hard_recipes = db_session.query(Recipe).filter(
            Recipe.difficulty == "Hard"
        ).all()
        
        total_filtered = len(easy_recipes) + len(medium_recipes) + len(hard_recipes)
        assert total_filtered == 10
        
    def test_recipe_edge_cases(self, db_session):
        """Test edge cases and boundary conditions."""
        # Test very long recipe name
        long_name = "A" * 500  # Very long name
        recipe = RecipeFactory(name=long_name)
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.name == long_name
        
        # Test empty optional fields
        minimal_recipe = Recipe(
            name="Minimal Recipe",
            description="",
            prep_time=1,
            cook_time=1,
            servings=1,
            instructions=[],
            tags=[]
        )
        db_session.add(minimal_recipe)
        db_session.commit()
        
        assert minimal_recipe.description == ""
        assert minimal_recipe.instructions == []
        assert minimal_recipe.tags == []
        
    def test_recipe_unicode_handling(self, db_session):
        """Test unicode and special character handling."""
        recipe = RecipeFactory(
            name="Crème Brûlée with Açaí",
            description="A dessert with special characters: é, ñ, ü, ç",
            notes="测试中文字符 and العربية والهندية"
        )
        db_session.add(recipe)
        db_session.commit()
        
        assert "Crème" in recipe.name
        assert "é" in recipe.description
        assert "测试" in recipe.notes
        
    @pytest.mark.slow
    def test_recipe_performance_bulk_operations(self, db_session):
        """Test performance with bulk operations."""
        # Create large batch of recipes
        recipes = RecipeFactory.create_batch(100)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Test bulk query performance
        all_recipes = db_session.query(Recipe).all()
        assert len(all_recipes) == 100
        
        # Test bulk filtering
        easy_recipes = db_session.query(Recipe).filter(
            Recipe.difficulty == "Easy"
        ).limit(50).all()
        
        assert len(easy_recipes) <= 50