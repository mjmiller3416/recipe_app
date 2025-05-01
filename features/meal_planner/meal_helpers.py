# recipe_app/meal_planner/meal_helpers.py
"""
Module: meal_planner.meal_helpers

This module provides helper functions for loading, saving, and updating meal plans in the MealPlanner.
It includes functions to load saved meal plans from QSettings, save the current meal plan, and save all meals in the planner.

Main Functions:
    - load_meal_plan(callback): Loads saved meal IDs from QSettings and uses a callback to populate the UI.
    - save_meal_plan(tab_map): Saves the meal IDs associated with the tabs to QSettings.
    - save_all_meals(tab_map): Saves or updates all open meals in the database based on the current tab map.
"""

# 🔸 Third-party Imports
from core.helpers.qt_imports import QSettings
from database.database import DB_INSTANCE
# 🔸 Local Application Imports
from helpers.app_helpers.debug_logger import DebugLogger


def load_meal_plan(callback):
    """
    Load saved meal IDs from QSettings and use callback to populate UI tabs.

    Args:
        callback (function): A function that takes `meal_data` and `meal_id` as arguments to populate the UI.

    Returns:
        bool: True if any meals were loaded, False otherwise.
    """
    DebugLogger.log("Attempting to load saved meal plan...", "info")
    settings = QSettings("MyCompany", "MealGenie")
    saved_meal_ids = settings.value("active_meal_ids", [])

    if not saved_meal_ids:
        DebugLogger.log("No saved meal IDs found in QSettings.", "info")
        return False

    loaded_any = False
    for meal_id in saved_meal_ids:
        meal = DB_INSTANCE.get_meal(meal_id)
        if not meal:
            DebugLogger.log(f"Meal ID {meal_id} not found in DB.", "warning")
            continue

        meal_data = {
            "main": meal.get("main_recipe_id"),
            "side1": meal.get("side_recipe_1"),
            "side2": meal.get("side_recipe_2"),
            "side3": meal.get("side_recipe_3"),
        }
        callback(meal_data=meal_data, meal_id=meal_id)
        loaded_any = True

    return loaded_any


def save_meal_plan(tab_map):
    """
    Save all tab-associated meal IDs to QSettings.

    Args:
        tab_map (dict): A dictionary mapping tab indices to their associated meal information.
    """
    settings = QSettings("MyCompany", "MealGenie")
    meal_ids = [
        info["meal_id"]
        for info in tab_map.values()
        if info.get("meal_id")
    ]
    settings.setValue("active_meal_ids", meal_ids)
    DebugLogger.log(f"[MealPlanner] Saved active meal tab IDs: {meal_ids}", "info")


def save_all_meals(tab_map):
    """
    Save or update all open meals from tab_map in the database.

    Args:
        tab_map (dict): A dictionary mapping tab indices to their associated meal information.
    """
    for index, tab_info in tab_map.items():
        layout = tab_info["layout"]
        meal_id = tab_info["meal_id"]
        data = layout.get_meal_data()

        if not data.get("main"):
            DebugLogger.log(f"[MealPlanner] Skipped saving tab {index}: No main recipe selected.", "warning")
            continue

        if meal_id is None:
            meal_id = DB_INSTANCE.save_meal("Custom Meal", data["main"], [data["side1"], data["side2"], data["side3"]])
            tab_info["meal_id"] = meal_id
            DebugLogger.log(f"[MealPlanner] Saved new meal ID: {meal_id} from tab {index}", "success")
        else:
            DB_INSTANCE.update_meal(meal_id, data)
            DebugLogger.log(f"[MealPlanner] Updated meal ID: {meal_id} from tab {index}", "info")
