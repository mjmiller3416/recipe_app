"""app/core/utils/fs_utils.py

File system utility functions.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import tempfile
import uuid
from pathlib import Path


# ── Functions ───────────────────────────────────────────────────────────────────
def ensure_directory_exists(dir_path: Path) -> None:
    """Make sure a directory exists (creates parents)."""
    dir_path.mkdir(parents=True, exist_ok=True)

def get_temp_image_path(prefix: str = "cropped", ext: str = "png", subdir: str = "app_crops") -> Path:
    """
    Returns a unique temp-file path under the system temp dir (or a subdir).
    e.g. /tmp/app_crops/cropped_ab12cd34.png
    """
    base = Path(tempfile.gettempdir()) / subdir
    ensure_directory_exists(base)
    filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    return base / filename