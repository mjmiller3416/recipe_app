"""ui/styles/utils/qss_combiner.py

Responsible for combining QSS files based on application views.
This allows for a modular approach to styling, where each view can have its own QSS file,
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from theme_loader.qss_paths import QssPaths


# ── Class Definition ────────────────────────────────────────────────────────────
class QssCombiner:
    """
    Fetches QSS paths for a specific view or for the entire app.
    """

    @staticmethod
    def get_for_view(view_name: str) -> list[str]:
        """
        Get QSS files for a specific view including application base.

        Args:
            view_name (str): Name of the view (e.g. 'dashboard')

        Returns:
            list[str]: List of QSS file paths for the view.
        """
        view_map = QssPaths.get_styles()
        common = view_map.get("application", [])
        specific = view_map.get(view_name.lower(), [])
        return common + specific

    @staticmethod
    def get_all_styles() -> list[str]:
        """
        Returns a deduplicated, flattened list of all QSS file paths.

        Returns:
            list[str]: All QSS paths across all views/components.
        """
        all_paths = []
        for paths in QssPaths.get_styles().values():
            all_paths.extend(paths)
        return list(dict.fromkeys(all_paths))  # preserve order