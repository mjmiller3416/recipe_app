# app/core/dtos/__init__.py

from .recipe_dtos import (
    RecipeIngredientDTO,
    RecipeBaseDTO,
    RecipeCreateDTO,
    RecipeUpdateDTO,
    RecipeResponseDTO,
    RecipeFilterDTO
)

from .ingredient_dtos import (
    IngredientBaseDTO,
    IngredientCreateDTO,
    IngredientUpdateDTO,
    IngredientResponseDTO,
    IngredientSearchDTO,
    IngredientDetailDTO
)

from .planner_dtos import (
    MealSelectionBaseDTO,
    MealSelectionCreateDTO,
    MealSelectionUpdateDTO,
    MealSelectionResponseDTO,
    MealSelectionFilterDTO,
    MealPlanSummaryDTO,
    MealPlanValidationDTO,
    MealPlanSaveResultDTO
)

from .shopping_dto import (
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
    BulkOperationResultDTO
)

__all__ = [
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
]