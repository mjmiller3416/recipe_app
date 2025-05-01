# ── Imports ─────────────────────────────────────────────────────────────────────
from core.application.config import ICONS_DIR, IMAGES_DIR, RECIPE_DIR
from helpers.app_helpers.debug_logger import DebugLogger


def image_path(name: str) -> str:
    return str(IMAGES_DIR / f"{name}")  # All images must be SVG

def recipe_image_path(name: str) -> str:
    return str(RECIPE_DIR / f"{name}")  # All recipe images must be PNG
