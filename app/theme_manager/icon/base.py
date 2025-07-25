"""app/theme_manager/icon/base

Shared types and protocols for icon package.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Dict, Protocol

ColorPalette = Dict[str, str]

# ── Protocol Definitions ─────────────────────────────────────────────────────────────────────
class ThemedIcon(Protocol):
    """Protocol for any theme-aware icon-like object."""
    def refresh_theme(self, palette: ColorPalette) -> None: ...
    def objectName(self) -> str: ...
