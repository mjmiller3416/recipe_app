"""Integration tests for RecipeBrowserView functionality.

Tests the complete integration between:
- RecipeBrowserView and RecipeBrowserViewModel
- View lifecycle and navigation
- Signal/slot connections and data flow
- Recipe display and interaction
- Filter and sort functionality
- Selection mode vs normal mode behavior
- Error handling integration
- UI component integration
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget
import pytest

from app.config import RECIPE_CATEGORIES, SORT_OPTIONS
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.components.composite.recipe_card import LayoutSize
from app.ui.view_models.recipe_browser_vm import RecipeBrowserViewModel
from app.ui.views.recipe_browser.view import RecipeBrowserView


# ── Test Data Factories ─────────────────────────────────────────────────────────────────────────────
def create_test_recipe(
    recipe_id: int = 1,
    name: str = "Test Recipe",
    category: str = "Main Course",
    is_favorite: bool = False,
    total_time: int = 30,
    servings: int = 4
) -> Recipe:
    """Create a test Recipe instance."""
    recipe = Recipe()
    recipe.id = recipe_id
    recipe.recipe_name = name
    recipe.recipe_category = category
    recipe.is_favorite = is_favorite
    recipe.total_time = total_time
    recipe.servings = servings
    recipe.directions = f"Instructions for {name}"
    recipe.notes = f"Notes for {name}"
    return recipe


def create_test_recipes(count: int = 5) -> List[Recipe]:
    """Create a list of test Recipe instances."""
    recipes = []
    categories = ["Main Course", "Appetizers", "Desserts", "Side Dishes"]

    for i in range(count):
        recipe = create_test_recipe(
            recipe_id=i + 1,
            name=f"Test Recipe {i + 1}",
            category=categories[i % len(categories)],
            is_favorite=i % 2 == 0,  # Every other recipe is favorite
            total_time=30 + (i * 10),
            servings=2 + i
        )
        recipes.append(recipe)

    return recipes


# ── Fixture Definitions ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_recipe_service():
    """Mock RecipeService for testing."""
    service = Mock(spec=RecipeService)
    service.list_filtered.return_value = create_test_recipes(3)
    service.toggle_favorite.return_value = create_test_recipe(1, "Favorited Recipe", is_favorite=True)
    return service


@pytest.fixture
def mock_view_model(db_session):
    """Mock RecipeBrowserViewModel for isolated view testing."""
    with patch('app.ui.views.recipe_browser_view.RecipeBrowserViewModel') as MockViewModel:
        vm = Mock(spec=RecipeBrowserViewModel)

        # Configure ViewModel signals as proper Qt signals
        vm.recipes_loaded = Signal(list)
        vm.recipes_cleared = Signal()
        vm.recipe_selected = Signal(int, object)
        vm.selection_mode_changed = Signal(bool)
        vm.filter_state_changed = Signal(object)
        vm.search_completed = Signal(int)
        vm.error_occurred = Signal(dict)

        # Configure default behavior
        vm.load_recipes.return_value = True
        vm.set_selection_mode.return_value = None
        vm.current_recipes = create_test_recipes(3)
        vm.recipe_count = 3
        vm.selection_mode = False

        MockViewModel.return_value = vm
        yield vm


@pytest.fixture
def browser_view_normal(qapp, mock_view_model):
    """Create RecipeBrowserView in normal browsing mode."""
    view = RecipeBrowserView(
        parent=None,
        selection_mode=False,
        card_size=LayoutSize.MEDIUM
    )
    yield view
    view.deleteLater()


@pytest.fixture
def browser_view_selection(qapp, mock_view_model):
    """Create RecipeBrowserView in selection mode."""
    view = RecipeBrowserView(
        parent=None,
        selection_mode=True,
        card_size=LayoutSize.SMALL
    )
    yield view
    view.deleteLater()


@pytest.fixture
def real_view_model(db_session):
    """Create real RecipeBrowserViewModel with test database session."""
    return RecipeBrowserViewModel(db_session)


@pytest.fixture
def integrated_browser_view(qapp, real_view_model):
    """Create RecipeBrowserView with real ViewModel for full integration testing."""
    view = RecipeBrowserView(parent=None, selection_mode=False)

    # Replace the view's ViewModel with our test one
    view._view_model = real_view_model

    # Mock the service to return test data
    with patch.object(real_view_model, '_recipe_service') as mock_service:
        mock_service.list_filtered.return_value = create_test_recipes(3)
        yield view, real_view_model, mock_service

    view.deleteLater()


# ── Normal Browsing Mode Tests ──────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewNormalMode:
    """Test RecipeBrowserView in normal browsing mode."""

    def test_initialization_normal_mode(self, browser_view_normal, mock_view_model):
        """Test view initialization in normal browsing mode."""
        view = browser_view_normal

        # Verify view properties
        assert not view.is_selection_mode()
        assert view._card_size == LayoutSize.MEDIUM
        assert view.objectName() == "RecipeBrowserView"

        # Verify ViewModel configuration
        mock_view_model.set_selection_mode.assert_called_once_with(False)
        mock_view_model.load_recipes.assert_called_once()

    def test_recipe_loading_and_display(self, browser_view_normal, mock_view_model):
        """Test recipe loading and display functionality."""
        view = browser_view_normal
        test_recipes = create_test_recipes(3)

        # Simulate ViewModel emitting recipes_loaded signal
        view._on_recipes_loaded(test_recipes)

        # Process Qt events to ensure UI updates
        QApplication.processEvents()

        # Verify recipes are displayed
        assert view.is_recipes_loaded()
        assert view._flow_layout.count() == 3

        # Verify layout geometry updates
        assert hasattr(view, '_scroll_container')
        assert hasattr(view, '_scroll_area')

    def test_category_filtering(self, browser_view_normal, mock_view_model):
        """Test category filter functionality."""
        view = browser_view_normal

        # Test category filter change
        view._on_category_filter_changed("Main Course")

        # Verify ViewModel was called with correct category
        mock_view_model.update_category_filter.assert_called_with("Main Course")

    def test_sort_option_changes(self, browser_view_normal, mock_view_model):
        """Test sort option functionality."""
        view = browser_view_normal

        # Test sort option change
        view._on_sort_option_changed("Z-A")

        # Verify ViewModel was called with correct sort option
        mock_view_model.update_sort_option.assert_called_with("Z-A")

    def test_favorites_filter(self, browser_view_normal, mock_view_model):
        """Test favorites filter functionality."""
        view = browser_view_normal

        # Test favorites filter enabled
        view._on_favorites_filter_changed(Qt.Checked.value)

        # Verify ViewModel was called with correct state
        mock_view_model.update_favorites_filter.assert_called_with(True)

        # Test favorites filter disabled
        view._on_favorites_filter_changed(Qt.Unchecked.value)
        mock_view_model.update_favorites_filter.assert_called_with(False)

    def test_recipe_card_click_normal_mode(self, browser_view_normal, mock_view_model):
        """Test recipe card clicks in normal browsing mode."""
        view = browser_view_normal
        test_recipe = create_test_recipe(1, "Clicked Recipe")

        # Mock signal emission
        with patch.object(view, 'recipe_opened') as mock_signal:
            view._handle_recipe_opened(test_recipe)

            # Verify recipe_opened signal was emitted
            mock_signal.emit.assert_called_once_with(test_recipe)

    def test_public_interface_methods(self, browser_view_normal, mock_view_model):
        """Test public interface methods work correctly."""
        view = browser_view_normal

        # Test refresh_recipes
        view.refresh_recipes()
        mock_view_model.refresh_recipes.assert_called_once()

        # Test clear_recipes
        view.clear_recipes()
        mock_view_model.clear_recipes.assert_called_once()

        # Test search_recipes
        view.search_recipes("test search")
        mock_view_model.search_recipes.assert_called_with("test search")

        # Test clear_search
        view.clear_search()
        mock_view_model.clear_search.assert_called_once()

        # Test get_current_recipe_count
        mock_view_model.recipe_count = 5
        assert view.get_current_recipe_count() == 5


# ── Selection Mode Tests ────────────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewSelectionMode:
    """Test RecipeBrowserView in selection mode."""

    def test_initialization_selection_mode(self, browser_view_selection, mock_view_model):
        """Test view initialization in selection mode."""
        view = browser_view_selection

        # Verify view properties
        assert view.is_selection_mode()
        assert view._card_size == LayoutSize.SMALL

        # Verify ViewModel configuration
        mock_view_model.set_selection_mode.assert_called_once_with(True)

    def test_recipe_selection_workflow(self, browser_view_selection, mock_view_model):
        """Test recipe selection workflow in selection mode."""
        view = browser_view_selection
        test_recipe = create_test_recipe(1, "Selected Recipe")

        # Test recipe selection handling
        view._handle_recipe_selection(test_recipe)

        # Verify ViewModel handles selection
        mock_view_model.handle_recipe_selection.assert_called_once_with(test_recipe)

    def test_recipe_card_click_selection_mode(self, browser_view_selection, mock_view_model):
        """Test recipe card clicks emit selection signals."""
        view = browser_view_selection
        test_recipe = create_test_recipe(1, "Selected Recipe")

        # Mock the recipe_selected signal
        with patch.object(view, 'recipe_selected') as mock_signal:
            # Simulate ViewModel emitting recipe selection
            view._on_recipe_selected(1, test_recipe)

            # Verify recipe_selected signal was emitted
            mock_signal.emit.assert_called_once_with(1, test_recipe)

    def test_selection_mode_toggle(self, browser_view_selection, mock_view_model):
        """Test selection mode toggling functionality."""
        view = browser_view_selection

        # Test mode change from ViewModel
        view._on_selection_mode_changed(False)

        # Verify view state updated
        assert not view._selection_mode

        # Test set_selection_mode public method
        view.set_selection_mode(True)
        mock_view_model.set_selection_mode.assert_called_with(True)


# ── Navigation Integration Tests ────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewNavigation:
    """Test navigation lifecycle and route handling."""

    def test_after_navigate_to(self, browser_view_normal, mock_view_model):
        """Test after_navigate_to lifecycle method."""
        view = browser_view_normal

        # Reset recipes loaded state
        view._recipes_loaded = False

        # Test navigation
        view.after_navigate_to("/recipes", {"filter": "main-course"})

        # Verify ViewModel initialization and recipe loading
        assert mock_view_model.load_recipes.call_count >= 1

    def test_before_navigate_from(self, browser_view_normal, mock_view_model):
        """Test before_navigate_from lifecycle method."""
        view = browser_view_normal

        # Test navigation away
        result = view.before_navigate_from("/dashboard", {})

        # Should return True to allow navigation
        assert result is True

    def test_route_parameter_handling(self, browser_view_normal, mock_view_model):
        """Test route parameter handling."""
        view = browser_view_normal

        # Test selection mode parameter handling
        view.on_route_changed("/recipes", {"selection_mode": "true"})

        # Verify selection mode was set
        mock_view_model.set_selection_mode.assert_called_with(True)
        assert view._selection_mode is True

        # Test disabling selection mode
        view.on_route_changed("/recipes", {"selection_mode": "false"})
        mock_view_model.set_selection_mode.assert_called_with(False)

    def test_navigation_signals(self, browser_view_normal, mock_view_model):
        """Test navigation signal emissions."""
        view = browser_view_normal

        # Test recipe_opened signal for navigation
        test_recipe = create_test_recipe(1, "Navigation Recipe")

        with patch.object(view, 'recipe_opened') as mock_signal:
            view._handle_recipe_opened(test_recipe)
            mock_signal.emit.assert_called_once_with(test_recipe)


# ── ViewModel Integration Tests ─────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewModelIntegration:
    """Test integration with RecipeBrowserViewModel."""

    def test_viewmodel_signal_connections(self, browser_view_normal, mock_view_model):
        """Test ViewModel signal connections are established."""
        view = browser_view_normal

        # Verify signal connections were attempted
        # Note: Mock signals don't actually connect, but we can verify setup
        assert view._view_model is mock_view_model

    def test_viewmodel_error_handling(self, browser_view_normal, mock_view_model):
        """Test ViewModel error handling integration."""
        view = browser_view_normal
        error_info = {"message": "Test error", "code": "test_error"}

        # Simulate ViewModel error
        view._on_view_model_error(error_info)

        # Error handling should not crash the view
        assert view._view_model is mock_view_model

    def test_filter_state_synchronization(self, browser_view_normal, mock_view_model):
        """Test filter state synchronization with ViewModel."""
        view = browser_view_normal

        # Create test filter DTO
        filter_dto = RecipeFilterDTO(
            recipe_category="Main Course",
            sort_by="recipe_name",
            sort_order="asc",
            favorites_only=True
        )

        # Simulate ViewModel filter state change
        view._on_filter_state_changed(filter_dto)

        # Should not crash and should handle the state change
        assert view._view_model is mock_view_model

    def test_search_completion_handling(self, browser_view_normal, mock_view_model):
        """Test search completion signal handling."""
        view = browser_view_normal

        # Simulate search completion
        view._on_search_completed(5)

        # Should handle search completion without issues
        assert view._view_model is mock_view_model


# ── UI Component Integration Tests ──────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewUIIntegration:
    """Test UI component integration and interaction."""

    def test_filter_controls_setup(self, browser_view_normal, mock_view_model):
        """Test filter controls are properly set up."""
        view = browser_view_normal

        # Verify filter controls exist
        assert hasattr(view, '_cb_filter')
        assert hasattr(view, '_cb_sort')
        assert hasattr(view, '_chk_favorites')

        # Verify controls have correct object names
        assert view._cb_filter.objectName() == "CategoryFilter"
        assert view._cb_sort.objectName() == "SortFilter"
        assert view._chk_favorites.objectName() == "FavoritesFilter"

    def test_recipe_grid_layout(self, browser_view_normal, mock_view_model):
        """Test recipe grid layout functionality."""
        view = browser_view_normal

        # Verify grid components exist
        assert hasattr(view, '_scroll_area')
        assert hasattr(view, '_scroll_container')
        assert hasattr(view, '_flow_layout')

        # Test recipe display
        test_recipes = create_test_recipes(2)
        view._display_recipes(test_recipes)

        # Process events
        QApplication.processEvents()

        # Verify recipes were added to layout
        assert view._flow_layout.count() == 2

    def test_recipe_card_creation_and_interaction(self, browser_view_normal, mock_view_model):
        """Test recipe card creation and interaction."""
        view = browser_view_normal
        test_recipes = create_test_recipes(1)

        # Display recipes to create cards
        view._display_recipes(test_recipes)
        QApplication.processEvents()

        # Verify card was created
        assert view._flow_layout.count() == 1

        # Test clearing cards
        view._clear_recipe_cards()
        QApplication.processEvents()

        # Verify cards were cleared
        assert view._flow_layout.count() == 0

    def test_layout_updates_and_geometry(self, browser_view_normal, mock_view_model):
        """Test layout updates and geometry calculations."""
        view = browser_view_normal

        # Test layout geometry update
        view._update_layout_geometry()

        # Should complete without errors
        assert hasattr(view, '_scroll_container')
        assert hasattr(view, '_scroll_area')

    def test_show_and_resize_events(self, browser_view_normal, mock_view_model):
        """Test Qt event handling for show and resize."""
        view = browser_view_normal

        # Test show event
        from PySide6.QtGui import QShowEvent
        show_event = QShowEvent()
        view.showEvent(show_event)

        # Test resize event
        from PySide6.QtGui import QResizeEvent
        from PySide6.QtCore import QSize
        resize_event = QResizeEvent(QSize(800, 600), QSize(600, 400))
        view.resizeEvent(resize_event)

        # Events should be handled without errors
        assert view._view_model is mock_view_model


# ── Full Integration Tests ──────────────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.slow
class TestRecipeBrowserViewFullIntegration:
    """Test full integration with real ViewModel and mocked services."""

    def test_complete_recipe_loading_flow(self, integrated_browser_view):
        """Test complete recipe loading flow with real ViewModel."""
        view, view_model, mock_service = integrated_browser_view

        # Test recipe loading
        success = view_model.load_recipes()
        assert success

        # Verify service was called
        mock_service.list_filtered.assert_called_once()

    def test_filter_integration_workflow(self, integrated_browser_view):
        """Test complete filter workflow integration."""
        view, view_model, mock_service = integrated_browser_view

        # Test category filter
        success = view_model.update_category_filter("Main Course")
        assert success

        # Test sort option
        success = view_model.update_sort_option("Z-A")
        assert success

        # Test favorites filter
        success = view_model.update_favorites_filter(True)
        assert success

        # Verify multiple service calls occurred
        assert mock_service.list_filtered.call_count >= 3

    def test_selection_mode_integration(self, integrated_browser_view):
        """Test selection mode integration with real ViewModel."""
        view, view_model, mock_service = integrated_browser_view

        # Test selection mode toggle
        view_model.set_selection_mode(True)
        assert view_model.selection_mode is True

        # Test recipe selection
        test_recipe = create_test_recipe(1, "Selected Recipe")
        view_model.handle_recipe_selection(test_recipe)

        # Should handle selection without errors
        assert view_model.selection_mode is True

    def test_search_integration_workflow(self, integrated_browser_view):
        """Test search functionality integration."""
        view, view_model, mock_service = integrated_browser_view

        # Test search
        success = view_model.search_recipes("test search")
        assert success

        # Test search clear
        success = view_model.clear_search()
        assert success

        # Verify service calls occurred
        assert mock_service.list_filtered.call_count >= 2

    def test_error_handling_integration(self, integrated_browser_view):
        """Test error handling across the integration."""
        view, view_model, mock_service = integrated_browser_view

        # Mock service error
        mock_service.list_filtered.side_effect = Exception("Service error")

        # Test that errors are handled gracefully
        success = view_model.load_recipes()
        assert not success

        # View should still be functional
        assert view_model is not None
        assert view._view_model is not None


# ── Edge Cases and Error Scenarios ──────────────────────────────────────────────────────────────────
@pytest.mark.integration
@pytest.mark.ui
class TestRecipeBrowserViewEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_recipe_list_handling(self, browser_view_normal, mock_view_model):
        """Test handling of empty recipe lists."""
        view = browser_view_normal

        # Test empty recipe list
        view._on_recipes_loaded([])
        QApplication.processEvents()

        # Should handle empty list gracefully
        assert view._flow_layout.count() == 0
        assert view.is_recipes_loaded()

    def test_none_recipe_handling(self, browser_view_normal, mock_view_model):
        """Test handling of None recipe objects."""
        view = browser_view_normal

        # Test None recipe in selection
        view._handle_recipe_selection(None)

        # Should not call ViewModel with None
        mock_view_model.handle_recipe_selection.assert_not_called()

        # Test None recipe in opening
        view._handle_recipe_opened(None)

        # Should handle gracefully without signal emission

    def test_invalid_filter_parameters(self, browser_view_normal, mock_view_model):
        """Test handling of invalid filter parameters."""
        view = browser_view_normal

        # Test invalid category
        view._on_category_filter_changed("")
        mock_view_model.update_category_filter.assert_called_with("")

        # Test invalid sort option
        view._on_sort_option_changed("InvalidSort")
        mock_view_model.update_sort_option.assert_called_with("InvalidSort")

    def test_view_without_viewmodel(self, qapp):
        """Test view behavior when ViewModel is None."""
        view = RecipeBrowserView(parent=None)
        view._view_model = None

        try:
            # These should not crash even with None ViewModel
            view._on_category_filter_changed("Test")
            view._on_sort_option_changed("A-Z")
            view._on_favorites_filter_changed(Qt.Checked.value)
            view.refresh_recipes()
            view.clear_recipes()

            # Should return 0 for recipe count
            assert view.get_current_recipe_count() == 0

        finally:
            view.deleteLater()

    def test_cleanup_and_destruction(self, browser_view_normal, mock_view_model):
        """Test proper cleanup when view is destroyed."""
        view = browser_view_normal

        # Test manual cleanup
        view.__del__()

        # Should handle cleanup gracefully
        # Note: Actual cleanup testing is limited in unit tests
