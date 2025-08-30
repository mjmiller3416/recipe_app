# tests/core/services/test_ingredient_service.py

import pytest

from app.core.dtos.ingredient_dtos import (IngredientCreateDTO,
                                           IngredientUpdateDTO)
from app.core.models.ingredient import Ingredient
from app.core.services.ingredient_service import IngredientService


def test_get_all_ingredients_empty(session):
    """Test getting all ingredients when none exist."""
    service = IngredientService(session)

    ingredients = service.get_all_ingredients()

    assert ingredients == []


def test_get_all_ingredients(session):
    """Test getting all ingredients."""
    # Create test ingredients
    ingredient1 = Ingredient(ingredient_name="Ingredient 1", ingredient_category="Category 1")
    ingredient2 = Ingredient(ingredient_name="Ingredient 2", ingredient_category="Category 2")
    session.add_all([ingredient1, ingredient2])
    session.commit()

    service = IngredientService(session)

    ingredients = service.get_all_ingredients()

    assert len(ingredients) == 2
    names = {ing.ingredient_name for ing in ingredients}
    assert names == {"Ingredient 1", "Ingredient 2"}


def test_get_ingredient_by_id_success(session):
    """Test getting an ingredient by ID."""
    ingredient = Ingredient(ingredient_name="Test Ingredient", ingredient_category="Test")
    session.add(ingredient)
    session.commit()

    service = IngredientService(session)

    result = service.get_ingredient_by_id(ingredient.id)

    assert result is not None
    assert result.ingredient_name == "Test Ingredient"
    assert result.ingredient_category == "Test"


def test_get_ingredient_by_id_not_found(session):
    """Test getting a non-existent ingredient."""
    service = IngredientService(session)

    result = service.get_ingredient_by_id(999)

    assert result is None


def test_create_ingredient_new(session):
    """Test creating a new ingredient."""
    service = IngredientService(session)

    create_dto = IngredientCreateDTO(
        ingredient_name="New Ingredient",
        ingredient_category="New Category"
    )

    result = service.create_ingredient(create_dto)

    assert result is not None
    assert result.ingredient_name == "New Ingredient"
    assert result.ingredient_category == "New Category"
    assert result.id is not None


def test_create_ingredient_duplicate(session):
    """Test creating a duplicate ingredient returns existing one."""
    # Create existing ingredient
    existing = Ingredient(ingredient_name="Existing Ingredient", ingredient_category="Test")
    session.add(existing)
    session.commit()

    service = IngredientService(session)

    create_dto = IngredientCreateDTO(
        ingredient_name="Existing Ingredient",
        ingredient_category="Test"
    )

    result = service.create_ingredient(create_dto)

    assert result is not None
    assert result.id == existing.id  # Should return existing ingredient


def test_update_ingredient_success(session):
    """Test updating an existing ingredient."""
    ingredient = Ingredient(ingredient_name="Original Name", ingredient_category="Original Category")
    session.add(ingredient)
    session.commit()

    service = IngredientService(session)

    update_dto = IngredientUpdateDTO(
        ingredient_name="Updated Name",
        ingredient_category="Updated Category"
    )

    result = service.update_ingredient(ingredient.id, update_dto)

    assert result is not None
    assert result.ingredient_name == "Updated Name"
    assert result.ingredient_category == "Updated Category"


def test_update_ingredient_not_found(session):
    """Test updating a non-existent ingredient."""
    service = IngredientService(session)

    update_dto = IngredientUpdateDTO(ingredient_name="Updated Name")

    result = service.update_ingredient(999, update_dto)

    assert result is None


def test_delete_ingredient_success(session):
    """Test deleting an existing ingredient."""
    ingredient = Ingredient(ingredient_name="Test Ingredient", ingredient_category="Test")
    session.add(ingredient)
    session.commit()
    ingredient_id = ingredient.id

    service = IngredientService(session)

    result = service.delete_ingredient(ingredient_id)

    assert result is True

    # Verify deletion
    deleted_ingredient = service.get_ingredient_by_id(ingredient_id)
    assert deleted_ingredient is None


def test_delete_ingredient_not_found(session):
    """Test deleting a non-existent ingredient."""
    service = IngredientService(session)

    result = service.delete_ingredient(999)

    assert result is False


def test_search_ingredients_by_name(session):
    """Test searching ingredients by name."""
    # Create test ingredients
    ingredient1 = Ingredient(ingredient_name="Apple Juice", ingredient_category="Beverages")
    ingredient2 = Ingredient(ingredient_name="Apple Pie", ingredient_category="Desserts")
    ingredient3 = Ingredient(ingredient_name="Orange Juice", ingredient_category="Beverages")
    session.add_all([ingredient1, ingredient2, ingredient3])
    session.commit()

    service = IngredientService(session)

    # Search for "apple"
    results = service.search_ingredients("apple")

    assert len(results) == 2
    names = {ing.ingredient_name for ing in results}
    assert names == {"Apple Juice", "Apple Pie"}


def test_search_ingredients_by_category(session):
    """Test searching ingredients by category."""
    # Create test ingredients
    ingredient1 = Ingredient(ingredient_name="Apple Juice", ingredient_category="Beverages")
    ingredient2 = Ingredient(ingredient_name="Orange Juice", ingredient_category="Beverages")
    ingredient3 = Ingredient(ingredient_name="Apple Pie", ingredient_category="Desserts")
    session.add_all([ingredient1, ingredient2, ingredient3])
    session.commit()

    service = IngredientService(session)

    # Search in beverages category
    results = service.search_ingredients("juice", "Beverages")

    assert len(results) == 2
    names = {ing.ingredient_name for ing in results}
    assert names == {"Apple Juice", "Orange Juice"}


def test_get_or_create_ingredient_existing(session):
    """Test get_or_create with existing ingredient."""
    existing = Ingredient(ingredient_name="Existing Ingredient", ingredient_category="Test")
    session.add(existing)
    session.commit()

    service = IngredientService(session)

    result = service.get_or_create_ingredient("Existing Ingredient", "Test")

    assert result.id == existing.id
    assert result.ingredient_name == "Existing Ingredient"


def test_get_or_create_ingredient_new(session):
    """Test get_or_create with new ingredient."""
    service = IngredientService(session)

    result = service.get_or_create_ingredient("New Ingredient", "New Category")

    assert result is not None
    assert result.ingredient_name == "New Ingredient"
    assert result.ingredient_category == "New Category"
    assert result.id is not None


def test_get_ingredients_by_category(session):
    """Test getting ingredients filtered by category."""
    # Create test ingredients
    ingredient1 = Ingredient(ingredient_name="Apple Juice", ingredient_category="Beverages")
    ingredient2 = Ingredient(ingredient_name="Orange Juice", ingredient_category="Beverages")
    ingredient3 = Ingredient(ingredient_name="Apple Pie", ingredient_category="Desserts")
    session.add_all([ingredient1, ingredient2, ingredient3])
    session.commit()

    service = IngredientService(session)

    beverages = service.get_ingredients_by_category("Beverages")

    assert len(beverages) == 2
    names = {ing.ingredient_name for ing in beverages}
    assert names == {"Apple Juice", "Orange Juice"}


def test_get_ingredient_categories(session):
    """Test getting all unique ingredient categories."""
    # Create test ingredients
    ingredient1 = Ingredient(ingredient_name="Apple Juice", ingredient_category="Beverages")
    ingredient2 = Ingredient(ingredient_name="Orange Juice", ingredient_category="Beverages")
    ingredient3 = Ingredient(ingredient_name="Apple Pie", ingredient_category="Desserts")
    ingredient4 = Ingredient(ingredient_name="Bread", ingredient_category="Bakery")
    session.add_all([ingredient1, ingredient2, ingredient3, ingredient4])
    session.commit()

    service = IngredientService(session)

    categories = service.get_ingredient_categories()

    assert set(categories) == {"Beverages", "Desserts", "Bakery"}


def test_bulk_create_ingredients(session):
    """Test creating multiple ingredients at once."""
    service = IngredientService(session)

    create_dtos = [
        IngredientCreateDTO(ingredient_name="Ingredient 1", ingredient_category="Category 1"),
        IngredientCreateDTO(ingredient_name="Ingredient 2", ingredient_category="Category 2"),
        IngredientCreateDTO(ingredient_name="Ingredient 3", ingredient_category="Category 1"),
    ]

    results = service.bulk_create_ingredients(create_dtos)

    assert len(results) == 3
    names = {ing.ingredient_name for ing in results}
    assert names == {"Ingredient 1", "Ingredient 2", "Ingredient 3"}

    # Verify all have IDs (were actually created)
    assert all(ing.id is not None for ing in results)
