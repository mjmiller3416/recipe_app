"""style_manager/utils/theme_utils.py

Utility functions for handling theme properties in a Qt application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QWidget

# ── Constants ──────────────────────────────────────────────────────────
PROPS = {
    # ── Labels ──
    "LABEL_HEADER": ("textHeader", True),
    "LABEL_META": ("metaTitle", True),
    "LABEL_INGREDIENT": ("textIngredients", True),
    "LABEL_DIRECTIONS": ("textDirections", True),

    # ── Recipe Card States ──
    "RECIPE_TITLE": ("title_text", True),
    "RECIPE_LABEL": ("label_text", True),
    "RECIPE_VALUE": ("value_text", True),
}

DO_NOT_FLATTEN_KEYS = {"ICON_STYLES"}  # these will be preserved as-is

# ── Function Definitions ────────────────────────────────────────────────────────
def apply_prop(widget: QWidget, key: str):
    """
    Apply a named Qt property to a widget based on the centralized PROPS map.

    Args:
        widget (QWidget): The widget to assign the property to.
        key (str): The key in the PROPS dictionary (e.g. 'LABEL_HEADER')
    """
    prop = PROPS.get(key)
    if prop:
        widget.setProperty(*prop)

def flatten_theme_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    """
    Recursively flattens a nested theme dictionary, skipping defined complex keys.

    Args:
        d (dict): The nested theme dictionary.
        parent_key (str, optional): Key prefix for recursion.
        sep (str, optional): Separator between nested keys.

    Returns:
        dict: Flattened dictionary with compound keys, excluding complex blocks like ICON_STYLES.
    """
    items = []

    for k, v in d.items():
        if k in DO_NOT_FLATTEN_KEYS:
            # Leave these untouched (e.g. ICON_STYLES stays a dict)
            items.append((k, v))
            continue

        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_theme_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key.upper(), v))

    return dict(items)
