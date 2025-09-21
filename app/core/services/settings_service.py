"""app/core/services/settings_service.py

Service for managing application settings and updating configurations.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from app.config import AppPaths


class SettingsService:
    """Service for managing application settings."""

    def __init__(self):
        self.settings_file = AppPaths.USER_DATA_DIR / "user_settings.json"
