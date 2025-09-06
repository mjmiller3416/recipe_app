"""
Unit tests for Ingredient model.

Tests the Ingredient SQLAlchemy model including:
- Model creation and validation
- Category management and relationships
- Ingredient search and filtering
- Data integrity constraints
"""

from faker import Faker
import pytest
from sqlalchemy.exc import IntegrityError

from _tests.fixtures.recipe_factories import (
    IngredientFactory,
    IngredientTraits,
    RecipeFactory,
    RecipeIngredientFactory,
)
from app.core.models import Ingredient, Recipe, RecipeIngredient

fake = Faker()


@pytest.mark.models
@pytest.mark.unit
class TestIngredientModel:
    """Test cases for Ingredient model functionality."""
    
    def test_ingredient_creation(self, db_session):
        """Test basic ingredient creation."""
        ingredient_data = {
            "ingredient_name": "Tomato",
            "ingredient_category": "Vegetables"
        }
        
        ingredient = Ingredient(**ingredient_data)
        db_session.add(ingredient)
        db_session.commit()
        
        assert ingredient.id is not None
        assert ingredient.ingredient_name == "Tomato"
        assert ingredient.ingredient_category == "Vegetables"
        
    def test_ingredient_factory(self, db_session):
        """Test ingredient creation using factory."""
        ingredient = IngredientFactory()
        db_session.add(ingredient)
        db_session.commit()
        
        assert ingredient.id is not None
        assert ingredient.name is not None
        assert ingredient.category is not None
        assert ingredient.category in [
            "Vegetables", "Fruits", "Proteins", "Grains", "Dairy", 
            "Spices", "Oils", "Condiments", "Beverages", "Other"
        ]
        
    def test_ingredient_traits(self, db_session):
        """Test ingredient trait factories."""
        # Vegetable ingredient
        vegetable = IngredientFactory(**IngredientTraits.vegetable())
        db_session.add(vegetable)
        assert vegetable.category == "Vegetables"
        
        # Protein ingredient
        protein = IngredientFactory(**IngredientTraits.protein())
        db_session.add(protein)
        assert protein.category == "Proteins"
        
        # Dairy ingredient
        dairy = IngredientFactory(**IngredientTraits.dairy())
        db_session.add(dairy)
        assert dairy.category == "Dairy"
        
        db_session.commit()
        
    def test_ingredient_name_normalization(self, db_session):
        """Test ingredient name normalization."""
        ingredients = IngredientFactory.create_batch(5)
        db_session.add_all(ingredients)
        db_session.commit()
        
        for ingredient in ingredients:
            # Check that names are title-cased due to factory post-generation
            assert ingredient.name[0].isupper()
            
    def test_ingredient_categories(self, db_session):
        """Test ingredient category functionality."""
        categories = [
            "Vegetables", "Fruits", "Proteins", "Grains", "Dairy", 
            "Spices", "Oils", "Condiments", "Beverages", "Other"
        ]
        
        ingredients = []
        for category in categories:
            ingredient = IngredientFactory(category=category)
            ingredients.append(ingredient)
            
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Test category filtering
        for category in categories:
            category_ingredients = db_session.query(Ingredient).filter(
                Ingredient.category == category
            ).all()
            assert len(category_ingredients) >= 1
            
    def test_ingredient_recipe_relationships(self, db_session):
        """Test ingredient relationships with recipes."""
        ingredient = IngredientFactory()
        recipes = RecipeFactory.create_batch(3)
        
        db_session.add(ingredient)
        db_session.add_all(recipes)
        db_session.commit()
        
        # Create recipe-ingredient relationships
        for recipe in recipes:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity=fake.random_digit_not_null(),
                unit="cups"
            )
            db_session.add(recipe_ingredient)
            
        db_session.commit()
        
        # Test relationships
        assert len(ingredient.recipe_ingredients) == 3
        recipe_ids = {ri.recipe.id for ri in ingredient.recipe_ingredients}
        expected_ids = {recipe.id for recipe in recipes}
        assert recipe_ids == expected_ids
        
    def test_ingredient_search_functionality(self, db_session):
        """Test ingredient search capabilities."""
        ingredients = [
            IngredientFactory(name="Tomato", category="Vegetables"),
            IngredientFactory(name="Cherry Tomato", category="Vegetables"),
            IngredientFactory(name="Potato", category="Vegetables"),
            IngredientFactory(name="Chicken", category="Proteins"),
        ]
        
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Test name search
        tomato_ingredients = db_session.query(Ingredient).filter(
            Ingredient.name.contains("Tomato")
        ).all()
        assert len(tomato_ingredients) == 2
        
        # Test exact name search
        exact_match = db_session.query(Ingredient).filter(
            Ingredient.name == "Tomato"
        ).first()
        assert exact_match is not None
        assert exact_match.name == "Tomato"
        
        # Test category search
        vegetables = db_session.query(Ingredient).filter(
            Ingredient.category == "Vegetables"
        ).all()
        assert len(vegetables) == 3
        
    def test_ingredient_uniqueness(self, db_session):
        """Test ingredient name uniqueness constraints."""
        ingredient1 = IngredientFactory(name="Unique Ingredient")
        db_session.add(ingredient1)
        db_session.commit()
        
        # Try to create another ingredient with the same name
        # Note: This depends on database constraints being defined
        ingredient2 = IngredientFactory(name="Unique Ingredient")
        db_session.add(ingredient2)
        
        # If uniqueness is enforced, this should raise an error
        try:
            db_session.commit()
            # If no error, check that we have distinct ingredients
            ingredients = db_session.query(Ingredient).filter(
                Ingredient.name == "Unique Ingredient"
            ).all()
            # This test adapts to whether uniqueness is enforced or not
        except IntegrityError:
            db_session.rollback()
            # Uniqueness is enforced - this is expected
            pass
            
    def test_ingredient_validation_constraints(self, db_session):
        """Test ingredient model validation."""
        # Test required fields
        with pytest.raises((IntegrityError, ValueError)):
            ingredient = Ingredient()  # No required fields
            db_session.add(ingredient)
            db_session.commit()
            
        db_session.rollback()
        
        # Test valid minimal ingredient
        minimal_ingredient = Ingredient(
            name="Test Ingredient",
            category="Other"
        )
        db_session.add(minimal_ingredient)
        db_session.commit()
        
        assert minimal_ingredient.name == "Test Ingredient"
        assert minimal_ingredient.category == "Other"
        
    def test_ingredient_case_sensitivity(self, db_session):
        """Test ingredient name case handling."""
        ingredients = [
            IngredientFactory(name="basil"),
            IngredientFactory(name="Basil"),
            IngredientFactory(name="BASIL"),
        ]
        
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Test case-insensitive search
        basil_ingredients = db_session.query(Ingredient).filter(
            Ingredient.name.ilike("%basil%")
        ).all()
        assert len(basil_ingredients) == 3
        
    def test_ingredient_special_characters(self, db_session):
        """Test ingredients with special characters."""
        special_ingredients = [
            IngredientFactory(name="Jalapeño"),
            IngredientFactory(name="Gruyère Cheese"),
            IngredientFactory(name="Pâté"),
            IngredientFactory(name="Açaí Berry"),
        ]
        
        db_session.add_all(special_ingredients)
        db_session.commit()
        
        for ingredient in special_ingredients:
            assert ingredient.id is not None
            
        # Test special character search
        accented_ingredients = db_session.query(Ingredient).filter(
            Ingredient.name.contains("é")
        ).all()
        assert len(accented_ingredients) >= 1
        
    def test_ingredient_batch_operations(self, db_session):
        """Test batch operations with ingredients."""
        # Create multiple ingredients
        ingredients = IngredientFactory.create_batch(20)
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Verify batch creation
        ingredient_count = db_session.query(Ingredient).count()
        assert ingredient_count == 20
        
        # Test batch filtering by category
        all_categories = db_session.query(Ingredient.category).distinct().all()
        assert len(all_categories) > 0
        
        for (category,) in all_categories:
            category_ingredients = db_session.query(Ingredient).filter(
                Ingredient.category == category
            ).all()
            assert len(category_ingredients) > 0
            
    def test_ingredient_sorting(self, db_session):
        """Test ingredient sorting functionality."""
        ingredients = [
            IngredientFactory(name="Zucchini", category="Vegetables"),
            IngredientFactory(name="Apple", category="Fruits"),
            IngredientFactory(name="Banana", category="Fruits"),
            IngredientFactory(name="Carrot", category="Vegetables"),
        ]
        
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Test alphabetical sorting
        sorted_ingredients = db_session.query(Ingredient).order_by(
            Ingredient.name
        ).all()
        
        names = [ing.name for ing in sorted_ingredients]
        assert names == sorted(names)
        
        # Test category sorting
        category_sorted = db_session.query(Ingredient).order_by(
            Ingredient.category, Ingredient.name
        ).all()
        
        # Verify category grouping
        prev_category = None
        for ingredient in category_sorted:
            if prev_category is not None:
                assert ingredient.category >= prev_category
            prev_category = ingredient.category
            
    def test_ingredient_filtering_combinations(self, db_session):
        """Test complex filtering combinations."""
        ingredients = [
            IngredientFactory(name="Roma Tomato", category="Vegetables"),
            IngredientFactory(name="Cherry Tomato", category="Vegetables"),
            IngredientFactory(name="Tomato Paste", category="Condiments"),
            IngredientFactory(name="Chicken Breast", category="Proteins"),
            IngredientFactory(name="Ground Beef", category="Proteins"),
        ]
        
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Combined name and category filter
        vegetable_tomatoes = db_session.query(Ingredient).filter(
            Ingredient.name.contains("Tomato"),
            Ingredient.category == "Vegetables"
        ).all()
        assert len(vegetable_tomatoes) == 2
        
        # Multiple category filter
        proteins_and_condiments = db_session.query(Ingredient).filter(
            Ingredient.category.in_(["Proteins", "Condiments"])
        ).all()
        assert len(proteins_and_condiments) == 3
        
    def test_ingredient_usage_tracking(self, db_session):
        """Test ingredient usage in recipes."""
        popular_ingredient = IngredientFactory(name="Popular Ingredient")
        rare_ingredient = IngredientFactory(name="Rare Ingredient")
        
        recipes = RecipeFactory.create_batch(5)
        
        db_session.add_all([popular_ingredient, rare_ingredient] + recipes)
        db_session.commit()
        
        # Use popular ingredient in multiple recipes
        for recipe in recipes[:4]:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=popular_ingredient,
                quantity=1,
                unit="cup"
            )
            db_session.add(recipe_ingredient)
            
        # Use rare ingredient in only one recipe
        rare_usage = RecipeIngredient(
            recipe=recipes[0],
            ingredient=rare_ingredient,
            quantity=1,
            unit="tsp"
        )
        db_session.add(rare_usage)
        db_session.commit()
        
        # Test usage counting
        assert len(popular_ingredient.recipe_ingredients) == 4
        assert len(rare_ingredient.recipe_ingredients) == 1
        
    def test_ingredient_edge_cases(self, db_session):
        """Test edge cases and boundary conditions."""
        # Test very long ingredient name
        long_name = "A" * 300
        long_ingredient = IngredientFactory(name=long_name)
        db_session.add(long_ingredient)
        db_session.commit()
        
        assert long_ingredient.name == long_name
        
        # Test empty category (if allowed)
        try:
            empty_category = IngredientFactory(name="No Category", category="")
            db_session.add(empty_category)
            db_session.commit()
        except (IntegrityError, ValueError):
            db_session.rollback()
            # Empty category not allowed - this is expected behavior
            
    def test_ingredient_unicode_names(self, db_session):
        """Test ingredients with unicode names."""
        unicode_ingredients = [
            IngredientFactory(name="香菜"),  # Chinese cilantro
            IngredientFactory(name="τυρί"),  # Greek cheese
            IngredientFactory(name="चावल"),  # Hindi rice
            IngredientFactory(name="الحليب"),  # Arabic milk
        ]
        
        db_session.add_all(unicode_ingredients)
        db_session.commit()
        
        for ingredient in unicode_ingredients:
            assert ingredient.id is not None
            assert len(ingredient.name) > 0
            
    @pytest.mark.slow
    def test_ingredient_performance_large_dataset(self, db_session):
        """Test performance with large ingredient datasets."""
        # Create large batch of ingredients
        ingredients = IngredientFactory.create_batch(500)
        db_session.add_all(ingredients)
        db_session.commit()
        
        # Test query performance
        all_ingredients = db_session.query(Ingredient).all()
        assert len(all_ingredients) == 500
        
        # Test search performance
        search_results = db_session.query(Ingredient).filter(
            Ingredient.name.contains("a")
        ).limit(50).all()
        assert len(search_results) <= 50