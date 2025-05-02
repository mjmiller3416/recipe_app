"""core.helpers.fontkit.py

Register and manage custom fonts for the application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path
from PySide6.QtGui import QFontDatabase

from config.paths.app_paths import AppPaths

# ── Font Registration ───────────────────────────────────────────────────────────
FONTS = {
    "roboto": AppPaths.FONTS_DIR / "Roboto-Regular.ttf",
    "montserrat": AppPaths.FONTS_DIR / "Montserrat-Regular.ttf",
    "poppins": AppPaths.FONTS_DIR / "Poppins-Regular.ttf",
    "sakitu": AppPaths.FONTS_DIR / "SakituBaelahClean.ttf",
}

def register_all_fonts():
    """Register all application fonts with the Qt font system."""
    for font_name, path in FONTS.items():
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))


# ── PUA Swash Logic ────────────────────────────────────────────────────────────
# Example: Mapping standard lowercase characters to PUA characters with swooshes
PUA_MAP = {
    "a": "",  # Replace with actual PUA codes from the font
    "b": "",
    "l": "",
    "k": "",
    # ... add more as needed
}

def swooshify(text: str) -> str:
    """
    Replace lowercase characters in a string with PUA alternatives if available.
    Intended for stylized recipe names using decorative fonts.
    """
    return ''.join(PUA_MAP.get(c, c) for c in text)


# Optional utility
__all__ = ["register_all_fonts", "swooshify"]
