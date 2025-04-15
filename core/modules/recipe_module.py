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
        self.name = self._data.get("recipe_name", "Unnamed")
        self.category = self._data.get("recipe_category", "Uncategorized")
        self.total_time = self._data.get("total_time", "N/A")
        self.servings = self._data.get("servings", "N/A")
        self.image_path = self._data.get("image_path")
        self.ingredients = [RecipeIngredient(i) for i in data.get("ingredients", [])]
        self.directions = self._data.get("directions", "")

    def has_image(self) -> bool:
        """Returns True if the recipe has an associated image path."""
        return bool(self.image_path)

    def formatted_time(self) -> str:
        """Returns a string-formatted cook time."""
        return f"{self.total_time} min" if isinstance(self.total_time, int) else str(self.total_time)

    def formatted_servings(self) -> str:
        """Returns a string-formatted servings count."""
        return f"{self.servings}" if isinstance(self.servings, int) else str(self.servings)

    def to_dict(self) -> dict:
        """Returns the original dictionary."""
        return self._data
