# tests/core/repos/test_shopping_repo.py

from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.models.shopping_item import ShoppingItem
from app.core.models.shopping_state import ShoppingState
from app.core.repositories.shopping_repo import ShoppingRepo


def test_get_recipe_ingredients_empty(session):
    """Test getting recipe ingredients when no recipes exist."""
    repo = ShoppingRepo(session)

    ingredients = repo.get_recipe_ingredients([])

    assert ingredients == []


def test_get_recipe_ingredients(session):
    """Test getting recipe ingredients for specific recipes."""
    # Create recipes, ingredients, and recipe_ingredients
    recipe1 = Recipe(recipe_name="Recipe 1", recipe_category="Test", meal_type="Dinner")
    recipe2 = Recipe(recipe_name="Recipe 2", recipe_category="Test", meal_type="Dinner")
    session.add_all([recipe1, recipe2])
    session.commit()

    ingredient1 = Ingredient(ingredient_name="Ingredient 1", ingredient_category="Test")
    ingredient2 = Ingredient(ingredient_name="Ingredient 2", ingredient_category="Test")
    session.add_all([ingredient1, ingredient2])
    session.commit()

    recipe_ing1 = RecipeIngredient(recipe_id=recipe1.id, ingredient_id=ingredient1.id, quantity=1.0, unit="cup")
    recipe_ing2 = RecipeIngredient(recipe_id=recipe2.id, ingredient_id=ingredient2.id, quantity=2.0, unit="tbsp")
    session.add_all([recipe_ing1, recipe_ing2])
    session.commit()

    repo = ShoppingRepo(session)

    # Get ingredients for recipe1
    ingredients = repo.get_recipe_ingredients([recipe1.id])

    assert len(ingredients) == 1
    assert ingredients[0].recipe_id == recipe1.id
    assert ingredients[0].ingredient_id == ingredient1.id


def test_aggregate_ingredients(session):
    """Test aggregating ingredients with quantity consolidation."""
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

    repo = ShoppingRepo(session)

    aggregated = repo.aggregate_ingredients([recipe1.id, recipe2.id])

    assert len(aggregated) == 1
    agg_item = aggregated[0]
    assert agg_item.ingredient_name == "Flour"
    assert agg_item.quantity == 3.0  # 1.0 + 2.0
    assert agg_item.unit == "cup"


def test_create_shopping_items_from_recipes(session):
    """Test creating shopping items from recipe ingredients."""
    # Create recipe and ingredient
    recipe = Recipe(recipe_name="Test Recipe", recipe_category="Test", meal_type="Dinner")
    session.add(recipe)
    session.commit()

    ingredient = Ingredient(ingredient_name="Test Ingredient", ingredient_category="Test")
    session.add(ingredient)
    session.commit()

    recipe_ing = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=1.5, unit="tsp")
    session.add(recipe_ing)
    session.commit()

    repo = ShoppingRepo(session)

    # Create shopping items
    created_items = repo.create_shopping_items_from_recipes([recipe.id])

    assert len(created_items) == 1
    item = created_items[0]
    assert item.ingredient_name == "Test Ingredient"
    assert item.quantity == 1.5
    assert item.unit == "tsp"
    assert item.source == "recipe"


def test_get_all_shopping_items(session):
    """Test getting all shopping items."""
    # Create shopping items
    item1 = ShoppingItem.create_manual("Item 1", 1.0, "piece")
    item2 = ShoppingItem.create_manual("Item 2", 2.0, "cup")
    session.add_all([item1, item2])
    session.commit()

    repo = ShoppingRepo(session)

    items = repo.get_all_shopping_items()

    assert len(items) == 2
    item_names = {item.ingredient_name for item in items}
    assert item_names == {"Item 1", "Item 2"}


def test_add_manual_item(session):
    """Test adding a manual shopping item."""
    repo = ShoppingRepo(session)

    item = ShoppingItem.create_manual("Manual Item", 3.0, "lb")
    added_item = repo.add_manual_item(item)

    assert added_item.id is not None
    assert added_item.ingredient_name == "Manual Item"
    assert added_item.source == "manual"


def test_update_item_status(session):
    """Test updating shopping item status."""
    item = ShoppingItem.create_manual("Test Item", 1.0, "piece")
    session.add(item)
    session.commit()

    repo = ShoppingRepo(session)

    # Update item status
    result = repo.update_item_status(item.id, True)

    assert result is True

    # Verify update
    updated_item = session.get(ShoppingItem, item.id)
    assert updated_item.have is True


def test_delete_item(session):
    """Test deleting a shopping item."""
    item = ShoppingItem.create_manual("Test Item", 1.0, "piece")
    session.add(item)
    session.commit()
    item_id = item.id

    repo = ShoppingRepo(session)

    # Delete item
    result = repo.delete_item(item_id)

    assert result is True

    # Verify deletion
    deleted_item = session.get(ShoppingItem, item_id)
    assert deleted_item is None


def test_clear_recipe_items(session):
    """Test clearing all recipe-generated items."""
    # Create both manual and recipe items
    manual_item = ShoppingItem.create_manual("Manual Item", 1.0, "piece")
    recipe_item = ShoppingItem.create_from_recipe("Recipe Item", 2.0, "cup", "Test")
    session.add_all([manual_item, recipe_item])
    session.commit()

    repo = ShoppingRepo(session)

    # Clear recipe items
    repo.clear_recipe_items()
    session.commit()

    # Verify only manual item remains
    remaining_items = repo.get_all_shopping_items()
    assert len(remaining_items) == 1
    assert remaining_items[0].source == "manual"


def test_get_shopping_state(session):
    """Test getting shopping state by key."""
    state = ShoppingState(key="test_key", quantity=1.0, unit="cup", checked=True)
    session.add(state)
    session.commit()

    repo = ShoppingRepo(session)

    retrieved_state = repo.get_shopping_state("test_key")

    assert retrieved_state is not None
    assert retrieved_state.key == "test_key"
    assert retrieved_state.checked is True


def test_save_shopping_state(session):
    """Test saving shopping state."""
    repo = ShoppingRepo(session)

    # Save new state
    repo.save_shopping_state("new_key", 2.0, "tbsp", True)
    session.commit()

    # Verify state was saved
    saved_state = repo.get_shopping_state("new_key")
    assert saved_state is not None
    assert saved_state.quantity == 2.0
    assert saved_state.unit == "tbsp"
    assert saved_state.checked is True


def test_update_shopping_state(session):
    """Test updating existing shopping state."""
    # Create initial state
    state = ShoppingState(key="update_key", quantity=1.0, unit="cup", checked=False)
    session.add(state)
    session.commit()

    repo = ShoppingRepo(session)

    # Update state
    repo.save_shopping_state("update_key", 3.0, "cup", True)
    session.commit()

    # Verify update
    updated_state = repo.get_shopping_state("update_key")
    assert updated_state.quantity == 3.0
    assert updated_state.checked is True


def test_bulk_update_states(session):
    """Test bulk updating multiple shopping states."""
    # Create multiple states
    state1 = ShoppingState(key="key1", quantity=1.0, unit="cup", checked=False)
    state2 = ShoppingState(key="key2", quantity=2.0, unit="tbsp", checked=False)
    session.add_all([state1, state2])
    session.commit()

    repo = ShoppingRepo(session)

    # Bulk update
    updates = {"key1": True, "key2": True}
    updated_count = repo.bulk_update_states(updates)

    assert updated_count == 2

    # Verify updates
    assert repo.get_shopping_state("key1").checked is True
    assert repo.get_shopping_state("key2").checked is True
