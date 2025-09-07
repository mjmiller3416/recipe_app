"""Core Events Package

Domain event system for notifying components about business logic changes.
This package contains event managers and utilities for decoupling components
while maintaining proper architectural boundaries.

Available Events:
- RecipeEvents: Recipe lifecycle events (create, update, delete)
"""

from .recipe_events import (
    RecipeEventManager,
    get_recipe_event_manager,
    notify_recipe_created,
    notify_recipe_updated,
    notify_recipe_deleted,
    notify_recipes_batch_updated,
    notify_meal_plan_updated,
)

__all__ = [
    "RecipeEventManager",
    "get_recipe_event_manager",
    "notify_recipe_created",
    "notify_recipe_updated", 
    "notify_recipe_deleted",
    "notify_recipes_batch_updated",
    "notify_meal_plan_updated",
]