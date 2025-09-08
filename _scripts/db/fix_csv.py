# fix_csv.py (in recipe_app/database)
import os


# 1. Locate files relative to this script’s folder
BASE_DIR = os.path.dirname(__file__)  # .../recipe_app/database
INPUT_CSV  = os.path.join(BASE_DIR, 'recipes_with_ingredients.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'recipes_with_ingredients_multiline.csv')

with open(INPUT_CSV, 'r', encoding='utf-8') as infile:
    raw = infile.read()

fixed = raw.replace('\\n', '\n')

with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as outfile:
    outfile.write(fixed)

print(f"✅ Done! Wrote fixed CSV to:\n  {OUTPUT_CSV}")
