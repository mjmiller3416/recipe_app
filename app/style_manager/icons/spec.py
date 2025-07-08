"""app/style_manager/icons/spec.py

Module defining IconSpec for themed icon specifications.
IconSpec encapsulates the path, size, variant, and optional button size
for icons used in the application.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QSize


# ── Icon Specification ───────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class IconSpec:
    path: Path
    size: QSize
    variant: str                # e.g. "DEFAULT" or a key into your theme’s state‐colors
    button_size: Optional[QSize] = None
