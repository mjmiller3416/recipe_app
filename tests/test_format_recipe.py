# tests/test_format_recipe.py

from app.helpers.formatters import format_recipe_data


def test_format_includes_meal_type():
    sample = {
        "name": "Pancakes",
        "ingredients": ["Flour", "Eggs"],
        "meal_type": "Breakfast",
    }
    result = format_recipe_data(sample)
    assert "Meal Type: Breakfast" in result
