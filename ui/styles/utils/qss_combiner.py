"""ui/styles/utils/qss_combiner.py

Responsible for combining QSS files based on application views.
This allows for a modular approach to styling, where each view can have its own QSS file,
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from config.paths.qss_paths import QssPaths


# ── Class Definition ────────────────────────────────────────────────────────────
class QssCombiner:
    """
    Centralized mapping of which QSS files to apply per view.
    Used by ThemeController to build the correct style stack.
    """

    @staticmethod
    def get_for_view(view_name: str) -> list[str]:
        view_map = {
            "application": [
                QssPaths.APPLICATION,
                QssPaths.Components.TITLE_BAR,
                QssPaths.Components.SIDEBAR_WIDGET,
                QssPaths.Components.SEARCH_WIDGET,
            ],
            "dashboard": [
                QssPaths.APPLICATION,
                QssPaths.Views.DASHBOARD,
            ],
            "add_recipes": [
                QssPaths.APPLICATION,
                QssPaths.Views.ADD_RECIPES,
                QssPaths.Components.MESSAGE_DIALOG,
            ],
            "view_recipes": [
                QssPaths.APPLICATION,
                QssPaths.Views.VIEW_RECIPES,
                QssPaths.Components.RECIPE_WIDGET,
            ],
            "meal_planner": [
                QssPaths.APPLICATION,
                QssPaths.Views.MEAL_PLANNER,
            ],
            "shopping_list": [
                QssPaths.APPLICATION,
                QssPaths.Views.SHOPPING_LIST,
            ],
        }

        return view_map.get(view_name.lower(), [QssPaths.APPLICATION])
