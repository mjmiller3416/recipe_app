""""config/paths/qss_paths.py

Centralized mapping of QSS stylesheet file paths.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from config.paths.app_paths import AppPaths


# ── Class Definition ────────────────────────────────────────────────────────────
class QssPaths:
    """
    Centralized mapping of QSS stylesheet file paths.
    Used by ThemeController and ThemedStyleLoader for structured styling.
    """

    # ── Constants ───────────────────────────────────────────────────────────────────
    BASE = AppPaths.qss_path("base.qss")
    APPLICATION = AppPaths.qss_path("application.qss")

    # ── Styles Sheets ───────────────────────────────────────────────────────────────
    class Views:
        ADD_RECIPES = AppPaths.qss_path("add_recipes.qss")
        DASHBOARD = AppPaths.qss_path("dashboard.qss")
        VIEW_RECIPES = AppPaths.qss_path("view_recipes.qss")
        MEAL_PLANNER = AppPaths.qss_path("meal_planner.qss")
        SHOPPING_LIST = AppPaths.qss_path("shopping_list.qss")

    class Components:
        DIALOG = AppPaths.qss_path("dialog_widget.qss")
        RECIPE_WIDGET = AppPaths.qss_path("recipe_widget.qss")
