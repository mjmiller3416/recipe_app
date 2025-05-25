"""ui/components/widget_frame.py

A container widget that combines QFrame with integrated layout management and optional header.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QLabel, QWidget
from PySide6.QtCore import Qt
from typing import Union, Optional

class WidgetFrame(QFrame):
    """A QFrame container with integrated layout management and optional header.
    
    This class provides a convenient way to create framed containers with
    pre-configured layouts and an optional header section for organizing UI components.
    """
    
    def __init__(self,
                 header_text: Optional[str] = None,
                 layout_type: str = "vertical",
                 frame_shape: QFrame.Shape = QFrame.Box,
                 frame_shadow: QFrame.Shadow = QFrame.Plain,
                 line_width: int = 1,
                 size_policy: tuple = (QSizePolicy.Expanding, QSizePolicy.Expanding),
                 margins: tuple = (0, 0, 0, 0),
                 spacing: int = 0,
                 parent: Optional[QFrame] = None):
        """Initialize the WidgetFrame.
        
        Args:
            header_text (str, optional): Text for the header label. If None, no header is created.
            layout_type (str): Type of layout for content area ("vertical", "horizontal", "grid")
            frame_shape (QFrame.Shape): Shape of the frame (Box, NoFrame, etc.)
            frame_shadow (QFrame.Shadow): Shadow style of the frame
            line_width (int): Line width for the frame border
            size_policy (tuple): (horizontal, vertical) QSizePolicy values
            margins (tuple): Layout margins for content area (left, top, right, bottom)
            spacing (int): Spacing between layout elements in content area
            parent (QFrame, optional): Parent widget
        """
        super().__init__(parent)
        
        # ── Configure Frame Properties ──
        self.setFrameShape(frame_shape)
        self.setFrameShadow(frame_shadow)
        self.setLineWidth(line_width)
        self.setSizePolicy(*size_policy)
        self.setObjectName("WidgetFrame")
        
        # ── Create Main Layout ──
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # ── Create Header (if requested) ──
        self._header_label = None
        if header_text:
            self._create_header(header_text)
        
        # ── Create Content Area ──
        self._content_widget = QWidget()
        self._content_widget.setObjectName("WidgetFrameContent")
        self._content_layout = self._create_layout(layout_type)
        self._content_layout.setContentsMargins(*margins)
        self._content_layout.setSpacing(spacing)
        self._content_widget.setLayout(self._content_layout)
        
        self._main_layout.addWidget(self._content_widget)
    
    def _create_header(self, header_text: str):
        """Create the header section with label.
        
        Args:
            header_text (str): Text for the header label
        """
        self._header_label = QLabel(header_text)
        self._header_label.setObjectName("WidgetFrameHeader")
        self._header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._main_layout.addWidget(self._header_label)
    
    def _create_layout(self, layout_type: str) -> Union[QVBoxLayout, QHBoxLayout, QGridLayout]:
        """Create the specified layout type for the content area.
        
        Args:
            layout_type (str): Type of layout to create
            
        Returns:
            The created layout object
            
        Raises:
            ValueError: If layout_type is not supported
        """
        layout_map = {
            "vertical": QVBoxLayout,
            "horizontal": QHBoxLayout,
            "grid": QGridLayout
        }
        
        if layout_type not in layout_map:
            raise ValueError(f"Unsupported layout type: {layout_type}. "
                           f"Supported types: {list(layout_map.keys())}")
        
        return layout_map[layout_type]()
    
    def add_widget(self, widget, *args, **kwargs):
        """Add a widget to the frame's content layout.
        
        Args:
            widget: The widget to add
            *args, **kwargs: Additional arguments passed to the layout's addWidget method
        """
        self._content_layout.addWidget(widget, *args, **kwargs)
    
    def add_layout(self, layout, *args, **kwargs):
        """Add a layout to the frame's content layout.
        
        Args:
            layout: The layout to add
            *args, **kwargs: Additional arguments passed to the layout's addLayout method
        """
        self._content_layout.addLayout(layout, *args, **kwargs)
    
    def add_stretch(self, stretch: int = 0):
        """Add stretch to the content layout (only works with box layouts).
        
        Args:
            stretch (int): Stretch factor
        """
        if hasattr(self._content_layout, 'addStretch'):
            self._content_layout.addStretch(stretch)
    
    def get_layout(self) -> Union[QVBoxLayout, QHBoxLayout, QGridLayout]:
        """Get the internal content layout object.
        
        Returns:
            The internal content layout object
        """
        return self._content_layout
    
    def get_header_label(self) -> Optional[QLabel]:
        """Get the header label widget.
        
        Returns:
            The header label widget or None if no header was created
        """
        return self._header_label
    
    def set_header_text(self, text: str):
        """Set the header text.
        
        Args:
            text (str): New header text
        """
        if self._header_label:
            self._header_label.setText(text)
    
    def set_margins(self, left: int, top: int, right: int, bottom: int):
        """Set the content layout margins.
        
        Args:
            left (int): Left margin
            top (int): Top margin
            right (int): Right margin
            bottom (int): Bottom margin
        """
        self._content_layout.setContentsMargins(left, top, right, bottom)
    
    def set_spacing(self, spacing: int):
        """Set the content layout spacing.
        
        Args:
            spacing (int): Spacing between layout elements
        """
        self._content_layout.setSpacing(spacing)