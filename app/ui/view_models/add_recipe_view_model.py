"""app/ui/view_models/add_recipe_view_model.py

AddRecipeViewModel for MVVM architecture compliance.
Handles all recipe creation business logic, validation, and error handling.
Serves as the bridge between the AddRecipes View and Core services.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Signal

from _dev_tools import DebugLogger
from app.core.dtos.ingredient_dtos import IngredientSearchDTO
from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeIngredientDTO
from app.core.services.ingredient_service import IngredientService
from app.core.services.recipe_service import (
    DuplicateRecipeError,
    RecipeSaveError,
    RecipeService,
)
from app.core.utils.conversion_utils import (
    parse_servings_range,
    safe_float_conversion,
    safe_int_conversion,
)
from app.core.utils.text_utils import sanitize_form_input, sanitize_multiline_input
from app.ui.view_models.base_view_model import BaseValidationResult, BaseViewModel

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.core.models.ingredient import Ingredient
    from app.core.models.recipe import Recipe


# Note: Using BaseValidationResult from base_view_model instead


# ── Form Data Container ─────────────────────────────────────────────────────────────────────────────────────
class RecipeFormData:
    """Container for raw recipe form data before validation and transformation."""
    
    def __init__(self):
        # Recipe basic info
        self.recipe_name: str = ""
        self.recipe_category: str = ""
        self.meal_type: str = ""
        self.dietary_preference: str = ""
        self.total_time: str = ""
        self.servings: str = ""
        self.directions: str = ""
        self.notes: str = ""
        
        # Image handling
        self.reference_image_path: str = ""
        self.banner_image_path: str = ""
        
        # Ingredients (list of raw form data dicts)
        self.ingredients: list[dict] = []


# ── Add Recipe ViewModel ────────────────────────────────────────────────────────────────────────────────────
class AddRecipeViewModel(BaseViewModel):
    """
    ViewModel for AddRecipes view implementing proper MVVM architecture.
    
    Handles all recipe creation business logic, form validation, data transformation,
    and coordination between UI and Core services. Ensures clean separation of concerns
    by removing all business logic from the View layer.
    """
    
    # Specific signals for AddRecipe operations (inherits common signals from BaseViewModel)
    recipe_saved_successfully = Signal(str)  # recipe_name
    recipe_save_failed = Signal(str)  # error_message
    ingredient_search_completed = Signal(list)  # list[Ingredient]
    form_cleared = Signal()
    form_validation_state_changed = Signal(bool)  # is_valid
    recipe_name_validated = Signal(bool, str)  # is_unique, message
    
    def __init__(self, session: Session | None = None):
        """
        Initialize the AddRecipeViewModel with Core service dependencies.
        
        Args:
            session: Optional SQLAlchemy session for dependency injection.
                    If None, services will create their own sessions.
        """
        super().__init__(session)
        
        # Initialize Core services with proper session management
        self._initialize_services()
        
        # Internal state specific to AddRecipe
        self._current_form_data: RecipeFormData | None = None
        
        DebugLogger.log("AddRecipeViewModel initialized with dependency injection", "debug")
    
    def _initialize_services(self) -> None:
        """Initialize Core services with proper session management."""
        if not self._ensure_session():
            DebugLogger.log("Failed to ensure session in AddRecipeViewModel", "error")
            return
        
        try:
            self.recipe_service = RecipeService(self._session)
            self.ingredient_service = IngredientService(self._session)
            DebugLogger.log("AddRecipeViewModel services initialized", "debug")
        except Exception as e:
            DebugLogger.log(f"Failed to initialize services in AddRecipeViewModel: {e}", "error")
            self.recipe_service = None
            self.ingredient_service = None
    
    # ── Core Recipe Operations ──────────────────────────────────────────────────────────────────────────────
    
    def create_recipe(self, form_data: RecipeFormData) -> None:
        """
        Main recipe creation orchestrator.
        
        Validates form data, transforms to DTOs, and coordinates with RecipeService
        to create the recipe. Handles all error scenarios and success/failure states.
        
        Args:
            form_data: Raw form data from the UI layer
        """
        if self.is_processing:
            DebugLogger.log("Recipe creation already in progress, ignoring duplicate request", "warning")
            return
        
        self._set_processing_state(True)
        self._current_form_data = form_data
        self._clear_validation_errors()
        
        # Emit loading state change
        self._set_loading_state(True, "Saving recipe...")
        
        try:
            # Step 1: Validate form data
            validation_result = self._validate_recipe_form(form_data)
            if not validation_result.is_valid:
                self._emit_validation_errors(validation_result.errors)
                self.form_validation_state_changed.emit(False)
                return
            
            self.form_validation_state_changed.emit(True)
            
            # Step 2: Transform raw data to DTOs
            recipe_dto = self._transform_to_recipe_dto(form_data)
            if not recipe_dto:
                self.recipe_save_failed.emit("Failed to process form data")
                return
            
            # Step 3: Create recipe via service
            self._set_loading_state(True, "Creating recipe...")
            created_recipe = self.recipe_service.create_recipe_with_ingredients(recipe_dto)
            
            # Step 4: Handle image updates if provided
            if form_data.reference_image_path:
                self._set_loading_state(True, "Saving recipe image...")
                self._update_recipe_image(created_recipe.id, form_data.reference_image_path)
            
            # Step 5: Success - emit signal and reset state
            DebugLogger.log(f"Recipe '{created_recipe.recipe_name}' created successfully with ID={created_recipe.id}", "info")
            self.recipe_saved_successfully.emit(created_recipe.recipe_name)
            self._reset_internal_state()
            
        except DuplicateRecipeError as e:
            DebugLogger.log(f"Duplicate recipe error: {e}", "warning")
            self.recipe_save_failed.emit(str(e))
        except RecipeSaveError as e:
            DebugLogger.log(f"Recipe save error: {e}", "error")
            self.recipe_save_failed.emit(f"Failed to save recipe: {e}")
        except Exception as e:
            DebugLogger.log(f"Unexpected error during recipe creation: {e}", "error")
            self.recipe_save_failed.emit(f"An unexpected error occurred: {e}")
        finally:
            self._set_processing_state(False)
            self._set_loading_state(False, "")
    
    # ── Form Validation ─────────────────────────────────────────────────────────────────────────────────────
    
    def _validate_recipe_form(self, form_data: RecipeFormData) -> BaseValidationResult:
        """
        Comprehensive validation of recipe form data.
        
        Validates required fields, data types, business rules, and ingredient data.
        
        Args:
            form_data: Raw form data to validate
            
        Returns:
            BaseValidationResult: Contains validation status and error messages
        """
        result = BaseValidationResult()
        
        # Required field validation
        if not form_data.recipe_name.strip():
            result.add_error("Recipe name is required")
        
        if not form_data.meal_type.strip():
            result.add_error("Meal type must be selected")
        
        if not form_data.servings.strip():
            result.add_error("Number of servings is required")
        
        # Data type and range validation
        if form_data.servings.strip():
            servings_value = parse_servings_range(form_data.servings)
            if servings_value is None or servings_value < 1:
                result.add_error("Servings must be a valid positive number")
        
        if form_data.total_time.strip():
            time_value = safe_int_conversion(form_data.total_time)
            if time_value is not None and time_value < 0:
                result.add_error("Total time cannot be negative")
        
        # Ingredient validation
        ingredient_validation = self._validate_ingredients(form_data.ingredients)
        if not ingredient_validation.is_valid:
            result.errors.extend(ingredient_validation.errors)
            result.is_valid = False
        
        # Business rule validation
        if len(form_data.recipe_name.strip()) > 200:
            result.add_error("Recipe name cannot exceed 200 characters")
        
        if form_data.directions and len(form_data.directions) > 5000:
            result.add_error("Directions cannot exceed 5000 characters")
        
        return result
    
    def _validate_ingredients(self, ingredients: list[dict]) -> BaseValidationResult:
        """
        Validate ingredient data from form.
        
        Args:
            ingredients: List of raw ingredient data dictionaries
            
        Returns:
            BaseValidationResult: Contains validation status and error messages
        """
        result = BaseValidationResult()
        
        if not ingredients:
            result.add_error("At least one ingredient is required")
            return result
        
        valid_ingredients = []
        for i, ingredient in enumerate(ingredients, 1):
            # Check required fields
            if not ingredient.get("ingredient_name", "").strip():
                result.add_error(f"Ingredient {i}: Name is required")
                continue
            
            if not ingredient.get("ingredient_category", "").strip():
                result.add_error(f"Ingredient {i}: Category is required")
                continue
            
            # Validate quantity if provided
            quantity_str = ingredient.get("quantity", "")
            if quantity_str:
                quantity = safe_float_conversion(str(quantity_str))
                if quantity is None or quantity <= 0:
                    result.add_error(f"Ingredient {i}: Quantity must be a positive number")
                    continue
            
            valid_ingredients.append(ingredient)
        
        if not valid_ingredients:
            result.add_error("No valid ingredients found")
        
        return result
    
    # ── Data Transformation ─────────────────────────────────────────────────────────────────────────────────
    
    def _transform_to_recipe_dto(self, form_data: RecipeFormData) -> RecipeCreateDTO | None:
        """
        Transform raw form data into a validated RecipeCreateDTO.
        
        Handles data sanitization, type conversion, and DTO construction.
        
        Args:
            form_data: Raw form data from the UI
            
        Returns:
            RecipeCreateDTO | None: Validated DTO or None if transformation fails
        """
        try:
            # Transform ingredients first
            ingredient_dtos = self._transform_ingredients(form_data.ingredients)
            if not ingredient_dtos:
                DebugLogger.log("Failed to transform ingredients to DTOs", "error")
                return None
            
            # Sanitize and transform recipe data
            recipe_data = {
                "recipe_name": sanitize_form_input(form_data.recipe_name),
                "recipe_category": sanitize_form_input(form_data.recipe_category) or "General",
                "meal_type": sanitize_form_input(form_data.meal_type),
                "diet_pref": sanitize_form_input(form_data.dietary_preference) or None,
                "total_time": safe_int_conversion(form_data.total_time),
                "servings": parse_servings_range(form_data.servings),
                "directions": sanitize_multiline_input(form_data.directions) or None,
                "notes": sanitize_multiline_input(form_data.notes) or None,
                "reference_image_path": form_data.reference_image_path or None,
                "banner_image_path": form_data.banner_image_path or None,
                "ingredients": ingredient_dtos
            }
            
            # Create and validate DTO
            recipe_dto = RecipeCreateDTO(**recipe_data)
            DebugLogger.log(f"Successfully transformed form data to RecipeCreateDTO: {recipe_dto.recipe_name}", "debug")
            return recipe_dto
            
        except Exception as e:
            DebugLogger.log(f"Failed to transform form data to DTO: {e}", "error")
            return None
    
    def _transform_ingredients(self, raw_ingredients: list[dict]) -> list[RecipeIngredientDTO]:
        """
        Transform raw ingredient data to validated RecipeIngredientDTOs.
        
        Args:
            raw_ingredients: List of raw ingredient dictionaries from form
            
        Returns:
            list[RecipeIngredientDTO]: List of validated ingredient DTOs
        """
        ingredient_dtos = []
        
        for ingredient_data in raw_ingredients:
            try:
                # Skip empty ingredients
                if not ingredient_data.get("ingredient_name", "").strip():
                    continue
                
                dto_data = {
                    "ingredient_name": sanitize_form_input(ingredient_data["ingredient_name"]),
                    "ingredient_category": sanitize_form_input(ingredient_data["ingredient_category"]),
                    "quantity": safe_float_conversion(ingredient_data.get("quantity", "")),
                    "unit": sanitize_form_input(ingredient_data.get("unit", "")) or None,
                    "existing_ingredient_id": ingredient_data.get("existing_ingredient_id")
                }
                
                ingredient_dto = RecipeIngredientDTO(**dto_data)
                ingredient_dtos.append(ingredient_dto)
                
            except Exception as e:
                DebugLogger.log(f"Failed to transform ingredient data: {ingredient_data}, error: {e}", "error")
                continue
        
        DebugLogger.log(f"Transformed {len(ingredient_dtos)} ingredients to DTOs", "debug")
        return ingredient_dtos
    
    # ── Image Handling ──────────────────────────────────────────────────────────────────────────────────────
    
    def _update_recipe_image(self, recipe_id: int, image_path: str) -> None:
        """
        Update recipe with selected image path.
        
        Args:
            recipe_id: ID of the created recipe
            image_path: Path to the selected image
        """
        try:
            self.recipe_service.update_recipe_reference_image_path(recipe_id, image_path)
            DebugLogger.log(f"Updated recipe {recipe_id} with reference image: {image_path}", "info")
        except Exception as e:
            DebugLogger.log(f"Failed to update recipe {recipe_id} reference image: {e}", "warning")
            # Don't fail the entire operation for image update failures
    
    # ── Ingredient Search Operations ────────────────────────────────────────────────────────────────────────
    
    def search_ingredients(self, search_term: str, category: str | None = None) -> list[Ingredient]:
        """
        Search for ingredients using the IngredientService.
        
        Args:
            search_term: Term to search for in ingredient names
            category: Optional category filter
            
        Returns:
            list[Ingredient]: List of matching ingredients
        """
        if not self.ingredient_service:
            # Initialize services if not already done
            self._initialize_services()
            if not self.ingredient_service:
                DebugLogger.log("Failed to initialize ingredient service for search", "error")
                return []
        
        try:
            search_dto = IngredientSearchDTO(
                search_term=search_term.strip(),
                category=category
            )
            ingredients = self.ingredient_service.search(search_dto)
            self.ingredient_search_completed.emit(ingredients)
            return ingredients
        except Exception as e:
            DebugLogger.log(f"Failed to search ingredients: {e}", "error")
            return []
    
    def get_ingredient_names(self) -> list[str]:
        """
        Get all distinct ingredient names for autocomplete.
        
        Returns:
            list[str]: List of all ingredient names
        """
        if not self.ingredient_service:
            # Initialize services if not already done
            self._initialize_services()
            if not self.ingredient_service:
                DebugLogger.log("Failed to initialize ingredient service for names", "error")
                return []
        
        try:
            return self.ingredient_service.list_distinct_names()
        except Exception as e:
            DebugLogger.log(f"Failed to get ingredient names: {e}", "error")
            return []
    
    # ── Form Management ─────────────────────────────────────────────────────────────────────────────────────
    
    def clear_form_data(self) -> None:
        """
        Clear all form data and reset to initial state.
        
        Emits form_cleared signal to notify the UI layer.
        """
        self._reset_internal_state()
        self.form_cleared.emit()
        DebugLogger.log("Form data cleared and reset signal emitted", "debug")
    
    def reset_state(self) -> None:
        """
        Reset ViewModel to initial state.
        
        Clears all internal state and emits reset signal.
        """
        self._reset_internal_state()
        self.state_reset.emit()
        DebugLogger.log("ViewModel state reset and signal emitted", "debug")
    
    def _reset_internal_state(self) -> None:
        """Reset all internal state variables including recipe-specific state."""
        super()._reset_internal_state()  # Reset base state
        self._current_form_data = None
    
    def cleanup(self) -> None:
        """Clean up resources and clear references for performance optimization."""
        try:
            # Clear form data
            self._current_form_data = None
            
            # Reset internal state
            self._reset_internal_state()
            
            DebugLogger.log("AddRecipeViewModel cleaned up successfully", "debug")
            
        except Exception as e:
            DebugLogger.log(f"Error during AddRecipeViewModel cleanup: {e}", "warning")
    
    # ── State Properties ────────────────────────────────────────────────────────────────────────────────────
    
    # Note: is_processing, has_validation_errors, validation_errors inherited from BaseViewModel
    
    @property
    def current_form_data(self) -> RecipeFormData | None:
        """Get current form data (read-only)."""
        return self._current_form_data
    
    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────────────────
    
    def validate_recipe_name(self, recipe_name: str, recipe_category: str) -> bool:
        """
        Check if a recipe with the given name and category already exists.
        
        Args:
            recipe_name: Name of the recipe to check
            recipe_category: Category of the recipe to check
            
        Returns:
            bool: True if recipe is unique, False if duplicate exists
        """
        try:
            is_unique = not self.recipe_service.recipe_repo.recipe_exists(
                name=recipe_name.strip(),
                category=recipe_category.strip()
            )
            
            # Emit validation result signal
            message = "Recipe name is available" if is_unique else f"Recipe '{recipe_name}' already exists in {recipe_category}"
            self.recipe_name_validated.emit(is_unique, message)
            
            return is_unique
        except Exception as e:
            DebugLogger.log(f"Failed to validate recipe uniqueness: {e}", "error")
            self.recipe_name_validated.emit(True, "")
            return True  # Assume unique on error to avoid blocking legitimate saves
    
    # ── Real-time Field Validation ──────────────────────────────────────────────────────────────────────────────
    
    def validate_field_real_time(self, field_name: str, value: str, additional_context: dict = None) -> bool:
        """
        Perform real-time validation on individual form fields.
        
        Args:
            field_name: Name of the field being validated
            value: Current value of the field
            additional_context: Additional context needed for validation (e.g., category for recipe name)
            
        Returns:
            bool: True if field is valid, False otherwise
        """
        additional_context = additional_context or {}
        
        try:
            if field_name == "recipe_name":
                return self._validate_recipe_name_field(value)
            elif field_name == "servings":
                return self._validate_servings_field(value)
            elif field_name == "total_time":
                return self._validate_total_time_field(value)
            elif field_name == "meal_type":
                return self._validate_meal_type_field(value)
            else:
                # Clear any existing error for unknown fields
                self.field_validation_cleared.emit(field_name)
                return True
                
        except Exception as e:
            DebugLogger.log(f"Error in real-time validation for {field_name}: {e}", "error")
            self.field_validation_error.emit(field_name, "Validation error occurred")
            return False
    
    def _validate_recipe_name_field(self, value: str) -> bool:
        """Validate recipe name field in real-time."""
        return self._validate_required_field(value, "recipe_name", "Recipe Name") and \
               self._validate_field_length(value, "recipe_name", "Recipe Name", max_length=200)
    
    def _validate_servings_field(self, value: str) -> bool:
        """Validate servings field in real-time."""
        if not self._validate_required_field(value, "servings", "Servings"):
            return False
        
        servings_value = parse_servings_range(value)
        if servings_value is None or servings_value < 1:
            self._emit_field_error("servings", "Servings must be a valid positive number")
            return False
        
        self._clear_field_error("servings")
        return True
    
    def _validate_total_time_field(self, value: str) -> bool:
        """Validate total time field in real-time."""
        if value.strip():
            time_value = safe_int_conversion(value)
            if time_value is not None and time_value < 0:
                self._emit_field_error("total_time", "Total time cannot be negative")
                return False
        
        self._clear_field_error("total_time")
        return True
    
    def _validate_meal_type_field(self, value: str) -> bool:
        """Validate meal type field in real-time."""
        return self._validate_required_field(value, "meal_type", "Meal Type")
    
    def preprocess_form_data(self, raw_form_data: dict) -> RecipeFormData:
        """
        Preprocess raw form data from UI into structured RecipeFormData.
        
        Args:
            raw_form_data: Raw dictionary data from UI form
            
        Returns:
            RecipeFormData: Structured form data container
        """
        form_data = RecipeFormData()
        
        # Map raw data to structured container
        form_data.recipe_name = str(raw_form_data.get("recipe_name", "")).strip()
        form_data.recipe_category = str(raw_form_data.get("recipe_category", "")).strip()
        form_data.meal_type = str(raw_form_data.get("meal_type", "")).strip()
        form_data.dietary_preference = str(raw_form_data.get("dietary_preference", "")).strip()
        form_data.total_time = str(raw_form_data.get("total_time", "")).strip()
        form_data.servings = str(raw_form_data.get("servings", "")).strip()
        form_data.directions = str(raw_form_data.get("directions", "")).strip()
        form_data.notes = str(raw_form_data.get("notes", "")).strip()
        form_data.reference_image_path = str(raw_form_data.get("reference_image_path", "")).strip()
        form_data.banner_image_path = str(raw_form_data.get("banner_image_path", "")).strip()
        form_data.ingredients = raw_form_data.get("ingredients", [])
        
        return form_data