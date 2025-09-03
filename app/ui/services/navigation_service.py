"""app/ui/services/navigation_service.py

Navigation service for managing view navigation and routing.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from enum import Enum, auto
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget


# ── Navigation Types & Models ───────────────────────────────────────────────────────────────────────────────
class ViewType(Enum):
    """Types of views in the application"""
    MAIN = auto()      # Sidebar-accessible views
    SUB = auto()       # Child views (FullRecipe, etc.)
    DIALOG = auto()    # Modal dialogs
    TEMP = auto()      # Temporary instances (edit forms)

class NavigationMode(Enum):
    """How the navigation should behave"""
    PUSH = auto()      # Add to stack
    REPLACE = auto()   # Replace current
    MODAL = auto()     # Open as modal
    EMBEDDED = auto()  # Embedded within parent

@dataclass
class Route:
    """Definition of a navigable route"""
    name: str
    view_class: type
    view_type: ViewType
    sidebar_visible: bool = False
    requires_auth: bool = False
    cache_instance: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NavigationContext:
    """Context passed during navigation"""
    from_route: Optional[str] = None
    to_route: str = None
    params: Dict[str, Any] = field(default_factory=dict)
    mode: NavigationMode = NavigationMode.PUSH
    caller: Optional[str] = None  # Track who called this view


# ── Base Navigable View ─────────────────────────────────────────────────────────────────────────────────────
class NavigableView(QObject):
    """Base class for all navigable views"""

    # Lifecycle signals
    before_enter = Signal(dict)  # Params dict
    after_enter = Signal()
    before_leave = Signal()
    after_leave = Signal()

    def __init__(self, navigation_service=None, parent=None):
        super().__init__(parent)
        self.navigation_service = navigation_service
        self._view_state = {}

    # Lifecycle hooks (override in subclasses)
    def on_before_enter(self, params: Dict[str, Any]) -> bool:
        """Called before view is shown. Return False to cancel navigation."""
        return True

    def on_enter(self, params: Dict[str, Any]):
        """Called when view is entered with navigation params"""
        pass

    def on_before_leave(self) -> bool:
        """Called before leaving view. Return False to cancel (e.g., unsaved changes)."""
        return True

    def on_leave(self):
        """Called when view is being left"""
        pass

    def on_resume(self):
        """Called when returning to this view from another"""
        pass

    def save_state(self) -> Dict[str, Any]:
        """Save view state for restoration"""
        return self._view_state

    def restore_state(self, state: Dict[str, Any]):
        """Restore previously saved state"""
        self._view_state = state

# ============= Route Registry =============

class RouteRegistry:
    """Central registry for all application routes"""

    _routes: Dict[str, Route] = {}

    @classmethod
    def register(cls,
                 name: str,
                 view_type: ViewType = ViewType.MAIN,
                 sidebar_visible: bool = False,
                 cache_instance: bool = True,
                 **metadata):
        """Decorator to register a view class as a route"""
        def decorator(view_class):
            route = Route(
                name=name,
                view_class=view_class,
                view_type=view_type,
                sidebar_visible=sidebar_visible,
                cache_instance=cache_instance,
                metadata=metadata
            )
            cls._routes[name] = route
            view_class.route_name = name  # Add route name to class
            return view_class
        return decorator

    @classmethod
    def get_route(cls, name: str) -> Optional[Route]:
        return cls._routes.get(name)

    @classmethod
    def get_sidebar_routes(cls) -> List[Route]:
        """Get all routes that should appear in sidebar"""
        return [r for r in cls._routes.values() if r.sidebar_visible]

    @classmethod
    def get_all_routes(cls) -> Dict[str, Route]:
        return cls._routes.copy()

# ── Navigation Service ──────────────────────────────────────────────────────────────────────────────────────

class NavigationService(QObject):
    """Core navigation service managing all view transitions"""

    # Navigation events
    navigation_started = Signal(NavigationContext)
    navigation_completed = Signal(NavigationContext)
    navigation_failed = Signal(str)  # Error message

    def __init__(self, stack_widget: QStackedWidget, parent=None):
        super().__init__(parent)
        self.stack_widget = stack_widget
        self.history: List[NavigationContext] = []
        self.view_instances: Dict[str, NavigableView] = {}
        self.current_route: Optional[str] = None

        # Service coordinators
        self.interceptors: List[Callable] = []
        self.service_handlers: Dict[str, Callable] = {}

    def navigate_to(self,
                   route_name: str,
                   params: Optional[Dict[str, Any]] = None,
                   mode: NavigationMode = NavigationMode.PUSH,
                   caller: Optional[str] = None) -> bool:
        """Navigate to a route with optional parameters"""

        route = RouteRegistry.get_route(route_name)
        if not route:
            self.navigation_failed.emit(f"Route '{route_name}' not found")
            return False

        # Create navigation context
        context = NavigationContext(
            from_route=self.current_route,
            to_route=route_name,
            params=params or {},
            mode=mode,
            caller=caller or self.current_route
        )

        # Run interceptors (e.g., check unsaved changes)
        if not self._run_interceptors(context):
            return False

        # Handle current view exit
        if self.current_route:
            if not self._handle_view_exit(self.current_route):
                return False

        # Get or create view instance
        view = self._get_or_create_view(route)

        # Handle view entry
        if not self._handle_view_entry(view, context):
            return False

        # Update stack widget
        self._update_stack(view, mode)

        # Update state
        self.current_route = route_name
        if mode == NavigationMode.PUSH:
            self.history.append(context)
        elif mode == NavigationMode.REPLACE and self.history:
            self.history[-1] = context

        # Trigger any registered service handlers
        self._trigger_services(context)

        self.navigation_completed.emit(context)
        return True

    def go_back(self) -> bool:
        """Navigate to previous view in history"""
        if len(self.history) <= 1:
            return False

        # Remove current from history
        self.history.pop()

        # Get previous context
        prev_context = self.history[-1]

        # Navigate to it (without adding to history again)
        return self.navigate_to(
            prev_context.to_route,
            prev_context.params,
            NavigationMode.REPLACE
        )

    def register_interceptor(self, interceptor: Callable[[NavigationContext], bool]):
        """Register a navigation interceptor (e.g., unsaved changes check)"""
        self.interceptors.append(interceptor)

    def register_service_handler(self, route_name: str, handler: Callable):
        """Register a service to be triggered on navigation to a route"""
        self.service_handlers[route_name] = handler

    # ============= Private Methods =============

    def _get_or_create_view(self, route: Route) -> NavigableView:
        """Get existing or create new view instance"""
        if route.cache_instance and route.name in self.view_instances:
            return self.view_instances[route.name]

        # Create new instance
        view = route.view_class(navigation_service=self)

        if route.cache_instance:
            self.view_instances[route.name] = view

        return view

    def _handle_view_exit(self, route_name: str) -> bool:
        """Handle view exit lifecycle"""
        if route_name not in self.view_instances:
            return True

        view = self.view_instances[route_name]

        # Check if view allows exit
        if not view.on_before_leave():
            return False

        view.before_leave.emit()
        view.on_leave()
        view.after_leave.emit()

        # Save state if needed
        route = RouteRegistry.get_route(route_name)
        if route and route.cache_instance:
            view.save_state()

        return True

    def _handle_view_entry(self, view: NavigableView, context: NavigationContext) -> bool:
        """Handle view entry lifecycle"""
        # Check if view allows entry
        if not view.on_before_enter(context.params):
            return False

        view.before_enter.emit(context.params)
        view.on_enter(context.params)
        view.after_enter.emit()

        return True

    def _update_stack(self, view: NavigableView, mode: NavigationMode):
        """Update the stack widget based on navigation mode"""
        if mode in [NavigationMode.PUSH, NavigationMode.REPLACE]:
            # Check if view is already in stack
            index = self.stack_widget.indexOf(view)
            if index == -1:
                # Add to stack
                index = self.stack_widget.addWidget(view)

            # Set as current
            self.stack_widget.setCurrentIndex(index)

    def _run_interceptors(self, context: NavigationContext) -> bool:
        """Run all registered interceptors"""
        for interceptor in self.interceptors:
            if not interceptor(context):
                return False
        return True

    def _trigger_services(self, context: NavigationContext):
        """Trigger any registered service handlers"""
        if context.to_route in self.service_handlers:
            handler = self.service_handlers[context.to_route]
            handler(context)
