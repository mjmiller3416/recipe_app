"""Script to insert recipes and their ingredients from a CSV file into the database."""

# ── Imports ───────────────────────────────────────────────────────────────
import csv

# 🔹 Local Application Imports
from database import DB_INSTANCE


def insert_recipes_from_csv(csv_file: str) -> None:
    """Reads a CSV file and inserts unique recipes and ingredients into the database.

    Args:
        csv_file (str): Path to the CSV file containing recipe and ingredient data.
    """
    recipes = {}

    # ── Read and organize CSV data ───────────────────────────────────────────
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipe_name = row["recipe_name"]

            if recipe_name not in recipes:
                recipes[recipe_name] = {
                    "recipe_data": {
                        "recipe_name": recipe_name,
                        "recipe_category": row["recipe_category"],
                        "total_time": int(row["total_time"]),
                        "servings": int(row["servings"]),
                        "directions": row["directions"],
                        "image_path": row["image_path"],
                    },
                    "ingredients": []
                }

            # Add each ingredient to the recipe's ingredient list
            recipes[recipe_name]["ingredients"].append({
                "ingredient_name": row["ingredient_name"],
                "quantity": float(row["quantity"]),
                "unit": row["unit"],
                "ingredient_category": row["ingredient_category"],
            })

    # ── Insert into database ─────────────────────────────────────────────────
    inserted_count = 0
    skipped_count = 0

    for recipe_name, data in recipes.items():
        recipe_category = data["recipe_data"]["recipe_category"]

        if not DB_INSTANCE.recipe_exists(recipe_name, recipe_category):
            recipe_id = DB_INSTANCE.save_recipe(data["recipe_data"])
            if recipe_id:
                DB_INSTANCE.save_ingredients(recipe_id, data["ingredients"])
                print(f"✅ Added Recipe: {recipe_name} ({len(data['ingredients'])} ingredients)")
        else:
            print(f"⚠️ Skipped existing Recipe: {recipe_name}")
            skipped_count += 1

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n✨ Import complete: {inserted_count} added, {skipped_count} skipped.\n")


# ── Extend Database Class ───────────────────────────────────────────────────
# (Put this in your database.py!)


