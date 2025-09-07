#!/usr/bin/env python3
"""Debug script to trace the 'All' filter flow through the entire system."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.core.services.recipe_service import RecipeService
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator, FilterState

def debug_all_filter_flow():
    """Trace the flow of 'All' filter through the system."""
    print("=== Debug: 'All' Filter Flow ===")
    
    session = SessionLocal()
    try:
        recipe_service = RecipeService(session)
        
        print("\n1. Testing FilterState for 'All' filter...")
        filter_state = FilterState()  # Default state (like "all_recipes" preset)
        print(f"   FilterState category: {filter_state.category}")
        print(f"   FilterState sort_option: {filter_state.sort_option}")
        print(f"   FilterState favorites_only: {filter_state.favorites_only}")
        
        print("\n2. Converting FilterState to DTO...")
        filter_dto = filter_state.to_filter_dto()
        print(f"   DTO recipe_category: {filter_dto.recipe_category}")
        print(f"   DTO sort_by: {filter_dto.sort_by}")
        print(f"   DTO sort_order: {filter_dto.sort_order}")
        print(f"   DTO favorites_only: {filter_dto.favorites_only}")
        print(f"   DTO search_term: {filter_dto.search_term}")
        
        print("\n3. Testing repository query with DTO...")
        recipes = recipe_service.list_filtered(filter_dto)
        print(f"   Recipes returned: {len(recipes)}")
        
        if len(recipes) > 0:
            print(f"   Sample recipe: {recipes[0].recipe_name}")
            print("   ✅ Backend filtering works correctly!")
        else:
            print("   ❌ No recipes returned from backend!")
            
        print("\n4. Testing different category values...")
        
        # Test with None
        test_dto_none = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc"
        )
        recipes_none = recipe_service.list_filtered(test_dto_none)
        print(f"   category=None: {len(recipes_none)} recipes")
        
        # Test with "All" 
        test_dto_all = RecipeFilterDTO(
            recipe_category="All",
            sort_by="recipe_name", 
            sort_order="asc"
        )
        recipes_all = recipe_service.list_filtered(test_dto_all)
        print(f"   category='All': {len(recipes_all)} recipes")
        
        # Test with empty string
        test_dto_empty = RecipeFilterDTO(
            recipe_category="",
            sort_by="recipe_name",
            sort_order="asc"  
        )
        recipes_empty = recipe_service.list_filtered(test_dto_empty)
        print(f"   category='': {len(recipes_empty)} recipes")
        
        print("\n5. Testing FilterState normalization...")
        
        # Test "All" category filter state
        filter_state_all = FilterState(category="All")
        dto_all = filter_state_all.to_filter_dto()
        print(f"   FilterState(category='All') -> DTO category: {dto_all.recipe_category}")
        
        recipes_from_all_state = recipe_service.list_filtered(dto_all)
        print(f"   Recipes from 'All' FilterState: {len(recipes_from_all_state)}")
        
        print("\n6. Summary...")
        print(f"   Default FilterState DTO: {len(recipes)} recipes")
        print(f"   category=None: {len(recipes_none)} recipes") 
        print(f"   category='All': {len(recipes_all)} recipes")
        print(f"   category='': {len(recipes_empty)} recipes")
        print(f"   FilterState('All'): {len(recipes_from_all_state)} recipes")
        
        # All should return the same number of recipes
        all_counts = [len(recipes), len(recipes_none), len(recipes_all), 
                     len(recipes_empty), len(recipes_from_all_state)]
        
        if len(set(all_counts)) == 1:
            print("   ✅ All filter variations return the same count - backend is working!")
        else:
            print("   ❌ Different filter variations return different counts!")
            print(f"   Counts: {all_counts}")

    finally:
        session.close()

if __name__ == "__main__":
    debug_all_filter_flow()