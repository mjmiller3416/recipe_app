"""config/paths.py

This module defines a class that centralizes the static paths used in the MealGenie application
"""
from pathlib import Path


# ── Class Definition ────────────────────────────────────────────────────────────
class AppPaths:
    """
    Centralized static paths used across the MealGenie application. \n
    *** Adjust ROOT_DIR if folder structure changes ***
    """

    # ── Root Directories ───────────────────────────────────────────────────────
    ROOT_DIR = Path(__file__).resolve().parents[3]
    APP_DIR = ROOT_DIR / "app"
    CONFIG_DIR = APP_DIR / "config"
    ASSETS_DIR = APP_DIR / "assets"
    DATA_DIR = ROOT_DIR / "data_files"
    USER_PROFILE_DIR = DATA_DIR / "user_profile"
    TM_DIR = APP_DIR / "theme_manager"

    # ── Asset Directories ───────────────────────────────────────────────────────
    ICONS_DIR = ASSETS_DIR / "icons"
    IMAGES_DIR = DATA_DIR / "images"
    TEMP_CROP_DIR = DATA_DIR / "temp_crops"
    FONT_DIR = ASSETS_DIR / "fonts"
    RECIPE_IMAGES_DIR = DATA_DIR / "recipe_images"

    # ── Theme Directories ───────────────────────────────────────────────────────
    USER_SETTINGS_PATH = DATA_DIR / "user_settings.json"
    THEME_CONFIG_PATH = CONFIG_DIR / "theme_config.json"
    BASE_STYLE = TM_DIR / "base_style.qss"
    QSS_DIR = TM_DIR / "qss"

    # ── Path Utilities ──────────────────────────────────────────────────────────
    @staticmethod
    def image_path(file_name: str) -> str:
        """Get path to general image (SVG format)."""
        return str(AppPaths.IMAGES_DIR / f"{file_name}")

    @staticmethod
    def recipe_image_path(file_name: str) -> str:
        """Get path to saved recipe image (PNG format)."""
        return str(AppPaths.RECIPE_IMAGES_DIR / f"{file_name}")

    @staticmethod
    def icon_path(file_name: str) -> str:
        """Get path to UI icon (SVG format)."""
        return str(AppPaths.ICONS_DIR / f"{file_name}")

    @staticmethod
    def qss_path(*path_parts: str) -> str:
        """Get path to a QSS file by category and name."""
        return str(AppPaths.QSS_DIR.joinpath(*path_parts))
