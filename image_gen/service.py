"""image_gen/service.py

Generate two images (square + banner) per recipe.
Public API is synchronous; under the hood we run the two sizes in parallel.

- Model-aware size validation (gpt-image-1 vs dall-e-3)
- gpt-image-1: no response_format param; returns base64 (b64_json) by default
- Tiny retry/backoff for transient errors (e.g., 429)
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from openai import OpenAI, AsyncOpenAI

# Keep your local import path as-is
from config import ImageGenConfig


_SLUG_RE = re.compile(r"[^a-z0-9]+")

_ALLOWED_SIZES_BY_MODEL = {
    # GPT Image 1 (successor to DALL·E 3)
    "gpt-image-1": {"1024x1024", "1024x1536", "1536x1024"},
    # DALL·E 3 sizes (in case you flip back)
    "dall-e-3": {"1024x1024", "1024x1792", "1792x1024"},
    # DALL·E 2 for completeness
    "dall-e-2": {"256x256", "512x512", "1024x1024"},
}


@dataclass
class ImagePairPaths:
    """Return value with the two generated file paths."""
    portrait_path: Path
    banner_path: Path


class ImageGenService:
    """Encapsulates image generation behavior and file handling."""

    def __init__(self, config: ImageGenConfig, *, api_key: Optional[str] = None) -> None:
        """Initialize the service.

        Args:
            config: Image generation configuration.
            api_key: Optional override for OpenAI API key. If None, reads from env OPENAI_API_KEY.
        """
        self.config = config
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Load .env or pass api_key=...")

        # A small sync client (used only for non-parallel paths if needed)
        self.client = OpenAI(api_key=self.api_key)

        self._validate_sizes()

    # ── Public API ────────────────────────────────────────────────────────────
    def generate_for_recipe(self, recipe_name: str) -> ImagePairPaths:
        """Generate both a 1:1 portrait and a banner image for a recipe name (in parallel).

        Returns:
            ImagePairPaths with portrait and banner file paths.
        """
        prompt = self._build_prompt(recipe_name)
        portrait_path, banner_path = self._target_paths(recipe_name)

        # Skip if already present and we're not overwriting
        if (not self.config.allow_overwrite and
                portrait_path.exists() and banner_path.exists()):
            return ImagePairPaths(portrait_path=portrait_path, banner_path=banner_path)

        # Run both sizes concurrently using the async client under the hood.
        # Tip: call this method from a worker thread to avoid blocking your UI.
        img1_bytes, img2_bytes = asyncio.run(
            self._generate_pair_async(prompt, self.config.portrait_size,
                                      prompt + " — wide banner composition, 3/4 plate angle.",
                                      self.config.banner_size)
        )

        self._save_bytes(img1_bytes, portrait_path)
        self._save_bytes(img2_bytes, banner_path)
        return ImagePairPaths(portrait_path=portrait_path, banner_path=banner_path)

    # ── Internals ────────────────────────────────────────────────────────────
    def _build_prompt(self, recipe_name: str) -> str:
        """Fill the configured template with a recipe name and add soft negatives."""
        base = self.config.prompt_template.format(recipe_name=recipe_name.strip())
        if self.config.negative_prompt:
            base = f"{base} Avoid: {self.config.negative_prompt}."
        return base

    def _target_paths(self, recipe_name: str) -> Tuple[Path, Path]:
        """Compute deterministic output paths for this recipe."""
        slug = self._slugify(recipe_name)
        digest = hashlib.sha1(recipe_name.encode("utf-8")).hexdigest()[:8]
        out = self.config.output_dir()
        portrait_path = out / f"{slug}-{digest}-portrait_{self.config.portrait_size}.png"
        banner_path = out / f"{slug}-{digest}-banner_{self.config.banner_size}.png"
        return portrait_path, banner_path

    def _slugify(self, text: str) -> str:
        s = text.lower().strip()
        s = _SLUG_RE.sub("-", s)
        return s.strip("-")

    def _save_bytes(self, data: bytes, path: Path) -> None:
        """Write bytes to disk (atomic-ish)."""
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)

    def _validate_sizes(self) -> None:
        sizes = _ALLOWED_SIZES_BY_MODEL.get(self.config.model)
        if not sizes:
            raise ValueError(f"Unknown or unsupported model: {self.config.model}")
        if self.config.portrait_size not in sizes:
            raise ValueError(
                f"portrait_size {self.config.portrait_size} not valid for {self.config.model}. "
                f"Allowed: {sorted(sizes)}"
            )
        if self.config.banner_size not in sizes:
            raise ValueError(
                f"banner_size {self.config.banner_size} not valid for {self.config.model}. "
                f"Allowed: {sorted(sizes)}"
            )

    # ── Async core (used internally for parallel generation) ─────────────────
    async def _generate_pair_async(
        self,
        prompt1: str,
        size1: str,
        prompt2: str,
        size2: str,
    ) -> tuple[bytes, bytes]:
        """Generate two images concurrently (uses AsyncOpenAI)."""
        
        async def gen_b64(prompt: str, size: str) -> bytes:
            # Create a new client for each request to avoid cleanup issues
            aclient = AsyncOpenAI(api_key=self.api_key)
            
            # gpt-image-1: do NOT pass response_format; it returns b64_json by default
            # retry/backoff (3 tries: 0.5s, 1.0s, 2.0s)
            delay = 0.5
            for attempt in range(3):
                try:
                    resp = await aclient.images.generate(
                        model=self.config.model,
                        prompt=prompt,
                        size=size,
                        n=1,
                    )
                    b64 = resp.data[0].b64_json
                    return base64.b64decode(b64)
                except Exception as e:  # broad catch to keep example self-contained
                    if attempt == 2:
                        raise
                    # Heuristic: back off on rate limits / transient issues
                    await asyncio.sleep(delay)  # Use async sleep
                    delay *= 2

        # Generate both images concurrently
        img1, img2 = await asyncio.gather(
            gen_b64(prompt1, size1),
            gen_b64(prompt2, size2),
        )
        return img1, img2
