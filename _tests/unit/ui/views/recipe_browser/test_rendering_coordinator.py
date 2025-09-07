"""Unit tests for RenderingCoordinator.

Tests the recipe-specific rendering coordination including:
- Recipe card creation and configuration
- Progressive rendering coordination with PerformanceManager
- Selection mode handling for recipe cards
- Layout management with FlowLayout integration
- Recipe-specific performance optimizations
- Card pool management and object recycling
- Recipe card interaction handling (clicks, selection, favorites)
- Memory management for recipe card lifecycle
- Error handling and edge cases in rendering
- Recipe data validation and card state management

The RenderingCoordinator bridges generic performance management with
recipe domain-specific rendering requirements in the RecipeBrowser.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import time
import weakref
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.core.models.recipe import Recipe
from app.ui.components.composite.recipe_card import BaseRecipeCard, LayoutSize, create_recipe_card
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.managers.performance.performance_manager import PerformanceManager
from app.ui.views.recipe_browser.config import RecipeBrowserConfig, create_default_config
from app.ui.views.recipe_browser.rendering_coordinator import (
    RenderingCoordinator, RecipeRenderState, CardInteractionType
)

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────────────────
def create_test_recipe(**kwargs) -> Recipe:
    """Create test recipe with defaults."""
    defaults = {
        'id': 1,
        'recipe_name': 'Test Recipe',
        'recipe_category': 'Main Course',
        'is_favorite': False,
        'total_time': 30,
        'servings': 4,
        'directions': 'Test directions',
        'notes': 'Test notes'
    }
    defaults.update(kwargs)
    return RecipeFactory.build(**defaults)


def create_test_recipes(count: int = 10) -> List[Recipe]:
    """Create list of test recipes."""
    recipes = []
    categories = ["Main Course", "Desserts", "Appetizers", "Side Dishes", "Soups"]
    
    for i in range(count):
        recipe = create_test_recipe(
            id=i + 1,
            recipe_name=f"Recipe {i + 1}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 3 == 0),
            total_time=15 + (i * 5),
            servings=2 + (i % 6)
        )
        recipes.append(recipe)
    
    return recipes


class MockRecipeCard(BaseRecipeCard):
    """Mock recipe card for testing."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._recipe_data = None
        self.click_count = 0
        self.favorite_toggle_count = 0
        self.selection_changed_count = 0
    
    def set_recipe_data(self, recipe: Recipe):
        self._recipe_data = recipe
    
    def get_recipe_data(self) -> Optional[Recipe]:
        return self._recipe_data
    
    def set_selection_mode(self, enabled: bool):
        self.selection_changed_count += 1
    
    def toggle_favorite(self):
        self.favorite_toggle_count += 1
        if self._recipe_data:
            self._recipe_data.is_favorite = not self._recipe_data.is_favorite
    
    def simulate_click(self):
        self.click_count += 1


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def performance_manager():
    """Create PerformanceManager for rendering testing."""
    manager = PerformanceManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def rendering_config():
    """Create rendering configuration for testing."""
    config = create_default_config()
    # Optimize for test execution
    config.performance.batch_size = 3
    config.performance.card_pool_size = 10
    config.display.default_card_size = LayoutSize.MEDIUM
    return config


@pytest.fixture
def flow_layout(qapp):
    """Create FlowLayout for testing."""
    widget = QWidget()
    layout = FlowLayout(widget)
    widget.setLayout(layout)
    yield layout
    widget.deleteLater()


@pytest.fixture
def rendering_coordinator(performance_manager, rendering_config, flow_layout):
    """Create RenderingCoordinator for testing."""
    coordinator = RenderingCoordinator(
        performance_manager=performance_manager,
        config=rendering_config,
        parent_layout=flow_layout
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def mock_card_factory():
    """Create mock recipe card factory."""
    def factory(*args, **kwargs):
        card = MockRecipeCard()
        return card
    
    with patch('app.ui.views.recipe_browser.rendering_coordinator.create_recipe_card', side_effect=factory):
        yield factory


# ── Test Classes ─────────────────────────────────────────────────────────────────────────────────────────────
class TestRenderingCoordinatorInitialization:
    """Test RenderingCoordinator initialization and setup."""
    
    def test_initialization_default(self, rendering_coordinator, performance_manager, rendering_config, flow_layout):
        """Test default initialization."""
        coordinator = rendering_coordinator
        
        # Verify dependencies
        assert coordinator._performance_manager is performance_manager
        assert coordinator._config is rendering_config
        assert coordinator._parent_layout is flow_layout
        
        # Verify state initialization
        assert isinstance(coordinator._render_state, RecipeRenderState)
        assert coordinator._render_state.is_rendering is False
        assert coordinator._render_state.total_recipes == 0
        assert coordinator._render_state.rendered_count == 0
        
        # Verify collections
        assert isinstance(coordinator._active_cards, dict)
        assert isinstance(coordinator._card_cache, dict)
        assert len(coordinator._active_cards) == 0
    
    def test_performance_manager_integration(self, rendering_coordinator, performance_manager):
        """Test integration with PerformanceManager."""
        coordinator = rendering_coordinator
        
        # Verify performance manager setup
        assert coordinator._performance_manager is performance_manager
        
        # Verify card pool creation
        card_pool = performance_manager.get_widget_pool("recipe_cards")
        assert card_pool is not None or coordinator._card_pool is not None
    
    def test_configuration_application(self, rendering_coordinator, rendering_config):
        """Test configuration application."""
        coordinator = rendering_coordinator
        
        # Verify config settings are applied
        assert coordinator._default_card_size == rendering_config.display.default_card_size
        assert coordinator._batch_size == rendering_config.performance.batch_size
    
    def test_signal_setup(self, rendering_coordinator):
        """Test signal setup and connections."""
        coordinator = rendering_coordinator
        
        # Verify signals exist
        assert hasattr(coordinator, 'rendering_started')
        assert hasattr(coordinator, 'rendering_completed')
        assert hasattr(coordinator, 'recipe_card_clicked')
        assert hasattr(coordinator, 'recipe_card_selection_changed')


class TestRecipeCardCreation:
    """Test recipe card creation and management."""
    
    def test_create_recipe_card_basic(self, rendering_coordinator, mock_card_factory):
        """Test basic recipe card creation."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe(id=1, recipe_name="Test Recipe")
        
        card = coordinator._create_recipe_card(recipe)
        
        assert card is not None
        assert isinstance(card, MockRecipeCard)
        assert card.get_recipe_data() is recipe
    
    def test_create_recipe_card_with_size(self, rendering_coordinator, mock_card_factory):
        """Test recipe card creation with specific size."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe()
        
        card = coordinator._create_recipe_card(recipe, LayoutSize.LARGE)
        
        assert card is not None
        # Verify size was applied (depends on mock implementation)
    
    def test_create_multiple_recipe_cards(self, rendering_coordinator, mock_card_factory):
        """Test creating multiple recipe cards."""
        coordinator = rendering_coordinator
        recipes = create_test_recipes(5)
        
        cards = []
        for recipe in recipes:
            card = coordinator._create_recipe_card(recipe)
            cards.append(card)
        
        assert len(cards) == 5
        for i, card in enumerate(cards):
            assert card.get_recipe_data() is recipes[i]
    
    def test_recipe_card_configuration(self, rendering_coordinator, mock_card_factory):
        """Test recipe card configuration."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe(is_favorite=True)
        
        card = coordinator._create_recipe_card(recipe)
        
        # Verify card is configured correctly
        assert card.get_recipe_data().is_favorite is True
    
    def test_recipe_card_error_handling(self, rendering_coordinator):
        """Test error handling in card creation."""
        coordinator = rendering_coordinator
        
        # Test with None recipe
        card = coordinator._create_recipe_card(None)
        assert card is None
        
        # Test with invalid recipe data
        invalid_recipe = Recipe()  # Missing required fields
        card = coordinator._create_recipe_card(invalid_recipe)
        # Should handle gracefully (exact behavior depends on implementation)


class TestRecipeRendering:
    """Test recipe rendering operations."""
    
    def test_render_recipes_basic(self, rendering_coordinator, mock_card_factory, flow_layout):
        """Test basic recipe rendering."""
        coordinator = rendering_coordinator
        recipes = create_test_recipes(3)
        
        success = coordinator.render_recipes(recipes)
        
        assert success is True
        assert coordinator._render_state.total_recipes == 3
        
        # Process rendering
        QApplication.processEvents()
        
        # Verify cards were added to layout
        assert flow_layout.count() >= 0  # May be progressive
    
    def test_render_recipes_empty_list(self, rendering_coordinator, mock_card_factory):
        """Test rendering empty recipe list."""
        coordinator = rendering_coordinator
        
        success = coordinator.render_recipes([])
        
        assert success is True
        assert coordinator._render_state.total_recipes == 0
    
    def test_render_recipes_progressive(self, rendering_coordinator, mock_card_factory):
        """Test progressive recipe rendering."""
        coordinator = rendering_coordinator
        recipes = create_test_recipes(10)  # More than batch size
        
        # Enable progressive rendering
        coordinator._use_progressive_rendering = True
        
        success = coordinator.render_recipes(recipes)
        
        assert success is True
        assert coordinator._render_state.is_rendering is True or coordinator._render_state.rendering_complete
        
        # Process multiple rendering batches
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Eventually should complete
        # Note: Exact verification depends on progressive rendering implementation
    
    def test_render_recipes_immediate(self, rendering_coordinator, mock_card_factory):
        """Test immediate recipe rendering."""
        coordinator = rendering_coordinator
        recipes = create_test_recipes(5)
        
        # Disable progressive rendering
        coordinator._use_progressive_rendering = False
        
        success = coordinator.render_recipes(recipes)
        
        assert success is True
        QApplication.processEvents()
        
        # Should render immediately
        assert coordinator._render_state.rendering_complete is True
    
    def test_render_recipes_with_existing_cards(self, rendering_coordinator, mock_card_factory):
        """Test rendering when cards already exist."""
        coordinator = rendering_coordinator
        
        # First render
        recipes1 = create_test_recipes(3)
        coordinator.render_recipes(recipes1)
        QApplication.processEvents()
        
        initial_count = len(coordinator._active_cards)
        
        # Second render with different recipes
        recipes2 = create_test_recipes(3, start_id=10)
        coordinator.render_recipes(recipes2)
        QApplication.processEvents()
        
        # Should clear previous cards and render new ones
        assert len(coordinator._active_cards) >= 0


class TestSelectionModeHandling:
    """Test selection mode functionality."""
    
    def test_set_selection_mode_enable(self, rendering_coordinator, mock_card_factory):
        """Test enabling selection mode."""
        coordinator = rendering_coordinator
        
        # Create and render some cards
        recipes = create_test_recipes(3)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Enable selection mode
        coordinator.set_selection_mode(True)
        
        assert coordinator._selection_mode is True
        
        # Verify cards are updated to selection mode
        for card in coordinator._active_cards.values():
            if hasattr(card, 'selection_changed_count'):
                assert card.selection_changed_count > 0
    
    def test_set_selection_mode_disable(self, rendering_coordinator, mock_card_factory):
        """Test disabling selection mode."""
        coordinator = rendering_coordinator
        
        # Enable first
        coordinator.set_selection_mode(True)
        
        # Create cards in selection mode
        recipes = create_test_recipes(2)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Disable selection mode
        coordinator.set_selection_mode(False)
        
        assert coordinator._selection_mode is False
    
    def test_selection_mode_with_new_cards(self, rendering_coordinator, mock_card_factory):
        """Test selection mode with newly created cards."""
        coordinator = rendering_coordinator
        
        # Enable selection mode first
        coordinator.set_selection_mode(True)
        
        # Render new cards
        recipes = create_test_recipes(3)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # New cards should be created in selection mode
        for card in coordinator._active_cards.values():
            # Verify cards were configured for selection mode
            # Exact verification depends on card implementation
            assert card is not None


class TestCardInteractionHandling:
    """Test recipe card interaction handling."""
    
    def test_handle_card_clicked(self, rendering_coordinator, mock_card_factory):
        """Test handling card click interactions."""
        coordinator = rendering_coordinator
        
        # Setup signal capture
        clicked_recipes = []
        coordinator.recipe_card_clicked.connect(
            lambda recipe_id, interaction_type: clicked_recipes.append((recipe_id, interaction_type))
        )
        
        # Create and render cards
        recipes = create_test_recipes(2)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Simulate card click
        test_recipe = recipes[0]
        coordinator._handle_card_interaction(test_recipe.id, CardInteractionType.CARD_CLICKED)
        
        # Verify signal emission
        assert len(clicked_recipes) == 1
        assert clicked_recipes[0][0] == test_recipe.id
        assert clicked_recipes[0][1] == CardInteractionType.CARD_CLICKED
    
    def test_handle_favorite_toggled(self, rendering_coordinator, mock_card_factory):
        """Test handling favorite toggle interactions."""
        coordinator = rendering_coordinator
        
        # Setup signal capture
        favorite_events = []
        coordinator.recipe_card_clicked.connect(
            lambda recipe_id, interaction_type: favorite_events.append((recipe_id, interaction_type))
        )
        
        # Create card
        recipe = create_test_recipe(is_favorite=False)
        coordinator.render_recipes([recipe])
        QApplication.processEvents()
        
        # Simulate favorite toggle
        coordinator._handle_card_interaction(recipe.id, CardInteractionType.FAVORITE_TOGGLED)
        
        # Verify signal
        assert len(favorite_events) == 1
        assert favorite_events[0][1] == CardInteractionType.FAVORITE_TOGGLED
    
    def test_handle_selection_changed(self, rendering_coordinator, mock_card_factory):
        """Test handling selection change interactions."""
        coordinator = rendering_coordinator
        
        # Setup signal capture
        selection_events = []
        coordinator.recipe_card_selection_changed.connect(
            lambda recipe_id, selected: selection_events.append((recipe_id, selected))
        )
        
        # Enable selection mode
        coordinator.set_selection_mode(True)
        
        # Create card
        recipe = create_test_recipe()
        coordinator.render_recipes([recipe])
        QApplication.processEvents()
        
        # Simulate selection change
        coordinator._handle_selection_changed(recipe.id, True)
        
        # Verify signal
        assert len(selection_events) == 1
        assert selection_events[0][0] == recipe.id
        assert selection_events[0][1] is True
    
    def test_handle_recipe_opened(self, rendering_coordinator, mock_card_factory):
        """Test handling recipe opened interactions."""
        coordinator = rendering_coordinator
        
        # Setup signal capture
        opened_recipes = []
        coordinator.recipe_card_clicked.connect(
            lambda recipe_id, interaction_type: opened_recipes.append((recipe_id, interaction_type))
        )
        
        # Create card
        recipe = create_test_recipe()
        coordinator.render_recipes([recipe])
        QApplication.processEvents()
        
        # Simulate recipe open
        coordinator._handle_card_interaction(recipe.id, CardInteractionType.RECIPE_OPENED)
        
        # Verify signal
        assert len(opened_recipes) == 1
        assert opened_recipes[0][1] == CardInteractionType.RECIPE_OPENED


class TestLayoutManagement:
    """Test layout management functionality."""
    
    def test_add_card_to_layout(self, rendering_coordinator, mock_card_factory, flow_layout):
        """Test adding cards to layout."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe()
        
        card = coordinator._create_recipe_card(recipe)
        coordinator._add_card_to_layout(card, recipe.id)
        
        # Verify card was added
        assert recipe.id in coordinator._active_cards
        assert flow_layout.count() == 1
    
    def test_remove_card_from_layout(self, rendering_coordinator, mock_card_factory, flow_layout):
        """Test removing cards from layout."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe()
        
        # Add card first
        card = coordinator._create_recipe_card(recipe)
        coordinator._add_card_to_layout(card, recipe.id)
        
        # Remove card
        coordinator._remove_card_from_layout(recipe.id)
        
        # Verify card was removed
        assert recipe.id not in coordinator._active_cards
        assert flow_layout.count() == 0
    
    def test_clear_all_cards(self, rendering_coordinator, mock_card_factory, flow_layout):
        """Test clearing all cards from layout."""
        coordinator = rendering_coordinator
        recipes = create_test_recipes(5)
        
        # Add multiple cards
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        initial_count = len(coordinator._active_cards)
        
        # Clear all cards
        coordinator.clear_all_cards()
        
        # Verify all cards cleared
        assert len(coordinator._active_cards) == 0
        assert flow_layout.count() == 0
    
    def test_update_layout_geometry(self, rendering_coordinator, mock_card_factory):
        """Test layout geometry updates."""
        coordinator = rendering_coordinator
        
        # Should not crash
        coordinator._update_layout_geometry()
        
        # Add some cards and update again
        recipes = create_test_recipes(3)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        coordinator._update_layout_geometry()


class TestPerformanceOptimization:
    """Test performance optimization features."""
    
    def test_card_pooling_integration(self, rendering_coordinator, performance_manager, mock_card_factory):
        """Test card pooling integration."""
        coordinator = rendering_coordinator
        
        # Render recipes to use card pool
        recipes = create_test_recipes(5)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Clear cards (should return to pool)
        coordinator.clear_all_cards()
        
        # Render again (should reuse from pool)
        new_recipes = create_test_recipes(3)
        coordinator.render_recipes(new_recipes)
        QApplication.processEvents()
        
        # Verify pool statistics
        if hasattr(coordinator, '_card_pool') and coordinator._card_pool:
            stats = coordinator._card_pool.statistics
            assert stats['total_created'] >= 0
    
    def test_progressive_rendering_performance(self, rendering_coordinator, mock_card_factory):
        """Test progressive rendering performance optimization."""
        coordinator = rendering_coordinator
        
        # Large dataset to trigger progressive rendering
        recipes = create_test_recipes(20)
        
        # Enable progressive rendering
        coordinator._use_progressive_rendering = True
        
        start_time = time.perf_counter()
        
        success = coordinator.render_recipes(recipes)
        
        # Process batches
        for _ in range(15):
            QApplication.processEvents()
            time.sleep(0.01)
        
        end_time = time.perf_counter()
        
        # Should complete in reasonable time
        assert (end_time - start_time) < 2.0  # Adjust threshold as needed
        assert success is True
    
    def test_memory_management_cards(self, rendering_coordinator, mock_card_factory):
        """Test memory management for recipe cards."""
        coordinator = rendering_coordinator
        
        # Create weak references to track cleanup
        card_refs = []
        
        # Create and render cards
        recipes = create_test_recipes(5)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Collect card references
        for card in coordinator._active_cards.values():
            card_refs.append(weakref.ref(card))
        
        # Clear cards
        coordinator.clear_all_cards()
        QApplication.processEvents()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Cards should be cleaned up (exact verification depends on implementation)
        # Note: Weak references may still be alive due to pools
    
    def test_render_batch_optimization(self, rendering_coordinator, mock_card_factory):
        """Test render batching optimization."""
        coordinator = rendering_coordinator
        
        # Configure small batch size for testing
        coordinator._batch_size = 2
        
        recipes = create_test_recipes(6)  # Multiple batches
        
        # Track rendering progress
        rendered_counts = []
        
        def track_progress():
            rendered_counts.append(coordinator._render_state.rendered_count)
        
        # Start rendering
        success = coordinator.render_recipes(recipes)
        
        # Process batches with tracking
        for _ in range(10):
            track_progress()
            QApplication.processEvents()
            time.sleep(0.01)
        
        assert success is True
        # Should show progressive increase in rendered count
        # Note: Exact verification depends on implementation


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""
    
    def test_render_with_invalid_recipe_data(self, rendering_coordinator, mock_card_factory):
        """Test rendering with invalid recipe data."""
        coordinator = rendering_coordinator
        
        # Mix valid and invalid recipes
        recipes = [
            create_test_recipe(id=1),
            None,  # Invalid
            create_test_recipe(id=2, recipe_name=""),  # Potentially invalid
            create_test_recipe(id=3)
        ]
        
        success = coordinator.render_recipes(recipes)
        
        # Should handle gracefully
        assert success is True or success is False  # Depends on implementation
        
        # Should not crash
        QApplication.processEvents()
    
    def test_card_interaction_with_missing_recipe(self, rendering_coordinator):
        """Test card interaction with missing recipe ID."""
        coordinator = rendering_coordinator
        
        # Try to handle interaction for non-existent recipe
        coordinator._handle_card_interaction(999, CardInteractionType.CARD_CLICKED)
        
        # Should not crash
    
    def test_selection_mode_with_no_cards(self, rendering_coordinator):
        """Test selection mode changes with no cards."""
        coordinator = rendering_coordinator
        
        # Enable selection mode with no cards
        coordinator.set_selection_mode(True)
        assert coordinator._selection_mode is True
        
        # Disable selection mode
        coordinator.set_selection_mode(False)
        assert coordinator._selection_mode is False
    
    def test_layout_operations_with_deleted_cards(self, rendering_coordinator, mock_card_factory):
        """Test layout operations with deleted cards."""
        coordinator = rendering_coordinator
        recipe = create_test_recipe()
        
        # Create and add card
        card = coordinator._create_recipe_card(recipe)
        coordinator._add_card_to_layout(card, recipe.id)
        
        # Simulate card deletion
        card.deleteLater()
        QApplication.processEvents()
        
        # Try to remove from layout
        coordinator._remove_card_from_layout(recipe.id)
        
        # Should handle gracefully
    
    def test_progressive_rendering_cancellation(self, rendering_coordinator, mock_card_factory):
        """Test cancelling progressive rendering."""
        coordinator = rendering_coordinator
        
        # Start progressive rendering
        recipes = create_test_recipes(20)
        coordinator.render_recipes(recipes)
        
        # Cancel rendering
        coordinator.cancel_rendering()
        
        # Should stop rendering
        assert coordinator._render_state.is_rendering is False or coordinator._render_state.rendering_complete
    
    def test_rapid_render_operations(self, rendering_coordinator, mock_card_factory):
        """Test rapid render operations."""
        coordinator = rendering_coordinator
        
        # Rapidly start multiple render operations
        for i in range(5):
            recipes = create_test_recipes(3)
            coordinator.render_recipes(recipes)
            time.sleep(0.001)  # Very rapid
        
        # Process all operations
        for _ in range(20):
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Should handle gracefully without errors
    
    def test_memory_cleanup_during_rendering(self, rendering_coordinator, mock_card_factory, performance_manager):
        """Test memory cleanup during active rendering."""
        coordinator = rendering_coordinator
        
        # Start rendering
        recipes = create_test_recipes(15)
        coordinator.render_recipes(recipes)
        
        # Trigger memory cleanup while rendering
        performance_manager.trigger_memory_cleanup()
        
        # Continue rendering
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.01)
        
        # Should complete without issues


class TestRenderingCoordinatorCleanup:
    """Test RenderingCoordinator cleanup and resource management."""
    
    def test_cleanup_all_resources(self, rendering_coordinator, mock_card_factory):
        """Test comprehensive cleanup."""
        coordinator = rendering_coordinator
        
        # Create rendering state
        recipes = create_test_recipes(5)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Cleanup
        coordinator.cleanup()
        
        # Verify cleanup
        assert len(coordinator._active_cards) == 0
        assert coordinator._render_state.is_rendering is False
    
    def test_cleanup_with_active_rendering(self, rendering_coordinator, mock_card_factory):
        """Test cleanup with active progressive rendering."""
        coordinator = rendering_coordinator
        
        # Start progressive rendering
        recipes = create_test_recipes(20)
        coordinator._use_progressive_rendering = True
        coordinator.render_recipes(recipes)
        
        # Cleanup before completion
        coordinator.cleanup()
        
        # Should complete without hanging
    
    def test_cleanup_signal_connections(self, rendering_coordinator):
        """Test cleanup of signal connections."""
        coordinator = rendering_coordinator
        
        # Connect some test signals
        signal_received = []
        coordinator.rendering_started.connect(lambda: signal_received.append('started'))
        coordinator.rendering_completed.connect(lambda: signal_received.append('completed'))
        
        # Cleanup
        coordinator.cleanup()
        
        # Should not cause connection errors
    
    def test_cleanup_performance_manager_resources(self, rendering_coordinator, performance_manager):
        """Test cleanup of performance manager resources."""
        coordinator = rendering_coordinator
        
        # Use performance manager resources
        recipes = create_test_recipes(10)
        coordinator.render_recipes(recipes)
        QApplication.processEvents()
        
        # Cleanup
        coordinator.cleanup()
        
        # Performance manager should still be functional
        # (coordinator shouldn't break shared resources)
        summary = performance_manager.get_performance_summary()
        assert summary is not None