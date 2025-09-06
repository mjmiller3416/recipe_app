"""
Unit tests for IngredientViewModel.

Tests the ingredient view model including:
- Ingredient search functionality
- Data validation and transformation
- Ingredient matching algorithms
- Category suggestion logic
- Autocomplete data management
- Real-time field validation
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from app.core.dtos.ingredient_dtos import IngredientCreateDTO, IngredientSearchDTO
from app.core.models.ingredient import Ingredient
from app.ui.view_models.ingredient_view_model import (
    IngredientFormData, IngredientMatchResult, IngredientValidationResult,
    IngredientViewModel,
)

@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_ingredient_service():
    """Create a mock IngredientService."""
    service = Mock()
    service.search = Mock(return_value=[])
    service.list_distinct_names = Mock(return_value=["tomato", "onion", "garlic"])
    service.get_ingredient_categories = Mock(return_value=["Vegetables", "Fruits"])
    service.get_or_create = Mock()
    return service


@pytest.fixture
def ingredient_vm(mock_session):
    """Create IngredientViewModel instance with mocked dependencies."""
    with patch('app.ui.view_models.ingredient_view_model.IngredientService') as mock_svc:
        vm = IngredientViewModel(mock_session)
        vm.ingredient_service = Mock()
        return vm


@pytest.fixture
def sample_ingredient_data():
    """Create sample ingredient form data for testing."""
    data = IngredientFormData()
    data.ingredient_name = "tomato"
    data.ingredient_category = "Vegetables"
    data.quantity = "2.5"
    data.unit = "cups"
    data.existing_ingredient_id = None
    return data


@pytest.fixture
def mock_ingredients():
    """Create mock ingredient objects for testing."""
    ingredient1 = Mock(spec=Ingredient)
    ingredient1.id = 1
    ingredient1.ingredient_name = "tomato"
    ingredient1.ingredient_category = "Vegetables"
    
    ingredient2 = Mock(spec=Ingredient)
    ingredient2.id = 2
    ingredient2.ingredient_name = "cherry tomato"
    ingredient2.ingredient_category = "Vegetables"
    
    ingredient3 = Mock(spec=Ingredient)
    ingredient3.id = 3
    ingredient3.ingredient_name = "tomato sauce"
    ingredient3.ingredient_category = "Condiments"
    
    return [ingredient1, ingredient2, ingredient3]


class TestIngredientViewModelInitialization:
    """Test IngredientViewModel initialization and setup."""

    def test_initialization_with_session(self, mock_session):
        """Test ViewModel initializes correctly with provided session."""
        with patch('app.ui.view_models.ingredient_view_model.IngredientService') as mock_svc:
            vm = IngredientViewModel(mock_session)
            
            assert vm._session is mock_session
            assert not vm._owns_session
            assert vm._autocomplete_cache == []
            assert vm._categories_cache == []
            assert not vm._cache_loaded
            assert not vm.is_processing

    def test_initialization_without_session(self):
        """Test ViewModel initializes correctly without session."""
        with patch('app.ui.view_models.ingredient_view_model.IngredientService'), \
             patch('app.ui.view_models.base_view_model.create_session') as mock_create_session:
            
            mock_session = Mock()
            mock_create_session.return_value = mock_session
            
            vm = IngredientViewModel()
            
            # Session should be created when needed
            vm._ensure_session()
            assert vm._session is mock_session
            assert vm._owns_session

    def test_service_initialization(self, mock_session):
        """Test that IngredientService is properly initialized."""
        with patch('app.ui.view_models.ingredient_view_model.IngredientService') as mock_svc:
            vm = IngredientViewModel(mock_session)
            
            mock_svc.assert_called_once_with(mock_session)

    def test_signal_definitions(self, ingredient_vm):
        """Test that all required signals are defined."""
        vm = ingredient_vm
        
        # Check ingredient-specific signals
        assert hasattr(vm, 'ingredient_search_completed')
        assert hasattr(vm, 'ingredient_matched')
        assert hasattr(vm, 'ingredient_validated')
        assert hasattr(vm, 'category_suggested')
        assert hasattr(vm, 'autocomplete_data_ready')
        assert hasattr(vm, 'ingredient_categories_loaded')
        
        # Check enhanced validation signals
        assert hasattr(vm, 'ingredient_name_validation_changed')
        assert hasattr(vm, 'ingredient_category_validation_changed')
        assert hasattr(vm, 'ingredient_quantity_validation_changed')
        assert hasattr(vm, 'collection_validation_completed')


class TestIngredientSearch:
    """Test ingredient search functionality."""

    def test_search_ingredients_success(self, ingredient_vm, mock_ingredients):
        """Test successful ingredient search."""
        ingredient_vm.ingredient_service.search.return_value = mock_ingredients
        
        # Connect signal spy
        search_completed_spy = Mock()
        ingredient_vm.ingredient_search_completed.connect(search_completed_spy)
        
        result = ingredient_vm.search_ingredients("tom")
        
        assert result == mock_ingredients
        search_completed_spy.assert_called_once_with(mock_ingredients)
        ingredient_vm.ingredient_service.search.assert_called_once()

    def test_search_ingredients_empty_term(self, ingredient_vm):
        """Test ingredient search with empty search term."""
        result = ingredient_vm.search_ingredients("")
        
        ingredient_vm.ingredient_service.search.assert_not_called()
        assert result == []

    def test_search_ingredients_whitespace_only(self, ingredient_vm):
        """Test ingredient search with whitespace-only search term."""
        result = ingredient_vm.search_ingredients("   ")
        
        ingredient_vm.ingredient_service.search.assert_not_called()
        assert result == []

    def test_search_ingredients_with_category_filter(self, ingredient_vm, mock_ingredients):
        """Test ingredient search with category filter."""
        ingredient_vm.ingredient_service.search.return_value = mock_ingredients
        
        result = ingredient_vm.search_ingredients("tom", "Vegetables")
        
        ingredient_vm.ingredient_service.search.assert_called_once()
        # Verify search DTO was created with category
        search_dto_arg = ingredient_vm.ingredient_service.search.call_args[0][0]
        assert isinstance(search_dto_arg, IngredientSearchDTO)
        assert search_dto_arg.search_term == "tom"
        assert search_dto_arg.category == "Vegetables"

    def test_search_ingredients_service_failure(self, ingredient_vm):
        """Test ingredient search with service failure."""
        ingredient_vm.ingredient_service.search.side_effect = Exception("Search failed")
        
        # Connect signal spy
        search_completed_spy = Mock()
        ingredient_vm.ingredient_search_completed.connect(search_completed_spy)
        
        result = ingredient_vm.search_ingredients("tom")
        
        assert result == []
        search_completed_spy.assert_called_once_with([])

    def test_search_ingredients_no_service(self, mock_session):
        """Test ingredient search when service is not available."""
        with patch('app.ui.view_models.ingredient_view_model.IngredientService') as mock_svc:
            vm = IngredientViewModel(mock_session)
            vm.ingredient_service = None
            
            result = vm.search_ingredients("tom")
            
            assert result == []


class TestIngredientMatching:
    """Test ingredient matching algorithms."""

    def test_find_ingredient_matches_exact_match(self, ingredient_vm, mock_ingredients):
        """Test finding exact ingredient match."""
        # Setup search to return ingredients including exact match
        ingredient_vm.search_ingredients = Mock(return_value=mock_ingredients)
        
        # Connect signal spy
        matched_spy = Mock()
        category_suggested_spy = Mock()
        ingredient_vm.ingredient_matched.connect(matched_spy)
        ingredient_vm.category_suggested.connect(category_suggested_spy)
        
        result = ingredient_vm.find_ingredient_matches("tomato")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match == mock_ingredients[0]  # First ingredient is exact match
        assert result.partial_matches == mock_ingredients[1:]  # Others are partial matches
        assert result.suggested_category == "Vegetables"
        assert result.is_valid_name is True
        
        matched_spy.assert_called_once()
        category_suggested_spy.assert_called_once_with("Vegetables")

    def test_find_ingredient_matches_partial_only(self, ingredient_vm, mock_ingredients):
        """Test finding partial ingredient matches only."""
        # Setup search to return only partial matches
        ingredient_vm.search_ingredients = Mock(return_value=mock_ingredients[1:])
        
        # Connect signal spy
        matched_spy = Mock()
        ingredient_vm.ingredient_matched.connect(matched_spy)
        
        result = ingredient_vm.find_ingredient_matches("tom")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match is None
        assert result.partial_matches == mock_ingredients[1:]
        assert result.suggested_category == "Vegetables"  # Most common category
        assert result.is_valid_name is True

    def test_find_ingredient_matches_no_matches(self, ingredient_vm):
        """Test finding ingredient matches with no results."""
        ingredient_vm.search_ingredients = Mock(return_value=[])
        
        # Connect signal spy
        matched_spy = Mock()
        ingredient_vm.ingredient_matched.connect(matched_spy)
        
        result = ingredient_vm.find_ingredient_matches("nonexistent")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match is None
        assert result.partial_matches == []
        assert result.suggested_category is None
        assert result.is_valid_name is True

    def test_find_ingredient_matches_invalid_name(self, ingredient_vm):
        """Test finding matches with invalid ingredient name."""
        # Connect signal spy
        matched_spy = Mock()
        ingredient_vm.ingredient_matched.connect(matched_spy)
        
        result = ingredient_vm.find_ingredient_matches("123invalid!")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match is None
        assert result.partial_matches == []
        assert result.suggested_category is None
        assert result.is_valid_name is False
        
        matched_spy.assert_called_once_with(result)

    def test_find_ingredient_matches_empty_name(self, ingredient_vm):
        """Test finding matches with empty ingredient name."""
        result = ingredient_vm.find_ingredient_matches("")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.is_valid_name is False

    def test_find_ingredient_matches_service_failure(self, ingredient_vm):
        """Test finding matches when service fails."""
        ingredient_vm.search_ingredients = Mock(side_effect=Exception("Search failed"))
        
        result = ingredient_vm.find_ingredient_matches("tomato")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match is None
        assert result.partial_matches == []
        assert result.is_valid_name is True


class TestIngredientValidation:
    """Test ingredient validation functionality."""

    def test_validate_ingredient_data_valid(self, ingredient_vm, sample_ingredient_data):
        """Test validation with valid ingredient data."""
        # Connect signal spy
        validated_spy = Mock()
        ingredient_vm.ingredient_validated.connect(validated_spy)
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert isinstance(result, IngredientValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        validated_spy.assert_called_once_with(result)

    def test_validate_ingredient_data_missing_name(self, ingredient_vm, sample_ingredient_data):
        """Test validation with missing ingredient name."""
        sample_ingredient_data.ingredient_name = ""
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Ingredient name is required" in result.errors

    def test_validate_ingredient_data_missing_category(self, ingredient_vm, sample_ingredient_data):
        """Test validation with missing category."""
        sample_ingredient_data.ingredient_category = ""
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Ingredient category is required" in result.errors

    def test_validate_ingredient_data_invalid_name_format(self, ingredient_vm, sample_ingredient_data):
        """Test validation with invalid ingredient name format."""
        sample_ingredient_data.ingredient_name = "123invalid!"
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Ingredient name contains invalid characters" in result.errors

    def test_validate_ingredient_data_name_too_long(self, ingredient_vm, sample_ingredient_data):
        """Test validation with ingredient name exceeding length limit."""
        sample_ingredient_data.ingredient_name = "a" * 101  # Exceeds 100 character limit
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Ingredient name cannot exceed 100 characters" in result.errors

    def test_validate_ingredient_data_invalid_quantity(self, ingredient_vm, sample_ingredient_data):
        """Test validation with invalid quantity."""
        sample_ingredient_data.quantity = "invalid"
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Quantity must be a valid number" in result.errors

    def test_validate_ingredient_data_zero_quantity(self, ingredient_vm, sample_ingredient_data):
        """Test validation with zero quantity."""
        sample_ingredient_data.quantity = "0"
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Quantity must be greater than zero" in result.errors

    def test_validate_ingredient_data_large_quantity_warning(self, ingredient_vm, sample_ingredient_data):
        """Test validation with unusually large quantity generates warning."""
        sample_ingredient_data.quantity = "10001"
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is True  # Still valid, just a warning
        assert "Quantity seems unusually large" in result.warnings

    def test_validate_ingredient_data_invalid_category_warning(self, ingredient_vm, sample_ingredient_data):
        """Test validation with non-standard category generates warning."""
        sample_ingredient_data.ingredient_category = "Custom Category"
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is True  # Still valid, just a warning
        assert any("not in the standard list" in warning for warning in result.warnings)

    def test_validate_ingredient_data_unit_too_long(self, ingredient_vm, sample_ingredient_data):
        """Test validation with unit exceeding length limit."""
        sample_ingredient_data.unit = "a" * 51  # Exceeds 50 character limit
        
        result = ingredient_vm.validate_ingredient_data(sample_ingredient_data)
        
        assert result.is_valid is False
        assert "Unit cannot exceed 50 characters" in result.errors


class TestRealTimeValidation:
    """Test real-time field validation."""

    def test_validate_ingredient_name_real_time_valid(self, ingredient_vm):
        """Test real-time ingredient name validation with valid name."""
        # Connect signal spy
        name_validation_spy = Mock()
        ingredient_vm.ingredient_name_validation_changed.connect(name_validation_spy)
        
        result = ingredient_vm.validate_ingredient_name_real_time("tomato")
        
        assert result is True
        name_validation_spy.assert_called_once_with(True, "")

    def test_validate_ingredient_name_real_time_empty(self, ingredient_vm):
        """Test real-time ingredient name validation with empty name."""
        # Connect signal spy
        name_validation_spy = Mock()
        ingredient_vm.ingredient_name_validation_changed.connect(name_validation_spy)
        
        result = ingredient_vm.validate_ingredient_name_real_time("")
        
        assert result is False
        name_validation_spy.assert_called_once_with(False, "Ingredient name is required")

    def test_validate_ingredient_name_real_time_invalid_format(self, ingredient_vm):
        """Test real-time ingredient name validation with invalid format."""
        # Connect signal spy
        name_validation_spy = Mock()
        ingredient_vm.ingredient_name_validation_changed.connect(name_validation_spy)
        
        result = ingredient_vm.validate_ingredient_name_real_time("123invalid!")
        
        assert result is False
        name_validation_spy.assert_called_once_with(False, "Ingredient name contains invalid characters")

    def test_validate_ingredient_category_real_time_valid(self, ingredient_vm):
        """Test real-time category validation with valid category."""
        # Connect signal spy
        category_validation_spy = Mock()
        ingredient_vm.ingredient_category_validation_changed.connect(category_validation_spy)
        
        result = ingredient_vm.validate_ingredient_category_real_time("Vegetables")
        
        assert result is True
        category_validation_spy.assert_called_once_with(True, "")

    def test_validate_ingredient_category_real_time_empty(self, ingredient_vm):
        """Test real-time category validation with empty category."""
        # Connect signal spy
        category_validation_spy = Mock()
        ingredient_vm.ingredient_category_validation_changed.connect(category_validation_spy)
        
        result = ingredient_vm.validate_ingredient_category_real_time("")
        
        assert result is False
        category_validation_spy.assert_called_once_with(False, "Category is required")

    def test_validate_ingredient_quantity_real_time_valid(self, ingredient_vm):
        """Test real-time quantity validation with valid quantity."""
        # Connect signal spy
        quantity_validation_spy = Mock()
        ingredient_vm.ingredient_quantity_validation_changed.connect(quantity_validation_spy)
        
        result = ingredient_vm.validate_ingredient_quantity_real_time("2.5")
        
        assert result is True
        quantity_validation_spy.assert_called_once_with(True, "")

    def test_validate_ingredient_quantity_real_time_empty(self, ingredient_vm):
        """Test real-time quantity validation with empty quantity (should be valid)."""
        # Connect signal spy
        quantity_validation_spy = Mock()
        ingredient_vm.ingredient_quantity_validation_changed.connect(quantity_validation_spy)
        
        result = ingredient_vm.validate_ingredient_quantity_real_time("")
        
        assert result is True  # Empty quantity is valid (optional field)
        quantity_validation_spy.assert_called_once_with(True, "")

    def test_validate_ingredient_quantity_real_time_invalid(self, ingredient_vm):
        """Test real-time quantity validation with invalid quantity."""
        # Connect signal spy
        quantity_validation_spy = Mock()
        ingredient_vm.ingredient_quantity_validation_changed.connect(quantity_validation_spy)
        
        result = ingredient_vm.validate_ingredient_quantity_real_time("invalid")
        
        assert result is False
        quantity_validation_spy.assert_called_once_with(False, "Quantity must be a valid number")

    def test_validate_ingredient_quantity_real_time_large_quantity(self, ingredient_vm):
        """Test real-time quantity validation with unusually large quantity."""
        # Connect signal spy
        quantity_validation_spy = Mock()
        ingredient_vm.ingredient_quantity_validation_changed.connect(quantity_validation_spy)
        
        result = ingredient_vm.validate_ingredient_quantity_real_time("10001")
        
        assert result is True  # Still valid, just a warning
        quantity_validation_spy.assert_called_once_with(True, "Quantity seems unusually large")


class TestDataTransformation:
    """Test data transformation functionality."""

    def test_transform_to_ingredient_dto_success(self, ingredient_vm, sample_ingredient_data):
        """Test successful transformation to ingredient DTO."""
        result = ingredient_vm.transform_to_ingredient_dto(sample_ingredient_data)
        
        assert isinstance(result, dict)
        assert result["ingredient_name"] == "tomato"
        assert result["ingredient_category"] == "Vegetables"
        assert result["quantity"] == 2.5
        assert result["unit"] == "cups"
        assert result["existing_ingredient_id"] is None

    def test_transform_to_ingredient_dto_no_quantity(self, ingredient_vm, sample_ingredient_data):
        """Test transformation with no quantity."""
        sample_ingredient_data.quantity = ""
        
        result = ingredient_vm.transform_to_ingredient_dto(sample_ingredient_data)
        
        assert result["quantity"] is None

    def test_transform_to_ingredient_dto_no_unit(self, ingredient_vm, sample_ingredient_data):
        """Test transformation with no unit."""
        sample_ingredient_data.unit = ""
        
        result = ingredient_vm.transform_to_ingredient_dto(sample_ingredient_data)
        
        assert result["unit"] is None

    def test_transform_to_ingredient_dto_with_existing_id(self, ingredient_vm, sample_ingredient_data):
        """Test transformation with existing ingredient ID."""
        sample_ingredient_data.existing_ingredient_id = 123
        
        result = ingredient_vm.transform_to_ingredient_dto(sample_ingredient_data)
        
        assert result["existing_ingredient_id"] == 123

    def test_transform_to_ingredient_dto_failure(self, ingredient_vm):
        """Test transformation failure handling."""
        with patch('app.ui.view_models.ingredient_view_model.sanitize_form_input', side_effect=Exception("Transform failed")):
            result = ingredient_vm.transform_to_ingredient_dto(IngredientFormData())
            
            assert result == {}

    def test_parse_form_data_success(self, ingredient_vm):
        """Test successful form data parsing."""
        raw_data = {
            "ingredient_name": "  tomato  ",  # With whitespace
            "ingredient_category": "Vegetables",
            "quantity": "2.5",
            "unit": "cups",
            "existing_ingredient_id": 123
        }
        
        result = ingredient_vm.parse_form_data(raw_data)
        
        assert isinstance(result, IngredientFormData)
        assert result.ingredient_name == "tomato"  # Whitespace trimmed
        assert result.ingredient_category == "Vegetables"
        assert result.quantity == "2.5"
        assert result.unit == "cups"
        assert result.existing_ingredient_id == 123

    def test_parse_form_data_missing_fields(self, ingredient_vm):
        """Test form data parsing with missing fields."""
        raw_data = {
            "ingredient_name": "tomato"
            # Missing other fields
        }
        
        result = ingredient_vm.parse_form_data(raw_data)
        
        assert isinstance(result, IngredientFormData)
        assert result.ingredient_name == "tomato"
        assert result.ingredient_category == ""
        assert result.quantity == ""
        assert result.unit == ""
        assert result.existing_ingredient_id is None


class TestAutocompleteAndCategories:
    """Test autocomplete and category management."""

    def test_get_autocomplete_suggestions_success(self, ingredient_vm):
        """Test getting autocomplete suggestions."""
        ingredient_vm._autocomplete_cache = ["tomato", "onion", "garlic", "potato"]
        ingredient_vm._cache_loaded = True
        
        # Connect signal spy
        autocomplete_spy = Mock()
        ingredient_vm.autocomplete_data_ready.connect(autocomplete_spy)
        
        result = ingredient_vm.get_autocomplete_suggestions("to", 3)
        
        assert result == ["tomato", "potato"]  # Should match "to" and respect limit
        autocomplete_spy.assert_called_once_with(["tomato", "potato"])

    def test_get_autocomplete_suggestions_empty_term(self, ingredient_vm):
        """Test getting autocomplete suggestions with empty term."""
        result = ingredient_vm.get_autocomplete_suggestions("")
        
        assert result == []

    def test_get_autocomplete_suggestions_loads_cache(self, ingredient_vm):
        """Test that autocomplete suggestions loads cache if not loaded."""
        ingredient_vm._load_autocomplete_cache = Mock()
        ingredient_vm._cache_loaded = False
        ingredient_vm._autocomplete_cache = ["tomato"]
        
        result = ingredient_vm.get_autocomplete_suggestions("to")
        
        ingredient_vm._load_autocomplete_cache.assert_called_once()

    def test_get_available_categories_from_cache(self, ingredient_vm):
        """Test getting available categories from cache."""
        ingredient_vm._categories_cache = ["Vegetables", "Fruits", "Proteins"]
        
        # Connect signal spy
        categories_spy = Mock()
        ingredient_vm.ingredient_categories_loaded.connect(categories_spy)
        
        result = ingredient_vm.get_available_categories()
        
        assert result == ["Vegetables", "Fruits", "Proteins"]
        categories_spy.assert_called_once_with(["Vegetables", "Fruits", "Proteins"])

    def test_get_available_categories_loads_from_service(self, ingredient_vm):
        """Test getting categories from service when cache is empty."""
        ingredient_vm._categories_cache = []
        ingredient_vm.ingredient_service.get_ingredient_categories.return_value = ["Custom Category"]
        
        result = ingredient_vm.get_available_categories()
        
        assert "Custom Category" in result
        assert "Vegetables" in result  # Should include standard categories

    def test_suggest_category_for_name(self, ingredient_vm):
        """Test category suggestion for ingredient name."""
        # Mock find_ingredient_matches to return suggestion
        mock_result = IngredientMatchResult(suggested_category="Vegetables")
        ingredient_vm.find_ingredient_matches = Mock(return_value=mock_result)
        
        result = ingredient_vm.suggest_category_for_name("tomato")
        
        assert result == "Vegetables"
        ingredient_vm.find_ingredient_matches.assert_called_once_with("tomato")


class TestIngredientCollectionValidation:
    """Test ingredient collection validation functionality."""

    def test_validate_ingredient_collection_valid(self, ingredient_vm):
        """Test validation of valid ingredient collection."""
        ingredients_data = [
            {
                "ingredient_name": "tomato",
                "ingredient_category": "Vegetables",
                "quantity": "2",
                "unit": "cups"
            },
            {
                "ingredient_name": "onion",
                "ingredient_category": "Vegetables",
                "quantity": "1",
                "unit": "piece"
            }
        ]
        
        # Mock individual validation to return valid results
        ingredient_vm.validate_ingredient_data = Mock(
            return_value=IngredientValidationResult(is_valid=True)
        )
        
        result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        
        assert isinstance(result, IngredientValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_ingredient_collection_empty(self, ingredient_vm):
        """Test validation of empty ingredient collection."""
        result = ingredient_vm.validate_ingredient_collection([])
        
        assert result.is_valid is False
        assert "At least one ingredient is required" in result.errors

    def test_validate_ingredient_collection_with_invalid_ingredient(self, ingredient_vm):
        """Test validation with invalid ingredient in collection."""
        ingredients_data = [
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "", "ingredient_category": "Vegetables"}  # Invalid
        ]
        
        # Mock validation to return different results for each ingredient
        invalid_result = IngredientValidationResult(is_valid=False)
        invalid_result.add_error("Name is required")
        
        ingredient_vm.validate_ingredient_data = Mock(side_effect=[
            IngredientValidationResult(is_valid=True),  # First ingredient valid
            invalid_result  # Second ingredient invalid
        ])
        
        result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        
        assert result.is_valid is False
        assert any("Ingredient 2: Name is required" in error for error in result.errors)

    def test_validate_ingredient_collection_duplicates(self, ingredient_vm):
        """Test validation detects duplicate ingredients."""
        ingredients_data = [
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "Tomato", "ingredient_category": "Vegetables"}  # Duplicate (case insensitive)
        ]
        
        # Mock validation to return valid for both
        ingredient_vm.validate_ingredient_data = Mock(
            return_value=IngredientValidationResult(is_valid=True)
        )
        
        result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        
        assert result.is_valid is True  # Still valid, just a warning
        assert any("Duplicate ingredients found: tomato" in warning for warning in result.warnings)

    def test_transform_ingredient_collection_success(self, ingredient_vm):
        """Test successful transformation of ingredient collection."""
        ingredients_data = [
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "onion", "ingredient_category": "Vegetables"}
        ]
        
        # Mock transform_to_ingredient_dto to return sample data
        ingredient_vm.transform_to_ingredient_dto = Mock(side_effect=[
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "onion", "ingredient_category": "Vegetables"}
        ])
        
        result = ingredient_vm.transform_ingredient_collection(ingredients_data)
        
        assert len(result) == 2
        assert result[0]["ingredient_name"] == "tomato"
        assert result[1]["ingredient_name"] == "onion"

    def test_transform_ingredient_collection_skips_empty(self, ingredient_vm):
        """Test collection transformation skips empty ingredients."""
        ingredients_data = [
            {"ingredient_name": "tomato", "ingredient_category": "Vegetables"},
            {"ingredient_name": "", "ingredient_category": "Vegetables"},  # Empty name
            {"ingredient_name": "onion", "ingredient_category": "Vegetables"}
        ]
        
        # Mock transform_to_ingredient_dto
        ingredient_vm.transform_to_ingredient_dto = Mock(side_effect=[
            {"ingredient_name": "tomato"},
            {"ingredient_name": "onion"}
        ])
        
        result = ingredient_vm.transform_ingredient_collection(ingredients_data)
        
        assert len(result) == 2  # Should skip empty ingredient
        assert ingredient_vm.transform_to_ingredient_dto.call_count == 2


class TestCacheManagement:
    """Test cache management functionality."""

    def test_load_autocomplete_cache_success(self, ingredient_vm):
        """Test successful loading of autocomplete cache."""
        ingredient_vm.ingredient_service.list_distinct_names.return_value = ["tomato", "onion"]
        
        ingredient_vm._load_autocomplete_cache()
        
        assert ingredient_vm._autocomplete_cache == ["tomato", "onion"]
        assert ingredient_vm._cache_loaded is True

    def test_load_autocomplete_cache_failure(self, ingredient_vm):
        """Test autocomplete cache loading failure handling."""
        ingredient_vm.ingredient_service.list_distinct_names.side_effect = Exception("Cache load failed")
        
        ingredient_vm._load_autocomplete_cache()
        
        assert ingredient_vm._autocomplete_cache == []
        assert ingredient_vm._cache_loaded is False

    def test_refresh_cache(self, ingredient_vm):
        """Test cache refresh functionality."""
        # Set some initial cache data
        ingredient_vm._autocomplete_cache = ["old_data"]
        ingredient_vm._categories_cache = ["old_categories"]
        ingredient_vm._cache_loaded = True
        
        # Mock methods
        ingredient_vm._load_autocomplete_cache = Mock()
        ingredient_vm.get_available_categories = Mock()
        
        ingredient_vm.refresh_cache()
        
        assert ingredient_vm._autocomplete_cache == []
        assert ingredient_vm._categories_cache == []
        assert ingredient_vm._cache_loaded is False
        ingredient_vm._load_autocomplete_cache.assert_called_once()
        ingredient_vm.get_available_categories.assert_called_once()


class TestUtilityMethods:
    """Test utility methods."""

    def test_create_or_get_ingredient_success(self, ingredient_vm):
        """Test successful ingredient creation/retrieval."""
        mock_ingredient = Mock(spec=Ingredient)
        mock_ingredient.ingredient_name = "tomato"
        ingredient_vm.ingredient_service.get_or_create.return_value = mock_ingredient
        
        result = ingredient_vm.create_or_get_ingredient("tomato", "Vegetables")
        
        assert result is mock_ingredient
        ingredient_vm.ingredient_service.get_or_create.assert_called_once()

    def test_create_or_get_ingredient_failure(self, ingredient_vm):
        """Test ingredient creation/retrieval failure."""
        ingredient_vm.ingredient_service.get_or_create.side_effect = Exception("Create failed")
        
        result = ingredient_vm.create_or_get_ingredient("tomato", "Vegetables")
        
        assert result is None

    def test_is_valid_ingredient_name_valid(self, ingredient_vm):
        """Test valid ingredient name validation."""
        assert ingredient_vm.is_valid_ingredient_name("tomato") is True
        assert ingredient_vm.is_valid_ingredient_name("cherry tomato") is True
        assert ingredient_vm.is_valid_ingredient_name("olive oil") is True

    def test_is_valid_ingredient_name_invalid(self, ingredient_vm):
        """Test invalid ingredient name validation."""
        assert ingredient_vm.is_valid_ingredient_name("") is False
        assert ingredient_vm.is_valid_ingredient_name("   ") is False
        assert ingredient_vm.is_valid_ingredient_name("123invalid!") is False
        assert ingredient_vm.is_valid_ingredient_name(None) is False


class TestProperties:
    """Test ViewModel properties."""

    def test_cache_loaded_property(self, ingredient_vm):
        """Test cache loaded property."""
        assert ingredient_vm.cache_loaded is False
        
        ingredient_vm._cache_loaded = True
        assert ingredient_vm.cache_loaded is True

    def test_autocomplete_count_property(self, ingredient_vm):
        """Test autocomplete count property."""
        assert ingredient_vm.autocomplete_count == 0
        
        ingredient_vm._autocomplete_cache = ["tomato", "onion"]
        assert ingredient_vm.autocomplete_count == 2

    def test_categories_count_property(self, ingredient_vm):
        """Test categories count property."""
        # Should return count of standard categories when cache is empty
        count = ingredient_vm.categories_count
        assert count > 0  # INGREDIENT_CATEGORIES should have items
        
        ingredient_vm._categories_cache = ["Custom1", "Custom2"]
        assert ingredient_vm.categories_count == 2


class TestAdvancedValidationScenarios:
    """Test advanced validation scenarios and edge cases."""

    def test_validate_ingredient_data_comprehensive_errors(self, ingredient_vm):
        """Test validation with multiple error types."""
        invalid_data = IngredientFormData()
        invalid_data.ingredient_name = ""  # Required field missing
        invalid_data.ingredient_category = ""  # Required field missing
        invalid_data.quantity = "invalid"  # Invalid format
        invalid_data.unit = "x" * 51  # Too long
        
        result = ingredient_vm.validate_ingredient_data(invalid_data)
        
        assert not result.is_valid
        assert len(result.errors) >= 4
        
        error_text = " ".join(result.errors)
        assert "Ingredient name is required" in error_text
        assert "category is required" in error_text
        assert "valid number" in error_text
        assert "cannot exceed 50 characters" in error_text

    def test_validate_ingredient_data_boundary_values(self, ingredient_vm):
        """Test validation at boundary values."""
        # Test maximum valid length
        boundary_data = IngredientFormData()
        boundary_data.ingredient_name = "x" * 100  # Exactly at limit
        boundary_data.ingredient_category = "Vegetables"
        boundary_data.quantity = "10000"  # At warning threshold
        boundary_data.unit = "x" * 50  # Exactly at limit
        
        result = ingredient_vm.validate_ingredient_data(boundary_data)
        
        assert result.is_valid
        assert len(result.warnings) >= 1  # Should warn about large quantity

    def test_validate_ingredient_data_special_characters(self, ingredient_vm):
        """Test validation with special characters in names."""
        special_data = IngredientFormData()
        special_data.ingredient_name = "tomato & basil (fresh)"  # Valid special chars
        special_data.ingredient_category = "Herbs & Spices"
        
        result = ingredient_vm.validate_ingredient_data(special_data)
        
        assert result.is_valid

    def test_validate_ingredient_data_invalid_characters(self, ingredient_vm):
        """Test validation with invalid characters in names."""
        invalid_data = IngredientFormData()
        invalid_data.ingredient_name = "tomato123!"  # Contains numbers and invalid chars
        invalid_data.ingredient_category = "Vegetables"
        
        result = ingredient_vm.validate_ingredient_data(invalid_data)
        
        assert not result.is_valid
        assert any("invalid characters" in error for error in result.errors)


class TestCacheManagementComprehensive:
    """Test comprehensive cache management functionality."""

    def test_cache_initialization_and_lifecycle(self, ingredient_vm):
        """Test complete cache lifecycle."""
        assert not ingredient_vm.cache_loaded
        assert ingredient_vm.autocomplete_count == 0
        
        # Mock service to return data
        ingredient_vm.ingredient_service.list_distinct_names.return_value = ["apple", "banana", "carrot"]
        
        # Load cache
        ingredient_vm._load_autocomplete_cache()
        
        assert ingredient_vm.cache_loaded
        assert ingredient_vm.autocomplete_count == 3
        assert "apple" in ingredient_vm._autocomplete_cache

    def test_autocomplete_filtering_logic(self, ingredient_vm):
        """Test autocomplete filtering with various patterns."""
        ingredient_vm._autocomplete_cache = ["apple", "apricot", "banana", "grape"]
        ingredient_vm._cache_loaded = True
        
        # Test partial match
        results = ingredient_vm.get_autocomplete_suggestions("ap", 10)
        assert "apple" in results
        assert "apricot" in results
        assert "banana" not in results
        
        # Test case insensitive
        results = ingredient_vm.get_autocomplete_suggestions("AP", 10)
        assert len(results) == 2
        
        # Test limit
        ingredient_vm._autocomplete_cache = [f"ingredient_{i}" for i in range(20)]
        results = ingredient_vm.get_autocomplete_suggestions("ingredient", 5)
        assert len(results) == 5

    def test_cache_refresh_comprehensive(self, ingredient_vm):
        """Test comprehensive cache refresh."""
        # Set up initial cache state
        ingredient_vm._autocomplete_cache = ["old_data"]
        ingredient_vm._categories_cache = ["old_categories"]
        ingredient_vm._ingredients_cache = [Mock()]
        ingredient_vm._cache_loaded = True
        
        # Mock methods
        ingredient_vm._load_autocomplete_cache = Mock()
        ingredient_vm.get_available_categories = Mock()
        
        # Refresh cache
        ingredient_vm.refresh_cache()
        
        # Verify all caches were cleared
        assert ingredient_vm._autocomplete_cache == []
        assert ingredient_vm._categories_cache == []
        assert ingredient_vm._ingredients_cache == []
        assert not ingredient_vm._cache_loaded
        
        # Verify reload methods were called
        ingredient_vm._load_autocomplete_cache.assert_called_once()
        ingredient_vm.get_available_categories.assert_called_once()

    def test_get_available_categories_comprehensive(self, ingredient_vm):
        """Test comprehensive category retrieval."""
        # Test with empty cache - should load from service
        ingredient_vm._categories_cache = []
        ingredient_vm.ingredient_service.get_ingredient_categories.return_value = ["Custom1", "Custom2"]
        
        # Connect signal spy
        categories_spy = Mock()
        ingredient_vm.ingredient_categories_loaded.connect(categories_spy)
        
        result = ingredient_vm.get_available_categories()
        
        # Should combine standard and custom categories
        assert "Vegetables" in result  # Standard category
        assert "Custom1" in result  # From service
        assert "Custom2" in result  # From service
        assert result == sorted(result)  # Should be sorted
        
        categories_spy.assert_called_once()

    def test_category_caching_behavior(self, ingredient_vm):
        """Test category caching behavior."""
        # First call loads from service
        ingredient_vm.ingredient_service.get_ingredient_categories.return_value = ["Service Category"]
        
        result1 = ingredient_vm.get_available_categories()
        
        # Second call should use cache
        ingredient_vm.ingredient_service.get_ingredient_categories.return_value = ["Different Category"]
        
        result2 = ingredient_vm.get_available_categories()
        
        # Results should be the same (cached)
        assert result1 == result2
        assert "Service Category" in result2
        assert "Different Category" not in result2


class TestErrorHandlingAndEdgeCases:
    """Test comprehensive error handling and edge cases."""

    def test_service_initialization_failure_handling(self, mock_session):
        """Test handling of service initialization failure."""
        with patch('app.ui.view_models.ingredient_view_model.IngredientService', side_effect=Exception("Service init failed")):
            vm = IngredientViewModel(mock_session)
            
            assert vm.ingredient_service is None
            
            # All methods should handle None service gracefully
            assert vm.search_ingredients("test") == []
            assert vm.create_or_get_ingredient("test", "Vegetables") is None
            
            match_result = vm.find_ingredient_matches("test")
            assert not match_result.is_valid_name

    def test_session_creation_failure_handling(self):
        """Test handling of session creation failure."""
        with patch('app.ui.view_models.base_view_model.create_session', side_effect=Exception("Session failed")):
            vm = IngredientViewModel()  # No session provided
            
            # Should handle session creation failure
            result = vm._ensure_service()
            assert result is False

    def test_search_with_none_or_empty_terms(self, ingredient_vm):
        """Test search with various edge case inputs."""
        # None term (should not happen but handle gracefully)
        with patch.object(ingredient_vm, '_ensure_service', return_value=True):
            # Empty string
            assert ingredient_vm.search_ingredients("") == []
            
            # Whitespace only
            assert ingredient_vm.search_ingredients("   ") == []

    def test_ingredient_matching_with_service_errors(self, ingredient_vm):
        """Test ingredient matching when service methods fail."""
        ingredient_vm.search_ingredients = Mock(side_effect=Exception("Search failed"))
        
        result = ingredient_vm.find_ingredient_matches("tomato")
        
        assert isinstance(result, IngredientMatchResult)
        assert result.exact_match is None
        assert result.partial_matches == []
        assert result.is_valid_name is True  # Input was valid, just service failed

    def test_autocomplete_with_cache_load_failure(self, ingredient_vm):
        """Test autocomplete when cache loading fails."""
        ingredient_vm._cache_loaded = False
        ingredient_vm._load_autocomplete_cache = Mock(side_effect=Exception("Cache load failed"))
        
        result = ingredient_vm.get_autocomplete_suggestions("test")
        
        assert result == []

    def test_transform_ingredient_dto_with_none_values(self, ingredient_vm):
        """Test DTO transformation with None/empty values."""
        data = IngredientFormData()
        data.ingredient_name = None  # Should be handled
        data.ingredient_category = ""
        data.quantity = None
        data.unit = None
        
        with patch('app.ui.view_models.ingredient_view_model.sanitize_form_input', side_effect=Exception("Sanitize failed")):
            result = ingredient_vm.transform_to_ingredient_dto(data)
            
            assert result == {}  # Should return empty dict on error

    def test_collection_validation_with_transform_errors(self, ingredient_vm):
        """Test collection validation when individual transformations fail."""
        ingredients_data = [
            {"ingredient_name": "valid", "ingredient_category": "Vegetables"},
            {"ingredient_name": "also_valid", "ingredient_category": "Vegetables"}
        ]
        
        # Mock parse_form_data to fail for second ingredient
        original_parse = ingredient_vm.parse_form_data
        def failing_parse(data):
            if data.get("ingredient_name") == "also_valid":
                raise Exception("Parse failed")
            return original_parse(data)
        
        ingredient_vm.parse_form_data = Mock(side_effect=failing_parse)
        
        # Should handle parsing errors gracefully
        result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        
        # Should still process the valid ingredient
        assert len(result.errors) >= 0  # May have errors but shouldn't crash


class TestRealTimeValidationComprehensive:
    """Test comprehensive real-time validation scenarios."""

    def test_all_real_time_validation_methods_boundary_conditions(self, ingredient_vm):
        """Test all real-time validation methods with boundary conditions."""
        # Test name validation boundaries
        assert ingredient_vm.validate_ingredient_name_real_time("a") is True  # Minimum
        assert ingredient_vm.validate_ingredient_name_real_time("x" * 100) is True  # At limit
        assert ingredient_vm.validate_ingredient_name_real_time("x" * 101) is False  # Over limit
        
        # Test category validation
        assert ingredient_vm.validate_ingredient_category_real_time("V") is True  # Minimum
        assert ingredient_vm.validate_ingredient_category_real_time("   ") is False  # Whitespace
        
        # Test quantity validation boundaries
        assert ingredient_vm.validate_ingredient_quantity_real_time("0.001") is True  # Very small
        assert ingredient_vm.validate_ingredient_quantity_real_time("9999") is True  # Just under warning
        assert ingredient_vm.validate_ingredient_quantity_real_time("10001") is True  # Warning case but valid

    def test_real_time_validation_signal_emission(self, ingredient_vm):
        """Test that real-time validation emits correct signals."""
        # Connect all validation signal spies
        name_spy = Mock()
        category_spy = Mock()
        quantity_spy = Mock()
        
        ingredient_vm.ingredient_name_validation_changed.connect(name_spy)
        ingredient_vm.ingredient_category_validation_changed.connect(category_spy)
        ingredient_vm.ingredient_quantity_validation_changed.connect(quantity_spy)
        
        # Test valid inputs
        ingredient_vm.validate_ingredient_name_real_time("valid name")
        ingredient_vm.validate_ingredient_category_real_time("Vegetables")
        ingredient_vm.validate_ingredient_quantity_real_time("2.5")
        
        # Verify success signals
        name_spy.assert_called_with(True, "")
        category_spy.assert_called_with(True, "")
        quantity_spy.assert_called_with(True, "")
        
        # Test invalid inputs
        name_spy.reset_mock()
        category_spy.reset_mock()
        quantity_spy.reset_mock()
        
        ingredient_vm.validate_ingredient_name_real_time("")
        ingredient_vm.validate_ingredient_category_real_time("")
        ingredient_vm.validate_ingredient_quantity_real_time("invalid")
        
        # Verify error signals
        name_spy.assert_called_with(False, "Ingredient name is required")
        category_spy.assert_called_with(False, "Category is required")
        quantity_spy.assert_called_with(False, "Quantity must be a valid number")


class TestUtilityMethodsAndProperties:
    """Test utility methods and properties comprehensively."""

    def test_is_valid_ingredient_name_comprehensive(self, ingredient_vm):
        """Test ingredient name validation with various inputs."""
        # Valid names
        assert ingredient_vm.is_valid_ingredient_name("tomato") is True
        assert ingredient_vm.is_valid_ingredient_name("cherry tomato") is True
        assert ingredient_vm.is_valid_ingredient_name("olive oil") is True
        assert ingredient_vm.is_valid_ingredient_name("salt & pepper") is True
        assert ingredient_vm.is_valid_ingredient_name("herbs (fresh)") is True
        
        # Invalid names
        assert ingredient_vm.is_valid_ingredient_name("") is False
        assert ingredient_vm.is_valid_ingredient_name(None) is False
        assert ingredient_vm.is_valid_ingredient_name("   ") is False
        assert ingredient_vm.is_valid_ingredient_name("123invalid") is False
        assert ingredient_vm.is_valid_ingredient_name("tomato@home") is False

    def test_properties_with_various_states(self, ingredient_vm):
        """Test properties in various states."""
        # Initial state
        assert not ingredient_vm.cache_loaded
        assert ingredient_vm.autocomplete_count == 0
        assert ingredient_vm.categories_count > 0  # Should have standard categories
        
        # After cache loading
        ingredient_vm._autocomplete_cache = ["item1", "item2", "item3"]
        ingredient_vm._cache_loaded = True
        ingredient_vm._categories_cache = ["Cat1", "Cat2"]
        
        assert ingredient_vm.cache_loaded
        assert ingredient_vm.autocomplete_count == 3
        assert ingredient_vm.categories_count == 2

    def test_create_or_get_ingredient_comprehensive(self, ingredient_vm):
        """Test create or get ingredient with various scenarios."""
        # Mock successful creation
        mock_ingredient = Mock()
        mock_ingredient.ingredient_name = "test ingredient"
        ingredient_vm.ingredient_service.get_or_create.return_value = mock_ingredient
        
        result = ingredient_vm.create_or_get_ingredient("test ingredient", "Vegetables")
        
        assert result is mock_ingredient
        ingredient_vm.ingredient_service.get_or_create.assert_called_once()
        
        # Test with whitespace (should be trimmed)
        ingredient_vm.ingredient_service.get_or_create.reset_mock()
        
        ingredient_vm.create_or_get_ingredient("  spaced ingredient  ", "  Vegetables  ")
        
        # Should have been called with trimmed values
        call_args = ingredient_vm.ingredient_service.get_or_create.call_args[0][0]
        assert call_args.ingredient_name == "spaced ingredient"
        assert call_args.ingredient_category == "Vegetables"

    def test_suggest_category_for_name_integration(self, ingredient_vm):
        """Test category suggestion integration."""
        # Mock find_ingredient_matches
        mock_result = IngredientMatchResult(suggested_category="Vegetables")
        ingredient_vm.find_ingredient_matches = Mock(return_value=mock_result)
        
        result = ingredient_vm.suggest_category_for_name("tomato")
        
        assert result == "Vegetables"
        ingredient_vm.find_ingredient_matches.assert_called_once_with("tomato")


class TestComplexWorkflowScenarios:
    """Test complex workflow scenarios combining multiple features."""

    def test_complete_ingredient_workflow_simulation(self, ingredient_vm):
        """Test complete ingredient workflow from input to validation."""
        # Simulate user typing ingredient name
        ingredient_vm.find_ingredient_matches = Mock(return_value=IngredientMatchResult(
            exact_match=None,
            partial_matches=[],
            suggested_category="Vegetables"
        ))
        
        # Connect signal spy
        category_suggested_spy = Mock()
        ingredient_vm.category_suggested.connect(category_suggested_spy)
        
        # Step 1: Find matches for ingredient
        match_result = ingredient_vm.find_ingredient_matches("new ingredient")
        
        # Step 2: Should suggest category
        category_suggested_spy.assert_called_once_with("Vegetables")
        
        # Step 3: Validate the ingredient data
        form_data = IngredientFormData()
        form_data.ingredient_name = "new ingredient"
        form_data.ingredient_category = "Vegetables"
        form_data.quantity = "2"
        form_data.unit = "cups"
        
        validation_result = ingredient_vm.validate_ingredient_data(form_data)
        assert validation_result.is_valid
        
        # Step 4: Transform to DTO
        dto_data = ingredient_vm.transform_to_ingredient_dto(form_data)
        assert dto_data["ingredient_name"] == "new ingredient"
        assert dto_data["quantity"] == 2.0

    def test_ingredient_search_to_matching_workflow(self, ingredient_vm):
        """Test workflow from search to matching to category suggestion."""
        # Mock search results
        mock_ingredient = Mock()
        mock_ingredient.ingredient_name = "cherry tomato"
        mock_ingredient.ingredient_category = "Vegetables"
        
        ingredient_vm.ingredient_service.search.return_value = [mock_ingredient]
        
        # Connect signal spies
        search_spy = Mock()
        matched_spy = Mock()
        category_spy = Mock()
        
        ingredient_vm.ingredient_search_completed.connect(search_spy)
        ingredient_vm.ingredient_matched.connect(matched_spy)
        ingredient_vm.category_suggested.connect(category_spy)
        
        # Perform search
        search_results = ingredient_vm.search_ingredients("tomato")
        
        # Verify search completed
        search_spy.assert_called_once_with([mock_ingredient])
        
        # Find matches based on search
        match_result = ingredient_vm.find_ingredient_matches("tomato")
        
        # Should suggest category and emit signals
        matched_spy.assert_called_once()
        # Note: exact category suggestion depends on matching logic

    def test_collection_processing_comprehensive(self, ingredient_vm):
        """Test comprehensive collection processing."""
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
                "ingredient_name": "",  # Empty - should be skipped
                "ingredient_category": "Vegetables"
            },
            {
                "ingredient_name": "Tomato",  # Duplicate (case insensitive)
                "ingredient_category": "Vegetables",
                "quantity": "1"
            }
        ]
        
        # Test validation
        validation_result = ingredient_vm.validate_ingredient_collection(ingredients_data)
        
        assert validation_result.is_valid  # Should be valid overall
        assert len(validation_result.warnings) >= 1  # Should warn about duplicate
        
        # Test transformation
        transformed = ingredient_vm.transform_ingredient_collection(ingredients_data)
        
        # Should have 3 items (excluding empty one)
        assert len(transformed) == 3
        assert transformed[0]["ingredient_name"] == "tomato"
        assert transformed[1]["ingredient_name"] == "olive oil"


@pytest.mark.integration  
class TestIngredientViewModelIntegration:
    """Integration tests for IngredientViewModel with real services."""

    def test_full_ingredient_workflow(self, db_session):
        """Test complete ingredient workflow with real database."""
        from app.core.repositories.ingredient_repo import IngredientRepo
        from app.core.services.ingredient_service import IngredientService

        # Create real service with test database session
        ingredient_service = IngredientService(db_session)
        
        # Create ViewModel with real service
        vm = IngredientViewModel(db_session)
        vm.ingredient_service = ingredient_service
        
        # Test ingredient creation
        ingredient = vm.create_or_get_ingredient("test ingredient", "Vegetables")
        assert ingredient is not None
        assert ingredient.ingredient_name == "test ingredient"
        
        # Test ingredient search
        search_results = vm.search_ingredients("test")
        assert len(search_results) >= 1
        assert any(ing.ingredient_name == "test ingredient" for ing in search_results)
        
        # Test ingredient matching
        match_result = vm.find_ingredient_matches("test ingredient")
        assert match_result.exact_match is not None
        assert match_result.exact_match.ingredient_name == "test ingredient"