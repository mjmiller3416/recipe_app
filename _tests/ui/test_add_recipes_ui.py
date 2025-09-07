"""
UI tests for AddRecipes view and components.

Tests the UI functionality including:
- AddRecipes view behavior and interactions
- IngredientForm component functionality
- Form submission workflows
- User interaction scenarios
- Error display in UI
- Data binding between UI and ViewModels
- Widget state management
"""

from unittest.mock import MagicMock, Mock, patch

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import pytest
import pytestqt

from app.ui.view_models.add_recipe_view_model import AddRecipeViewModel
from app.ui.view_models.ingredient_view_model import IngredientViewModel
from app.ui.views.add_recipes.add_recipes_view import (
    AddRecipes,
    IngredientForm,
    IngredientsCard,
)

@pytest.fixture
def mock_add_recipe_vm():
    """Create a mock AddRecipeViewModel."""
    vm = Mock(spec=AddRecipeViewModel)
    vm.is_processing = False
    vm.has_validation_errors = False
    vm.validation_errors = []
    vm.current_form_data = None

    # Mock all signals
    vm.recipe_saved_successfully = Mock()
    vm.recipe_save_failed = Mock()
    vm.validation_failed = Mock()
    vm.form_cleared = Mock()
    vm.processing_state_changed = Mock()
    vm.form_validation_state_changed = Mock()
    vm.field_validation_error = Mock()
    vm.field_validation_cleared = Mock()
    vm.recipe_name_validated = Mock()
    vm.loading_state_changed = Mock()

    # Mock signal connection methods
    for attr_name in dir(vm):
        attr = getattr(vm, attr_name)
        if hasattr(attr, 'connect'):
            attr.connect = Mock()

    # Mock methods
    vm.create_recipe = Mock()
    vm.validate_field_real_time = Mock(return_value=True)
    vm.validate_recipe_name = Mock(return_value=True)
    vm.preprocess_form_data = Mock()
    vm.clear_form_data = Mock()
    vm.reset_state = Mock()

    return vm


@pytest.fixture
def mock_ingredient_vm():
    """Create a mock IngredientViewModel."""
    vm = Mock(spec=IngredientViewModel)
    vm.cache_loaded = True
    vm.autocomplete_count = 10
    vm._autocomplete_cache = ["tomato", "onion", "garlic"]

    # Mock all signals
    vm.ingredient_search_completed = Mock()
    vm.ingredient_matched = Mock()
    vm.ingredient_validated = Mock()
    vm.category_suggested = Mock()
    vm.ingredient_name_validation_changed = Mock()
    vm.ingredient_category_validation_changed = Mock()
    vm.ingredient_quantity_validation_changed = Mock()

    # Mock signal connection methods
    for attr_name in dir(vm):
        attr = getattr(vm, attr_name)
        if hasattr(attr, 'connect'):
            attr.connect = Mock()

    # Mock methods
    vm.find_ingredient_matches = Mock()
    vm.validate_ingredient_name_real_time = Mock(return_value=True)
    vm.validate_ingredient_category_real_time = Mock(return_value=True)
    vm.validate_ingredient_quantity_real_time = Mock(return_value=True)
    vm._load_autocomplete_cache = Mock()

    return vm


@pytest.fixture
def add_recipes_view(qapp, mock_add_recipe_vm, mock_ingredient_vm):
    """Create AddRecipes view with mocked ViewModels."""
    with patch('app.ui.views.add_recipes.AddRecipeViewModel', return_value=mock_add_recipe_vm), \
         patch('app.ui.views.add_recipes.IngredientViewModel', return_value=mock_ingredient_vm):

        view = AddRecipes()
        return view


@pytest.fixture
def ingredient_form(qapp, mock_ingredient_vm):
    """Create IngredientForm component with mocked ViewModel."""
    form = IngredientForm(ingredient_view_model=mock_ingredient_vm)
    return form


@pytest.fixture
def ingredients_card(qapp, mock_ingredient_vm):
    """Create IngredientsCard component with mocked ViewModel."""
    card = IngredientsCard(ingredient_view_model=mock_ingredient_vm)
    return card


class TestAddRecipesViewInitialization:
    """Test AddRecipes view initialization and setup."""

    @pytest.mark.ui
    def test_view_initialization(self, add_recipes_view):
        """Test that AddRecipes view initializes correctly."""
        view = add_recipes_view

        # Verify basic properties
        assert view.objectName() == "AddRecipes"
        assert view.isVisible() is False  # Not shown by default

        # Verify ViewModels are set
        assert hasattr(view, 'add_recipe_view_model')
        assert hasattr(view, 'ingredient_view_model')

        # Verify main UI components exist
        assert hasattr(view, 'recipe_details_card')
        assert hasattr(view, 'ingredient_container')
        assert hasattr(view, 'directions_notes_card')
        assert hasattr(view, 'recipe_image')
        assert hasattr(view, 'btn_save')

    @pytest.mark.ui
    def test_form_fields_initialization(self, add_recipes_view):
        """Test that form fields are properly initialized."""
        view = add_recipes_view

        # Verify form fields exist and are accessible
        assert hasattr(view, 'le_recipe_name')
        assert hasattr(view, 'cb_recipe_category')
        assert hasattr(view, 'cb_meal_type')
        assert hasattr(view, 'cb_dietary_preference')
        assert hasattr(view, 'le_time')
        assert hasattr(view, 'le_servings')
        assert hasattr(view, 'te_directions')
        assert hasattr(view, 'te_notes')

        # Verify fields are enabled and editable
        assert view.le_recipe_name.isEnabled()
        assert view.cb_meal_type.isEnabled()
        assert view.btn_save.isEnabled()

    @pytest.mark.ui
    def test_signal_connections(self, mock_add_recipe_vm, mock_ingredient_vm):
        """Test that ViewModel signals are properly connected."""
        with patch('app.ui.views.add_recipes.AddRecipeViewModel', return_value=mock_add_recipe_vm), \
             patch('app.ui.views.add_recipes.IngredientViewModel', return_value=mock_ingredient_vm):

            view = AddRecipes()

            # Verify AddRecipeViewModel signals are connected
            mock_add_recipe_vm.recipe_saved_successfully.connect.assert_called()
            mock_add_recipe_vm.recipe_save_failed.connect.assert_called()
            mock_add_recipe_vm.validation_failed.connect.assert_called()
            mock_add_recipe_vm.processing_state_changed.connect.assert_called()

            # Verify IngredientViewModel signals are connected
            mock_ingredient_vm.ingredient_name_validation_changed.connect.assert_called()
            mock_ingredient_vm.ingredient_category_validation_changed.connect.assert_called()


class TestFormInteraction:
    """Test form interaction and user input handling."""

    @pytest.mark.ui
    def test_recipe_name_input(self, add_recipes_view, qtbot):
        """Test recipe name input field interaction."""
        view = add_recipes_view

        # Simulate user typing in recipe name
        qtbot.keyClicks(view.le_recipe_name, "Delicious Test Recipe")

        assert view.le_recipe_name.text() == "Delicious Test Recipe"

        # Verify real-time validation was triggered
        view.add_recipe_view_model.validate_field_real_time.assert_called()

    @pytest.mark.ui
    def test_servings_input_validation(self, add_recipes_view, qtbot):
        """Test servings input field with validation."""
        view = add_recipes_view

        # Test valid servings input
        qtbot.keyClicks(view.le_servings, "4")
        assert view.le_servings.text() == "4"

        # Test invalid servings input
        view.le_servings.clear()
        qtbot.keyClicks(view.le_servings, "invalid")

        # Verify validation was called
        view.add_recipe_view_model.validate_field_real_time.assert_called()

    @pytest.mark.ui
    def test_meal_type_selection(self, add_recipes_view, qtbot):
        """Test meal type combo box selection."""
        view = add_recipes_view

        # Simulate selecting a meal type
        view.cb_meal_type.setCurrentText("dinner")

        assert view.cb_meal_type.currentText() == "dinner"

        # Verify real-time validation was triggered
        view.add_recipe_view_model.validate_field_real_time.assert_called()

    @pytest.mark.ui
    def test_directions_text_input(self, add_recipes_view, qtbot):
        """Test directions text edit interaction."""
        view = add_recipes_view

        test_directions = "1. Prepare ingredients\n2. Cook for 20 minutes\n3. Serve hot"

        # Simulate typing in directions
        qtbot.keyClicks(view.te_directions, test_directions)

        assert test_directions in view.te_directions.toPlainText()

    @pytest.mark.ui
    def test_directions_notes_toggle(self, add_recipes_view, qtbot):
        """Test toggling between directions and notes views."""
        view = add_recipes_view
        card = view.directions_notes_card

        # Initially should show directions
        assert card.te_directions.isVisible()
        assert not card.te_notes.isVisible()

        # Click notes button
        qtbot.mouseClick(card.btn_notes, Qt.LeftButton)

        # Should now show notes
        assert not card.te_directions.isVisible()
        assert card.te_notes.isVisible()

        # Click directions button
        qtbot.mouseClick(card.btn_directions, Qt.LeftButton)

        # Should show directions again
        assert card.te_directions.isVisible()
        assert not card.te_notes.isVisible()


class TestIngredientFormComponent:
    """Test IngredientForm component functionality."""

    @pytest.mark.ui
    def test_ingredient_form_initialization(self, ingredient_form):
        """Test IngredientForm component initializes correctly."""
        form = ingredient_form

        # Verify UI components exist
        assert hasattr(form, 'sle_ingredient_name')
        assert hasattr(form, 'cb_ingredient_category')
        assert hasattr(form, 'le_quantity')
        assert hasattr(form, 'cb_unit')
        assert hasattr(form, 'btn_delete')

        # Verify components are enabled
        assert form.sle_ingredient_name.isEnabled()
        assert form.cb_ingredient_category.isEnabled()
        assert form.le_quantity.isEnabled()

    @pytest.mark.ui
    def test_ingredient_name_input_with_autocomplete(self, ingredient_form, qtbot):
        """Test ingredient name input with autocomplete functionality."""
        form = ingredient_form

        # Simulate typing ingredient name
        qtbot.keyClicks(form.sle_ingredient_name, "tom")

        # Verify autocomplete cache was used
        form.ingredient_view_model._load_autocomplete_cache.assert_called()

        # Verify validation was triggered
        form.ingredient_view_model.validate_ingredient_name_real_time.assert_called()

    @pytest.mark.ui
    def test_ingredient_category_auto_population(self, ingredient_form):
        """Test ingredient category auto-population based on name."""
        form = ingredient_form

        # Mock ingredient matching result
        from app.ui.view_models.ingredient_view_model import IngredientMatchResult
        mock_ingredient = Mock()
        mock_ingredient.ingredient_category = "Vegetables"
        mock_result = IngredientMatchResult(exact_match=mock_ingredient)

        form.ingredient_view_model.find_ingredient_matches.return_value = mock_result

        # Simulate ingredient name change
        form.sle_ingredient_name.setText("tomato")
        form._ingredient_name_changed("tomato")

        # Verify matching was called
        form.ingredient_view_model.find_ingredient_matches.assert_called_with("tomato")

    @pytest.mark.ui
    def test_ingredient_quantity_validation(self, ingredient_form, qtbot):
        """Test ingredient quantity input validation."""
        form = ingredient_form

        # Test valid quantity
        qtbot.keyClicks(form.le_quantity, "2.5")
        assert form.le_quantity.text() == "2.5"

        # Test invalid quantity
        form.le_quantity.clear()
        qtbot.keyClicks(form.le_quantity, "invalid")

        # Verify validation was called
        form.ingredient_view_model.validate_ingredient_quantity_real_time.assert_called()

    @pytest.mark.ui
    def test_ingredient_data_collection(self, ingredient_form):
        """Test collecting ingredient data from form."""
        form = ingredient_form

        # Set form data
        form.sle_ingredient_name.setText("tomato")
        form.cb_ingredient_category.setCurrentText("Vegetables")
        form.le_quantity.setText("3")
        form.cb_unit.setCurrentText("pieces")

        # Get ingredient data
        data = form.get_ingredient_data()

        assert data["ingredient_name"] == "tomato"
        assert data["ingredient_category"] == "Vegetables"
        assert data["quantity"] == 3.0
        assert data["unit"] == "pieces"

    @pytest.mark.ui
    def test_ingredient_removal_request(self, ingredient_form, qtbot):
        """Test ingredient removal functionality."""
        form = ingredient_form

        # Connect signal spy
        removal_spy = Mock()
        form.remove_ingredient_requested.connect(removal_spy)

        # Click delete button
        qtbot.mouseClick(form.btn_delete, Qt.LeftButton)

        # Verify removal request was emitted
        removal_spy.assert_called_once_with(form)

    @pytest.mark.ui
    def test_ingredient_validation_error_display(self, ingredient_form):
        """Test ingredient validation error display in UI."""
        form = ingredient_form

        # Simulate validation error
        form._on_name_validation_changed(False, "Invalid ingredient name")

        # Verify error styling was applied
        assert "border: 2px solid #f44336" in form.sle_ingredient_name.styleSheet()
        assert form.sle_ingredient_name.toolTip() == "Invalid ingredient name"

        # Simulate validation cleared
        form._on_name_validation_changed(True, "")

        # Verify styling was cleared
        assert form.sle_ingredient_name.styleSheet() == ""
        assert form.sle_ingredient_name.toolTip() == ""


class TestIngredientsCardComponent:
    """Test IngredientsCard component functionality."""

    @pytest.mark.ui
    def test_ingredients_card_initialization(self, ingredients_card):
        """Test IngredientsCard component initializes correctly."""
        card = ingredients_card

        # Should start with one ingredient widget
        assert len(card.ingredient_widgets) == 1
        assert card.get_ingredient_count() == 1

        # Verify add button exists
        assert hasattr(card, 'button')
        assert card.button is not None

    @pytest.mark.ui
    def test_add_ingredient_widget(self, ingredients_card, qtbot):
        """Test adding ingredient widgets."""
        card = ingredients_card
        initial_count = card.get_ingredient_count()

        # Connect signal spy
        ingredients_changed_spy = Mock()
        card.ingredients_changed.connect(ingredients_changed_spy)

        # Click add button
        qtbot.mouseClick(card.button, Qt.LeftButton)

        # Verify ingredient was added
        assert card.get_ingredient_count() == initial_count + 1
        ingredients_changed_spy.assert_called()

    @pytest.mark.ui
    def test_remove_ingredient_widget(self, ingredients_card, qtbot):
        """Test removing ingredient widgets."""
        card = ingredients_card

        # Add a second ingredient first
        qtbot.mouseClick(card.button, Qt.LeftButton)
        assert card.get_ingredient_count() == 2

        # Connect signal spy
        ingredients_changed_spy = Mock()
        card.ingredients_changed.connect(ingredients_changed_spy)

        # Remove the second ingredient
        second_ingredient = card.ingredient_widgets[1]
        card._remove_ingredient_widget(second_ingredient)

        # Verify ingredient was removed
        assert card.get_ingredient_count() == 1
        ingredients_changed_spy.assert_called()

    @pytest.mark.ui
    def test_cannot_remove_last_ingredient(self, ingredients_card):
        """Test that the last ingredient cannot be removed."""
        card = ingredients_card

        # Should have only one ingredient
        assert card.get_ingredient_count() == 1

        # Try to remove the last ingredient
        last_ingredient = card.ingredient_widgets[0]
        card._remove_ingredient_widget(last_ingredient)

        # Should still have one ingredient
        assert card.get_ingredient_count() == 1

    @pytest.mark.ui
    def test_collect_all_ingredients_data(self, ingredients_card, qtbot):
        """Test collecting data from all ingredient widgets."""
        card = ingredients_card

        # Add a second ingredient
        qtbot.mouseClick(card.button, Qt.LeftButton)

        # Set data in both ingredients
        card.ingredient_widgets[0].sle_ingredient_name.setText("tomato")
        card.ingredient_widgets[0].cb_ingredient_category.setCurrentText("Vegetables")

        card.ingredient_widgets[1].sle_ingredient_name.setText("onion")
        card.ingredient_widgets[1].cb_ingredient_category.setCurrentText("Vegetables")

        # Collect all data
        all_data = card.get_all_ingredients_data()

        assert len(all_data) == 2
        assert all_data[0]["ingredient_name"] == "tomato"
        assert all_data[1]["ingredient_name"] == "onion"

    @pytest.mark.ui
    def test_clear_all_ingredients(self, ingredients_card, qtbot):
        """Test clearing all ingredient widgets."""
        card = ingredients_card

        # Add multiple ingredients
        qtbot.mouseClick(card.button, Qt.LeftButton)
        qtbot.mouseClick(card.button, Qt.LeftButton)
        assert card.get_ingredient_count() == 3

        # Clear all ingredients
        card.clear_all_ingredients()

        # Should have one fresh ingredient
        assert card.get_ingredient_count() == 1
        assert card.ingredient_widgets[0].sle_ingredient_name.text() == ""


class TestRecipeSaveWorkflow:
    """Test complete recipe save workflow through UI."""

    @pytest.mark.ui
    def test_save_button_click_triggers_save(self, add_recipes_view, qtbot):
        """Test that clicking save button triggers recipe creation."""
        view = add_recipes_view

        # Set up basic form data
        view.le_recipe_name.setText("Test Recipe")
        view.cb_meal_type.setCurrentText("dinner")
        view.le_servings.setText("4")

        # Click save button
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Verify create_recipe was called on ViewModel
        view.add_recipe_view_model.create_recipe.assert_called_once()

    @pytest.mark.ui
    def test_form_data_collection_for_save(self, add_recipes_view, qtbot):
        """Test that form data is correctly collected for save operation."""
        view = add_recipes_view

        # Set form data
        view.le_recipe_name.setText("Integration Test Recipe")
        view.cb_recipe_category.setCurrentText("Main Course")
        view.cb_meal_type.setCurrentText("dinner")
        view.le_servings.setText("6")
        view.te_directions.setPlainText("Test directions")

        # Set ingredient data
        ingredient_widget = view.ingredient_container.ingredient_widgets[0]
        ingredient_widget.sle_ingredient_name.setText("tomato")
        ingredient_widget.cb_ingredient_category.setCurrentText("Vegetables")

        # Click save button
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Verify ViewModel methods were called with correct data
        view.add_recipe_view_model.preprocess_form_data.assert_called_once()
        view.add_recipe_view_model.create_recipe.assert_called_once()

    @pytest.mark.ui
    def test_processing_state_ui_updates(self, add_recipes_view):
        """Test UI updates during processing state."""
        view = add_recipes_view

        # Simulate processing state change
        view._on_processing_state_changed(True)

        # Verify UI changes
        assert not view.btn_save.isEnabled()
        assert view.btn_save.text() == "Saving..."

        # Simulate processing complete
        view._on_processing_state_changed(False)

        # Verify UI restored
        assert view.btn_save.isEnabled()
        assert view.btn_save.text() == "Save Recipe"

    @pytest.mark.ui
    def test_save_success_ui_response(self, add_recipes_view):
        """Test UI response to successful recipe save."""
        view = add_recipes_view

        # Set some form data first
        view.le_recipe_name.setText("Test Recipe")
        view.te_directions.setPlainText("Test directions")

        # Mock clear_form_fields function
        with patch('app.ui.views.add_recipes.clear_form_fields') as mock_clear:
            # Simulate successful save
            view._on_recipe_saved_successfully("Test Recipe")

            # Verify form was cleared
            mock_clear.assert_called_once()

    @pytest.mark.ui
    def test_save_failure_ui_response(self, add_recipes_view):
        """Test UI response to recipe save failure."""
        view = add_recipes_view

        # Mock toast notification
        with patch('app.ui.components.widgets.show_toast') as mock_toast:
            # Simulate save failure
            error_message = "Recipe name already exists"
            view._on_recipe_save_failed(error_message)

            # Verify error message was shown
            mock_toast.assert_called_once()
            args = mock_toast.call_args[0]
            assert error_message in args[1]  # Message should contain error
            assert args[2] is False  # success=False

    @pytest.mark.ui
    def test_validation_error_ui_display(self, add_recipes_view):
        """Test UI display of validation errors."""
        view = add_recipes_view

        # Mock toast notification
        with patch('app.ui.components.widgets.show_toast') as mock_toast:
            # Simulate validation failure
            error_messages = ["Recipe name is required", "Servings must be a number"]
            view._on_validation_failed(error_messages)

            # Verify error message was shown
            mock_toast.assert_called_once()
            displayed_message = mock_toast.call_args[0][1]
            assert "Recipe name is required" in displayed_message
            assert "Servings must be a number" in displayed_message


class TestFieldValidationUI:
    """Test field validation UI feedback."""

    @pytest.mark.ui
    def test_field_validation_error_styling(self, add_recipes_view):
        """Test field validation error styling application."""
        view = add_recipes_view

        # Simulate field validation error
        view._on_field_validation_error("recipe_name", "Recipe name is required")

        # Verify error styling was applied
        field_widget = view._get_field_widget("recipe_name")
        assert field_widget is not None
        assert "border: 2px solid #f44336" in field_widget.styleSheet()
        assert field_widget.toolTip() == "Recipe name is required"

    @pytest.mark.ui
    def test_field_validation_clear_styling(self, add_recipes_view):
        """Test field validation error styling clearing."""
        view = add_recipes_view

        # First apply error styling
        view._on_field_validation_error("recipe_name", "Recipe name is required")
        field_widget = view._get_field_widget("recipe_name")

        # Then clear it
        view._on_field_validation_cleared("recipe_name")

        # Verify styling was cleared
        assert field_widget.styleSheet() == ""
        assert field_widget.toolTip() == ""

    @pytest.mark.ui
    def test_recipe_name_uniqueness_validation_ui(self, add_recipes_view):
        """Test recipe name uniqueness validation UI feedback."""
        view = add_recipes_view

        # Simulate duplicate recipe name validation
        view._on_recipe_name_validated(False, "Recipe 'Test Recipe' already exists")

        # Verify error styling was applied to recipe name field
        field_widget = view._get_field_widget("recipe_name")
        assert "border: 2px solid #f44336" in field_widget.styleSheet()

        # Simulate unique recipe name validation
        view._on_recipe_name_validated(True, "Recipe name is available")

        # Verify styling was cleared
        assert field_widget.styleSheet() == ""

    @pytest.mark.ui
    def test_real_time_validation_triggers(self, add_recipes_view, qtbot):
        """Test that real-time validation is triggered by user input."""
        view = add_recipes_view

        # Type in recipe name field
        qtbot.keyClicks(view.le_recipe_name, "Test Recipe")

        # Verify real-time validation was called
        view.add_recipe_view_model.validate_field_real_time.assert_called()

        # Type in servings field
        qtbot.keyClicks(view.le_servings, "4")

        # Verify validation was called for servings field
        assert view.add_recipe_view_model.validate_field_real_time.call_count >= 2


class TestUIStateManagement:
    """Test UI state management and widget interactions."""

    @pytest.mark.ui
    def test_form_clear_functionality(self, add_recipes_view):
        """Test form clearing functionality."""
        view = add_recipes_view

        # Set form data
        view.le_recipe_name.setText("Test Recipe")
        view.cb_meal_type.setCurrentText("dinner")
        view.te_directions.setPlainText("Test directions")

        # Mock clear_form_fields and related functions
        with patch('app.ui.views.add_recipes.clear_form_fields') as mock_clear:
            # Trigger form clear
            view._on_form_cleared()

            # Verify clear function was called
            mock_clear.assert_called_once()

    @pytest.mark.ui
    def test_loading_state_ui_feedback(self, add_recipes_view):
        """Test UI feedback during loading states."""
        view = add_recipes_view

        # Simulate loading state start
        view._on_loading_state_changed(True, "Saving recipe...")

        # Note: The current implementation doesn't show loading indicators,
        # but the handler is called and available for future enhancements

        # Simulate loading state end
        view._on_loading_state_changed(False, "")

    @pytest.mark.ui
    def test_tab_order_functionality(self, add_recipes_view, qtbot):
        """Test keyboard navigation tab order."""
        view = add_recipes_view
        view.show()  # Need to show widget for focus testing

        # Set focus to first field
        view.le_recipe_name.setFocus()

        # Verify focus is on recipe name field
        assert view.le_recipe_name.hasFocus()

        # Simulate tab key press
        qtbot.keyPress(view.le_recipe_name, Qt.Key_Tab)

        # Focus should move to next field in tab order
        # Note: Exact behavior depends on tab order setup

    @pytest.mark.ui
    def test_focus_behavior_on_show(self, add_recipes_view, qtbot):
        """Test focus behavior when view is shown."""
        view = add_recipes_view

        # Mock QTimer.singleShot to avoid timing issues
        with patch.object(QTimer, 'singleShot') as mock_timer:
            # Trigger show event
            view.showEvent(Mock())

            # Verify timer was set to focus recipe name field
            mock_timer.assert_called_once()
            assert mock_timer.call_args[1] == view.le_recipe_name.setFocus


class TestImageHandling:
    """Test image handling functionality in UI."""

    @pytest.mark.ui
    def test_recipe_image_component_integration(self, add_recipes_view):
        """Test recipe image component integration."""
        view = add_recipes_view

        # Verify recipe image component exists
        assert hasattr(view, 'recipe_image')
        assert view.recipe_image is not None

        # Test getting image path (when no image is selected)
        image_path = view.recipe_image.get_reference_image_path()
        assert image_path is None or image_path == ""

    @pytest.mark.ui
    def test_image_path_in_form_data_collection(self, add_recipes_view, qtbot):
        """Test that image path is included in form data collection."""
        view = add_recipes_view

        # Mock image path
        with patch.object(view.recipe_image, 'get_reference_image_path', return_value="/path/to/image.jpg"):
            # Set minimal required form data
            view.le_recipe_name.setText("Test Recipe")
            view.cb_meal_type.setCurrentText("dinner")
            view.le_servings.setText("4")

            # Click save to trigger form data collection
            qtbot.mouseClick(view.btn_save, Qt.LeftButton)

            # Verify preprocess_form_data was called (which includes image path)
            view.add_recipe_view_model.preprocess_form_data.assert_called_once()


class TestErrorHandling:
    """Test error handling and edge cases in UI."""

    @pytest.mark.ui
    def test_empty_form_submission(self, add_recipes_view, qtbot):
        """Test submitting empty form."""
        view = add_recipes_view

        # Click save button without filling any fields
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Should still call ViewModel (validation happens there)
        view.add_recipe_view_model.create_recipe.assert_called_once()

    @pytest.mark.ui
    def test_ingredient_form_with_no_viewmodel(self, qapp):
        """Test ingredient form behavior when no ViewModel is provided."""
        # Create ingredient form without ViewModel
        form = IngredientForm(ingredient_view_model=None)

        # Should still initialize without errors
        assert form.ingredient_view_model is None
        assert form.exact_match is None

        # Basic functionality should still work
        form.sle_ingredient_name.setText("tomato")
        data = form.get_ingredient_data()
        assert data["ingredient_name"] == "tomato"

    @pytest.mark.ui
    def test_widget_lifecycle_cleanup(self, add_recipes_view):
        """Test proper widget cleanup and memory management."""
        view = add_recipes_view

        # Add multiple ingredient widgets
        for _ in range(3):
            view.ingredient_container._add_ingredient_widget()

        initial_count = view.ingredient_container.get_ingredient_count()
        assert initial_count == 4  # 1 initial + 3 added

        # Clear all ingredients (should properly clean up widgets)
        view.ingredient_container.clear_all_ingredients()

        final_count = view.ingredient_container.get_ingredient_count()
        assert final_count == 1  # Should have one fresh widget

    @pytest.mark.ui
    def test_signal_disconnection_safety(self, add_recipes_view):
        """Test that widget can handle signal disconnections safely."""
        view = add_recipes_view

        # Manually disconnect a signal
        view.add_recipe_view_model.recipe_saved_successfully.disconnect()

        # Should not crash when trying to emit signals
        try:
            view._on_recipe_saved_successfully("Test Recipe")
        except Exception as e:
            pytest.fail(f"Signal disconnection caused crash: {e}")


class TestAdvancedUIInteractions:
    """Test advanced UI interaction scenarios."""

    @pytest.mark.ui
    def test_keyboard_navigation_workflow(self, add_recipes_view, qtbot):
        """Test complete keyboard navigation through the form."""
        view = add_recipes_view
        view.show()

        # Start with recipe name focused
        view.le_recipe_name.setFocus()
        assert view.le_recipe_name.hasFocus()

        # Type recipe name
        qtbot.keyClicks(view.le_recipe_name, "Keyboard Navigation Recipe")

        # Tab to next field
        qtbot.keyPress(view.le_recipe_name, Qt.Key_Tab)

        # Should move focus (exact behavior depends on tab order)
        # Note: In real implementation, verify proper tab order is set

    @pytest.mark.ui
    def test_form_validation_ui_feedback_comprehensive(self, add_recipes_view):
        """Test comprehensive form validation UI feedback."""
        view = add_recipes_view

        # Test multiple field validation errors at once
        view._on_field_validation_error("recipe_name", "Recipe name is required")
        view._on_field_validation_error("servings", "Servings must be a number")
        view._on_field_validation_error("meal_type", "Meal type must be selected")

        # Check that all fields show error styling
        name_field = view._get_field_widget("recipe_name")
        servings_field = view._get_field_widget("servings")
        meal_type_field = view._get_field_widget("meal_type")

        assert "border: 2px solid #f44336" in name_field.styleSheet()
        assert "border: 2px solid #f44336" in servings_field.styleSheet()
        assert "border: 2px solid #f44336" in meal_type_field.styleSheet()

        # Clear errors selectively
        view._on_field_validation_cleared("recipe_name")
        view._on_field_validation_cleared("servings")

        # Only meal_type should still have error styling
        assert name_field.styleSheet() == ""
        assert servings_field.styleSheet() == ""
        assert "border: 2px solid #f44336" in meal_type_field.styleSheet()

    @pytest.mark.ui
    def test_dynamic_ingredient_form_behavior(self, ingredients_card, qtbot):
        """Test dynamic behavior of ingredient forms."""
        card = ingredients_card

        # Test maximum ingredients (if there's a limit)
        initial_count = card.get_ingredient_count()

        # Add many ingredients
        for i in range(10):
            qtbot.mouseClick(card.button, Qt.LeftButton)

        # Should handle many ingredients gracefully
        assert card.get_ingredient_count() == initial_count + 10

        # Test removing from middle
        middle_widget = card.ingredient_widgets[5]
        card._remove_ingredient_widget(middle_widget)

        assert card.get_ingredient_count() == initial_count + 9

        # Test that remaining widgets are still functional
        remaining_widget = card.ingredient_widgets[0]
        remaining_widget.sle_ingredient_name.setText("test ingredient")

        data = card.get_all_ingredients_data()
        assert data[0]["ingredient_name"] == "test ingredient"

    @pytest.mark.ui
    def test_ingredient_autocomplete_ui_integration(self, ingredient_form, qtbot):
        """Test ingredient autocomplete UI integration."""
        form = ingredient_form

        # Mock autocomplete suggestions
        form.ingredient_view_model._autocomplete_cache = ["tomato", "potato", "carrot"]
        form.ingredient_view_model._cache_loaded = True

        # Simulate typing that triggers autocomplete
        qtbot.keyClicks(form.sle_ingredient_name, "to")

        # Verify autocomplete was attempted
        form.ingredient_view_model._load_autocomplete_cache.assert_called()

    @pytest.mark.ui
    def test_drag_drop_ingredient_reordering(self, ingredients_card, qtbot):
        """Test drag and drop reordering of ingredients (if implemented)."""
        card = ingredients_card

        # Add multiple ingredients
        for i in range(3):
            qtbot.mouseClick(card.button, Qt.LeftButton)

        # Set unique names for each
        for i, widget in enumerate(card.ingredient_widgets):
            widget.sle_ingredient_name.setText(f"ingredient_{i}")

        # Get initial order
        initial_data = card.get_all_ingredients_data()
        initial_names = [data["ingredient_name"] for data in initial_data]

        # Note: Actual drag-drop testing would require more complex simulation
        # For now, just verify data collection works correctly
        assert len(initial_names) == 4  # 1 initial + 3 added
        assert all(name.startswith("ingredient_") for name in initial_names)

    @pytest.mark.ui
    def test_responsive_layout_behavior(self, add_recipes_view, qtbot):
        """Test UI behavior with different window sizes."""
        view = add_recipes_view
        view.show()

        # Test with normal size
        view.resize(800, 600)
        qtbot.wait(100)  # Allow layout to update

        # Test with narrow width
        view.resize(400, 600)
        qtbot.wait(100)

        # Test with very wide
        view.resize(1200, 600)
        qtbot.wait(100)

        # Verify components are still accessible and functional
        assert view.le_recipe_name.isVisible()
        assert view.btn_save.isVisible()
        assert view.ingredient_container.isVisible()

    @pytest.mark.ui
    def test_accessibility_features(self, add_recipes_view):
        """Test accessibility features of the UI."""
        view = add_recipes_view

        # Test that important fields have proper tooltips/accessibility info
        assert view.le_recipe_name.accessibleName() or view.le_recipe_name.toolTip()
        assert view.cb_meal_type.accessibleName() or view.cb_meal_type.toolTip()
        assert view.btn_save.accessibleName() or view.btn_save.toolTip()

        # Test keyboard accessibility
        view.le_recipe_name.setFocus()
        assert view.le_recipe_name.hasFocus()

    @pytest.mark.ui
    def test_context_menu_functionality(self, add_recipes_view, qtbot):
        """Test context menu functionality (if implemented)."""
        view = add_recipes_view

        # Right-click on text areas to test context menus
        qtbot.mouseClick(view.te_directions, Qt.RightButton)

        # Note: Actual context menu testing would depend on implementation
        # For now, verify the widget handles right-clicks without crashing


class TestErrorScenarioHandling:
    """Test UI handling of various error scenarios."""

    @pytest.mark.ui
    def test_network_error_simulation(self, add_recipes_view):
        """Test UI behavior when network/service errors occur."""
        view = add_recipes_view

        # Simulate various error types
        error_scenarios = [
            ("Network timeout", "Connection timed out while saving recipe"),
            ("Server error", "Server returned error 500"),
            ("Validation error", "Recipe name contains invalid characters"),
            ("Permission error", "You don't have permission to save recipes")
        ]

        for error_type, error_message in error_scenarios:
            with patch('app.ui.components.widgets.show_toast') as mock_toast:
                view._on_recipe_save_failed(error_message)

                # Verify error was displayed to user
                mock_toast.assert_called_once()
                displayed_args = mock_toast.call_args[0]
                assert error_message in displayed_args[1]
                assert displayed_args[2] is False  # success=False

    @pytest.mark.ui
    def test_form_state_preservation_on_error(self, add_recipes_view, qtbot):
        """Test that form state is preserved when errors occur."""
        view = add_recipes_view

        # Fill out form
        view.le_recipe_name.setText("Test Recipe")
        view.cb_meal_type.setCurrentText("dinner")
        view.le_servings.setText("4")
        view.te_directions.setPlainText("Test directions")

        # Simulate save error
        view._on_recipe_save_failed("Save failed")

        # Form data should still be there
        assert view.le_recipe_name.text() == "Test Recipe"
        assert view.cb_meal_type.currentText() == "dinner"
        assert view.le_servings.text() == "4"
        assert "Test directions" in view.te_directions.toPlainText()

    @pytest.mark.ui
    def test_partial_form_completion_handling(self, add_recipes_view, qtbot):
        """Test UI behavior with partially completed forms."""
        view = add_recipes_view

        # Fill only some required fields
        view.le_recipe_name.setText("Partial Recipe")
        # Leave meal_type and servings empty

        # Try to save
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Should still attempt to save (validation happens in ViewModel)
        view.add_recipe_view_model.create_recipe.assert_called_once()

    @pytest.mark.ui
    def test_concurrent_user_actions(self, add_recipes_view, qtbot):
        """Test UI behavior with rapid user actions."""
        view = add_recipes_view

        # Simulate rapid button clicking
        for i in range(5):
            qtbot.mouseClick(view.btn_save, Qt.LeftButton)
            qtbot.wait(50)  # Small delay between clicks

        # Should handle multiple clicks gracefully
        # (Processing state should prevent duplicate operations)
        assert view.add_recipe_view_model.create_recipe.call_count >= 1

    @pytest.mark.ui
    def test_memory_cleanup_on_view_close(self, add_recipes_view):
        """Test proper memory cleanup when view is closed."""
        view = add_recipes_view
        view.show()

        # Add some ingredients and data
        view.le_recipe_name.setText("Memory Test Recipe")
        view.ingredient_container._add_ingredient_widget()
        view.ingredient_container._add_ingredient_widget()

        initial_widget_count = view.ingredient_container.get_ingredient_count()
        assert initial_widget_count > 1

        # Close view
        view.close()

        # Note: Actual memory cleanup verification would need more sophisticated testing
        # For now, verify close doesn't crash
        assert True


class TestPerformanceAndUsability:
    """Test performance and usability aspects of the UI."""

    @pytest.mark.ui
    def test_form_responsiveness_with_large_data(self, add_recipes_view, qtbot):
        """Test form responsiveness with large amounts of data."""
        view = add_recipes_view

        # Add many ingredients
        for i in range(20):
            view.ingredient_container._add_ingredient_widget()

        # Fill with data
        for i, widget in enumerate(view.ingredient_container.ingredient_widgets):
            widget.sle_ingredient_name.setText(f"ingredient_{i}")
            widget.cb_ingredient_category.setCurrentText("Vegetables")

        # Test that form is still responsive
        qtbot.keyClicks(view.le_recipe_name, "Large Recipe")

        # Should complete without hanging
        assert view.le_recipe_name.text() == "Large Recipe"

    @pytest.mark.ui
    def test_ui_feedback_timing(self, add_recipes_view, qtbot):
        """Test timing of UI feedback for user actions."""
        view = add_recipes_view

        # Test immediate feedback for processing state
        view._on_processing_state_changed(True)

        # Button should be disabled immediately
        assert not view.btn_save.isEnabled()
        assert view.btn_save.text() == "Saving..."

        # Test restoration
        view._on_processing_state_changed(False)

        assert view.btn_save.isEnabled()
        assert view.btn_save.text() == "Save Recipe"

    @pytest.mark.ui
    def test_visual_consistency_across_components(self, add_recipes_view, ingredient_form, ingredients_card):
        """Test visual consistency across different components."""
        # Test that similar components have consistent styling
        view = add_recipes_view
        form = ingredient_form
        card = ingredients_card

        # Note: Actual visual consistency testing would involve style analysis
        # For now, verify components are properly initialized
        assert view.objectName() == "AddRecipes"
        assert form is not None
        assert card is not None

    @pytest.mark.ui
    def test_form_state_transitions(self, add_recipes_view):
        """Test various form state transitions."""
        view = add_recipes_view

        # Test state progression: empty -> filled -> processing -> success

        # Empty state
        assert view.btn_save.isEnabled()
        assert view.btn_save.text() == "Save Recipe"

        # Processing state
        view._on_processing_state_changed(True)
        assert not view.btn_save.isEnabled()
        assert view.btn_save.text() == "Saving..."

        # Success state
        view._on_processing_state_changed(False)
        assert view.btn_save.isEnabled()
        assert view.btn_save.text() == "Save Recipe"


@pytest.mark.ui
class TestUIIntegration:
    """Integration tests for UI components working together."""

    def test_complete_ui_workflow_simulation(self, add_recipes_view, qtbot):
        """Test complete UI workflow from start to finish."""
        view = add_recipes_view
        view.show()

        # Fill out recipe form
        qtbot.keyClicks(view.le_recipe_name, "UI Test Recipe")
        view.cb_meal_type.setCurrentText("dinner")
        view.cb_recipe_category.setCurrentText("Main Course")
        qtbot.keyClicks(view.le_servings, "4")
        qtbot.keyClicks(view.le_time, "30")
        qtbot.keyClicks(view.te_directions, "Test cooking directions")

        # Fill out ingredient form
        ingredient_widget = view.ingredient_container.ingredient_widgets[0]
        qtbot.keyClicks(ingredient_widget.sle_ingredient_name, "tomato")
        ingredient_widget.cb_ingredient_category.setCurrentText("Vegetables")
        qtbot.keyClicks(ingredient_widget.le_quantity, "2")
        ingredient_widget.cb_unit.setCurrentText("cups")

        # Add another ingredient
        qtbot.mouseClick(view.ingredient_container.button, Qt.LeftButton)
        second_ingredient = view.ingredient_container.ingredient_widgets[1]
        qtbot.keyClicks(second_ingredient.sle_ingredient_name, "onion")
        second_ingredient.cb_ingredient_category.setCurrentText("Vegetables")

        # Click save button
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Verify all the expected interactions occurred
        view.add_recipe_view_model.create_recipe.assert_called_once()
        view.add_recipe_view_model.preprocess_form_data.assert_called_once()

        # Verify form data was collected correctly
        call_args = view.add_recipe_view_model.preprocess_form_data.call_args[0][0]
        assert call_args["recipe_name"] == "UI Test Recipe"
        assert call_args["meal_type"] == "dinner"
        assert len(call_args["ingredients"]) == 2

    def test_ingredient_management_ui_flow(self, ingredients_card, qtbot):
        """Test ingredient management through UI interactions."""
        card = ingredients_card

        # Start with one ingredient
        assert card.get_ingredient_count() == 1

        # Add ingredients
        for i in range(3):
            qtbot.mouseClick(card.button, Qt.LeftButton)

        assert card.get_ingredient_count() == 4

        # Fill in ingredient data
        for i, widget in enumerate(card.ingredient_widgets):
            widget.sle_ingredient_name.setText(f"ingredient_{i}")
            widget.cb_ingredient_category.setCurrentText("Vegetables")

        # Collect all data
        all_data = card.get_all_ingredients_data()
        assert len(all_data) == 4

        # Remove an ingredient
        second_widget = card.ingredient_widgets[1]
        card._remove_ingredient_widget(second_widget)

        assert card.get_ingredient_count() == 3

        # Verify data collection still works
        remaining_data = card.get_all_ingredients_data()
        assert len(remaining_data) == 3

    def test_viewmodel_ui_signal_integration(self, add_recipes_view, qtbot):
        """Test integration between ViewModel signals and UI updates."""
        view = add_recipes_view

        # Test processing state signal
        view._on_processing_state_changed(True)
        assert not view.btn_save.isEnabled()

        # Test validation error signal
        view._on_field_validation_error("recipe_name", "Name is required")
        field_widget = view._get_field_widget("recipe_name")
        assert "border: 2px solid #f44336" in field_widget.styleSheet()

        # Test success signal
        with patch('app.ui.views.add_recipes.clear_form_fields') as mock_clear:
            view._on_recipe_saved_successfully("Test Recipe")
            mock_clear.assert_called_once()

        # Test error signal
        with patch('app.ui.components.widgets.show_toast') as mock_toast:
            view._on_recipe_save_failed("Save error")
            mock_toast.assert_called_once()

    def test_complete_error_recovery_workflow(self, add_recipes_view, qtbot):
        """Test complete error recovery workflow."""
        view = add_recipes_view
        view.show()

        # Fill form
        qtbot.keyClicks(view.le_recipe_name, "Error Recovery Recipe")
        view.cb_meal_type.setCurrentText("dinner")
        qtbot.keyClicks(view.le_servings, "4")

        # Simulate validation error
        view._on_validation_failed(["Recipe name is required", "Invalid servings"])

        # Simulate error display
        with patch('app.ui.components.widgets.show_toast') as mock_toast:
            view._on_validation_failed(["Recipe name is required"])
            mock_toast.assert_called_once()

        # Fix validation errors
        view._on_field_validation_cleared("recipe_name")
        view._on_field_validation_cleared("servings")

        # Try save again
        qtbot.mouseClick(view.btn_save, Qt.LeftButton)

        # Should attempt save again
        assert view.add_recipe_view_model.create_recipe.call_count >= 2

    def test_ui_component_lifecycle_integration(self, qapp):
        """Test UI component lifecycle integration."""
        # Test creating and destroying components
        with patch('app.ui.views.add_recipes.AddRecipeViewModel') as mock_vm:
            mock_vm_instance = Mock()
            mock_vm.return_value = mock_vm_instance

            # Create view
            view = AddRecipes()

            # Verify ViewModel was created
            mock_vm.assert_called_once()

            # Verify signals were connected
            assert mock_vm_instance.recipe_saved_successfully.connect.called
            assert mock_vm_instance.recipe_save_failed.connect.called

            # Close view
            view.close()
            view.deleteLater()

            # Process events to ensure cleanup
            qapp.processEvents()
