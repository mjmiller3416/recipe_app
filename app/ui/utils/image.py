"""app/ui/utils/image_utils.py

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QMessageBox

from app.core.utils import img_qt_load_safe


def load_pixmap_or_warn(path: str, parent=None) -> QPixmap:
    """Return a QPixmap from ``path`` or show a warning dialog if it fails."""
    pixmap = img_qt_load_safe(path)
    if pixmap.isNull() and parent is not None:
        QMessageBox.warning(parent, "Image Error", f"Could not load image: {path}")
    return pixmap

def img_qt_create_placeholder(size: QSize, color: QColor = None,
                            text: str = "") -> QPixmap:
    """Create placeholder pixmap with optional text.

    Args:
        size: Pixmap size
        color: Background color
        text: Optional text to draw

    Returns:
        Placeholder QPixmap
    """
    placeholder_color = color if color is not None else Qt.lightGray

    pixmap = QPixmap(size)
    pixmap.fill(placeholder_color)

    if text:
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()

    return pixmap
