import sys
from pathlib import Path
import pytest
from app.core.dtos import RecipeCreateDTO, RecipeIngredientInputDTO
from app.core.services.recipe_service import RecipeService
from app.core.features.recipes.recipe_model import Recipe
from app.core.models.ingredient import Ingredient
from app.core.database.db import get_connection
import uuid

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture
def sample_recipe(tmp_path):
    unique_name = f"UnitTest Stew {uuid.uuid4()}"
    image_dir = Path("data_files/recipe_images")
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"test_{uuid.uuid4().hex}.png"
    image_path.write_bytes(b"fake")

    dto = RecipeCreateDTO(
        recipe_name=unique_name,
        recipe_category="Chicken",
        meal_type="Dinner",
        total_time=45,
        servings=4,
        directions="Step1\nStep2",
        image_path=str(image_path),
        ingredients=[
            RecipeIngredientInputDTO(
                ingredient_name="Chicken Breast",
                ingredient_category="meat",
                quantity=1,
                unit="lb",
            ),
            RecipeIngredientInputDTO(
                ingredient_name="Salt",
                ingredient_category="spices",
                quantity=1,
                unit="tsp",
            ),
        ],
    )
    recipe = RecipeService.create_recipe_with_ingredients(dto)
    yield recipe, image_path
    with get_connection() as conn:
        conn.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (recipe.id,))
        conn.execute("DELETE FROM recipes WHERE id=?", (recipe.id,))
    image_path.unlink(missing_ok=True)

def test_save_recipe_fields(sample_recipe):
    recipe, img_path = sample_recipe
    fetched = Recipe.get(recipe.id)
    assert fetched.recipe_name.startswith("UnitTest Stew")
    assert fetched.recipe_category == "Chicken"
    assert fetched.meal_type == "Dinner"
    assert fetched.total_time == 45
    assert fetched.servings == 4
    assert fetched.directions == "Step1\nStep2"
    assert fetched.image_path == str(img_path)
    assert img_path.exists()
    links = fetched.get_recipe_ingredients()
    assert len(links) == 2
    names = [
        Ingredient.get(link.ingredient_id).ingredient_name
        for link in links
    ]
    assert "Chicken Breast" in names
    assert "Salt" in names

def test_fetch_recipe_details(sample_recipe, capsys):
    recipe, img_path = sample_recipe
    fetched = Recipe.get(recipe.id)
    print("ID:", fetched.id)
    print("Name:", fetched.recipe_name)
    print("Category:", fetched.recipe_category)
    print("Meal Type:", fetched.meal_type)
    print("Servings:", fetched.servings)
    print("Cook Time:", fetched.total_time)
    print("Directions:", fetched.directions)
    for link in fetched.get_recipe_ingredients():
        ing = Ingredient.get(link.ingredient_id)
        print("Ingredient:", ing.ingredient_name, ing.ingredient_category, link.quantity, link.unit)
    captured = capsys.readouterr()
    assert str(fetched.id) in captured.out
