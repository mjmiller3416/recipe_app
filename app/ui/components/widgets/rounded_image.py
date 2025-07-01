# ── components/image/rounded_image.py ──

from pathlib import Path
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QSize, QRectF

# ── In-Memory Image Cache ──────────────────────────────────────────────────────
_image_cache: dict[tuple[str, int, tuple[int, int, int, int]], QPixmap] = {}

# ── RoundedImage Widget ────────────────────────────────────────────────────────
class RoundedImage(QLabel):
    """A QLabel that displays a rounded image with optional per-corner radii."""

    def __init__(self, image_path: str | Path, size: int = 100, radii: tuple[int, int, int, int] = (0, 0, 0, 0), parent=None):
        super().__init__(parent)
        self.image_path = str(image_path)
        self.size = size
        self.radii = radii

        # ── Size Handling ──
        if isinstance(size, QSize):
            self.size = size.width()  # Assume square
            qsize = size
        else:
            self.size = size
            qsize = QSize(size, size)

        # ── Radii Handling ──
        if isinstance(radii, int):
            self.radii = (radii, radii, radii, radii)
        else:
            self.radii = radii

        self.setFixedSize(qsize)
        self.setScaledContents(True)

        self.setPixmap(self._get_cached_rounded_pixmap())

    def _get_cached_rounded_pixmap(self) -> QPixmap:
        key = (self.image_path, self.size, self.radii)
        if key in _image_cache:
            return _image_cache[key]

        pixmap = QPixmap(self.image_path).scaled(
            self.size, self.size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )

        rounded = QPixmap(self.size, self.size)
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)

        path = self._build_round_rect_path(self.size, self.radii)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        _image_cache[key] = rounded
        return rounded

    def _build_round_rect_path(self, size: int, radii: tuple[int, int, int, int]) -> QPainterPath:
        tl, tr, br, bl = radii
        rect = QRectF(0, 0, size, size)
        path = QPainterPath()
        path.moveTo(rect.left() + tl, rect.top())

        path.lineTo(rect.right() - tr, rect.top())
        path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + tr)

        path.lineTo(rect.right(), rect.bottom() - br)
        path.quadTo(rect.right(), rect.bottom(), rect.right() - br, rect.bottom())

        path.lineTo(rect.left() + bl, rect.bottom())
        path.quadTo(rect.left(), rect.bottom(), rect.left(), rect.bottom() - bl)

        path.lineTo(rect.left(), rect.top() + tl)
        path.quadTo(rect.left(), rect.top(), rect.left() + tl, rect.top())

        path.closeSubpath()
        return path
