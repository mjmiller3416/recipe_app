"""config/settings.py

This module defines a class that loads and saves user settings to a local JSON file. It provides methods to
get, set, and toggle settings.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import json
from pathlib import Path

from config.paths.app_paths import AppPaths

# ── Class Definition ────────────────────────────────────────────────────────────
class UserSettings:
    """
    Loads and saves user preferences (e.g. theme, layout, last used page) to a local JSON file.
    """

    # ── Constants ───────────────────────────────────────────────────────────────
    CONFIG_PATH = AppPaths.USER_SETTINGS_PATH
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    DEFAULTS = {
        "theme": "dark",
        "start_on_last_page": True,
        "preferred_font_size": 14,
        "dev_mode": False,
    }

    def __init__(self):
        self.settings = self.DEFAULTS.copy()
        self.load()

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def load(self):
        """Load user settings from disk, or fall back to defaults."""
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"[UserSettings] ⚠️ Failed to load settings: {e}")

    def save(self):
        """Persist current settings to disk."""
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[UserSettings] ⚠️ Failed to save settings: {e}")

    def get(self, key, fallback=None):
        return self.settings.get(key, fallback)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def toggle(self, key: str):
        """Toggle a boolean setting and auto-save."""
        current = self.settings.get(key, False)
        self.settings[key] = not current
        self.save()
        return self.settings[key]
