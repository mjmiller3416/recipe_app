# ── Imports ─────────────────────────────────────────────────────────────────────
from collections import defaultdict
from typing import Any, Dict, List

from database.db import get_connection
from database.models.ingredient import Ingredient
from database.models.recipe_ingredient import RecipeIngredient
from database.models.shopping_list import ShoppingList

# ── Constants ───────────────────────────────────────────────────────────────────
_CONVERSIONS = {
    "butter": {"stick": 8, "tbsp": 1},
    # a simple conversion map for special cases (butter, etc.)
    # add more: e.g. sugar: {"cup":1, "tbsp":1/16}, etc.
}

# ── Public Methods ──────────────────────────────────────────────────────────────
def _convert_qty(name: str, qty: float, unit: str) -> tuple[float, str]:
    """If `name` has a conversion group, convert `qty`+`unit` into the best display."""
    key = name.lower()
    if key in _CONVERSIONS:
        group = _CONVERSIONS[key]
        # convert everything into the base unit (smallest factor)
        base = unit
        factor = group.get(unit)
        if factor is None:
            return qty, unit
        qty_base = qty * factor
        # pick the largest unit that divides cleanly
        for u, f in sorted(group.items(), key=lambda it: -it[1]):
            if qty_base % f == 0:
                return qty_base // f, u
        # fallback: return in base unit
        return qty_base / group[base], base
    return qty, unit

def generate_shopping_list(recipe_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Returns a list of dicts, each with:
      - ingredient_name, quantity, unit, category, source="recipe" or "manual", have (for manual)
    """
    # ── Aggregate Recipe Ingredients ──
    agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {"qty": 0, "unit": None, "category": None, "name": None})
    for ri in RecipeIngredient.filter(recipe_id__in=recipe_ids):
        ing = Ingredient.get(ri.ingredient_id)
        data = agg[ri.ingredient_id]
        data["name"]     = ing.ingredient_name
        data["category"] = ing.ingredient_category
        data["unit"]     = ri.unit or data["unit"]
        data["qty"]     += (ri.quantity or 0)

    # ── Build Results ──
    result = []
    for ing_id, data in agg.items():
        q, u = _convert_qty(data["name"], data["qty"], data["unit"]) # convert to best display
        result.append({
            "ingredient_name": data["name"],
            "quantity": q,
            "unit": u,
            "category": data["category"],
            "source": "recipe",
            "have": False
        })

    # ── Append Manual Enteries ──
    for m in ShoppingList.all():
        result.append({
            "ingredient_name": m.ingredient_name,
            "quantity": m.quantity,
            "unit": m.unit,
            "category": None,
            "source": "manual",
            "have": m.have
        })

    return result
