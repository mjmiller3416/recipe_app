"""app/ui/components/images/image_cropper.py

Image cropping tool with interactive rectangle for selecting crop area.
"""
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, Signal, QRect
from PySide6.QtGui import QMouseEvent, QPainter, QPainterPath, QPen, QPixmap, QColor
from PySide6.QtWidgets import QLabel, QSizePolicy
from app.ui.helpers.dialog_helpers import MIN_CROP_DIM_ORIGINAL

# ── Constants ───────────────────────────────────────────────────────────────────
HANDLE_SIZE = 10  # Visual size of resize handles
HANDLE_INTERACTION_OFFSET = 4 # Extend interaction area for handles slightly

class ImageCropper(QLabel):
    """
    A QLabel subclass for displaying an image and handling interactive cropping.
    Draws the image, a draggable and resizable crop rectangle, and handles.
    """
    crop_rect_updated = Signal() # Emitted when the crop rectangle changes

    def __init__(self, original_pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.original_pixmap = original_pixmap
        self.scaled_pixmap = QPixmap()
        self.scale_factor = 1.0
        
        # Crop rectangle in the coordinate system of the scaled_pixmap
        self.crop_rect_on_scaled = QRectF()

        self.handles = {}  # Stores QRectF for handle areas on scaled_pixmap
        self.active_handle_key = None
        self.is_dragging_rect = False
        self.drag_start_mouse_pos = QPointF()
        self.drag_start_crop_rect = QRectF()

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set a minimum size for the cropper area itself
        self.setMinimumSize(MIN_CROP_DIM_ORIGINAL + 40, MIN_CROP_DIM_ORIGINAL + 40)


    def set_original_pixmap(self, pixmap: QPixmap):
        self.original_pixmap = pixmap
        self._update_scaled_pixmap_and_crop_rect() # Recalculate everything

    def _update_scaled_pixmap_and_crop_rect(self):
        if self.original_pixmap.isNull():
            self.scaled_pixmap = QPixmap()
            self.crop_rect_on_scaled = QRectF()
            self.update()
            return

        widget_size = self.size()
        self.scaled_pixmap = self.original_pixmap.scaled(
            widget_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Determine scale factor
        if self.original_pixmap.width() * self.scaled_pixmap.height() > \
           self.original_pixmap.height() * self.scaled_pixmap.width():
            # Limited by widget width
            self.scale_factor = self.scaled_pixmap.width() / self.original_pixmap.width()
        elif self.original_pixmap.height() > 0 : # Avoid division by zero for null pixmap
            # Limited by widget height (or perfect fit)
            self.scale_factor = self.scaled_pixmap.height() / self.original_pixmap.height()
        else:
            self.scale_factor = 1.0
        
        if self.scale_factor == 0 : self.scale_factor = 1.0


        # Initialize crop rectangle
        min_dim_scaled = max(1.0, MIN_CROP_DIM_ORIGINAL * self.scale_factor)
        max_dim_scaled = min(self.scaled_pixmap.width(), self.scaled_pixmap.height())
        
        initial_dim = max(min_dim_scaled, max_dim_scaled * 0.75) # Start at 75% of max possible or min_dim_scaled
        initial_dim = min(initial_dim, max_dim_scaled) # Cannot exceed max_dim_scaled

        crop_x = (self.scaled_pixmap.width() - initial_dim) / 2.0
        crop_y = (self.scaled_pixmap.height() - initial_dim) / 2.0
        self.crop_rect_on_scaled = QRectF(crop_x, crop_y, initial_dim, initial_dim)

        self._update_handles()
        self.update()
        self.crop_rect_updated.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap_and_crop_rect()

    def _get_pixmap_display_rect(self) -> QRect:
        """Returns the QRect where the scaled_pixmap is actually drawn within the widget."""
        if self.scaled_pixmap.isNull():
            return QRect()
        
        x_offset = (self.width() - self.scaled_pixmap.width()) / 2
        y_offset = (self.height() - self.scaled_pixmap.height()) / 2
        return QRect(int(x_offset), int(y_offset), self.scaled_pixmap.width(), self.scaled_pixmap.height())

    def paintEvent(self, event):
        super().paintEvent(event) # Let QLabel draw its background etc.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.scaled_pixmap.isNull():
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Image")
            return

        pixmap_display_rect = self._get_pixmap_display_rect()
        painter.drawPixmap(pixmap_display_rect.topLeft(), self.scaled_pixmap)

        # Crop rect visual is in widget coordinates
        crop_rect_visual = self.crop_rect_on_scaled.translated(pixmap_display_rect.topLeft())

        # Draw semi-transparent overlay outside crop area
        overlay_path = QPainterPath()
        overlay_path.addRect(QRectF(self.rect())) # Whole widget
        overlay_path.addRect(crop_rect_visual) # Subtract crop area
        painter.setBrush(QColor(0, 0, 0, 120)) # Semi-transparent black
        painter.drawPath(overlay_path)

        # Draw crop rectangle border
        pen = QPen(QColor(255, 255, 255, 200), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(crop_rect_visual)

        # Draw resize handles (visual representation)
        painter.setBrush(QColor(255, 255, 255, 220))
        pen.setColor(QColor(50,50,50,180))
        pen.setWidth(1)
        painter.setPen(pen)
        for handle_key in self.handles:
            handle_visual_rect = self.handles[handle_key].translated(pixmap_display_rect.topLeft())
            painter.drawRect(handle_visual_rect)
        
        painter.end()

    def _update_handles(self):
        if self.crop_rect_on_scaled.isNull():
            self.handles = {}
            return
            
        r = self.crop_rect_on_scaled
        hs_v = HANDLE_SIZE # Visual size
        
        # Define visual rects for handles (centered on corners/edges)
        self.handles['tl'] = QRectF(r.left() - hs_v/2, r.top() - hs_v/2, hs_v, hs_v)
        self.handles['tr'] = QRectF(r.right() - hs_v/2, r.top() - hs_v/2, hs_v, hs_v)
        self.handles['bl'] = QRectF(r.left() - hs_v/2, r.bottom() - hs_v/2, hs_v, hs_v)
        self.handles['br'] = QRectF(r.right() - hs_v/2, r.bottom() - hs_v/2, hs_v, hs_v)
        # Add side handles if desired for more complex resizing (though 1:1 makes corners primary)
        # self.handles['t'] = QRectF(r.center().x() - hs_v/2, r.top() - hs_v/2, hs_v, hs_v)
        # self.handles['b'] = QRectF(r.center().x() - hs_v/2, r.bottom() - hs_v/2, hs_v, hs_v)
        # self.handles['l'] = QRectF(r.left() - hs_v/2, r.center().y() - hs_v/2, hs_v, hs_v)
        # self.handles['r'] = QRectF(r.right() - hs_v/2, r.center().y() - hs_v/2, hs_v, hs_v)


    def _get_handle_key_at(self, pos_in_widget: QPointF):
        pixmap_display_rect = self._get_pixmap_display_rect()
        pos_on_scaled_pixmap = pos_in_widget - pixmap_display_rect.topLeft()
        
        # Use a slightly larger interaction area for handles
        offset = HANDLE_INTERACTION_OFFSET
        for key, visual_rect in self.handles.items():
            interaction_rect = visual_rect.adjusted(-offset, -offset, offset, offset)
            if interaction_rect.contains(pos_on_scaled_pixmap):
                return key
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_handle_key = self._get_handle_key_at(event.position())
            pixmap_display_rect = self._get_pixmap_display_rect()
            pos_on_scaled_pixmap = event.position() - pixmap_display_rect.topLeft()

            if self.active_handle_key:
                self.is_dragging_rect = False
            elif self.crop_rect_on_scaled.contains(pos_on_scaled_pixmap):
                self.is_dragging_rect = True
            else: # Clicked outside crop rect and not on a handle
                self.active_handle_key = None
                self.is_dragging_rect = False
                return # Do nothing

            self.drag_start_mouse_pos = pos_on_scaled_pixmap # Store relative to scaled pixmap
            self.drag_start_crop_rect = QRectF(self.crop_rect_on_scaled) # Deep copy
            event.accept()


    def mouseMoveEvent(self, event: QMouseEvent):
        pixmap_display_rect = self._get_pixmap_display_rect()
        current_mouse_pos_on_scaled = event.position() - pixmap_display_rect.topLeft()

        if not (self.is_dragging_rect or self.active_handle_key):
            hover_handle_key = self._get_handle_key_at(event.position())
            if hover_handle_key in ['tl', 'br']: self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif hover_handle_key in ['tr', 'bl']: self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif self.crop_rect_on_scaled.contains(current_mouse_pos_on_scaled): self.setCursor(Qt.CursorShape.SizeAllCursor)
            else: self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if not event.buttons() & Qt.MouseButton.LeftButton:
            self.is_dragging_rect = False
            self.active_handle_key = None
            return

        delta = current_mouse_pos_on_scaled - self.drag_start_mouse_pos
        
        # Get image boundaries and minimum dimension on the scaled pixmap
        img_bounds = QRectF(0, 0, self.scaled_pixmap.width(), self.scaled_pixmap.height())
        min_dim_on_scaled = max(1.0, MIN_CROP_DIM_ORIGINAL * self.scale_factor)
        
        new_rect = QRectF(self.drag_start_crop_rect) # Start with a copy

        if self.is_dragging_rect:
            new_rect.translate(delta)
            # Constrain movement within image bounds
            if new_rect.left() < img_bounds.left(): new_rect.moveLeft(img_bounds.left())
            if new_rect.top() < img_bounds.top(): new_rect.moveTop(img_bounds.top())
            if new_rect.right() > img_bounds.right(): new_rect.moveRight(img_bounds.right())
            if new_rect.bottom() > img_bounds.bottom(): new_rect.moveBottom(img_bounds.bottom())
        
        elif self.active_handle_key:
            # --- Start of Fix ---
            # This new logic proactively calculates constraints.
            
            # Use a copy of the original drag-start rectangle for reference
            start_rect = self.drag_start_crop_rect
            mouse_pos = current_mouse_pos_on_scaled

            if self.active_handle_key == 'br': # Anchor: TopLeft
                anchor = start_rect.topLeft()
                desired_size = max(mouse_pos.x() - anchor.x(), mouse_pos.y() - anchor.y())
                max_allowed_size = min(img_bounds.right() - anchor.x(), img_bounds.bottom() - anchor.y())
                final_size = max(min_dim_on_scaled, min(desired_size, max_allowed_size))
                new_rect = QRectF(anchor, QSizeF(final_size, final_size))

            elif self.active_handle_key == 'tl': # Anchor: BottomRight
                anchor = start_rect.bottomRight()
                desired_size = max(anchor.x() - mouse_pos.x(), anchor.y() - mouse_pos.y())
                max_allowed_size = min(anchor.x() - img_bounds.left(), anchor.y() - img_bounds.top())
                final_size = max(min_dim_on_scaled, min(desired_size, max_allowed_size))
                top_left = QPointF(anchor.x() - final_size, anchor.y() - final_size)
                new_rect = QRectF(top_left, QSizeF(final_size, final_size))

            elif self.active_handle_key == 'tr': # Anchor: BottomLeft
                anchor = start_rect.bottomLeft()
                desired_size = max(mouse_pos.x() - anchor.x(), anchor.y() - mouse_pos.y())
                max_allowed_size = min(img_bounds.right() - anchor.x(), anchor.y() - img_bounds.top())
                final_size = max(min_dim_on_scaled, min(desired_size, max_allowed_size))
                top_left = QPointF(anchor.x(), anchor.y() - final_size)
                new_rect = QRectF(top_left, QSizeF(final_size, final_size))

            elif self.active_handle_key == 'bl': # Anchor: TopRight
                anchor = start_rect.topRight()
                desired_size = max(anchor.x() - mouse_pos.x(), mouse_pos.y() - anchor.y())
                max_allowed_size = min(anchor.x() - img_bounds.left(), img_bounds.bottom() - anchor.y())
                final_size = max(min_dim_on_scaled, min(desired_size, max_allowed_size))
                top_left = QPointF(anchor.x() - final_size, anchor.y())
                new_rect = QRectF(top_left, QSizeF(final_size, final_size))
            # --- End of Fix ---

        # Update the cropper with the new, correctly-constrained rectangle
        self.crop_rect_on_scaled = new_rect.normalized()
        self._update_handles()
        self.update()
        self.crop_rect_updated.emit()
        event.accept()


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging_rect = False
            self.active_handle_key = None
            self.setCursor(Qt.CursorShape.ArrowCursor) # Reset cursor
            event.accept()

    def get_cropped_qpixmap(self) -> QPixmap:
        if self.original_pixmap.isNull() or self.crop_rect_on_scaled.isNull() or self.scale_factor == 0:
            return QPixmap()

        crop_x_orig = self.crop_rect_on_scaled.x() / self.scale_factor
        crop_y_orig = self.crop_rect_on_scaled.y() / self.scale_factor
        crop_w_orig = self.crop_rect_on_scaled.width() / self.scale_factor
        # crop_h_orig will be same as crop_w_orig due to 1:1

        # Ensure dimensions are integers for QRect for .copy()
        rect_on_original = QRect(
            round(crop_x_orig),
            round(crop_y_orig),
            round(crop_w_orig),
            round(crop_w_orig) # Ensure square
        )
        
        # Ensure the crop rect is within the original pixmap bounds
        original_bounds = self.original_pixmap.rect()
        rect_on_original = rect_on_original.intersected(original_bounds)

        if rect_on_original.isEmpty() or rect_on_original.width() < 1 or rect_on_original.height() < 1:
            return QPixmap() # Crop area is invalid or outside image

        return self.original_pixmap.copy(rect_on_original)