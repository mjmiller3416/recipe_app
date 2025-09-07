#!/usr/bin/env python3
"""Debug script to test the 'All' filter issue in RecipeBrowser."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.core.services.recipe_service import RecipeService
from app.core.dtos.recipe_dtos import RecipeFilterDTO

def test_all_filter():
    """Test the 'All' filter functionality."""
    print("=== Debug: Testing 'All' Filter ===")
    
    # Initialize database
    session = SessionLocal()
    try:
        # Initialize service
        recipe_service = RecipeService(session)
        
        # Test 1: Get total recipe count
        print(f"Testing total recipe count...")
        all_filter = RecipeFilterDTO()  # Empty filter should get all recipes
        all_recipes = recipe_service.list_filtered(all_filter)
        print(f"Total recipes in database: {len(all_recipes)}")
        
        if len(all_recipes) == 0:
            print("❌ No recipes in database - this could be the issue!")
            return
        
        # Test 2: Test 'All' filter (category=None)
        print(f"\nTesting 'All' filter (category=None)...")
        all_filter = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc"
        )
        
        filtered_recipes = recipe_service.list_filtered(all_filter)
        print(f"Recipes with 'All' filter: {len(filtered_recipes)}")
        
        if len(filtered_recipes) != len(all_recipes):
            print(f"❌ Mismatch! Expected {len(all_recipes)}, got {len(filtered_recipes)}")
        else:
            print(f"✅ 'All' filter working correctly!")
        
        # Test 3: Test specific category filter
        if all_recipes:
            test_category = all_recipes[0].recipe_category
            print(f"\nTesting specific category filter: '{test_category}'...")
            
            category_filter = RecipeFilterDTO(
                recipe_category=test_category,
                sort_by="recipe_name", 
                sort_order="asc"
            )
            
            category_recipes = recipe_service.list_filtered(category_filter)
            print(f"Recipes with category '{test_category}': {len(category_recipes)}")
        
        # Test 4: Check if FilterState conversion works
        print(f"\nTesting FilterState to DTO conversion...")
        from app.ui.views.recipe_browser.filter_coordinator import FilterState
        
        filter_state = FilterState()  # Default state (like "all_recipes" preset)
        dto = filter_state.to_filter_dto()
        
        print(f"FilterState default category: {filter_state.category}")
        print(f"DTO converted category: {dto.recipe_category}")
        
        dto_filtered_recipes = recipe_service.list_filtered(dto)
        print(f"Recipes with FilterState DTO: {len(dto_filtered_recipes)}")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Total recipes: {len(all_recipes)}")
        print(f"'All' filter recipes: {len(filtered_recipes)}")
        print(f"FilterState DTO recipes: {len(dto_filtered_recipes)}")
        
        if len(all_recipes) == len(filtered_recipes) == len(dto_filtered_recipes):
            print("✅ All filters working correctly - issue might be in UI layer")
        else:
            print("❌ Filter logic issue detected!")
    
    finally:
        session.close()

if __name__ == "__main__":
    test_all_filter()