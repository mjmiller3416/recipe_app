"""app/ui/utils/form_validation.py

Comprehensive form validation framework for Recipe App UI components.
Provides reusable validation patterns, error collection, and consistent
validation logic across all form-based views.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from app.core.utils.text_utils import sanitize_form_input

# ── Validation Result ───────────────────────────────────────────────────────────────────────────────────────
class ValidationResult:
    """Container for form validation results with comprehensive error tracking."""
    
    def __init__(self, is_valid: bool = True):
        """Initialize validation result.
        
        Args:
            is_valid: Initial validation state
        """
        self.is_valid = is_valid
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.field_errors: Dict[str, List[str]] = {}
        self.field_warnings: Dict[str, List[str]] = {}
    
    def add_error(self, error: str, field_name: str = None) -> None:
        """Add a validation error.
        
        Args:
            error: Error message
            field_name: Optional field name for field-specific errors
        """
        self.errors.append(error)
        self.is_valid = False
        
        if field_name:
            if field_name not in self.field_errors:
                self.field_errors[field_name] = []
            self.field_errors[field_name].append(error)
    
    def add_warning(self, warning: str, field_name: str = None) -> None:
        """Add a validation warning.
        
        Args:
            warning: Warning message
            field_name: Optional field name for field-specific warnings
        """
        self.warnings.append(warning)
        
        if field_name:
            if field_name not in self.field_warnings:
                self.field_warnings[field_name] = []
            self.field_warnings[field_name].append(warning)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one.
        
        Args:
            other: ValidationResult to merge
        """
        if not other.is_valid:
            self.is_valid = False
        
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        
        # Merge field-specific errors and warnings
        for field, errors in other.field_errors.items():
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].extend(errors)
        
        for field, warnings in other.field_warnings.items():
            if field not in self.field_warnings:
                self.field_warnings[field] = []
            self.field_warnings[field].extend(warnings)
    
    def get_field_errors(self, field_name: str) -> List[str]:
        """Get errors for a specific field."""
        return self.field_errors.get(field_name, [])
    
    def get_field_warnings(self, field_name: str) -> List[str]:
        """Get warnings for a specific field."""
        return self.field_warnings.get(field_name, [])
    
    def has_field_issues(self, field_name: str) -> bool:
        """Check if a field has any errors or warnings."""
        return field_name in self.field_errors or field_name in self.field_warnings
    
    def get_all_messages(self) -> List[str]:
        """Get all error and warning messages."""
        return self.errors + self.warnings
    
    def get_summary(self) -> str:
        """Get a summary of validation results."""
        issues = []
        if self.errors:
            issues.append(f"{len(self.errors)} errors")
        if self.warnings:
            issues.append(f"{len(self.warnings)} warnings")
        return ", ".join(issues) if issues else "No issues"


# ── Form Validators ─────────────────────────────────────────────────────────────────────────────────────────
class FormValidator:
    """Comprehensive form validation utilities for Recipe App forms."""
    
    @staticmethod
    def validate_shopping_item_form(name: str, qty: str, unit: str, category: str) -> ValidationResult:
        """
        Validate shopping item form data.
        
        Args:
            name: Item name
            qty: Quantity as string
            unit: Measurement unit
            category: Item category
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        result = ValidationResult()
        
        # Required field validations
        if not FormValidator._validate_required_text(name, "name"):
            result.add_error("Item name is required", "name")
        elif len(name.strip()) > 200:
            result.add_error("Item name cannot exceed 200 characters", "name")
        
        if not FormValidator._validate_required_text(qty, "quantity"):
            result.add_error("Quantity is required", "quantity")
        else:
            # Validate quantity is numeric and positive
            qty_validation = FormValidator._validate_positive_number(qty, "quantity")
            result.merge(qty_validation)
        
        # Optional field validations with warnings
        if not FormValidator._validate_required_text(unit, "unit"):
            result.add_warning("Unit not specified - item will be added without unit", "unit")
        elif len(unit.strip()) > 50:
            result.add_error("Unit cannot exceed 50 characters", "unit")
        
        if not FormValidator._validate_required_text(category, "category"):
            result.add_warning("Category not specified - item will be added to 'Other' category", "category")
        elif len(category.strip()) > 100:
            result.add_error("Category cannot exceed 100 characters", "category")
        
        return result
    
    @staticmethod
    def validate_recipe_form(title: str, description: str, servings: str, prep_time: str, cook_time: str) -> ValidationResult:
        """
        Validate recipe form data.
        
        Args:
            title: Recipe title
            description: Recipe description
            servings: Number of servings as string
            prep_time: Preparation time in minutes as string
            cook_time: Cooking time in minutes as string
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        result = ValidationResult()
        
        # Required fields
        if not FormValidator._validate_required_text(title, "title"):
            result.add_error("Recipe title is required", "title")
        elif len(title.strip()) > 200:
            result.add_error("Recipe title cannot exceed 200 characters", "title")
        elif len(title.strip()) < 3:
            result.add_error("Recipe title must be at least 3 characters", "title")
        
        # Optional fields with constraints
        if description and len(description.strip()) > 1000:
            result.add_error("Recipe description cannot exceed 1000 characters", "description")
        
        if servings:
            servings_validation = FormValidator._validate_positive_integer(servings, "servings", min_value=1, max_value=50)
            result.merge(servings_validation)
        
        if prep_time:
            prep_validation = FormValidator._validate_positive_integer(prep_time, "prep_time", min_value=0, max_value=1440)  # Max 24 hours
            result.merge(prep_validation)
        
        if cook_time:
            cook_validation = FormValidator._validate_positive_integer(cook_time, "cook_time", min_value=0, max_value=1440)  # Max 24 hours
            result.merge(cook_validation)
        
        return result
    
    @staticmethod
    def validate_ingredient_form(name: str, quantity: str, unit: str, category: str) -> ValidationResult:
        """
        Validate ingredient form data.
        
        Args:
            name: Ingredient name
            quantity: Quantity as string
            unit: Measurement unit
            category: Ingredient category
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        result = ValidationResult()
        
        # Required fields
        if not FormValidator._validate_required_text(name, "name"):
            result.add_error("Ingredient name is required", "name")
        elif len(name.strip()) > 150:
            result.add_error("Ingredient name cannot exceed 150 characters", "name")
        
        if not FormValidator._validate_required_text(quantity, "quantity"):
            result.add_error("Quantity is required", "quantity")
        else:
            qty_validation = FormValidator._validate_positive_number(quantity, "quantity")
            result.merge(qty_validation)
        
        if not FormValidator._validate_required_text(unit, "unit"):
            result.add_error("Unit is required", "unit")
        elif len(unit.strip()) > 50:
            result.add_error("Unit cannot exceed 50 characters", "unit")
        
        # Category is optional but constrained
        if category and len(category.strip()) > 100:
            result.add_error("Category cannot exceed 100 characters", "category")
        
        return result
    
    # ── Helper Validation Methods ───────────────────────────────────────────────────────────────────────────────
    
    @staticmethod
    def _validate_required_text(value: Any, field_name: str) -> bool:
        """Validate that a text field has content."""
        return bool(value and str(value).strip())
    
    @staticmethod
    def _validate_positive_number(value: str, field_name: str, min_value: float = 0) -> ValidationResult:
        """
        Validate that a string represents a positive number.
        
        Args:
            value: String value to validate
            field_name: Field name for error messages
            min_value: Minimum allowed value (default: 0)
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not value or not str(value).strip():
            return result  # Empty is handled by required validation
        
        try:
            numeric_value = float(str(value).strip())
            
            if numeric_value < min_value:
                result.add_error(f"{field_name.title()} must be at least {min_value}", field_name)
            elif numeric_value > 999999:  # Reasonable upper limit
                result.add_error(f"{field_name.title()} cannot exceed 999,999", field_name)
        except ValueError:
            result.add_error(f"{field_name.title()} must be a valid number", field_name)
        
        return result
    
    @staticmethod
    def _validate_positive_integer(value: str, field_name: str, min_value: int = 0, max_value: int = None) -> ValidationResult:
        """
        Validate that a string represents a positive integer.
        
        Args:
            value: String value to validate
            field_name: Field name for error messages
            min_value: Minimum allowed value (default: 0)
            max_value: Maximum allowed value (optional)
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not value or not str(value).strip():
            return result  # Empty is handled by required validation
        
        try:
            numeric_value = int(float(str(value).strip()))  # Convert via float to handle "5.0" -> 5
            
            if numeric_value < min_value:
                result.add_error(f"{field_name.title()} must be at least {min_value}", field_name)
            elif max_value is not None and numeric_value > max_value:
                result.add_error(f"{field_name.title()} cannot exceed {max_value}", field_name)
        except ValueError:
            result.add_error(f"{field_name.title()} must be a whole number", field_name)
        
        return result
    
    @staticmethod
    def _validate_email(email: str, field_name: str) -> ValidationResult:
        """Validate email format."""
        result = ValidationResult()
        
        if not email or not email.strip():
            return result  # Empty is handled by required validation
        
        email = email.strip()
        
        # Basic email validation
        if "@" not in email or "." not in email:
            result.add_error(f"{field_name.title()} must be a valid email address", field_name)
        elif len(email) > 320:  # RFC limit
            result.add_error(f"{field_name.title()} cannot exceed 320 characters", field_name)
        elif len(email) < 5:  # Minimum reasonable email
            result.add_error(f"{field_name.title()} must be at least 5 characters", field_name)
        
        return result
    
    @staticmethod
    def sanitize_form_data(form_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Sanitize all form data values.
        
        Args:
            form_data: Dictionary of form field values
            
        Returns:
            Dictionary with sanitized string values
        """
        sanitized = {}
        
        for field, value in form_data.items():
            if value is None:
                sanitized[field] = ""
            elif isinstance(value, str):
                sanitized[field] = sanitize_form_input(value)
            else:
                sanitized[field] = sanitize_form_input(str(value))
        
        return sanitized
    
    @staticmethod
    def create_custom_validator(validation_func: Callable[[Any], bool], 
                               error_message: str, 
                               field_name: str) -> Callable[[Any], ValidationResult]:
        """
        Create a custom validator function.
        
        Args:
            validation_func: Function that takes a value and returns bool
            error_message: Error message if validation fails
            field_name: Field name for error tracking
            
        Returns:
            Validator function that returns ValidationResult
        """
        def validator(value: Any) -> ValidationResult:
            result = ValidationResult()
            
            if not validation_func(value):
                result.add_error(error_message, field_name)
            
            return result
        
        return validator


# ── Validation Decorators ──────────────────────────────────────────────────────────────────────────────────
def validate_form_data(validator_func: Callable) -> Callable:
    """
    Decorator to automatically validate form data before method execution.
    
    Args:
        validator_func: Function that takes form data and returns ValidationResult
        
    Returns:
        Decorated method that validates input first
    """
    def decorator(method: Callable) -> Callable:
        def wrapper(self, *args, **kwargs):
            # Assume first argument after self is form data
            if args:
                form_data = args[0] if isinstance(args[0], dict) else None
                
                if form_data:
                    validation_result = validator_func(form_data)
                    
                    if not validation_result.is_valid:
                        # Handle validation failure (emit signals if available)
                        if hasattr(self, '_emit_validation_errors'):
                            self._emit_validation_errors(validation_result.errors)
                        return False
            
            # Proceed with original method if validation passes
            return method(self, *args, **kwargs)
        
        return wrapper
    return decorator


# ── Field Validators ────────────────────────────────────────────────────────────────────────────────────────
class FieldValidators:
    """Collection of common field validation functions."""
    
    @staticmethod
    def non_empty_string(value: Any) -> bool:
        """Validate that value is a non-empty string."""
        return bool(value and str(value).strip())
    
    @staticmethod
    def positive_number(value: Any) -> bool:
        """Validate that value is a positive number."""
        try:
            return float(str(value).strip()) > 0
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def whole_number(value: Any) -> bool:
        """Validate that value is a whole number."""
        try:
            num = float(str(value).strip())
            return num == int(num) and num >= 0
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def length_between(min_len: int, max_len: int) -> Callable[[Any], bool]:
        """Create validator for string length constraints."""
        def validator(value: Any) -> bool:
            if not value:
                return True  # Length validation only applies to non-empty values
            return min_len <= len(str(value).strip()) <= max_len
        return validator
    
    @staticmethod
    def in_choices(choices: List[str]) -> Callable[[Any], bool]:
        """Create validator for choice constraints."""
        def validator(value: Any) -> bool:
            return str(value).strip() in choices
        return validator