"""app/theme_manager/config.py

Configuration module for theme management in the application.
Defines color enums, theme modes, and paths to QSS files.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum

from app.config.paths.app_paths import AppPaths

# ── Theme Configuration ──────────────────────────────────────────────────────────────────────
class Color(Enum):
    INDIGO      = "#3F51B5"
    BLUE        = "#2196F3"
    TEAL        = "#009688"
    GREEN       = "#63A002"
    YELLOW      = "#FFDE3F"
    ORANGE      = "#FF9800"
    RED         = "#F44336"
    PINK        = "#E91E63"
    PURPLE      = "#9C27B0"
    DEEP_PURPLE = "#673AB7"
    BROWN       = "#795548"
    GRAY        = "#607D8B"

class Mode(Enum):
    LIGHT = "light"
    DARK  = "dark"

class Typography(Enum):
    """Typography styles for the application using CSS font shorthand syntax."""

    # CSS font shorthand format: [font-style] [font-weight] [font-size] [font-family]
    HEADER_LARGE    = 'normal 600 52px "Roboto"'
    HEADER_SMALL    = 'normal 500 32px "Roboto"'
    SUBHEADER       = 'italic 400 24px "Roboto"'
    TITLE_SMALL     = 'normal 500 14px "Roboto"'
    BODY_LARGE      = 'normal 400 22px "Roboto"'
    BODY_MEDIUM     = 'normal 400 14px "Roboto"'
    LABEL_SMALL     = 'normal 500 12px "Roboto"'

    @classmethod
    def generate_font_variables(cls) -> dict[str, str]:
        """Generate font variable dictionary for stylesheet injection."""
        return {typography.name.lower(): typography.value for typography in cls}

class Qss(Enum):
    BASE = AppPaths.BASE_STYLE

    # component styles
    AVATAR_LOADER     = AppPaths.QSS_DIR / "avatar_loader.qss"
    CARD              = AppPaths.QSS_DIR / "card.qss"
    COMBOBOX          = AppPaths.QSS_DIR / "combobox.qss"
    DIALOG_WINDOW     = AppPaths.QSS_DIR / "dialog_window.qss"
    EMPTY_STATE       = AppPaths.QSS_DIR / "empty_state.qss"
    INGREDIENT_WIDGET = AppPaths.QSS_DIR / "ingredient_widget.qss"
    NAV_BUTTON        = AppPaths.QSS_DIR / "nav_button.qss"
    RECIPE_CARD       = AppPaths.QSS_DIR / "recipe_card.qss"
    RECIPE_DIALOG     = AppPaths.QSS_DIR / "recipe_dialog.qss"
    SEARCH_BAR        = AppPaths.QSS_DIR / "search_bar.qss"
    SIDEBAR           = AppPaths.QSS_DIR / "sidebar.qss"
    TITLE_BAR         = AppPaths.QSS_DIR / "title_bar.qss"
    UPLOAD_IMAGE      = AppPaths.QSS_DIR / "upload_image.qss"

    # view styles
    ADD_RECIPE        = AppPaths.QSS_DIR / "add_recipe.qss"
    DASHBOARD         = AppPaths.QSS_DIR / "dashboard.qss"
    MAIN_WINDOW       = AppPaths.QSS_DIR / "main_window.qss"
    MEAL_PLANNER      = AppPaths.QSS_DIR / "meal_planner.qss"
    SHOPPING_LIST     = AppPaths.QSS_DIR / "shopping_list.qss"
    VIEW_RECIPES      = AppPaths.QSS_DIR / "view_recipes.qss"

