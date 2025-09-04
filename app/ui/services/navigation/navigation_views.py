"""app/ui/services/navigation_views.py

Base view classes for the route-based navigation system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from enum import Enum

from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import QDialog, QWidget

from .navigation_registry import ViewType, NavigationRegistry
from .navigation_stack import NavigationStackManager
from _dev_tools import DebugLogger


T = TypeVar('T', bound='NavigableView')


class NavigationLifecycle:
    """Defines the navigation lifecycle hook methods."""

    def before_navigate_to(self, path: str, params: Dict[str, str]) -> bool:
        """
        Called before navigating to this view.

        Args:
            path: The route path being navigated to
            params: Route parameters

        Returns:
            True to allow navigation, False to cancel
        """
        return True

    def after_navigate_to(self, path: str, params: Dict[str, str]):
        """
        Called after successfully navigating to this view.

        Args:
            path: The route path that was navigated to
            params: Route parameters
        """
        pass

    def before_navigate_from(self, next_path: str, next_params: Dict[str, str]) -> bool:
        """
        Called before navigating away from this view.

        Args:
            next_path: The route path being navigated to
            next_params: Route parameters for next view

        Returns:
            True to allow navigation, False to cancel
        """
        return True

    def after_navigate_from(self, next_path: str, next_params: Dict[str, str]):
        """
        Called after successfully navigating away from this view.

        Args:
            next_path: The route path that was navigated to
            next_params: Route parameters for next view
        """
        pass


class NavigableView(QWidget, NavigationLifecycle):
    """
    Base class for all navigable views.

    Provides common navigation functionality and lifecycle hooks.
    """

    # Signals
    navigation_requested = Signal(str, dict)  # path, params
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path: Optional[str] = None
        self._current_params: Dict[str, str] = {}
        self._navigation_data: Dict[str, Any] = {}
        self._view_type = ViewType.MAIN

    def set_route_info(self, path: str, params: Dict[str, str]):
        """
        Set the current route information for this view.

        Args:
            path: Current route path
            params: Route parameters
        """
        self._current_path = path
        self._current_params = params.copy()
        self.on_route_changed(path, params)

    def get_current_path(self) -> Optional[str]:
        """Get the current route path."""
        return self._current_path

    def get_current_params(self) -> Dict[str, str]:
        """Get the current route parameters."""
        return self._current_params.copy()

    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Get a specific route parameter value.

        Args:
            key: Parameter key
            default: Default value if key not found

        Returns:
            Parameter value or default
        """
        return self._current_params.get(key, default)

    def set_navigation_data(self, key: str, value: Any):
        """
        Set navigation-specific data for this view.

        Args:
            key: Data key
            value: Data value
        """
        self._navigation_data[key] = value

    def get_navigation_data(self, key: str, default: Any = None) -> Any:
        """
        Get navigation-specific data for this view.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        return self._navigation_data.get(key, default)

    def navigate_to(self, path: str, params: Optional[Dict[str, str]] = None, **kwargs):
        """
        Request navigation to another route.

        Args:
            path: Target route path
            params: Route parameters
            **kwargs: Additional navigation options
        """
        if params is None:
            params = {}

        # Add any additional kwargs as navigation data
        if kwargs:
            params.update(kwargs)

        DebugLogger.log(f"Navigation requested from {self.__class__.__name__}: {path}", "info")
        self.navigation_requested.emit(path, params)

    def go_back(self):
        """Request backward navigation."""
        from .navigation_service import NavigationService
        nav_service = NavigationService.get_instance()
        if nav_service:
            nav_service.go_back()

    def go_forward(self):
        """Request forward navigation."""
        from .navigation_service import NavigationService
        nav_service = NavigationService.get_instance()
        if nav_service:
            nav_service.go_forward()

    def close_view(self):
        """Request to close this view."""
        DebugLogger.log(f"Close requested for {self.__class__.__name__}", "info")
        self.close_requested.emit()

    def on_route_changed(self, path: str, params: Dict[str, str]):
        """
        Called when the route information changes.
        Override in subclasses to handle route-specific initialization.

        Args:
            path: New route path
            params: New route parameters
        """
        pass


class MainView(NavigableView):
    """
    Base class for main application views.

    These are full-screen views displayed in the main stacked widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._view_type = ViewType.MAIN


class ModalView(QDialog, NavigationLifecycle):
    """
    Base class for modal dialog views.

    These are dialog-style views that appear over the main application.
    """

    # Signals
    navigation_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path: Optional[str] = None
        self._current_params: Dict[str, str] = {}
        self._navigation_data: Dict[str, Any] = {}
        self._view_type = ViewType.MODAL

        # Set modal properties
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def set_route_info(self, path: str, params: Dict[str, str]):
        """Set the current route information for this view."""
        self._current_path = path
        self._current_params = params.copy()
        self.on_route_changed(path, params)

    def get_current_path(self) -> Optional[str]:
        """Get the current route path."""
        return self._current_path

    def get_current_params(self) -> Dict[str, str]:
        """Get the current route parameters."""
        return self._current_params.copy()

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get a specific route parameter value."""
        return self._current_params.get(key, default)

    def navigate_to(self, path: str, params: Optional[Dict[str, str]] = None, **kwargs):
        """Request navigation to another route."""
        if params is None:
            params = {}
        if kwargs:
            params.update(kwargs)

        DebugLogger.log(f"Navigation requested from modal {self.__class__.__name__}: {path}", "info")
        self.navigation_requested.emit(path, params)

    def on_route_changed(self, path: str, params: Dict[str, str]):
        """Called when the route information changes."""
        pass


class OverlayView(NavigableView):
    """
    Base class for overlay views.

    These are popup-style views that appear over other content.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._view_type = ViewType.OVERLAY

        # Set overlay properties
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose, True)


class EmbeddedView(NavigableView):
    """
    Base class for embedded views.

    These are components that can be embedded in other views or used standalone.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._view_type = ViewType.EMBEDDED
        self._is_standalone = False

    def set_standalone_mode(self, standalone: bool):
        """
        Set whether this view is being used in standalone mode.

        Args:
            standalone: True if used as standalone view, False if embedded
        """
        self._is_standalone = standalone
        self.on_standalone_changed(standalone)

    def is_standalone(self) -> bool:
        """Check if this view is in standalone mode."""
        return self._is_standalone

    def on_standalone_changed(self, standalone: bool):
        """
        Called when standalone mode changes.
        Override in subclasses to adjust behavior.

        Args:
            standalone: New standalone mode
        """
        pass


class ViewFactory:
    """Factory for creating view instances with proper setup."""

    @staticmethod
    def create_view(view_class: Type[T], **kwargs) -> T:
        """
        Create a view instance with proper initialization.

        Args:
            view_class: The view class to instantiate
            **kwargs: Arguments to pass to the constructor

        Returns:
            Initialized view instance
        """
        instance = view_class(**kwargs)

        # Set up navigation connections if it's a navigable view
        if isinstance(instance, (NavigableView, ModalView)):
            # Connect navigation requests to the navigation service
            # This will be handled by the NavigationService when it's created
            pass

        return instance


# ── Helper Functions ────────────────────────────────────────────────────────────────────────────────────────
def register_view(
    path: str,
    view_type: ViewType = ViewType.MAIN,
    **kwargs
):
    """
    Decorator to register a view class with the navigation system.

    Args:
        path: Route path
        view_type: Type of view
        **kwargs: Additional registration options

    Returns:
        Decorator function
    """
    return NavigationRegistry.register(path=path, view_type=view_type, **kwargs)
