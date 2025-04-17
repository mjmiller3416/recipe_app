import csv
from database import DB_INSTANCE

def insert_recipes_from_csv(csv_file):
    recipes = {}
    
    # Read CSV file
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipe_name = row["recipe_name"]

            # If recipe not seen before, add it
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

            # Append ingredients to the recipe
            recipes[recipe_name]["ingredients"].append({
                "ingredient_name": row["ingredient_name"],
                "quantity": float(row["quantity"]),
                "unit": row["unit"],
                "ingredient_category": row["ingredient_category"],
            })

    # Insert each recipe and its ingredients
    for recipe_name, data in recipes.items():
        recipe_id = DB_INSTANCE.save_recipe(data["recipe_data"])
        if recipe_id:
            DB_INSTANCE.save_ingredients(recipe_id, data["ingredients"])
            print(f"✅ Added Recipe: {recipe_name} with {len(data['ingredients'])} ingredients")

# Run the function
insert_recipes_from_csv("database/recipes_with_ingredients.csv")
