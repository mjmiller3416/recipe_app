"""
Factory-boy factories for creating test data models.

Provides factories for all MealGenie models using factory-boy and faker
to generate realistic test data with proper relationships and constraints.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import factory
import factory.fuzzy
from faker import Faker

from app.core.database.base import Base
from app.core.models import (
    Ingredient,
    MealSelection,
    Recipe,
    RecipeHistory,
    RecipeIngredient,
    SavedMealState,
    ShoppingItem,
    ShoppingState,
)

fake = Faker()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory with common configuration."""
    
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


class IngredientFactory(BaseFactory):
    """Factory for creating Ingredient instances."""
    
    class Meta:
        model = Ingredient
    
    name = factory.Faker("word")
    category = factory.fuzzy.FuzzyChoice([
        "Vegetables", "Fruits", "Proteins", "Grains", "Dairy", 
        "Spices", "Oils", "Condiments", "Beverages", "Other"
    ])
    
    @factory.post_generation
    def normalize_name(obj, create, extracted, **kwargs):
        """Normalize ingredient name to title case."""
        if obj.name:
            obj.name = obj.name.title()


class RecipeFactory(BaseFactory):
    """Factory for creating Recipe instances."""
    
    class Meta:
        model = Recipe
    
    name = factory.Faker("sentence", nb_words=3, variable_nb_words=True)
    description = factory.Faker("paragraph", nb_sentences=2)
    prep_time = factory.fuzzy.FuzzyInteger(5, 60)
    cook_time = factory.fuzzy.FuzzyInteger(10, 180)
    servings = factory.fuzzy.FuzzyInteger(1, 8)
    difficulty = factory.fuzzy.FuzzyChoice(["Easy", "Medium", "Hard"])
    tags = factory.Faker("words", nb=3)
    notes = factory.Faker("paragraph", nb_sentences=1)
    created_at = factory.Faker("date_time_between", start_date="-1y", end_date="now")
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    
    # Image paths
    image_path = factory.Faker("file_path", depth=2, extension="jpg")
    reference_image_path = factory.Faker("file_path", depth=2, extension="jpg")
    
    @factory.post_generation
    def clean_name(obj, create, extracted, **kwargs):
        """Clean up recipe name."""
        if obj.name and obj.name.endswith('.'):
            obj.name = obj.name[:-1]
    
    @factory.post_generation
    def instructions(obj, create, extracted, **kwargs):
        """Generate instructions list."""
        if extracted:
            obj.instructions = extracted
        else:
            num_steps = fake.random_int(min=3, max=8)
            obj.instructions = [
                f"Step {i+1}: {fake.sentence()}" 
                for i in range(num_steps)
            ]


class RecipeIngredientFactory(BaseFactory):
    """Factory for creating RecipeIngredient instances."""
    
    class Meta:
        model = RecipeIngredient
    
    recipe = factory.SubFactory(RecipeFactory)
    ingredient = factory.SubFactory(IngredientFactory)
    quantity = factory.fuzzy.FuzzyFloat(0.25, 5.0, precision=2)
    unit = factory.fuzzy.FuzzyChoice([
        "cups", "tablespoons", "teaspoons", "pounds", "ounces",
        "grams", "kilograms", "milliliters", "liters", "pieces"
    ])
    notes = factory.Maybe(
        "has_notes",
        yes_declaration=factory.Faker("sentence"),
        no_declaration=""
    )
    
    has_notes = factory.Faker("boolean", chance_of_getting_true=30)


class MealSelectionFactory(BaseFactory):
    """Factory for creating MealSelection instances."""
    
    class Meta:
        model = MealSelection
    
    recipe = factory.SubFactory(RecipeFactory)
    date = factory.Faker("date_between", start_date="-30d", end_date="+30d")
    meal_type = factory.fuzzy.FuzzyChoice(["breakfast", "lunch", "dinner", "snack"])
    servings = factory.fuzzy.FuzzyInteger(1, 6)
    notes = factory.Maybe(
        "has_notes",
        yes_declaration=factory.Faker("sentence"),
        no_declaration=""
    )
    
    has_notes = factory.Faker("boolean", chance_of_getting_true=20)


class ShoppingItemFactory(BaseFactory):
    """Factory for creating ShoppingItem instances."""
    
    class Meta:
        model = ShoppingItem
    
    ingredient = factory.SubFactory(IngredientFactory)
    quantity = factory.fuzzy.FuzzyFloat(0.5, 10.0, precision=2)
    unit = factory.fuzzy.FuzzyChoice([
        "cups", "tablespoons", "teaspoons", "pounds", "ounces",
        "grams", "kilograms", "milliliters", "liters", "pieces"
    ])
    is_purchased = factory.Faker("boolean", chance_of_getting_true=25)
    category = factory.LazyAttribute(lambda obj: obj.ingredient.category if obj.ingredient else "Other")
    notes = factory.Maybe(
        "has_notes",
        yes_declaration=factory.Faker("sentence"),
        no_declaration=""
    )
    
    has_notes = factory.Faker("boolean", chance_of_getting_true=15)


class SavedMealStateFactory(BaseFactory):
    """Factory for creating SavedMealState instances."""
    
    class Meta:
        model = SavedMealState
    
    name = factory.Faker("sentence", nb_words=2, variable_nb_words=False)
    description = factory.Faker("paragraph", nb_sentences=1)
    created_at = factory.Faker("date_time_between", start_date="-6m", end_date="now")
    
    @factory.post_generation
    def meal_data(obj, create, extracted, **kwargs):
        """Generate meal plan data structure."""
        if extracted:
            obj.meal_data = extracted
        else:
            # Generate sample meal plan data
            meal_data = {}
            for day_offset in range(7):
                date_key = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                meal_data[date_key] = {
                    "breakfast": {"recipe_id": fake.random_int(1, 100), "servings": 2} if fake.boolean(chance_of_getting_true=70) else None,
                    "lunch": {"recipe_id": fake.random_int(1, 100), "servings": 2} if fake.boolean(chance_of_getting_true=80) else None,
                    "dinner": {"recipe_id": fake.random_int(1, 100), "servings": 4} if fake.boolean(chance_of_getting_true=90) else None,
                    "snack": {"recipe_id": fake.random_int(1, 100), "servings": 1} if fake.boolean(chance_of_getting_true=30) else None,
                }
            obj.meal_data = meal_data


class ShoppingStateFactory(BaseFactory):
    """Factory for creating ShoppingState instances."""
    
    class Meta:
        model = ShoppingState
    
    name = factory.Faker("sentence", nb_words=2, variable_nb_words=False)
    description = factory.Faker("paragraph", nb_sentences=1)
    created_at = factory.Faker("date_time_between", start_date="-3m", end_date="now")
    
    @factory.post_generation
    def shopping_data(obj, create, extracted, **kwargs):
        """Generate shopping list data structure."""
        if extracted:
            obj.shopping_data = extracted
        else:
            # Generate sample shopping list data
            categories = ["Vegetables", "Fruits", "Proteins", "Grains", "Dairy"]
            shopping_data = {}
            
            for category in categories:
                if fake.boolean(chance_of_getting_true=80):
                    shopping_data[category] = []
                    num_items = fake.random_int(1, 5)
                    for _ in range(num_items):
                        shopping_data[category].append({
                            "ingredient_id": fake.random_int(1, 50),
                            "quantity": fake.random_digit_not_null(),
                            "unit": fake.random_element(["cups", "lbs", "oz"]),
                            "is_purchased": fake.boolean(chance_of_getting_true=30)
                        })
            
            obj.shopping_data = shopping_data


class RecipeHistoryFactory(BaseFactory):
    """Factory for creating RecipeHistory instances."""
    
    class Meta:
        model = RecipeHistory
    
    recipe = factory.SubFactory(RecipeFactory)
    action = factory.fuzzy.FuzzyChoice(["created", "updated", "deleted", "viewed"])
    timestamp = factory.Faker("date_time_between", start_date="-1y", end_date="now")
    details = factory.Maybe(
        "has_details",
        yes_declaration=factory.LazyFunction(lambda: {
            "changes": fake.words(nb=3),
            "user_agent": fake.user_agent(),
            "version": fake.numerify("#.#.#")
        }),
        no_declaration=None
    )
    
    has_details = factory.Faker("boolean", chance_of_getting_true=40)


# Specialized factories for specific test scenarios

class QuickRecipeFactory(RecipeFactory):
    """Factory for quick/easy recipes."""
    
    prep_time = factory.fuzzy.FuzzyInteger(5, 15)
    cook_time = factory.fuzzy.FuzzyInteger(5, 30)
    difficulty = "Easy"
    

class ComplexRecipeFactory(RecipeFactory):
    """Factory for complex recipes."""
    
    prep_time = factory.fuzzy.FuzzyInteger(30, 120)
    cook_time = factory.fuzzy.FuzzyInteger(60, 300)
    difficulty = "Hard"
    servings = factory.fuzzy.FuzzyInteger(6, 12)


class VeganRecipeFactory(RecipeFactory):
    """Factory for vegan recipes."""
    
    tags = factory.LazyFunction(lambda: ["vegan", "plant-based", "healthy"])
    

class RecipeWithIngredientsFactory(RecipeFactory):
    """Factory that creates a recipe with associated ingredients."""
    
    @factory.post_generation
    def ingredients(obj, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            # Use provided ingredients
            for ingredient_data in extracted:
                RecipeIngredientFactory(recipe=obj, **ingredient_data)
        else:
            # Create random ingredients
            num_ingredients = fake.random_int(3, 8)
            for _ in range(num_ingredients):
                RecipeIngredientFactory(recipe=obj)


class WeeklyMealPlanFactory(factory.Factory):
    """Factory for creating a complete weekly meal plan."""
    
    class Meta:
        model = dict
    
    @classmethod
    def create(cls, **kwargs):
        """Create a weekly meal plan with recipes for each day."""
        meal_plan = {}
        recipes = RecipeFactory.create_batch(10)
        
        for day_offset in range(7):
            date = datetime.now() + timedelta(days=day_offset)
            date_key = date.strftime("%Y-%m-%d")
            
            meal_plan[date_key] = {
                "breakfast": MealSelectionFactory(
                    recipe=fake.random_element(recipes[:3]),
                    date=date.date(),
                    meal_type="breakfast"
                ) if fake.boolean(chance_of_getting_true=70) else None,
                "lunch": MealSelectionFactory(
                    recipe=fake.random_element(recipes[3:6]),
                    date=date.date(),
                    meal_type="lunch"
                ) if fake.boolean(chance_of_getting_true=80) else None,
                "dinner": MealSelectionFactory(
                    recipe=fake.random_element(recipes[6:10]),
                    date=date.date(),
                    meal_type="dinner"
                ) if fake.boolean(chance_of_getting_true=90) else None,
            }
        
        return meal_plan


# Utility functions for creating test data sets

def create_sample_database(session, num_recipes=20, num_ingredients=50):
    """Create a sample database with related test data."""
    
    # Create ingredients
    ingredients = IngredientFactory.create_batch(num_ingredients)
    session.add_all(ingredients)
    session.commit()
    
    # Create recipes with ingredients
    recipes = []
    for _ in range(num_recipes):
        recipe = RecipeFactory()
        session.add(recipe)
        session.commit()
        
        # Add 3-8 ingredients to each recipe
        num_recipe_ingredients = fake.random_int(3, 8)
        recipe_ingredients = []
        used_ingredients = set()
        
        for _ in range(num_recipe_ingredients):
            ingredient = fake.random_element(ingredients)
            if ingredient.id not in used_ingredients:
                recipe_ingredient = RecipeIngredientFactory(
                    recipe=recipe,
                    ingredient=ingredient
                )
                recipe_ingredients.append(recipe_ingredient)
                used_ingredients.add(ingredient.id)
        
        session.add_all(recipe_ingredients)
        recipes.append(recipe)
    
    session.commit()
    
    # Create some meal selections
    meal_selections = []
    for _ in range(30):  # 30 meal selections
        meal_selection = MealSelectionFactory(
            recipe=fake.random_element(recipes)
        )
        meal_selections.append(meal_selection)
    
    session.add_all(meal_selections)
    
    # Create some shopping items
    shopping_items = []
    for _ in range(20):
        shopping_item = ShoppingItemFactory(
            ingredient=fake.random_element(ingredients)
        )
        shopping_items.append(shopping_item)
    
    session.add_all(shopping_items)
    session.commit()
    
    return {
        "recipes": recipes,
        "ingredients": ingredients,
        "meal_selections": meal_selections,
        "shopping_items": shopping_items
    }


# Trait-based factories for common testing scenarios

class RecipeTraits:
    """Common traits for recipe testing."""
    
    @staticmethod
    def with_image():
        return {"image_path": "/test/images/recipe.jpg"}
    
    @staticmethod
    def vegetarian():
        return {"tags": ["vegetarian", "healthy"]}
    
    @staticmethod
    def quick_meal():
        return {"prep_time": 10, "cook_time": 15, "difficulty": "Easy"}
    
    @staticmethod
    def complex_dish():
        return {"prep_time": 60, "cook_time": 120, "difficulty": "Hard"}


class IngredientTraits:
    """Common traits for ingredient testing."""
    
    @staticmethod
    def vegetable():
        return {"category": "Vegetables"}
    
    @staticmethod
    def protein():
        return {"category": "Proteins"}
    
    @staticmethod
    def dairy():
        return {"category": "Dairy"}