"""app/ui/utils/image_utils.py

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap


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
