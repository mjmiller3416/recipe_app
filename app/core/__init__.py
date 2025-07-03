# app/core/__init__.py

# Core database components
from .database import Base, SessionLocal, engine, get_session

# Models
from .models import (
    Recipe,
    RecipeIngredient, 
    RecipeHistory,
    Ingredient,
    MealSelection,
    SavedMealState,
    ShoppingItem,
    ShoppingState,
)

# Repositories
from .repos import (
    RecipeRepository,
    IngredientRepository,
    PlannerRepository, 
    ShoppingRepository,
)

# Services
from .services import (
    RecipeService,
    RecipeSaveError,
    DuplicateRecipeError,
    IngredientService,
    PlannerService,
    ShoppingService,
    NavigationService,
)

# DTOs
from .dtos import (
    # Recipe DTOs
    RecipeIngredientDTO,
    RecipeBaseDTO,
    RecipeCreateDTO,
    RecipeUpdateDTO,
    RecipeResponseDTO,
    RecipeFilterDTO,
    
    # Ingredient DTOs
    IngredientBaseDTO,
    IngredientCreateDTO,
    IngredientUpdateDTO,
    IngredientResponseDTO,
    IngredientSearchDTO,
    IngredientDetailDTO,
    
    # Planner DTOs
    MealSelectionBaseDTO,
    MealSelectionCreateDTO,
    MealSelectionUpdateDTO,
    MealSelectionResponseDTO,
    MealSelectionFilterDTO,
    MealPlanSummaryDTO,
    MealPlanValidationDTO,
    MealPlanSaveResultDTO,
    
    # Shopping DTOs
    ShoppingItemBaseDTO,
    ShoppingItemCreateDTO,
    ManualItemCreateDTO,
    ShoppingItemUpdateDTO,
    ShoppingItemResponseDTO,
    ShoppingListResponseDTO,
    ShoppingListFilterDTO,
    ShoppingListGenerationDTO,
    ShoppingListGenerationResultDTO,
    IngredientAggregationDTO,
    IngredientBreakdownDTO,
    IngredientBreakdownItemDTO,
    ShoppingStateDTO,
    BulkStateUpdateDTO,
    BulkOperationResultDTO,
)

# Utilities
from .utils import (
    SingletonMixin,
    utcnow,
    strip_string_values,
    ensure_directory_exists,
    get_platform_info,
)

__all__ = [
    # Database
    "Base",
    "SessionLocal", 
    "engine",
    "get_session",
    
    # Models
    "Recipe",
    "RecipeIngredient",
    "RecipeHistory", 
    "Ingredient",
    "MealSelection",
    "SavedMealState",
    "ShoppingItem",
    "ShoppingState",
    
    # Repositories
    "RecipeRepository",
    "IngredientRepository",
    "PlannerRepository",
    "ShoppingRepository",
    
    # Services
    "RecipeService",
    "RecipeSaveError",
    "DuplicateRecipeError",
    "IngredientService",
    "PlannerService",
    "ShoppingService",
    "NavigationService",
    
    # Recipe DTOs
    "RecipeIngredientDTO",
    "RecipeBaseDTO",
    "RecipeCreateDTO",
    "RecipeUpdateDTO",
    "RecipeResponseDTO",
    "RecipeFilterDTO",
    
    # Ingredient DTOs
    "IngredientBaseDTO",
    "IngredientCreateDTO",
    "IngredientUpdateDTO",
    "IngredientResponseDTO",
    "IngredientSearchDTO",
    "IngredientDetailDTO",
    
    # Planner DTOs
    "MealSelectionBaseDTO",
    "MealSelectionCreateDTO",
    "MealSelectionUpdateDTO",
    "MealSelectionResponseDTO",
    "MealSelectionFilterDTO",
    "MealPlanSummaryDTO",
    "MealPlanValidationDTO",
    "MealPlanSaveResultDTO",
    
    # Shopping DTOs
    "ShoppingItemBaseDTO",
    "ShoppingItemCreateDTO",
    "ManualItemCreateDTO",
    "ShoppingItemUpdateDTO",
    "ShoppingItemResponseDTO",
    "ShoppingListResponseDTO",
    "ShoppingListFilterDTO",
    "ShoppingListGenerationDTO",
    "ShoppingListGenerationResultDTO",
    "IngredientAggregationDTO",
    "IngredientBreakdownDTO",
    "IngredientBreakdownItemDTO",
    "ShoppingStateDTO",
    "BulkStateUpdateDTO",
    "BulkOperationResultDTO",
    
    # Utilities
    "SingletonMixin",
    "utcnow",
    "strip_string_values",
    "ensure_directory_exists",
    "get_platform_info",
]