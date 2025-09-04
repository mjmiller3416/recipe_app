"""app/ui/services/navigation_service.py

Route-based NavigationService with enhanced functionality.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QStackedWidget, QWidget

from .navigation_registry import NavigationRegistry, RouteMatch, ViewType
from .navigation_stack import NavigationStackManager, NavigationEntry
from .navigation_views import EmbeddedView, NavigationLifecycle

from _dev_tools import DebugLogger


# ── Errors ──────────────────────────────────────────────────────────────────────────────────────────────────
class NavigationError(Exception):
    """Base exception for navigation errors."""
    pass

class RouteNotFoundError(NavigationError):
    """Raised when a route cannot be found."""
    pass

class NavigationCanceledError(NavigationError):
    """Raised when navigation is canceled by lifecycle hooks."""
    pass


# ── Navigation Service ─────────────────────────────────────────────────────────────────────────────────────
class NavigationContext:
    """Represents a navigation context with its own stack and container."""

    def __init__(self, name: str, container: Optional[QWidget] = None):
        self.name = name
        self.container = container
        self.stack = NavigationStackManager.get_stack(name)
        self.current_view: Optional[QWidget] = None

class NavigationService(QObject):
    """
    Enhanced navigation service with route-based navigation.

    Signals:
        navigation_started: Emitted when navigation begins
        navigation_completed: Emitted when navigation completes successfully
        navigation_failed: Emitted when navigation fails
        route_changed: Emitted when the current route changes
    """

    # Signals
    navigation_started = Signal(str, dict)  # path, params
    navigation_completed = Signal(str, dict)  # path, params
    navigation_failed = Signal(str, str)  # path, error_message
    route_changed = Signal(str, dict)  # path, params

    _instance: Optional['NavigationService'] = None

    def __init__(self):
        super().__init__()
        self._contexts: Dict[str, NavigationContext] = {}
        self._modal_views: List[QDialog] = []
        self._overlay_views: List[QWidget] = []

        # Create main context by default
        self._contexts["main"] = NavigationContext("main")

    @classmethod
    def create(cls, main_container: QStackedWidget) -> 'NavigationService':
        """
        Factory method to create the navigation service.

        Args:
            main_container: Main stacked widget for primary navigation

        Returns:
            NavigationService instance
        """
        instance = cls()
        instance.set_main_container(main_container)
        cls._instance = instance
        return instance

    @classmethod
    def get_instance(cls) -> Optional['NavigationService']:
        """Get the current navigation service instance."""
        return cls._instance

    def set_main_container(self, container: QStackedWidget):
        """
        Set the main container for primary navigation.

        Args:
            container: Main stacked widget
        """
        self._contexts["main"].container = container
        DebugLogger.log("Main navigation container set", "info")

    def add_context(self, name: str, container: Optional[QWidget] = None):
        """
        Add a new navigation context.

        Args:
            name: Context name
            container: Optional container widget for this context
        """
        if name not in self._contexts:
            self._contexts[name] = NavigationContext(name, container)
            DebugLogger.log(f"Added navigation context: {name}", "info")

    def navigate_to(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        context: str = "main",
        replace_current: bool = False,
        **kwargs
    ) -> bool:
        """
        Navigate to a route.

        Args:
            path: Route path to navigate to
            params: Route parameters
            context: Navigation context to use
            replace_current: Whether to replace current history entry
            **kwargs: Additional options passed to view

        Returns:
            True if navigation succeeded, False otherwise
        """
        if params is None:
            params = {}

        try:
            # Emit navigation started
            self.navigation_started.emit(path, params)
            DebugLogger.log(f"Navigation started: {path} (context: {context})", "info")

            # Find matching route
            route_match = NavigationRegistry.match_route(path)
            if not route_match:
                raise RouteNotFoundError(f"No route found for path: {path}")

            # Get navigation context
            if context not in self._contexts:
                self.add_context(context)
            nav_context = self._contexts[context]

            # Handle navigation based on view type
            success = self._handle_navigation(
                route_match, nav_context, params, replace_current, **kwargs
            )

            if success:
                # Add to navigation stack
                nav_context.stack.push(
                    path=path,
                    params=params,
                    replace_current=replace_current
                )

                # Emit completion signals
                self.navigation_completed.emit(path, params)
                self.route_changed.emit(path, params)
                DebugLogger.log(f"Navigation completed: {path}", "info")

            return success

        except Exception as e:
            error_msg = str(e)
            DebugLogger.log(f"Navigation failed: {path} - {error_msg}", "error")
            self.navigation_failed.emit(path, error_msg)
            return False

    def go_back(self, context: str = "main") -> bool:
        """
        Navigate backward in history.

        Args:
            context: Navigation context

        Returns:
            True if backward navigation succeeded
        """
        if context not in self._contexts:
            return False

        nav_context = self._contexts[context]
        prev_entry = nav_context.stack.go_back()

        if prev_entry:
            return self.navigate_to(
                prev_entry.path,
                prev_entry.params,
                context,
                replace_current=True  # Don't add to history again
            )

        return False

    def go_forward(self, context: str = "main") -> bool:
        """
        Navigate forward in history.

        Args:
            context: Navigation context

        Returns:
            True if forward navigation succeeded
        """
        if context not in self._contexts:
            return False

        nav_context = self._contexts[context]
        next_entry = nav_context.stack.go_forward()

        if next_entry:
            return self.navigate_to(
                next_entry.path,
                next_entry.params,
                context,
                replace_current=True  # Don't add to history again
            )

        return False

    def can_go_back(self, context: str = "main") -> bool:
        """Check if backward navigation is possible."""
        if context not in self._contexts:
            return False
        return self._contexts[context].stack.can_go_back()

    def can_go_forward(self, context: str = "main") -> bool:
        """Check if forward navigation is possible."""
        if context not in self._contexts:
            return False
        return self._contexts[context].stack.can_go_forward()

    def get_current_route(self, context: str = "main") -> Optional[NavigationEntry]:
        """
        Get the current navigation entry for a context.

        Args:
            context: Navigation context

        Returns:
            Current navigation entry or None
        """
        if context not in self._contexts:
            return None
        return self._contexts[context].stack.current()

    def get_current_view(self, context: str = "main") -> Optional[QWidget]:
        """
        Get the current view widget for a context.

        Args:
            context: Navigation context

        Returns:
            Current view widget or None
        """
        if context not in self._contexts:
            return None
        return self._contexts[context].current_view

    def close_modals(self):
        """Close all open modal views."""
        for modal in self._modal_views[:]:  # Copy list to avoid modification during iteration
            if modal and not modal.isHidden():
                modal.close()
        self._modal_views.clear()

    def close_overlays(self):
        """Close all open overlay views."""
        for overlay in self._overlay_views[:]:  # Copy list
            if overlay and not overlay.isHidden():
                overlay.close()
        self._overlay_views.clear()

    def _handle_navigation(
        self,
        route_match: RouteMatch,
        nav_context: NavigationContext,
        params: Dict[str, str],
        replace_current: bool,
        **kwargs
    ) -> bool:
        """Handle navigation for different view types."""
        config = route_match.config
        view_type = config.view_type

        # Call before navigation hooks on current view
        if nav_context.current_view and isinstance(nav_context.current_view, NavigationLifecycle):
            if not nav_context.current_view.before_navigate_from(route_match.path, params):
                raise NavigationCanceledError("Navigation canceled by current view")

        # Create new view instance
        view_instance = NavigationRegistry.get_instance(route_match, **kwargs)

        # Call before navigation hooks on new view
        if isinstance(view_instance, NavigationLifecycle):
            if not view_instance.before_navigate_to(route_match.path, params):
                raise NavigationCanceledError("Navigation canceled by target view")

        # Handle based on view type
        if view_type == ViewType.MAIN:
            success = self._handle_main_view(view_instance, nav_context)
        elif view_type == ViewType.MODAL:
            success = self._handle_modal_view(view_instance)
        elif view_type == ViewType.OVERLAY:
            success = self._handle_overlay_view(view_instance)
        elif view_type == ViewType.EMBEDDED:
            success = self._handle_embedded_view(view_instance, nav_context)
        else:
            DebugLogger.log(f"Unknown view type: {view_type}", "error")
            return False

        if success:
            # Call after navigation hooks
            if nav_context.current_view and isinstance(nav_context.current_view, NavigationLifecycle):
                nav_context.current_view.after_navigate_from(route_match.path, params)

            if isinstance(view_instance, NavigationLifecycle):
                view_instance.after_navigate_to(route_match.path, params)

            # Connect view navigation signals
            self._connect_view_signals(view_instance)

        return success

    def _handle_main_view(self, view: QWidget, nav_context: NavigationContext) -> bool:
        """Handle navigation for main views."""
        if not nav_context.container:
            DebugLogger.log("No container set for main navigation context", "error")
            return False

        if isinstance(nav_context.container, QStackedWidget):
            # Add to stacked widget if not already present
            if nav_context.container.indexOf(view) == -1:
                nav_context.container.addWidget(view)
            nav_context.container.setCurrentWidget(view)
        else:
            DebugLogger.log("Main navigation container is not a QStackedWidget", "error")
            return False

        nav_context.current_view = view
        return True

    def _handle_modal_view(self, view: QWidget) -> bool:
        """Handle navigation for modal views."""
        if isinstance(view, QDialog):
            self._modal_views.append(view)
            # Connect close signal to remove from list
            view.finished.connect(lambda: self._modal_views.remove(view) if view in self._modal_views else None)
            view.show()
            return True
        else:
            DebugLogger.log(f"Modal view {view.__class__.__name__} is not a QDialog", "error")
            return False

    def _handle_overlay_view(self, view: QWidget) -> bool:
        """Handle navigation for overlay views."""
        self._overlay_views.append(view)
        # Connect close signal to remove from list
        view.destroyed.connect(lambda: self._overlay_views.remove(view) if view in self._overlay_views else None)
        view.show()
        return True

    def _handle_embedded_view(self, view: QWidget, nav_context: NavigationContext) -> bool:
        """Handle navigation for embedded views."""
        # For embedded views used standalone, treat like main views
        if isinstance(view, EmbeddedView):
            view.set_standalone_mode(True)

        return self._handle_main_view(view, nav_context)

    def _connect_view_signals(self, view: QWidget):
        """Connect view navigation signals to the service."""
        if hasattr(view, 'navigation_requested'):
            view.navigation_requested.connect(
                lambda path, params: self.navigate_to(path, params)
            )

        if hasattr(view, 'close_requested'):
            view.close_requested.connect(view.close)


# ── Helper Functions ────────────────────────────────────────────────────────────────────────────────────────
def navigate_to(path: str, params: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Global navigation function."""
    service = NavigationService.get_instance()
    if service:
        return service.navigate_to(path, params, **kwargs)
    return False


def go_back() -> bool:
    """Global back navigation function."""
    service = NavigationService.get_instance()
    if service:
        return service.go_back()
    return False


def go_forward() -> bool:
    """Global forward navigation function."""
    service = NavigationService.get_instance()
    if service:
        return service.go_forward()
    return False
