"""
Unit tests for RecipeBrowserViewModel.

Tests the recipe browser view model functionality including:
- Recipe loading and filtering logic
- Sort option parsing and application
- Search functionality
- Selection mode management
- Error handling and state management
- Recipe favorite toggling
- Filter state management
"""

from typing import List
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtCore import QObject
import pytest

from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.view_models.recipe_browser_view_model import RecipeBrowserViewModel

# ── Fixtures ────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = Mock()
    session.close = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    return session


@pytest.fixture
def mock_recipe_service():
    """Create a mock recipe service."""
    service = Mock(spec=RecipeService)
    return service


@pytest.fixture
def sample_recipes():
    """Create sample recipe objects for testing."""
    recipes = []
    
    # Create mock recipes
    recipe1 = Mock(spec=Recipe)
    recipe1.id = 1
    recipe1.recipe_name = "Apple Pie"
    recipe1.recipe_category = "Desserts"
    recipe1.is_favorite = False
    recipe1.total_time = 60
    recipe1.servings = 8
    
    recipe2 = Mock(spec=Recipe)
    recipe2.id = 2
    recipe2.recipe_name = "Beef Stew"
    recipe2.recipe_category = "Main Course"
    recipe2.is_favorite = True
    recipe2.total_time = 120
    recipe2.servings = 6
    
    recipe3 = Mock(spec=Recipe)
    recipe3.id = 3
    recipe3.recipe_name = "Caesar Salad"
    recipe3.recipe_category = "Salads"
    recipe3.is_favorite = False
    recipe3.total_time = 15
    recipe3.servings = 4
    
    return [recipe1, recipe2, recipe3]


@pytest.fixture
def browser_vm(mock_session):
    """Create RecipeBrowserViewModel instance with mocked session."""
    return RecipeBrowserViewModel(mock_session)


@pytest.fixture
def browser_vm_with_service(browser_vm, mock_recipe_service):
    """Create RecipeBrowserViewModel with mocked recipe service."""
    browser_vm._recipe_service = mock_recipe_service
    return browser_vm


# ── Test RecipeBrowserViewModel Initialization ──────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelInit:
    """Test RecipeBrowserViewModel initialization."""

    def test_initialization_default(self, browser_vm):
        """Test default initialization of RecipeBrowserViewModel."""
        assert browser_vm._recipe_service is None
        assert browser_vm._current_recipes == []
        assert isinstance(browser_vm._current_filter, RecipeFilterDTO)
        assert browser_vm._selection_mode is False
        assert browser_vm._recipes_loaded is False
        assert browser_vm._category_filter is None
        assert browser_vm._sort_option == "A-Z"
        assert browser_vm._favorites_only is False
        assert browser_vm._search_term is None

    def test_initialization_with_session(self, mock_session):
        """Test initialization with provided session."""
        vm = RecipeBrowserViewModel(mock_session)
        assert vm._session is mock_session
        assert not vm._owns_session  # Should not own injected session

    @patch('app.ui.view_models.recipe_browser_view_model.RecipeService')
    def test_ensure_recipe_service_success(self, mock_service_class, browser_vm):
        """Test successful recipe service initialization."""
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        
        result = browser_vm._ensure_recipe_service()
        
        assert result is True
        assert browser_vm._recipe_service is mock_service_instance
        mock_service_class.assert_called_once_with(browser_vm._session)

    def test_ensure_recipe_service_no_session(self):
        """Test recipe service initialization without session."""
        vm = RecipeBrowserViewModel(session=None)
        
        with patch.object(vm, '_ensure_session', return_value=False):
            result = vm._ensure_recipe_service()
            assert result is False


# ── Test Properties ─────────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelProperties:
    """Test RecipeBrowserViewModel properties."""

    def test_selection_mode_property(self, browser_vm):
        """Test selection mode property."""
        assert browser_vm.selection_mode is False
        
        browser_vm._selection_mode = True
        assert browser_vm.selection_mode is True

    def test_recipes_loaded_state_property(self, browser_vm):
        """Test recipes loaded state property."""
        assert browser_vm.recipes_loaded_state is False
        
        browser_vm._recipes_loaded = True
        assert browser_vm.recipes_loaded_state is True

    def test_current_recipes_property(self, browser_vm, sample_recipes):
        """Test current recipes property returns copy."""
        browser_vm._current_recipes = sample_recipes
        
        current = browser_vm.current_recipes
        assert current == sample_recipes
        assert current is not sample_recipes  # Should be a copy

    def test_recipe_count_property(self, browser_vm, sample_recipes):
        """Test recipe count property."""
        assert browser_vm.recipe_count == 0
        
        browser_vm._current_recipes = sample_recipes
        assert browser_vm.recipe_count == 3


# ── Test Recipe Loading ─────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelLoading:
    """Test recipe loading functionality."""

    def test_load_recipes_success(self, browser_vm_with_service, sample_recipes):
        """Test successful recipe loading with default filter."""
        # Setup
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        # Execute
        result = browser_vm_with_service.load_recipes()
        
        # Verify core business logic
        assert result is True
        assert browser_vm_with_service._recipes_loaded is True
        assert browser_vm_with_service._current_recipes == sample_recipes
        
        # Verify service was called with default filter
        expected_filter = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name", 
            sort_order="asc",
            favorites_only=False
        )
        browser_vm_with_service._recipe_service.list_filtered.assert_called_once()
        actual_filter = browser_vm_with_service._recipe_service.list_filtered.call_args[0][0]
        assert actual_filter.recipe_category == expected_filter.recipe_category
        assert actual_filter.sort_by == expected_filter.sort_by
        assert actual_filter.sort_order == expected_filter.sort_order
        assert actual_filter.favorites_only == expected_filter.favorites_only

    def test_load_recipes_service_error(self, browser_vm_with_service):
        """Test recipe loading with service error."""
        # Setup
        browser_vm_with_service._recipe_service.list_filtered.side_effect = Exception("Service error")
        
        # Execute
        result = browser_vm_with_service.load_recipes()
        
        # Verify business logic
        assert result is False
        assert browser_vm_with_service._recipes_loaded is False
        assert browser_vm_with_service._current_recipes == []

    def test_load_filtered_sorted_recipes_success(self, browser_vm_with_service, sample_recipes):
        """Test loading with custom filter DTO."""
        # Setup
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        filter_dto = RecipeFilterDTO(
            recipe_category="Main Course",
            sort_by="total_time",
            sort_order="desc",
            favorites_only=True
        )
        
        # Execute
        result = browser_vm_with_service.load_filtered_sorted_recipes(filter_dto)
        
        # Verify
        assert result is True
        assert browser_vm_with_service._current_filter == filter_dto
        browser_vm_with_service._recipe_service.list_filtered.assert_called_once_with(filter_dto)

    def test_load_filtered_sorted_recipes_none_filter(self, browser_vm_with_service):
        """Test loading with None filter DTO."""
        result = browser_vm_with_service.load_filtered_sorted_recipes(None)
        assert result is False

    def test_refresh_recipes(self, browser_vm_with_service, sample_recipes):
        """Test refreshing recipes with existing filter."""
        # Setup existing filter
        browser_vm_with_service._current_filter = RecipeFilterDTO(favorites_only=True)
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        # Execute
        result = browser_vm_with_service.refresh_recipes()
        
        # Verify
        assert result is True
        browser_vm_with_service._recipe_service.list_filtered.assert_called_once_with(
            browser_vm_with_service._current_filter
        )

    def test_clear_recipes(self, browser_vm, sample_recipes):
        """Test clearing loaded recipes."""
        # Setup
        browser_vm._current_recipes = sample_recipes
        browser_vm._recipes_loaded = True
        
        # Execute
        browser_vm.clear_recipes()
        
        # Verify business logic
        assert browser_vm._current_recipes == []
        assert browser_vm._recipes_loaded is False


# ── Test Filter Management ──────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelFiltering:
    """Test filtering functionality."""

    def test_update_category_filter(self, browser_vm_with_service, sample_recipes):
        """Test updating category filter."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_category_filter("Main Course")
        
        assert result is True
        assert browser_vm_with_service._category_filter == "Main Course"

    def test_update_category_filter_normalize_all(self, browser_vm_with_service, sample_recipes):
        """Test category filter normalization for 'All'."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_category_filter("All")
        
        assert result is True
        assert browser_vm_with_service._category_filter is None

    def test_update_sort_option_valid(self, browser_vm_with_service, sample_recipes):
        """Test updating with valid sort option."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_sort_option("Z-A")
        
        assert result is True
        assert browser_vm_with_service._sort_option == "Z-A"

    def test_update_sort_option_invalid(self, browser_vm_with_service):
        """Test updating with invalid sort option."""
        result = browser_vm_with_service.update_sort_option("Invalid Sort")
        
        assert result is False
        assert browser_vm_with_service._sort_option == "A-Z"  # Should remain unchanged

    def test_update_favorites_filter(self, browser_vm_with_service, sample_recipes):
        """Test updating favorites filter."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_favorites_filter(True)
        
        assert result is True
        assert browser_vm_with_service._favorites_only is True

    def test_update_search_term(self, browser_vm_with_service, sample_recipes):
        """Test updating search term."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_search_term("Apple")
        
        assert result is True
        assert browser_vm_with_service._search_term == "Apple"

    def test_update_search_term_normalize_empty(self, browser_vm_with_service, sample_recipes):
        """Test search term normalization for empty string."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.update_search_term("  ")
        
        assert result is True
        assert browser_vm_with_service._search_term is None

    def test_parse_sort_option_all_options(self, browser_vm):
        """Test parsing all available sort options."""
        test_cases = [
            ("A-Z", ("recipe_name", "asc")),
            ("Z-A", ("recipe_name", "desc")),
            ("Newest", ("created_at", "desc")),
            ("Oldest", ("created_at", "asc")),
            ("Shortest Time", ("total_time", "asc")),
            ("Longest Time", ("total_time", "desc")),
            ("Most Servings", ("servings", "desc")),
            ("Fewest Servings", ("servings", "asc")),
        ]
        
        for sort_option, expected in test_cases:
            result = browser_vm._parse_sort_option(sort_option)
            assert result == expected

    def test_parse_sort_option_unknown(self, browser_vm):
        """Test parsing unknown sort option defaults to A-Z."""
        result = browser_vm._parse_sort_option("Unknown Sort")
        assert result == ("recipe_name", "asc")


# ── Test Selection Mode ─────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelSelection:
    """Test selection mode functionality."""

    def test_set_selection_mode_enable(self, browser_vm):
        """Test enabling selection mode."""
        browser_vm.set_selection_mode(True)
        
        assert browser_vm._selection_mode is True

    def test_set_selection_mode_disable(self, browser_vm):
        """Test disabling selection mode."""
        browser_vm._selection_mode = True
        
        browser_vm.set_selection_mode(False)
        
        assert browser_vm._selection_mode is False

    def test_set_selection_mode_no_change(self, browser_vm):
        """Test setting selection mode to same value."""
        initial_state = browser_vm._selection_mode
        
        browser_vm.set_selection_mode(False)  # Already False
        
        assert browser_vm._selection_mode == initial_state

    def test_handle_recipe_selection_success(self, browser_vm, sample_recipes):
        """Test successful recipe selection logic."""
        browser_vm._selection_mode = True
        
        recipe = sample_recipes[0]
        # Test that method doesn't raise error - signal emission tested elsewhere
        browser_vm.handle_recipe_selection(recipe)
        
        # Test business logic remains intact
        assert browser_vm._selection_mode is True

    def test_handle_recipe_selection_not_in_selection_mode(self, browser_vm, sample_recipes):
        """Test recipe selection when not in selection mode."""
        browser_vm._selection_mode = False
        
        recipe = sample_recipes[0]
        # Should not raise error but also not change state
        browser_vm.handle_recipe_selection(recipe)
        
        assert browser_vm._selection_mode is False

    def test_handle_recipe_selection_none_recipe(self, browser_vm):
        """Test recipe selection with None recipe."""
        browser_vm._selection_mode = True
        
        # Should not raise error
        browser_vm.handle_recipe_selection(None)
        
        assert browser_vm._selection_mode is True


# ── Test Search Operations ──────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelSearch:
    """Test search functionality."""

    def test_search_recipes_with_term(self, browser_vm_with_service, sample_recipes):
        """Test searching recipes with search term."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.search_recipes("Apple", apply_current_filters=False)
        
        assert result is True
        assert browser_vm_with_service._search_term == "Apple"

    def test_search_recipes_empty_term(self, browser_vm_with_service, sample_recipes):
        """Test searching with empty term loads all recipes."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        result = browser_vm_with_service.search_recipes("", apply_current_filters=False)
        
        assert result is True
        assert browser_vm_with_service._search_term is None

    def test_search_recipes_with_current_filters(self, browser_vm_with_service, sample_recipes):
        """Test searching with current filters applied."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        browser_vm_with_service._favorites_only = True
        
        result = browser_vm_with_service.search_recipes("Apple", apply_current_filters=True)
        
        assert result is True
        # Should call _update_filter_and_reload which applies current filters

    def test_clear_search(self, browser_vm_with_service, sample_recipes):
        """Test clearing search term."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        browser_vm_with_service._search_term = "Apple"
        
        result = browser_vm_with_service.clear_search()
        
        assert result is True
        assert browser_vm_with_service._search_term is None


# ── Test Recipe Actions ─────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelActions:
    """Test recipe action functionality."""

    def test_toggle_recipe_favorite_success(self, browser_vm_with_service, sample_recipes):
        """Test successful recipe favorite toggle."""
        # Setup
        recipe = sample_recipes[0]
        recipe.is_favorite = True  # Toggle to true
        browser_vm_with_service._current_recipes = sample_recipes
        browser_vm_with_service._recipe_service.toggle_favorite.return_value = recipe
        
        # Execute
        result = browser_vm_with_service.toggle_recipe_favorite(recipe.id)
        
        # Verify
        assert result is True
        browser_vm_with_service._recipe_service.toggle_favorite.assert_called_once_with(recipe.id)

    def test_toggle_recipe_favorite_not_found(self, browser_vm_with_service):
        """Test recipe favorite toggle when recipe not found."""
        browser_vm_with_service._recipe_service.toggle_favorite.return_value = None
        
        result = browser_vm_with_service.toggle_recipe_favorite(999)
        
        assert result is False

    def test_toggle_recipe_favorite_service_error(self, browser_vm_with_service):
        """Test recipe favorite toggle with service error."""
        browser_vm_with_service._recipe_service.toggle_favorite.side_effect = Exception("Service error")
        
        result = browser_vm_with_service.toggle_recipe_favorite(1)
        
        assert result is False

    def test_get_recipe_by_id_found(self, browser_vm, sample_recipes):
        """Test getting recipe by ID when it exists."""
        browser_vm._current_recipes = sample_recipes
        
        recipe = browser_vm.get_recipe_by_id(2)
        
        assert recipe is sample_recipes[1]

    def test_get_recipe_by_id_not_found(self, browser_vm, sample_recipes):
        """Test getting recipe by ID when it doesn't exist."""
        browser_vm._current_recipes = sample_recipes
        
        recipe = browser_vm.get_recipe_by_id(999)
        
        assert recipe is None


# ── Test State Management ───────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelState:
    """Test state management functionality."""

    def test_reset_browser_state(self, browser_vm, sample_recipes):
        """Test resetting browser to initial state."""
        # Setup dirty state
        browser_vm._current_recipes = sample_recipes
        browser_vm._recipes_loaded = True
        browser_vm._category_filter = "Main Course"
        browser_vm._sort_option = "Z-A"
        browser_vm._favorites_only = True
        browser_vm._search_term = "Apple"
        browser_vm._selection_mode = True
        
        # Execute
        browser_vm.reset_browser_state()
        
        # Verify state reset
        assert browser_vm._current_recipes == []
        assert browser_vm._recipes_loaded is False
        assert browser_vm._category_filter is None
        assert browser_vm._sort_option == "A-Z"
        assert browser_vm._favorites_only is False
        assert browser_vm._search_term is None
        assert browser_vm._selection_mode is False
        assert isinstance(browser_vm._current_filter, RecipeFilterDTO)

    def test_get_available_categories(self, browser_vm):
        """Test getting available categories."""
        categories = browser_vm.get_available_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0  # Should have categories from config

    def test_get_available_sort_options(self, browser_vm):
        """Test getting available sort options."""
        sort_options = browser_vm.get_available_sort_options()
        
        assert isinstance(sort_options, list)
        assert len(sort_options) > 0  # Should have sort options from config
        assert "A-Z" in sort_options

    def test_validate_filter_dto_valid(self, browser_vm):
        """Test validating a valid filter DTO."""
        filter_dto = RecipeFilterDTO(
            recipe_category="Main Course",
            sort_by="recipe_name",
            sort_order="asc"
        )
        
        result = browser_vm.validate_filter_dto(filter_dto)
        
        assert result is True

    def test_validate_filter_dto_invalid(self, browser_vm):
        """Test validating an invalid filter DTO."""
        # Create an invalid filter DTO by mocking model_dump to return invalid data
        filter_dto = Mock()
        filter_dto.model_dump.return_value = {"sort_by": "invalid_field"}
        
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeFilterDTO.model_validate') as mock_validate:
            mock_validate.side_effect = ValueError("Invalid field")
            
            result = browser_vm.validate_filter_dto(filter_dto)
            
            assert result is False


# ── Test Error Handling ─────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelErrorHandling:
    """Test error handling in RecipeBrowserViewModel."""

    def test_service_initialization_failure(self, browser_vm):
        """Test handling of service initialization failure."""
        with patch.object(browser_vm, '_ensure_session', return_value=True), \
             patch('app.ui.view_models.recipe_browser_view_model.RecipeService', side_effect=Exception("Service init failed")):
            
            result = browser_vm._ensure_recipe_service()
            assert result is False

    def test_load_recipes_without_service(self, browser_vm):
        """Test loading recipes when service initialization fails."""
        with patch.object(browser_vm, '_ensure_recipe_service', return_value=False):
            result = browser_vm.load_recipes()
            assert result is False

    def test_fetch_and_emit_recipes_exception(self, browser_vm_with_service):
        """Test exception handling in _fetch_and_emit_recipes."""
        browser_vm_with_service._recipe_service.list_filtered.side_effect = Exception("Database error")
        
        result = browser_vm_with_service._fetch_and_emit_recipes(RecipeFilterDTO())
        
        assert result is False
        assert browser_vm_with_service._current_recipes == []
        assert browser_vm_with_service._recipes_loaded is False


# ── Test Integration ────────────────────────────────────────────────────────────────────────────────────────
class TestRecipeBrowserViewModelIntegration:
    """Test integration scenarios for RecipeBrowserViewModel."""

    def test_full_workflow_search_and_filter(self, browser_vm_with_service, sample_recipes):
        """Test complete workflow with search and filtering."""
        browser_vm_with_service._recipe_service.list_filtered.return_value = sample_recipes
        
        # Load initial recipes
        result1 = browser_vm_with_service.load_recipes()
        assert result1 is True
        
        # Update filters
        result2 = browser_vm_with_service.update_category_filter("Main Course")
        assert result2 is True
        
        # Update search
        result3 = browser_vm_with_service.update_search_term("Apple")
        assert result3 is True
        
        # Verify final state
        assert browser_vm_with_service._category_filter == "Main Course"
        assert browser_vm_with_service._search_term == "Apple"

    def test_selection_mode_workflow(self, browser_vm, sample_recipes):
        """Test selection mode workflow."""
        browser_vm._current_recipes = sample_recipes
        
        # Enable selection mode
        browser_vm.set_selection_mode(True)
        assert browser_vm.selection_mode is True
        
        # Select a recipe
        recipe = sample_recipes[0]
        browser_vm.handle_recipe_selection(recipe)  # Should not raise error
        
        # Disable selection mode
        browser_vm.set_selection_mode(False)
        assert browser_vm.selection_mode is False