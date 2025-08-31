"""Mock data generation for development and testing.

This module provides functions to generate realistic test data for the recipe application.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("Warning: faker not installed. Install with: pip install faker")

from app.core.models.recipe import Recipe
from app.core.database.db import DatabaseSession
from app.config.paths.app_paths import AppPaths

# Initialize Faker if available
fake = Faker() if FAKER_AVAILABLE else None

# ── Mock Data Constants ──────────────────────────────────────────────────────

RECIPE_CATEGORIES = ["Ground Beef", "Chicken", "Seafood", "Veggie", "Other"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
DIETARY_PREFERENCES = ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Paleo"]

SAMPLE_RECIPE_NAMES = [
    "Spaghetti Bolognese", "Caesar Salad", "Stir Fry", "Beef Tacos", "Salmon Herb Butter",
    "Mushroom Risotto", "BBQ Pulled Pork", "Curry Chicken", "Quinoa Bowl", "Pancakes",
    "Avocado Toast", "Chicken Wings", "Stuffed Chicken", "Baked Potato Soup",
    "Honey Garlic Shrimp", "Vegetable Curry", "Bacon Cheeseburger", "Fish and Chips",
    "Greek Salad", "Beef Stroganoff", "Chicken Parmesan", "Veggie Pizza", "Clam Chowder",
    "Pork Chops", "Tuna Sandwich", "Alfredo Pasta", "BBQ Chicken Pizza", "Teriyaki Chicken",
    "Meatball Marinara Subs", "Tomato Soup", "Chicken Noodle Soup", "Mac and Cheese",
    "Grilled Salmon", "Chicken Quesadillas", "Beef Stir Fry", "Margherita Pizza",
    "Turkey Club", "Tikka Masala", "Shepherd's Pie", "Lasagna", "Chicken Fried Rice",
    "Penne Arrabbiata", "BBQ Ribs", "Fish Tacos", "Stuffed Bell Peppers", "Chicken Pot Pie",
    "Beef Chili", "Garlic Butter Pasta", "Baked Chicken Thighs", "Shrimp Fried Rice",
    "Italian Meatballs", "Grilled Portobello Burgers", "Chicken Fajitas", "Baked Ziti",
    "Mongolian Beef", "Lemon Pepper Chicken", "Taco Salad"
]

SAMPLE_DIRECTIONS = [
    [
        "Heat oil in large skillet over medium-high heat",
        "Add onions and cook until softened, about 5 minutes",
        "Add garlic and cook for 1 minute more",
        "Add main ingredients and season with salt and pepper",
        "Cook until done, stirring occasionally",
        "Serve hot and enjoy"
    ],
    [
        "Preheat oven to 375°F (190°C)",
        "Prepare ingredients by washing and chopping as needed",
        "Mix seasonings in small bowl",
        "Place ingredients in baking dish and coat with seasonings",
        "Bake for 25-30 minutes until cooked through",
        "Let rest 5 minutes before serving"
    ],
    [
        "Bring large pot of salted water to boil",
        "Cook pasta according to package directions",
        "Meanwhile, heat sauce in separate pan",
        "Drain pasta and reserve 1 cup pasta water",
        "Toss pasta with sauce, adding pasta water as needed",
        "Garnish and serve immediately"
    ]
]

SAMPLE_NOTES = [
    "This recipe is great for meal prep and leftovers taste even better!",
    "Try substituting different vegetables based on what's in season.",
    "For extra flavor, marinate the protein for 2-4 hours before cooking.",
    "This dish pairs well with a crisp white wine or light beer.",
    "Double the recipe for entertaining - it's always a crowd pleaser.",
    None  # Some recipes won't have notes
]


# ── Mock Data Generators ─────────────────────────────────────────────────────

def create_realistic_recipe() -> Dict[str, Any]:
    """Generate realistic mock recipe data using Faker if available."""
    # Always use realistic recipe names from predefined list
    recipe_name = random.choice(SAMPLE_RECIPE_NAMES)

    if FAKER_AVAILABLE:
        # Use Faker for directions, notes, and dates
        directions_text = "\n".join([
            fake.sentence(nb_words=8) for _ in range(random.randint(4, 8))
        ])
        notes = fake.text(max_nb_chars=150) if random.choice([True, False, False]) else None
        created_at = fake.date_time_between(start_date='-6m', end_date='now')
    else:
        # Fallback to predefined data
        directions_text = "\n".join(random.choice(SAMPLE_DIRECTIONS))
        notes = random.choice(SAMPLE_NOTES)
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 180))

    return {
        'recipe_name': recipe_name,
        'recipe_category': random.choice(RECIPE_CATEGORIES),
        'meal_type': random.choice(MEAL_TYPES),
        'diet_pref': random.choice(DIETARY_PREFERENCES),
        'total_time': random.choice([15, 20, 30, 45, 60, 75, 90, 120]),
        'servings': random.randint(2, 8),
        'directions': directions_text,
        'notes': notes,
        'created_at': created_at,
        'is_favorite': random.choice([True] + [False] * 4)  # 20% chance of favorite
    }

def create_simple_recipe(index: int) -> Dict[str, Any]:
    """Generate simple mock recipe data without external dependencies."""
    return {
        'recipe_name': f"Mock Recipe {index + 1}",
        'recipe_category': random.choice(RECIPE_CATEGORIES),
        'meal_type': random.choice(MEAL_TYPES),
        'diet_pref': random.choice(DIETARY_PREFERENCES),
        'total_time': random.choice([20, 30, 45, 60, 90]),
        'servings': random.randint(2, 6),
        'directions': "\n".join(random.choice(SAMPLE_DIRECTIONS)),
        'notes': random.choice(SAMPLE_NOTES),
        'created_at': datetime.utcnow(),
        'is_favorite': False
    }


# ── Image Handling Functions ─────────────────────────────────────────────────

def get_available_recipe_images() -> tuple[list[str], list[str]]:
    """
    Get lists of available reference and banner images.

    Returns:
        tuple: (reference_images, banner_images) - lists of full file paths
    """
    recipe_images_dir = AppPaths.RECIPE_IMAGES_DIR

    if not recipe_images_dir.exists():
        print(f"Warning: Recipe images directory not found: {recipe_images_dir}")
        return [], []

    # Get all image files
    image_files = list(recipe_images_dir.glob("*.png")) + list(recipe_images_dir.glob("*.jpg")) + list(recipe_images_dir.glob("*.jpeg"))

    # Separate reference and banner images
    reference_images = [str(img) for img in image_files if img.stem.endswith('_reference')]
    banner_images = [str(img) for img in image_files if img.stem.endswith('_banner')]

    print(f"Found {len(reference_images)} reference images and {len(banner_images)} banner images")
    return reference_images, banner_images

def add_random_images_to_recipe(recipe_data: dict, reference_images: list[str], banner_images: list[str], use_images: bool = True) -> dict:
    """
    Add random image paths to recipe data.

    Args:
        recipe_data: Base recipe data dictionary
        reference_images: List of reference image paths
        banner_images: List of banner image paths
        use_images: Whether to add images to recipes

    Returns:
        dict: Recipe data with image paths added
    """
    if not use_images or (not reference_images and not banner_images):
        return recipe_data

    # Add reference image (60% chance)
    if reference_images and random.random() < 0.6:
        recipe_data['reference_image_path'] = random.choice(reference_images)

    # Add banner image (40% chance)
    if banner_images and random.random() < 0.4:
        recipe_data['banner_image_path'] = random.choice(banner_images)

    return recipe_data


# ── Database Seeding Functions ───────────────────────────────────────────────

def seed_recipes(count: int = 25, realistic: bool = True, use_images: bool = False) -> None:
    """
    Seed the database with mock recipe data.

    Args:
        count: Number of recipes to create
        realistic: Use Faker for realistic data (requires faker package)
        use_images: Whether to add random image paths to recipes
    """
    print(f"Generating {count} mock recipes...")

    # Get available images if needed
    reference_images, banner_images = [], []
    if use_images:
        reference_images, banner_images = get_available_recipe_images()
        if not reference_images and not banner_images:
            print("No images found, proceeding without image paths")
            use_images = False

    # Generate recipe data
    if realistic and FAKER_AVAILABLE:
        recipes_data = [create_realistic_recipe() for _ in range(count)]
    else:
        if realistic and not FAKER_AVAILABLE:
            print("Faker not available, using simple mock data instead")
        recipes_data = [create_simple_recipe(i) for i in range(count)]

    # Add random images to recipes if requested
    if use_images:
        print(f"Adding random image paths to recipes...")
        recipes_data = [
            add_random_images_to_recipe(recipe, reference_images, banner_images, use_images)
            for recipe in recipes_data
        ]

    # Insert into database using bulk insert for efficiency
    with DatabaseSession() as session:
        session.bulk_insert_mappings(Recipe, recipes_data)

    images_msg = " with random image paths" if use_images else ""
    print(f"✅ Successfully inserted {count} mock recipes{images_msg}")

def clear_all_recipes() -> int:
    """
    Clear all recipes from the database.

    Returns:
        Number of recipes deleted
    """
    with DatabaseSession() as session:
        deleted_count = session.query(Recipe).count()
        session.query(Recipe).delete()
        print(f"🗑️  Cleared {deleted_count} existing recipes")
        return deleted_count

def get_recipe_count() -> int:
    """Get current number of recipes in database."""
    with DatabaseSession() as session:
        count = session.query(Recipe).count()
        return count
