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
    BASE =        AppPaths.qss_path("base.qss")
    APPLICATION = AppPaths.qss_path("application.qss")

    # ── Styles Sheets ───────────────────────────────────────────────────────────────
    class Views:
        ADD_RECIPES   = AppPaths.qss_path("add_recipes.qss")
        DASHBOARD     = AppPaths.qss_path("dashboard.qss")
        MEAL_PLANNER  = AppPaths.qss_path("meal_planner.qss")
        SHOPPING_LIST = AppPaths.qss_path("shopping_list.qss")
        VIEW_RECIPES  = AppPaths.qss_path("view_recipes.qss")

    class Components:
        MESSAGE_DIALOG    = AppPaths.qss_path("message_dialog.qss")
        RECIPE_DIALOG     = AppPaths.qss_path("recipe_dialog.qss")
        RECIPE_WIDGET     = AppPaths.qss_path("recipe_widget.qss")
        SEARCH_WIDGET     = AppPaths.qss_path("search_widget.qss")
        SIDEBAR_WIDGET    = AppPaths.qss_path("sidebar_widget.qss")
        TITLE_BAR         = AppPaths.qss_path("title_bar.qss")
        EMPTY_STATE_FRAME = AppPaths.qss_path("empty_state_frame.qss")
        INGREDIENT_WIDGET = AppPaths.qss_path("ingredient_widget.qss")
        SMART_COMBOBOX    = AppPaths.qss_path("smart_combobox.qss")
        WIDGET_FRAME      = AppPaths.qss_path("widget_frame.qss")

    @staticmethod
    def get_view_styles() -> dict:
        """
        Returns a mapping of view names to their associated QSS paths.
        """
        return {
            "application": [
                QssPaths.BASE,
                QssPaths.APPLICATION,
                QssPaths.Components.TITLE_BAR,
                QssPaths.Components.SIDEBAR_WIDGET,
                QssPaths.Components.SEARCH_WIDGET,
            ],
            "dashboard": [QssPaths.Views.DASHBOARD],
            "add_recipes": [
                QssPaths.Views.ADD_RECIPES,
                QssPaths.Components.MESSAGE_DIALOG,
                QssPaths.Components.INGREDIENT_WIDGET,
                QssPaths.Components.SMART_COMBOBOX
            ],
            "view_recipes": [
                QssPaths.Views.VIEW_RECIPES,
                QssPaths.Components.RECIPE_WIDGET,
                QssPaths.Components.RECIPE_DIALOG,
                QssPaths.Components.SMART_COMBOBOX,
            ],
            "meal_planner": [
                QssPaths.Views.MEAL_PLANNER,
                QssPaths.Components.EMPTY_STATE_FRAME
                ],
            "shopping_list": [QssPaths.Views.SHOPPING_LIST],
        }
