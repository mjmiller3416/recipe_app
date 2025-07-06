"""
scripts/db/recipes_with_ingredients.py

Script to insert recipes and their ingredients from a CSV file into the database
using the updated SQLAlchemy-based services.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import csv
from pathlib import Path
from typing import Dict, Tuple, Any

from app.core.database.db import create_session
from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService, DuplicateRecipeError, RecipeSaveError
from dev_tools import DebugLogger

def insert_recipes_from_csv(csv_file: str) -> None:
    """
    Reads a CSV file and inserts unique recipes with their ingredients via RecipeService.
    """
    recipes: Dict[Tuple[str, str], Dict[str, Any]] = {}
    csv_path = Path(csv_file)

    if not csv_path.exists():
        DebugLogger.log(f"❌ CSV file not found: {csv_file}", "error")
        return

    # ── Read CSV and group rows by (name, category) ────────────────────────────────────────────
    with csv_path.open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                recipe_name = row["recipe_name"].strip()
                recipe_category = row["recipe_category"].strip()
                total_time = int(row.get("total_time", 0)) if row.get("total_time") else None
                servings = int(row.get("servings", 0)) if row.get("servings") else None
                directions = row.get("directions", "").strip()
                image_path = row.get("image_path", "").strip()
                ingredient_name = row["ingredient_name"].strip()
                ingredient_category = row["ingredient_category"].strip()
                quantity = float(row["quantity"]) if row.get("quantity") else None
                unit = row.get("unit", "").strip()
            except Exception as e:
                DebugLogger.log(f"❌ Error parsing CSV row: {e}", "error")
                continue

            key = (recipe_name, recipe_category)
            if key not in recipes:
                recipes[key] = {"recipe_data": {
                    "recipe_name": recipe_name,
                    "recipe_category": recipe_category,
                    "total_time": total_time,
                    "servings": servings,
                    "directions": directions,
                    "image_path": image_path,
                    "ingredients": []
                }}
            recipes[key]["recipe_data"]["ingredients"].append({
                "ingredient_name": ingredient_name,
                "ingredient_category": ingredient_category,
                "quantity": quantity,
                "unit": unit
            })

    # ── Insert into DB via RecipeService ─────────────────────────────────────────────────────
    session = create_session()
    service = RecipeService(session)
    inserted_count = 0
    skipped_count = 0
    error_count = 0

    for (recipe_name, recipe_category), data in recipes.items():
        rd = data["recipe_data"]
        try:
            ing_dtos = [RecipeIngredientDTO(**ing) for ing in rd["ingredients"]]
            create_dto = RecipeCreateDTO(
                recipe_name=rd["recipe_name"],
                recipe_category=rd["recipe_category"],
                total_time=rd.get("total_time"),
                servings=rd.get("servings"),
                directions=rd.get("directions"),
                image_path=rd.get("image_path"),
                ingredients=ing_dtos
            )
            service.create_recipe_with_ingredients(create_dto)
            inserted_count += 1
            DebugLogger.log(f"✅ Added Recipe: {recipe_name} ({len(ing_dtos)} ingredients)", "info")
        except DuplicateRecipeError:
            skipped_count += 1
            DebugLogger.log(f"⚠️ Skipped existing Recipe: {recipe_name}", "warning")
        except RecipeSaveError as e:
            error_count += 1
            DebugLogger.log(f"❌ Error saving Recipe: {recipe_name}: {e}", "error")
        except Exception as e:
            error_count += 1
            DebugLogger.log(f"❌ Unexpected error for Recipe: {recipe_name}: {e}", "error")

    DebugLogger.log(
        f"\n✨ Import complete: {inserted_count} added, {skipped_count} skipped, {error_count} errors.\n",
        "info"
    )
    session.close()

if __name__ == "__main__":
    # file path to the CSV containing recipes and ingredients
    csv_path = "scripts/db/recipes_with_ingredients_multiline.csv"
    insert_recipes_from_csv(csv_path)
