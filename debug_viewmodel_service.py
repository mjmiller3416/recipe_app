#!/usr/bin/env python3
"""
Debug script to test RecipeService creation through ViewModel.
This will help isolate the issue with 'scalars' attribute error.
"""

import sys
sys.path.append('.')

from app.core.database.db import create_session
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from _dev_tools import DebugLogger

def test_service_creation():
    """Test RecipeService creation through different paths."""
    
    print("=== Testing RecipeService Creation Paths ===\n")
    
    # 1. Test direct service creation (known to work)
    print("1. Testing direct RecipeService creation...")
    session1 = create_session()
    service1 = RecipeService(session1)
    print(f"   Direct service type: {type(service1)}")
    print(f"   Direct service has scalars: {hasattr(service1, 'scalars')}")
    print(f"   Direct session has scalars: {hasattr(session1, 'scalars')}")
    
    # 2. Test ViewModel with session injection
    print("\n2. Testing ViewModel with session injection...")
    session2 = create_session()
    view_model1 = RecipeBrowserViewModel(session2)
    
    # Force service creation by calling _ensure_recipe_service
    success1 = view_model1._ensure_recipe_service()
    print(f"   Service creation success: {success1}")
    
    if view_model1._recipe_service:
        print(f"   ViewModel service type: {type(view_model1._recipe_service)}")
        print(f"   ViewModel service has scalars: {hasattr(view_model1._recipe_service, 'scalars')}")
        print(f"   ViewModel session has scalars: {hasattr(view_model1._session, 'scalars')}")
        
        # Test the service method
        filter_dto = RecipeFilterDTO(recipe_category=None, sort_by='recipe_name', sort_order='asc', favorites_only=False, search_term=None)
        try:
            recipes1 = view_model1._recipe_service.list_filtered(filter_dto)
            print(f"   ViewModel service.list_filtered works: {len(recipes1)} recipes")
        except Exception as e:
            print(f"   ViewModel service.list_filtered failed: {e}")
    
    # 3. Test ViewModel without session injection (auto-creation)
    print("\n3. Testing ViewModel without session injection...")
    view_model2 = RecipeBrowserViewModel(None)
    
    success2 = view_model2._ensure_recipe_service()
    print(f"   Service creation success: {success2}")
    
    if view_model2._recipe_service:
        print(f"   Auto service type: {type(view_model2._recipe_service)}")
        print(f"   Auto service has scalars: {hasattr(view_model2._recipe_service, 'scalars')}")
        print(f"   Auto session has scalars: {hasattr(view_model2._session, 'scalars')}")
        
        # Test the service method
        try:
            recipes2 = view_model2._recipe_service.list_filtered(filter_dto)
            print(f"   Auto service.list_filtered works: {len(recipes2)} recipes")
        except Exception as e:
            print(f"   Auto service.list_filtered failed: {e}")
    
    # 4. Test the actual load method that's failing
    print("\n4. Testing load_filtered_sorted_recipes method...")
    
    for i, vm in enumerate([view_model1, view_model2], 1):
        try:
            success = vm.load_filtered_sorted_recipes(filter_dto)
            print(f"   ViewModel {i} load_filtered_sorted_recipes: {success}")
        except Exception as e:
            print(f"   ViewModel {i} load_filtered_sorted_recipes failed: {e}")
    
    # Cleanup
    session1.close()
    session2.close()

if __name__ == "__main__":
    test_service_creation()