"""tools/imagegen_config.py
Configuration for AI image generation.

PEP 8 + Google-style docstrings + type hints.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageGenConfig:
    """Holds tunable knobs for image generation.

    Attributes:
        model: OpenAI image model name.
        portrait_size: Square size (1:1) for card/thumb images.
        banner_size: Wide banner size (16:9-ish). Use one of the allowed sizes.
        quality: Quality hint (currently 'standard' or 'high' for some providers; OpenAI uses defaults).
        output_root: Root folder for generated images (inside your existing user_data).
        dir_name: Subfolder for AI images under the output_root.
        prompt_template: Template string for the image prompt. {recipe_name} is injected.
        negative_prompt: Things to avoid in the image (optional).
        allow_overwrite: If False and file exists, skip regeneration.
    """

    model: str = "gpt-image-1"
    portrait_size: str = "1024x1024"      # 1:1
    banner_size: str = "1536x1024"      # wide banner supported by OpenAI
    quality: str = "standard"

    output_root: Path = Path("data_files")
    dir_name: str = "ai_images"

    prompt_template: str = (
        "High-quality studio food photography of {recipe_name}. "
        "Style: natural light, shallow depth-of-field, appetizing, no text, no branding, no people. "
        "Plating on a neutral surface. Composition centered and clean. "
        "White balance slightly warm. Ultra-detailed, realistic, crisp."
    )

    negative_prompt: str = (
        "text, watermark, logo, brand, humans, hands, clutter, messy background, "
        "oversaturation, unrealistic colors, tilt-shift artifacts"
    )

    allow_overwrite: bool = False

    def output_dir(self) -> Path:
        """Return path to the output directory (ensures it exists)."""
        p = self.output_root / self.dir_name
        p.mkdir(parents=True, exist_ok=True)
        return p
