"""app/ui/components/images/image_cropper.py

Refactored image cropping components with separation of concerns.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QPointF, QRect, QRectF, QSizeF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from app.core.utils.image_utils import (
    img_calc_scale_factor, img_crop_from_scaled_coords, img_scale_to_fit
)
from app.ui.helpers.dialog_helpers import MIN_CROP_DIM_ORIGINAL


# ── Constants ────────────────────────────────────────────────────────────────────────────────
HANDLE_SIZE = 10
HANDLE_INTERACTION_OFFSET = 4


# ── Crop Rectangle State Manager ─────────────────────────────────────────────────────────────
class CropRectangle:
    """Manages crop rectangle state and transformations."""

    def __init__(self):
        self.rect = QRectF()
        self.handles = {}

    def initialize_for_image(self, scaled_pixmap: QPixmap, scale_factor: float):
        """Initialize crop rectangle for given image dimensions."""
        min_dim_scaled = max(1.0, MIN_CROP_DIM_ORIGINAL * scale_factor)
        max_dim_scaled = min(scaled_pixmap.width(), scaled_pixmap.height())

        initial_dim = max(min_dim_scaled, max_dim_scaled * 0.75)
        initial_dim = min(initial_dim, max_dim_scaled)

        crop_x = (scaled_pixmap.width() - initial_dim) / 2.0
        crop_y = (scaled_pixmap.height() - initial_dim) / 2.0

        self.rect = QRectF(crop_x, crop_y, initial_dim, initial_dim)
        self._update_handles()

    def _update_handles(self):
        """Update handle positions based on current rectangle."""
        if self.rect.isNull():
            self.handles = {}
            return

        r = self.rect
        hs = HANDLE_SIZE / 2

        self.handles = {
            'tl': QRectF(r.left() - hs, r.top() - hs, HANDLE_SIZE, HANDLE_SIZE),
            'tr': QRectF(r.right() - hs, r.top() - hs, HANDLE_SIZE, HANDLE_SIZE),
            'bl': QRectF(r.left() - hs, r.bottom() - hs, HANDLE_SIZE, HANDLE_SIZE),
            'br': QRectF(r.right() - hs, r.bottom() - hs, HANDLE_SIZE, HANDLE_SIZE),
        }

    def get_handle_at_pos(self, pos: QPointF) -> str:
        """Get handle key at given position, or None."""
        offset = HANDLE_INTERACTION_OFFSET
        for key, handle_rect in self.handles.items():
            interaction_rect = handle_rect.adjusted(-offset, -offset, offset, offset)
            if interaction_rect.contains(pos):
                return key
        return None

    def contains_point(self, pos: QPointF) -> bool:
        """Check if position is inside crop rectangle."""
        return self.rect.contains(pos)

    def move_by_delta(self, delta: QPointF, bounds: QRectF):
        """Move rectangle by delta, constraining within bounds."""
        new_rect = QRectF(self.rect).translated(delta)

        # Constrain within bounds
        if new_rect.left() < bounds.left():
            new_rect.moveLeft(bounds.left())
        if new_rect.top() < bounds.top():
            new_rect.moveTop(bounds.top())
        if new_rect.right() > bounds.right():
            new_rect.moveRight(bounds.right())
        if new_rect.bottom() > bounds.bottom():
            new_rect.moveBottom(bounds.bottom())

        self.rect = new_rect
        self._update_handles()

    def resize_from_handle(self, handle_key: str, mouse_pos: QPointF,
                          start_rect: QRectF, bounds: QRectF, min_size: float):
        """Resize rectangle from handle position."""
        if handle_key == 'br':  # Bottom-right handle
            anchor = start_rect.topLeft()
            desired_size = max(mouse_pos.x() - anchor.x(), mouse_pos.y() - anchor.y())
            max_size = min(bounds.right() - anchor.x(), bounds.bottom() - anchor.y())
            final_size = max(min_size, min(desired_size, max_size))
            self.rect = QRectF(anchor, QSizeF(final_size, final_size))

        elif handle_key == 'tl':  # Top-left handle
            anchor = start_rect.bottomRight()
            desired_size = max(anchor.x() - mouse_pos.x(), anchor.y() - mouse_pos.y())
            max_size = min(anchor.x() - bounds.left(), anchor.y() - bounds.top())
            final_size = max(min_size, min(desired_size, max_size))
            top_left = QPointF(anchor.x() - final_size, anchor.y() - final_size)
            self.rect = QRectF(top_left, QSizeF(final_size, final_size))

        elif handle_key == 'tr':  # Top-right handle
            anchor = start_rect.bottomLeft()
            desired_size = max(mouse_pos.x() - anchor.x(), anchor.y() - mouse_pos.y())
            max_size = min(bounds.right() - anchor.x(), anchor.y() - bounds.top())
            final_size = max(min_size, min(desired_size, max_size))
            top_left = QPointF(anchor.x(), anchor.y() - final_size)
            self.rect = QRectF(top_left, QSizeF(final_size, final_size))

        elif handle_key == 'bl':  # Bottom-left handle
            anchor = start_rect.topRight()
            desired_size = max(anchor.x() - mouse_pos.x(), mouse_pos.y() - anchor.y())
            max_size = min(anchor.x() - bounds.left(), bounds.bottom() - anchor.y())
            final_size = max(min_size, min(desired_size, max_size))
            top_left = QPointF(anchor.x() - final_size, anchor.y())
            self.rect = QRectF(top_left, QSizeF(final_size, final_size))

        self._update_handles()


# ── Mouse Interaction Handler ────────────────────────────────────────────────────────────────
class CropInteractionHandler:
    """Handles mouse interactions for cropping."""

    def __init__(self, crop_rect: CropRectangle):
        self.crop_rect = crop_rect
        self.active_handle = None
        self.is_dragging = False
        self.drag_start_pos = QPointF()
        self.drag_start_rect = QRectF()

    def handle_mouse_press(self, pos_on_image: QPointF) -> bool:
        """Handle mouse press. Returns True if interaction started."""
        self.active_handle = self.crop_rect.get_handle_at_pos(pos_on_image)

        if self.active_handle:
            self.is_dragging = False
        elif self.crop_rect.contains_point(pos_on_image):
            self.is_dragging = True
            self.active_handle = None
        else:
            return False  # No interaction

        self.drag_start_pos = pos_on_image
        self.drag_start_rect = QRectF(self.crop_rect.rect)
        return True

    def handle_mouse_move(self, pos_on_image: QPointF, bounds: QRectF,
                         scale_factor: float) -> bool:
        """Handle mouse move. Returns True if crop changed."""
        if not (self.is_dragging or self.active_handle):
            return False

        if self.is_dragging:
            delta = pos_on_image - self.drag_start_pos
            self.crop_rect.move_by_delta(delta, bounds)
            return True

        elif self.active_handle:
            min_size = max(1.0, MIN_CROP_DIM_ORIGINAL * scale_factor)
            self.crop_rect.resize_from_handle(
                self.active_handle, pos_on_image,
                self.drag_start_rect, bounds, min_size
            )
            return True

        return False

    def handle_mouse_release(self):
        """Handle mouse release."""
        self.is_dragging = False
        self.active_handle = None

    def get_cursor_for_pos(self, pos_on_image: QPointF) -> Qt.CursorShape:
        """Get appropriate cursor for position."""
        if self.is_dragging or self.active_handle:
            return Qt.CursorShape.ArrowCursor

        handle = self.crop_rect.get_handle_at_pos(pos_on_image)
        if handle in ['tl', 'br']:
            return Qt.CursorShape.SizeFDiagCursor
        elif handle in ['tr', 'bl']:
            return Qt.CursorShape.SizeBDiagCursor
        elif self.crop_rect.contains_point(pos_on_image):
            return Qt.CursorShape.SizeAllCursor
        else:
            return Qt.CursorShape.ArrowCursor


# ── Crop Renderer ────────────────────────────────────────────────────────────────────────────
class CropRenderer:
    """Handles rendering of crop overlay and handles."""

    @staticmethod
    def draw_crop_overlay(painter: QPainter, widget_rect: QRect,
                         crop_visual_rect: QRectF, crop_rect: CropRectangle,
                         pixmap_display_rect: QRect):
        """Draw the crop overlay with darkened areas and handles."""
        # Semi-transparent overlay outside crop area
        overlay_path = QPainterPath()
        overlay_path.addRect(QRectF(widget_rect))
        overlay_path.addRect(crop_visual_rect)
        painter.setBrush(QColor(0, 0, 0, 120))
        painter.setPen(Qt.NoPen)
        painter.drawPath(overlay_path)

        # Crop rectangle border
        pen = QPen(QColor(255, 255, 255, 200), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(crop_visual_rect)

        # Draw resize handles
        painter.setBrush(QColor(255, 255, 255, 220))
        pen.setColor(QColor(50, 50, 50, 180))
        pen.setWidth(1)
        painter.setPen(pen)

        for handle_rect in crop_rect.handles.values():
            visual_handle = handle_rect.translated(pixmap_display_rect.topLeft())
            painter.drawRect(visual_handle)


# ── Main ImageCropper Widget ─────────────────────────────────────────────────────────────────
class ImageCropper(QLabel):
    """Interactive image cropper with drag-and-resize functionality."""

    crop_rect_updated = Signal()

    def __init__(self, original_pixmap: QPixmap, parent=None):
        super().__init__(parent)

        # Image state
        self.original_pixmap = original_pixmap
        self.scaled_pixmap = QPixmap()
        self.scale_factor = 1.0

        # Components
        self.crop_rect = CropRectangle()
        self.interaction_handler = CropInteractionHandler(self.crop_rect)

        # Widget setup
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(MIN_CROP_DIM_ORIGINAL + 40, MIN_CROP_DIM_ORIGINAL + 40)

        self._update_scaled_pixmap_and_crop_rect()

    def set_original_pixmap(self, pixmap: QPixmap):
        """Set new original pixmap and recalculate everything."""
        self.original_pixmap = pixmap
        self._update_scaled_pixmap_and_crop_rect()

    def get_cropped_qpixmap(self) -> QPixmap:
        """Get cropped result using utility function."""
        return img_crop_from_scaled_coords(
            self.original_pixmap,
            self.crop_rect.rect,
            self.scale_factor,
            force_square=True
        )

    def _update_scaled_pixmap_and_crop_rect(self):
        """Update scaled pixmap and initialize crop rectangle."""
        if self.original_pixmap.isNull():
            self.scaled_pixmap = QPixmap()
            self.crop_rect.rect = QRectF()
            self.update()
            return

        # Scale image to fit widget
        self.scaled_pixmap = img_scale_to_fit(
            self.original_pixmap,
            self.size().width(),
            self.size().height()
        )

        # Calculate scale factor
        self.scale_factor = img_calc_scale_factor(self.original_pixmap, self.scaled_pixmap)
        if self.scale_factor == 0:
            self.scale_factor = 1.0

        # Initialize crop rectangle
        self.crop_rect.initialize_for_image(self.scaled_pixmap, self.scale_factor)

        self.update()
        self.crop_rect_updated.emit()

    def _get_pixmap_display_rect(self) -> QRect:
        """Get rectangle where scaled pixmap is displayed in widget."""
        if self.scaled_pixmap.isNull():
            return QRect()

        x_offset = (self.width() - self.scaled_pixmap.width()) / 2
        y_offset = (self.height() - self.scaled_pixmap.height()) / 2
        return QRect(int(x_offset), int(y_offset),
                    self.scaled_pixmap.width(), self.scaled_pixmap.height())

    # ── Event Handlers ──
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap_and_crop_rect()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.scaled_pixmap.isNull():
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Image")
            return

        # Draw image
        pixmap_display_rect = self._get_pixmap_display_rect()
        painter.drawPixmap(pixmap_display_rect.topLeft(), self.scaled_pixmap)

        # Draw crop overlay
        crop_visual_rect = self.crop_rect.rect.translated(pixmap_display_rect.topLeft())
        CropRenderer.draw_crop_overlay(
            painter, self.rect(), crop_visual_rect,
            self.crop_rect, pixmap_display_rect
        )

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        pixmap_display_rect = self._get_pixmap_display_rect()
        pos_on_image = event.position() - pixmap_display_rect.topLeft()

        if self.interaction_handler.handle_mouse_press(pos_on_image):
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pixmap_display_rect = self._get_pixmap_display_rect()
        pos_on_image = event.position() - pixmap_display_rect.topLeft()

        # Update cursor
        cursor = self.interaction_handler.get_cursor_for_pos(pos_on_image)
        self.setCursor(cursor)

        # Handle interaction
        if event.buttons() & Qt.MouseButton.LeftButton:
            bounds = QRectF(0, 0, self.scaled_pixmap.width(), self.scaled_pixmap.height())
            if self.interaction_handler.handle_mouse_move(pos_on_image, bounds, self.scale_factor):
                self.update()
                self.crop_rect_updated.emit()
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.interaction_handler.handle_mouse_release()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
