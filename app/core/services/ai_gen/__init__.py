# app/core/services/ai_image_generation/__init__.py

from .service import ImageGenService, ImageRequest
from .config import ImageGenConfig
from .recipe_helper import RecipeImageHelper

def create_recipe_service() -> RecipeImageHelper:
    """Convenience factory for recipe image generation."""
    config = ImageGenConfig()
    service = ImageGenService(config)
    return RecipeImageHelper(service, config)

__all__ = ['ImageGenService', 'ImageGenConfig', 'RecipeImageHelper', 'ImageRequest', 'create_recipe_service']

