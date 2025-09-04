"""app/ui/services/registry.py

Route-based navigation registry system for dynamic view registration and management.
"""

from dataclasses import dataclass
from enum import Enum

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import re
from typing import Callable, Dict, List, Optional, Type, TypeVar, Union

from PySide6.QtWidgets import QWidget

from _dev_tools import DebugLogger

T = TypeVar('T', bound=QWidget)


# ── View Types ──────────────────────────────────────────────────────────────────────────────────────────────
class ViewType(Enum):
    """Defines the different types of navigable views."""
    MAIN = "main"           # Full-screen views in main stacked widget
    MODAL = "modal"         # Dialog-style views
    OVERLAY = "overlay"     # Popup-style views
    EMBEDDED = "embedded"   # Components that can be embedded or standalone


# ── Route Configuration ─────────────────────────────────────────────────────────────────────────────────────
@dataclass
class RouteConfig:
    """Configuration for a registered route."""
    path: str
    view_class: Type[QWidget]
    view_type: ViewType
    lazy_load: bool = True
    cached: bool = True
    title: Optional[str] = None
    description: Optional[str] = None

@dataclass
class RouteMatch:
    """Result of route matching with extracted parameters."""
    config: RouteConfig
    params: Dict[str, str]
    path: str

class RouteConstants:
    """Constants for commonly used routes."""

    # Main navigation routes
    DASHBOARD = "/dashboard"
    MEAL_PLANNER = "/meal-planner"
    SHOPPING_LIST = "/shopping-list"
    SETTINGS = "/settings"

    # Recipe routes
    RECIPES_BROWSE = "/recipes/browse"
    RECIPES_ADD = "/recipes/add"
    RECIPES_EDIT = "/recipes/edit/{id}"
    RECIPES_VIEW = "/recipes/view/{id}"

    # Dynamic routes with parameters
    RECIPE_BY_ID = "/recipes/{id}"


# ── Navigation Registry ─────────────────────────────────────────────────────────────────────────────────────
class NavigationRegistry:
    """
    Central registry for route-based navigation.

    Manages route registration, pattern matching, and view instantiation.
    """

    _routes: Dict[str, RouteConfig] = {}
    _pattern_routes: List[RouteConfig] = []
    _instances: Dict[str, QWidget] = {}

    @classmethod
    def register(
        cls,
        path: str,
        view_type: ViewType = ViewType.MAIN,
        lazy_load: bool = True,
        cached: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable[[Type[T]], Type[T]]:
        """
        Decorator to register a view class with a route path.

        Args:
            path: Route path (e.g., '/dashboard', '/recipes/{id}')
            view_type: Type of view (main, modal, overlay, embedded)
            lazy_load: Whether to instantiate only when navigated to
            cached: Whether to cache the instance after first creation
            title: Optional display title for the route
            description: Optional description for the route

        Returns:
            Decorator function that registers the view class
        """
        def decorator(view_class: Type[T]) -> Type[T]:
            cls._register_route(
                path=path,
                view_class=view_class,
                view_type=view_type,
                lazy_load=lazy_load,
                cached=cached,
                title=title,
                description=description
            )
            return view_class
        return decorator

    @classmethod
    def register_route(
        cls,
        path: str,
        view_class: Type[QWidget],
        view_type: ViewType = ViewType.MAIN,
        lazy_load: bool = True,
        cached: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Programmatically register a route without using decorator syntax.

        Args:
            path: Route path (e.g., '/dashboard', '/recipes/{id}')
            view_class: The widget class to instantiate for this route
            view_type: Type of view (main, modal, overlay, embedded)
            lazy_load: Whether to instantiate only when navigated to
            cached: Whether to cache the instance after first creation
            title: Optional display title for the route
            description: Optional description for the route
        """
        cls._register_route(
            path=path,
            view_class=view_class,
            view_type=view_type,
            lazy_load=lazy_load,
            cached=cached,
            title=title,
            description=description
        )

    @classmethod
    def _register_route(
        cls,
        path: str,
        view_class: Type[QWidget],
        view_type: ViewType,
        lazy_load: bool,
        cached: bool,
        title: Optional[str],
        description: Optional[str]
    ):
        """Internal method to register a route configuration."""
        if not path.startswith('/'):
            path = '/' + path

        config = RouteConfig(
            path=path,
            view_class=view_class,
            view_type=view_type,
            lazy_load=lazy_load,
            cached=cached,
            title=title or view_class.__name__,
            description=description
        )

        # Store in appropriate registry
        if cls._has_parameters(path):
            cls._pattern_routes.append(config)
        else:
            cls._routes[path] = config

        DebugLogger.log(f"Registered route: {path} -> {view_class.__name__} ({view_type.value})", "info")

    @classmethod
    def match_route(cls, path: str) -> Optional[RouteMatch]:
        """
        Match a path to a registered route and extract parameters.

        Args:
            path: The path to match (e.g., '/recipes/123')

        Returns:
            RouteMatch object if found, None otherwise
        """
        if not path.startswith('/'):
            path = '/' + path

        # Try exact match first
        if path in cls._routes:
            return RouteMatch(
                config=cls._routes[path],
                params={},
                path=path
            )

        # Try pattern matching
        for config in cls._pattern_routes:
            params = cls._extract_params(config.path, path)
            if params is not None:
                return RouteMatch(
                    config=config,
                    params=params,
                    path=path
                )

        return None

    @classmethod
    def get_instance(cls, route_match: RouteMatch, **kwargs) -> QWidget:
        """
        Get or create a view instance for the matched route.

        Args:
            route_match: The matched route information
            **kwargs: Additional arguments to pass to view constructor

        Returns:
            The view widget instance
        """
        config = route_match.config
        cache_key = f"{config.path}#{hash(frozenset(route_match.params.items()))}"

        # Return cached instance if available and caching is enabled
        if config.cached and cache_key in cls._instances:
            return cls._instances[cache_key]

        # Create new instance
        try:
            instance = config.view_class(**kwargs)

            # Set route information on the instance
            if hasattr(instance, 'set_route_info'):
                instance.set_route_info(route_match.path, route_match.params)

            # Cache if enabled
            if config.cached:
                cls._instances[cache_key] = instance

            DebugLogger.log(f"Created instance for route: {route_match.path}", "info")
            return instance

        except Exception as e:
            DebugLogger.log(f"Error creating instance for route {route_match.path}: {e}", "error")
            raise

    @classmethod
    def clear_cache(cls, path_pattern: Optional[str] = None):
        """
        Clear cached view instances.

        Args:
            path_pattern: Optional pattern to match paths for selective clearing.
                         If None, clears all cached instances.
        """
        if path_pattern is None:
            cls._instances.clear()
            DebugLogger.log("Cleared all navigation cache", "info")
        else:
            to_remove = [
                key for key in cls._instances.keys()
                if key.split('#')[0] == path_pattern
            ]
            for key in to_remove:
                del cls._instances[key]
            DebugLogger.log(f"Cleared cache for pattern: {path_pattern}", "info")

    @classmethod
    def get_routes(cls) -> List[RouteConfig]:
        """Get all registered routes."""
        all_routes = list(cls._routes.values()) + cls._pattern_routes
        return sorted(all_routes, key=lambda r: r.path)

    @classmethod
    def get_routes_by_type(cls, view_type: ViewType) -> List[RouteConfig]:
        """Get all routes of a specific view type."""
        return [route for route in cls.get_routes() if route.view_type == view_type]

    @classmethod
    def _has_parameters(cls, path: str) -> bool:
        """Check if a path contains parameter placeholders."""
        return '{' in path and '}' in path

    @classmethod
    def _extract_params(cls, pattern: str, path: str) -> Optional[Dict[str, str]]:
        """
        Extract parameters from a path using a pattern.

        Args:
            pattern: Route pattern with {param} placeholders
            path: Actual path to extract from

        Returns:
            Dictionary of extracted parameters, or None if no match
        """
        # Convert pattern to regex
        regex_pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', pattern)
        regex_pattern = f'^{regex_pattern}$'

        match = re.match(regex_pattern, path)
        if match:
            return match.groupdict()

        return None



