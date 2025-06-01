"""ui/components/dialogs/image_crop_dialog.py

A dialog for cropping images to a fixed 300x300 size with an interactive crop area.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QDialogButtonBox, QFrame, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView, QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout, QWidget)

from core.helpers import DebugLogger
from ui.components.dialogs.dialog_window import DialogWindow

# ── Constants ───────────────────────────────────────────────────────────────────
CROP_SIZE = 1024  # Fixed crop size: 300x300


# ── Class Definition ────────────────────────────────────────────────────────────
class CropGraphicsView(QGraphicsView):
    """Custom QGraphicsView for image cropping with draggable crop area."""
    
    crop_changed = Signal(QRect)  # emitted when crop area changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Initialize scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # ── crop area properties ──
        self.crop_rect = QRect(0, 0, CROP_SIZE, CROP_SIZE)
        self.crop_item = None
        self.image_item = None
        self.dragging = False
        self.drag_start_pos = QPoint()
        
        # ── stylesheet ──
        self.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #3B575B;
                border-radius: 8px;
                background-color: #2A2D35;
            }
        """)
    
    def set_image(self, pixmap: QPixmap):
        """Set the image to be cropped."""
        # clear existing items
        self.scene.clear()
        
        # add image to scene
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        
        # calculate initial crop position (center of image)
        image_rect = self.image_item.boundingRect()
        crop_x = max(0, int((image_rect.width() - CROP_SIZE) / 2))
        crop_y = max(0, int((image_rect.height() - CROP_SIZE) / 2))
        
        # ensure crop area doesn't exceed image boundaries
        max_x = max(0, int(image_rect.width() - CROP_SIZE))
        max_y = max(0, int(image_rect.height() - CROP_SIZE))
        crop_x = min(crop_x, max_x)
        crop_y = min(crop_y, max_y)
        
        self.crop_rect = QRect(crop_x, crop_y, CROP_SIZE, CROP_SIZE)
        
        # create crop overlay
        self._create_crop_overlay()
        
        # fit image in view
        self.fitInView(self.image_item, Qt.KeepAspectRatio)
        
        # emit initial crop area
        self.crop_changed.emit(self.crop_rect)
    
    def _create_crop_overlay(self):
        """Create the crop area overlay with darkened outside area."""
        if not self.image_item:
            return
        
        image_rect = self.image_item.boundingRect()
        
        # create darkened overlay for the entire image
        overlay_item = QGraphicsRectItem(image_rect)
        overlay_item.setBrush(QBrush(QColor(0, 0, 0, 120)))  # Semi-transparent black
        overlay_item.setPen(QPen(Qt.NoPen))
        self.scene.addItem(overlay_item)
        
        # create the clear crop area (punch a hole in the overlay)
        crop_clear_item = QGraphicsRectItem(self.crop_rect)
        crop_clear_item.setBrush(QBrush(Qt.NoBrush))
        crop_clear_item.setPen(QPen(QColor("#03B79E"), 3))  # Bright border
        self.scene.addItem(crop_clear_item)
        
        self.crop_item = crop_clear_item
        
        # add corner handles for visual feedback
        self._add_corner_handles()
    
    def _add_corner_handles(self):
        """Add small corner handles to the crop area."""
        handle_size = 8
        handle_color = QColor("#03B79E")
        
        # top-left handle
        handle = QGraphicsRectItem(
            self.crop_rect.x() - handle_size//2,
            self.crop_rect.y() - handle_size//2,
            handle_size, handle_size
        )
        handle.setBrush(QBrush(handle_color))
        handle.setPen(QPen(Qt.NoPen))
        self.scene.addItem(handle)
        
        # top-right handle
        handle = QGraphicsRectItem(
            self.crop_rect.right() - handle_size//2,
            self.crop_rect.y() - handle_size//2,
            handle_size, handle_size
        )
        handle.setBrush(QBrush(handle_color))
        handle.setPen(QPen(Qt.NoPen))
        self.scene.addItem(handle)
        
        # bottom-left handle
        handle = QGraphicsRectItem(
            self.crop_rect.x() - handle_size//2,
            self.crop_rect.bottom() - handle_size//2,
            handle_size, handle_size
        )
        handle.setBrush(QBrush(handle_color))
        handle.setPen(QPen(Qt.NoPen))
        self.scene.addItem(handle)
        
        # bottom-right handle
        handle = QGraphicsRectItem(
            self.crop_rect.right() - handle_size//2,
            self.crop_rect.bottom() - handle_size//2,
            handle_size, handle_size
        )
        handle.setBrush(QBrush(handle_color))
        handle.setPen(QPen(Qt.NoPen))
        self.scene.addItem(handle)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging the crop area."""
        if event.button() == Qt.LeftButton and self.crop_item:
            # convert to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            # check if click is within crop area
            if self.crop_rect.contains(scene_pos.toPoint()):
                self.dragging = True
                self.drag_start_pos = scene_pos.toPoint()
                self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging the crop area."""
        if self.dragging and self.image_item:
            scene_pos = self.mapToScene(event.pos())
            delta = scene_pos.toPoint() - self.drag_start_pos
            
            # calculate new crop position
            new_crop_rect = QRect(
                self.crop_rect.x() + delta.x(),
                self.crop_rect.y() + delta.y(),
                CROP_SIZE, CROP_SIZE
            )
            
            # constrain to image boundaries
            image_rect = self.image_item.boundingRect().toRect()
            
            if new_crop_rect.left() < image_rect.left():
                new_crop_rect.moveLeft(image_rect.left())
            if new_crop_rect.top() < image_rect.top():
                new_crop_rect.moveTop(image_rect.top())
            if new_crop_rect.right() > image_rect.right():
                new_crop_rect.moveRight(image_rect.right())
            if new_crop_rect.bottom() > image_rect.bottom():
                new_crop_rect.moveBottom(image_rect.bottom())
            
            # update crop area if position changed
            if new_crop_rect != self.crop_rect:
                self.crop_rect = new_crop_rect
                self.drag_start_pos = scene_pos.toPoint()
                
                # recreate overlay with new position
                self._create_crop_overlay()
                self.crop_changed.emit(self.crop_rect)
        else:
            # show appropriate cursor based on position
            if self.crop_item:
                scene_pos = self.mapToScene(event.pos())
                if self.crop_rect.contains(scene_pos.toPoint()):
                    self.setCursor(Qt.OpenHandCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def get_crop_rect(self) -> QRect:
        """Get the current crop rectangle."""
        return self.crop_rect


class ImageCropDialog(DialogWindow):
    """Dialog for cropping images to a fixed 300x300 size."""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        
        self.image_path = image_path
        self.cropped_image_path: Optional[str] = None
        
        # setup dialog
        self.setWindowTitle("Crop Image")
        self.setMinimumSize(600, 500)
        self.title_bar.btn_ico_maximize.setVisible(False)
        self.title_bar.btn_ico_toggle_sidebar.setVisible(False)
        
        self._setup_ui()
        self._load_image()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # main layout
        main_layout = QVBoxLayout()
        
        # instructions
        instructions = QLabel(
            f"Position the {CROP_SIZE}×{CROP_SIZE} crop area over the part of the image you want to keep.\n"
            "Drag the highlighted area to reposition it."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            QLabel {
                color: #E1E1E3;
                font-size: 14px;
                padding: 10px;
                background-color: #3A4048;
                border-radius: 6px;
                margin: 5px;
            }
        """)
        main_layout.addWidget(instructions)
        
        # crop view
        self.crop_view = CropGraphicsView()
        self.crop_view.setMinimumHeight(350)
        self.crop_view.crop_changed.connect(self._on_crop_changed)
        main_layout.addWidget(self.crop_view)
        
        # info label
        self.info_label = QLabel(f"Crop area: {CROP_SIZE}×{CROP_SIZE} at (0, 0)")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                font-size: 12px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.info_label)
        
        # buttons
        button_layout = QHBoxLayout()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #5A5A5A;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6A6A6A;
            }
        """)
        
        self.btn_crop = QPushButton("Crop & Use Image")
        self.btn_crop.clicked.connect(self._crop_and_accept)
        self.btn_crop.setStyleSheet("""
            QPushButton {
                background-color: #03B79E;
                color: #1A1A1A;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #04D1B5;
            }
        """)
        self.btn_crop.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_crop)
        
        main_layout.addLayout(button_layout)
        
        self.content_layout.addLayout(main_layout) # add main layout to content area
    
    def _load_image(self):
        """Load the image into the crop view."""
        try:
            pixmap = QPixmap(self.image_path)
            if pixmap.isNull():
                raise ValueError(f"Could not load image: {self.image_path}")
            
            # check if image is large enough for cropping
            if pixmap.width() < CROP_SIZE or pixmap.height() < CROP_SIZE:
                from ui.components.dialogs import MessageDialog
                MessageDialog(
                    "error", 
                    "Image Too Small", 
                    f"Image must be at least {CROP_SIZE}×{CROP_SIZE} pixels.\n"
                    f"Current image is {pixmap.width()}×{pixmap.height()} pixels.",
                    self
                ).exec()
                self.reject()
                return
            
            self.crop_view.set_image(pixmap)
            
        except Exception as e:
            DebugLogger.log(f"Error loading image for cropping: {e}", "error")
            from ui.components.dialogs import MessageDialog
            MessageDialog("error", "Error", f"Failed to load image: {str(e)}", self).exec()
            self.reject()
    
    def _on_crop_changed(self, crop_rect: QRect):
        """Update info label when crop area changes."""
        self.info_label.setText(
            f"Crop area: {CROP_SIZE}×{CROP_SIZE} at ({crop_rect.x()}, {crop_rect.y()})"
        )
    
    def _crop_and_accept(self):
        """Crop the image and accept the dialog."""
        try:
            # load original image
            original_pixmap = QPixmap(self.image_path)
            if original_pixmap.isNull():
                raise ValueError("Could not load original image")
            
            # get crop rectangle
            crop_rect = self.crop_view.get_crop_rect()
            
            # crop the image
            cropped_pixmap = original_pixmap.copy(crop_rect)
            
            # ensure the cropped image is exactly 1024x1024
            if cropped_pixmap.size() != (CROP_SIZE, CROP_SIZE):
                cropped_pixmap = cropped_pixmap.scaled(
                    CROP_SIZE, CROP_SIZE, 
                    Qt.IgnoreAspectRatio, 
                    Qt.SmoothTransformation
                )
            
            # save cropped image to temporary file
            temp_dir = Path(tempfile.gettempdir())
            temp_file = temp_dir / f"recipe_cropped_{Path(self.image_path).stem}.png"
            
            if cropped_pixmap.save(str(temp_file), "PNG"):
                self.cropped_image_path = str(temp_file)
                DebugLogger.log(f"Image cropped and saved to: {self.cropped_image_path}", "info")
                self.accept()
            else:
                raise ValueError("Failed to save cropped image")
                
        except Exception as e:
            DebugLogger.log(f"Error cropping image: {e}", "error")
            from ui.components.dialogs import MessageDialog
            MessageDialog("error", "Error", f"Failed to crop image: {str(e)}", self).exec()
    
    def get_cropped_image_path(self) -> Optional[str]:
        """Get the path to the cropped image."""
        return self.cropped_image_path
