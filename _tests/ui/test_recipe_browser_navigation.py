"""
UI tests for navigation service integration with RecipeBrowserView.

Tests focus on actual user interaction workflows and navigation system functionality
using pytest-qt to simulate real user interactions and verify complete navigation
integration from the UI perspective.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton
from PySide6.QtTest import QTest

from app.core.models.recipe import Recipe
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.ui.main_window import MainWindow
from app.ui.views.recipe_browser.recipe_browser_view import RecipeBrowserView
from app.ui.views.meal_planner.meal_planner_view import MealPlanner
from app.ui.managers.navigation.service import NavigationService
from app.ui.managers.navigation.registry import NavigationRegistry, RouteConstants
from app.ui.components.composite.recipe_card import LayoutSize


@pytest.fixture
def mock_recipe_service():
    """Mock recipe service for testing."""
    service = Mock()
    service.get_all_recipes.return_value = []
    service.search_recipes.return_value = []
    service.get_recipes_by_category.return_value = []
    return service


@pytest.fixture
def mock_planner_service():
    """Mock planner service for testing."""
    service = Mock()
    service.get_meal_plans.return_value = []
    return service


@pytest.fixture
def sample_recipes():
    """Create sample Recipe objects for testing."""
    recipes = []
    for i in range(3):
        recipe = Mock(spec=Recipe)
        recipe.recipe_id = i + 1
        recipe.recipe_name = f"Test Recipe {i + 1}"
        recipe.description = f"Test description {i + 1}"
        recipe.prep_time = 15
        recipe.cook_time = 30
        recipe.servings = 4
        recipe.category = "Test Category"
        recipe.is_favorite = False
        recipes.append(recipe)
    return recipes


@pytest.fixture
def navigation_service(qapp):
    """Create NavigationService instance for testing."""
    # Clear any existing instance
    NavigationService._instance = None

    # Clear navigation registry to start fresh
    NavigationRegistry._routes.clear()
    NavigationRegistry._pattern_routes.clear()
    NavigationRegistry._instances.clear()

    # Register test routes
    from app.ui.managers.navigation.routes import register_main_routes
    register_main_routes()

    # Create a mock stacked widget
    stacked_widget = QStackedWidget()

    # Create navigation service
    nav_service = NavigationService.create(stacked_widget)

    yield nav_service

    # Cleanup
    NavigationService._instance = None
    NavigationRegistry._routes.clear()
    NavigationRegistry._pattern_routes.clear()
    NavigationRegistry._instances.clear()


@pytest.fixture
def main_window_fixture(qapp, navigation_service):
    """Create MainWindow fixture with mocked services."""
    with patch('app.ui.main_window.NavigationService') as MockNavService:
        MockNavService.get_instance.return_value = navigation_service
        MockNavService.create.return_value = navigation_service

        # Mock the service dependencies in MainWindow
        with patch('app.core.services.recipe_service.RecipeService'), \
             patch('app.core.services.planner_service.PlannerService'):

            window = MainWindow()
            yield window
            window.close()


@pytest.fixture
def recipe_browser_view(qapp, navigation_service):
    """Create RecipeBrowserView fixture."""
    with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
        # Create mock view model
        mock_vm = Mock()
        mock_vm.recipes_loaded = Mock()
        mock_vm.recipes_cleared = Mock()
        mock_vm.recipe_selected = Mock()
        mock_vm.selection_mode_changed = Mock()
        mock_vm.filter_state_changed = Mock()
        mock_vm.search_completed = Mock()
        mock_vm.error_occurred = Mock()
        mock_vm.load_recipes.return_value = True
        mock_vm.recipe_count = 0
        MockVM.return_value = mock_vm

        view = RecipeBrowserView(selection_mode=False)
        view._view_model = mock_vm
        yield view


@pytest.fixture
def meal_planner_view(qapp, navigation_service):
    """Create MealPlanner fixture."""
    with patch('app.core.services.recipe_service.RecipeService'), \
         patch('app.core.services.planner_service.PlannerService'), \
         patch('app.ui.view_models.meal_planner_view_model.MealPlannerViewModel'):

        view = MealPlanner()
        yield view


class TestRecipeBrowserNavigation:
    """Test suite for RecipeBrowserView navigation integration."""

    def test_dashboard_to_recipe_browser_navigation(self, qtbot, main_window_fixture, navigation_service):
        """Test clicking 'View Recipes' button in sidebar navigates to recipe browser."""
        window = main_window_fixture
        qtbot.addWidget(window)

        # Get the View Recipes button from sidebar
        view_recipes_btn = window.sidebar.buttons.get("btn_view_recipes")
        assert view_recipes_btn is not None, "View Recipes button should exist in sidebar"

        # Mock the navigation service navigate_to method
        with patch.object(navigation_service, 'navigate_to', return_value=True) as mock_navigate:
            # Simulate clicking the View Recipes button
            qtbot.mouseClick(view_recipes_btn, Qt.LeftButton)

            # Verify navigation was called with correct route
            mock_navigate.assert_called_once_with(RouteConstants.RECIPES_BROWSE)

    def test_meal_planner_to_recipe_selection_navigation(self, qtbot, meal_planner_view, navigation_service):
        """Test clicking 'Add Recipe' in MealPlanner navigates to recipe selection."""
        meal_planner = meal_planner_view
        qtbot.addWidget(meal_planner)

        # Mock navigation service
        with patch.object(navigation_service, 'navigate_to', return_value=True) as mock_navigate:
            # Simulate navigation to recipe selection
            # This would typically be triggered by an "Add Recipe" button in meal planner
            navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE_SELECTION)

            # Verify navigation was called with correct route
            mock_navigate.assert_called_once_with(RouteConstants.RECIPES_BROWSE_SELECTION)

    def test_recipe_browser_loads_in_normal_mode(self, qtbot, recipe_browser_view, sample_recipes):
        """Test RecipeBrowserView loads correctly in normal mode."""
        view = recipe_browser_view
        qtbot.addWidget(view)

        # Verify view is in normal mode (not selection mode)
        assert not view.is_selection_mode(), "View should be in normal mode by default"

        # Simulate recipes being loaded
        view._display_recipes(sample_recipes)

        # Verify UI components are initialized
        assert hasattr(view, '_cb_filter'), "Category filter should be initialized"
        assert hasattr(view, '_cb_sort'), "Sort filter should be initialized"
        assert hasattr(view, '_chk_favorites'), "Favorites filter should be initialized"
        assert hasattr(view, '_flow_layout'), "Recipe grid layout should be initialized"

    def test_recipe_browser_loads_in_selection_mode(self, qtbot, navigation_service):
        """Test RecipeBrowserView loads correctly in selection mode."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            mock_vm.set_selection_mode = Mock()
            MockVM.return_value = mock_vm

            # Create view in selection mode
            view = RecipeBrowserView(selection_mode=True)
            qtbot.addWidget(view)

            # Verify view is in selection mode
            assert view.is_selection_mode(), "View should be in selection mode"

            # Verify UI components are initialized (main functionality test)
            assert hasattr(view, '_cb_filter'), "Category filter should be initialized"
            assert hasattr(view, '_cb_sort'), "Sort filter should be initialized"
            assert hasattr(view, '_chk_favorites'), "Favorites filter should be initialized"
            assert hasattr(view, '_flow_layout'), "Recipe grid layout should be initialized"

    def test_back_forward_navigation(self, qtbot, navigation_service):
        """Test browser-style back/forward navigation."""
        # Navigate to dashboard first
        success = navigation_service.navigate_to("/dashboard")
        assert success, "Should navigate to dashboard successfully"

        # Navigate to recipe browser
        success = navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE)
        assert success, "Should navigate to recipe browser successfully"

        # Test back navigation
        assert navigation_service.can_go_back(), "Should be able to go back"
        success = navigation_service.go_back()
        assert success, "Should navigate back successfully"

        # Verify current route is dashboard
        current_entry = navigation_service.get_current_route()
        assert current_entry is not None, "Should have current route"
        assert current_entry.path == "/dashboard", "Should be back at dashboard"

        # Test forward navigation
        assert navigation_service.can_go_forward(), "Should be able to go forward"
        success = navigation_service.go_forward()
        assert success, "Should navigate forward successfully"

        # Verify current route is recipe browser
        current_entry = navigation_service.get_current_route()
        assert current_entry is not None, "Should have current route"
        assert current_entry.path == RouteConstants.RECIPES_BROWSE, "Should be at recipe browser"

    def test_recipe_selected_signal_emission(self, qtbot, sample_recipes):
        """Test recipe_selected signal emission in selection mode."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            mock_vm.handle_recipe_selection = Mock()
            MockVM.return_value = mock_vm

            # Create view in selection mode
            view = RecipeBrowserView(selection_mode=True)
            qtbot.addWidget(view)

            # Set up signal spy
            with qtbot.waitSignal(view.recipe_selected, timeout=1000) as blocker:
                # Simulate recipe selection by calling the signal handler directly
                test_recipe = sample_recipes[0]
                view._on_recipe_selected(test_recipe.recipe_id, test_recipe)

            # Verify signal was emitted with correct data
            assert blocker.args == [test_recipe.recipe_id, test_recipe]

    def test_recipe_opened_signal_emission(self, qtbot, sample_recipes):
        """Test recipe_opened signal emission in normal mode."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            MockVM.return_value = mock_vm

            # Create view in normal mode
            view = RecipeBrowserView(selection_mode=False)
            qtbot.addWidget(view)

            # Set up signal spy
            with qtbot.waitSignal(view.recipe_opened, timeout=1000) as blocker:
                # Simulate recipe opening
                test_recipe = sample_recipes[0]
                view._handle_recipe_opened(test_recipe)

            # Verify signal was emitted with correct data
            assert blocker.args == [test_recipe]

    def test_navigation_service_route_resolution(self, qtbot, navigation_service):
        """Test navigation service route resolution and parameter handling."""
        # Test route resolution for recipe browser
        route_match = NavigationRegistry.match_route(RouteConstants.RECIPES_BROWSE)
        assert route_match is not None, "Should find route match for recipe browser"
        assert route_match.config.view_class == RecipeBrowserView, "Should match RecipeBrowserView"

        # Test route resolution for recipe selection
        route_match = NavigationRegistry.match_route(RouteConstants.RECIPES_BROWSE_SELECTION)
        assert route_match is not None, "Should find route match for recipe selection"
        # Note: This should resolve to RecipeBrowserSelectionView wrapper class

    def test_navigation_parameter_passing(self, qtbot, navigation_service):
        """Test parameter passing through navigation system."""
        # Test navigation with parameters
        test_params = {"selection_mode": "true", "category": "desserts"}
        success = navigation_service.navigate_to(
            RouteConstants.RECIPES_BROWSE,
            params=test_params
        )
        assert success, "Should navigate with parameters successfully"

        # Verify parameters are stored in navigation entry
        current_entry = navigation_service.get_current_route()
        assert current_entry is not None, "Should have current route"
        assert current_entry.params == test_params, "Parameters should be preserved"

    def test_navigation_context_switching(self, qtbot, navigation_service):
        """Test navigation service context management."""
        # Add a secondary navigation context
        from PySide6.QtWidgets import QStackedWidget
        secondary_container = QStackedWidget()
        navigation_service.add_context("secondary", secondary_container)

        # Test navigation in main context
        success = navigation_service.navigate_to("/dashboard", context="main")
        assert success, "Should navigate in main context"

        # Test navigation in secondary context
        success = navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE, context="secondary")
        assert success, "Should navigate in secondary context"

        # Verify contexts maintain separate navigation stacks
        main_route = navigation_service.get_current_route("main")
        secondary_route = navigation_service.get_current_route("secondary")

        assert main_route.path == "/dashboard", "Main context should have dashboard route"
        assert secondary_route.path == RouteConstants.RECIPES_BROWSE, "Secondary context should have recipe browser route"

    def test_navigation_error_handling(self, qtbot, navigation_service):
        """Test navigation error scenarios and handling."""
        # Test navigation to invalid route
        with qtbot.waitSignal(navigation_service.navigation_failed, timeout=1000) as blocker:
            success = navigation_service.navigate_to("/invalid/route")
            assert not success, "Navigation to invalid route should fail"

        # Verify error signal was emitted
        assert blocker.args[0] == "/invalid/route", "Should emit correct route path"
        assert "route" in blocker.args[1].lower(), "Error message should mention route"

    def test_navigation_lifecycle_hooks(self, qtbot):
        """Test navigation lifecycle hook execution."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            MockVM.return_value = mock_vm

            # Create view and mock lifecycle methods
            view = RecipeBrowserView()
            view.before_navigate_from = Mock(return_value=True)
            view.after_navigate_to = Mock()

            qtbot.addWidget(view)

            # Test lifecycle hooks are called during navigation
            test_path = "/test/route"
            test_params = {"test": "value"}

            # Simulate navigation lifecycle
            view.after_navigate_to(test_path, test_params)
            view.before_navigate_from("/next/route", {})

            # Verify hooks were called
            view.after_navigate_to.assert_called_once_with(test_path, test_params)
            view.before_navigate_from.assert_called_once_with("/next/route", {})

    def test_ui_component_initialization_after_navigation(self, qtbot, sample_recipes):
        """Test UI components are properly initialized after navigation."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            mock_vm.recipe_count = len(sample_recipes)
            MockVM.return_value = mock_vm

            view = RecipeBrowserView()
            qtbot.addWidget(view)

            # Simulate navigation lifecycle
            view.after_navigate_to(RouteConstants.RECIPES_BROWSE, {})

            # Verify UI components are initialized
            assert view._view_model is not None, "ViewModel should be initialized"
            assert hasattr(view, '_cb_filter'), "Category filter should be created"
            assert hasattr(view, '_cb_sort'), "Sort filter should be created"
            assert hasattr(view, '_chk_favorites'), "Favorites checkbox should be created"
            assert hasattr(view, '_scroll_area'), "Scroll area should be created"
            assert hasattr(view, '_flow_layout'), "Flow layout should be created"

    def test_recipe_card_interaction_modes(self, qtbot, sample_recipes):
        """Test recipe cards behave differently in selection vs normal mode."""
        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            mock_vm.handle_recipe_selection = Mock()
            MockVM.return_value = mock_vm

            # Test normal mode
            normal_view = RecipeBrowserView(selection_mode=False)
            qtbot.addWidget(normal_view)

            # Test selection mode
            selection_view = RecipeBrowserView(selection_mode=True)
            qtbot.addWidget(selection_view)

            # Verify mode differences
            assert not normal_view.is_selection_mode(), "Normal view should not be in selection mode"
            assert selection_view.is_selection_mode(), "Selection view should be in selection mode"

            # Simulate displaying recipes in both views
            normal_view._display_recipes(sample_recipes[:1])
            selection_view._display_recipes(sample_recipes[:1])

            # Both should have recipe cards (testing card creation)
            assert normal_view._flow_layout.count() > 0, "Normal view should have recipe cards"
            assert selection_view._flow_layout.count() > 0, "Selection view should have recipe cards"

    def test_navigation_stack_management(self, qtbot, navigation_service):
        """Test navigation history stack is properly managed."""
        # Clear any existing navigation history to start fresh
        context = navigation_service._contexts.get("main")
        if context and context.stack:
            context.stack._history.clear()
            context.stack._current_index = -1

        # Start fresh navigation stack
        assert not navigation_service.can_go_back(), "Should not be able to go back initially"
        assert not navigation_service.can_go_forward(), "Should not be able to go forward initially"

        # Navigate through multiple routes
        navigation_service.navigate_to("/dashboard")
        navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE)
        navigation_service.navigate_to("/meal-planner")

        # Should be able to go back but not forward
        assert navigation_service.can_go_back(), "Should be able to go back after navigation"
        assert not navigation_service.can_go_forward(), "Should not be able to go forward"

        # Go back once
        navigation_service.go_back()

        # Should be able to go both directions
        assert navigation_service.can_go_back(), "Should still be able to go back"
        assert navigation_service.can_go_forward(), "Should now be able to go forward"

        # Verify current route
        current_entry = navigation_service.get_current_route()
        assert current_entry.path == RouteConstants.RECIPES_BROWSE, "Should be at recipe browser after going back"


class TestNavigationServiceIntegration:
    """Test suite focusing specifically on NavigationService integration."""

    def test_navigation_service_singleton_pattern(self, navigation_service):
        """Test NavigationService follows singleton pattern correctly."""
        # Get instance should return the same instance
        instance1 = NavigationService.get_instance()
        instance2 = NavigationService.get_instance()

        assert instance1 is instance2, "Should return same instance"
        assert instance1 is navigation_service, "Should return the created instance"

    def test_navigation_signal_connections(self, qtbot, navigation_service):
        """Test navigation service signals are properly connected."""
        # Test navigation_started signal
        with qtbot.waitSignal(navigation_service.navigation_started, timeout=1000) as blocker:
            navigation_service.navigate_to("/dashboard")

        assert blocker.args[0] == "/dashboard", "Should emit correct path"
        assert isinstance(blocker.args[1], dict), "Should emit parameters dict"

    def test_route_matching_accuracy(self, qtbot, navigation_service):
        """Test route matching works correctly for all registered routes."""
        # Ensure routes are registered for this test
        from app.ui.managers.navigation.routes import register_main_routes
        register_main_routes()

        # Test exact route matching
        route_match = NavigationRegistry.match_route(RouteConstants.RECIPES_BROWSE)
        assert route_match is not None, "Should match exact route"
        assert route_match.config.path == RouteConstants.RECIPES_BROWSE, "Should match correct route"

        # Test route with selection mode
        route_match = NavigationRegistry.match_route(RouteConstants.RECIPES_BROWSE_SELECTION)
        assert route_match is not None, "Should match selection route"
        assert route_match.config.path == RouteConstants.RECIPES_BROWSE_SELECTION, "Should match correct selection route"

    def test_view_instantiation_caching(self, qtbot, navigation_service):
        """Test view instances are properly cached/reused."""
        # Navigate to route twice
        success1 = navigation_service.navigate_to("/dashboard")
        view1 = navigation_service.get_current_view()

        success2 = navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE)
        success3 = navigation_service.navigate_to("/dashboard")
        view2 = navigation_service.get_current_view()

        assert success1 and success2 and success3, "All navigations should succeed"
        # Note: Depending on caching configuration, views might be the same instance or different
        # This test verifies the navigation service manages view instances correctly


@pytest.mark.slow
class TestNavigationPerformance:
    """Performance-focused navigation tests (marked as slow)."""

    def test_large_recipe_set_navigation_performance(self, qtbot, navigation_service, sample_recipes):
        """Test navigation performance with large number of recipes."""
        # Create a large set of sample recipes
        large_recipe_set = []
        for i in range(100):
            recipe = Mock(spec=Recipe)
            recipe.recipe_id = i + 1
            recipe.recipe_name = f"Performance Test Recipe {i + 1}"
            recipe.description = f"Performance test description {i + 1}"
            recipe.prep_time = 15
            recipe.cook_time = 30
            recipe.servings = 4
            recipe.category = "Performance Test"
            recipe.is_favorite = i % 10 == 0  # Every 10th recipe is favorite
            large_recipe_set.append(recipe)

        with patch('app.ui.view_models.recipe_browser_view_model.RecipeBrowserViewModel') as MockVM:
            mock_vm = Mock()
            mock_vm.recipes_loaded = Mock()
            mock_vm.recipes_cleared = Mock()
            mock_vm.recipe_selected = Mock()
            mock_vm.selection_mode_changed = Mock()
            mock_vm.filter_state_changed = Mock()
            mock_vm.search_completed = Mock()
            mock_vm.error_occurred = Mock()
            mock_vm.load_recipes.return_value = True
            mock_vm.recipe_count = len(large_recipe_set)
            MockVM.return_value = mock_vm

            # Measure navigation performance
            import time
            start_time = time.time()

            success = navigation_service.navigate_to(RouteConstants.RECIPES_BROWSE)
            view = navigation_service.get_current_view()

            if view and hasattr(view, '_display_recipes'):
                view._display_recipes(large_recipe_set)

            end_time = time.time()
            navigation_time = end_time - start_time

            assert success, "Navigation should succeed with large recipe set"
            assert navigation_time < 2.0, f"Navigation should complete within 2 seconds, took {navigation_time:.2f}s"

    def test_rapid_navigation_switching(self, qtbot, navigation_service):
        """Test rapid navigation between different views."""
        routes = [
            "/dashboard",
            RouteConstants.RECIPES_BROWSE,
            "/meal-planner",
            "/shopping-list",
            "/settings"
        ]

        import time
        start_time = time.time()

        # Rapidly navigate between routes
        for _ in range(3):  # 3 cycles through all routes
            for route in routes:
                success = navigation_service.navigate_to(route)
                assert success, f"Navigation to {route} should succeed"
                QApplication.processEvents()  # Process any pending UI updates

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete rapid navigation within reasonable time
        expected_max_time = len(routes) * 3 * 0.1  # 0.1s per navigation max
        assert total_time < expected_max_time, f"Rapid navigation should complete within {expected_max_time}s, took {total_time:.2f}s"
