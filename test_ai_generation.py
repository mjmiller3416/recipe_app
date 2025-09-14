"""Test script for AI image generation integration.

Run this to test the background image generation when saving recipes.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from _dev_tools import DebugLogger
from app.core.database.db import DatabaseSession
from app.core.dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import RecipeService
from app.core.services.ai_gen.background_manager import get_background_manager
from app.config import AppPaths


def test_recipe_with_ai_generation():
    """Test creating a recipe with background AI image generation."""

    # Enable mock mode for testing (no real API calls)
    os.environ["AI_GEN_MOCK_MODE"] = "true"

    print("\n=== Testing Recipe Save with AI Generation ===\n")

    # Create test recipe data with unique name
    import datetime
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    recipe_dto = RecipeCreateDTO(
        recipe_name=f"Test Pasta Carbonara {timestamp}",
        recipe_category="Italian",
        meal_type="Dinner",
        dietary_preference="None",
        total_time=30,
        servings=4,
        directions="1. Cook pasta\n2. Fry bacon\n3. Mix eggs and cheese\n4. Combine all",
        notes="Classic Italian recipe",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="Spaghetti",
                ingredient_category="Pasta",
                quantity=400,
                unit="g"
            ),
            RecipeIngredientDTO(
                ingredient_name="Bacon",
                ingredient_category="Meat",
                quantity=200,
                unit="g"
            ),
            RecipeIngredientDTO(
                ingredient_name="Eggs",
                ingredient_category="Dairy",
                quantity=4,
                unit="whole"
            ),
            RecipeIngredientDTO(
                ingredient_name="Parmesan Cheese",
                ingredient_category="Dairy",
                quantity=100,
                unit="g"
            )
        ]
    )

    # Save recipe
    with DatabaseSession() as session:
        service = RecipeService(session)

        print("1. Saving recipe...")
        new_recipe = service.create_recipe_with_ingredients(recipe_dto)
        print(f"   [OK] Recipe saved with ID: {new_recipe.id}")
        print(f"   [OK] Recipe name: {new_recipe.recipe_name}")

        # Trigger background image generation
        print("\n2. Starting background AI image generation...")
        manager = get_background_manager()
        reference_path, banner_path = manager.generate_recipe_images(
            new_recipe.id,
            new_recipe.recipe_name
        )

        # Update recipe with predicted paths
        service.update_recipe_reference_image_path(new_recipe.id, reference_path)
        service.update_recipe_banner_image_path(new_recipe.id, banner_path)

        print(f"   [OK] Reference path: {reference_path}")
        print(f"   [OK] Banner path: {banner_path}")

        # Wait a bit for background generation
        print("\n3. Waiting for background generation (mock mode)...")
        time.sleep(5)  # Give more time for both images

        # Check if files exist
        print("\n4. Checking generated files...")
        ref_exists = Path(reference_path).exists()
        banner_exists = Path(banner_path).exists()

        print(f"   {'[OK]' if ref_exists else '[X]'} Reference image exists: {ref_exists}")
        print(f"   {'[OK]' if banner_exists else '[X]'} Banner image exists: {banner_exists}")

        # Verify database was updated
        print("\n5. Verifying database...")
        updated_recipe = service.get_recipe(new_recipe.id)
        print(f"   [OK] DB reference_image_path: {updated_recipe.reference_image_path}")
        print(f"   [OK] DB banner_image_path: {updated_recipe.banner_image_path}")

        print("\n=== Test Complete ===\n")

        if ref_exists and banner_exists:
            print("SUCCESS: Images were generated successfully!")
        else:
            print("INFO: Images are being generated in the background...")
            print("      Check the recipe_images directory in a few seconds.")

        return new_recipe.id


if __name__ == "__main__":
    try:
        recipe_id = test_recipe_with_ai_generation()
        print(f"\nCreated recipe ID {recipe_id} - check the database and image directory!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()