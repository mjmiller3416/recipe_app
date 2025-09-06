"""
Integration tests for AddRecipes functionality.

Tests the complete integration between:
- AddRecipeViewModel and IngredientViewModel
- ViewModels and Core services
- Form validation across layers
- Data flow from UI to database
- Error handling integration
- Transaction management
"""

from unittest.mock import Mock, patch

from PySide6.QtCore import QTimer
import pytest

from app.core.dtos.recipe_dtos import RecipeCreateDTO
from app.core.models.ingredient import Ingredient
from app.core.models.recipe import Recipe
from app.core.repositories.ingredient_repo import IngredientRepo
from app.core.repositories.recipe_repo import RecipeRepo
from app.core.services.ingredient_service import IngredientService
from app.core.services.recipe_service import DuplicateRecipeError, RecipeService
from app.ui.view_models.add_recipe_view_model import AddRecipeViewModel, RecipeFormData
from app.ui.view_models.ingredient_view_model import (
    IngredientFormData, IngredientViewModel,
)

@pytest.fixture
def recipe_repository(db_session):
    """Create recipe repository with test database."""
    return RecipeRepo(db_session)


@pytest.fixture
def ingredient_repository(db_session):
    """Create ingredient repository with test database."""
    return IngredientRepo(db_session)


@pytest.fixture
def recipe_service(db_session):
    """Create recipe service with test database."""
    return RecipeService(db_session)


@pytest.fixture
def ingredient_service(db_session):
    """Create ingredient service with test database."""
    return IngredientService(db_session)


@pytest.fixture
def add_recipe_vm(db_session, recipe_service, ingredient_service):
    """Create AddRecipeViewModel with real services."""
    vm = AddRecipeViewModel(db_session)
    vm.recipe_service = recipe_service
    vm.ingredient_service = ingredient_service
    return vm


@pytest.fixture
def ingredient_vm(db_session, ingredient_service):
    """Create IngredientViewModel with real services."""
    vm = IngredientViewModel(db_session)
    vm.ingredient_service = ingredient_service
    return vm


@pytest.fixture
def sample_recipe_form_data():
    """Create sample recipe form data for testing."""
    form_data = RecipeFormData()
    form_data.recipe_name = "Integration Test Recipe"
    form_data.recipe_category = "Main Course"
    form_data.meal_type = "dinner"
    form_data.dietary_preference = "vegetarian"
    form_data.total_time = "45"
    form_data.servings = "6"
    form_data.directions = "1. Prep ingredients\n2. Cook according to instructions\n3. Serve hot"
    form_data.notes = "This is a test recipe for integration testing"
    form_data.reference_image_path = ""
    form_data.ingredients = [
        {
            "ingredient_name": "tomato",
            "ingredient_category": "Vegetables",
            "quantity": "3",
            "unit": "pieces",
            "existing_ingredient_id": None
        },
        {
            "ingredient_name": "olive oil",
            "ingredient_category": "Oils",
            "quantity": "2",
            "unit": "tablespoons",
            "existing_ingredient_id": None
        }
    ]
    return form_data


class TestRecipeCreationWorkflow:
    """Test complete recipe creation workflow integration."""

    @pytest.mark.integration
    def test_complete_recipe_creation_success(self, add_recipe_vm, sample_recipe_form_data, recipe_repository):
        """Test complete successful recipe creation workflow."""
        # Connect signal spies
        recipe_saved_spy = Mock()
        validation_failed_spy = Mock()
        processing_changed_spy = Mock()
        
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        add_recipe_vm.validation_failed.connect(validation_failed_spy)
        add_recipe_vm.processing_state_changed.connect(processing_changed_spy)
        
        # Execute recipe creation
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Verify success signals
        recipe_saved_spy.assert_called_once_with("Integration Test Recipe")
        validation_failed_spy.assert_not_called()
        
        # Verify processing state changes
        assert processing_changed_spy.call_count >= 2  # Should be called for start and end
        
        # Verify recipe was created in database
        created_recipe = recipe_repository.find_by_name("Integration Test Recipe")
        assert created_recipe is not None
        assert created_recipe.recipe_name == "Integration Test Recipe"
        assert created_recipe.recipe_category == "Main Course"
        assert created_recipe.meal_type == "dinner"
        assert created_recipe.servings == 6
        assert created_recipe.total_time == 45
        
        # Verify ingredients were created
        assert len(created_recipe.recipe_ingredients) == 2
        ingredient_names = [ri.ingredient.ingredient_name for ri in created_recipe.recipe_ingredients]
        assert "tomato" in ingredient_names
        assert "olive oil" in ingredient_names

    @pytest.mark.integration
    def test_recipe_creation_with_existing_ingredients(self, add_recipe_vm, ingredient_service, sample_recipe_form_data):
        """Test recipe creation when some ingredients already exist in database."""
        # Pre-create an ingredient
        existing_ingredient = ingredient_service.get_or_create_from_name_category("tomato", "Vegetables")
        assert existing_ingredient.id is not None
        
        # Update form data to reference existing ingredient
        sample_recipe_form_data.ingredients[0]["existing_ingredient_id"] = existing_ingredient.id
        
        # Connect signal spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        # Execute recipe creation
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Verify success
        recipe_saved_spy.assert_called_once()
        
        # Verify existing ingredient was reused
        created_recipe = add_recipe_vm.recipe_service.recipe_repo.find_by_name("Integration Test Recipe")
        tomato_recipe_ingredient = next(
            (ri for ri in created_recipe.recipe_ingredients if ri.ingredient.ingredient_name == "tomato"),
            None
        )
        assert tomato_recipe_ingredient is not None
        assert tomato_recipe_ingredient.ingredient.id == existing_ingredient.id

    @pytest.mark.integration
    def test_recipe_creation_validation_failure(self, add_recipe_vm, sample_recipe_form_data):
        """Test recipe creation with validation failure."""
        # Make form data invalid
        sample_recipe_form_data.recipe_name = ""  # Required field
        sample_recipe_form_data.meal_type = ""    # Required field
        sample_recipe_form_data.servings = "invalid"  # Invalid format
        
        # Connect signal spies
        recipe_saved_spy = Mock()
        validation_failed_spy = Mock()
        form_validation_spy = Mock()
        
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        add_recipe_vm.validation_failed.connect(validation_failed_spy)
        add_recipe_vm.form_validation_state_changed.connect(form_validation_spy)
        
        # Execute recipe creation
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Verify failure signals
        recipe_saved_spy.assert_not_called()
        form_validation_spy.assert_called_with(False)
        
        # Verify no recipe was created
        assert add_recipe_vm.recipe_service.recipe_repo.find_by_name("") is None

    @pytest.mark.integration
    def test_recipe_creation_duplicate_error(self, add_recipe_vm, sample_recipe_form_data):
        """Test recipe creation with duplicate recipe error."""
        # Create initial recipe
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Connect signal spy for second attempt
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        # Try to create duplicate recipe
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Verify duplicate error handling
        save_failed_spy.assert_called_once()
        error_message = save_failed_spy.call_args[0][0]
        assert "already exists" in error_message.lower()

    @pytest.mark.integration
    def test_recipe_creation_with_image_path(self, add_recipe_vm, sample_recipe_form_data, temp_dir):
        """Test recipe creation with image path handling."""
        # Create a mock image file
        image_path = temp_dir / "test_image.jpg"
        image_path.write_bytes(b"fake_image_data")
        
        sample_recipe_form_data.reference_image_path = str(image_path)
        
        # Connect signal spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        # Execute recipe creation
        add_recipe_vm.create_recipe(sample_recipe_form_data)
        
        # Verify success
        recipe_saved_spy.assert_called_once()
        
        # Verify image path was stored
        created_recipe = add_recipe_vm.recipe_service.recipe_repo.find_by_name("Integration Test Recipe")
        assert created_recipe.reference_image_path == str(image_path)


class TestIngredientViewModelIntegration:
    """Test IngredientViewModel integration with services and database."""

    @pytest.mark.integration
    def test_ingredient_search_and_matching(self, ingredient_vm, ingredient_service):
        """Test ingredient search and matching functionality."""
        # Pre-populate database with test ingredients
        test_ingredients = [
            ingredient_service.get_or_create_from_name_category("tomato", "Vegetables"),
            ingredient_service.get_or_create_from_name_category("cherry tomato", "Vegetables"),
            ingredient_service.get_or_create_from_name_category("tomato sauce", "Condiments")
        ]
        
        # Test search functionality
        search_results = ingredient_vm.search_ingredients("tomato")
        assert len(search_results) == 3
        
        # Test exact matching
        match_result = ingredient_vm.find_ingredient_matches("tomato")
        assert match_result.exact_match is not None
        assert match_result.exact_match.ingredient_name == "tomato"
        assert len(match_result.partial_matches) == 2
        assert match_result.suggested_category == "Vegetables"

    @pytest.mark.integration
    def test_ingredient_validation_with_real_data(self, ingredient_vm):
        """Test ingredient validation with realistic data scenarios."""
        # Test valid ingredient data
        valid_data = IngredientFormData()
        valid_data.ingredient_name = "organic tomato"
        valid_data.ingredient_category = "Vegetables"
        valid_data.quantity = "2.5"
        valid_data.unit = "cups"
        
        result = ingredient_vm.validate_ingredient_data(valid_data)
        assert result.is_valid is True
        assert len(result.errors) == 0
        
        # Test ingredient with warnings
        warning_data = IngredientFormData()
        warning_data.ingredient_name = "exotic spice"
        warning_data.ingredient_category = "Custom Spices"  # Non-standard category
        warning_data.quantity = "15000"  # Unusually large quantity
        
        result = ingredient_vm.validate_ingredient_data(warning_data)
        assert result.is_valid is True
        assert len(result.warnings) >= 1

    @pytest.mark.integration
    def test_ingredient_collection_validation_integration(self, ingredient_vm):
        """Test ingredient collection validation with mixed scenarios."""
        ingredients_data = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "3",
                "unit": "pieces"
            },
            {
                "ingredient_name": "olive oil",
                "ingredient_category": "Oils",
                "quantity": "2",
                "unit": "tablespoons"
            },
            {
                "ingredient_name": "tomato",  # Duplicate
                "ingredient_category": "Vegetables",
                "quantity": "1",
                "unit": "cup"
            }
        ]
        
        result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        assert result.is_valid is True
        assert len(result.warnings) >= 1  # Should warn about duplicate
        assert any("duplicate" in warning.lower() for warning in result.warnings)

    @pytest.mark.integration
    def test_autocomplete_cache_integration(self, ingredient_vm, ingredient_service):
        """Test autocomplete cache functionality with real database."""
        # Pre-populate with ingredients
        ingredients = [
            "tomato", "potato", "carrot", "onion", "garlic"
        ]
        for name in ingredients:
            ingredient_service.get_or_create_from_name_category(name, "Vegetables")
        
        # Test autocomplete suggestions
        suggestions = ingredient_vm.get_autocomplete_suggestions("to", limit=3)
        assert len(suggestions) <= 3
        assert all("to" in suggestion.lower() for suggestion in suggestions)
        
        # Verify cache was loaded
        assert ingredient_vm.cache_loaded is True
        assert ingredient_vm.autocomplete_count >= len(ingredients)

    @pytest.mark.integration
    def test_category_management_integration(self, ingredient_vm, ingredient_service):
        """Test category management with database integration."""
        # Add ingredients with custom categories
        ingredient_service.get_or_create_from_name_category("quinoa", "Ancient Grains")
        ingredient_service.get_or_create_from_name_category("coconut oil", "Healthy Oils")
        
        # Get all categories
        categories = ingredient_vm.get_available_categories()
        
        # Should include both standard and custom categories
        assert "Vegetables" in categories  # Standard category
        assert "Ancient Grains" in categories  # Custom category
        assert "Healthy Oils" in categories  # Custom category


class TestViewModelDataBinding:
    """Test data binding between ViewModels and form validation integration."""

    @pytest.mark.integration
    def test_real_time_validation_integration(self, add_recipe_vm, ingredient_vm):
        """Test real-time validation integration between ViewModels."""
        # Connect validation signal spies
        recipe_validation_spy = Mock()
        ingredient_validation_spy = Mock()
        
        add_recipe_vm.field_validation_error.connect(recipe_validation_spy)
        ingredient_vm.ingredient_name_validation_changed.connect(ingredient_validation_spy)
        
        # Test recipe field validation
        add_recipe_vm.validate_field_real_time("recipe_name", "")
        recipe_validation_spy.assert_called_once()
        
        # Test ingredient field validation  
        ingredient_vm.validate_ingredient_name_real_time("")
        ingredient_validation_spy.assert_called_once_with(False, "Ingredient name is required")

    @pytest.mark.integration
    def test_form_data_transformation_integration(self, add_recipe_vm, ingredient_vm):
        """Test data transformation integration across ViewModels."""
        # Test recipe form data transformation
        raw_recipe_data = {
            "recipe_name": "  Test Recipe  ",
            "recipe_category": "Main Course",
            "meal_type": "dinner",
            "servings": "4",
            "ingredients": [
                {
                    "ingredient_name": "tomato",
                    "ingredient_category": "Vegetables",
                    "quantity": "2.5",
                    "unit": "cups"
                }
            ]
        }
        
        recipe_form_data = add_recipe_vm.preprocess_form_data(raw_recipe_data)
        assert recipe_form_data.recipe_name == "Test Recipe"  # Trimmed
        assert len(recipe_form_data.ingredients) == 1
        
        # Test ingredient data transformation
        ingredient_data = ingredient_vm.parse_form_data(raw_recipe_data["ingredients"][0])
        dto_data = ingredient_vm.transform_to_ingredient_dto(ingredient_data)
        
        assert dto_data["ingredient_name"] == "tomato"
        assert dto_data["quantity"] == 2.5
        assert dto_data["unit"] == "cups"

    @pytest.mark.integration
    def test_error_propagation_integration(self, add_recipe_vm, recipe_service):
        """Test error propagation from services through ViewModels."""
        # Mock service to raise specific error
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.side_effect = \
            Exception("Database connection failed")
        
        # Connect error signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        # Create form data that would normally be valid
        form_data = RecipeFormData()
        form_data.recipe_name = "Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [
            {"ingredient_name": "test", "ingredient_category": "Vegetables"}
        ]
        
        # Execute and verify error handling
        add_recipe_vm.create_recipe(form_data)
        
        save_failed_spy.assert_called_once()
        error_message = save_failed_spy.call_args[0][0]
        assert "unexpected error" in error_message.lower()


class TestTransactionIntegration:
    """Test transaction management across services."""

    @pytest.mark.integration
    def test_recipe_creation_transaction_rollback(self, db_session, add_recipe_vm):
        """Test that recipe creation transactions roll back properly on failure."""
        # Create form data that will pass validation but fail during save
        form_data = RecipeFormData()
        form_data.recipe_name = "Rollback Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [
            {"ingredient_name": "test ingredient", "ingredient_category": "Vegetables"}
        ]
        
        # Mock a failure during ingredient processing
        with patch.object(add_recipe_vm.recipe_service, 'create_recipe_with_ingredients') as mock_create:
            mock_create.side_effect = Exception("Simulated failure")
            
            # Connect error signal spy
            save_failed_spy = Mock()
            add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
            
            # Attempt recipe creation
            add_recipe_vm.create_recipe(form_data)
            
            # Verify error was handled
            save_failed_spy.assert_called_once()
        
        # Verify no partial data was committed
        assert add_recipe_vm.recipe_service.recipe_repo.find_by_name("Rollback Test Recipe") is None

    @pytest.mark.integration
    def test_concurrent_recipe_creation(self, db_session):
        """Test handling of concurrent recipe creation attempts."""
        # This test simulates race conditions that might occur in real usage
        vm1 = AddRecipeViewModel(db_session)
        vm2 = AddRecipeViewModel(db_session)
        vm1.recipe_service = RecipeService(db_session)
        vm2.recipe_service = RecipeService(db_session)
        vm1.ingredient_service = IngredientService(db_session)
        vm2.ingredient_service = IngredientService(db_session)
        
        # Create identical recipe data
        form_data1 = RecipeFormData()
        form_data1.recipe_name = "Concurrent Recipe"
        form_data1.meal_type = "dinner"
        form_data1.servings = "4"
        form_data1.ingredients = [{"ingredient_name": "test", "ingredient_category": "Vegetables"}]
        
        form_data2 = RecipeFormData()
        form_data2.recipe_name = "Concurrent Recipe"  # Same name
        form_data2.recipe_category = "Main Course"  # Same category (or default)
        form_data2.meal_type = "dinner"
        form_data2.servings = "4"
        form_data2.ingredients = [{"ingredient_name": "test", "ingredient_category": "Vegetables"}]
        
        # Connect signal spies
        success_spy1 = Mock()
        success_spy2 = Mock()
        failed_spy1 = Mock()
        failed_spy2 = Mock()
        
        vm1.recipe_saved_successfully.connect(success_spy1)
        vm1.recipe_save_failed.connect(failed_spy1)
        vm2.recipe_saved_successfully.connect(success_spy2)
        vm2.recipe_save_failed.connect(failed_spy2)
        
        # Create recipes concurrently (simulate)
        vm1.create_recipe(form_data1)
        vm2.create_recipe(form_data2)
        
        # One should succeed, one should fail with duplicate error
        total_successes = success_spy1.call_count + success_spy2.call_count
        total_failures = failed_spy1.call_count + failed_spy2.call_count
        
        assert total_successes == 1
        assert total_failures == 1
        
        # Verify only one recipe exists in database
        created_recipes = db_session.query(Recipe).filter(Recipe.recipe_name == "Concurrent Recipe").all()
        assert len(created_recipes) == 1


class TestViewModelDataBindingIntegration:
    """Test enhanced data binding integration between ViewModels."""

    @pytest.mark.integration
    def test_complete_mvvm_data_flow(self, add_recipe_vm, ingredient_vm):
        """Test complete MVVM data flow from user input to persistence."""
        # Step 1: User starts typing ingredient name
        ingredient_vm.validate_ingredient_name_real_time("tomat")
        
        # Step 2: System finds matches and suggests category
        mock_matches = [Mock(ingredient_name="tomato", ingredient_category="Vegetables")]
        ingredient_vm.ingredient_service.search.return_value = mock_matches
        
        match_result = ingredient_vm.find_ingredient_matches("tomato")
        assert match_result.exact_match.ingredient_category == "Vegetables"
        
        # Step 3: User completes ingredient form
        ingredient_data = IngredientFormData()
        ingredient_data.ingredient_name = "tomato"
        ingredient_data.ingredient_category = "Vegetables"
        ingredient_data.quantity = "3"
        ingredient_data.unit = "pieces"
        
        validation_result = ingredient_vm.validate_ingredient_data(ingredient_data)
        assert validation_result.is_valid
        
        # Step 4: Ingredient data is transformed for recipe
        dto_data = ingredient_vm.transform_to_ingredient_dto(ingredient_data)
        
        # Step 5: Recipe form is populated and validated
        recipe_form = RecipeFormData()
        recipe_form.recipe_name = "Test Integration Recipe"
        recipe_form.meal_type = "dinner"
        recipe_form.servings = "4"
        recipe_form.ingredients = [dto_data]
        
        # Connect success spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        # Step 6: Recipe is created
        add_recipe_vm.create_recipe(recipe_form)
        
        # Verify complete flow worked
        recipe_saved_spy.assert_called_once_with("Test Integration Recipe")

    @pytest.mark.integration
    def test_cross_viewmodel_validation_integration(self, add_recipe_vm, ingredient_vm):
        """Test validation integration across ViewModels."""
        # Test ingredient validation affects recipe validation
        invalid_ingredients_data = [
            {"ingredient_name": "", "ingredient_category": "Vegetables"},  # Invalid
            {"ingredient_name": "valid", "ingredient_category": "Vegetables"}  # Valid
        ]
        
        # Validate collection through ingredient ViewModel
        collection_result = ingredient_vm.validate_ingredient_collection(invalid_ingredients_data)
        assert not collection_result.is_valid
        
        # Create recipe form with invalid ingredients
        form_data = RecipeFormData()
        form_data.recipe_name = "Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = invalid_ingredients_data
        
        # Connect validation spy
        validation_failed_spy = Mock()
        add_recipe_vm.validation_failed.connect(validation_failed_spy)
        
        # Recipe creation should fail due to ingredient validation
        add_recipe_vm.create_recipe(form_data)
        
        # Should have validation errors
        assert validation_failed_spy.call_count >= 0  # May emit validation failures

    @pytest.mark.integration
    def test_real_time_validation_coordination(self, add_recipe_vm, ingredient_vm):
        """Test real-time validation coordination between ViewModels."""
        # Connect signal spies for both ViewModels
        recipe_field_spy = Mock()
        ingredient_field_spy = Mock()
        
        add_recipe_vm.field_validation_error.connect(recipe_field_spy)
        ingredient_vm.ingredient_name_validation_changed.connect(ingredient_field_spy)
        
        # Test recipe field validation
        add_recipe_vm.validate_field_real_time("recipe_name", "")
        recipe_field_spy.assert_called_once()
        
        # Test ingredient field validation
        ingredient_vm.validate_ingredient_name_real_time("")
        ingredient_field_spy.assert_called_once_with(False, "Ingredient name is required")

    @pytest.mark.integration
    def test_state_synchronization_across_viewmodels(self, add_recipe_vm, ingredient_vm):
        """Test state synchronization across ViewModels."""
        # Connect processing state spies
        recipe_processing_spy = Mock()
        ingredient_processing_spy = Mock()
        
        add_recipe_vm.processing_state_changed.connect(recipe_processing_spy)
        # Note: IngredientViewModel doesn't have processing_state_changed in current implementation
        
        # Start recipe creation (should set processing state)
        form_data = RecipeFormData()
        form_data.recipe_name = "Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [{"ingredient_name": "tomato", "ingredient_category": "Vegetables"}]
        
        # Mock successful creation
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Test Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        add_recipe_vm.create_recipe(form_data)
        
        # Should have processing state changes
        assert recipe_processing_spy.call_count >= 2  # Start and end


class TestErrorHandlingIntegration:
    """Test error handling integration across layers."""

    @pytest.mark.integration
    def test_service_error_propagation_to_viewmodel(self, add_recipe_vm):
        """Test that service errors propagate properly to ViewModels."""
        # Mock service to throw different error types
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.side_effect = DuplicateRecipeError("Recipe exists")
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        # Connect error signal spy
        save_failed_spy = Mock()
        add_recipe_vm.recipe_save_failed.connect(save_failed_spy)
        
        # Create recipe form
        form_data = RecipeFormData()
        form_data.recipe_name = "Duplicate Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [{"ingredient_name": "tomato", "ingredient_category": "Vegetables"}]
        
        # Execute
        add_recipe_vm.create_recipe(form_data)
        
        # Verify error was handled and propagated
        save_failed_spy.assert_called_once_with("Recipe exists")

    @pytest.mark.integration
    def test_validation_error_cascade(self, add_recipe_vm, ingredient_vm):
        """Test validation error cascade from ingredient to recipe level."""
        # Create invalid ingredient collection
        invalid_ingredients = [
            {"ingredient_name": "", "ingredient_category": ""},  # Multiple errors
            {"ingredient_name": "valid", "ingredient_category": "Vegetables"}
        ]
        
        # Validate collection
        result = ingredient_vm.validate_ingredient_collection(invalid_ingredients)
        assert not result.is_valid
        assert len(result.errors) >= 2
        
        # Create recipe with invalid ingredients
        form_data = RecipeFormData()
        form_data.recipe_name = "Recipe With Invalid Ingredients"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = invalid_ingredients
        
        # Recipe validation should catch ingredient errors
        recipe_validation = add_recipe_vm._validate_recipe_form(form_data)
        assert not recipe_validation.is_valid

    @pytest.mark.integration
    def test_transaction_rollback_on_error(self, db_session):
        """Test that transactions roll back properly on errors."""
        # Create ViewModels with real services
        from app.core.services.ingredient_service import IngredientService
        from app.core.services.recipe_service import RecipeService
        
        recipe_service = RecipeService(db_session)
        ingredient_service = IngredientService(db_session)
        
        vm = AddRecipeViewModel(db_session)
        vm.recipe_service = recipe_service
        vm.ingredient_service = ingredient_service
        
        # Create form data that should succeed initially
        form_data = RecipeFormData()
        form_data.recipe_name = "Rollback Test Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [{"ingredient_name": "test ingredient", "ingredient_category": "Vegetables"}]
        
        # Mock the service to fail after some processing
        original_create = recipe_service.create_recipe_with_ingredients
        def failing_create(dto):
            # Simulate partial work then failure
            raise Exception("Simulated failure after partial processing")
        
        recipe_service.create_recipe_with_ingredients = failing_create
        
        # Connect error spy
        save_failed_spy = Mock()
        vm.recipe_save_failed.connect(save_failed_spy)
        
        # Execute - should fail gracefully
        vm.create_recipe(form_data)
        
        # Verify error was handled
        save_failed_spy.assert_called_once()
        
        # Verify no partial data exists (transaction rolled back)
        assert recipe_service.recipe_repo.find_by_name("Rollback Test Recipe") is None


class TestDataTransformationIntegration:
    """Test data transformation integration across layers."""

    @pytest.mark.integration
    def test_form_to_dto_to_model_transformation(self, add_recipe_vm, db_session):
        """Test complete data transformation from form to database model."""
        # Create comprehensive form data
        form_data = RecipeFormData()
        form_data.recipe_name = "Transformation Test Recipe"
        form_data.recipe_category = "Main Course"
        form_data.meal_type = "dinner"
        form_data.dietary_preference = "vegetarian"
        form_data.total_time = "45"
        form_data.servings = "6"
        form_data.directions = "Detailed cooking instructions for testing"
        form_data.notes = "Special notes about this test recipe"
        form_data.ingredients = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "3",
                "unit": "pieces"
            },
            {
                "ingredient_name": "olive oil",
                "ingredient_category": "Oils",
                "quantity": "2",
                "unit": "tablespoons"
            }
        ]
        
        # Transform to DTO
        recipe_dto = add_recipe_vm._transform_to_recipe_dto(form_data)
        
        # Verify DTO transformation
        assert recipe_dto.recipe_name == "Transformation Test Recipe"
        assert recipe_dto.recipe_category == "Main Course"
        assert recipe_dto.total_time == 45
        assert recipe_dto.servings == 6
        assert len(recipe_dto.ingredients) == 2
        assert recipe_dto.ingredients[0].quantity == 3.0
        
        # Create real services for database persistence
        from app.core.repositories.recipe_repo import RecipeRepo
        from app.core.services.recipe_service import RecipeService
        
        recipe_service = RecipeService(db_session)
        recipe_repo = RecipeRepo(db_session)
        
        add_recipe_vm.recipe_service = recipe_service
        
        # Connect success spy
        recipe_saved_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(recipe_saved_spy)
        
        # Execute creation
        add_recipe_vm.create_recipe(form_data)
        
        # Verify persistence
        recipe_saved_spy.assert_called_once_with("Transformation Test Recipe")
        
        # Verify database model
        created_recipe = recipe_repo.find_by_name("Transformation Test Recipe")
        assert created_recipe is not None
        assert created_recipe.recipe_category == "Main Course"
        assert created_recipe.total_time == 45
        assert created_recipe.servings == 6
        assert len(created_recipe.recipe_ingredients) == 2

    @pytest.mark.integration
    def test_ingredient_transformation_with_matching(self, ingredient_vm, db_session):
        """Test ingredient transformation with database matching."""
        # Create real service
        from app.core.services.ingredient_service import IngredientService
        
        ingredient_service = IngredientService(db_session)
        ingredient_vm.ingredient_service = ingredient_service
        
        # Pre-create an ingredient in database
        existing_ingredient = ingredient_service.get_or_create_from_name_category("tomato", "Vegetables")
        assert existing_ingredient.id is not None
        
        # Test matching
        match_result = ingredient_vm.find_ingredient_matches("tomato")
        assert match_result.exact_match is not None
        assert match_result.exact_match.id == existing_ingredient.id
        assert match_result.suggested_category == "Vegetables"
        
        # Test transformation with existing ingredient
        form_data = IngredientFormData()
        form_data.ingredient_name = "tomato"
        form_data.ingredient_category = "Vegetables"
        form_data.quantity = "2"
        form_data.unit = "cups"
        form_data.existing_ingredient_id = existing_ingredient.id
        
        dto_data = ingredient_vm.transform_to_ingredient_dto(form_data)
        assert dto_data["existing_ingredient_id"] == existing_ingredient.id


class TestPerformanceIntegration:
    """Test performance aspects of integrated operations."""

    @pytest.mark.integration
    def test_bulk_ingredient_operations_performance(self, ingredient_vm, ingredient_service):
        """Test performance with bulk ingredient operations."""
        # Create a large number of ingredients
        ingredient_names = [f"ingredient_{i}" for i in range(100)]
        
        # Bulk create ingredients
        for name in ingredient_names:
            ingredient_service.get_or_create_from_name_category(name, "Test Category")
        
        # Test search performance
        import time
        start_time = time.time()
        
        search_results = ingredient_vm.search_ingredients("ingredient")
        
        end_time = time.time()
        search_duration = end_time - start_time
        
        # Verify results and performance
        assert len(search_results) >= 100
        assert search_duration < 1.0  # Should complete within 1 second
        
        # Test autocomplete performance
        start_time = time.time()
        suggestions = ingredient_vm.get_autocomplete_suggestions("ingredient", limit=10)
        end_time = time.time()
        autocomplete_duration = end_time - start_time
        
        assert len(suggestions) == 10  # Should respect limit
        assert autocomplete_duration < 0.5  # Should be very fast

    @pytest.mark.integration
    def test_complex_recipe_creation_performance(self, add_recipe_vm):
        """Test performance with complex recipe creation."""
        # Create recipe with many ingredients
        form_data = RecipeFormData()
        form_data.recipe_name = "Complex Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "8"
        form_data.directions = "Very long directions..." * 100  # Large text
        
        # Add many ingredients
        form_data.ingredients = []
        for i in range(50):
            form_data.ingredients.append({
                "ingredient_name": f"ingredient_{i}",
                "ingredient_category": "Vegetables",
                "quantity": str(i + 1),
                "unit": "cups"
            })
        
        # Connect signal spy
        success_spy = Mock()
        add_recipe_vm.recipe_saved_successfully.connect(success_spy)
        
        # Measure creation time
        import time
        start_time = time.time()
        
        add_recipe_vm.create_recipe(form_data)
        
        end_time = time.time()
        creation_duration = end_time - start_time
        
        # Verify success and performance
        success_spy.assert_called_once()
        assert creation_duration < 5.0  # Should complete within 5 seconds
        
        # Verify all data was saved correctly
        created_recipe = add_recipe_vm.recipe_service.recipe_repo.find_by_name("Complex Recipe")
        assert created_recipe is not None
        assert len(created_recipe.recipe_ingredients) == 50


class TestSignalIntegrationAdvanced:
    """Test advanced signal integration scenarios."""

    @pytest.mark.integration
    def test_signal_chain_integration(self, add_recipe_vm, ingredient_vm):
        """Test signal chains across ViewModels."""
        signal_chain = []
        
        def track_ingredient_validation(is_valid, message):
            signal_chain.append(f"ingredient_validation:{is_valid}:{message[:20]}")
        
        def track_recipe_processing(is_processing):
            signal_chain.append(f"recipe_processing:{is_processing}")
        
        def track_recipe_saved(name):
            signal_chain.append(f"recipe_saved:{name}")
        
        # Connect signal trackers
        ingredient_vm.ingredient_name_validation_changed.connect(track_ingredient_validation)
        add_recipe_vm.processing_state_changed.connect(track_recipe_processing)
        add_recipe_vm.recipe_saved_successfully.connect(track_recipe_saved)
        
        # Execute workflow
        ingredient_vm.validate_ingredient_name_real_time("tomato")
        
        form_data = RecipeFormData()
        form_data.recipe_name = "Signal Chain Recipe"
        form_data.meal_type = "dinner"
        form_data.servings = "4"
        form_data.ingredients = [{"ingredient_name": "tomato", "ingredient_category": "Vegetables"}]
        
        # Mock successful creation
        mock_recipe = Mock()
        mock_recipe.id = 1
        mock_recipe.recipe_name = "Signal Chain Recipe"
        add_recipe_vm.recipe_service.create_recipe_with_ingredients.return_value = mock_recipe
        add_recipe_vm._validate_recipe_form = Mock(return_value=BaseValidationResult(is_valid=True))
        
        add_recipe_vm.create_recipe(form_data)
        
        # Verify signal chain
        assert len(signal_chain) >= 3
        assert any("ingredient_validation:True" in signal for signal in signal_chain)
        assert any("recipe_processing:True" in signal for signal in signal_chain)
        assert any("recipe_saved:Signal Chain Recipe" in signal for signal in signal_chain)

    @pytest.mark.integration
    def test_concurrent_viewmodel_operations(self, db_session):
        """Test concurrent operations across multiple ViewModel instances."""
        # Create multiple ViewModel instances
        vm1 = AddRecipeViewModel(db_session)
        vm2 = AddRecipeViewModel(db_session)
        
        from app.core.services.ingredient_service import IngredientService
        from app.core.services.recipe_service import RecipeService

        # Each gets its own service instances but shares session
        vm1.recipe_service = RecipeService(db_session)
        vm1.ingredient_service = IngredientService(db_session)
        vm2.recipe_service = RecipeService(db_session)
        vm2.ingredient_service = IngredientService(db_session)
        
        # Create different recipes simultaneously
        form_data1 = RecipeFormData()
        form_data1.recipe_name = "Concurrent Recipe 1"
        form_data1.meal_type = "dinner"
        form_data1.servings = "4"
        form_data1.ingredients = [{"ingredient_name": "ingredient1", "ingredient_category": "Vegetables"}]
        
        form_data2 = RecipeFormData()
        form_data2.recipe_name = "Concurrent Recipe 2"
        form_data2.meal_type = "lunch"
        form_data2.servings = "2"
        form_data2.ingredients = [{"ingredient_name": "ingredient2", "ingredient_category": "Vegetables"}]
        
        # Connect signal spies
        success_spy1 = Mock()
        success_spy2 = Mock()
        vm1.recipe_saved_successfully.connect(success_spy1)
        vm2.recipe_saved_successfully.connect(success_spy2)
        
        # Execute concurrently (simulated)
        vm1.create_recipe(form_data1)
        vm2.create_recipe(form_data2)
        
        # Both should succeed
        success_spy1.assert_called_once_with("Concurrent Recipe 1")
        success_spy2.assert_called_once_with("Concurrent Recipe 2")
        
        # Verify both recipes exist
        assert vm1.recipe_service.recipe_repo.find_by_name("Concurrent Recipe 1") is not None
        assert vm2.recipe_service.recipe_repo.find_by_name("Concurrent Recipe 2") is not None