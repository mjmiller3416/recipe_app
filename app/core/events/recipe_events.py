"""Recipe Event System

Global event system for notifying views when recipe data changes.
This allows cached views to stay synchronized with database changes.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional

from app.core.models.recipe import Recipe


class RecipeEventManager(QObject):
    """Global event manager for recipe-related changes."""
    
    # Signals for recipe lifecycle events
    recipe_created = Signal(object)      # Recipe object
    recipe_updated = Signal(object)      # Recipe object  
    recipe_deleted = Signal(int)         # Recipe ID
    recipes_batch_updated = Signal()     # Multiple recipes changed
    
    # Signals for meal plan changes
    meal_plan_updated = Signal(list)     # List of recipe IDs in active meal plan
    
    _instance: Optional['RecipeEventManager'] = None
    
    def __init__(self):
        super().__init__()
    
    @classmethod
    def get_instance(cls) -> 'RecipeEventManager':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def emit_recipe_created(self, recipe: Recipe):
        """Emit signal when a new recipe is created."""
        self.recipe_created.emit(recipe)
    
    def emit_recipe_updated(self, recipe: Recipe):
        """Emit signal when a recipe is updated."""
        self.recipe_updated.emit(recipe)
    
    def emit_recipe_deleted(self, recipe_id: int):
        """Emit signal when a recipe is deleted."""
        self.recipe_deleted.emit(recipe_id)
    
    def emit_recipes_batch_updated(self):
        """Emit signal when multiple recipes are updated (e.g., bulk import)."""
        self.recipes_batch_updated.emit()
    
    def emit_meal_plan_updated(self, recipe_ids: list):
        """Emit signal when the meal plan is updated."""
        self.meal_plan_updated.emit(recipe_ids)


# Global convenience functions
def get_recipe_event_manager() -> RecipeEventManager:
    """Get the global recipe event manager instance."""
    return RecipeEventManager.get_instance()

def notify_recipe_created(recipe: Recipe):
    """Notify all listeners that a recipe was created."""
    get_recipe_event_manager().emit_recipe_created(recipe)

def notify_recipe_updated(recipe: Recipe):
    """Notify all listeners that a recipe was updated."""
    get_recipe_event_manager().emit_recipe_updated(recipe)

def notify_recipe_deleted(recipe_id: int):
    """Notify all listeners that a recipe was deleted."""
    get_recipe_event_manager().emit_recipe_deleted(recipe_id)

def notify_recipes_batch_updated():
    """Notify all listeners that multiple recipes were updated."""
    get_recipe_event_manager().emit_recipes_batch_updated()

def notify_meal_plan_updated(recipe_ids: list):
    """Notify all listeners that the meal plan was updated."""
    get_recipe_event_manager().emit_meal_plan_updated(recipe_ids)