"""app/core/services/settings_service.py

Service for managing application settings and updating configurations.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from typing import Any, Dict

from app.config.paths import AppPaths
from app.core.services.ai_image_generation import ImageGenConfig
from dev_tools import DebugLogger


# ── Settings Service ─────────────────────────────────────────────────────────────────────────
class SettingsService:
    """Service for managing application settings."""

    def __init__(self):
        self.settings_file = AppPaths.USER_DATA_DIR / "user_settings.json"

    def get_image_generation_settings(self) -> Dict[str, Any]:
        """Get current image generation settings."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    return data.get("image_generation", {})
        except Exception as e:
            DebugLogger().log(f"Error loading image generation settings: {e}", "warning")

        # Return defaults if no settings found
        config = ImageGenConfig()
        return {
            "model": config.model,
            "prompt_template": config.prompt_template
        }

    def update_image_generation_settings(self, settings: Dict[str, Any]) -> bool:
        """Update image generation settings and return success status."""
        try:
            # Load existing settings
            data = {}
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)

            # Update image generation settings
            data["image_generation"] = settings

            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)

            DebugLogger().log(f"Updated image generation settings: {settings}", "info")
            return True

        except Exception as e:
            DebugLogger().log(f"Error updating image generation settings: {e}", "error")
            return False

    def get_current_image_config(self) -> ImageGenConfig:
        """Get current ImageGenConfig with settings applied."""
        settings = self.get_image_generation_settings()

        # Create config with custom settings
        config = ImageGenConfig()

        if "model" in settings:
            config.model = settings["model"]
        if "prompt_template" in settings:
            config.prompt_template = settings["prompt_template"]

        return config
