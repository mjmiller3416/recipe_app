# db_formatters.py
"""
Transforms raw widget input into fully-typed domain objects
ready for ApplicationDatabase.save_recipe().
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import List, Optional

from core.helpers.debug_logger import DebugLogger
from database.modules.recipe_module import Recipe, RecipeIngredient


# ── Helpers ─────────────────────────────────────────────────────────────────────
def _clean_directions(raw_text: str) -> str:
    """Collapse multi-line text into trimmed newline-separated steps."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    return "\n".join(lines)

# ── Public builders ─────────────────────────────────────────────────────────────
def build_recipe(
    le_recipe_name,
    cb_recipe_category,
    le_total_time,
    le_servings,
    te_directions,
    ingredient_objs: List[RecipeIngredient],
    image_path: Optional[str] = None,
) -> Recipe:
    """
    Convert form widgets → `Recipe` dataclass instance.

    UI code should gather the ingredient objects first (see `build_ingredient`).
    """
    return Recipe(
        id=None,   # new recipe, DB will assign
        recipe_name=le_recipe_name.text().strip(),
        recipe_category=cb_recipe_category.currentText().strip(),
        total_time=int(le_total_time.text().strip()),
        servings=int(le_servings.text().strip()),
        directions=_clean_directions(te_directions.toPlainText()),
        image_path=image_path if image_path else None,
        ingredients=ingredient_objs,
    )

def build_ingredient(
    le_quantity,
    cb_unit,
    le_ingredient_name,
    cb_ingredient_category,
) -> RecipeIngredient:
    """
    Convert one row of the ingredient editor → `RecipeIngredient`.
    """
    return RecipeIngredient(
        ingredient_id=None,                      # new row, DB will assign
        ingredient_name=le_ingredient_name.text().strip(),
        ingredient_category=cb_ingredient_category.currentText().strip(),
        quantity=float(le_quantity.text().strip()),
        unit=cb_unit.currentText().strip(),
    )
