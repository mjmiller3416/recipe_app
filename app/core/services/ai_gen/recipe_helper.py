"""app/core/services/ai_image_generation/recipe_helper.py

Recipe-specific image generation helpers.

Provides recipe-domain logic for prompts, sizing, and file naming
while delegating actual generation to the generic ImageGenService.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple, Optional

from .service import ImageGenService, ImageRequest
from .config import ImageGenConfig
from dev_tools import DebugLogger


class RecipeImagePaths(NamedTuple):
    """Paths to generated recipe images."""
    standard: Path
    banner: Path


class RecipeImageHelper:
    """Helper for generating recipe-specific images.

    Handles recipe-specific concerns like prompt templates,
    sizing decisions, and file naming conventions.
    """

    # Image type configurations
    _IMAGE_CONFIGS = {
        "standard": {
            "size_preference": ["1024x1024"],  # Square aspect ratio
            "prompt_suffix": "Close-up, top-down view. Centered plating.",
        },
        "banner": {
            "size_preference": ["1536x1024", "1792x1024", "1024x1024"],  # Wide preferred
            "prompt_suffix": "Wide banner composition, 3/4 plate angle, appetizing presentation.",
        },
    }

    # Base prompt template
    _BASE_PROMPT = (
        "High-quality studio food photography of {recipe_name}. "
        "Style: natural light, shallow depth-of-field, appetizing, "
        "no text, no branding, no people. Plating on neutral surface. "
        "Composition clean and professional. White balance slightly warm. "
        "Ultra-detailed, realistic, crisp."
    )

    def __init__(self, service: ImageGenService, config: ImageGenConfig):
        """Initialize recipe helper.

        Args:
            service: Generic image generation service
            config: Generation configuration
        """
        self.service = service
        self.config = config

        DebugLogger().log("RecipeImageHelper initialized", "info")

    async def generate_for_recipe(self,
                          recipe_name: str,
                          image_type: str = "standard") -> Path:
        """Generate a single image for a recipe.

        Args:
            recipe_name: Name of the recipe
            image_type: Type of image ("standard" or "banner")

        Returns:
            Path to generated image

        Raises:
            ValueError: If image_type is not supported
        """
        if image_type not in self._IMAGE_CONFIGS:
            available = list(self._IMAGE_CONFIGS.keys())
            raise ValueError(f"Unknown image type '{image_type}'. Available: {available}")

        recipe_name = recipe_name.strip()
        if not recipe_name:
            raise ValueError("Recipe name cannot be empty")

        # Build prompt and determine size
        prompt = self._build_prompt(recipe_name, image_type)
        size = self._get_optimal_size(image_type)
        filename_base = f"{recipe_name}-{image_type}"

        DebugLogger().log(
            f"Generating {image_type} image for '{recipe_name}' @ {size}",
            "info"
        )

        return await self.service.generate_image_async(prompt, filename_base, size)

    async def generate_both_for_recipe(self, recipe_name: str) -> RecipeImagePaths:
        """Generate both standard and banner images for a recipe.

        Args:
            recipe_name: Name of the recipe

        Returns:
            RecipeImagePaths with both image paths
        """
        recipe_name = recipe_name.strip()
        if not recipe_name:
            raise ValueError("Recipe name cannot be empty")

        DebugLogger().log(f"Generating both images for '{recipe_name}'", "info")

        # Generate them individually to guarantee ordering
        standard_path = await self.generate_for_recipe(recipe_name, "standard")
        banner_path = await self.generate_for_recipe(recipe_name, "banner")

        return RecipeImagePaths(
            standard=standard_path,
            banner=banner_path
        )

    def _build_prompt(self, recipe_name: str, image_type: str) -> str:
        """Build a complete prompt for recipe image generation."""
        config = self._IMAGE_CONFIGS[image_type]

        base = self._BASE_PROMPT.format(recipe_name=recipe_name)
        suffix = config["prompt_suffix"]

        return f"{base} {suffix}"

    def _get_optimal_size(self, image_type: str) -> str:
        """Get the best size for an image type given the current model."""
        preferences = self._IMAGE_CONFIGS[image_type]["size_preference"]
        supported = self.config.get_supported_sizes()

        # Return first preference that's supported
        for preferred in preferences:
            if preferred in supported:
                return preferred

        # Fallback to config default
        return self.config.default_size
