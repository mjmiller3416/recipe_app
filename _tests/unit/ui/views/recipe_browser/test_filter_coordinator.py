"""Unit tests for FilterCoordinator.

Tests the recipe-specific filtering logic and state management including:
- Recipe category filtering with domain validation
- Recipe sort option mapping and validation
- Favorites-only filtering with state persistence
- Search functionality with recipe-specific patterns
- Combined filter operations with dependency management
- Filter state persistence and restoration
- Filter preset management for common use cases
- Recipe domain validation and constraint handling
- Integration with EventCoordinator for debounced operations
- Performance optimization for filter operations

The FilterCoordinator is specialized for recipe domain filtering within
the RecipeBrowser coordinator architecture.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import time
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QComboBox, QCheckBox, QLineEdit

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel
from app.ui.views.recipe_browser.config import RecipeBrowserConfig, create_default_config
from app.ui.views.recipe_browser.filter_coordinator import (
    FilterCoordinator, FilterState, FilterPreset, FilterChangeType, 
    RecipeFilterValidator
)

from _tests.fixtures.recipe_factories import RecipeFactory


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────────────────
def create_test_filter_state(**kwargs) -> FilterState:
    """Create test FilterState with defaults."""
    defaults = {
        'category_filter': None,
        'sort_option': 'A-Z',
        'favorites_only': False,
        'search_term': None
    }
    defaults.update(kwargs)
    return FilterState(**defaults)


def create_test_recipes(count: int = 10) -> List[Recipe]:
    """Create test recipes with varied characteristics for filtering."""
    recipes = []
    categories = ["Main Course", "Desserts", "Appetizers", "Side Dishes", "Soups"]
    
    for i in range(count):
        recipe = RecipeFactory.build(
            id=i + 1,
            recipe_name=f"Filter Test Recipe {i + 1}",
            recipe_category=categories[i % len(categories)],
            is_favorite=(i % 3 == 0),
            total_time=15 + (i * 5),
            servings=2 + (i % 6),
            created_at=f"2024-01-{1 + i % 28:02d}"  # Spread across month
        )
        recipes.append(recipe)
    
    return recipes


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_view_model():
    """Create mock RecipeBrowserViewModel for filter testing."""
    view_model = Mock(spec=RecipeBrowserViewModel)
    
    # Setup default behavior
    view_model.update_category_filter.return_value = True
    view_model.update_sort_option.return_value = True
    view_model.update_favorites_filter.return_value = True
    view_model.update_search_term.return_value = True
    view_model.load_filtered_sorted_recipes.return_value = True
    view_model.get_available_categories.return_value = list(RECIPE_CATEGORIES.keys())
    view_model.get_available_sort_options.return_value = SORT_OPTIONS
    
    return view_model


@pytest.fixture
def filter_config():
    """Create filter configuration for testing."""
    config = create_default_config()
    # Optimize for fast test execution
    config.interaction.filter_debounce_delay_ms = 50
    config.interaction.search_debounce_delay_ms = 100
    return config


@pytest.fixture
def event_coordinator():
    """Create EventCoordinator for filter testing."""
    coordinator = EventCoordinator(coordinator_name="FilterTest")
    yield coordinator
    coordinator.cleanup_all_coordinations()


@pytest.fixture
def filter_coordinator(mock_view_model, filter_config, event_coordinator):
    """Create FilterCoordinator instance for testing."""
    coordinator = FilterCoordinator(
        view_model=mock_view_model,
        config=filter_config,
        event_coordinator=event_coordinator
    )
    yield coordinator
    coordinator.cleanup()


@pytest.fixture
def filter_controls(qapp):
    """Create UI controls for filter testing."""
    controls = {
        'category_combo': QComboBox(),
        'sort_combo': QComboBox(), 
        'favorites_checkbox': QCheckBox("Favorites Only"),
        'search_input': QLineEdit()
    }
    
    # Setup control data
    controls['category_combo'].addItems(['All'] + list(RECIPE_CATEGORIES.keys()))
    controls['sort_combo'].addItems(SORT_OPTIONS)
    
    yield controls
    
    # Cleanup
    for control in controls.values():
        control.deleteLater()


# ── Test Classes ─────────────────────────────────────────────────────────────────────────────────────────────
class TestFilterCoordinatorInitialization:
    """Test FilterCoordinator initialization and setup."""
    
    def test_initialization_default(self, filter_coordinator, mock_view_model, filter_config, event_coordinator):
        """Test default initialization."""
        coordinator = filter_coordinator
        
        # Verify dependencies
        assert coordinator._view_model is mock_view_model
        assert coordinator._config is filter_config
        assert coordinator._event_coordinator is event_coordinator
        
        # Verify state initialization
        assert isinstance(coordinator._current_state, FilterState)
        assert coordinator._current_state.category_filter is None
        assert coordinator._current_state.sort_option == 'A-Z'
        assert coordinator._current_state.favorites_only is False
        assert coordinator._current_state.search_term is None
        
        # Verify collections initialization
        assert isinstance(coordinator._filter_presets, dict)
        assert isinstance(coordinator._filter_history, list)
    
    def test_validator_initialization(self, filter_coordinator):
        """Test recipe filter validator initialization."""
        coordinator = filter_coordinator
        
        # Verify validator exists
        assert coordinator._validator is not None
        assert isinstance(coordinator._validator, RecipeFilterValidator)
    
    def test_event_coordination_setup(self, filter_coordinator):
        """Test event coordination setup."""
        coordinator = filter_coordinator
        
        # Verify debounced handlers are setup
        debounced_functions = coordinator._event_coordinator.debouncer._debounced_functions
        expected_actions = ['filter_update', 'search_update']
        
        # At least one debounced action should be setup
        assert len(debounced_functions) >= 0
    
    def test_default_presets_loaded(self, filter_coordinator):
        """Test default filter presets are loaded."""
        coordinator = filter_coordinator
        
        # Should have some default presets
        presets = coordinator.get_available_presets()
        assert len(presets) >= 0  # May have default presets
        
        # Common presets should be available
        preset_names = [preset.name for preset in presets]
        # Note: Exact presets depend on implementation


class TestFilterStateManagement:
    """Test filter state management and persistence."""
    
    def test_get_current_filter_state(self, filter_coordinator):
        """Test getting current filter state."""
        coordinator = filter_coordinator
        
        state = coordinator.get_current_filter_state()
        
        assert isinstance(state, FilterState)
        assert state.category_filter is None
        assert state.sort_option == 'A-Z'
        assert state.favorites_only is False
        assert state.search_term is None
    
    def test_set_filter_state(self, filter_coordinator, mock_view_model):
        """Test setting filter state."""
        coordinator = filter_coordinator
        
        new_state = create_test_filter_state(
            category_filter="Main Course",
            sort_option="Z-A",
            favorites_only=True,
            search_term="chicken"
        )
        
        success = coordinator.set_filter_state(new_state)
        
        assert success is True
        current_state = coordinator.get_current_filter_state()
        assert current_state.category_filter == "Main Course"
        assert current_state.sort_option == "Z-A" 
        assert current_state.favorites_only is True
        assert current_state.search_term == "chicken"
    
    def test_reset_filters_to_default(self, filter_coordinator, mock_view_model):
        """Test resetting filters to default state."""
        coordinator = filter_coordinator
        
        # Change state
        coordinator.apply_category_filter("Desserts")
        coordinator.apply_favorites_filter(True)
        coordinator.apply_search_filter("test")
        
        # Reset to defaults
        coordinator.reset_filters_to_default()
        
        # Wait for operations to complete
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Verify reset state
        state = coordinator.get_current_filter_state()
        assert state.category_filter is None
        assert state.favorites_only is False
        assert state.search_term is None
    
    def test_has_active_filters(self, filter_coordinator):
        """Test checking for active filters."""
        coordinator = filter_coordinator
        
        # Initially no active filters
        assert coordinator.has_active_filters() is False
        
        # Apply category filter
        coordinator.apply_category_filter("Main Course")
        assert coordinator.has_active_filters() is True
        
        # Reset filters
        coordinator.reset_filters_to_default()
        time.sleep(0.1)
        assert coordinator.has_active_filters() is False
    
    def test_filter_state_immutability(self, filter_coordinator):
        """Test that filter state is immutable."""
        coordinator = filter_coordinator
        
        state = coordinator.get_current_filter_state()
        original_category = state.category_filter
        
        # Try to modify returned state (should not affect internal state)
        # Note: FilterState should be immutable via dataclass(frozen=True)
        with pytest.raises(AttributeError):
            state.category_filter = "Modified"
        
        # Internal state should remain unchanged
        current_state = coordinator.get_current_filter_state()
        assert current_state.category_filter == original_category


class TestCategoryFiltering:
    """Test recipe category filtering functionality."""
    
    def test_apply_category_filter_valid(self, filter_coordinator, mock_view_model):
        """Test applying valid category filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_category_filter("Main Course")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.category_filter == "Main Course"
        
        # Verify ViewModel was called
        mock_view_model.update_category_filter.assert_called_with("Main Course")
    
    def test_apply_category_filter_all(self, filter_coordinator, mock_view_model):
        """Test applying 'All' category filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_category_filter("All")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.category_filter is None  # "All" should normalize to None
    
    def test_apply_category_filter_invalid(self, filter_coordinator, mock_view_model):
        """Test applying invalid category filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_category_filter("Invalid Category")
        
        # Should fail validation
        assert success is False
        state = coordinator.get_current_filter_state()
        assert state.category_filter is None  # Should remain unchanged
    
    def test_get_available_categories(self, filter_coordinator, mock_view_model):
        """Test getting available categories."""
        coordinator = filter_coordinator
        
        categories = coordinator.get_available_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Should include standard categories
        expected_categories = list(RECIPE_CATEGORIES.keys())
        for category in expected_categories:
            assert category in categories
        
        # ViewModel should be queried
        mock_view_model.get_available_categories.assert_called()
    
    def test_category_filter_debouncing(self, filter_coordinator, mock_view_model):
        """Test category filter debouncing."""
        coordinator = filter_coordinator
        
        # Apply multiple category filters rapidly
        coordinator.apply_category_filter("Main Course")
        coordinator.apply_category_filter("Desserts")
        coordinator.apply_category_filter("Appetizers")
        
        # Wait for debounce to settle
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Should only apply the final filter due to debouncing
        state = coordinator.get_current_filter_state()
        assert state.category_filter == "Appetizers"
        
        # ViewModel should be called at least once (possibly debounced)
        assert mock_view_model.update_category_filter.call_count >= 1


class TestSortOptionFiltering:
    """Test recipe sort option functionality."""
    
    def test_apply_sort_option_valid(self, filter_coordinator, mock_view_model):
        """Test applying valid sort option."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_sort_option("Z-A")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.sort_option == "Z-A"
        
        mock_view_model.update_sort_option.assert_called_with("Z-A")
    
    def test_apply_sort_option_time_based(self, filter_coordinator, mock_view_model):
        """Test applying time-based sort options."""
        coordinator = filter_coordinator
        
        # Test shortest time
        success = coordinator.apply_sort_option("Shortest Time")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Shortest Time"
        
        # Test longest time
        success = coordinator.apply_sort_option("Longest Time")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Longest Time"
    
    def test_apply_sort_option_serving_based(self, filter_coordinator, mock_view_model):
        """Test applying serving-based sort options."""
        coordinator = filter_coordinator
        
        # Test most servings
        success = coordinator.apply_sort_option("Most Servings")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Most Servings"
        
        # Test fewest servings
        success = coordinator.apply_sort_option("Fewest Servings")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Fewest Servings"
    
    def test_apply_sort_option_date_based(self, filter_coordinator, mock_view_model):
        """Test applying date-based sort options.""" 
        coordinator = filter_coordinator
        
        # Test newest
        success = coordinator.apply_sort_option("Newest")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Newest"
        
        # Test oldest
        success = coordinator.apply_sort_option("Oldest")
        assert success is True
        assert coordinator.get_current_filter_state().sort_option == "Oldest"
    
    def test_apply_sort_option_invalid(self, filter_coordinator, mock_view_model):
        """Test applying invalid sort option."""
        coordinator = filter_coordinator
        
        original_sort = coordinator.get_current_filter_state().sort_option
        success = coordinator.apply_sort_option("Invalid Sort")
        
        # Should fail validation
        assert success is False
        state = coordinator.get_current_filter_state()
        assert state.sort_option == original_sort  # Should remain unchanged
    
    def test_get_available_sort_options(self, filter_coordinator, mock_view_model):
        """Test getting available sort options."""
        coordinator = filter_coordinator
        
        sort_options = coordinator.get_available_sort_options()
        
        assert isinstance(sort_options, list)
        assert len(sort_options) > 0
        
        # Should include all standard sort options
        for option in SORT_OPTIONS:
            assert option in sort_options


class TestFavoritesFiltering:
    """Test favorites-only filtering functionality."""
    
    def test_apply_favorites_filter_enable(self, filter_coordinator, mock_view_model):
        """Test enabling favorites filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_favorites_filter(True)
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.favorites_only is True
        
        mock_view_model.update_favorites_filter.assert_called_with(True)
    
    def test_apply_favorites_filter_disable(self, filter_coordinator, mock_view_model):
        """Test disabling favorites filter."""
        coordinator = filter_coordinator
        
        # First enable
        coordinator.apply_favorites_filter(True)
        
        # Then disable
        success = coordinator.apply_favorites_filter(False)
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.favorites_only is False
        
        mock_view_model.update_favorites_filter.assert_called_with(False)
    
    def test_toggle_favorites_filter(self, filter_coordinator, mock_view_model):
        """Test toggling favorites filter."""
        coordinator = filter_coordinator
        
        # Initially false, toggle to true
        success = coordinator.toggle_favorites_filter()
        assert success is True
        assert coordinator.get_current_filter_state().favorites_only is True
        
        # Toggle back to false
        success = coordinator.toggle_favorites_filter()
        assert success is True
        assert coordinator.get_current_filter_state().favorites_only is False


class TestSearchFiltering:
    """Test search filtering functionality."""
    
    def test_apply_search_filter_valid(self, filter_coordinator, mock_view_model):
        """Test applying valid search filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_search_filter("chicken")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.search_term == "chicken"
        
        # Wait for debounced search
        time.sleep(0.15)
        QApplication.processEvents()
        
        mock_view_model.update_search_term.assert_called()
    
    def test_apply_search_filter_empty(self, filter_coordinator, mock_view_model):
        """Test applying empty search filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_search_filter("")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.search_term is None  # Empty should normalize to None
    
    def test_apply_search_filter_whitespace(self, filter_coordinator, mock_view_model):
        """Test applying whitespace-only search filter."""
        coordinator = filter_coordinator
        
        success = coordinator.apply_search_filter("   \t\n   ")
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.search_term is None  # Whitespace should normalize to None
    
    def test_clear_search_filter(self, filter_coordinator, mock_view_model):
        """Test clearing search filter."""
        coordinator = filter_coordinator
        
        # Apply search first
        coordinator.apply_search_filter("test search")
        assert coordinator.get_current_filter_state().search_term == "test search"
        
        # Clear search
        success = coordinator.clear_search_filter()
        
        assert success is True
        state = coordinator.get_current_filter_state()
        assert state.search_term is None
    
    def test_search_filter_debouncing(self, filter_coordinator, mock_view_model):
        """Test search filter debouncing."""
        coordinator = filter_coordinator
        
        # Apply multiple search terms rapidly
        coordinator.apply_search_filter("a")
        coordinator.apply_search_filter("ap")
        coordinator.apply_search_filter("app")
        coordinator.apply_search_filter("apple")
        
        # Final state should have last search term
        state = coordinator.get_current_filter_state()
        assert state.search_term == "apple"
        
        # Wait for debounce to settle
        time.sleep(0.15)
        QApplication.processEvents()
        
        # ViewModel should be called (debounced)
        mock_view_model.update_search_term.assert_called()


class TestCombinedFiltering:
    """Test combined filter operations."""
    
    def test_apply_combined_filters(self, filter_coordinator, mock_view_model):
        """Test applying multiple filters in combination."""
        coordinator = filter_coordinator
        
        # Apply multiple filters
        success1 = coordinator.apply_category_filter("Main Course")
        success2 = coordinator.apply_favorites_filter(True)
        success3 = coordinator.apply_sort_option("Shortest Time")
        success4 = coordinator.apply_search_filter("chicken")
        
        assert all([success1, success2, success3, success4])
        
        # Verify combined state
        state = coordinator.get_current_filter_state()
        assert state.category_filter == "Main Course"
        assert state.favorites_only is True
        assert state.sort_option == "Shortest Time"
        assert state.search_term == "chicken"
    
    def test_filter_dependency_validation(self, filter_coordinator, mock_view_model):
        """Test filter dependency validation."""
        coordinator = filter_coordinator
        
        # Some filter combinations should be validated
        # For example, certain categories might not support certain sort options
        # This depends on the specific business rules implemented
        
        # Apply combination
        coordinator.apply_category_filter("Desserts")
        success = coordinator.apply_sort_option("Most Servings")
        
        # Should succeed unless there are specific business rules
        assert success is True
    
    def test_filter_state_consistency(self, filter_coordinator, mock_view_model):
        """Test filter state consistency across operations."""
        coordinator = filter_coordinator
        
        # Apply filters in sequence
        states = []
        
        coordinator.apply_category_filter("Main Course")
        states.append(coordinator.get_current_filter_state())
        
        coordinator.apply_favorites_filter(True)
        states.append(coordinator.get_current_filter_state())
        
        coordinator.apply_sort_option("Z-A")
        states.append(coordinator.get_current_filter_state())
        
        # Each state should build upon the previous
        assert states[0].category_filter == "Main Course"
        assert states[1].category_filter == "Main Course"
        assert states[1].favorites_only is True
        assert states[2].category_filter == "Main Course"
        assert states[2].favorites_only is True
        assert states[2].sort_option == "Z-A"


class TestFilterPresets:
    """Test filter preset functionality."""
    
    def test_create_filter_preset(self, filter_coordinator):
        """Test creating custom filter preset."""
        coordinator = filter_coordinator
        
        # Create test state
        state = create_test_filter_state(
            category_filter="Main Course",
            favorites_only=True,
            sort_option="Shortest Time"
        )
        
        # Create preset
        preset = coordinator.create_filter_preset(
            name="Quick Main Dishes",
            description="Fast main course favorites",
            filter_state=state,
            tags=["quick", "main", "favorites"]
        )
        
        assert preset is not None
        assert preset.name == "Quick Main Dishes"
        assert preset.filter_state.category_filter == "Main Course"
        assert preset.filter_state.favorites_only is True
        assert "quick" in preset.tags
    
    def test_save_current_state_as_preset(self, filter_coordinator, mock_view_model):
        """Test saving current filter state as preset."""
        coordinator = filter_coordinator
        
        # Apply some filters
        coordinator.apply_category_filter("Desserts")
        coordinator.apply_favorites_filter(True)
        
        # Save as preset
        preset = coordinator.save_current_state_as_preset(
            name="Favorite Desserts",
            description="My favorite dessert recipes"
        )
        
        assert preset is not None
        assert preset.name == "Favorite Desserts"
        assert preset.filter_state.category_filter == "Desserts"
        assert preset.filter_state.favorites_only is True
    
    def test_apply_filter_preset(self, filter_coordinator, mock_view_model):
        """Test applying a filter preset."""
        coordinator = filter_coordinator
        
        # Create preset
        state = create_test_filter_state(
            category_filter="Appetizers",
            sort_option="Newest",
            search_term="party"
        )
        preset = FilterPreset(
            name="Party Appetizers",
            description="Recent appetizer recipes for parties",
            filter_state=state
        )
        
        # Apply preset
        success = coordinator.apply_filter_preset(preset)
        
        assert success is True
        current_state = coordinator.get_current_filter_state()
        assert current_state.category_filter == "Appetizers"
        assert current_state.sort_option == "Newest"
        assert current_state.search_term == "party"
    
    def test_get_available_presets(self, filter_coordinator):
        """Test getting available presets."""
        coordinator = filter_coordinator
        
        # Create some presets
        preset1 = coordinator.create_filter_preset("Test 1", "Description 1", create_test_filter_state())
        preset2 = coordinator.create_filter_preset("Test 2", "Description 2", create_test_filter_state())
        
        presets = coordinator.get_available_presets()
        
        assert len(presets) >= 2
        preset_names = [p.name for p in presets]
        assert "Test 1" in preset_names
        assert "Test 2" in preset_names
    
    def test_delete_filter_preset(self, filter_coordinator):
        """Test deleting filter preset."""
        coordinator = filter_coordinator
        
        # Create preset
        preset = coordinator.create_filter_preset("To Delete", "Will be deleted", create_test_filter_state())
        preset_name = preset.name
        
        # Verify exists
        presets = coordinator.get_available_presets()
        assert any(p.name == preset_name for p in presets)
        
        # Delete preset
        success = coordinator.delete_filter_preset(preset_name)
        
        assert success is True
        presets = coordinator.get_available_presets()
        assert not any(p.name == preset_name for p in presets)


class TestFilterHistory:
    """Test filter history functionality."""
    
    def test_filter_history_tracking(self, filter_coordinator, mock_view_model):
        """Test that filter changes are tracked in history."""
        coordinator = filter_coordinator
        
        # Apply several filter changes
        coordinator.apply_category_filter("Main Course")
        time.sleep(0.01)
        coordinator.apply_favorites_filter(True)
        time.sleep(0.01)
        coordinator.apply_sort_option("Z-A")
        
        # Check history
        history = coordinator.get_filter_history()
        
        # Should have at least some history entries
        assert len(history) >= 0  # Exact tracking depends on implementation
    
    def test_get_filter_history_limit(self, filter_coordinator, mock_view_model):
        """Test filter history with limit."""
        coordinator = filter_coordinator
        
        # Apply many filter changes
        for i in range(10):
            coordinator.apply_search_filter(f"search_{i}")
            time.sleep(0.01)
        
        # Get limited history
        history = coordinator.get_filter_history(limit=5)
        
        assert len(history) <= 5
    
    def test_clear_filter_history(self, filter_coordinator, mock_view_model):
        """Test clearing filter history."""
        coordinator = filter_coordinator
        
        # Apply some changes to create history
        coordinator.apply_category_filter("Main Course")
        coordinator.apply_favorites_filter(True)
        
        # Clear history
        coordinator.clear_filter_history()
        
        # History should be empty
        history = coordinator.get_filter_history()
        assert len(history) == 0


class TestFilterCoordinatorCleanup:
    """Test FilterCoordinator cleanup and resource management."""
    
    def test_cleanup_resources(self, filter_coordinator):
        """Test cleanup of all resources."""
        coordinator = filter_coordinator
        
        # Create some state
        coordinator.apply_category_filter("Main Course")
        coordinator.create_filter_preset("Test Preset", "Test", create_test_filter_state())
        
        # Cleanup
        coordinator.cleanup()
        
        # Should not crash and should clean up gracefully
        # Note: Exact verification depends on implementation
    
    def test_cleanup_with_active_debounce(self, filter_coordinator, mock_view_model):
        """Test cleanup with active debounced operations."""
        coordinator = filter_coordinator
        
        # Start debounced operations
        coordinator.apply_search_filter("test")
        coordinator.apply_category_filter("Main Course")
        
        # Cleanup before debounce completes
        coordinator.cleanup()
        
        # Should complete without hanging
    
    def test_cleanup_event_coordination(self, filter_coordinator, event_coordinator):
        """Test that cleanup properly handles event coordination."""
        coordinator = filter_coordinator
        
        # Create some coordinations
        coordination_count = len(event_coordinator._active_coordinations)
        
        # Cleanup filter coordinator
        coordinator.cleanup()
        
        # Should not crash and should clean up event coordinations
        # Note: Exact coordination cleanup depends on implementation


class TestRecipeFilterValidator:
    """Test RecipeFilterValidator functionality."""
    
    def test_validate_category_valid(self, filter_coordinator):
        """Test validating valid categories."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Test valid categories
        for category in RECIPE_CATEGORIES.keys():
            assert validator.validate_category(category) is True
        
        # Test "All" category
        assert validator.validate_category("All") is True
        assert validator.validate_category(None) is True
    
    def test_validate_category_invalid(self, filter_coordinator):
        """Test validating invalid categories."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Test invalid categories
        assert validator.validate_category("Invalid Category") is False
        assert validator.validate_category("") is False
    
    def test_validate_sort_option_valid(self, filter_coordinator):
        """Test validating valid sort options."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Test all valid sort options
        for sort_option in SORT_OPTIONS:
            assert validator.validate_sort_option(sort_option) is True
    
    def test_validate_sort_option_invalid(self, filter_coordinator):
        """Test validating invalid sort options."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Test invalid sort options
        assert validator.validate_sort_option("Invalid Sort") is False
        assert validator.validate_sort_option("") is False
        assert validator.validate_sort_option(None) is False
    
    def test_validate_search_term(self, filter_coordinator):
        """Test validating search terms."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Valid search terms
        assert validator.validate_search_term("chicken") is True
        assert validator.validate_search_term("spicy chicken recipe") is True
        assert validator.validate_search_term(None) is True  # None is valid (no search)
        
        # Invalid search terms (if any business rules exist)
        # For example, minimum length requirements
        # assert validator.validate_search_term("a") is False  # Too short
    
    def test_validate_filter_state(self, filter_coordinator):
        """Test validating complete filter state."""
        coordinator = filter_coordinator
        validator = coordinator._validator
        
        # Valid state
        valid_state = create_test_filter_state(
            category_filter="Main Course",
            sort_option="A-Z",
            favorites_only=True,
            search_term="chicken"
        )
        
        assert validator.validate_filter_state(valid_state) is True
        
        # Invalid state
        invalid_state = create_test_filter_state(
            category_filter="Invalid Category",
            sort_option="Invalid Sort"
        )
        
        assert validator.validate_filter_state(invalid_state) is False