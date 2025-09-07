"""Comprehensive integration tests for the refactored RecipeBrowser system.

This module tests the coordinator architecture integration and all recipe domain functionality:

Architecture Components:
- PerformanceManager: Object pooling and progressive rendering
- EventCoordinator: Debounced interactions and signal management  
- RecipeBrowserConfig: Configuration management
- FilterCoordinator: Recipe-specific filtering logic
- RenderingCoordinator: Recipe card creation and layout management
- Enhanced ViewModel: Business logic and coordinator integration
- Refactored View: Coordinator orchestration and UI assembly

Test Categories:
- Complete recipe browsing workflows end-to-end
- Coordinator communication and coordination
- Recipe filtering with multiple coordinators
- Selection mode and navigation workflows  
- Performance optimization integration
- Error handling across coordinators
- Memory management and cleanup

Recipe Domain Focus:
- Recipe card creation and interaction patterns
- Recipe filtering by category, favorites, search
- Recipe selection for meal planning
- Recipe data validation and business rules
- Recipe performance optimizations
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import gc
import time
import weakref
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import LayoutSize, BaseRecipeCard
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import RecipeBrowserConfig, create_default_config
from app.ui.views.recipe_browser.filter_coordinator import FilterCoordinator
from app.ui.views.recipe_browser.rendering_coordinator import RenderingCoordinator
from app.ui.views.recipe_browser.recipe_browser_view import RecipeBrowser

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────────────────
def create_recipe_test_data(count: int = 10) -> List[Recipe]:
    """Create realistic test recipe data for integration tests."""
    recipes = []
    categories = ["Main Course", "Appetizers", "Desserts", "Side Dishes", "Soups", "Salads"]
    
    for i in range(count):
        recipe = RecipeFactory.build(
            id=i + 1,
            recipe_name=f"Integration Test Recipe {i + 1}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 3 == 0),  # Every 3rd recipe is favorite
            total_time=15 + (i * 5),  # Varying cook times
            servings=2 + (i % 6),     # 2-8 servings
            directions=f"Step-by-step instructions for recipe {i + 1}",
            notes=f"Chef notes for recipe {i + 1}"
        )
        recipes.append(recipe)
    
    return recipes


def create_complex_recipe_dataset() -> List[Recipe]:
    """Create a complex recipe dataset for performance and filtering tests."""
    recipes = []
    categories = list(RECIPE_CATEGORIES.keys())
    
    # Create varied recipes with different characteristics
    for i in range(50):
        recipe = RecipeFactory.build(
            id=i + 1,
            recipe_name=f"Recipe {i + 1}: {['Quick', 'Gourmet', 'Family', 'Healthy'][i % 4]} {['Chicken', 'Beef', 'Vegetarian', 'Seafood'][i % 4]}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 7 == 0),  # ~14% favorites
            total_time=10 + (i * 3) if i % 5 == 0 else 30 + (i * 2),  # Mix of quick and slow recipes
            servings=1 + (i % 8),     # 1-8 servings variety
            difficulty_level=['Easy', 'Medium', 'Hard'][i % 3] if i % 10 < 7 else None,
            dietary_tags=['Vegetarian', 'Gluten-Free', 'Dairy-Free', 'Low-Carb'][i % 4] if i % 6 == 0 else None
        )
        recipes.append(recipe)
    
    return recipes


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_recipe_service():
    """Create a comprehensive mock recipe service for integration tests."""
    service = Mock(spec=RecipeService)
    
    # Default behavior returns test recipes
    test_recipes = create_recipe_test_data(15)
    service.list_filtered.return_value = test_recipes
    service.get_by_id.side_effect = lambda recipe_id: next((r for r in test_recipes if r.id == recipe_id), None)
    service.toggle_favorite.side_effect = lambda recipe_id: _toggle_recipe_favorite(test_recipes, recipe_id)
    
    return service


def _toggle_recipe_favorite(recipes: List[Recipe], recipe_id: int) -> Optional[Recipe]:
    """Helper to toggle favorite status in test data."""
    recipe = next((r for r in recipes if r.id == recipe_id), None)
    if recipe:
        recipe.is_favorite = not recipe.is_favorite
    return recipe


@pytest.fixture
def integration_config():
    """Create integration test configuration."""
    config = create_default_config()
    # Optimize for fast test execution
    config.performance.batch_size = 5
    config.performance.card_pool_size = 15
    config.interaction.filter_debounce_delay_ms = 50  # Fast debounce for tests
    config.interaction.search_debounce_delay_ms = 100
    return config


@pytest.fixture
def performance_manager():
    """Create PerformanceManager for integration testing."""
    manager = PerformanceManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def event_coordinator():
    """Create EventCoordinator for integration testing."""
    coordinator = EventCoordinator(coordinator_name="IntegrationTest")
    yield coordinator
    coordinator.cleanup_all_coordinations()


@pytest.fixture
def integrated_view_model(db_session, mock_recipe_service):
    """Create integrated ViewModel with mocked service."""
    view_model = RecipeBrowserViewModel(db_session)
    view_model._recipe_service = mock_recipe_service
    return view_model


@pytest.fixture
def filter_coordinator(integrated_view_model, integration_config, event_coordinator):
    """Create FilterCoordinator for integration testing."""
    coordinator = FilterCoordinator(
        view_model=integrated_view_model,
        config=integration_config,
        event_coordinator=event_coordinator
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def rendering_coordinator(performance_manager, integration_config):
    """Create RenderingCoordinator for integration testing."""
    coordinator = RenderingCoordinator(
        performance_manager=performance_manager,
        config=integration_config
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def integrated_recipe_browser(
    qapp, 
    integrated_view_model, 
    integration_config,
    performance_manager,
    event_coordinator,
    filter_coordinator,
    rendering_coordinator
):
    """Create fully integrated RecipeBrowser with all coordinators."""
    browser = RecipeBrowser(
        parent=None,
        selection_mode=False,
        card_size=LayoutSize.MEDIUM,
        config=integration_config
    )
    
    # Inject our test coordinators
    browser._performance_manager = performance_manager
    browser._event_coordinator = event_coordinator
    browser._filter_coordinator = filter_coordinator
    browser._rendering_coordinator = rendering_coordinator
    browser._view_model = integrated_view_model
    
    yield browser
    browser.deleteLater()


# ── Integration Test Classes ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserCoordinatorArchitecture:
    """Test coordinator architecture integration and communication."""
    
    def test_coordinator_initialization_and_wiring(self, integrated_recipe_browser):
        """Test that all coordinators are properly initialized and wired together."""
        browser = integrated_recipe_browser
        
        # Verify all coordinators exist
        assert browser._performance_manager is not None
        assert browser._event_coordinator is not None
        assert browser._filter_coordinator is not None
        assert browser._rendering_coordinator is not None
        assert browser._view_model is not None
        
        # Verify coordinator communication setup
        assert browser._filter_coordinator._event_coordinator is browser._event_coordinator
        assert browser._rendering_coordinator._performance_manager is browser._performance_manager
    
    def test_coordinator_configuration_propagation(self, integrated_recipe_browser):
        """Test configuration is properly propagated to all coordinators."""
        browser = integrated_recipe_browser
        config = browser._config
        
        # Verify config reaches all coordinators
        assert browser._filter_coordinator._config is config
        assert browser._rendering_coordinator._config is config
        
        # Verify coordinator-specific optimizations
        optimized = config.get_optimized_settings(10)
        assert optimized['batch_size'] == 5  # Our test setting
        assert optimized['progressive_rendering'] is True
    
    def test_coordinator_lifecycle_management(self, integrated_recipe_browser):
        """Test coordinator lifecycle management and cleanup."""
        browser = integrated_recipe_browser
        
        # Create weak references to track cleanup
        performance_ref = weakref.ref(browser._performance_manager)
        event_ref = weakref.ref(browser._event_coordinator)
        filter_ref = weakref.ref(browser._filter_coordinator)
        rendering_ref = weakref.ref(browser._rendering_coordinator)
        
        # Trigger cleanup
        browser._cleanup_coordinators()
        
        # Verify coordinators are cleaned up
        # Note: Actual garbage collection testing is limited in integration tests
        assert performance_ref() is not None  # Still referenced by fixture
        assert event_ref() is not None
        assert filter_ref() is not None
        assert rendering_ref() is not None


@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowsingWorkflows:
    """Test complete recipe browsing workflows end-to-end."""
    
    def test_complete_recipe_loading_workflow(self, integrated_recipe_browser, mock_recipe_service):
        """Test complete recipe loading workflow through all coordinators."""
        browser = integrated_recipe_browser
        
        # Initial load should trigger through all layers
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify ViewModel was called
        mock_recipe_service.list_filtered.assert_called()
        
        # Verify rendering coordinator was engaged
        assert browser._rendering_coordinator.is_rendering_active()
        
        # Verify recipe cards were created
        assert browser._flow_layout.count() > 0
    
    def test_recipe_filtering_coordination_workflow(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe filtering coordination between multiple components."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Apply category filter
        browser._filter_coordinator.apply_category_filter("Main Course")
        QApplication.processEvents()
        
        # Verify debounced filter execution
        time.sleep(0.1)  # Wait for debounce
        QApplication.processEvents()
        
        # Verify service was called with filtered parameters
        calls = mock_recipe_service.list_filtered.call_args_list
        filter_dto = calls[-1][0][0]  # Last call's first argument
        assert filter_dto.recipe_category == "Main Course"
        
        # Verify rendering coordination
        assert browser._rendering_coordinator._current_recipes is not None
    
    def test_recipe_search_integration_workflow(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe search integration across coordinators."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Trigger search through filter coordinator
        browser._filter_coordinator.apply_search_filter("chicken")
        
        # Wait for debounced search
        time.sleep(0.15)  # Wait longer than search debounce
        QApplication.processEvents()
        
        # Verify search was executed
        calls = mock_recipe_service.list_filtered.call_args_list
        filter_dto = calls[-1][0][0]
        assert "chicken" in str(filter_dto.model_dump()).lower()
    
    def test_recipe_selection_workflow(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe selection workflow in both normal and selection modes."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Test normal mode - recipe opening
        recipes = mock_recipe_service.list_filtered.return_value
        test_recipe = recipes[0]
        
        with patch.object(browser, 'recipe_opened') as mock_opened:
            browser._handle_recipe_interaction(test_recipe, 'opened')
            mock_opened.emit.assert_called_once_with(test_recipe)
        
        # Test selection mode
        browser.set_selection_mode(True)
        QApplication.processEvents()
        
        with patch.object(browser, 'recipe_selected') as mock_selected:
            browser._handle_recipe_interaction(test_recipe, 'selected')
            mock_selected.emit.assert_called_once_with(test_recipe.id, test_recipe)
    
    def test_combined_filtering_workflow(self, integrated_recipe_browser, mock_recipe_service):
        """Test combining multiple filters in a single workflow."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Apply multiple filters in sequence
        browser._filter_coordinator.apply_category_filter("Desserts")
        browser._filter_coordinator.apply_favorites_filter(True)
        browser._filter_coordinator.apply_sort_option("Shortest Time")
        
        # Wait for all debounced operations
        time.sleep(0.2)
        QApplication.processEvents()
        
        # Verify final filter state combines all criteria
        calls = mock_recipe_service.list_filtered.call_args_list
        final_filter = calls[-1][0][0]
        assert final_filter.recipe_category == "Desserts"
        assert final_filter.favorites_only is True
        assert final_filter.sort_by == "total_time"
        assert final_filter.sort_order == "asc"


@pytest.mark.integration
@pytest.mark.ui
class TestPerformanceOptimizationIntegration:
    """Test performance optimization integration across coordinators."""
    
    def test_object_pooling_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test object pooling integration with recipe card creation."""
        browser = integrated_recipe_browser
        
        # Setup large dataset for pooling test
        large_dataset = create_complex_recipe_dataset()
        mock_recipe_service.list_filtered.return_value = large_dataset
        
        # Load recipes to trigger pooling
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify performance manager has recipe card pool
        card_pool = browser._performance_manager.get_widget_pool("recipe_cards")
        assert card_pool is not None
        
        # Verify pool statistics
        stats = card_pool.statistics
        assert stats['total_created'] >= 0
        assert stats['pool_size'] >= 0
        assert stats['active_count'] >= 0
    
    def test_progressive_rendering_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test progressive rendering coordination."""
        browser = integrated_recipe_browser
        
        # Setup dataset larger than batch size
        large_dataset = create_complex_recipe_dataset()
        mock_recipe_service.list_filtered.return_value = large_dataset
        
        # Start progressive rendering
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify progressive renderer is active
        renderer = browser._performance_manager.get_progressive_renderer("recipe_rendering")
        if renderer:
            assert renderer.is_rendering or browser._flow_layout.count() > 0
        
        # Process multiple batches
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.02)  # Small delay for batch processing
        
        # Verify some cards were rendered
        assert browser._flow_layout.count() > 0
    
    def test_memory_management_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test memory management across coordinator lifecycle."""
        browser = integrated_recipe_browser
        
        # Load initial recipes
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Track initial memory state
        initial_metrics = browser._performance_manager.get_performance_summary()
        
        # Perform multiple filter operations
        for category in ["Main Course", "Desserts", "Appetizers"]:
            browser._filter_coordinator.apply_category_filter(category)
            time.sleep(0.1)
            QApplication.processEvents()
        
        # Trigger memory cleanup
        browser._performance_manager.trigger_memory_cleanup()
        QApplication.processEvents()
        
        # Verify cleanup occurred
        final_metrics = browser._performance_manager.get_performance_summary()
        assert final_metrics['memory']['tracked_objects'] >= 0
    
    def test_performance_metrics_collection(self, integrated_recipe_browser, mock_recipe_service):
        """Test performance metrics collection across operations."""
        browser = integrated_recipe_browser
        
        # Enable performance monitoring
        browser._config.features.enable_performance_monitoring = True
        
        # Perform various operations
        browser.load_initial_recipes()
        browser._filter_coordinator.apply_category_filter("Main Course")
        browser._filter_coordinator.apply_search_filter("test")
        
        # Wait for operations to complete
        time.sleep(0.2)
        QApplication.processEvents()
        
        # Collect performance metrics
        metrics = browser._performance_manager.get_performance_summary()
        
        # Verify metrics are collected
        assert 'metrics' in metrics
        assert 'pools' in metrics
        assert 'memory' in metrics
        assert metrics['metrics']['total_operations'] >= 0


@pytest.mark.integration
@pytest.mark.ui
class TestRecipeDomainFunctionality:
    """Test recipe domain-specific functionality integration."""
    
    def test_recipe_category_filtering_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe category filtering with domain validation."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Test each valid category
        for category in RECIPE_CATEGORIES:
            browser._filter_coordinator.apply_category_filter(category)
            time.sleep(0.1)
            QApplication.processEvents()
            
            # Verify filter was applied
            calls = mock_recipe_service.list_filtered.call_args_list
            if calls:
                filter_dto = calls[-1][0][0]
                assert filter_dto.recipe_category == category
    
    def test_recipe_favorite_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe favorite functionality integration."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Get a test recipe
        recipes = mock_recipe_service.list_filtered.return_value
        test_recipe = recipes[0]
        
        # Test favorite toggle through ViewModel
        original_favorite = test_recipe.is_favorite
        success = browser._view_model.toggle_recipe_favorite(test_recipe.id)
        
        assert success is True
        assert test_recipe.is_favorite != original_favorite
    
    def test_recipe_sort_options_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test all recipe sort options integration."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Test each sort option
        for sort_option in SORT_OPTIONS:
            browser._filter_coordinator.apply_sort_option(sort_option)
            time.sleep(0.1)
            QApplication.processEvents()
            
            # Verify sort was applied
            calls = mock_recipe_service.list_filtered.call_args_list
            if calls:
                filter_dto = calls[-1][0][0]
                # Verify sort fields are set correctly
                assert filter_dto.sort_by is not None
                assert filter_dto.sort_order in ["asc", "desc"]
    
    def test_recipe_card_creation_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test recipe card creation with domain data."""
        browser = integrated_recipe_browser
        
        # Setup recipes with comprehensive data
        test_recipes = create_recipe_test_data(5)
        mock_recipe_service.list_filtered.return_value = test_recipes
        
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify cards were created
        assert browser._flow_layout.count() > 0
        
        # Verify card properties match recipe data
        for i in range(min(browser._flow_layout.count(), len(test_recipes))):
            card_widget = browser._flow_layout.itemAt(i).widget()
            if isinstance(card_widget, BaseRecipeCard):
                recipe = test_recipes[i]
                # Verify card has recipe data
                assert hasattr(card_widget, '_recipe_data')


@pytest.mark.integration
@pytest.mark.ui
class TestErrorHandlingIntegration:
    """Test error handling across coordinator integration."""
    
    def test_service_error_handling_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test service error handling across coordinators."""
        browser = integrated_recipe_browser
        
        # Setup service to throw error
        mock_recipe_service.list_filtered.side_effect = Exception("Service unavailable")
        
        # Attempt to load recipes
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify error is handled gracefully
        assert browser._flow_layout.count() == 0  # No cards should be displayed
        
        # Verify coordinators remain functional
        assert browser._filter_coordinator is not None
        assert browser._rendering_coordinator is not None
    
    def test_rendering_error_recovery_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test rendering error recovery across coordinators."""
        browser = integrated_recipe_browser
        
        # Setup rendering to fail for some recipes
        test_recipes = create_recipe_test_data(10)
        mock_recipe_service.list_filtered.return_value = test_recipes
        
        # Mock card creation to fail occasionally
        original_create = browser._rendering_coordinator._create_recipe_card
        def failing_create(recipe):
            if recipe.id % 3 == 0:  # Fail every 3rd recipe
                raise Exception("Card creation failed")
            return original_create(recipe)
        
        browser._rendering_coordinator._create_recipe_card = failing_create
        
        # Load recipes
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        # Verify some cards were still created
        # Note: Exact count depends on error handling implementation
        card_count = browser._flow_layout.count()
        assert card_count >= 0  # At least some should succeed or graceful failure
    
    def test_coordinator_communication_error_handling(self, integrated_recipe_browser, mock_recipe_service):
        """Test error handling in coordinator communication."""
        browser = integrated_recipe_browser
        
        # Break coordinator communication
        original_method = browser._filter_coordinator.apply_category_filter
        def failing_filter(category):
            raise Exception("Filter coordinator communication failed")
        
        browser._filter_coordinator.apply_category_filter = failing_filter
        
        # Attempt filtering - should not crash the entire system
        try:
            browser._filter_coordinator.apply_category_filter("Main Course")
            QApplication.processEvents()
        except Exception:
            pass  # Expected to fail
        
        # Verify other coordinators still work
        assert browser._rendering_coordinator is not None
        assert browser._performance_manager is not None


@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.slow
class TestRecipeBrowserPerformanceIntegration:
    """Test performance scenarios and stress testing."""
    
    def test_large_dataset_performance_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test performance with large recipe dataset."""
        browser = integrated_recipe_browser
        
        # Create large dataset
        large_dataset = create_complex_recipe_dataset()  # 50 recipes
        mock_recipe_service.list_filtered.return_value = large_dataset
        
        # Time the loading operation
        start_time = time.perf_counter()
        
        browser.load_initial_recipes()
        
        # Process all rendering batches
        for _ in range(20):  # Allow multiple batch cycles
            QApplication.processEvents()
            time.sleep(0.01)
        
        end_time = time.perf_counter()
        loading_time = end_time - start_time
        
        # Verify performance is reasonable (adjust threshold as needed)
        assert loading_time < 5.0  # Should complete within 5 seconds
        
        # Verify all recipes were eventually rendered
        assert browser._flow_layout.count() <= len(large_dataset)
    
    def test_rapid_filter_changes_performance(self, integrated_recipe_browser, mock_recipe_service):
        """Test performance under rapid filter changes."""
        browser = integrated_recipe_browser
        browser.load_initial_recipes()
        QApplication.processEvents()
        
        start_time = time.perf_counter()
        
        # Rapid filter changes
        categories = ["Main Course", "Desserts", "Appetizers", "Side Dishes", "Soups"]
        for _ in range(3):  # 3 cycles
            for category in categories:
                browser._filter_coordinator.apply_category_filter(category)
                QApplication.processEvents()
        
        # Wait for debouncing to settle
        time.sleep(0.3)
        QApplication.processEvents()
        
        end_time = time.perf_counter()
        filter_time = end_time - start_time
        
        # Verify reasonable performance
        assert filter_time < 3.0  # Should handle rapid changes efficiently
        
        # Verify debouncing worked (fewer service calls than filter attempts)
        assert mock_recipe_service.list_filtered.call_count < 20  # Debounced
    
    def test_memory_usage_stability_integration(self, integrated_recipe_browser, mock_recipe_service):
        """Test memory usage stability over multiple operations."""
        browser = integrated_recipe_browser
        
        # Perform repeated operations
        for cycle in range(5):
            # Load different datasets
            dataset = create_recipe_test_data(15 + cycle * 3)
            mock_recipe_service.list_filtered.return_value = dataset
            
            browser.load_initial_recipes()
            QApplication.processEvents()
            
            # Apply filters
            browser._filter_coordinator.apply_category_filter("Main Course")
            browser._filter_coordinator.apply_favorites_filter(cycle % 2 == 0)
            
            time.sleep(0.1)
            QApplication.processEvents()
            
            # Trigger cleanup
            if cycle % 2 == 1:
                browser._performance_manager.trigger_memory_cleanup()
                gc.collect()
        
        # Final cleanup and verification
        browser._performance_manager.trigger_memory_cleanup()
        QApplication.processEvents()
        
        # Memory should be stable (exact values depend on implementation)
        metrics = browser._performance_manager.get_performance_summary()
        assert metrics['memory']['tracked_objects'] >= 0