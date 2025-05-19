"""service/ingredient_service.py

Service class for managing ingredients.
Provides methods to retrieve, create, and validate ingredients.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from database.models.ingredient import Ingredient

# ── Class Definition ────────────────────────────────────────────────────────────
class IngredientService:
    """
    Service class for managing ingredients.
    Provides methods to retrieve, create, and validate ingredients.
    """

    @staticmethod
    def list_all_ingredient_names() -> list[str]:
        """Returns a list of all distinct ingredient names."""
        return [i.ingredient_name for i in Ingredient.all()]

    @staticmethod
    def find_matching_ingredients(query: str) -> list[Ingredient]:
        """Returns a list of Ingredient objects matching the query."""
        return [
            i for i in Ingredient.all()
            if query.lower() in i.ingredient_name.lower()
        ]

    @staticmethod
    def get_or_create_ingredient(name: str, category: str) -> Ingredient:
        """Returns an existing ingredient or creates a new one."""
        match = Ingredient.exists(ingredient_name=name, ingredient_category=category)
        if match:
            return Ingredient.get_by_field(ingredient_name=name, ingredient_category=category)
        return Ingredient(ingredient_name=name, ingredient_category=category).save()
    
    @staticmethod
    def build_payload_from_widget(widget) -> dict:
        """
        Extracts and formats data from an IngredientWidget instance
        into a payload compatible with create_recipe_with_ingredients().
        """
        return {
            "ingredient_name": widget.le_ingredient_name.text().strip(),
            "category": widget.cb_ingredient_category.currentText().strip(),
            "unit": widget.cb_unit.currentText().strip(),
            "quantity": float(widget.le_quantity.text().strip() or 0)
        }
