"""core.helpers.ui_helpers.py

Helper functions for managing UI properties and styles.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QWidget

# ── Property Constants ──────────────────────────────────────────────────────────
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
