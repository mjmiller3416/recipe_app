""""config/paths/qss_paths.py

Centralized mapping of QSS stylesheet file paths organized by category.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from config.paths.app_paths import AppPaths


# ── Class Definition ────────────────────────────────────────────────────────────
class QssPaths:
    """
    Centralized mapping of QSS stylesheet file paths.
    Used by ThemeController and ThemeLoader for structured styling.
    """

    # ── Core Styles ─────────────────────────────────────────────────────────────────
    class Core:
        BASE              = AppPaths.qss_path("core", "base.qss")
        APPLICATION       = AppPaths.qss_path("core", "application.qss")

    # ── View Styles ─────────────────────────────────────────────────────────────────
    class Views:
        ADD_RECIPES       = AppPaths.qss_path("views", "add_recipes.qss")
        DASHBOARD         = AppPaths.qss_path("views", "dashboard.qss")
        MEAL_PLANNER      = AppPaths.qss_path("views", "meal_planner.qss")
        SHOPPING_LIST     = AppPaths.qss_path("views", "shopping_list.qss")
        VIEW_RECIPES      = AppPaths.qss_path("views", "view_recipes.qss")

    # ── Component Styles ────────────────────────────────────────────────────────────
    class Components:
        EMPTY_STATE_FRAME = AppPaths.qss_path("components", "empty_state_frame.qss")
        INGREDIENT_WIDGET = AppPaths.qss_path("components", "ingredient_widget.qss")
        RECIPE_CARD       = AppPaths.qss_path("components", "recipe_card.qss")
        SEARCH_BAR        = AppPaths.qss_path("components", "search_bar.qss")
        SIDE_BAR          = AppPaths.qss_path("components", "side_bar.qss")
        TITLE_BAR         = AppPaths.qss_path("components", "title_bar.qss")

    # ── Dialog Styles ───────────────────────────────────────────────────────────────
    class Dialogs:
        MESSAGE_DIALOG    = AppPaths.qss_path("dialogs", "message_dialog.qss")
        RECIPE_DIALOG     = AppPaths.qss_path("dialogs", "recipe_dialog.qss")

    # ── Widget Styles (Override-Protected) ──────────────────────────────────────────
    class Widgets:
        SMART_COMBOBOX    = AppPaths.qss_path("widgets", "smart_combobox.qss")
        WIDGET_FRAME      = AppPaths.qss_path("widgets", "widget_frame.qss")

    @staticmethod
    def get_styles() -> dict:
        """
        Returns a mapping of style categories to their QSS paths.
        Excludes widget-specific styles which are applied separately.
        """
        return {
            "core": [
                QssPaths.Core.APPLICATION,
                QssPaths.Core.BASE,
            ],
            "views": [
                QssPaths.Views.ADD_RECIPES,
                QssPaths.Views.DASHBOARD,
                QssPaths.Views.MEAL_PLANNER,
                QssPaths.Views.SHOPPING_LIST,
                QssPaths.Views.VIEW_RECIPES,
            ],
            "components": [
                QssPaths.Components.EMPTY_STATE_FRAME,
                QssPaths.Components.INGREDIENT_WIDGET,
                QssPaths.Components.RECIPE_CARD,
                QssPaths.Components.SEARCH_BAR,
                QssPaths.Components.SIDE_BAR,
                QssPaths.Components.TITLE_BAR,
            ],
            "dialogs": [
                QssPaths.Dialogs.MESSAGE_DIALOG,
                QssPaths.Dialogs.RECIPE_DIALOG,

            ],
            "widgets": [
                QssPaths.Widgets.SMART_COMBOBOX,
                QssPaths.Widgets.WIDGET_FRAME,
            ]
        }

