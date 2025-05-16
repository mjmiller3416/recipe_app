"""services/meal_planner_service.py

Service module for managing meal planner data. This includes loading saved meals, creating/updating 
MealSelection entries, and deleting meals from the planner view.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional

from database.models.meal_selection import MealSelection
from database.models.saved_meal_state import SavedMealState
from core.helpers import DebugLogger

# ── Core Meal Planner Service ───────────────────────────────────────────────────

def get_meal_by_id(meal_id: int) -> dict[str, Optional[int]]:
    """
    Get meal data for a given MealSelection.

    Args:
        meal_id (int): The ID of the meal selection.

    Returns:
        dict[str, Optional[int]]: Dictionary with keys: main, side1, side2, side3.
    """
    meal = MealSelection.get(meal_id)
    if not meal:
        return {"main": None, "side1": None, "side2": None, "side3": None}

    return {
        "main": meal.main_recipe_id,
        "side1": meal.side_recipe_1,
        "side2": meal.side_recipe_2,
        "side3": meal.side_recipe_3,
    }

def save_meal(data: dict[str, Optional[int]]) -> int:
    """
    Save a new custom meal to the database.

    Args:
        data (dict): Dictionary with recipe IDs for main and sides.

    Returns:
        int: The ID of the new MealSelection entry.
    """
    meal = MealSelection(
        meal_name="Custom Meal",
        main_recipe_id=data["main"],
        side_recipe_1=data.get("side1"),
        side_recipe_2=data.get("side2"),
        side_recipe_3=data.get("side3"),
    )
    meal.save()
    return meal.id

def update_meal(meal_id: int, data: dict[str, Optional[int]]):
    """
    Update an existing meal with new recipe selections.

    Args:
        meal_id (int): The MealSelection ID to update.
        data (dict): Dictionary with updated main/side recipe IDs.
    """
    MealSelection.update(
        meal_id,
        meal_name="Custom Meal",
        main_recipe_id=data["main"],
        side_recipe_1=data.get("side1"),
        side_recipe_2=data.get("side2"),
        side_recipe_3=data.get("side3"),
    )

def delete_meal(meal_id: int):
    """
    Permanently delete a meal selection from the database.

    Args:
        meal_id (int): ID of the MealSelection to delete.
    """
    meal = MealSelection.get(meal_id)
    if meal:
        meal.delete()

def get_saved_meal_ids() -> list[int]:
    from database.models.saved_meal_state import SavedMealState
    rows = SavedMealState.all()
    meal_ids = [entry.meal_id for entry in rows]
    DebugLogger.log(f"[meal_planner_service.get_saved_meal_ids] Found: {meal_ids}", "info")
    return meal_ids


def save_active_meal_ids(meal_ids: list[int]):
    """Overwrite saved meal state with given IDs."""
    # Clear existing state
    for entry in SavedMealState.all():
        entry.delete()

    # Save new state
    for meal_id in meal_ids:
        SavedMealState(meal_id=meal_id).save()
