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
        APPLICATION       = AppPaths.qss_path("core", "application.qss")
        APP_WINDOW        = AppPaths.qss_path("core", "app_window.qss")
        SIDE_BAR          = AppPaths.qss_path("core", "side_bar.qss")
        TITLE_BAR         = AppPaths.qss_path("core", "title_bar.qss")

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
        DIALOG_WINDOW     = AppPaths.qss_path("components", "dialog_window.qss")
        RECIPE_CARD       = AppPaths.qss_path("components", "recipe_card.qss")
        RECIPE_DIALOG     = AppPaths.qss_path("components", "recipe_dialog.qss")
        SEARCH_BAR        = AppPaths.qss_path("components", "search_bar.qss")
        CUSTOM_COMBOBOX   = AppPaths.qss_path("components", "custom_combobox.qss")
        WIDGET_FRAME      = AppPaths.qss_path("components", "widget_frame.qss")
        UPLOAD_IMAGE      = AppPaths.qss_path("components", "upload_image.qss")
        #SMART_LINE_EDIT   = AppPaths.qss_path("components", "smart_line_edit.qss")
    @staticmethod
    def get_styles() -> dict:
        """
        Returns a mapping of style categories to their QSS paths.
        Excludes widget-specific styles which are applied separately.
        """
        return {
            "core": [
                #QssPaths.Core.APPLICATION,
                QssPaths.Core.APP_WINDOW,
                QssPaths.Core.SIDE_BAR,
                #QssPaths.Core.TITLE_BAR,
            ],
            "views": [
                #QssPaths.Views.ADD_RECIPES,
                #QssPaths.Views.DASHBOARD,
                #QssPaths.Views.MEAL_PLANNER,
                #QssPaths.Views.SHOPPING_LIST,
                #QssPaths.Views.VIEW_RECIPES,
            ],
            "components": [
                #QssPaths.Components.EMPTY_STATE_FRAME,
                #QssPaths.Components.DIALOG_WINDOW,
                #QssPaths.Components.RECIPE_CARD,
                #QssPaths.Components.RECIPE_DIALOG,
                #QssPaths.Components.SEARCH_BAR,
                #QssPaths.Components.INGREDIENT_WIDGET,
                #QssPaths.Components.CUSTOM_COMBOBOX,
                #QssPaths.Components.WIDGET_FRAME,
                #QssPaths.Components.UPLOAD_IMAGE,
            ]
        }

