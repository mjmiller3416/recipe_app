"""
Unit tests for AddRecipeViewModel.

Tests the add recipe view model including:
- Recipe form data validation and business logic
- Ingredient addition and management workflows
- Form state management and real-time validation
- User input processing and sanitization
- MVVM pattern implementation for recipe creation
- DTO construction and data transformation
- Error handling scenarios and edge cases
- Service coordination and session management
"""

from unittest.mock import MagicMock, Mock, call, patch

from PySide6.QtCore import QObject
import pytest

from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.recipe_service import DuplicateRecipeError, RecipeSaveError
from app.ui.view_models.add_recipe_view_model import AddRecipeViewModel, RecipeFormData
from app.ui.view_models.base_view_model import BaseValidationResult

@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_recipe_service():
    """Create a mock RecipeService."""
    service = Mock()
    service.create_recipe_with_ingredients = Mock()
    service.update_recipe_reference_image_path = Mock()
    service.recipe_repo = Mock()
    service.recipe_repo.recipe_exists = Mock(return_value=False)
    return service


@pytest.fixture
def mock_ingredient_service():
    """Create a mock IngredientService."""
    service = Mock()
    service.search = Mock(return_value=[])
    service.list_distinct_names = Mock(return_value=["tomato", "onion", "garlic"])
    return service


@pytest.fixture
def add_recipe_vm(mock_session):
    """Create AddRecipeViewModel instance with mocked dependencies."""
    with patch('app.ui.view_models.add_recipe_view_model.RecipeService') as mock_recipe_svc, \
         patch('app.ui.view_models.add_recipe_view_model.IngredientService') as mock_ingredient_svc:
        
        vm = AddRecipeViewModel(mock_session)
        vm.recipe_service = Mock()
        vm.ingredient_service = Mock()
        return vm


@pytest.fixture
def sample_form_data():
    """Create sample form data for testing."""
    form_data = RecipeFormData()
    form_data.recipe_name = "Test Recipe"
    form_data.recipe_category = "Main Course"
    form_data.meal_type = "dinner"
    form_data.dietary_preference = "vegetarian"
    form_data.total_time = "30"
    form_data.servings = "4"
    form_data.directions = "Mix ingredients and cook."
    form_data.notes = "Test notes"
    form_data.ingredients = [
        {
            "ingredient_name": "tomato",
            "ingredient_category": "Vegetables",
            "quantity": "2",
            "unit": "cups"
        }
    ]
    return form_data


@pytest.fixture 
def sample_recipe_dto():
    """Create sample RecipeCreateDTO for testing."""
    return RecipeCreateDTO(
        recipe_name="Test Recipe",
        recipe_category="Main Course", 
        meal_type="dinner",
        diet_pref="vegetarian",
        total_time=30,
        servings=4,
        directions="Mix ingredients and cook.",
        notes="Test notes",
        ingredients=[
            RecipeIngredientDTO(
                ingredient_name="tomato",
                ingredient_category="Vegetables",
                quantity=2.0,
                unit="cups"
            )
        ]
    )


class TestAddRecipeViewModelInitialization:
    """Test AddRecipeViewModel initialization and setup."""

    def test_initialization_with_session(self, mock_session):
        """Test ViewModel initializes correctly with provided session."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService') as mock_recipe_svc, \
             patch('app.ui.view_models.add_recipe_view_model.IngredientService') as mock_ingredient_svc:
            
            vm = AddRecipeViewModel(mock_session)
            
            assert vm._session is mock_session
            assert not vm._owns_session
            assert vm._current_form_data is None
            assert not vm.is_processing
            assert not vm.has_validation_errors


    def test_initialization_without_session(self):
        """Test ViewModel initializes correctly without session."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService'), \
             patch('app.ui.view_models.add_recipe_view_model.IngredientService'), \
             patch('app.core.database.db.create_session') as mock_create_session:
            
            mock_session = Mock()
            mock_create_session.return_value = mock_session
            
            vm = AddRecipeViewModel()
            
            # Session should be created when needed
            vm._ensure_session()
            assert vm._session is mock_session
            assert vm._owns_session


    def test_services_initialization(self, mock_session):
        """Test that Core services are properly initialized."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService') as mock_recipe_svc, \
             patch('app.ui.view_models.add_recipe_view_model.IngredientService') as mock_ingredient_svc:
            
            vm = AddRecipeViewModel(mock_session)
            
            mock_recipe_svc.assert_called_once_with(mock_session)
            mock_ingredient_svc.assert_called_once_with(mock_session)


    def test_signal_definitions(self, add_recipe_vm):
        """Test that all required signals are defined."""
        vm = add_recipe_vm
        
        # Check that signals exist
        assert hasattr(vm, 'recipe_saved_successfully')
        assert hasattr(vm, 'recipe_save_failed')
        assert hasattr(vm, 'ingredient_search_completed')
        assert hasattr(vm, 'form_cleared')
        assert hasattr(vm, 'form_validation_state_changed')
        assert hasattr(vm, 'recipe_name_validated')
        
        # Check inherited signals from BaseViewModel
        assert hasattr(vm, 'processing_state_changed')
        assert hasattr(vm, 'validation_failed')
        assert hasattr(vm, 'error_occurred')


class TestFormValidation:
    """Test form validation functionality."""

    def test_validate_recipe_form_valid_data(self, add_recipe_vm, sample_form_data):
        """Test form validation with valid data."""
        result = add_recipe_vm._validate_recipe_form(sample_form_data)
        
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_recipe_form_missing_required_fields(self, add_recipe_vm):
        """Test form validation with missing required fields."""
        form_data = RecipeFormData()
        form_data.ingredients = [{"ingredient_name": "test", "ingredient_category": "Vegetables"}]
        
        result = add_recipe_vm._validate_recipe_form(form_data)
        
        assert not result.is_valid
        assert "Recipe name is required" in result.errors
        assert "Meal type must be selected" in result.errors
        assert "Number of servings is required" in result.errors

    def test_validate_recipe_form_invalid_servings(self, add_recipe_vm, sample_form_data):
        """Test form validation with invalid servings value."""
        sample_form_data.servings = "invalid"
        
        result = add_recipe_vm._validate_recipe_form(sample_form_data)
        
        assert not result.is_valid
        assert any("Servings must be a valid positive number" in error for error in result.errors)

    def test_validate_recipe_form_invalid_time(self, add_recipe_vm, sample_form_data):
        """Test form validation with invalid total time."""
        sample_form_data.total_time = "-10"
        
        result = add_recipe_vm._validate_recipe_form(sample_form_data)
        
        assert not result.is_valid
        assert any("Total time cannot be negative" in error for error in result.errors)

    def test_validate_recipe_form_excessive_lengths(self, add_recipe_vm, sample_form_data):
        """Test form validation with fields exceeding length limits."""
        sample_form_data.recipe_name = "a" * 201  # Exceeds 200 char limit
        sample_form_data.directions = "a" * 5001   # Exceeds 5000 char limit
        
        result = add_recipe_vm._validate_recipe_form(sample_form_data)
        
        assert not result.is_valid
        assert any("Recipe name cannot exceed 200 characters" in error for error in result.errors)
        assert any("Directions cannot exceed 5000 characters" in error for error in result.errors)

    def test_validate_ingredients_empty_list(self, add_recipe_vm):
        """Test ingredient validation with empty ingredient list."""
        result = add_recipe_vm._validate_ingredients([])
        
        assert not result.is_valid
        assert "At least one ingredient is required" in result.errors

    def test_validate_ingredients_missing_required_fields(self, add_recipe_vm):
        """Test ingredient validation with missing required fields."""
        ingredients = [
            {"ingredient_name": "", "ingredient_category": "Vegetables"},
            {"ingredient_name": "tomato", "ingredient_category": ""}
        ]
        
        result = add_recipe_vm._validate_ingredients(ingredients)
        
        assert not result.is_valid
        assert any("Ingredient 1: Name is required" in error for error in result.errors)
        assert any("Ingredient 2: Category is required" in error for error in result.errors)

    def test_validate_ingredients_invalid_quantity(self, add_recipe_vm):
        """Test ingredient validation with invalid quantity."""
        ingredients = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables", 
                "quantity": "invalid"
            }
        ]
        
        result = add_recipe_vm._validate_ingredients(ingredients)
        
        assert not result.is_valid
        assert any("Ingredient 1: Quantity must be a positive number" in error for error in result.errors)


class TestDataTransformation:
    """Test data transformation functionality."""

    def test_transform_to_recipe_dto_success(self, add_recipe_vm, sample_form_data):
        """Test successful transformation of form data to RecipeCreateDTO."""
        result = add_recipe_vm._transform_to_recipe_dto(sample_form_data)
        
        assert result is not None
        assert isinstance(result, RecipeCreateDTO)
        assert result.recipe_name == "Test Recipe"
        assert result.recipe_category == "Main Course"
        assert result.meal_type == "dinner"
        assert result.servings == 4
        assert result.total_time == 30
        assert len(result.ingredients) == 1

    def test_transform_to_recipe_dto_with_defaults(self, add_recipe_vm):
        """Test transformation with missing optional fields uses defaults."""
        form_data = RecipeFormData()
        form_data.recipe_name = "Simple Recipe"
        form_data.meal_type = "lunch"
        form_data.servings = "2"
        form_data.ingredients = [
            {"ingredient_name": "bread", "ingredient_category": "Grains"}
        ]
        
        result = add_recipe_vm._transform_to_recipe_dto(form_data)
        
        assert result is not None
        assert result.recipe_category == "General"  # Default value
        assert result.diet_pref is None
        assert result.directions is None
        assert result.notes is None

    def test_transform_ingredients_success(self, add_recipe_vm):
        """Test successful transformation of ingredient data."""
        raw_ingredients = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "2.5",
                "unit": "cups"
            },
            {
                "ingredient_name": "onion",
                "ingredient_category": "Vegetables",
                "quantity": "",  # No quantity
                "unit": ""
            }
        ]
        
        result = add_recipe_vm._transform_ingredients(raw_ingredients)
        
        assert len(result) == 2
        assert result[0].ingredient_name == "tomato"
        assert result[0].quantity == 2.5
        assert result[0].unit == "cups"
        assert result[1].ingredient_name == "onion"
        assert result[1].quantity is None
        assert result[1].unit is None

    def test_transform_ingredients_skips_empty(self, add_recipe_vm):
        """Test that empty ingredients are skipped during transformation."""
        raw_ingredients = [
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "", "ingredient_category": "Vegetables"},  # Empty name
            {"ingredient_name": "   ", "ingredient_category": "Vegetables"}  # Whitespace only
        ]
        
        result = add_recipe_vm._transform_ingredients(raw_ingredients)
        
        assert len(result) == 1
        assert result[0].ingredient_name == "tomato"


class TestRecipeCreation:
    """Test recipe creation workflow."""

    def test_create_recipe_success(self, add_recipe_vm, sample_form_data):
        """Test successful recipe creation."""
        # Mock successful recipe creation
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Test Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        
        # Mock validation to return valid
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Connect signal spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Verify recipe was created
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.assert_called_once()
        recipe_saved_spy.assert_called_once_with("Test Recipe")
        assert not add_recipe_vm.is_processing
        assert add_recipe_vm._current_form_data is None

    def test_create_recipe_validation_failure(self, add_recipe_vm, sample_form_data):
        """Test recipe creation with validation failure."""
        # Mock validation failure
        validation_result = BaseValidationResult(is_valid=False)
        validation_result.add_error("Test error")
        add_recipe_vm._validate_recipe_form = Mock(return_value=validation_result)
        
        # Connect signal spies
        validation_failed_spy = Mock()
        form_validation_spy = Mock()
        add_recipe_vm.validation_failed.connect(validation_failed_spy)
        add_recipe_vm.form_validation_state_changed.connect(form_validation_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Verify validation failure was handled
        form_validation_spy.assert_called_with(False)
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.assert_not_called()
        assert not add_recipe_vm.is_processing

    def test_create_recipe_duplicate_error(self, add_recipe_vm, sample_form_data):
        """Test recipe creation with duplicate recipe error."""
        # Mock validation success
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Mock duplicate recipe error
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.side_effect = \
            DuplicateRecipeError("Recipe already exists")
        
        # Connect signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Verify error was handled
        save_failed_spy.assert_called_once_with("Recipe already exists")
        assert not add_recipe_vm.is_processing

    def test_create_recipe_save_error(self, add_recipe_vm, sample_form_data):
        """Test recipe creation with save error."""
        # Mock validation success
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Mock save error
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.side_effect = \
            RecipeSaveError("Database error")
        
        # Connect signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Verify error was handled
        save_failed_spy.assert_called_once_with("Failed to save recipe: Database error")
        assert not add_recipe_vm.is_processing

    def test_create_recipe_already_processing(self, add_recipe_vm, sample_form_data):
        """Test that duplicate recipe creation requests are ignored when already processing."""
        add_recipe_vm._set_processing_state(True)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Verify no processing occurred
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.assert_not_called()


class TestImageHandling:
    """Test image handling functionality."""

    def test_update_recipe_image_success(self, add_recipe_vm):
        """Test successful recipe image update."""
        add_recipe_vm._update_recipe_image(1, "/path/to/image.jpg")
        
        add_recipe_vm.recipe_service.update_recipe_reference_image_path.assert_called_once_with(
            1, "/path/to/image.jpg"
        )

    def test_update_recipe_image_failure(self, add_recipe_vm):
        """Test recipe image update failure doesn't crash operation."""
        add_recipe_vm.recipe_service.update_recipe_reference_image_path.side_effect = \
            Exception("Image update failed")
        
        # Should not raise exception
        add_recipe_vm._update_recipe_image(1, "/path/to/image.jpg")


class TestIngredientSearch:
    """Test ingredient search functionality."""

    def test_search_ingredients_success(self, add_recipe_vm):
        """Test successful ingredient search."""
        # Mock ingredient search results
        mock_ingredients = [Mock(ingredient_name="tomato"), Mock(ingredient_name="onion")]
        add_recipe_vm.ingredient_service.search.return_value = mock_ingredients
        
        # Connect signal spy
        search_completed_spy = Mock()
        add_recipe_vm.ingredient_search_completed.connect(search_completed_spy)
        
        result = add_recipe_vm.search_ingredients("tom")
        
        assert result == mock_ingredients
        search_completed_spy.assert_called_once_with(mock_ingredients)

    def test_search_ingredients_empty_term(self, add_recipe_vm):
        """Test ingredient search with empty search term."""
        result = add_recipe_vm.search_ingredients("")
        
        add_recipe_vm.ingredient_service.search.assert_not_called()
        assert result == []

    def test_search_ingredients_service_failure(self, add_recipe_vm):
        """Test ingredient search with service failure."""
        add_recipe_vm.ingredient_service.search.side_effect = Exception("Search failed")
        
        result = add_recipe_vm.search_ingredients("tom")
        
        assert result == []

    def test_get_ingredient_names(self, add_recipe_vm):
        """Test getting ingredient names for autocomplete."""
        mock_names = ["tomato", "onion", "garlic"]
        add_recipe_vm.ingredient_service.list_distinct_names.return_value = mock_names
        
        result = add_recipe_vm.get_ingredient_names()
        
        assert result == mock_names


class TestFormManagement:
    """Test form management functionality."""

    def test_clear_form_data(self, add_recipe_vm):
        """Test clearing form data."""
        # Set some state
        add_recipe_vm._current_form_data = RecipeFormData()
        
        # Connect signal spy
        form_cleared_spy = Mock()
        add_recipe_vm.form_cleared.connect(form_cleared_spy)
        
        add_recipe_vm.clear_form_data()
        
        assert add_recipe_vm._current_form_data is None
        form_cleared_spy.assert_called_once()

    def test_reset_state(self, add_recipe_vm):
        """Test resetting ViewModel state."""
        # Set some state
        add_recipe_vm._set_processing_state(True)
        add_recipe_vm._current_form_data = RecipeFormData()
        
        # Connect signal spy
        state_reset_spy = Mock()
        add_recipe_vm.state_reset.connect(state_reset_spy)
        
        add_recipe_vm.reset_state()
        
        assert not add_recipe_vm.is_processing
        assert add_recipe_vm._current_form_data is None
        state_reset_spy.assert_called_once()


class TestRecipeNameValidation:
    """Test recipe name uniqueness validation."""

    def test_validate_recipe_name_unique(self, add_recipe_vm):
        """Test recipe name validation when name is unique."""
        add_recipe_vm.recipe_service.recipe_repo.recipe_exists.return_value = False
        
        # Connect signal spy
        name_validated_spy = Mock()
        add_recipe_vm.recipe_name_validated.connect(name_validated_spy)
        
        result = add_recipe_vm.validate_recipe_name("New Recipe", "Main Course")
        
        assert result is True
        name_validated_spy.assert_called_once_with(True, "Recipe name is available")

    def test_validate_recipe_name_duplicate(self, add_recipe_vm):
        """Test recipe name validation when duplicate exists."""
        add_recipe_vm.recipe_service.recipe_repo.recipe_exists.return_value = True
        
        # Connect signal spy
        name_validated_spy = Mock()
        add_recipe_vm.recipe_name_validated.connect(name_validated_spy)
        
        result = add_recipe_vm.validate_recipe_name("Existing Recipe", "Main Course")
        
        assert result is False
        name_validated_spy.assert_called_once_with(
            False, "Recipe 'Existing Recipe' already exists in Main Course"
        )


class TestRealTimeValidation:
    """Test real-time field validation."""

    def test_validate_field_real_time_recipe_name(self, add_recipe_vm):
        """Test real-time validation for recipe name field."""
        # Test valid name
        result = add_recipe_vm.validate_field_real_time("recipe_name", "Valid Recipe Name")
        assert result is True
        
        # Test empty name
        result = add_recipe_vm.validate_field_real_time("recipe_name", "")
        assert result is False

    def test_validate_field_real_time_servings(self, add_recipe_vm):
        """Test real-time validation for servings field."""
        # Test valid servings
        result = add_recipe_vm.validate_field_real_time("servings", "4")
        assert result is True
        
        # Test invalid servings
        result = add_recipe_vm.validate_field_real_time("servings", "invalid")
        assert result is False

    def test_validate_field_real_time_total_time(self, add_recipe_vm):
        """Test real-time validation for total time field."""
        # Test valid time
        result = add_recipe_vm.validate_field_real_time("total_time", "30")
        assert result is True
        
        # Test negative time
        result = add_recipe_vm.validate_field_real_time("total_time", "-10")
        assert result is False
        
        # Test empty time (should be valid as optional)
        result = add_recipe_vm.validate_field_real_time("total_time", "")
        assert result is True

    def test_validate_field_real_time_unknown_field(self, add_recipe_vm):
        """Test real-time validation for unknown field."""
        # Connect signal spy
        field_cleared_spy = Mock()
        add_recipe_vm.field_validation_cleared.connect(field_cleared_spy)
        
        result = add_recipe_vm.validate_field_real_time("unknown_field", "value")
        
        assert result is True
        field_cleared_spy.assert_called_once_with("unknown_field")


class TestFormDataPreprocessing:
    """Test form data preprocessing functionality."""

    def test_preprocess_form_data_success(self, add_recipe_vm):
        """Test successful form data preprocessing."""
        raw_data = {
            "recipe_name": "  Test Recipe  ",
            "recipe_category": "Main Course",
            "meal_type": "dinner",
            "total_time": "30",
            "servings": "4",
            "ingredients": [{"ingredient_name": "tomato"}]
        }
        
        result = add_recipe_vm.preprocess_form_data(raw_data)
        
        assert isinstance(result, RecipeFormData)
        assert result.recipe_name == "Test Recipe"  # Whitespace trimmed
        assert result.recipe_category == "Main Course"
        assert result.meal_type == "dinner"
        assert result.total_time == "30"
        assert result.servings == "4"
        assert result.ingredients == [{"ingredient_name": "tomato"}]

    def test_preprocess_form_data_with_missing_fields(self, add_recipe_vm):
        """Test form data preprocessing with missing fields."""
        raw_data = {
            "recipe_name": "Test Recipe"
            # Missing other fields
        }
        
        result = add_recipe_vm.preprocess_form_data(raw_data)
        
        assert isinstance(result, RecipeFormData)
        assert result.recipe_name == "Test Recipe"
        assert result.recipe_category == ""
        assert result.meal_type == ""
        assert result.ingredients == []


class TestProperties:
    """Test ViewModel properties."""

    def test_current_form_data_property(self, add_recipe_vm):
        """Test current form data property."""
        assert add_recipe_vm.current_form_data is None
        
        form_data = RecipeFormData()
        add_recipe_vm._current_form_data = form_data
        
        assert add_recipe_vm.current_form_data is form_data


class TestServiceInitialization:
    """Test service initialization and session management."""

    def test_service_initialization_success(self, mock_session):
        """Test successful service initialization."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService') as mock_recipe_svc, \
             patch('app.ui.view_models.add_recipe_view_model.IngredientService') as mock_ingredient_svc:
            
            vm = AddRecipeViewModel(mock_session)
            
            # Verify services were initialized
            mock_recipe_svc.assert_called_once_with(mock_session)
            mock_ingredient_svc.assert_called_once_with(mock_session)
            assert vm.recipe_service is not None
            assert vm.ingredient_service is not None

    def test_service_initialization_failure(self, mock_session):
        """Test service initialization failure handling."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService') as mock_recipe_svc:
            mock_recipe_svc.side_effect = Exception("Service init failed")
            
            vm = AddRecipeViewModel(mock_session)
            
            # Services should be None after failure
            assert vm.recipe_service is None
            assert vm.ingredient_service is None

    def test_ensure_session_creates_new_session(self):
        """Test that _ensure_session creates session when needed."""
        vm = AddRecipeViewModel()  # No session provided
        
        with patch('app.core.database.db.create_session') as mock_create:
            mock_session = Mock()
            mock_create.return_value = mock_session
            
            # Should create session
            result = vm._ensure_session()
            
            assert result is True
            assert vm._session is mock_session
            assert vm._owns_session is True


class TestAdvancedFormValidation:
    """Test advanced form validation scenarios."""

    def test_validate_recipe_form_comprehensive_errors(self, add_recipe_vm):
        """Test form validation with multiple error types."""
        form_data = RecipeFormData()
        # Leave all required fields empty and add invalid data
        form_data.recipe_name = ""  # Required
        form_data.meal_type = ""   # Required
        form_data.servings = ""    # Required
        form_data.total_time = "-5"  # Invalid
        form_data.directions = "x" * 5001  # Too long
        form_data.ingredients = []  # Empty
        
        result = add_recipe_vm._validate_recipe_form(form_data)
        
        assert not result.is_valid
        assert len(result.errors) >= 6  # At least 6 different errors
        
        # Check specific error messages
        error_messages = " ".join(result.errors)
        assert "Recipe name is required" in error_messages
        assert "Meal type must be selected" in error_messages
        assert "Number of servings is required" in error_messages
        assert "Total time cannot be negative" in error_messages
        assert "Directions cannot exceed 5000 characters" in error_messages
        assert "At least one ingredient is required" in error_messages

    def test_validate_recipe_form_edge_cases(self, add_recipe_vm):
        """Test form validation edge cases."""
        form_data = RecipeFormData()
        form_data.recipe_name = "x" * 200  # Exactly at limit
        form_data.meal_type = "dinner"
        form_data.servings = "1"  # Minimum valid
        form_data.total_time = "0"  # Zero time (valid)
        form_data.directions = "x" * 5000  # Exactly at limit
        form_data.ingredients = [{"ingredient_name": "test", "ingredient_category": "Vegetables"}]
        
        result = add_recipe_vm._validate_recipe_form(form_data)
        
        assert result.is_valid  # Should be valid at exact limits

    def test_validate_ingredients_complex_scenarios(self, add_recipe_vm):
        """Test ingredient validation with complex scenarios."""
        ingredients = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "2.5",
                "unit": "cups"
            },
            {
                "ingredient_name": "",  # Empty name
                "ingredient_category": "Vegetables"
            },
            {
                "ingredient_name": "onion",
                "ingredient_category": ""  # Empty category
            },
            {
                "ingredient_name": "garlic",
                "ingredient_category": "Vegetables",
                "quantity": "invalid_number"
            },
            {
                "ingredient_name": "pepper",
                "ingredient_category": "Vegetables",
                "quantity": "-2"  # Negative quantity
            }
        ]
        
        result = add_recipe_vm._validate_ingredients(ingredients)
        
        assert not result.is_valid
        assert len(result.errors) >= 4  # Multiple validation errors
        
        # Check for specific error patterns
        error_text = " ".join(result.errors)
        assert "Name is required" in error_text
        assert "Category is required" in error_text
        assert "must be a positive number" in error_text


class TestDataTransformationComprehensive:
    """Test comprehensive data transformation scenarios."""

    def test_transform_to_recipe_dto_all_fields(self, add_recipe_vm):
        """Test DTO transformation with all fields populated."""
        form_data = RecipeFormData()
        form_data.recipe_name = "Complete Recipe"
        form_data.recipe_category = "Main Course"
        form_data.meal_type = "dinner"
        form_data.dietary_preference = "vegetarian"
        form_data.total_time = "45"
        form_data.servings = "6"
        form_data.directions = "Detailed cooking instructions"
        form_data.notes = "Additional recipe notes"
        form_data.reference_image_path = "/path/to/image.jpg"
        form_data.banner_image_path = "/path/to/banner.jpg"
        form_data.ingredients = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "3",
                "unit": "pieces",
                "existing_ingredient_id": 123
            }
        ]
        
        result = add_recipe_vm._transform_to_recipe_dto(form_data)
        
        assert result is not None
        assert isinstance(result, RecipeCreateDTO)
        assert result.recipe_name == "Complete Recipe"
        assert result.recipe_category == "Main Course"
        assert result.meal_type == "dinner"
        assert result.diet_pref == "vegetarian"
        assert result.total_time == 45
        assert result.servings == 6
        assert result.directions == "Detailed cooking instructions"
        assert result.notes == "Additional recipe notes"
        assert result.reference_image_path == "/path/to/image.jpg"
        assert result.banner_image_path == "/path/to/banner.jpg"
        assert len(result.ingredients) == 1
        assert result.ingredients[0].existing_ingredient_id == 123

    def test_transform_to_recipe_dto_transformation_error(self, add_recipe_vm):
        """Test DTO transformation error handling."""
        form_data = RecipeFormData()
        form_data.recipe_name = "Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [{"ingredient_name": "test", "ingredient_category": "Vegetables"}]
        
        # Mock a transformation failure
        with patch.object(add_recipe_vm, '_transform_ingredients', side_effect=Exception("Transform failed")):
            result = add_recipe_vm._transform_to_recipe_dto(form_data)
            
            assert result is None

    def test_transform_ingredients_edge_cases(self, add_recipe_vm):
        """Test ingredient transformation edge cases."""
        raw_ingredients = [
            {
                "ingredient_name": "  tomato  ",  # Whitespace
                "ingredient_category": "Vegetables",
                "quantity": "",  # Empty quantity
                "unit": "",  # Empty unit
            },
            {
                "ingredient_name": "",  # Empty name (should be skipped)
                "ingredient_category": "Vegetables",
                "quantity": "2",
                "unit": "cups"
            },
            {
                "ingredient_name": "onion",
                "ingredient_category": "Vegetables",
                "quantity": "invalid",  # Invalid quantity (should be None)
                "unit": "pieces"
            }
        ]
        
        result = add_recipe_vm._transform_ingredients(raw_ingredients)
        
        # Should skip empty ingredient, process others
        assert len(result) == 2
        assert result[0].ingredient_name == "tomato"
        assert result[0].quantity is None
        assert result[0].unit is None
        assert result[1].ingredient_name == "onion"
        assert result[1].quantity is None  # Invalid quantity becomes None


class TestRecipeCreationAdvanced:
    """Test advanced recipe creation scenarios."""

    def test_create_recipe_processing_state_management(self, add_recipe_vm, sample_form_data):
        """Test processing state management during recipe creation."""
        # Mock successful creation
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Test Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Connect signal spy
        processing_spy = Mock()
        add_recipe_vm.processing_state_changed.connect(processing_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Should have been called twice: start and end
        assert processing_spy.call_count == 2
        processing_spy.assert_has_calls([call(True), call(False)])
        assert not add_recipe_vm.is_processing

    def test_create_recipe_loading_state_progression(self, add_recipe_vm, sample_form_data):
        """Test loading state progression during recipe creation."""
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Test Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Connect signal spy
        loading_spy = Mock()
        add_recipe_vm.loading_state_changed.connect(loading_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Should show different loading messages during process
        assert loading_spy.call_count >= 4  # At least start, creating, and end states
        
        # Check that different loading messages were used
        call_args_list = [call.args for call in loading_spy.call_args_list]
        messages = [args[1] for args in call_args_list if len(args) > 1]
        assert "Saving recipe..." in messages
        assert "Creating recipe..." in messages

    def test_create_recipe_with_image_update_failure(self, add_recipe_vm, sample_form_data):
        """Test recipe creation when image update fails."""
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Test Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Mock image update failure
        add_recipe_vm.recipe_service.update_recipe_reference_image_path.side_effect = Exception("Image update failed")
        
        # Set image path
        sample_form_data.reference_image_path = "/path/to/image.jpg"
        
        # Connect signal spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Should still succeed despite image failure
        recipe_saved_spy.assert_called_once_with("Test Recipe")

    def test_create_recipe_dto_transformation_failure(self, add_recipe_vm, sample_form_data):
        """Test recipe creation when DTO transformation fails."""
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        add_recipe_vm._transform_to_recipe_dto = Mock(return_value=None)  # Simulate failure
        
        # Connect signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Should handle transformation failure
        save_failed_spy.assert_called_once_with("Failed to process form data")
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.assert_not_called()

    def test_create_recipe_unexpected_error_handling(self, add_recipe_vm, sample_form_data):
        """Test handling of unexpected errors during recipe creation."""
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.side_effect = Exception("Unexpected database error")
        
        # Connect signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        add_recipe_vm.create_recipe(sample_form_data)
        
        # Should handle unexpected error gracefully
        save_failed_spy.assert_called_once()
        error_message = save_failed_spy.call_args[0][0]
        assert "unexpected error" in error_message.lower()
        assert not add_recipe_vm.is_processing


class TestIngredientSearchEnhanced:
    """Test enhanced ingredient search functionality."""

    def test_search_ingredients_with_category_filter(self, add_recipe_vm):
        """Test ingredient search with category filter."""
        mock_ingredients = [Mock(ingredient_name="tomato")]
        add_recipe_vm.ingredient_service.search.return_value = mock_ingredients
        
        result = add_recipe_vm.search_ingredients("tom", "Vegetables")
        
        assert result == mock_ingredients
        add_recipe_vm.ingredient_service.search.assert_called_once()

    def test_search_ingredients_service_not_initialized(self, mock_session):
        """Test ingredient search when service is not initialized."""
        with patch('app.ui.view_models.add_recipe_view_model.RecipeService'), \
             patch('app.ui.view_models.add_recipe_view_model.IngredientService', side_effect=Exception("Init failed")):
            
            vm = AddRecipeViewModel(mock_session)
            assert vm.ingredient_service is None
            
            result = vm.search_ingredients("tomato")
            
            assert result == []

    def test_get_ingredient_names_service_failure(self, add_recipe_vm):
        """Test get ingredient names with service failure."""
        add_recipe_vm.ingredient_service.list_distinct_names.side_effect = Exception("Service failed")
        
        result = add_recipe_vm.get_ingredient_names()
        
        assert result == []

    def test_search_ingredients_empty_term_handling(self, add_recipe_vm):
        """Test search ingredients with empty term."""
        result = add_recipe_vm.search_ingredients("")
        
        assert result == []
        add_recipe_vm.ingredient_service.search.assert_not_called()


class TestRealTimeValidationEnhanced:
    """Test enhanced real-time field validation."""

    def test_validate_field_real_time_all_fields(self, add_recipe_vm):
        """Test real-time validation for all supported fields."""
        # Test recipe name
        assert add_recipe_vm.validate_field_real_time("recipe_name", "Valid Recipe") is True
        assert add_recipe_vm.validate_field_real_time("recipe_name", "") is False
        
        # Test servings
        assert add_recipe_vm.validate_field_real_time("servings", "4") is True
        assert add_recipe_vm.validate_field_real_time("servings", "invalid") is False
        
        # Test total time
        assert add_recipe_vm.validate_field_real_time("total_time", "30") is True
        assert add_recipe_vm.validate_field_real_time("total_time", "-10") is False
        assert add_recipe_vm.validate_field_real_time("total_time", "") is True  # Optional
        
        # Test meal type
        assert add_recipe_vm.validate_field_real_time("meal_type", "dinner") is True
        assert add_recipe_vm.validate_field_real_time("meal_type", "") is False
        
        # Test unknown field
        assert add_recipe_vm.validate_field_real_time("unknown_field", "value") is True

    def test_validate_field_real_time_with_context(self, add_recipe_vm):
        """Test real-time validation with additional context."""
        context = {"recipe_category": "Main Course"}
        
        result = add_recipe_vm.validate_field_real_time("recipe_name", "Test Recipe", context)
        
        assert result is True

    def test_validate_field_real_time_exception_handling(self, add_recipe_vm):
        """Test real-time validation exception handling."""
        # Connect signal spy
        field_error_spy = Mock()
        add_recipe_vm.field_validation_error.connect(field_error_spy)
        
        # Mock validation method to raise exception
        add_recipe_vm._validate_recipe_name_field = Mock(side_effect=Exception("Validation error"))
        
        result = add_recipe_vm.validate_field_real_time("recipe_name", "Test")
        
        assert result is False
        field_error_spy.assert_called_once_with("recipe_name", "Validation error occurred")

    def test_individual_field_validation_methods(self, add_recipe_vm):
        """Test individual field validation methods."""
        # Test recipe name field validation
        add_recipe_vm._validate_required_field = Mock(return_value=True)
        add_recipe_vm._validate_field_length = Mock(return_value=True)
        
        result = add_recipe_vm._validate_recipe_name_field("Valid Recipe")
        
        assert result is True
        add_recipe_vm._validate_required_field.assert_called_once()
        add_recipe_vm._validate_field_length.assert_called_once()
        
        # Test servings field validation
        add_recipe_vm._validate_required_field.reset_mock()
        add_recipe_vm._clear_field_error = Mock()
        
        result = add_recipe_vm._validate_servings_field("4")
        
        assert result is True
        add_recipe_vm._clear_field_error.assert_called_once_with("servings")

    def test_meal_type_field_validation(self, add_recipe_vm):
        """Test meal type field validation specifically."""
        add_recipe_vm._validate_required_field = Mock(return_value=True)
        
        result = add_recipe_vm._validate_meal_type_field("dinner")
        
        assert result is True
        add_recipe_vm._validate_required_field.assert_called_once_with("dinner", "meal_type", "Meal Type")


class TestUtilityMethodsAndProperties:
    """Test utility methods and properties."""

    def test_validate_recipe_name_service_failure(self, add_recipe_vm):
        """Test recipe name validation with service failure."""
        add_recipe_vm.recipe_service.recipe_repo.recipe_exists.side_effect = Exception("Service failed")
        
        # Connect signal spy
        name_validated_spy = Mock()
        add_recipe_vm.recipe_name_validated.connect(name_validated_spy)
        
        result = add_recipe_vm.validate_recipe_name("Test Recipe", "Main Course")
        
        # Should assume unique on error
        assert result is True
        name_validated_spy.assert_called_once_with(True, "")

    def test_preprocess_form_data_comprehensive(self, add_recipe_vm):
        """Test comprehensive form data preprocessing."""
        raw_data = {
            "recipe_name": "  Test Recipe  ",
            "recipe_category": "Main Course",
            "meal_type": "dinner",
            "dietary_preference": "vegetarian",
            "total_time": "  45  ",
            "servings": "6",
            "directions": "Cook well",
            "notes": "Good recipe",
            "reference_image_path": "/path/to/image.jpg",
            "banner_image_path": "/path/to/banner.jpg",
            "ingredients": [{"ingredient_name": "tomato"}]
        }
        
        result = add_recipe_vm.preprocess_form_data(raw_data)
        
        assert isinstance(result, RecipeFormData)
        assert result.recipe_name == "Test Recipe"  # Trimmed
        assert result.recipe_category == "Main Course"
        assert result.meal_type == "dinner"
        assert result.dietary_preference == "vegetarian"
        assert result.total_time == "45"  # Trimmed
        assert result.servings == "6"
        assert result.directions == "Cook well"
        assert result.notes == "Good recipe"
        assert result.reference_image_path == "/path/to/image.jpg"
        assert result.banner_image_path == "/path/to/banner.jpg"
        assert len(result.ingredients) == 1

    def test_preprocess_form_data_with_missing_fields(self, add_recipe_vm):
        """Test form data preprocessing with missing fields."""
        raw_data = {"recipe_name": "Test Recipe"}  # Only name provided
        
        result = add_recipe_vm.preprocess_form_data(raw_data)
        
        assert isinstance(result, RecipeFormData)
        assert result.recipe_name == "Test Recipe"
        assert result.recipe_category == ""
        assert result.meal_type == ""
        assert result.ingredients == []

    def test_current_form_data_property(self, add_recipe_vm):
        """Test current_form_data property."""
        assert add_recipe_vm.current_form_data is None
        
        form_data = RecipeFormData()
        add_recipe_vm._current_form_data = form_data
        
        assert add_recipe_vm.current_form_data is form_data

    def test_reset_internal_state_override(self, add_recipe_vm):
        """Test that _reset_internal_state properly clears recipe-specific state."""
        add_recipe_vm._current_form_data = RecipeFormData()
        add_recipe_vm._is_processing = True
        
        add_recipe_vm._reset_internal_state()
        
        assert add_recipe_vm._current_form_data is None
        assert not add_recipe_vm._is_processing


@pytest.mark.integration
class TestAddRecipeViewModelIntegration:
    """Integration tests for AddRecipeViewModel with real services."""

    def test_full_recipe_creation_workflow(self, db_session):
        """Test complete recipe creation workflow with real database."""
        from app.core.repositories.ingredient_repo import IngredientRepo
        from app.core.repositories.recipe_repo import RecipeRepo
        from app.core.services.ingredient_service import IngredientService
        from app.core.services.recipe_service import RecipeService

        # Create real services with test database session
        recipe_repo = RecipeRepo(db_session)
        ingredient_repo = IngredientRepo(db_session)
        recipe_service = RecipeService(db_session)
        ingredient_service = IngredientService(db_session)
        
        # Create ViewModel with real services
        vm = AddRecipeViewModel(db_session)
        vm.recipe_service = recipe_service
        vm.ingredient_service = ingredient_service
        
        # Create form data
        form_data = RecipeFormData()
        form_data.recipe_name = "Integration Test Recipe"
        form_data.recipe_category = "Test Category"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [
            {
                "ingredient_name": "test ingredient",
                "ingredient_category": "Vegetables",
                "quantity": "2",
                "unit": "cups"
            }
        ]
        
        # Connect signal spies
        recipe_saved_spy = Mock()
        vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        # Execute recipe creation
        vm.create_recipe(form_data)
        
        # Verify recipe was created
        recipe_saved_spy.assert_called_once_with("Integration Test Recipe")
        
        # Verify recipe exists in database
        created_recipe = recipe_repo.find_by_name("Integration Test Recipe")
        assert created_recipe is not None
        assert created_recipe.recipe_name == "Integration Test Recipe"
        assert created_recipe.meal_type == "dinner"
        assert len(created_recipe.recipe_ingredients) == 1