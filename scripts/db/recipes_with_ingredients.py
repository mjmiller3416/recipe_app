"""Script to insert recipes and their ingredients from a CSV file into the database."""

# ── Imports ───────────────────────────────────────────────────────────────
import csv
from typing import List

# 🔹 Local Imports
from database.db import get_connection
from database.models.recipe import Recipe as RecipeModel
from database.models.recipe_ingredient_detail import RecipeIngredientDetail as IngredientModel
import sys
from pathlib import Path

# Add root directory to sys.path (adjust as needed!)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

def insert_recipes_from_csv(csv_file: str) -> None:
    """Reads a CSV file and inserts unique recipes and ingredients into the database."""
    recipes: dict[str, dict] = {}
    csv_path = Path(csv_file)

    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return

    # ── Read CSV ────────────────────────────────────────────────────────────
    with csv_path.open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row["recipe_name"]

            if name not in recipes:
                recipes[name] = {
                    "recipe_data": RecipeModel(
                        recipe_name=name,
                        recipe_category=row["recipe_category"],
                        total_time=int(row["total_time"]),
                        servings=int(row["servings"]),
                        directions=row["directions"],
                        image_path=row["image_path"]
                    ),
                    "ingredients": []
                }

            # Add ingredient
            recipes[name]["ingredients"].append(IngredientModel(
                ingredient_name=row["ingredient_name"],
                ingredient_category=row["ingredient_category"],
                quantity=float(row["quantity"]),
                unit=row["unit"]
            ))

    # ── Insert into DB ───────────────────────────────────────────────────────
    inserted_count = 0
    skipped_count = 0

    for name, data in recipes.items():
        recipe = data["recipe_data"]
        ingredients: List[IngredientModel] = data["ingredients"]

        if RecipeModel.exists(recipe_name=recipe.recipe_name, recipe_category=recipe.recipe_category):
            print(f"⚠️ Skipped existing Recipe: {name}")
            skipped_count += 1
            continue

        recipe.save()
        inserted_count += 1
        print(f"✅ Added Recipe: {name} ({len(ingredients)} ingredients)")

        # Insert into join table
        with get_connection() as conn:
            for ing in ingredients:
                # Check or insert ingredient into ingredients table
                cursor = conn.execute(
                    "SELECT id FROM ingredients WHERE ingredient_name = ? AND ingredient_category = ?",
                    (ing.ingredient_name, ing.ingredient_category)
                )
                row = cursor.fetchone()
                if row:
                    ingredient_id = row["id"]
                else:
                    result = conn.execute(
                        "INSERT INTO ingredients (ingredient_name, ingredient_category) VALUES (?, ?)",
                        (ing.ingredient_name, ing.ingredient_category)
                    )
                    ingredient_id = result.lastrowid

                # Insert into join table
                conn.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                    (recipe.id, ingredient_id, ing.quantity, ing.unit)
                )

    print(f"\n✨ Import complete: {inserted_count} added, {skipped_count} skipped.\n")


if __name__ == "__main__":
    # You can hardcode a test file path, or later switch to argparse
    csv_path = "scripts/db/recipes_with_ingredients_multiline.csv"  # ← change this to match your actual CSV path
    insert_recipes_from_csv(csv_path)