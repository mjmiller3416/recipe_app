class Ingredient:
    """
    Represents a globally defined ingredient (independent of any recipe).

    Args:
        data (dict): Raw ingredient record from the 'ingredients' table.
    """

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["ingredient_name"]
        self.category = data["ingredient_category"]

    def __str__(self):
        return self.name


class RecipeIngredient:
    """
    Represents a specific use of an ingredient in a recipe,
    including quantity and unit overrides.

    This model is built from a JOIN of the 'recipe_ingredients' and 'ingredients' tables.

    Args:
        data (dict): Joined row from recipe_ingredients + ingredients
    """

    def __init__(self, data: dict):
        self.recipe_id = data.get("recipe_id")
        self.ingredient_id = data.get("ingredient_id")
        self.quantity = data.get("quantity", "")
        self.unit = data.get("unit", "")
        self.name = data.get("ingredient_name")  # Comes from join

    def __str__(self):
        qty = str(self.quantity) if self.quantity else ""
        unit = self.unit if self.unit else ""
        return f"{qty} {unit} - {self.name}".strip(" -")
