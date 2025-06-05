# ui/dialogs/recipe_image_crop_dialog.py

# ── Imports ─────────────────────────────────────────────────────────────────────
import tempfile
import uuid
from pathlib import Path

from PySide6.QtCore import (Qt, Signal, QRect, QPoint, QSize, Slot, QRectF, 
                            QPointF, QSizeF)
from PySide6.QtGui import (QPixmap, QPainter, QPen, QBrush, QColor, QMouseEvent,
                           QPainterPath, QCursor)
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QFrame, QSpacerItem)

from ui.components.dialogs.dialog_window import DialogWindow 
from core.helpers.debug_logger import DebugLogger

# ── Constants ───────────────────────────────────────────────────────────────────
MIN_CROP_DIM_ORIGINAL = 280  # Minimum crop dimension on the original image
HANDLE_SIZE = 10  # Visual size of resize handles
HANDLE_INTERACTION_OFFSET = 4 # Extend interaction area for handles slightly

class CropperLabel(QLabel):
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
            # Add other cursor shapes for side handles if implemented
            elif self.crop_rect_on_scaled.contains(current_mouse_pos_on_scaled): self.setCursor(Qt.CursorShape.SizeAllCursor)
            else: self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if not event.buttons() & Qt.MouseButton.LeftButton: # Should not happen if logic is correct
            self.is_dragging_rect = False
            self.active_handle_key = None
            return

        delta = current_mouse_pos_on_scaled - self.drag_start_mouse_pos
        new_rect = QRectF(self.drag_start_crop_rect) # Work on a copy

        min_dim_on_scaled = max(1.0, MIN_CROP_DIM_ORIGINAL * self.scale_factor)
        max_dim_on_scaled = min(self.scaled_pixmap.width(), self.scaled_pixmap.height())
        
        # Image boundaries for the crop rectangle
        img_bounds = QRectF(0, 0, self.scaled_pixmap.width(), self.scaled_pixmap.height())

        if self.is_dragging_rect:
            new_rect.translate(delta)
            # Constrain movement within image bounds
            if new_rect.left() < img_bounds.left(): new_rect.moveLeft(img_bounds.left())
            if new_rect.top() < img_bounds.top(): new_rect.moveTop(img_bounds.top())
            if new_rect.right() > img_bounds.right(): new_rect.moveRight(img_bounds.right())
            if new_rect.bottom() > img_bounds.bottom(): new_rect.moveBottom(img_bounds.bottom())
        
        elif self.active_handle_key:
            # For 1:1 aspect ratio, corner drags determine the new size.
            # The change (dx, dy) is applied, then the dimension is made square.
            # The anchor point is the corner opposite to the handle.
            
            current_size = 0
            if self.active_handle_key == 'br': # Anchor: tl
                new_rect.setBottomRight(self.drag_start_crop_rect.topLeft() + delta)
                current_size = max(new_rect.width(), new_rect.height())
                new_rect.setWidth(current_size)
                new_rect.setHeight(current_size)
            elif self.active_handle_key == 'tl': # Anchor: br
                new_rect.setTopLeft(self.drag_start_crop_rect.bottomRight() + delta)
                current_size = max(new_rect.width(), new_rect.height())
                new_rect.setTopLeft(new_rect.bottomRight() - QPointF(current_size, current_size)) # Keep br fixed
            elif self.active_handle_key == 'tr': # Anchor: bl
                new_rect.setTopRight(self.drag_start_crop_rect.bottomLeft() + delta)
                current_size = max(new_rect.width(), new_rect.height())
                new_rect.setTopRight(QPointF(new_rect.left() + current_size, new_rect.top())) # fix y, adjust x
                new_rect.setHeight(current_size) # fix x, adjust y to match width
            elif self.active_handle_key == 'bl': # Anchor: tr
                new_rect.setBottomLeft(self.drag_start_crop_rect.topRight() + delta)
                current_size = max(new_rect.width(), new_rect.height())
                new_rect.setBottomLeft(QPointF(new_rect.right() - current_size, new_rect.top()))
                new_rect.setHeight(current_size)

            # Normalize (ensure positive width/height)
            new_rect = new_rect.normalized()

            # Clamp size
            current_dim = new_rect.width() # Should be square
            clamped_dim = max(min_dim_on_scaled, min(current_dim, max_dim_on_scaled))
            
            # Re-anchor if size was clamped
            if abs(clamped_dim - current_dim) > 1e-3: # If clamping changed size significantly
                if self.active_handle_key == 'br': new_rect.setSize(QSizeF(clamped_dim, clamped_dim)) # TL anchor
                elif self.active_handle_key == 'tl': # BR anchor
                    old_br = new_rect.bottomRight()
                    new_rect.setTopLeft(old_br - QPointF(clamped_dim, clamped_dim))
                    new_rect.setSize(QSizeF(clamped_dim, clamped_dim))
                elif self.active_handle_key == 'tr': # BL anchor
                    old_bl = new_rect.bottomLeft()
                    new_rect.setTopRight(old_bl + QPointF(clamped_dim, -clamped_dim)) # Y is inverted for TR from BL
                    new_rect.setSize(QSizeF(clamped_dim, clamped_dim))
                    new_rect.moveTop(old_bl.y() - clamped_dim) # Correct top after setting size from BL
                elif self.active_handle_key == 'bl': # TR anchor
                    old_tr = new_rect.topRight()
                    new_rect.setBottomLeft(old_tr + QPointF(-clamped_dim, clamped_dim))
                    new_rect.setSize(QSizeF(clamped_dim, clamped_dim))
                    new_rect.moveLeft(old_tr.x() - clamped_dim)

            # Boundary checks after resize (can be complex if aspect ratio fixed)
            # Simple push-in:
            if new_rect.left() < img_bounds.left(): new_rect.moveLeft(img_bounds.left())
            if new_rect.top() < img_bounds.top(): new_rect.moveTop(img_bounds.top())
            if new_rect.right() > img_bounds.right(): new_rect.moveRight(img_bounds.right())
            if new_rect.bottom() > img_bounds.bottom(): new_rect.moveBottom(img_bounds.bottom())

            # After boundary push, re-ensure squareness and min/max constraints
            final_dim = min(new_rect.width(), new_rect.height()) # In case boundary push deformed it
            final_dim = max(min_dim_on_scaled, min(final_dim, max_dim_on_scaled))
            
            # Re-anchor based on handle to maintain its position relative to mouse if possible
            if self.active_handle_key == 'br': new_rect.setSize(QSizeF(final_dim, final_dim))
            elif self.active_handle_key == 'tl': new_rect.setTopLeft(QPointF(new_rect.right() - final_dim, new_rect.bottom() - final_dim))
            elif self.active_handle_key == 'tr': new_rect.setTopRight(QPointF(new_rect.left() + final_dim, new_rect.bottom() - final_dim))
            elif self.active_handle_key == 'bl': new_rect.setBottomLeft(QPointF(new_rect.right() - final_dim, new_rect.top() + final_dim))
            new_rect.setWidth(final_dim) # Ensure width and height are set
            new_rect.setHeight(final_dim)


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


class RecipeImageCropDialog(DialogWindow): # Inherit from your BaseDialog or QDialog
    # Emits the QPixmap of the cropped image area
    crop_finalized = Signal(QPixmap)
    # Emitted if the user wants to choose a different image file
    select_new_image_requested = Signal()

    # Custom result code for "Select New Image"
    SelectNewImageCode = QDialog.DialogCode.Rejected + 1 

    def __init__(self, image_path: str, parent=None):
        super().__init__(width=800, height=800, title="Crop Recipe Image", parent=parent)

        self.initial_image_path = image_path
        self.original_pixmap = QPixmap(image_path)

        if self.original_pixmap.isNull():
            print(f"Error: Could not load image from {image_path}")

        self._build_ui() 
        self._connect_signals()
        
        self.cropper_label.set_original_pixmap(self.original_pixmap)


    def _build_ui(self):
        """Builds the UI layout for the crop dialog."""
        # ── Instructions ──
        self.instruction_label = QLabel(
            "Adjust the square selection to choose your crop area.\n"
            "Minimum crop size is 280x280 pixels."
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.content_layout.addWidget(self.instruction_label) 

        # ── Cropper Area ──
        cropper_frame = QFrame()
        cropper_frame.setFrameShape(QFrame.Shape.StyledPanel)
        cropper_layout = QVBoxLayout(cropper_frame) # layout for the frame itself
        cropper_layout.setContentsMargins(0,0,0,0)
        
        self.cropper_label = CropperLabel(self.original_pixmap)
        cropper_layout.addWidget(self.cropper_label)
        
        self.content_layout.addWidget(cropper_frame, 1) # add frame to self.content_layout

        # ── Buttons ──
        self.buttons_layout = QHBoxLayout() 
        self.buttons_layout.setSpacing(10)

        self.btn_select_new = QPushButton("Select New Image")
        self.btn_select_new.setObjectName("SelectNewButton")

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("CancelButton")

        self.btn_save = QPushButton("Save Crop")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.setDefault(True)

        self.buttons_layout.addWidget(self.btn_select_new)
        self.buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.buttons_layout.addWidget(self.btn_cancel)
        self.buttons_layout.addWidget(self.btn_save)
        
        self.content_layout.addLayout(self.buttons_layout) #

    def _connect_signals(self):
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject) # QDialog's reject slot
        self.btn_select_new.clicked.connect(self._on_select_new)

    @Slot()
    def _on_save(self):
        cropped_pixmap = self.cropper_label.get_cropped_qpixmap()
        if not cropped_pixmap.isNull():
            # Validate final size against original minimum
            if cropped_pixmap.width() < MIN_CROP_DIM_ORIGINAL or cropped_pixmap.height() < MIN_CROP_DIM_ORIGINAL:
                 # This check should ideally be implicitly handled by cropper logic,
                 # but as a final validation:
                # msg_box = QMessageBox(self)
                # msg_box.setIcon(QMessageBox.Warning)
                # msg_box.setText(f"The selected crop ({cropped_pixmap.width()}x{cropped_pixmap.height()}) is smaller than the minimum allowed size of {MIN_CROP_DIM_ORIGINAL}x{MIN_CROP_DIM_ORIGINAL} pixels.")
                # msg_box.setWindowTitle("Crop Too Small")
                # msg_box.setStandardButtons(QMessageBox.Ok)
                # msg_box.exec()
                # return # Keep dialog open
                # Or, up-sample if that's desired (generally not for quality)
                pass # Assume cropper logic enforced this

            self.crop_finalized.emit(cropped_pixmap)
            self.accept() # QDialog's accept slot
        else:
            # Handle error - e.g., show a message
            print("Error: Could not get a valid cropped image.")
            # Potentially show a QMessageBox to the user

    @Slot()
    def _on_select_new(self):
        self.select_new_image_requested.emit()
        # Close this dialog with a custom code, or just reject.
        # If UploadRecipeImage handles the signal by re-opening file dialog,
        # then this dialog just needs to close.
        self.done(RecipeImageCropDialog.SelectNewImageCode)

    # Optional: Method to get the pixmap if not using signals for some reason
    def get_final_cropped_pixmap(self) -> QPixmap:
        return self.cropper_label.get_cropped_qpixmap()

    # Override showEvent to ensure the pixmap is scaled correctly after layout adjustments
    def showEvent(self, event):
        super().showEvent(event)
        # Ensures the cropper label has its final size before initial scaling
        if not self.original_pixmap.isNull():
             self.cropper_label._update_scaled_pixmap_and_crop_rect()