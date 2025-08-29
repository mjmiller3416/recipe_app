"""app/core/services/ai_image_generation/service.py

Core AI image generation service.

Provides generic image generation without domain-specific logic.
Handles OpenAI API calls, file management, and error handling.
"""

from __future__ import annotations

import os
import asyncio
import base64
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from openai import OpenAI, AsyncOpenAI

from .config import ImageGenConfig
from app.core.utils.image_utils import img_ai_slugify, img_ai_get_hash
from dev_tools import DebugLogger


@dataclass
class ImageRequest:
    """Request for image generation.

    Attributes:
        prompt: Text prompt for image generation
        size: Image dimensions (e.g. "1024x1024")
        filename_base: Base name for output file (will be slugified)
    """
    prompt: str
    size: str
    filename_base: str

    def __post_init__(self):
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if not self.filename_base.strip():
            raise ValueError("Filename base cannot be empty")


class ImageGenService:
    """Generic AI image generation service.

    Handles OpenAI API communication and file management without
    domain-specific knowledge.
    """

    def __init__(self, config: ImageGenConfig, *, api_key: Optional[str] = None):
        """Initialize the service.

        Args:
            config: Generation configuration
            api_key: Optional API key override (defaults to env OPENAI_API_KEY)
        """
        self.config = config
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise RuntimeError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)

        DebugLogger().log(
            f"ImageGenService initialized: {config.model} @ {config.default_size}",
            "info"
        )

    async def generate_image_async(
            self,
            prompt: str,
            filename_base: str,
            size: Optional[str] = None
        ) -> Path:
        """Generate a single image and save to file.

        Args:
            prompt: The text prompt for image generation
            filename_base: The base filename for the output image
            size: The desired image size

        Returns:
            The path to the generated image file
        """
        size = size or self.config.default_size

        # Validate size
        if not self.config.is_size_supported(size):
            supported = sorted(self.config.get_supported_sizes())
            raise ValueError(f"Size {size} not supported. Available: {supported}")

        # Check existing file
        output_path = self._get_output_path(filename_base, size)
        if not self.config.allow_overwrite and output_path.exists():
            DebugLogger().log(f"Image already exists: {output_path.name}", "info")
            return output_path

        # Generate and save
        image_bytes = await self._generate_async(prompt, size)  # Keep this as private
        self._save_image(image_bytes, output_path)

        return output_path

    async def generate_batch_async(self, requests: List[ImageRequest]) -> List[Path]:
        """Generate multiple images asynchronously.

        Args:
            requests: List of image generation requests

        Returns:
            List of paths to generated images
        """
        if not requests:
            return []

        output_paths = []
        tasks_with_indices = []  # Track which index each task corresponds to

        # First pass: determine what needs to be generated
        for i, request in enumerate(requests):
            # Validate size
            if not self.config.is_size_supported(request.size):
                supported = sorted(self.config.get_supported_sizes())
                raise ValueError(f"Size {request.size} not supported. Available: {supported}")

            # Get output path
            output_path = self._get_output_path(request.filename_base, request.size)
            output_paths.append(output_path)

            # Check if generation is needed
            if not self.config.allow_overwrite and output_path.exists():
                DebugLogger().log(f"Skipping existing: {output_path.name}", "debug")
                continue

            # Add generation task with its index
            task = self._generate_async(request.prompt, request.size)
            tasks_with_indices.append((task, i))

        # Generate in parallel
        if tasks_with_indices:
            tasks = [task for task, _ in tasks_with_indices]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Save results to correct paths
            for result, (_, original_index) in zip(results, tasks_with_indices):
                if isinstance(result, Exception):
                    raise result
                self._save_image(result, output_paths[original_index])

        DebugLogger().log(f"Batch complete: {len(output_paths)} images", "info")
        return output_paths

    async def _generate_async(self, prompt: str, size: str) -> bytes:
        """Generate a single image asynchronously.

        Args:
            prompt: The text prompt for image generation
            size: The desired image size

        Returns:
            The generated image as bytes
        """
        aclient = AsyncOpenAI(api_key=self.api_key)

        # Retry logic: 3 attempts with exponential backoff
        delay = 0.5
        for attempt in range(3):
            try:
                # Configure API call based on model
                if self.config.model == "gpt-image-1":
                    response = await aclient.images.generate(
                        model=self.config.model,
                        prompt=prompt,
                        size=size,
                        n=1,
                    )
                else:
                    # DALL-E models need response_format specified
                    response = await aclient.images.generate(
                        model=self.config.model,
                        prompt=prompt,
                        size=size,
                        n=1,
                        response_format="b64_json"
                    )

                b64_data = response.data[0].b64_json
                if not b64_data:
                    raise RuntimeError(f"API returned no image data for {self.config.model}")

                DebugLogger().log(
                    f"API success: {self.config.model} @ {size} ({len(b64_data)} chars)",
                    "debug"
                )
                return base64.b64decode(b64_data)

            except Exception as e:
                DebugLogger().log(
                    f"Attempt {attempt + 1}/3 failed: {e}",
                    "warning" if attempt < 2 else "error"
                )
                if attempt == 2:  # Last attempt
                    raise
                await asyncio.sleep(delay)
                delay *= 2

    def _get_output_path(self, filename_base: str, size: str) -> Path:
        """Generate output path for an image.

        Args:
            filename_base: The base filename for the output image
            size: The desired image size

        Returns:
            The output path for the generated image
        """
        slug = img_ai_slugify(filename_base)
        # Add hash for uniqueness while keeping readable names
        digest = img_ai_get_hash(filename_base)
        filename = f"{slug}-{digest}-{size}.png"
        return self.config.output_dir() / filename

    # Removed _slugify - now using img_ai_slugify from image_utils

    def _save_image(self, data: bytes, path: Path) -> None:
        """Save image data to file atomically.

        Args:
            data: The image data to save
            path: The path to the output file
        """
        # Write to temp file first, then rename (atomic on most filesystems)
        temp_path = path.with_suffix(".tmp")
        temp_path.write_bytes(data)
        temp_path.replace(path)
