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
    ROOT_DIR = Path(__file__).resolve().parents[2]
    CONFIG_DIR = ROOT_DIR / "config"
    ASSETS_DIR = ROOT_DIR / "assets"
    DATA_DIR = ROOT_DIR / "data"
    STYLES_DIR = ROOT_DIR / "ui" / "styles"

    # ── Asset Directories ───────────────────────────────────────────────────────
    ICONS_DIR = ASSETS_DIR / "icons"
    IMAGES_DIR = DATA_DIR / "images"
    FONTS_DIR = ASSETS_DIR / "fonts"
    RECIPE_IMAGES_DIR = DATA_DIR / "recipe_images"

    # ── Theme Directories ───────────────────────────────────────────────────────
    USER_SETTINGS_PATH = CONFIG_DIR / "user_settings.json"
    THEME_CONFIG_PATH = CONFIG_DIR / "theme_config.json"
    QSS_DIR = STYLES_DIR / "stylesheets"
    THEMES_DIR = STYLES_DIR / "themes"

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
    def qss_path(file_name: str) -> str:
        """Get path to a QSS file by name."""
        return str(AppPaths.QSS_DIR / f"{file_name}")
