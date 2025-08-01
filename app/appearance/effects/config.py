"""app/appearance/effects/config.py

Configuration for visual effects (shadows, glows, blurs, opacity) used in the application.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from collections import namedtuple
from enum import Enum

from PySide6.QtGui import QColor

# ── Shadow Effect Enum ───────────────────────────────────────────────────────────────────────
ShadowStyle = namedtuple("ShadowStyle", "color blur_radius offset_x offset_y")

class Shadow(Enum):
    """
    Predefined shadow styles for elevation effects.

    - ELEVATION_0: No shadow, flat appearance.
    - ELEVATION_1: Subtle shadow for resting cards.
    - ELEVATION_3: More pronounced shadow for hover/active states.
    - ELEVATION_6: Stronger shadow for floating cards.
    - ELEVATION_12: Heaviest shadow for dialogs/modals.
    """
    ELEVATION_0 = ShadowStyle(QColor(0, 0, 0, 0), 0.0, 0.0, 0.0)
    ELEVATION_1 = ShadowStyle(QColor(0, 0, 0, 40), 8.0, 0.0, 2.0)
    ELEVATION_3 = ShadowStyle(QColor(0, 0, 0, 60), 12.0, 0.0, 4.0)
    ELEVATION_6 = ShadowStyle(QColor(0, 0, 0, 80), 16.0, 0.0, 6.0)
    ELEVATION_12 = ShadowStyle(QColor(0, 0, 0, 100), 24.0, 0.0, 8.0)


# ── Glow Effect Enum ─────────────────────────────────────────────────────────────────────────
GlowStyle = namedtuple("GlowStyle", "color blur_radius")

class Glow(Enum):
    CYAN    = GlowStyle(QColor(0, 255, 255, 200), 60.0)
    PINK    = GlowStyle(QColor(255, 0, 255, 220), 50.0)
    GOLD    = GlowStyle(QColor(255, 215, 0, 180), 40.0)
    ERROR   = GlowStyle(QColor(255, 0, 0, 150), 30.0)
    PRIMARY = GlowStyle(QColor(100, 149, 237, 180), 45.0)  # Cornflower Blue-ish
