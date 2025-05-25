"""ui/components/widget_frame.py

A container widget that combines QFrame with integrated layout management.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from typing import Union, Optional

class WidgetFrame(QFrame):
    """A QFrame container with integrated layout management.
    
    This class provides a convenient way to create framed containers with
    pre-configured layouts for organizing UI components.
    """
    
    def __init__(self,
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
            layout_type (str): Type of layout ("vertical", "horizontal", "grid")
            frame_shape (QFrame.Shape): Shape of the frame (Box, NoFrame, etc.)
            frame_shadow (QFrame.Shadow): Shadow style of the frame
            line_width (int): Line width for the frame border
            size_policy (tuple): (horizontal, vertical) QSizePolicy values
            margins (tuple): Layout margins (left, top, right, bottom)
            spacing (int): Spacing between layout elements
            parent (QFrame, optional): Parent widget
        """
        super().__init__(parent)
        
        # ── Configure Frame Properties ──
        self.setFrameShape(frame_shape)
        self.setFrameShadow(frame_shadow)
        self.setLineWidth(line_width)
        self.setSizePolicy(*size_policy)
        self.setObjectName("WidgetFrame")
        
        # ── Create and Configure Layout ──
        self._layout = self._create_layout(layout_type)
        self._layout.setContentsMargins(*margins)
        self._layout.setSpacing(spacing)
        self.setLayout(self._layout)
    
    def _create_layout(self, layout_type: str) -> Union[QVBoxLayout, QHBoxLayout, QGridLayout]:
        """Create the specified layout type.
        
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
        """Add a widget to the frame's layout.
        
        Args:
            widget: The widget to add
            *args, **kwargs: Additional arguments passed to the layout's addWidget method
        """
        self._layout.addWidget(widget, *args, **kwargs)
    
    def add_layout(self, layout, *args, **kwargs):
        """Add a layout to the frame's layout.
        
        Args:
            layout: The layout to add
            *args, **kwargs: Additional arguments passed to the layout's addLayout method
        """
        self._layout.addLayout(layout, *args, **kwargs)
    
    def add_stretch(self, stretch: int = 0):
        """Add stretch to the layout (only works with box layouts).
        
        Args:
            stretch (int): Stretch factor
        """
        if hasattr(self._layout, 'addStretch'):
            self._layout.addStretch(stretch)
    
    def get_layout(self) -> Union[QVBoxLayout, QHBoxLayout, QGridLayout]:
        """Get the internal layout object.
        
        Returns:
            The internal layout object
        """
        return self._layout
    
    def set_margins(self, left: int, top: int, right: int, bottom: int):
        """Set the layout margins.
        
        Args:
            left (int): Left margin
            top (int): Top margin
            right (int): Right margin
            bottom (int): Bottom margin
        """
        self._layout.setContentsMargins(left, top, right, bottom)
    
    def set_spacing(self, spacing: int):
        """Set the layout spacing.
        
        Args:
            spacing (int): Spacing between layout elements
        """
        self._layout.setSpacing(spacing)