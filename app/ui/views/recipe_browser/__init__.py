"""RecipeBrowser Package

This package contains the RecipeBrowser view components including the main view,
configuration management, and supporting classes.

Components:
    RecipeBrowser: Main recipe browser view class
    RecipeBrowserConfig: Centralized configuration management
    RenderingCoordinator: Recipe-specific rendering coordination
    
Note: Object pooling and progressive rendering are now handled by the centralized
PerformanceManager in app.ui.managers.performance.
    
Configuration presets:
    create_default_config: Standard configuration
    create_performance_config: Optimized for performance
    create_quality_config: Optimized for quality
"""

from .config import (
    CacheStrategy,
    RecipeBrowserConfig,
    RenderingMode,
    create_default_config,
    create_performance_config,
    create_quality_config,
)
from .recipe_browser_view import RecipeBrowser
from .rendering_coordinator import (
    CardInteractionType, RecipeRenderState, RenderingCoordinator,
)

__all__ = [
    # Main view
    "RecipeBrowser",
    
    # Configuration
    "RecipeBrowserConfig",
    "create_default_config",
    "create_performance_config",
    "create_quality_config",
    "CacheStrategy",
    "RenderingMode",
    
    # Supporting classes
    "RenderingCoordinator",
    "CardInteractionType",
    "RecipeRenderState",
]