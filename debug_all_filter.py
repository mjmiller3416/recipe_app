#!/usr/bin/env python3
"""
Debug script to test the "All" filter issue in RecipeBrowser.
This will help isolate where the problem occurs in the filter chain.
"""

import sys
sys.path.append('.')

from app.core.database.db import create_session
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from _dev_tools import DebugLogger

def test_all_filter_chain():
    """Test the complete All filter chain step by step."""
    
    print("=== Testing 'All' Filter Chain ===\n")
    
    # 1. Test database level
    print("1. Testing database level...")
    session = create_session()
    service = RecipeService(session)
    
    filter_dto = RecipeFilterDTO(
        recipe_category=None,  # This is what "All" normalizes to
        sort_by='recipe_name',
        sort_order='asc',
        favorites_only=False,
        search_term=None
    )
    
    recipes = service.list_filtered(filter_dto)
    print(f"   Database returned {len(recipes)} recipes")
    if recipes:
        print(f"   First recipe: {recipes[0].recipe_name} (category: {recipes[0].recipe_category})")
    
    # 2. Test ViewModel level
    print("\n2. Testing ViewModel level...")
    view_model = RecipeBrowserViewModel(service)
    
    # Mock the signal emission to track what gets emitted
    loaded_recipes = []
    def capture_loaded_recipes(recipes_list):
        loaded_recipes.extend(recipes_list)
        print(f"   ViewModel emitted {len(recipes_list)} recipes")
    
    view_model.recipes_loaded.connect(capture_loaded_recipes)
    
    # Test load_filtered_sorted_recipes
    success = view_model.load_filtered_sorted_recipes(filter_dto)
    print(f"   load_filtered_sorted_recipes returned: {success}")
    print(f"   Total recipes emitted: {len(loaded_recipes)}")
    
    # 3. Test FilterCoordinator normalization
    print("\n3. Testing FilterCoordinator normalization...")
    from app.ui.views.recipe_browser.filter_coordinator import FilterState
    
    # Test "All" category normalization
    state_all = FilterState(category="All", sort_option="A-Z", favorites_only=False, search_term=None)
    dto_all = state_all.to_filter_dto()
    print(f"   'All' normalizes to recipe_category: {dto_all.recipe_category}")
    
    # Test other category for comparison
    state_chicken = FilterState(category="Chicken", sort_option="A-Z", favorites_only=False, search_term=None)
    dto_chicken = state_chicken.to_filter_dto()
    print(f"   'Chicken' normalizes to recipe_category: {dto_chicken.recipe_category}")
    
    # 4. Test with the actual normalized DTO
    print("\n4. Testing with normalized 'All' DTO...")
    loaded_recipes.clear()
    success_all = view_model.load_filtered_sorted_recipes(dto_all)
    print(f"   Normalized 'All' filter returned: {success_all}")
    print(f"   Recipes emitted with normalized DTO: {len(loaded_recipes)}")
    
    session.close()
    
    print("\n=== Summary ===")
    print(f"Database level: {len(recipes)} recipes")
    print(f"ViewModel level: Success={success}, Emitted={len(loaded_recipes)}")
    print(f"All filter works correctly: {len(recipes) > 0 and success and len(loaded_recipes) > 0}")
    
    return len(recipes), success, len(loaded_recipes)

if __name__ == "__main__":
    test_all_filter_chain()