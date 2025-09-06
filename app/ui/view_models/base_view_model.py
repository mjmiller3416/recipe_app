"""app/ui/view_models/base_view_model.py

Base ViewModel class implementing common MVVM patterns for Recipe App.
Provides shared functionality for session management, validation, error handling,
and DTO construction patterns used across all ViewModels.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from PySide6.QtCore import QObject, Signal

from _dev_tools import DebugLogger
from app.core.utils.text_utils import sanitize_form_input

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# ── Base Validation Result ──────────────────────────────────────────────────────────────────────────────────
class BaseValidationResult:
    """Base container for validation results with errors, warnings, and success status."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str) -> None:
        """Add an error message to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the validation result."""
        self.warnings.append(warning)
    
    def merge(self, other: 'BaseValidationResult') -> None:
        """Merge another validation result into this one."""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
    
    def has_issues(self) -> bool:
        """Check if there are any errors or warnings."""
        return bool(self.errors or self.warnings)
    
    def get_summary(self) -> str:
        """Get a summary of validation issues."""
        issues = []
        if self.errors:
            issues.append(f"{len(self.errors)} errors")
        if self.warnings:
            issues.append(f"{len(self.warnings)} warnings")
        return ", ".join(issues) if issues else "No issues"


# ── Base ViewModel ───────────────────────────────────────────────────────────────────────────────────────────
class BaseViewModel(QObject):
    """
    Base ViewModel class implementing common MVVM patterns.
    
    Provides:
    - Session management with proper cleanup
    - Common validation patterns
    - Error handling utilities
    - DTO construction helpers
    - Form state management
    - Signal management utilities
    """
    
    # Common signals for all ViewModels
    processing_state_changed = Signal(bool)  # is_processing
    loading_state_changed = Signal(bool, str)  # is_loading, operation_description
    error_occurred = Signal(str, str)  # error_type, error_message
    validation_failed = Signal(list)  # list[error_messages]
    state_reset = Signal()
    
    # Field validation signals
    field_validation_error = Signal(str, str)  # field_name, error_message
    field_validation_cleared = Signal(str)  # field_name
    
    def __init__(self, session: Session | None = None):
        """
        Initialize the BaseViewModel with optional session injection.
        
        Args:
            session: Optional SQLAlchemy session for dependency injection.
                    If None, session will be created when needed.
        """
        super().__init__()
        
        # Session management
        self._session = session
        self._owns_session = session is None  # Track if we need to manage session lifecycle
        
        # Common state
        self._is_processing = False
        self._is_loading = False
        self._validation_errors: List[str] = []
        
        DebugLogger.log(f"{self.__class__.__name__} initialized with session injection", "debug")
    
    # ── Session Management ──────────────────────────────────────────────────────────────────────────────────────
    
    def _ensure_session(self) -> bool:
        """
        Ensure a database session is available.
        Creates session if needed and tracks ownership for proper cleanup.
        
        Returns:
            bool: True if session is available, False if creation failed
        """
        if self._session is not None:
            return True
        
        try:
            from app.core.database.db import create_session
            self._session = create_session()
            self._owns_session = True
            DebugLogger.log(f"{self.__class__.__name__} created database session", "debug")
            return True
        except Exception as e:
            DebugLogger.log(f"Failed to create database session in {self.__class__.__name__}: {e}", "error")
            return False
    
    def _cleanup_session(self) -> None:
        """
        Clean up database session if owned by this ViewModel.
        Only closes sessions that were created by this ViewModel instance.
        """
        if self._session is not None and self._owns_session:
            try:
                self._session.close()
                DebugLogger.log(f"{self.__class__.__name__} closed database session", "debug")
            except Exception as e:
                DebugLogger.log(f"Error closing session in {self.__class__.__name__}: {e}", "warning")
            finally:
                self._session = None
    
    def __del__(self):
        """Ensure session cleanup on ViewModel destruction."""
        self._cleanup_session()
    
    # ── State Management ─────────────────────────────────────────────────────────────────────────────────────────
    
    @property
    def is_processing(self) -> bool:
        """Check if the ViewModel is currently processing an operation."""
        return self._is_processing
    
    @property
    def is_loading(self) -> bool:
        """Check if the ViewModel is currently loading data."""
        return self._is_loading
    
    @property
    def has_validation_errors(self) -> bool:
        """Check if there are current validation errors."""
        return bool(self._validation_errors)
    
    @property
    def validation_errors(self) -> List[str]:
        """Get current validation errors (read-only copy)."""
        return self._validation_errors.copy()
    
    def _set_processing_state(self, is_processing: bool) -> None:
        """Set processing state and emit signal."""
        if self._is_processing != is_processing:
            self._is_processing = is_processing
            self.processing_state_changed.emit(is_processing)
    
    def _set_loading_state(self, is_loading: bool, operation: str = "") -> None:
        """Set loading state and emit signal."""
        if self._is_loading != is_loading:
            self._is_loading = is_loading
            self.loading_state_changed.emit(is_loading, operation)
    
    def _reset_internal_state(self) -> None:
        """Reset all internal state to initial values."""
        self._is_processing = False
        self._is_loading = False
        self._validation_errors.clear()
    
    def reset_state(self) -> None:
        """Reset ViewModel to initial state and emit signal."""
        self._reset_internal_state()
        self.state_reset.emit()
        DebugLogger.log(f"{self.__class__.__name__} state reset", "debug")
    
    # ── Error Handling ──────────────────────────────────────────────────────────────────────────────────────────
    
    def _handle_error(self, error: Exception, context: str, error_type: str = "general") -> None:
        """
        Handle errors with consistent logging and signaling.
        
        Args:
            error: The exception that occurred
            context: Context description for the error
            error_type: Type of error for categorization
        """
        error_message = f"{context}: {str(error)}"
        DebugLogger.log(error_message, "error")
        self.error_occurred.emit(error_type, error_message)
    
    def _emit_validation_errors(self, errors: List[str]) -> None:
        """Emit validation errors and update internal state."""
        self._validation_errors = errors.copy()
        if errors:
            self.validation_failed.emit(errors)
    
    def _clear_validation_errors(self) -> None:
        """Clear validation errors."""
        self._validation_errors.clear()
    
    # ── Field Validation Utilities ──────────────────────────────────────────────────────────────────────────────
    
    def _emit_field_error(self, field_name: str, error_message: str) -> None:
        """Emit field validation error signal."""
        self.field_validation_error.emit(field_name, error_message)
    
    def _clear_field_error(self, field_name: str) -> None:
        """Clear field validation error signal."""
        self.field_validation_cleared.emit(field_name)
    
    def _validate_required_field(self, value: str, field_name: str, display_name: str) -> bool:
        """
        Validate a required field and emit appropriate signals.
        
        Args:
            value: Field value to validate
            field_name: Internal field name for signals
            display_name: User-friendly field name for error messages
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not value.strip():
            self._emit_field_error(field_name, f"{display_name} is required")
            return False
        
        self._clear_field_error(field_name)
        return True
    
    def _validate_field_length(self, value: str, field_name: str, display_name: str, 
                             min_length: int = None, max_length: int = None) -> bool:
        """
        Validate field length constraints.
        
        Args:
            value: Field value to validate
            field_name: Internal field name for signals
            display_name: User-friendly field name for error messages
            min_length: Minimum allowed length (optional)
            max_length: Maximum allowed length (optional)
            
        Returns:
            bool: True if valid, False otherwise
        """
        if min_length is not None and len(value.strip()) < min_length:
            self._emit_field_error(field_name, f"{display_name} must be at least {min_length} characters")
            return False
        
        if max_length is not None and len(value.strip()) > max_length:
            self._emit_field_error(field_name, f"{display_name} cannot exceed {max_length} characters")
            return False
        
        self._clear_field_error(field_name)
        return True
    
    def _validate_numeric_field(self, value: str, field_name: str, display_name: str,
                               min_value: float = None, max_value: float = None) -> bool:
        """
        Validate numeric field constraints.
        
        Args:
            value: Field value to validate
            field_name: Internal field name for signals
            display_name: User-friendly field name for error messages
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not value.strip():
            self._clear_field_error(field_name)
            return True  # Empty is valid for optional numeric fields
        
        try:
            numeric_value = float(value.strip())
            
            if min_value is not None and numeric_value < min_value:
                self._emit_field_error(field_name, f"{display_name} must be at least {min_value}")
                return False
            
            if max_value is not None and numeric_value > max_value:
                self._emit_field_error(field_name, f"{display_name} cannot exceed {max_value}")
                return False
            
            self._clear_field_error(field_name)
            return True
            
        except ValueError:
            self._emit_field_error(field_name, f"{display_name} must be a valid number")
            return False
    
    # ── DTO Construction Helpers ────────────────────────────────────────────────────────────────────────────────
    
    def _sanitize_form_input(self, value: Any) -> str:
        """Safely sanitize form input with null handling."""
        if value is None:
            return ""
        return sanitize_form_input(str(value))
    
    def _prepare_dto_field(self, value: Any, required: bool = False, default: Any = None) -> Any:
        """
        Prepare a field value for DTO construction.
        
        Args:
            value: Raw field value
            required: Whether the field is required
            default: Default value if field is empty/None
            
        Returns:
            Prepared value for DTO
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            if required:
                raise ValueError("Required field cannot be empty")
            return default
        
        if isinstance(value, str):
            sanitized = self._sanitize_form_input(value)
            return sanitized if sanitized else default
        
        return value
    
    def _build_dto_data(self, form_data: Dict[str, Any], field_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build DTO data dictionary from form data using field mapping configuration.
        
        Args:
            form_data: Raw form data dictionary
            field_mapping: Dictionary mapping form fields to DTO configuration
                          Format: {form_field: {dto_field: str, required: bool, default: Any, transform: callable}}
        
        Returns:
            Dict[str, Any]: Prepared DTO data
        """
        dto_data = {}
        
        for form_field, config in field_mapping.items():
            dto_field = config.get('dto_field', form_field)
            required = config.get('required', False)
            default = config.get('default', None)
            transform = config.get('transform', None)
            
            try:
                raw_value = form_data.get(form_field)
                
                # Apply transformation if provided
                if transform and callable(transform):
                    processed_value = transform(raw_value)
                else:
                    processed_value = self._prepare_dto_field(raw_value, required, default)
                
                dto_data[dto_field] = processed_value
                
            except Exception as e:
                DebugLogger.log(f"Error processing field {form_field}: {e}", "error")
                if required:
                    raise
                dto_data[dto_field] = default
        
        return dto_data
    
    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────────────────────
    
    def _safe_execute(self, operation: callable, context: str, *args, **kwargs) -> Any:
        """
        Safely execute an operation with error handling.
        
        Args:
            operation: Function to execute
            context: Context description for error messages
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Operation result or None if failed
        """
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            self._handle_error(e, context)
            return None
    
    def _batch_validate_fields(self, field_validations: List[tuple]) -> BaseValidationResult:
        """
        Perform batch validation of multiple fields.
        
        Args:
            field_validations: List of (field_value, field_name, display_name, validation_rules) tuples
            
        Returns:
            BaseValidationResult: Combined validation result
        """
        result = BaseValidationResult()
        
        for validation_data in field_validations:
            field_value, field_name, display_name, rules = validation_data
            
            # Required field check
            if rules.get('required', False):
                if not self._validate_required_field(field_value, field_name, display_name):
                    result.add_error(f"{display_name} is required")
            
            # Length validation
            if field_value.strip():  # Only validate length if field has content
                min_len = rules.get('min_length')
                max_len = rules.get('max_length')
                if not self._validate_field_length(field_value, field_name, display_name, min_len, max_len):
                    result.add_error(f"{display_name} length validation failed")
                
                # Numeric validation
                if rules.get('numeric', False):
                    min_val = rules.get('min_value')
                    max_val = rules.get('max_value')
                    if not self._validate_numeric_field(field_value, field_name, display_name, min_val, max_val):
                        result.add_error(f"{display_name} numeric validation failed")
        
        return result