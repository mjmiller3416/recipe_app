# app/core/__init__.py

# Core database components
from .database import Base, SessionLocal, engine, get_session

# DTOs
from .dtos import (  # Recipe DTOs; Ingredient DTOs; Planner DTOs; Shopping DTOs
    BulkOperationResultDTO,
    BulkStateUpdateDTO,
    IngredientAggregationDTO,
    IngredientBaseDTO,
    IngredientBreakdownDTO,
    IngredientBreakdownItemDTO,
    IngredientCreateDTO,
    IngredientDetailDTO,
    IngredientResponseDTO,
    IngredientSearchDTO,
    IngredientUpdateDTO,
    ManualItemCreateDTO,
    MealPlanSaveResultDTO,
    MealPlanSummaryDTO,
    MealPlanValidationDTO,
    MealSelectionBaseDTO,
    MealSelectionCreateDTO,
    MealSelectionFilterDTO,
    MealSelectionResponseDTO,
    MealSelectionUpdateDTO,
    RecipeBaseDTO,
    RecipeCreateDTO,
    RecipeFilterDTO,
    RecipeIngredientDTO,
    RecipeResponseDTO,
    RecipeUpdateDTO,
    ShoppingItemBaseDTO,
    ShoppingItemCreateDTO,
    ShoppingItemResponseDTO,
    ShoppingItemUpdateDTO,
    ShoppingListFilterDTO,
    ShoppingListGenerationDTO,
    ShoppingListGenerationResultDTO,
    ShoppingListResponseDTO,
    ShoppingStateDTO,
)

# Models
from .models import (
    Ingredient,
    MealSelection,
    Recipe,
    RecipeHistory,
    RecipeIngredient,
    SavedMealState,
    ShoppingItem,
    ShoppingState,
)

# Repositories
from .repositories import IngredientRepo, PlannerRepo, RecipeRepo, ShoppingRepo

# Services
from .services import (
    DuplicateRecipeError,
    IngredientService,
    PlannerService,
    RecipeSaveError,
    RecipeService,
    ShoppingService,
)

# Utilities
from .utils import QSingleton, utcnow


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
    "RecipeRepo",
    "IngredientRepo",
    "PlannerRepo",
    "ShoppingRepo",

    # Services
    "RecipeService",
    "RecipeSaveError",
    "DuplicateRecipeError",
    "IngredientService",
    "PlannerService",
    "ShoppingService",

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
    "QSingleton",
    "utcnow",
]
