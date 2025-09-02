"""app/ui/services/navigation_views_enhanced.py

Enhanced navigation view classes that include scrollable functionality.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from .navigation_views import NavigationLifecycle, NavigableView, ModalView, OverlayView, EmbeddedView
from .navigation_registry import ViewType
from app.ui.utils.layout_utils import setup_main_scroll_layout
from _dev_tools import DebugLogger


class ScrollableMainView(NavigableView):
    """
    Enhanced MainView with built-in scrollable content support.
    
    Combines the navigation functionality with the ScrollableView pattern.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._view_type = ViewType.MAIN
        self._setup_scroll_layout()
        self._build_ui()
        self._connect_signals()
        
    def _setup_scroll_layout(self):
        """Setup the standard scroll layout - same for all scrollable views."""
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

    @abstractmethod
    def _build_ui(self):
        """Override in subclasses to build view-specific content."""
        raise NotImplementedError("Subclasses must implement _build_ui")

    def _connect_signals(self):
        """Override in subclasses if signal connections are needed."""
        pass

    @property
    def content_layout(self):
        """Get the scroll content layout for adding widgets."""
        return self.scroll_layout


class SimpleMainView(NavigableView):
    """
    Simple MainView without scrollable content.
    
    Use this for views that don't need scrolling or manage their own layouts.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._view_type = ViewType.MAIN


class ScrollableEmbeddedView(EmbeddedView):
    """
    Enhanced EmbeddedView with built-in scrollable content support.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_scroll_layout()
        self._build_ui()
        self._connect_signals()
        
    def _setup_scroll_layout(self):
        """Setup the standard scroll layout."""
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

    @abstractmethod
    def _build_ui(self):
        """Override in subclasses to build view-specific content."""
        raise NotImplementedError("Subclasses must implement _build_ui")

    def _connect_signals(self):
        """Override in subclasses if signal connections are needed."""
        pass

    @property
    def content_layout(self):
        """Get the scroll content layout for adding widgets."""
        return self.scroll_layout


class ScrollableModalView(ModalView):
    """
    Enhanced ModalView with built-in scrollable content support.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_scroll_layout()
        self._build_ui()
        self._connect_signals()
        
    def _setup_scroll_layout(self):
        """Setup the standard scroll layout for modal."""
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

    @abstractmethod
    def _build_ui(self):
        """Override in subclasses to build view-specific content."""
        raise NotImplementedError("Subclasses must implement _build_ui")

    def _connect_signals(self):
        """Override in subclasses if signal connections are needed."""
        pass

    @property
    def content_layout(self):
        """Get the scroll content layout for adding widgets."""
        return self.scroll_layout


# Convenience aliases for backward compatibility
NavigableScrollableView = ScrollableMainView  # For migration
NavigableSimpleView = SimpleMainView         # For migration