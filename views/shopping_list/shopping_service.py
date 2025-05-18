"""services/shopping_service.py

Structured service for managing shopping lists.
Combines ingredients from recipes and manual entries for unified display and processing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from collections import defaultdict
from typing import Any, Dict, List

from core.helpers.debug_logger import DebugLogger
from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe_ingredient import RecipeIngredient
from database.models.shopping_item import ShoppingItem
from database.models.shopping_list import ShoppingList
from database.models.shopping_state import ShoppingState
from views.meal_planner.meal_service import MealService


# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingService:
    """
    Structured service for managing shopping lists.
    Combines ingredients from recipes and manual entries for unified display and processing.
    """

    # ── Constants ───────────────────────────────────────────────────────────────────
    _CONVERSIONS = {
        "butter": {"stick": 8, "tbsp": 1},
        # Add more: e.g. sugar: {"cup":1, "tbsp":1/16}
    }

    @staticmethod
    def _convert_qty(name: str, qty: float, unit: str) -> tuple[float, str]:
        """
        Convert quantity and unit to a base unit for consistent representation.

        Args:
            name (str): The name of the ingredient.
            qty (float): The quantity of the ingredient.
            unit (str): The unit of measurement.

        Returns:
            tuple[float, str]: A tuple containing the converted quantity and unit.
        """
        key = name.lower()
        if key in ShoppingService._CONVERSIONS:
            group = ShoppingService._CONVERSIONS[key]
            base = unit
            factor = group.get(unit)
            if factor is None:
                return qty, unit
            qty_base = qty * factor
            for u, f in sorted(group.items(), key=lambda it: -it[1]):
                if qty_base % f == 0:
                    return qty_base // f, u
            return qty_base / group[base], base
        return qty, unit

    @staticmethod
    def generate_shopping_list(recipe_ids: List[int]) -> List[ShoppingItem]:
        """
        Generate a shopping list based on the provided recipe IDs,
        restoring 'checked' states from persisted ShoppingState.

        Args:
            recipe_ids (List[int]): A list of recipe IDs.

        Returns:
            List[ShoppingItem]: A list of ShoppingItem objects representing the shopping list.
        """
        result = []

        # ── Load from Recipes ──
        for item in ShoppingService._aggregate_recipe_ingredients(recipe_ids):
            from database.models.shopping_state import ShoppingState  # local import to avoid circular refs

            state = ShoppingState.get_state(item.key())
            if state:
                item.have = state.checked
            result.append(item)

        # ── Append Manual Items ──
        for m in ShoppingList.all():
            result.append(m.to_item())

        DebugLogger.log(f"[ShoppingService] Total ingredients generated: {len(result)}", "info")
        return result

    @staticmethod
    def _aggregate_recipe_ingredients(recipe_ids: List[int]) -> List[ShoppingItem]:
        """
        Aggregate ingredients from recipes into a shopping list.

        Args:
            recipe_ids (List[int]): A list of recipe IDs.

        Returns:
            List[ShoppingItem]: A list of ShoppingItem objects representing the aggregated ingredients.
        """
        agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            "qty": 0,
            "unit": None,
            "category": None,
            "name": None
        })

        # ── Aggregate Ingredients ──
        for ri in RecipeIngredient.all():
            if ri.recipe_id in recipe_ids:
                ing = Ingredient.get(ri.ingredient_id)

                data = agg[ri.ingredient_id]
                data["name"]     = ing.ingredient_name
                data["category"] = ing.ingredient_category
                data["unit"]     = ri.unit or data["unit"]
                data["qty"]     += ri.quantity or 0

        items: List[ShoppingItem] = []

        # ── Convert and Create ShoppingItem ──
        for ing_id, data in agg.items():
            q, u = ShoppingService._convert_qty(data["name"], data["qty"], data["unit"] or "")
            item = ShoppingItem(
                ingredient_name=data["name"],
                quantity=q,
                unit=u,
                category=data["category"],
                source="recipe",
                have=False  # will be updated if a state exists
            )

            # check if we’ve seen this item before and apply its state
            state = ShoppingState.get_state(item.key())
            if state:
                item.have = state.checked

            items.append(item)
        return items

    @staticmethod
    def get_recipe_ids_from_meals(meal_ids: List[int]) -> List[int]:
        """
        Get recipe IDs from a list of meal IDs.

        Args:
            meal_ids (List[int]): A list of meal IDs.

        Returns:
            List[int]: A list of recipe IDs associated with the meals.
        """
        recipe_ids = []
        for meal_id in meal_ids:
            meal = MealService.load_meal(meal_id)
            if not meal:
                continue
            recipe_ids.append(meal.main_recipe_id)
            if meal.side_recipe_1:
                recipe_ids.append(meal.side_recipe_1)
            if meal.side_recipe_2:
                recipe_ids.append(meal.side_recipe_2)
            if meal.side_recipe_3:
                recipe_ids.append(meal.side_recipe_3)
        return recipe_ids

    @staticmethod
    def add_manual_item(name: str, qty: float, unit: str) -> None:
        """
        Add a manual item to the shopping list.

        Args:
            name (str): The name of the ingredient.
            qty (float): The quantity of the ingredient.
            unit (str): The unit of measurement.
        """
        item = ShoppingList(
            ingredient_name=name,
            quantity=qty,
            unit=unit,
            have=False
        )
        item.save()

    @staticmethod
    def clear_manual_items() -> None:
        """Clear all manual items from the shopping list."""
        for item in ShoppingList.all():
            item.delete()

    @staticmethod
    def toggle_have_status(item_name: str) -> None:
        """
        Toggle the 'have' status of a shopping list item.
        
        Args:
            item_name (str): The name of the ingredient.
        """
        for item in ShoppingList.all():
            if item.ingredient_name == item_name:
                item.have = not item.have
                item.save()
                break
