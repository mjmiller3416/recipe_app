"""config/app_paths.py

Centralized path management for the MealGenie application.
All application paths are defined here to ensure consistency across modules.
"""
from pathlib import Path


# ── Class Definition ────────────────────────────────────────────────────────────
class AppPaths:
    """
    Centralized static paths used across the MealGenie application.
    
    Directory structure:
    - ROOT_DIR: Project root (recipe_app/)
    - APP_DIR: Application code (app/)
    - DATA_DIR: User data files (_data_files/)
    """

    # ── Root Directories ───────────────────────────────────────────────────────
    ROOT_DIR = Path(__file__).resolve().parents[2]  # Fixed: parents[2] not [3]
    APP_DIR = ROOT_DIR / "app"
    CONFIG_DIR = APP_DIR / "config"
    ASSETS_DIR = APP_DIR / "assets"
    DATA_DIR = ROOT_DIR / "_data_files"
    USER_PROFILE_DIR = DATA_DIR / "user_profile"
    STYLE_DIR = APP_DIR / "style"

    # ── Core Directories ────────────────────────────────────────────────────────
    CORE_DIR = APP_DIR / "core"
    DATABASE_DIR = CORE_DIR / "database"
    MIGRATIONS_DIR = DATABASE_DIR / "migrations"
    MODELS_DIR = CORE_DIR / "models"
    REPOS_DIR = CORE_DIR / "repositories"
    SERVICES_DIR = CORE_DIR / "services"
    CORE_UTILS_DIR = CORE_DIR / "utils"

    # ── UI Directories ──────────────────────────────────────────────────────────
    UI_DIR = APP_DIR / "ui"
    COMPONENTS_DIR = UI_DIR / "components"
    VIEWS_DIR = UI_DIR / "views"
    UI_UTILS_DIR = UI_DIR / "utils"
    UI_SERVICES_DIR = UI_DIR / "services"

    # ── Asset Directories ───────────────────────────────────────────────────────
    ICONS_DIR = ASSETS_DIR / "icons"
    FONTS_DIR = ASSETS_DIR / "fonts"
    IMAGES_DIR = ASSETS_DIR / "images"

    # ── Data Directories ────────────────────────────────────────────────────────
    USER_DATA_DIR = DATA_DIR  # Alias for consistency with services
    TEMP_CROP_DIR = DATA_DIR / "temp_crops"
    RECIPE_IMAGES_DIR = DATA_DIR / "recipe_images"
    CUSTOM_THEMES_DIR = DATA_DIR / "custom_themes"

    # ── Database & Settings ─────────────────────────────────────────────────────
    DATABASE_PATH = DATABASE_DIR / "app_data.db"
    USER_SETTINGS_PATH = DATA_DIR / "user_settings.json"
    APP_CONFIG_PATH = CONFIG_DIR / "config.json"
    
    # ── Theme & Styling ──────────────────────────────────────────────────────────
    THEME_DIR = STYLE_DIR / "theme"
    BASE_STYLE = THEME_DIR / "base_style.qss"
    QSS_DIR = THEME_DIR / "qss"
    MATERIAL_THEME_PATH = THEME_DIR / "material-theme.json"
    ANIMATION_DIR = STYLE_DIR / "animation"
    EFFECTS_DIR = STYLE_DIR / "effects"
    ICON_DIR = STYLE_DIR / "icon"

    # ── Path Utilities ──────────────────────────────────────────────────────────
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
    
    @staticmethod
    def ensure_directories() -> None:
        """Create required directories if they don't exist."""
        directories = [
            AppPaths.DATA_DIR,
            AppPaths.USER_PROFILE_DIR,
            AppPaths.TEMP_CROP_DIR,
            AppPaths.RECIPE_IMAGES_DIR,
            AppPaths.CUSTOM_THEMES_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_temp_path(prefix: str = "temp", suffix: str = "") -> Path:
        """Generate a temporary file path in the temp crops directory."""
        import tempfile
        AppPaths.TEMP_CROP_DIR.mkdir(parents=True, exist_ok=True)
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, 
                                    dir=str(AppPaths.TEMP_CROP_DIR))
        import os
        os.close(fd)
        return Path(path)
