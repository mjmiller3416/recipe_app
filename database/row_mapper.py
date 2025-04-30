# database/row_mapper.py
from database.modules.recipe_module import Recipe, RecipeIngredient


def rows_to_recipe(recipe_row: dict, ingredient_rows: list[dict]) -> Recipe:
    ingredients = [RecipeIngredient(**ing) for ing in ingredient_rows]
    return Recipe(**recipe_row, ingredients=ingredients)

def recipe_to_rows(recipe: Recipe) -> tuple[dict, list[dict]]:
    core = {
        "recipe_name":    recipe.recipe_name,
        "recipe_category":recipe.recipe_category,
        "total_time":     recipe.total_time,
        "servings":       recipe.servings,
        "directions":     recipe.directions,
        "image_path":     recipe.image_path or "",
    }
    ing_rows = [
        {
            "ingredient_id":    ing.ingredient_id,
            "ingredient_name":  ing.ingredient_name,
            "ingredient_category": ing.ingredient_category,
            "quantity":         ing.quantity,
            "unit":             ing.unit
        }
        for ing in recipe.ingredients
    ]
    return core, ing_rows
