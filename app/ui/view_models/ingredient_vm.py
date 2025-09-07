"""app/ui/view_models/ingredient_vm.py

IngredientViewModel for MVVM architecture compliance.
Handles all ingredient business logic including search, validation, matching, and data transformation.
Specialized ViewModel that coordinates with AddRecipeViewModel for ingredient operations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Signal

from _dev_tools import DebugLogger
from app.config.config import INGREDIENT_CATEGORIES
from app.core.dtos.ingredient_dtos import IngredientCreateDTO, IngredientSearchDTO
from app.core.services.ingredient_service import IngredientService
from app.core.utils.conversion_utils import safe_float_conversion
from app.core.utils.text_utils import sanitize_form_input
from app.ui.view_models.base_view_model import BaseValidationResult, BaseViewModel

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.core.models.ingredient import Ingredient


# ── Validation Pattern ─────────────────────────────────────────────────────────────────────────────────────────
# Matches the existing NAME_PATTERN from the UI layer
NAME_PATTERN = re.compile(r"^[a-zA-Z\s\-'.,&()]+$")


# ── Ingredient Form Data Container ─────────────────────────────────────────────────────────────────────────────
class IngredientFormData:
    """Container for raw ingredient form data before validation and transformation."""

    def __init__(self):
        self.ingredient_name: str = ""
        self.ingredient_category: str = ""
        self.quantity: str = ""
        self.unit: str = ""
        self.existing_ingredient_id: Optional[int] = None


# ── Ingredient Match Result ────────────────────────────────────────────────────────────────────────────────────
class IngredientMatchResult:
    """Contains the result of ingredient matching operations."""

    def __init__(self,
                 exact_match: Optional[Ingredient] = None,
                 partial_matches: list[Ingredient] = None,
                 suggested_category: Optional[str] = None,
                 is_valid_name: bool = True):
        self.exact_match = exact_match
        self.partial_matches = partial_matches or []
        self.suggested_category = suggested_category
        self.is_valid_name = is_valid_name


# ── Ingredient Validation Result ───────────────────────────────────────────────────────────────────────────────
class IngredientValidationResult:
    """Container for ingredient validation results with errors and success status."""

    def __init__(self, is_valid: bool = True, errors: list[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings: list[str] = []

    def add_error(self, error: str) -> None:
        """Add an error message to the validation result."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message to the validation result."""
        self.warnings.append(warning)


# ── Ingredient ViewModel ───────────────────────────────────────────────────────────────────────────────────────
class IngredientViewModel(BaseViewModel):
    """
    ViewModel for ingredient operations implementing proper MVVM architecture.

    Handles ingredient search, validation, matching algorithms, category auto-population,
    and data transformation. Works in coordination with AddRecipeViewModel for complete
    recipe creation functionality.
    """

    # Signals for UI communication
    ingredient_search_completed = Signal(list)  # list[Ingredient] - search results
    ingredient_matched = Signal(object)  # IngredientMatchResult - matching results
    ingredient_validated = Signal(object)  # IngredientValidationResult - validation results
    category_suggested = Signal(str)  # str - suggested category for ingredient
    autocomplete_data_ready = Signal(list)  # list[str] - autocomplete suggestions
    ingredient_categories_loaded = Signal(list)  # list[str] - available categories

    # Enhanced data binding signals
    ingredient_name_validation_changed = Signal(bool, str)  # is_valid, error_message
    ingredient_category_validation_changed = Signal(bool, str)  # is_valid, error_message
    ingredient_quantity_validation_changed = Signal(bool, str)  # is_valid, error_message
    collection_validation_completed = Signal(object)  # IngredientValidationResult
    ingredient_processing_state_changed = Signal(bool)  # is_processing

    def __init__(self, session: Session | None = None):
        """
        Initialize the IngredientViewModel with Core service dependencies.

        Args:
            session: Optional SQLAlchemy session for dependency injection.
                    If None, services will create their own sessions.
        """
        super().__init__(session)

        # Initialize Core service with proper session management
        self._initialize_service()

        # Enhanced caching for performance with lazy loading
        self._autocomplete_cache: list[str] = []
        self._categories_cache: list[str] = []
        self._ingredients_cache: list[Ingredient] = []
        self._cache_loaded = False
        self._categories_cache_loaded = False

        # Performance optimization: cache frequently accessed data
        self._search_result_cache: dict[str, list[Ingredient]] = {}
        self._match_result_cache: dict[str, IngredientMatchResult] = {}
        self._cache_max_size = 100  # Limit cache size to prevent memory bloat

        DebugLogger.log("IngredientViewModel initialized with enhanced caching", "debug")

    def __del__(self):
        """Ensure proper resource cleanup on ViewModel destruction."""
        try:
            self._clear_all_caches()
            DebugLogger.log("IngredientViewModel caches cleared during cleanup", "debug")
        except Exception as e:
            DebugLogger.log(f"Error during IngredientViewModel cleanup: {e}", "warning")
        super().__del__()

    def _initialize_service(self) -> None:
        """Initialize Core service with proper session management."""
        if not self._ensure_session():
            DebugLogger.log("Failed to ensure session in IngredientViewModel", "error")
            return

        try:
            self.ingredient_service = IngredientService(self._session)
            DebugLogger.log("IngredientViewModel service initialized", "debug")
        except Exception as e:
            DebugLogger.log(f"Failed to initialize service in IngredientViewModel: {e}", "error")
            self.ingredient_service = None

    # ── Core Ingredient Operations ──────────────────────────────────────────────────────────────────────────────

    def search_ingredients(self, search_term: str, category: Optional[str] = None) -> list[Ingredient]:
        """
        Search for ingredients using the IngredientService with caching optimization.

        Args:
            search_term: Term to search for in ingredient names
            category: Optional category filter

        Returns:
            list[Ingredient]: List of matching ingredients
        """
        if not self._ensure_service():
            return []

        if not search_term.strip():
            return []

        # Performance optimization: check cache first
        cache_key = f"{search_term.strip().lower()}:{category or ''}"
        if cache_key in self._search_result_cache:
            cached_results = self._search_result_cache[cache_key]
            self.ingredient_search_completed.emit(cached_results)
            DebugLogger.log(f"Ingredient search cache hit for '{search_term}'", "debug")
            return cached_results

        try:
            search_dto = IngredientSearchDTO(
                search_term=search_term.strip(),
                category=category
            )
            ingredients = self.ingredient_service.search(search_dto)

            # Cache the results with size management
            self._cache_search_results(cache_key, ingredients)

            self.ingredient_search_completed.emit(ingredients)

            DebugLogger.log(f"Ingredient search for '{search_term}' returned {len(ingredients)} results", "debug")
            return ingredients

        except Exception as e:
            DebugLogger.log(f"Failed to search ingredients: {e}", "error")
            self.ingredient_search_completed.emit([])
            return []

    def find_ingredient_matches(self, ingredient_name: str) -> IngredientMatchResult:
        """
        Find exact and partial matches for an ingredient name with caching optimization.

        Implements sophisticated matching algorithms including exact match detection,
        partial matching for autocomplete, and category suggestion logic.

        Args:
            ingredient_name: Name to search for matches

        Returns:
            IngredientMatchResult: Container with match results and suggestions
        """
        if not self._ensure_service():
            return IngredientMatchResult(is_valid_name=False)

        ingredient_name = ingredient_name.strip()

        # Validate ingredient name format
        is_valid_name = bool(NAME_PATTERN.match(ingredient_name)) if ingredient_name else False

        if not ingredient_name or not is_valid_name:
            result = IngredientMatchResult(is_valid_name=is_valid_name)
            self.ingredient_matched.emit(result)
            return result

        # Performance optimization: check cache first
        cache_key = ingredient_name.lower()
        if cache_key in self._match_result_cache:
            cached_result = self._match_result_cache[cache_key]
            self.ingredient_matched.emit(cached_result)
            if cached_result.suggested_category:
                self.category_suggested.emit(cached_result.suggested_category)
            DebugLogger.log(f"Ingredient match cache hit for '{ingredient_name}'", "debug")
            return cached_result

        try:
            # Search for potential matches
            search_results = self.search_ingredients(ingredient_name)

            # Find exact match (case-insensitive)
            exact_match = None
            partial_matches = []

            for ingredient in search_results:
                if ingredient.ingredient_name.lower() == ingredient_name.lower():
                    exact_match = ingredient
                else:
                    partial_matches.append(ingredient)

            # Suggest category based on exact match or most common category in partial matches
            suggested_category = None
            if exact_match:
                suggested_category = exact_match.ingredient_category
            elif partial_matches:
                # Find most common category among partial matches
                categories = [ing.ingredient_category for ing in partial_matches]
                if categories:
                    suggested_category = max(set(categories), key=categories.count)

            result = IngredientMatchResult(
                exact_match=exact_match,
                partial_matches=partial_matches,
                suggested_category=suggested_category,
                is_valid_name=is_valid_name
            )

            # Cache the result with size management
            self._cache_match_result(cache_key, result)

            self.ingredient_matched.emit(result)

            if suggested_category:
                self.category_suggested.emit(suggested_category)

            DebugLogger.log(f"Ingredient matching for '{ingredient_name}': "
                          f"exact={exact_match is not None}, "
                          f"partial={len(partial_matches)}, "
                          f"category={suggested_category}", "debug")

            return result

        except Exception as e:
            DebugLogger.log(f"Failed to find ingredient matches for '{ingredient_name}': {e}", "error")
            result = IngredientMatchResult(is_valid_name=is_valid_name)
            self.ingredient_matched.emit(result)
            return result

    def validate_ingredient_data(self, ingredient_data: IngredientFormData) -> IngredientValidationResult:
        """
        Validate ingredient form data comprehensively.

        Validates required fields, data types, business rules, and consistency.

        Args:
            ingredient_data: Raw ingredient form data to validate

        Returns:
            IngredientValidationResult: Contains validation status, errors, and warnings
        """
        result = IngredientValidationResult()

        # Required field validation
        if not ingredient_data.ingredient_name.strip():
            result.add_error("Ingredient name is required")

        if not ingredient_data.ingredient_category.strip():
            result.add_error("Ingredient category is required")

        # Name format validation
        if ingredient_data.ingredient_name.strip():
            if not NAME_PATTERN.match(ingredient_data.ingredient_name.strip()):
                result.add_error("Ingredient name contains invalid characters")

            if len(ingredient_data.ingredient_name.strip()) > 100:
                result.add_error("Ingredient name cannot exceed 100 characters")

        # Category validation
        if ingredient_data.ingredient_category.strip():
            if ingredient_data.ingredient_category not in INGREDIENT_CATEGORIES:
                result.add_warning(f"Category '{ingredient_data.ingredient_category}' is not in the standard list")

        # Quantity validation
        if ingredient_data.quantity.strip():
            quantity = safe_float_conversion(ingredient_data.quantity.strip())
            if quantity is None:
                result.add_error("Quantity must be a valid number")
            elif quantity <= 0:
                result.add_error("Quantity must be greater than zero")
            elif quantity > 10000:
                result.add_warning("Quantity seems unusually large")

        # Unit validation
        if ingredient_data.unit.strip() and len(ingredient_data.unit.strip()) > 50:
            result.add_error("Unit cannot exceed 50 characters")

        self.ingredient_validated.emit(result)

        DebugLogger.log(f"Ingredient validation: valid={result.is_valid}, "
                       f"errors={len(result.errors)}, warnings={len(result.warnings)}", "debug")

        return result

    # ── Real-time Field Validation ──────────────────────────────────────────────────────────────────────────────

    def validate_ingredient_name_real_time(self, name: str) -> bool:
        """
        Perform real-time validation on ingredient name field.

        Args:
            name: Current ingredient name value

        Returns:
            bool: True if valid, False otherwise
        """
        if not name.strip():
            self.ingredient_name_validation_changed.emit(False, "Ingredient name is required")
            return False

        if not NAME_PATTERN.match(name.strip()):
            self.ingredient_name_validation_changed.emit(False, "Ingredient name contains invalid characters")
            return False

        if len(name.strip()) > 100:
            self.ingredient_name_validation_changed.emit(False, "Ingredient name cannot exceed 100 characters")
            return False

        self.ingredient_name_validation_changed.emit(True, "")
        return True

    def validate_ingredient_category_real_time(self, category: str) -> bool:
        """
        Perform real-time validation on ingredient category field.

        Args:
            category: Current category value

        Returns:
            bool: True if valid, False otherwise
        """
        if not category.strip():
            self.ingredient_category_validation_changed.emit(False, "Category is required")
            return False

        self.ingredient_category_validation_changed.emit(True, "")
        return True

    def validate_ingredient_quantity_real_time(self, quantity: str) -> bool:
        """
        Perform real-time validation on quantity field.

        Args:
            quantity: Current quantity value

        Returns:
            bool: True if valid, False otherwise
        """
        if not quantity.strip():
            # Quantity is optional, so empty is valid
            self.ingredient_quantity_validation_changed.emit(True, "")
            return True

        quantity_value = safe_float_conversion(quantity.strip())
        if quantity_value is None:
            self.ingredient_quantity_validation_changed.emit(False, "Quantity must be a valid number")
            return False

        if quantity_value <= 0:
            self.ingredient_quantity_validation_changed.emit(False, "Quantity must be greater than zero")
            return False

        if quantity_value > 10000:
            # This is a warning, not an error, so still valid
            self.ingredient_quantity_validation_changed.emit(True, "Quantity seems unusually large")
            return True

        self.ingredient_quantity_validation_changed.emit(True, "")
        return True

    # ── Data Transformation ─────────────────────────────────────────────────────────────────────────────────────

    def transform_to_ingredient_dto(self, ingredient_data: IngredientFormData) -> dict:
        """
        Transform validated ingredient form data to dictionary for RecipeIngredientDTO.

        Handles data sanitization and transformation to match the expected DTO structure
        used by the AddRecipeViewModel.

        Args:
            ingredient_data: Validated ingredient form data

        Returns:
            dict: Dictionary matching RecipeIngredientDTO structure
        """
        try:
            dto_data = {
                "ingredient_name": sanitize_form_input(ingredient_data.ingredient_name),
                "ingredient_category": sanitize_form_input(ingredient_data.ingredient_category),
                "quantity": safe_float_conversion(ingredient_data.quantity) if ingredient_data.quantity.strip() else None,
                "unit": sanitize_form_input(ingredient_data.unit) if ingredient_data.unit.strip() else None,
                "existing_ingredient_id": ingredient_data.existing_ingredient_id
            }

            DebugLogger.log(f"Transformed ingredient data: {dto_data['ingredient_name']}", "debug")
            return dto_data

        except Exception as e:
            DebugLogger.log(f"Failed to transform ingredient data: {e}", "error")
            return {}

    def parse_form_data(self, raw_data: dict) -> IngredientFormData:
        """
        Parse raw form data from UI into structured IngredientFormData.

        Args:
            raw_data: Raw dictionary data from UI form

        Returns:
            IngredientFormData: Structured ingredient form data container
        """
        form_data = IngredientFormData()

        form_data.ingredient_name = str(raw_data.get("ingredient_name", "")).strip()
        form_data.ingredient_category = str(raw_data.get("ingredient_category", "")).strip()
        form_data.quantity = str(raw_data.get("quantity", "")).strip()
        form_data.unit = str(raw_data.get("unit", "")).strip()
        form_data.existing_ingredient_id = raw_data.get("existing_ingredient_id")

        return form_data

    # ── Autocomplete and Category Management ────────────────────────────────────────────────────────────────────

    def get_autocomplete_suggestions(self, partial_name: str, limit: int = 10) -> list[str]:
        """
        Get autocomplete suggestions for ingredient names with optimized caching.

        Args:
            partial_name: Partial ingredient name to match
            limit: Maximum number of suggestions to return

        Returns:
            list[str]: List of suggested ingredient names
        """
        if not self._ensure_service():
            return []

        if not partial_name.strip():
            return []

        try:
            # Performance optimization: lazy load cache only when needed
            if not self._cache_loaded:
                self._load_autocomplete_cache()

            # Performance optimization: early exit if cache is empty
            if not self._autocomplete_cache:
                return []

            partial_lower = partial_name.lower().strip()

            # Performance optimization: use generator for memory efficiency
            suggestions = []
            count = 0
            for name in self._autocomplete_cache:
                if count >= limit:
                    break
                if partial_lower in name.lower():
                    suggestions.append(name)
                    count += 1

            self.autocomplete_data_ready.emit(suggestions)
            return suggestions

        except Exception as e:
            DebugLogger.log(f"Failed to get autocomplete suggestions: {e}", "error")
            return []

    def get_available_categories(self) -> list[str]:
        """
        Get all available ingredient categories with lazy loading optimization.

        Combines standard categories with any additional categories found in the database.

        Returns:
            list[str]: List of all available categories
        """
        if not self._ensure_service():
            return INGREDIENT_CATEGORIES.copy()

        try:
            # Performance optimization: lazy load categories cache only when needed
            if not self._categories_cache_loaded:
                self._load_categories_cache()

            self.ingredient_categories_loaded.emit(self._categories_cache)
            return self._categories_cache.copy()

        except Exception as e:
            DebugLogger.log(f"Failed to get ingredient categories: {e}", "error")
            return INGREDIENT_CATEGORIES.copy()

    def suggest_category_for_name(self, ingredient_name: str) -> Optional[str]:
        """
        Suggest the most appropriate category for an ingredient name.

        Uses existing database entries and partial matching to suggest categories.

        Args:
            ingredient_name: Name of the ingredient

        Returns:
            Optional[str]: Suggested category or None if no suggestion available
        """
        match_result = self.find_ingredient_matches(ingredient_name)
        return match_result.suggested_category

    # ── Ingredient Collection Management ────────────────────────────────────────────────────────────────────────

    def validate_ingredient_collection(self, ingredients_data: list[dict]) -> IngredientValidationResult:
        """
        Validate a collection of ingredient data.

        Performs validation on each ingredient and checks for collection-level issues
        like duplicates or empty collections.

        Args:
            ingredients_data: List of raw ingredient data dictionaries

        Returns:
            IngredientValidationResult: Validation result for the entire collection
        """
        result = IngredientValidationResult()

        if not ingredients_data:
            result.add_error("At least one ingredient is required")
            return result

        valid_ingredients = []
        ingredient_names = []

        for i, raw_ingredient in enumerate(ingredients_data, 1):
            ingredient_data = self.parse_form_data(raw_ingredient)

            # Skip empty ingredients
            if not ingredient_data.ingredient_name.strip():
                continue

            # Validate individual ingredient
            ingredient_validation = self.validate_ingredient_data(ingredient_data)

            if not ingredient_validation.is_valid:
                for error in ingredient_validation.errors:
                    result.add_error(f"Ingredient {i}: {error}")

            for warning in ingredient_validation.warnings:
                result.add_warning(f"Ingredient {i}: {warning}")

            if ingredient_validation.is_valid:
                valid_ingredients.append(ingredient_data)
                ingredient_names.append(ingredient_data.ingredient_name.lower())

        # Check for duplicates
        duplicate_names = set()
        seen_names = set()
        for name in ingredient_names:
            if name in seen_names:
                duplicate_names.add(name)
            seen_names.add(name)

        if duplicate_names:
            result.add_warning(f"Duplicate ingredients found: {', '.join(duplicate_names)}")

        if not valid_ingredients:
            result.add_error("No valid ingredients found")

        DebugLogger.log(f"Collection validation: {len(valid_ingredients)} valid ingredients, "
                       f"{len(result.errors)} errors, {len(result.warnings)} warnings", "debug")

        return result

    def transform_ingredient_collection(self, ingredients_data: list[dict]) -> list[dict]:
        """
        Transform a collection of raw ingredient data to DTO dictionaries.

        Args:
            ingredients_data: List of raw ingredient data dictionaries

        Returns:
            list[dict]: List of dictionaries matching RecipeIngredientDTO structure
        """
        transformed_ingredients = []

        for raw_ingredient in ingredients_data:
            ingredient_data = self.parse_form_data(raw_ingredient)

            # Skip empty ingredients
            if not ingredient_data.ingredient_name.strip():
                continue

            dto_dict = self.transform_to_ingredient_dto(ingredient_data)
            if dto_dict:
                transformed_ingredients.append(dto_dict)

        DebugLogger.log(f"Transformed {len(transformed_ingredients)} ingredients for collection", "debug")
        return transformed_ingredients

    # ── Cache Management ────────────────────────────────────────────────────────────────────────────────────────

    def _load_autocomplete_cache(self) -> None:
        """Load autocomplete data into cache for better performance."""
        try:
            if self._ensure_service():
                self._autocomplete_cache = self.ingredient_service.list_distinct_names()
                self._cache_loaded = True
                DebugLogger.log(f"Loaded {len(self._autocomplete_cache)} ingredient names into cache", "debug")
        except Exception as e:
            DebugLogger.log(f"Failed to load autocomplete cache: {e}", "error")

    def _load_categories_cache(self) -> None:
        """Load categories data into cache for better performance."""
        try:
            if self._ensure_service():
                db_categories = self.ingredient_service.get_ingredient_categories()
                all_categories = set(INGREDIENT_CATEGORIES + db_categories)
                self._categories_cache = sorted(all_categories)
                self._categories_cache_loaded = True
                DebugLogger.log(f"Loaded {len(self._categories_cache)} categories into cache", "debug")
        except Exception as e:
            DebugLogger.log(f"Failed to load categories cache: {e}", "error")
            self._categories_cache = INGREDIENT_CATEGORIES.copy()
            self._categories_cache_loaded = True

    def _cache_search_results(self, cache_key: str, results: list[Ingredient]) -> None:
        """Cache search results with size management to prevent memory bloat."""
        if len(self._search_result_cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO cache management)
            oldest_key = next(iter(self._search_result_cache))
            del self._search_result_cache[oldest_key]

        self._search_result_cache[cache_key] = results.copy()

    def _cache_match_result(self, cache_key: str, result: IngredientMatchResult) -> None:
        """Cache match results with size management to prevent memory bloat."""
        if len(self._match_result_cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO cache management)
            oldest_key = next(iter(self._match_result_cache))
            del self._match_result_cache[oldest_key]

        self._match_result_cache[cache_key] = result

    def refresh_cache(self) -> None:
        """Refresh all cached data from the database."""
        # Clear all caches
        self._clear_all_caches()

        # Preload primary caches
        self._load_autocomplete_cache()
        self._load_categories_cache()

        DebugLogger.log("Ingredient cache refreshed", "debug")

    def _clear_all_caches(self) -> None:
        """Clear all cached data for memory management."""
        self._autocomplete_cache.clear()
        self._categories_cache.clear()
        self._ingredients_cache.clear()
        self._search_result_cache.clear()
        self._match_result_cache.clear()
        self._cache_loaded = False
        self._categories_cache_loaded = False

    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────────────────────

    def _ensure_service(self) -> bool:
        """Ensure ingredient service is available, creating it if needed."""
        if not self.ingredient_service:
            # Initialize service using proper session management
            self._initialize_service()
        return self.ingredient_service is not None

    def create_or_get_ingredient(self, ingredient_name: str, category: str) -> Optional[Ingredient]:
        """
        Create a new ingredient or retrieve existing one.

        Args:
            ingredient_name: Name of the ingredient
            category: Category of the ingredient

        Returns:
            Optional[Ingredient]: Created or existing ingredient, None if failed
        """
        if not self._ensure_service():
            return None

        try:
            create_dto = IngredientCreateDTO(
                ingredient_name=ingredient_name.strip(),
                ingredient_category=category.strip()
            )
            ingredient = self.ingredient_service.get_or_create(create_dto)

            DebugLogger.log(f"Created/retrieved ingredient: {ingredient.ingredient_name}", "debug")
            return ingredient

        except Exception as e:
            DebugLogger.log(f"Failed to create/get ingredient '{ingredient_name}': {e}", "error")
            return None

    def is_valid_ingredient_name(self, name: str) -> bool:
        """
        Check if ingredient name follows the expected format.

        Args:
            name: Ingredient name to validate

        Returns:
            bool: True if name is valid format
        """
        if not name or not name.strip():
            return False
        return bool(NAME_PATTERN.match(name.strip()))

    # ── State Properties ────────────────────────────────────────────────────────────────────────────────────────

    @property
    def cache_loaded(self) -> bool:
        """Check if autocomplete cache has been loaded."""
        return self._cache_loaded

    @property
    def autocomplete_count(self) -> int:
        """Get count of cached autocomplete entries."""
        return len(self._autocomplete_cache)

    @property
    def categories_count(self) -> int:
        """Get count of available categories."""
        return len(self._categories_cache) if self._categories_cache else len(INGREDIENT_CATEGORIES)
