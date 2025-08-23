"""app/ui/components/composite/ingredients_preview.py

A compact ingredients preview component that shows a limited number of ingredients
with a hover-triggered overlay displaying the complete list.
"""

from typing import Iterable, Optional

from PySide6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QFrame, QGraphicsOpacityEffect, QGridLayout,
                               QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
                               QWidget)


class IngredientsOverlay(QFrame):
    """Animated overlay showing the complete ingredients list."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientsOverlay")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        
        # Setup overlay styling
        self.setStyleSheet("""
            QFrame#IngredientsOverlay {
                background-color: rgba(27, 29, 35, 0.95);
                border: 1px solid #3A3D46;
                border-radius: 8px;
            }
        """)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(8)
        
        # Header
        header = QLabel("Ingredients")
        header.setObjectName("OverlayHeader")
        header.setStyleSheet("QLabel { color: #6ad7ca; font-weight: bold; font-size: 14px; }")
        self.layout.addWidget(header)
        
        # Ingredients container
        self.ingredients_container = QWidget()
        self.ingredients_layout = QVBoxLayout(self.ingredients_container)
        self.ingredients_layout.setContentsMargins(0, 0, 0, 0)
        self.ingredients_layout.setSpacing(6)
        self.layout.addWidget(self.ingredients_container)
        
        # Setup animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Start hidden
        self.opacity_effect.setOpacity(0.0)
        self.hide()
    
    def setIngredients(self, ingredient_details: Iterable):
        """Set the complete ingredients list for the overlay."""
        # Clear existing ingredients
        while self.ingredients_layout.count():
            child = self.ingredients_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add all ingredients
        for detail in ingredient_details:
            self._addIngredientItem(detail)
    
    def _addIngredientItem(self, detail):
        """Add a single ingredient item to the overlay."""
        item_widget = QWidget()
        item_widget.setObjectName("OverlayIngredientItem")
        
        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setHorizontalSpacing(8)
        item_layout.setVerticalSpacing(0)
        
        # Set column stretch
        item_layout.setColumnStretch(0, 0)  # Quantity
        item_layout.setColumnStretch(1, 0)  # Unit  
        item_layout.setColumnStretch(2, 1)  # Name
        
        # Get ingredient details
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""
        
        # Create labels with overlay styling
        qty_label = QLabel(formatted_qty)
        qty_label.setStyleSheet("QLabel { color: #B0B3B8; font-size: 12px; }")
        qty_label.setMinimumWidth(50)
        qty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        unit_label = QLabel(abbreviated_unit)
        unit_label.setStyleSheet("QLabel { color: #B0B3B8; font-size: 12px; }")
        unit_label.setMinimumWidth(40)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        name_label = QLabel(ingredient_name)
        name_label.setStyleSheet("QLabel { color: #E4E6EA; font-size: 12px; }")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Add to grid
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)
        
        self.ingredients_layout.addWidget(item_widget)
    
    def showOverlay(self, target_pos: QPoint, target_size):
        """Show the overlay with animation at the specified position."""
        # Position the overlay
        self.move(target_pos)
        self.resize(max(300, target_size.width()), min(400, self.sizeHint().height()))
        
        # Show and animate in
        self.show()
        self.raise_()
        
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
    
    def hideOverlay(self):
        """Hide the overlay with animation."""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()


class IngredientsPreview(QWidget):
    """Compact ingredients preview with hover-triggered full list overlay."""
    
    def __init__(self, max_preview_items: int = 5, parent=None):
        super().__init__(parent)
        self.setObjectName("IngredientsPreview")
        self.max_preview_items = max_preview_items
        self.ingredient_details = []
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        
        # Preview container (the hoverable area)
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("IngredientsPreviewFrame")
        self.preview_frame.setAttribute(Qt.WA_Hover, True)
        self.preview_frame.installEventFilter(self)
        
        self.preview_layout = QVBoxLayout(self.preview_frame)
        self.preview_layout.setContentsMargins(8, 8, 8, 8)
        self.preview_layout.setSpacing(4)
        
        self.layout.addWidget(self.preview_frame)
        
        # Create overlay (initially hidden)
        self.overlay = IngredientsOverlay(self.parent() or self)
        
        # "View all" indicator
        self.view_all_label = QLabel()
        self.view_all_label.setObjectName("ViewAllLabel")
        self.view_all_label.setAlignment(Qt.AlignCenter)
        self.view_all_label.setStyleSheet("""
            QLabel {
                color: #6ad7ca;
                font-size: 11px;
                font-style: italic;
                padding: 4px;
            }
        """)
        self.layout.addWidget(self.view_all_label)
        self.view_all_label.hide()
    
    def setIngredients(self, ingredient_details: Iterable):
        """Set the ingredients to display."""
        self.ingredient_details = list(ingredient_details)
        
        # Clear existing preview
        while self.preview_layout.count():
            child = self.preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add preview items (limited number)
        preview_items = self.ingredient_details[:self.max_preview_items]
        for detail in preview_items:
            self._addPreviewItem(detail)
        
        # Show "view all" indicator if there are more items
        remaining_count = len(self.ingredient_details) - len(preview_items)
        if remaining_count > 0:
            self.view_all_label.setText(f"Hover to view {remaining_count} more...")
            self.view_all_label.show()
        else:
            self.view_all_label.hide()
        
        # Update overlay with complete list
        self.overlay.setIngredients(self.ingredient_details)
    
    def _addPreviewItem(self, detail):
        """Add a single ingredient item to the preview."""
        item_widget = QWidget()
        item_widget.setObjectName("PreviewIngredientItem")
        
        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setHorizontalSpacing(6)
        item_layout.setVerticalSpacing(0)
        
        # Set column stretch
        item_layout.setColumnStretch(0, 0)  # Quantity
        item_layout.setColumnStretch(1, 0)  # Unit
        item_layout.setColumnStretch(2, 1)  # Name
        
        # Get ingredient details
        formatted_qty = getattr(detail, 'formatted_quantity', '')
        abbreviated_unit = getattr(detail, 'abbreviated_unit', '')
        ingredient_name = getattr(detail, "ingredient_name", "") or ""
        
        # Create labels
        qty_label = QLabel(formatted_qty)
        qty_label.setObjectName("PreviewQuantity")
        qty_label.setMinimumWidth(40)
        qty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        unit_label = QLabel(abbreviated_unit)
        unit_label.setObjectName("PreviewUnit")
        unit_label.setMinimumWidth(35)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        name_label = QLabel(ingredient_name)
        name_label.setObjectName("PreviewName")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Add to grid
        item_layout.addWidget(qty_label, 0, 0)
        item_layout.addWidget(unit_label, 0, 1)
        item_layout.addWidget(name_label, 0, 2)
        
        self.preview_layout.addWidget(item_widget)
    
    def eventFilter(self, obj, event):
        """Handle hover events on the preview frame."""
        if obj == self.preview_frame:
            if event.type() == QEvent.Enter:
                self._showOverlay()
            elif event.type() == QEvent.Leave:
                self._hideOverlay()
        
        return super().eventFilter(obj, event)
    
    def _showOverlay(self):
        """Show the ingredients overlay."""
        if len(self.ingredient_details) <= self.max_preview_items:
            return  # No need to show overlay if all items are visible
        
        # Calculate overlay position
        frame_rect = self.preview_frame.geometry()
        global_pos = self.mapToGlobal(frame_rect.topLeft())
        
        # Position overlay to the right of the preview frame
        overlay_pos = QPoint(global_pos.x() + frame_rect.width() + 10, global_pos.y())
        
        self.overlay.showOverlay(overlay_pos, frame_rect.size())
    
    def _hideOverlay(self):
        """Hide the ingredients overlay."""
        self.overlay.hideOverlay()