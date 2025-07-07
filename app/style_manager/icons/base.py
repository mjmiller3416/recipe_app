"""Shared types and protocols for icon package."""
from typing import Protocol, Dict

IconName = str
ColorPalette = Dict[str, str]

class ThemedIcon(Protocol):
    """Protocol for any theme-aware icon-like object."""
    def refresh_theme(self, palette: ColorPalette) -> None: ...
    def objectName(self) -> str: ...