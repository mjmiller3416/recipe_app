# 🔸 Local Application Imports
from .ingredient_module import RecipeIngredient


class Recipe:
    """
    A lightweight wrapper for recipe data.

    Provides clean, attribute-based access to all recipe fields,
    with graceful handling of missing values.

    Args:
        data (dict): Raw recipe dictionary (from DB or API)
    """

    def __init__(self, data: dict):
        self._data = data or {}

        self.id = self._data.get("id")
        self.name = self._data.get("recipe_name")
        self.category = self._data.get("recipe_category")
        self.total_time = self._data.get("total_time")
        self.servings = self._data.get("servings")
        self.image_path = self._data.get("image_path")
        self.ingredients = [RecipeIngredient(i) for i in data.get("ingredients", [])]
        self.directions = self._data.get("directions")

    def has_image(self) -> bool:
        """Returns True if the recipe has an associated image path."""
        return bool(self.image_path)
    
    def formatted_total_time(self) -> str:
        return f"{self.total_time} min"

    def formatted_servings(self) -> str:
        """Returns the servings in a formatted string."""
        return f"{self.servings}"
    
    def to_dict(self) -> dict:
        """Returns the original dictionary."""
        return self._data
