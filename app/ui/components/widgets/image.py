"""app/ui/components/widgets/image.py

Unified image display widgets with caching, borders, and shape support.
Consolidates RoundedImage and CircularImage functionality.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import Property, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QStyle, QStyleOption

from app.core.utils.image_utils import (
    img_cache_get_key, img_cache_get, img_cache_set,
    img_apply_rounded_mask, img_apply_circular_mask,
    img_get_placeholder, img_validate_path, img_qt_load_safe
)


# ── Base Image Widget ───────────────────────────────────────────────────────────────────────────────────────
class BaseImage(QLabel):
    """Base class for shaped image widgets with caching and border support."""

    def __init__(self, size: Union[int, QSize] = 100, parent=None):
        super().__init__(parent)

        # Size handling
        if isinstance(size, int):
            self._size = size
            self.setFixedSize(size, size)
        else:
            self._size = size.width()  # Assume square for consistency
            self.setFixedSize(size)

        # Image properties
        self._image_path: Optional[str] = None
        self._original_pixmap: Optional[QPixmap] = None

        # Border properties (Qt Properties for QSS support)
        self._border_width = 0
        self._border_color = QColor(0, 0, 0, 0)

        # Widget setup
        self.setScaledContents(False)  # We handle scaling manually
        self.setAttribute(Qt.WA_StyledBackground, True)

    # ── Qt Properties for QSS Support ──
    def getBorderWidth(self) -> int:
        return self._border_width

    def setBorderWidth(self, width: int):
        self._border_width = max(0, width)
        self.update()

    def getBorderColor(self) -> QColor:
        return self._border_color

    def setBorderColor(self, color):
        self._border_color = QColor(color)
        self.update()

    borderWidth = Property(int, getBorderWidth, setBorderWidth)
    borderColor = Property(QColor, getBorderColor, setBorderColor)

    # ── Image Management ──
    def setImagePath(self, path: Union[str, Path, None]) -> None:
        """Set image from file path."""
        self._image_path = str(path) if path else None
        self._original_pixmap = None
        self._refresh_display()

    def updatePixmap(self, pixmap: QPixmap) -> None:
        """Set image from QPixmap directly."""
        self._image_path = None
        self._original_pixmap = pixmap
        self._refresh_display()

    def clearImage(self) -> None:
        """Clear the current image."""
        self._image_path = None
        self._original_pixmap = None
        self.clear()

    # ── Abstract/Override Methods ──
    def _get_cache_key(self) -> str:
        """Generate cache key for this widget configuration."""
        source = self._image_path or "direct_pixmap"
        return img_cache_get_key(source, size=self._size, radii=self._get_shape_params())

    def _get_shape_params(self) -> tuple:
        """Get shape-specific parameters for caching. Override in subclasses."""
        return ()

    def _apply_shape_mask(self, pixmap: QPixmap) -> QPixmap:
        """Apply shape-specific mask to pixmap. Override in subclasses."""
        return pixmap

    def _draw_border(self, painter: QPainter) -> None:
        """Draw shape-specific border. Override in subclasses."""
        pass

    # ── Core Implementation ──
    def _refresh_display(self) -> None:
        """Refresh the displayed image with caching."""
        cache_key = self._get_cache_key()
        cached = img_cache_get(cache_key)

        if cached is not None:
            self.setPixmap(cached)
            return

        # Load source pixmap
        if self._image_path:
            if not img_validate_path(self._image_path):
                placeholder = img_get_placeholder(self._size)
                img_cache_set(cache_key, placeholder)
                self.setPixmap(placeholder)
                return
            source_pixmap = img_qt_load_safe(self._image_path)
        elif self._original_pixmap:
            source_pixmap = self._original_pixmap
        else:
            placeholder = img_get_placeholder(self._size)
            img_cache_set(cache_key, placeholder)
            self.setPixmap(placeholder)
            return

        if source_pixmap.isNull():
            placeholder = img_get_placeholder(self._size)
            img_cache_set(cache_key, placeholder)
            self.setPixmap(placeholder)
            return

        # Scale to fit
        scaled = source_pixmap.scaled(
            self._size, self._size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        # Apply shape mask
        shaped = self._apply_shape_mask(scaled)

        # Cache and display
        img_cache_set(cache_key, shaped)
        self.setPixmap(shaped)

    def paintEvent(self, event):
        """Custom paint event for border support."""
        # Let QLabel draw the pixmap first
        super().paintEvent(event)

        # Draw custom border if needed
        if self._border_width > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)

            # Let QSS draw background
            opt = QStyleOption()
            opt.initFrom(self)
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

            # Draw shape-specific border
            self._draw_border(painter)
            painter.end()


# ── Rounded Rectangle Image ─────────────────────────────────────────────────────────────────────────────────
class RoundedImage(BaseImage):
    """Image widget with configurable rounded corners."""

    def __init__(self, image_path: Union[str, Path, None] = None,
                 size: Union[int, QSize] = 100,
                 radii: Union[int, tuple[int, int, int, int]] = 0,
                 parent=None):
        super().__init__(size, parent)

        # Handle radii parameter
        if isinstance(radii, int):
            self._radii = (radii, radii, radii, radii)
        else:
            self._radii = radii

        # Set initial image if provided
        if image_path:
            self.setImagePath(image_path)

    def setRadii(self, radii: Union[int, tuple[int, int, int, int]]) -> None:
        """Update corner radii and refresh display."""
        if isinstance(radii, int):
            self._radii = (radii, radii, radii, radii)
        else:
            self._radii = radii
        self._refresh_display()

    def _get_shape_params(self) -> tuple:
        return self._radii

    def _apply_shape_mask(self, pixmap: QPixmap) -> QPixmap:
        return img_apply_rounded_mask(pixmap, self._radii)

    def _draw_border(self, painter: QPainter) -> None:
        """Draw rounded rectangle border."""
        if self._border_width <= 0:
            return

        # Create border pen
        pen = QPen(self._border_color, self._border_width)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Calculate border rect (inset by half border width)
        half_border = self._border_width / 2
        border_rect = QRectF(
            half_border, half_border,
            self.width() - self._border_width,
            self.height() - self._border_width
        )

        # Draw rounded rectangle border
        from app.core.utils.image_utils import img_qt_apply_round_path
        border_path = img_qt_apply_round_path(
            int(border_rect.width()),
            int(border_rect.height()),
            self._radii
        )
        border_path.translate(half_border, half_border)
        painter.drawPath(border_path)


# ── Circular Image ──────────────────────────────────────────────────────────────────────────────────────────
class CircularImage(BaseImage):
    """Image widget with perfect circular shape and border support."""

    def __init__(self, diameter: int, parent=None):
        super().__init__(diameter, parent)

    def _get_shape_params(self) -> tuple:
        return ("circular",)  # Unique identifier for circular shape

    def _apply_shape_mask(self, pixmap: QPixmap) -> QPixmap:
        return img_apply_circular_mask(pixmap, self._size)

    def _draw_border(self, painter: QPainter) -> None:
        """Draw circular border."""
        if self._border_width <= 0:
            return

        # Create border pen
        pen = QPen(self._border_color, self._border_width)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Calculate border circle (inset by half border width)
        half_border = self._border_width / 2
        border_rect = QRectF(
            half_border, half_border,
            self._size - self._border_width,
            self._size - self._border_width
        )

        # Draw circular border
        painter.drawEllipse(border_rect)


# ── Recipe Image  ───────────────────────────────────────────────────────────────────────────────────────────
class RecipeImage(RoundedImage):
    """Image widget for displaying recipe images with rounded corners."""

    def __init__(self, image_path: Union[str, Path], size: int = 100,
                 corner_radius: int = 8, parent=None):
        super().__init__(image_path, size, corner_radius, parent)
        self.setImagePath(image_path)
        self.setRadii(corner_radius)


# ── Convenience Factory Functions ───────────────────────────────────────────────────────────────────────────
def create_rounded_image(image_path: Union[str, Path], size: int = 100,
                        corner_radius: int = 8) -> RoundedImage:
    """Convenience function to create a rounded image with uniform corners."""
    return RoundedImage(image_path, size, corner_radius)

def create_circular_image(image_path: Union[str, Path] = None,
                         diameter: int = 100) -> CircularImage:
    """Convenience function to create a circular image."""
    widget = CircularImage(diameter)
    if image_path:
        widget.setImagePath(image_path)
    return widget
