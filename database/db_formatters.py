# Description: Functions for formatting and validating data for saving to the database.

#🔸Local Imports
from core.helpers.debug_logger import DebugLogger


def format_directions(raw_text: str) -> str:
    """
    Formats the directions by ensuring each step is separated by a newline.

    Args:
        raw_text (str): The raw input text from the user.

    Returns:
        str: A cleaned, newline-separated directions string.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(lines)

#🔹FORMAT DATA
def format_recipe_data(le_recipe_name, cb_recipe_category, le_total_time, le_servings, te_directions, image_path=None):
    """
    Formats ingredient data for saving.

    Args:
        le_recipe_name (QLineEdit): Input field for recipe name.
        cb_recipe_category (QComboBox): Input field for recipe category.
        le_total_time (QLineEdit): Input field for total time.
        le_servings (QComboBox): Input field for servings.

    Returns:
        dict: Formatted ingredient data.
    """
    return {
        "recipe_name": le_recipe_name.text().strip(),
        "recipe_category": cb_recipe_category.currentText().strip(),
        "total_time": int(le_total_time.text().strip()),
        "servings": int(le_servings.text().strip()),
        "directions": format_directions(te_directions.toPlainText()),
        "image_path": image_path if image_path else "",
    }

def format_ingredient_data(le_quantity, cb_unit, le_ingredient_name, cb_ingredient_category):
    """
    Formats ingredient data for saving.

    Args:
        le_quantity (QLineEdit): Input field for ingredient quantity.
        cb_unit (QComboBox): Input field for ingredient unit.
        le_ingredient_name (QLineEdit): Input field for the ingredient name.
        cb_ingredient_category (QComboBox): Dropdown for selecting the ingredient category.

    Returns:
        dict: Formatted ingredient data.
    """
    return {
        "quantity": float(le_quantity.text().strip()),
        "unit": cb_unit.currentText().strip(),
        "ingredient_name": le_ingredient_name.text().strip(),
        "ingredient_category": cb_ingredient_category.currentText().strip(),
    }

#🔸END
