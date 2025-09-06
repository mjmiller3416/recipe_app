"""
Unit tests for BaseViewModel.

Tests the base view model functionality including:
- Session management and cleanup
- Common validation patterns
- Error handling utilities
- DTO construction helpers
- Form state management
- Signal management utilities
"""

from unittest.mock import MagicMock, Mock, patch

from PySide6.QtCore import QObject
import pytest

from app.ui.view_models.base_view_model import BaseValidationResult, BaseViewModel

@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def base_vm(mock_session):
    """Create BaseViewModel instance with mocked session."""
    return BaseViewModel(mock_session)


class TestBaseValidationResult:
    """Test BaseValidationResult functionality."""

    def test_initialization_default(self):
        """Test default initialization of BaseValidationResult."""
        result = BaseValidationResult()
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_initialization_with_values(self):
        """Test initialization with provided values."""
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]
        
        result = BaseValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        assert result.is_valid is False
        assert result.errors == errors
        assert result.warnings == warnings

    def test_add_error(self):
        """Test adding error to validation result."""
        result = BaseValidationResult()
        
        result.add_error("Test error")
        
        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warning to validation result."""
        result = BaseValidationResult()
        
        result.add_warning("Test warning")
        
        assert result.is_valid is True  # Warnings don't affect validity
        assert "Test warning" in result.warnings

    def test_merge_valid_results(self):
        """Test merging two valid validation results."""
        result1 = BaseValidationResult()
        result1.add_warning("Warning 1")
        
        result2 = BaseValidationResult()
        result2.add_warning("Warning 2")
        
        result1.merge(result2)
        
        assert result1.is_valid is True
        assert len(result1.warnings) == 2
        assert "Warning 1" in result1.warnings
        assert "Warning 2" in result1.warnings

    def test_merge_invalid_result(self):
        """Test merging invalid result makes combined result invalid."""
        result1 = BaseValidationResult()
        
        result2 = BaseValidationResult(is_valid=False)
        result2.add_error("Error from result2")
        
        result1.merge(result2)
        
        assert result1.is_valid is False
        assert "Error from result2" in result1.errors

    def test_has_issues(self):
        """Test has_issues method."""
        result = BaseValidationResult()
        assert result.has_issues() is False
        
        result.add_warning("Warning")
        assert result.has_issues() is True
        
        result = BaseValidationResult()
        result.add_error("Error")
        assert result.has_issues() is True

    def test_get_summary(self):
        """Test get_summary method."""
        result = BaseValidationResult()
        assert result.get_summary() == "No issues"
        
        result.add_error("Error")
        assert "1 errors" in result.get_summary()
        
        result.add_warning("Warning")
        summary = result.get_summary()
        assert "1 errors" in summary
        assert "1 warnings" in summary


class TestBaseViewModelInitialization:
    """Test BaseViewModel initialization and setup."""

    def test_initialization_with_session(self, mock_session):
        """Test ViewModel initializes correctly with provided session."""
        vm = BaseViewModel(mock_session)
        
        assert vm._session is mock_session
        assert vm._owns_session is False
        assert vm._is_processing is False
        assert vm._is_loading is False
        assert vm._validation_errors == []

    def test_initialization_without_session(self):
        """Test ViewModel initializes correctly without session."""
        vm = BaseViewModel()
        
        assert vm._session is None
        assert vm._owns_session is True
        assert vm._is_processing is False
        assert vm._is_loading is False

    def test_signal_definitions(self, base_vm):
        """Test that all required signals are defined."""
        vm = base_vm
        
        # Check common signals
        assert hasattr(vm, 'processing_state_changed')
        assert hasattr(vm, 'loading_state_changed')
        assert hasattr(vm, 'error_occurred')
        assert hasattr(vm, 'validation_failed')
        assert hasattr(vm, 'state_reset')
        assert hasattr(vm, 'field_validation_error')
        assert hasattr(vm, 'field_validation_cleared')

    def test_inherits_from_qobject(self, base_vm):
        """Test that BaseViewModel properly inherits from QObject."""
        assert isinstance(base_vm, QObject)


class TestSessionManagement:
    """Test session management functionality."""

    def test_ensure_session_with_existing_session(self, base_vm):
        """Test _ensure_session when session already exists."""
        result = base_vm._ensure_session()
        
        assert result is True
        assert base_vm._session is not None

    def test_ensure_session_creates_new_session(self):
        """Test _ensure_session creates new session when needed."""
        vm = BaseViewModel()  # No session provided
        
        with patch('app.ui.view_models.base_view_model.create_session') as mock_create:
            mock_session = Mock()
            mock_create.return_value = mock_session
            
            result = vm._ensure_session()
            
            assert result is True
            assert vm._session is mock_session
            assert vm._owns_session is True
            mock_create.assert_called_once()

    def test_ensure_session_handles_creation_failure(self):
        """Test _ensure_session handles session creation failure."""
        vm = BaseViewModel()
        
        with patch('app.ui.view_models.base_view_model.create_session', side_effect=Exception("DB Error")):
            result = vm._ensure_session()
            
            assert result is False
            assert vm._session is None

    def test_cleanup_session_owned(self):
        """Test session cleanup when ViewModel owns session."""
        vm = BaseViewModel()
        mock_session = Mock()
        vm._session = mock_session
        vm._owns_session = True
        
        vm._cleanup_session()
        
        mock_session.close.assert_called_once()
        assert vm._session is None

    def test_cleanup_session_not_owned(self, base_vm):
        """Test session cleanup when ViewModel doesn't own session."""
        original_session = base_vm._session
        
        base_vm._cleanup_session()
        
        # Session should not be closed if not owned
        original_session.close.assert_not_called()
        # But session reference should be cleared
        assert base_vm._session is None

    def test_cleanup_session_handles_error(self):
        """Test session cleanup handles close errors gracefully."""
        vm = BaseViewModel()
        mock_session = Mock()
        mock_session.close.side_effect = Exception("Close error")
        vm._session = mock_session
        vm._owns_session = True
        
        # Should not raise exception
        vm._cleanup_session()
        
        assert vm._session is None

    def test_destructor_calls_cleanup(self):
        """Test that destructor calls session cleanup."""
        vm = BaseViewModel()
        vm._cleanup_session = Mock()
        
        vm.__del__()
        
        vm._cleanup_session.assert_called_once()


class TestStateManagement:
    """Test state management functionality."""

    def test_is_processing_property(self, base_vm):
        """Test is_processing property."""
        assert base_vm.is_processing is False
        
        base_vm._is_processing = True
        assert base_vm.is_processing is True

    def test_is_loading_property(self, base_vm):
        """Test is_loading property."""
        assert base_vm.is_loading is False
        
        base_vm._is_loading = True
        assert base_vm.is_loading is True

    def test_has_validation_errors_property(self, base_vm):
        """Test has_validation_errors property."""
        assert base_vm.has_validation_errors is False
        
        base_vm._validation_errors = ["Error"]
        assert base_vm.has_validation_errors is True

    def test_validation_errors_property(self, base_vm):
        """Test validation_errors property returns copy."""
        errors = ["Error 1", "Error 2"]
        base_vm._validation_errors = errors
        
        returned_errors = base_vm.validation_errors
        
        assert returned_errors == errors
        assert returned_errors is not errors  # Should be a copy

    def test_set_processing_state(self, base_vm):
        """Test _set_processing_state method."""
        # Connect signal spy
        processing_spy = Mock()
        base_vm.processing_state_changed.connect(processing_spy)
        
        base_vm._set_processing_state(True)
        
        assert base_vm._is_processing is True
        processing_spy.assert_called_once_with(True)

    def test_set_processing_state_no_change(self, base_vm):
        """Test _set_processing_state doesn't emit signal when state unchanged."""
        base_vm._is_processing = True
        
        # Connect signal spy
        processing_spy = Mock()
        base_vm.processing_state_changed.connect(processing_spy)
        
        base_vm._set_processing_state(True)
        
        processing_spy.assert_not_called()

    def test_set_loading_state(self, base_vm):
        """Test _set_loading_state method."""
        # Connect signal spy
        loading_spy = Mock()
        base_vm.loading_state_changed.connect(loading_spy)
        
        base_vm._set_loading_state(True, "Loading data...")
        
        assert base_vm._is_loading is True
        loading_spy.assert_called_once_with(True, "Loading data...")

    def test_reset_internal_state(self, base_vm):
        """Test _reset_internal_state method."""
        # Set some state
        base_vm._is_processing = True
        base_vm._is_loading = True
        base_vm._validation_errors = ["Error"]
        
        base_vm._reset_internal_state()
        
        assert base_vm._is_processing is False
        assert base_vm._is_loading is False
        assert base_vm._validation_errors == []

    def test_reset_state(self, base_vm):
        """Test reset_state method."""
        # Set some state
        base_vm._is_processing = True
        
        # Connect signal spy
        reset_spy = Mock()
        base_vm.state_reset.connect(reset_spy)
        
        base_vm.reset_state()
        
        assert base_vm._is_processing is False
        reset_spy.assert_called_once()


class TestErrorHandling:
    """Test error handling functionality."""

    def test_handle_error(self, base_vm):
        """Test _handle_error method."""
        # Connect signal spy
        error_spy = Mock()
        base_vm.error_occurred.connect(error_spy)
        
        test_error = ValueError("Test error")
        base_vm._handle_error(test_error, "Test context", "validation")
        
        error_spy.assert_called_once_with("validation", "Test context: Test error")

    def test_emit_validation_errors(self, base_vm):
        """Test _emit_validation_errors method."""
        # Connect signal spy
        validation_spy = Mock()
        base_vm.validation_failed.connect(validation_spy)
        
        errors = ["Error 1", "Error 2"]
        base_vm._emit_validation_errors(errors)
        
        assert base_vm._validation_errors == errors
        validation_spy.assert_called_once_with(errors)

    def test_clear_validation_errors(self, base_vm):
        """Test _clear_validation_errors method."""
        base_vm._validation_errors = ["Error 1"]
        
        base_vm._clear_validation_errors()
        
        assert base_vm._validation_errors == []


class TestFieldValidationUtilities:
    """Test field validation utility methods."""

    def test_emit_field_error(self, base_vm):
        """Test _emit_field_error method."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        base_vm._emit_field_error("test_field", "Test error message")
        
        field_error_spy.assert_called_once_with("test_field", "Test error message")

    def test_clear_field_error(self, base_vm):
        """Test _clear_field_error method."""
        # Connect signal spy
        field_cleared_spy = Mock()
        base_vm.field_validation_cleared.connect(field_cleared_spy)
        
        base_vm._clear_field_error("test_field")
        
        field_cleared_spy.assert_called_once_with("test_field")

    def test_validate_required_field_valid(self, base_vm):
        """Test _validate_required_field with valid input."""
        # Connect signal spy
        field_cleared_spy = Mock()
        base_vm.field_validation_cleared.connect(field_cleared_spy)
        
        result = base_vm._validate_required_field("Valid Value", "test_field", "Test Field")
        
        assert result is True
        field_cleared_spy.assert_called_once_with("test_field")

    def test_validate_required_field_empty(self, base_vm):
        """Test _validate_required_field with empty input."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_required_field("", "test_field", "Test Field")
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field is required")

    def test_validate_required_field_whitespace_only(self, base_vm):
        """Test _validate_required_field with whitespace-only input."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_required_field("   ", "test_field", "Test Field")
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field is required")

    def test_validate_field_length_valid(self, base_vm):
        """Test _validate_field_length with valid length."""
        # Connect signal spy
        field_cleared_spy = Mock()
        base_vm.field_validation_cleared.connect(field_cleared_spy)
        
        result = base_vm._validate_field_length("Valid", "test_field", "Test Field", 2, 10)
        
        assert result is True
        field_cleared_spy.assert_called_once_with("test_field")

    def test_validate_field_length_too_short(self, base_vm):
        """Test _validate_field_length with input too short."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_field_length("A", "test_field", "Test Field", min_length=3)
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field must be at least 3 characters")

    def test_validate_field_length_too_long(self, base_vm):
        """Test _validate_field_length with input too long."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_field_length("Too long", "test_field", "Test Field", max_length=5)
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field cannot exceed 5 characters")

    def test_validate_numeric_field_valid(self, base_vm):
        """Test _validate_numeric_field with valid number."""
        # Connect signal spy
        field_cleared_spy = Mock()
        base_vm.field_validation_cleared.connect(field_cleared_spy)
        
        result = base_vm._validate_numeric_field("5", "test_field", "Test Field", 1, 10)
        
        assert result is True
        field_cleared_spy.assert_called_once_with("test_field")

    def test_validate_numeric_field_empty(self, base_vm):
        """Test _validate_numeric_field with empty value (should be valid for optional fields)."""
        # Connect signal spy
        field_cleared_spy = Mock()
        base_vm.field_validation_cleared.connect(field_cleared_spy)
        
        result = base_vm._validate_numeric_field("", "test_field", "Test Field")
        
        assert result is True
        field_cleared_spy.assert_called_once_with("test_field")

    def test_validate_numeric_field_invalid(self, base_vm):
        """Test _validate_numeric_field with invalid number."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_numeric_field("invalid", "test_field", "Test Field")
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field must be a valid number")

    def test_validate_numeric_field_too_small(self, base_vm):
        """Test _validate_numeric_field with value too small."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_numeric_field("1", "test_field", "Test Field", min_value=5)
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field must be at least 5")

    def test_validate_numeric_field_too_large(self, base_vm):
        """Test _validate_numeric_field with value too large."""
        # Connect signal spy
        field_error_spy = Mock()
        base_vm.field_validation_error.connect(field_error_spy)
        
        result = base_vm._validate_numeric_field("15", "test_field", "Test Field", max_value=10)
        
        assert result is False
        field_error_spy.assert_called_once_with("test_field", "Test Field cannot exceed 10")


class TestDTOConstructionHelpers:
    """Test DTO construction helper methods."""

    def test_sanitize_form_input_valid_string(self, base_vm):
        """Test _sanitize_form_input with valid string."""
        result = base_vm._sanitize_form_input("Test String")
        
        assert result == "Test String"

    def test_sanitize_form_input_none(self, base_vm):
        """Test _sanitize_form_input with None value."""
        result = base_vm._sanitize_form_input(None)
        
        assert result == ""

    def test_sanitize_form_input_number(self, base_vm):
        """Test _sanitize_form_input with number."""
        result = base_vm._sanitize_form_input(123)
        
        assert result == "123"

    def test_prepare_dto_field_valid_value(self, base_vm):
        """Test _prepare_dto_field with valid value."""
        result = base_vm._prepare_dto_field("Test Value")
        
        assert result == "Test Value"

    def test_prepare_dto_field_empty_optional(self, base_vm):
        """Test _prepare_dto_field with empty value (optional field)."""
        result = base_vm._prepare_dto_field("", required=False, default="Default")
        
        assert result == "Default"

    def test_prepare_dto_field_empty_required(self, base_vm):
        """Test _prepare_dto_field with empty value (required field)."""
        with pytest.raises(ValueError, match="Required field cannot be empty"):
            base_vm._prepare_dto_field("", required=True)

    def test_prepare_dto_field_none_optional(self, base_vm):
        """Test _prepare_dto_field with None value (optional field)."""
        result = base_vm._prepare_dto_field(None, required=False, default="Default")
        
        assert result == "Default"

    def test_build_dto_data_success(self, base_vm):
        """Test _build_dto_data with successful mapping."""
        form_data = {
            "name": "Test Name",
            "age": "25",
            "email": "test@example.com"
        }
        
        field_mapping = {
            "name": {"dto_field": "full_name", "required": True},
            "age": {"dto_field": "user_age", "required": False, "default": 0},
            "email": {"required": False}
        }
        
        result = base_vm._build_dto_data(form_data, field_mapping)
        
        assert result["full_name"] == "Test Name"
        assert result["user_age"] == "25"
        assert result["email"] == "test@example.com"

    def test_build_dto_data_with_transform(self, base_vm):
        """Test _build_dto_data with transformation function."""
        form_data = {"age": "25"}
        
        field_mapping = {
            "age": {"transform": lambda x: int(x) if x else 0}
        }
        
        result = base_vm._build_dto_data(form_data, field_mapping)
        
        assert result["age"] == 25  # Should be transformed to int

    def test_build_dto_data_handles_transform_error(self, base_vm):
        """Test _build_dto_data handles transformation errors gracefully."""
        form_data = {"age": "invalid"}
        
        field_mapping = {
            "age": {
                "transform": lambda x: int(x),  # Will fail with "invalid"
                "required": False,
                "default": 0
            }
        }
        
        result = base_vm._build_dto_data(form_data, field_mapping)
        
        assert result["age"] == 0  # Should fall back to default

    def test_build_dto_data_required_field_error(self, base_vm):
        """Test _build_dto_data raises error for required field transformation failure."""
        form_data = {"age": "invalid"}
        
        field_mapping = {
            "age": {
                "transform": lambda x: int(x),  # Will fail with "invalid"
                "required": True
            }
        }
        
        with pytest.raises(ValueError):
            base_vm._build_dto_data(form_data, field_mapping)


class TestUtilityMethods:
    """Test utility methods."""

    def test_safe_execute_success(self, base_vm):
        """Test _safe_execute with successful operation."""
        mock_operation = Mock(return_value="Success")
        
        result = base_vm._safe_execute(mock_operation, "Test operation", "arg1", key="value")
        
        assert result == "Success"
        mock_operation.assert_called_once_with("arg1", key="value")

    def test_safe_execute_failure(self, base_vm):
        """Test _safe_execute with operation failure."""
        mock_operation = Mock(side_effect=Exception("Operation failed"))
        
        # Connect signal spy
        error_spy = Mock()
        base_vm.error_occurred.connect(error_spy)
        
        result = base_vm._safe_execute(mock_operation, "Test operation")
        
        assert result is None
        error_spy.assert_called_once()

    def test_batch_validate_fields_all_valid(self, base_vm):
        """Test _batch_validate_fields with all valid fields."""
        field_validations = [
            ("Valid Name", "name", "Name", {"required": True, "max_length": 50}),
            ("25", "age", "Age", {"numeric": True, "min_value": 18})
        ]
        
        result = base_vm._batch_validate_fields(field_validations)
        
        assert isinstance(result, BaseValidationResult)
        assert result.is_valid is True

    def test_batch_validate_fields_with_errors(self, base_vm):
        """Test _batch_validate_fields with validation errors."""
        field_validations = [
            ("", "name", "Name", {"required": True}),  # Empty required field
            ("15", "age", "Age", {"numeric": True, "min_value": 18})  # Too young
        ]
        
        result = base_vm._batch_validate_fields(field_validations)
        
        assert isinstance(result, BaseValidationResult)
        assert result.is_valid is False
        assert len(result.errors) >= 2  # Should have errors for both fields

    def test_batch_validate_fields_length_validation(self, base_vm):
        """Test _batch_validate_fields with length validation."""
        field_validations = [
            ("A", "name", "Name", {"required": True, "min_length": 3}),  # Too short
            ("Very long name that exceeds limit", "title", "Title", {"max_length": 10})  # Too long
        ]
        
        result = base_vm._batch_validate_fields(field_validations)
        
        assert result.is_valid is False
        assert any("length validation failed" in error for error in result.errors)


class TestSignalIntegration:
    """Test signal integration and emission."""

    def test_multiple_signal_connections(self, base_vm):
        """Test that multiple signals can be connected and emit correctly."""
        # Connect multiple signal spies
        processing_spy = Mock()
        loading_spy = Mock()
        error_spy = Mock()
        validation_spy = Mock()
        
        base_vm.processing_state_changed.connect(processing_spy)
        base_vm.loading_state_changed.connect(loading_spy)
        base_vm.error_occurred.connect(error_spy)
        base_vm.validation_failed.connect(validation_spy)
        
        # Trigger various state changes
        base_vm._set_processing_state(True)
        base_vm._set_loading_state(True, "Loading...")
        base_vm._handle_error(Exception("Test error"), "Context")
        base_vm._emit_validation_errors(["Validation error"])
        
        # Verify all signals were emitted
        processing_spy.assert_called_once_with(True)
        loading_spy.assert_called_once_with(True, "Loading...")
        error_spy.assert_called_once()
        validation_spy.assert_called_once_with(["Validation error"])

    def test_signal_disconnection_safety(self, base_vm):
        """Test that operations work correctly when signals are not connected."""
        # These should not raise exceptions even without signal connections
        base_vm._set_processing_state(True)
        base_vm._set_loading_state(True, "Loading...")
        base_vm._handle_error(Exception("Test"), "Context")
        base_vm._emit_validation_errors(["Error"])
        base_vm._emit_field_error("field", "error")
        base_vm._clear_field_error("field")
        
        # All operations should complete without error
        assert True


class TestAdvancedFieldValidation:
    """Test advanced field validation scenarios."""

    def test_batch_validate_fields_comprehensive(self, base_vm):
        """Test comprehensive batch field validation scenarios."""
        field_validations = [
            # Test all validation types
            ("Valid Name", "name", "Name", {"required": True, "min_length": 2, "max_length": 50}),
            ("", "required_field", "Required Field", {"required": True}),
            ("A", "short_field", "Short Field", {"min_length": 3}),
            ("Very long field name that exceeds limit", "long_field", "Long Field", {"max_length": 10}),
            ("25", "numeric_field", "Numeric Field", {"numeric": True, "min_value": 18, "max_value": 65}),
            ("invalid", "invalid_numeric", "Invalid Numeric", {"numeric": True}),
            ("10", "under_min", "Under Min", {"numeric": True, "min_value": 20}),
            ("100", "over_max", "Over Max", {"numeric": True, "max_value": 50})
        ]
        
        result = base_vm._batch_validate_fields(field_validations)
        
        assert isinstance(result, BaseValidationResult)
        assert not result.is_valid
        assert len(result.errors) >= 6  # Multiple validation failures

    def test_batch_validate_fields_edge_cases(self, base_vm):
        """Test batch validation with edge cases."""
        # Empty validation list
        result = base_vm._batch_validate_fields([])
        assert result.is_valid
        
        # Validation with only optional fields
        optional_validations = [
            ("", "optional", "Optional", {}),  # No rules = valid
            ("valid", "optional2", "Optional 2", {"max_length": 10})  # Optional with constraint
        ]
        
        result = base_vm._batch_validate_fields(optional_validations)
        assert result.is_valid

    def test_validate_numeric_field_edge_cases(self, base_vm):
        """Test numeric field validation with edge cases."""
        # Test float values
        assert base_vm._validate_numeric_field("2.5", "test", "Test", 2.0, 3.0) is True
        assert base_vm._validate_numeric_field("1.99", "test", "Test", 2.0, 3.0) is False
        
        # Test scientific notation
        assert base_vm._validate_numeric_field("1e2", "test", "Test") is True
        
        # Test negative numbers
        assert base_vm._validate_numeric_field("-5", "test", "Test", -10, 0) is True
        
        # Test zero
        assert base_vm._validate_numeric_field("0", "test", "Test", 0, 10) is True

    def test_field_validation_signal_integration(self, base_vm):
        """Test field validation signal integration."""
        error_spy = Mock()
        cleared_spy = Mock()
        
        base_vm.field_validation_error.connect(error_spy)
        base_vm.field_validation_cleared.connect(cleared_spy)
        
        # Test error emission
        base_vm._validate_required_field("", "test_field", "Test Field")
        error_spy.assert_called_once_with("test_field", "Test Field is required")
        
        # Test clear emission
        error_spy.reset_mock()
        base_vm._validate_required_field("Valid", "test_field", "Test Field")
        cleared_spy.assert_called_once_with("test_field")


class TestDTOConstructionAdvanced:
    """Test advanced DTO construction scenarios."""

    def test_build_dto_data_complex_transformations(self, base_vm):
        """Test DTO building with complex transformations."""
        form_data = {
            "name": "  John Doe  ",
            "age": "25",
            "email": "john@example.com",
            "tags": "tag1,tag2,tag3",
            "active": "true",
            "score": "85.5"
        }
        
        field_mapping = {
            "name": {
                "dto_field": "full_name",
                "required": True,
                "transform": lambda x: x.strip().title() if x else ""
            },
            "age": {
                "dto_field": "user_age",
                "required": True,
                "transform": lambda x: int(x) if x and x.isdigit() else 0
            },
            "email": {
                "required": False,
                "transform": lambda x: x.lower() if x else None
            },
            "tags": {
                "dto_field": "tag_list",
                "transform": lambda x: x.split(',') if x else []
            },
            "active": {
                "dto_field": "is_active",
                "transform": lambda x: x.lower() == 'true'
            },
            "score": {
                "transform": lambda x: float(x) if x else 0.0
            }
        }
        
        result = base_vm._build_dto_data(form_data, field_mapping)
        
        assert result["full_name"] == "John Doe"
        assert result["user_age"] == 25
        assert result["email"] == "john@example.com"
        assert result["tag_list"] == ["tag1", "tag2", "tag3"]
        assert result["is_active"] is True
        assert result["score"] == 85.5

    def test_build_dto_data_with_nested_defaults(self, base_vm):
        """Test DTO building with complex default values."""
        form_data = {
            "partial_field": "value"
        }
        
        field_mapping = {
            "partial_field": {"required": False},
            "missing_field": {"default": {"nested": "value"}},
            "computed_field": {
                "transform": lambda x: {"computed": True, "source": x} if x else None,
                "default": {"computed": False}
            }
        }
        
        result = base_vm._build_dto_data(form_data, field_mapping)
        
        assert result["partial_field"] == "value"
        assert result["missing_field"] == {"nested": "value"}
        assert result["computed_field"] is None  # Missing field, no transform applied

    def test_prepare_dto_field_type_handling(self, base_vm):
        """Test DTO field preparation with various data types."""
        # Test different types
        assert base_vm._prepare_dto_field(123) == 123
        assert base_vm._prepare_dto_field(True) is True
        assert base_vm._prepare_dto_field([1, 2, 3]) == [1, 2, 3]
        assert base_vm._prepare_dto_field({"key": "value"}) == {"key": "value"}
        
        # Test string handling
        assert base_vm._prepare_dto_field("  text  ") == "text"
        assert base_vm._prepare_dto_field("") == ""
        
        # Test with defaults
        assert base_vm._prepare_dto_field("", default="default_value") == "default_value"
        assert base_vm._prepare_dto_field(None, default=42) == 42


class TestSessionManagementAdvanced:
    """Test advanced session management scenarios."""

    def test_session_cleanup_with_multiple_references(self):
        """Test session cleanup behavior with multiple ViewModels."""
        mock_session = Mock()
        
        # Create multiple ViewModels sharing the same session
        vm1 = BaseViewModel(mock_session)
        vm2 = BaseViewModel(mock_session)
        
        # Neither should own the session
        assert not vm1._owns_session
        assert not vm2._owns_session
        
        # Cleanup should not close shared session
        vm1._cleanup_session()
        mock_session.close.assert_not_called()
        
        vm2._cleanup_session()
        mock_session.close.assert_not_called()

    def test_session_ownership_transfer(self):
        """Test session ownership transfer scenarios."""
        vm = BaseViewModel()  # Creates its own session
        
        with patch('app.ui.view_models.base_view_model.create_session') as mock_create:
            mock_session = Mock()
            mock_create.return_value = mock_session
            
            # Ensure session creates one
            vm._ensure_session()
            assert vm._owns_session
            assert vm._session is mock_session
            
            # Transfer ownership by assigning external session
            external_session = Mock()
            vm._session = external_session
            vm._owns_session = False
            
            # Cleanup should not close external session
            vm._cleanup_session()
            external_session.close.assert_not_called()
            mock_session.close.assert_not_called()

    def test_session_recreation_after_cleanup(self):
        """Test session recreation after cleanup."""
        vm = BaseViewModel()
        
        with patch('app.ui.view_models.base_view_model.create_session') as mock_create:
            mock_session1 = Mock()
            mock_session2 = Mock()
            mock_create.side_effect = [mock_session1, mock_session2]
            
            # Create first session
            vm._ensure_session()
            assert vm._session is mock_session1
            
            # Cleanup
            vm._cleanup_session()
            assert vm._session is None
            
            # Create new session
            vm._ensure_session()
            assert vm._session is mock_session2


class TestErrorHandlingComprehensive:
    """Test comprehensive error handling scenarios."""

    def test_handle_error_with_complex_exceptions(self, base_vm):
        """Test error handling with complex exception scenarios."""
        error_spy = Mock()
        base_vm.error_occurred.connect(error_spy)
        
        # Test with nested exceptions
        try:
            try:
                raise ValueError("Inner error")
            except ValueError as inner:
                raise RuntimeError("Outer error") from inner
        except RuntimeError as e:
            base_vm._handle_error(e, "Complex error context", "nested")
        
        error_spy.assert_called_once()
        call_args = error_spy.call_args[0]
        assert call_args[0] == "nested"
        assert "Complex error context" in call_args[1]

    def test_safe_execute_with_various_operations(self, base_vm):
        """Test safe execute with various operation types."""
        error_spy = Mock()
        base_vm.error_occurred.connect(error_spy)
        
        # Test successful operation
        def success_op(x, y=10):
            return x + y
        
        result = base_vm._safe_execute(success_op, "Addition", 5, y=15)
        assert result == 20
        
        # Test failing operation
        def failing_op():
            raise Exception("Operation failed")
        
        result = base_vm._safe_execute(failing_op, "Failing operation")
        assert result is None
        error_spy.assert_called_once()

    def test_validation_error_management_lifecycle(self, base_vm):
        """Test validation error management lifecycle."""
        validation_spy = Mock()
        base_vm.validation_failed.connect(validation_spy)
        
        # Start with no errors
        assert not base_vm.has_validation_errors
        assert base_vm.validation_errors == []
        
        # Add errors
        errors = ["Error 1", "Error 2"]
        base_vm._emit_validation_errors(errors)
        
        assert base_vm.has_validation_errors
        assert base_vm.validation_errors == errors
        validation_spy.assert_called_once_with(errors)
        
        # Clear errors
        base_vm._clear_validation_errors()
        assert not base_vm.has_validation_errors
        assert base_vm.validation_errors == []

    def test_state_management_consistency(self, base_vm):
        """Test state management consistency across operations."""
        processing_spy = Mock()
        loading_spy = Mock()
        
        base_vm.processing_state_changed.connect(processing_spy)
        base_vm.loading_state_changed.connect(loading_spy)
        
        # Set multiple states
        base_vm._set_processing_state(True)
        base_vm._set_loading_state(True, "Loading...")
        base_vm._validation_errors = ["Error"]
        
        # Check states
        assert base_vm.is_processing
        assert base_vm.is_loading
        assert base_vm.has_validation_errors
        
        # Reset all state
        base_vm._reset_internal_state()
        
        # Verify all state is cleared
        assert not base_vm.is_processing
        assert not base_vm.is_loading
        assert not base_vm.has_validation_errors


class TestSignalManagementAdvanced:
    """Test advanced signal management scenarios."""

    def test_signal_emission_with_no_connections(self, base_vm):
        """Test signal emission when no slots are connected."""
        # Should not raise exceptions
        try:
            base_vm._set_processing_state(True)
            base_vm._set_loading_state(True, "Test")
            base_vm._handle_error(Exception("Test"), "Context")
            base_vm._emit_validation_errors(["Error"])
            base_vm._emit_field_error("field", "error")
            base_vm._clear_field_error("field")
        except Exception as e:
            pytest.fail(f"Signal emission without connections failed: {e}")

    def test_signal_emission_order_and_consistency(self, base_vm):
        """Test signal emission order and consistency."""
        signal_order = []
        
        def track_processing(is_processing):
            signal_order.append(f"processing:{is_processing}")
        
        def track_loading(is_loading, operation):
            signal_order.append(f"loading:{is_loading}:{operation}")
        
        def track_validation(errors):
            signal_order.append(f"validation:{len(errors)}")
        
        base_vm.processing_state_changed.connect(track_processing)
        base_vm.loading_state_changed.connect(track_loading)
        base_vm.validation_failed.connect(track_validation)
        
        # Emit in specific order
        base_vm._set_processing_state(True)
        base_vm._set_loading_state(True, "Operation")
        base_vm._emit_validation_errors(["Error1", "Error2"])
        base_vm._set_loading_state(False, "")
        base_vm._set_processing_state(False)
        
        expected_order = [
            "processing:True",
            "loading:True:Operation",
            "validation:2",
            "loading:False:",
            "processing:False"
        ]
        
        assert signal_order == expected_order

    def test_multiple_signal_connections_per_signal(self, base_vm):
        """Test multiple signal connections to same signal."""
        handlers = []
        
        def handler1(is_processing):
            handlers.append(f"handler1:{is_processing}")
        
        def handler2(is_processing):
            handlers.append(f"handler2:{is_processing}")
        
        base_vm.processing_state_changed.connect(handler1)
        base_vm.processing_state_changed.connect(handler2)
        
        base_vm._set_processing_state(True)
        
        # Both handlers should be called
        assert "handler1:True" in handlers
        assert "handler2:True" in handlers
        assert len(handlers) == 2


@pytest.mark.integration
class TestBaseViewModelIntegration:
    """Integration tests for BaseViewModel with Qt signals."""

    def test_qt_signal_integration(self, qapp, base_vm):
        """Test that Qt signals work correctly in application context."""
        # This test requires the Qt application to be running
        signal_received = []
        
        def on_processing_changed(is_processing):
            signal_received.append(('processing', is_processing))
        
        def on_loading_changed(is_loading, operation):
            signal_received.append(('loading', is_loading, operation))
        
        # Connect signals
        base_vm.processing_state_changed.connect(on_processing_changed)
        base_vm.loading_state_changed.connect(on_loading_changed)
        
        # Emit signals
        base_vm._set_processing_state(True)
        base_vm._set_loading_state(True, "Test operation")
        
        # Process Qt events
        qapp.processEvents()
        
        # Verify signals were received
        assert len(signal_received) == 2
        assert ('processing', True) in signal_received
        assert ('loading', True, "Test operation") in signal_received

    def test_viewmodel_inheritance_patterns(self, qapp, mock_session):
        """Test that ViewModels properly inherit BaseViewModel functionality."""
        class TestViewModel(BaseViewModel):
            custom_signal = Signal(str)
            
            def __init__(self, session=None):
                super().__init__(session)
                self.custom_state = False
            
            def custom_operation(self):
                self._set_processing_state(True)
                try:
                    # Simulate work
                    result = "Success"
                    self.custom_signal.emit(result)
                    return result
                finally:
                    self._set_processing_state(False)
        
        vm = TestViewModel(mock_session)
        
        # Test inherited functionality
        assert hasattr(vm, 'processing_state_changed')
        assert hasattr(vm, 'validation_failed')
        assert vm._session is mock_session
        
        # Test custom functionality
        custom_spy = Mock()
        processing_spy = Mock()
        
        vm.custom_signal.connect(custom_spy)
        vm.processing_state_changed.connect(processing_spy)
        
        result = vm.custom_operation()
        
        assert result == "Success"
        custom_spy.assert_called_once_with("Success")
        assert processing_spy.call_count == 2  # True, then False

    def test_complex_validation_integration(self, base_vm):
        """Test complex validation scenarios with signal integration."""
        validation_spy = Mock()
        field_error_spy = Mock()
        field_clear_spy = Mock()
        
        base_vm.validation_failed.connect(validation_spy)
        base_vm.field_validation_error.connect(field_error_spy)
        base_vm.field_validation_cleared.connect(field_clear_spy)
        
        # Simulate complex form validation
        field_validations = [
            ("", "name", "Name", {"required": True}),
            ("invalid_email", "email", "Email", {"required": True}),
            ("short", "description", "Description", {"min_length": 10})
        ]
        
        result = base_vm._batch_validate_fields(field_validations)
        
        assert not result.is_valid
        assert len(result.errors) >= 3
        
        # Check that field-level errors were emitted
        assert field_error_spy.call_count >= 3