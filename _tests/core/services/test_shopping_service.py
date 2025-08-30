# tests/core/services/test_shopping_service.py

import pytest

from app.core.dtos.shopping_dtos import (BulkStateUpdateDTO,
                                         ManualItemCreateDTO,
                                         ShoppingItemUpdateDTO,
                                         ShoppingListGenerationDTO)
from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.models.shopping_item import ShoppingItem
from app.core.services.shopping_service import ShoppingService


def test_generate_shopping_list_empty(session):
    """Test generating shopping list with no recipes."""
    service = ShoppingService(session)

    generation_dto = ShoppingListGenerationDTO(recipe_ids=[])
    result = service.generate_shopping_list(generation_dto)

    assert result.success is True
    assert result.items_created == 0
    assert result.items == []


def test_generate_shopping_list_with_recipes(session):
    """Test generating shopping list from recipes."""
    # Create recipe, ingredient, and recipe_ingredient
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    ingredient = Ingredient(ingredient_name="Test Ingredient", ingredient_category="Test")
    session.add(ingredient)
    session.commit()

    recipe_ing = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=1.5, unit="cup")
    session.add(recipe_ing)
    session.commit()

    service = ShoppingService(session)

    generation_dto = ShoppingListGenerationDTO(
        recipe_ids=[recipe.id],
        clear_existing=True
    )
    result = service.generate_shopping_list(generation_dto)

    assert result.success is True
    assert result.items_created == 1
    assert len(result.items) == 1
    assert result.items[0].ingredient_name == "Test Ingredient"
    assert result.items[0].quantity == 1.5


def test_get_shopping_list(session):
    """Test getting the current shopping list."""
    # Create some shopping items
    item1 = ShoppingItem.create_manual("Item 1", 1.0, "piece")
    item2 = ShoppingItem.create_from_recipe("Item 2", 2.0, "cup", "Test")
    session.add_all([item1, item2])
    session.commit()

    service = ShoppingService(session)

    shopping_list = service.get_shopping_list()

    assert len(shopping_list.items) == 2
    item_names = {item.ingredient_name for item in shopping_list.items}
    assert item_names == {"Item 1", "Item 2"}


def test_add_manual_item(session):
    """Test adding a manual shopping item."""
    service = ShoppingService(session)

    create_dto = ManualItemCreateDTO(
        ingredient_name="Manual Item",
        quantity=3.0,
        unit="lb"
    )

    result = service.add_manual_item(create_dto)

    assert result is not None
    assert result.ingredient_name == "Manual Item"
    assert result.quantity == 3.0
    assert result.unit == "lb"
    assert result.source == "manual"


def test_update_item(session):
    """Test updating a shopping item."""
    # Create an item
    item = ShoppingItem.create_manual("Test Item", 1.0, "piece")
    session.add(item)
    session.commit()

    service = ShoppingService(session)

    update_dto = ShoppingItemUpdateDTO(
        ingredient_name="Updated Item",
        quantity=2.0,
        unit="kg"
    )

    result = service.update_item(item.id, update_dto)

    assert result is not None
    assert result.ingredient_name == "Updated Item"
    assert result.quantity == 2.0
    assert result.unit == "kg"


def test_update_item_not_found(session):
    """Test updating a non-existent item."""
    service = ShoppingService(session)

    update_dto = ShoppingItemUpdateDTO(ingredient_name="Updated Item")

    result = service.update_item(999, update_dto)

    assert result is None


def test_delete_item(session):
    """Test deleting a shopping item."""
    # Create an item
    item = ShoppingItem.create_manual("Test Item", 1.0, "piece")
    session.add(item)
    session.commit()
    item_id = item.id

    service = ShoppingService(session)

    result = service.delete_item(item_id)

    assert result is True

    # Verify deletion
    shopping_list = service.get_shopping_list()
    assert len(shopping_list.items) == 0


def test_delete_item_not_found(session):
    """Test deleting a non-existent item."""
    service = ShoppingService(session)

    result = service.delete_item(999)

    assert result is False


def test_toggle_item_status(session):
    """Test toggling item completion status."""
    # Create an item
    item = ShoppingItem.create_manual("Test Item", 1.0, "piece")
    session.add(item)
    session.commit()

    service = ShoppingService(session)

    # Toggle to checked
    result = service.toggle_item_status(item.id)

    assert result is True

    # Verify status change
    updated_item = session.get(ShoppingItem, item.id)
    assert updated_item.have is True

    # Toggle back to unchecked
    result = service.toggle_item_status(item.id)

    assert result is True

    # Verify status change
    updated_item = session.get(ShoppingItem, item.id)
    assert updated_item.have is False


def test_toggle_item_status_not_found(session):
    """Test toggling status of non-existent item."""
    service = ShoppingService(session)

    result = service.toggle_item_status(999)

    assert result is False


def test_clear_completed_items(session):
    """Test clearing completed shopping items."""
    # Create items with different statuses
    item1 = ShoppingItem.create_manual("Incomplete Item", 1.0, "piece")
    item2 = ShoppingItem.create_manual("Complete Item", 2.0, "cup")
    item2.have = True
    session.add_all([item1, item2])
    session.commit()

    service = ShoppingService(session)

    cleared_count = service.clear_completed_items()

    assert cleared_count == 1

    # Verify only incomplete item remains
    shopping_list = service.get_shopping_list()
    assert len(shopping_list.items) == 1
    assert shopping_list.items[0].ingredient_name == "Incomplete Item"


def test_bulk_update_status(session):
    """Test bulk updating item statuses."""
    # Create multiple items
    item1 = ShoppingItem.create_manual("Item 1", 1.0, "piece")
    item2 = ShoppingItem.create_manual("Item 2", 2.0, "cup")
    session.add_all([item1, item2])
    session.commit()

    service = ShoppingService(session)

    # Bulk update
    update_dto = BulkStateUpdateDTO(
        item_updates={item1.id: True, item2.id: True}
    )

    result = service.bulk_update_status(update_dto)

    assert result.success is True
    assert result.updated_count == 2

    # Verify updates
    updated_item1 = session.get(ShoppingItem, item1.id)
    updated_item2 = session.get(ShoppingItem, item2.id)
    assert updated_item1.have is True
    assert updated_item2.have is True


def test_get_shopping_summary(session):
    """Test getting shopping list summary."""
    # Create items with different statuses
    item1 = ShoppingItem.create_manual("Incomplete Item", 1.0, "piece")
    item2 = ShoppingItem.create_manual("Complete Item", 2.0, "cup")
    item2.have = True
    item3 = ShoppingItem.create_from_recipe("Recipe Item", 3.0, "tbsp", "Test")
    session.add_all([item1, item2, item3])
    session.commit()

    service = ShoppingService(session)

    summary = service.get_shopping_summary()

    assert summary.total_items == 3
    assert summary.completed_items == 1
    assert summary.manual_items == 2  # item1 and item2
    assert summary.recipe_items == 1   # item3


def test_search_items(session):
    """Test searching shopping items by name."""
    # Create items
    item1 = ShoppingItem.create_manual("Apple Juice", 1.0, "bottle")
    item2 = ShoppingItem.create_manual("Apple Pie", 1.0, "slice")
    item3 = ShoppingItem.create_manual("Orange Juice", 1.0, "bottle")
    session.add_all([item1, item2, item3])
    session.commit()

    service = ShoppingService(session)

    # Search for "apple"
    results = service.search_items("apple")

    assert len(results) == 2
    item_names = {item.ingredient_name for item in results}
    assert item_names == {"Apple Juice", "Apple Pie"}


def test_get_ingredient_breakdown(session):
    """Test getting ingredient breakdown from recipes."""
    # Create recipes and ingredients
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    ingredient = Ingredient(ingredient_name="Flour", ingredient_category="Baking")
    session.add(ingredient)
    session.commit()

    # Same ingredient in both recipes
    recipe_ing1 = RecipeIngredient(recipe_id=recipe1.id, ingredient_id=ingredient.id, quantity=1.0, unit="cup")
    recipe_ing2 = RecipeIngredient(recipe_id=recipe2.id, ingredient_id=ingredient.id, quantity=2.0, unit="cup")
    session.add_all([recipe_ing1, recipe_ing2])
    session.commit()

    service = ShoppingService(session)

    breakdown = service.get_ingredient_breakdown([recipe1.id, recipe2.id])

    assert len(breakdown.items) == 1
    flour_item = breakdown.items[0]
    assert flour_item.ingredient_name == "Flour"
    assert flour_item.total_quantity == 3.0  # 1.0 + 2.0
    assert flour_item.unit == "cup"
    assert len(flour_item.recipe_breakdown) == 2
