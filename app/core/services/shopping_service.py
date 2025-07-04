"""app/core/services/shopping_service.py

Service layer for shopping list operations and business logic.
Orchestrates repository operations and coordinates with meal planning.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..repos.shopping_repo import ShoppingRepo
from ..repos.planner_repo import PlannerRepo
from ..models.shopping_item import ShoppingItem
from ..models.shopping_state import ShoppingState
from ..dtos.shopping_dto import (
    ManualItemCreateDTO, ShoppingItemUpdateDTO, ShoppingItemResponseDTO,
    ShoppingListResponseDTO, ShoppingListFilterDTO, ShoppingListGenerationResultDTO,
    IngredientBreakdownDTO, IngredientBreakdownItemDTO, BulkOperationResultDTO
)


# ── Shopping Service ─────────────────────────────────────────────────────────────────────────
class ShoppingService:
    """Service for shopping list operations with business logic."""

    def __init__(self, session: Session):
        """Initialize the ShoppingService with database session and repositories."""
        self.session = session
        self.shopping_repo = ShoppingRepo(session)
        self.planner_repo = PlannerRepo(session)

    # ── Shopping List Generation ─────────────────────────────────────────────────────────────
    def generate_shopping_list(
            self,
            meal_ids: List[int]
    ) -> ShoppingListGenerationResultDTO:
        """
        Generate shopping list from meal selections.

        Args:
            meal_ids (List[int]): List of meal selection IDs.

        Returns:
            ShoppingListGenerationResultDTO: Generation result with statistics.
        """
        try:
            # Get recipe IDs from meal selections
            recipe_ids = self._extract_recipe_ids_from_meals(meal_ids)

            if not recipe_ids:
                return ShoppingListGenerationResultDTO(
                    success=False,
                    items_created=0,
                    items_updated=0,
                    total_items=0,
                    message="No recipes found in the selected meals",
                    errors=["No valid recipes found"]
                )

            return self.generate_shopping_list_from_recipes(recipe_ids)

        except SQLAlchemyError as e:
            return ShoppingListGenerationResultDTO(
                success=False,
                items_created=0,
                items_updated=0,
                total_items=0,
                message=f"Database error: {e}",
                errors=[str(e)]
            )

    def generate_shopping_list_from_recipes(self, recipe_ids: List[int]) -> ShoppingListGenerationResultDTO:
        """
        Generate shopping list from recipes with state restoration.

        Args:
            recipe_ids (List[int]): List of recipe IDs.

        Returns:
            ShoppingListGenerationResultDTO: Generation result with statistics.
        """
        try:
            # clear existing recipe-generated items
            deleted_count = self.shopping_repo.clear_shopping_items(source="recipe")

            # aggregate ingredients from recipes
            recipe_items = self.shopping_repo.aggregate_recipe_ingredients(recipe_ids)

            # Apply saved states to items
            for item in recipe_items:
                if item.state_key:
                    saved_state = self.shopping_repo.get_shopping_state(item.state_key)
                    if saved_state:
                        item.have = saved_state.checked

            # save new items
            items_created = 0
            for item in recipe_items:
                self.shopping_repo.create_shopping_item(item)
                items_created += 1

            # get total count including manual items
            total_items = len(self.shopping_repo.get_all_shopping_items())

            return ShoppingListGenerationResultDTO(
                success=True,
                items_created=items_created,
                items_updated=0,
                total_items=total_items,
                message=f"Successfully generated shopping list with {items_created} recipe items"
            )

        except SQLAlchemyError as e:
            return ShoppingListGenerationResultDTO(
                success=False,
                items_created=0,
                items_updated=0,
                total_items=0,
                message=f"Database error: {e}",
                errors=[str(e)]
            )

    def _extract_recipe_ids_from_meals(self, meal_ids: List[int]) -> List[int]:
        """
        Extract all recipe IDs from meal selections.

        Args:
            meal_ids (List[int]): List of meal selection IDs.

        Returns:
            List[int]: List of recipe IDs used in the meals.
        """
        recipe_ids = []
        for meal_id in meal_ids:
            meal = self.planner_repo.get_meal_selection_by_id(meal_id)
            if meal:
                recipe_ids.append(meal.main_recipe_id)
                if meal.side_recipe_1_id:
                    recipe_ids.append(meal.side_recipe_1_id)
                if meal.side_recipe_2_id:
                    recipe_ids.append(meal.side_recipe_2_id)
                if meal.side_recipe_3_id:
                    recipe_ids.append(meal.side_recipe_3_id)
        return recipe_ids

    # ── Shopping List Retrieval ──────────────────────────────────────────────────────────────
    def get_shopping_list(
            self,
            filters: Optional[ShoppingListFilterDTO] = None
    ) -> ShoppingListResponseDTO:
        """
        Get the current shopping list with optional filters.

        Args:
            filters (Optional[ShoppingListFilterDTO]): Filter criteria.

        Returns:
            ShoppingListResponseDTO: Complete shopping list with metadata.
        """
        try:
            # apply filters if provided
            if filters:
                items = self.shopping_repo.search_shopping_items(
                    search_term=filters.search_term,
                    source=filters.source,
                    category=filters.category,
                    have=filters.have,
                    limit=filters.limit,
                    offset=filters.offset
                )
            else:
                items = self.shopping_repo.get_all_shopping_items()

            # convert to response DTOs
            item_dtos = [self._item_to_response_dto(item) for item in items]

            # get summary statistics
            summary = self.shopping_repo.get_shopping_list_summary()

            return ShoppingListResponseDTO(
                items=item_dtos,
                total_items=summary["total_items"],
                checked_items=summary["checked_items"],
                recipe_items=summary["recipe_items"],
                manual_items=summary["manual_items"],
                categories=summary["categories"]
            )

        except SQLAlchemyError:
            return ShoppingListResponseDTO(
                items=[],
                total_items=0,
                checked_items=0,
                recipe_items=0,
                manual_items=0,
                categories=[]
            )

    # ── Manual Item Management ───────────────────────────────────────────────────────────────
    def add_manual_item(
            self,
            create_dto: ManualItemCreateDTO
    ) -> Optional[ShoppingItemResponseDTO]:
        """
        Add a manual item to the shopping list.

        Args:
            create_dto (ManualItemCreateDTO): Manual item data.

        Returns:
            Optional[ShoppingItemResponseDTO]: Created item or None if failed.
        """
        try:
            manual_item = ShoppingItem.create_manual(
                ingredient_name=create_dto.ingredient_name,
                quantity=create_dto.quantity,
                unit=create_dto.unit
            )

            created_item = self.shopping_repo.create_shopping_item(manual_item)
            return self._item_to_response_dto(created_item)

        except SQLAlchemyError:
            return None

    def update_shopping_item(
            self,
            item_id: int,
            update_dto: ShoppingItemUpdateDTO
    ) -> Optional[ShoppingItemResponseDTO]:
        """
        Update a shopping item.

        Args:
            item_id (int): ID of the item to update.
            update_dto (ShoppingItemUpdateDTO): Update data.

        Returns:
            Optional[ShoppingItemResponseDTO]: Updated item or None if failed.
        """
        try:
            item = self.shopping_repo.get_shopping_item_by_id(item_id)
            if not item:
                return None

            # update fields from DTO
            if update_dto.ingredient_name is not None:
                item.ingredient_name = update_dto.ingredient_name
            if update_dto.quantity is not None:
                item.quantity = update_dto.quantity
            if update_dto.unit is not None:
                item.unit = update_dto.unit
            if update_dto.category is not None:
                item.category = update_dto.category
            if update_dto.have is not None:
                item.have = update_dto.have
                # update state if this is a recipe item
                if item.state_key and item.source == "recipe":
                    self.shopping_repo.save_shopping_state(
                        item.state_key, item.quantity, item.unit or "", item.have
                    )

            updated_item = self.shopping_repo.update_shopping_item(item)
            return self._item_to_response_dto(updated_item)

        except SQLAlchemyError:
            return None

    def delete_shopping_item(self, item_id: int) -> bool:
        """
        Delete a shopping item.

        Args:
            item_id (int): ID of the item to delete.

        Returns:
            bool: True if deleted successfully.
        """
        try:
            return self.shopping_repo.delete_shopping_item(item_id)
        except SQLAlchemyError:
            return False

    def clear_manual_items(self) -> BulkOperationResultDTO:
        """
        Clear all manual items from the shopping list.

        Returns:
            BulkOperationResultDTO: Operation result.
        """
        try:
            deleted_count = self.shopping_repo.clear_shopping_items(source="manual")

            return BulkOperationResultDTO(
                success=True,
                items_affected=deleted_count,
                message=f"Cleared {deleted_count} manual items"
            )

        except SQLAlchemyError as e:
            return BulkOperationResultDTO(
                success=False,
                items_affected=0,
                message="Failed to clear manual items",
                errors=[str(e)]
            )

    # ── Item Status Management ───────────────────────────────────────────────────────────────
    def toggle_item_status(self, item_id: int) -> Optional[bool]:
        """
        Toggle the 'have' status of a shopping item.

        Args:
            item_id (int): ID of the item to toggle.

        Returns:
            Optional[bool]: New have status or None if failed.
        """
        try:
            item = self.shopping_repo.get_shopping_item_by_id(item_id)
            if not item:
                return None

            item.have = not item.have

            # update state for recipe items
            if item.state_key and item.source == "recipe":
                self.shopping_repo.save_shopping_state(
                    item.state_key, item.quantity, item.unit or "", item.have
                )

            self.shopping_repo.update_shopping_item(item)
            return item.have

        except SQLAlchemyError:
            return None

    def bulk_update_status(self, updates: List[tuple[int, bool]]) -> BulkOperationResultDTO:
        """
        Bulk update have status for multiple items.

        Args:
            updates (List[tuple[int, bool]]): List of (item_id, have_status) tuples.

        Returns:
            BulkOperationResultDTO: Operation result.
        """
        try:
            updated_count = self.shopping_repo.bulk_update_have_status(updates)

            return BulkOperationResultDTO(
                success=True,
                items_affected=updated_count,
                message=f"Updated {updated_count} items"
            )

        except SQLAlchemyError as e:
            return BulkOperationResultDTO(
                success=False,
                items_affected=0,
                message="Failed to bulk update items",
                errors=[str(e)]
            )

    # ── Analysis and Breakdown ───────────────────────────────────────────────────────────────
    def get_ingredient_breakdown(self, recipe_ids: List[int]) -> List[IngredientBreakdownDTO]:
        """
        Get detailed breakdown of ingredients by recipe.

        Args:
            recipe_ids (List[int]): List of recipe IDs.

        Returns:
            List[IngredientBreakdownDTO]: Ingredient breakdown data.
        """
        try:
            breakdown = self.shopping_repo.get_ingredient_breakdown(recipe_ids)

            result = []
            for key, contributions in breakdown.items():
                # parse the key to get ingredient name and unit
                parts = key.split("::")
                ingredient_name = parts[0] if parts else "Unknown"
                unit = parts[1] if len(parts) > 1 else ""

                # calculate total quantity
                total_quantity = sum(qty for _, qty, _ in contributions)

                # create contribution DTOs
                contribution_dtos = [
                    IngredientBreakdownItemDTO(
                        recipe_name=recipe_name,
                        quantity=qty,
                        unit=unit
                    )
                    for recipe_name, qty, unit in contributions
                ]

                result.append(IngredientBreakdownDTO(
                    ingredient_name=ingredient_name,
                    unit=unit,
                    total_quantity=total_quantity,
                    recipe_contributions=contribution_dtos
                ))

            return result

        except SQLAlchemyError:
            return []

    # ── Helper Methods ───────────────────────────────────────────────────────────────────────
    def _item_to_response_dto(self, item: ShoppingItem) -> ShoppingItemResponseDTO:
        """Convert a ShoppingItem model to a response DTO."""
        return ShoppingItemResponseDTO(
            id=item.id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            source=item.source,
            have=item.have,
            state_key=item.state_key
        )

    # ── Shopping List Management ─────────────────────────────────────────────────────────────
    def clear_shopping_list(self) -> BulkOperationResultDTO:
        """
        Clear the entire shopping list.

        Returns:
            BulkOperationResultDTO: Operation result.
        """
        try:
            deleted_count = self.shopping_repo.clear_shopping_items()

            return BulkOperationResultDTO(
                success=True,
                items_affected=deleted_count,
                message=f"Cleared {deleted_count} items from shopping list"
            )

        except SQLAlchemyError as e:
            return BulkOperationResultDTO(
                success=False,
                items_affected=0,
                message="Failed to clear shopping list",
                errors=[str(e)]
            )

    def get_shopping_list_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the shopping list.

        Returns:
            Dict[str, Any]: Summary with counts and completion percentage.
        """
        try:
            return self.shopping_repo.get_shopping_list_summary()
        except SQLAlchemyError:
            return {
                "total_items": 0,
                "checked_items": 0,
                "recipe_items": 0,
                "manual_items": 0,
                "categories": [],
                "completion_percentage": 0
            }
