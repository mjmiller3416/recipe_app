# tests/core/models/test_shopping_models.py

import pytest
from app.core.models.shopping_item import ShoppingItem
from app.core.models.shopping_state import ShoppingState


def test_shopping_item_creation_manual(session):
    """Test creating a manual shopping item."""
    item = ShoppingItem.create_manual("Manual Item", 2.5, "cup")
    session.add(item)
    session.commit()

    assert item.id is not None
    assert item.ingredient_name == "Manual Item"
    assert item.quantity == 2.5
    assert item.unit == "cup"
    assert item.source == "manual"
    assert item.have is False


def test_shopping_item_creation_from_recipe(session):
    """Test creating a shopping item from recipe data."""
    item = ShoppingItem.create_from_recipe("Recipe Item", 1.0, "tbsp", "Spices")
    session.add(item)
    session.commit()

    assert item.id is not None
    assert item.ingredient_name == "Recipe Item"
    assert item.quantity == 1.0
    assert item.unit == "tbsp"
    assert item.category == "Spices"
    assert item.source == "recipe"
    assert item.have is False


def test_shopping_item_key_generation(session):
    """Test shopping item key generation."""
    # Test with unit
    item1 = ShoppingItem.create_manual("Test Item", 1.0, "cup")
    expected_key1 = "test item::cup"
    assert item1.key() == expected_key1

    # Test without unit
    item2 = ShoppingItem.create_manual("Test Item", 1.0)
    expected_key2 = "test item::"
    assert item2.key() == expected_key2

    # Test with state key
    item3 = ShoppingItem.create_manual("Test Item", 1.0, "cup")
    item3.state_key = "custom_key"
    assert item3.key() == "custom_key"


def test_shopping_item_display_label(session):
    """Test shopping item display label."""
    # Test unchecked item with unit
    item1 = ShoppingItem.create_manual("Test Item", 2.5, "cup")
    assert item1.display_label() == "○ Test Item: 2.5 cup"

    # Test checked item without unit
    item2 = ShoppingItem.create_manual("Test Item", 3.0)
    item2.have = True
    assert item2.display_label() == "✓ Test Item: 3.0"


def test_shopping_item_formatted_quantity(session):
    """Test shopping item quantity formatting."""
    # Test whole number
    item1 = ShoppingItem.create_manual("Item", 3.0, "cup")
    assert item1.formatted_quantity() == "3"

    # Test decimal
    item2 = ShoppingItem.create_manual("Item", 2.5, "cup")
    assert item2.formatted_quantity() == "2.5"

    # Test decimal with trailing zeros
    item3 = ShoppingItem.create_manual("Item", 2.50, "cup")
    assert item3.formatted_quantity() == "2.5"


def test_shopping_item_string_representation(session):
    """Test shopping item string representation."""
    item = ShoppingItem.create_manual("Test Item", 2.0, "cup")
    item.have = True
    session.add(item)
    session.commit()

    repr_str = repr(item)
    assert "Test Item" in repr_str
    assert "2.0" in repr_str
    assert "True" in repr_str


def test_shopping_state_creation(session):
    """Test creating a shopping state."""
    state = ShoppingState(
        key="test_key",
        quantity=1.5,
        unit="tbsp",
        checked=True
    )
    session.add(state)
    session.commit()

    assert state.id is not None
    assert state.key == "test_key"
    assert state.quantity == 1.5
    assert state.unit == "tbsp"
    assert state.checked is True


def test_shopping_state_normalize_key(session):
    """Test shopping state key normalization."""
    normalized = ShoppingState.normalize_key("  Test Key  ")
    assert normalized == "test key"


def test_shopping_state_create_key(session):
    """Test shopping state key creation."""
    # Test with unit
    key1 = ShoppingState.create_key("Test Ingredient", "cup")
    assert key1 == "test ingredient::cup"

    # Test without unit
    key2 = ShoppingState.create_key("Test Ingredient")
    assert key2 == "test ingredient::"

    # Test with unit that has trailing period
    key3 = ShoppingState.create_key("Test Ingredient", "tbsp.")
    assert key3 == "test ingredient::tbsp"


def test_shopping_state_string_representation(session):
    """Test shopping state string representation."""
    state = ShoppingState(
        key="test_key",
        quantity=1.0,
        unit="cup",
        checked=True
    )
    session.add(state)
    session.commit()

    repr_str = repr(state)
    assert "test_key" in repr_str
    assert "True" in repr_str


def test_shopping_state_unique_key_constraint(session):
    """Test that shopping state keys are unique."""
    # Create first state
    state1 = ShoppingState(key="unique_key", quantity=1.0, unit="cup", checked=False)
    session.add(state1)
    session.commit()

    # Try to create duplicate key
    state2 = ShoppingState(key="unique_key", quantity=2.0, unit="tbsp", checked=True)
    session.add(state2)

    # This should raise an integrity error due to unique constraint
    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        session.commit()
