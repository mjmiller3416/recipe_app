"""RecipeBrowser Package

This package contains the RecipeBrowser view components including the main view,
configuration management, performance optimization utilities, and supporting classes.

Components:
    RecipeBrowser: Main recipe browser view class
    RecipeBrowserConfig: Centralized configuration management
    RecipeCardPool: Object pooling for recipe cards
    ProgressiveRenderer: Progressive rendering for large datasets
    RenderingCoordinator: Recipe-specific rendering coordination
    
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
from .progressive_renderer import ProgressiveRenderer
from .recipe_browser_view import RecipeBrowser
from .recipe_card_pool import RecipeCardPool
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
    "RecipeCardPool",
    "ProgressiveRenderer",
    "RenderingCoordinator",
    "CardInteractionType",
    "RecipeRenderState",
]