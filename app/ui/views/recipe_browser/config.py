"""app/ui/views/recipe_browser/config.py

Centralized configuration management for the RecipeBrowser view component.
This module provides type-safe configuration with validation, environment overrides,
and performance tuning parameters for the recipe browsing functionality.

The RecipeBrowserConfig class consolidates all behavioral parameters that were
previously scattered throughout the view implementation, providing a single source
of truth for configuration values.

Classes:
    RecipeBrowserConfig: Main configuration dataclass with validation
    PerformanceConfig: Nested configuration for performance tuning
    FeatureFlags: Feature toggle configuration
    DisplayConfig: Display and layout configuration

Example:
    # Default configuration
    config = RecipeBrowserConfig()

    # Custom configuration
    config = RecipeBrowserConfig(
        batch_size=12,
        progressive_rendering_enabled=False
    )

    # Validation
    config.validate()  # Raises ValueError if invalid
"""

from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Optional

from app.ui.components.composite.recipe_card import LayoutSize
from app.config import SORT_OPTIONS

# ── Configuration Enums ──────────────────────────────────────────────────────────────────────────────────────
class CacheStrategy(Enum):
    """Cache strategy options for recipe data."""
    NONE = "none"           # No caching
    MEMORY = "memory"        # In-memory caching only
    AGGRESSIVE = "aggressive"  # Aggressive caching with longer TTL


class RenderingMode(Enum):
    """Rendering mode options for recipe display."""
    IMMEDIATE = "immediate"     # Render all items immediately
    PROGRESSIVE = "progressive"  # Progressive/lazy rendering
    VIRTUAL = "virtual"         # Virtual scrolling (future)


# ── Nested Configuration Classes ─────────────────────────────────────────────────────────────────────────────
@dataclass
class PerformanceConfig:
    """Performance tuning configuration for RecipeBrowser.

    These settings control resource usage and rendering behavior to optimize
    performance based on the deployment environment and dataset size.
    """
    # Rendering settings
    progressive_rendering_enabled: bool = True
    batch_size: int = 8                    # Items per render batch
    render_delay_ms: int = 16              # Delay between batches (target 60fps)

    # Object pooling settings
    card_pool_size: int = 30               # Maximum pooled card instances
    pool_preload_count: int = 10           # Cards to pre-create on init

    # Memory management
    max_cached_images: int = 50            # Maximum cached recipe images
    cache_strategy: CacheStrategy = CacheStrategy.MEMORY
    cache_ttl_seconds: int = 300           # Cache time-to-live

    # Performance thresholds
    slow_render_threshold_ms: float = 100.0  # Log warning if render exceeds
    max_concurrent_loads: int = 3            # Max concurrent image loads

    def validate(self) -> None:
        """Validate performance configuration values."""
        if self.batch_size < 1 or self.batch_size > 50:
            raise ValueError(f"batch_size must be between 1 and 50, got {self.batch_size}")

        if self.card_pool_size < self.batch_size:
            raise ValueError(f"card_pool_size ({self.card_pool_size}) must be >= batch_size ({self.batch_size})")

        if self.render_delay_ms < 0 or self.render_delay_ms > 1000:
            raise ValueError(f"render_delay_ms must be between 0 and 1000, got {self.render_delay_ms}")

        if self.cache_ttl_seconds < 0:
            raise ValueError(f"cache_ttl_seconds must be non-negative, got {self.cache_ttl_seconds}")


@dataclass
class DisplayConfig:
    """Display and layout configuration for RecipeBrowser."""
    # Layout settings
    default_card_size: LayoutSize = LayoutSize.MEDIUM
    card_spacing: int = 10                 # Pixels between cards
    content_margins: tuple[int, int, int, int] = (0, 0, 0, 0)  # LTRB margins

    # Grid settings
    min_columns: int = 1                   # Minimum grid columns
    max_columns: int = 6                   # Maximum grid columns
    responsive_layout: bool = True         # Auto-adjust columns to width

    # Animation settings
    enable_animations: bool = True         # Enable UI animations
    animation_duration_ms: int = 250       # Standard animation duration

    # Scroll settings
    smooth_scrolling: bool = True          # Enable smooth scroll
    scroll_per_pixel: bool = True          # Pixel-perfect scrolling

    def validate(self) -> None:
        """Validate display configuration values."""
        if self.min_columns < 1 or self.min_columns > self.max_columns:
            raise ValueError(f"Invalid column range: min={self.min_columns}, max={self.max_columns}")

        if self.card_spacing < 0 or self.card_spacing > 100:
            raise ValueError(f"card_spacing must be between 0 and 100, got {self.card_spacing}")


@dataclass
class InteractionConfig:
    """User interaction configuration for RecipeBrowser."""
    # Debouncing settings
    filter_debounce_delay_ms: int = 250    # Delay for filter changes
    search_debounce_delay_ms: int = 300    # Delay for search input
    resize_debounce_delay_ms: int = 50     # Delay for resize events

    # Selection behavior
    multi_select_enabled: bool = False     # Allow multiple selections
    selection_persist_navigation: bool = False  # Keep selection on navigation

    # Click behavior
    double_click_to_open: bool = False     # Require double-click to open
    right_click_menu: bool = True          # Enable context menu

    # Keyboard navigation
    keyboard_navigation_enabled: bool = True  # Arrow key navigation
    tab_navigation_enabled: bool = True       # Tab key navigation

    def validate(self) -> None:
        """Validate interaction configuration values."""
        if self.filter_debounce_delay_ms < 0 or self.filter_debounce_delay_ms > 2000:
            raise ValueError(f"filter_debounce_delay_ms must be between 0 and 2000, got {self.filter_debounce_delay_ms}")

        if self.search_debounce_delay_ms < 0 or self.search_debounce_delay_ms > 2000:
            raise ValueError(f"search_debounce_delay_ms must be between 0 and 2000, got {self.search_debounce_delay_ms}")


@dataclass
class FeatureFlags:
    """Feature toggle configuration for RecipeBrowser.

    These flags control optional features that can be enabled/disabled
    without code changes, useful for A/B testing and gradual rollouts.
    """
    # Core features
    enable_progressive_rendering: bool = True
    enable_object_pooling: bool = True
    enable_cache: bool = True

    # Performance monitoring
    enable_performance_monitoring: bool = True
    enable_render_timing: bool = True
    enable_cache_metrics: bool = True

    # Advanced features
    enable_virtual_scrolling: bool = False  # Future feature
    enable_infinite_scroll: bool = False    # Future feature
    enable_prefetching: bool = False        # Future feature

    # Debug features
    enable_debug_overlay: bool = False      # Show performance overlay
    enable_verbose_logging: bool = False    # Extra debug logging

    def validate(self) -> None:
        """Validate feature flags (currently no validation needed)."""
        pass


@dataclass
class DefaultsConfig:
    """Default values configuration for RecipeBrowser."""
    # Filter defaults
    default_sort_option: str = "A-Z"
    default_category: str = "All"
    default_favorites_only: bool = False

    # Display defaults
    default_view_mode: str = "grid"        # grid, list, tiles
    default_items_per_page: int = 20       # For pagination

    # Search defaults
    default_search_scope: str = "all"      # all, name, ingredients
    case_sensitive_search: bool = False

    def validate(self) -> None:
        """Validate defaults configuration."""
        if self.default_sort_option not in SORT_OPTIONS:
            raise ValueError(f"Invalid default_sort_option: {self.default_sort_option}. Valid options: {SORT_OPTIONS}")

        valid_view_modes = ["grid", "list", "tiles"]
        if self.default_view_mode not in valid_view_modes:
            raise ValueError(f"Invalid default_view_mode: {self.default_view_mode}")


# ── Main Configuration Class ─────────────────────────────────────────────────────────────────────────────────
@dataclass
class RecipeBrowserConfig:
    """Centralized configuration for RecipeBrowser view.

    This class consolidates all configuration parameters for the RecipeBrowser view,
    providing type safety, validation, and environment override support.

    Configuration can be customized through:
    1. Direct instantiation with custom values
    2. Environment variables (prefixed with RECIPE_BROWSER_)
    3. Configuration files (future enhancement)

    Attributes:
        performance: Performance tuning parameters
        display: Display and layout settings
        interaction: User interaction behavior
        features: Feature toggle flags
        defaults: Default values for filters and display

    Example:
        config = RecipeBrowserConfig()
        config.validate()  # Ensure all values are valid

        # Access nested configuration
        batch_size = config.performance.batch_size
        card_size = config.display.default_card_size
    """

    # Nested configuration objects
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    interaction: InteractionConfig = field(default_factory=InteractionConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)

    # Top-level settings
    enable_telemetry: bool = False         # Send anonymous usage stats
    config_version: str = "1.0.0"          # Configuration schema version

    def __post_init__(self):
        """Apply environment variable overrides after initialization."""
        self._apply_environment_overrides()

    def _apply_environment_overrides(self):
        """Apply configuration overrides from environment variables.

        Environment variables are prefixed with RECIPE_BROWSER_ and use
        double underscores for nested values.

        Examples:
            RECIPE_BROWSER_PERFORMANCE__BATCH_SIZE=12
            RECIPE_BROWSER_FEATURES__ENABLE_CACHE=false
        """
        # Performance overrides
        if batch_size := os.getenv("RECIPE_BROWSER_PERFORMANCE__BATCH_SIZE"):
            self.performance.batch_size = int(batch_size)

        if pool_size := os.getenv("RECIPE_BROWSER_PERFORMANCE__CARD_POOL_SIZE"):
            self.performance.card_pool_size = int(pool_size)

        if progressive := os.getenv("RECIPE_BROWSER_PERFORMANCE__PROGRESSIVE_RENDERING_ENABLED"):
            self.performance.progressive_rendering_enabled = progressive.lower() in ("true", "1", "yes")

        # Display overrides
        if card_size := os.getenv("RECIPE_BROWSER_DISPLAY__DEFAULT_CARD_SIZE"):
            try:
                self.display.default_card_size = LayoutSize[card_size.upper()]
            except KeyError:
                pass  # Invalid value, keep default

        # Interaction overrides
        if debounce := os.getenv("RECIPE_BROWSER_INTERACTION__FILTER_DEBOUNCE_DELAY_MS"):
            self.interaction.filter_debounce_delay_ms = int(debounce)

        # Feature flag overrides
        if enable_cache := os.getenv("RECIPE_BROWSER_FEATURES__ENABLE_CACHE"):
            self.features.enable_cache = enable_cache.lower() in ("true", "1", "yes")

        if enable_monitoring := os.getenv("RECIPE_BROWSER_FEATURES__ENABLE_PERFORMANCE_MONITORING"):
            self.features.enable_performance_monitoring = enable_monitoring.lower() in ("true", "1", "yes")

        # Defaults overrides
        if sort_option := os.getenv("RECIPE_BROWSER_DEFAULTS__DEFAULT_SORT_OPTION"):
            self.defaults.default_sort_option = sort_option

    def validate(self) -> None:
        """Validate all configuration values.

        Raises:
            ValueError: If any configuration value is invalid
        """
        # Validate nested configurations
        self.performance.validate()
        self.display.validate()
        self.interaction.validate()
        self.features.validate()
        self.defaults.validate()

        # Cross-configuration validation
        if self.features.enable_progressive_rendering and not self.performance.progressive_rendering_enabled:
            raise ValueError("Feature flag enable_progressive_rendering requires performance.progressive_rendering_enabled")

        if self.features.enable_object_pooling and self.performance.card_pool_size < 1:
            raise ValueError("Feature flag enable_object_pooling requires card_pool_size >= 1")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary for serialization.

        Returns:
            dict: Configuration as nested dictionary
        """
        return {
            "performance": {
                "progressive_rendering_enabled": self.performance.progressive_rendering_enabled,
                "batch_size": self.performance.batch_size,
                "render_delay_ms": self.performance.render_delay_ms,
                "card_pool_size": self.performance.card_pool_size,
                "pool_preload_count": self.performance.pool_preload_count,
                "max_cached_images": self.performance.max_cached_images,
                "cache_strategy": self.performance.cache_strategy.value,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "slow_render_threshold_ms": self.performance.slow_render_threshold_ms,
                "max_concurrent_loads": self.performance.max_concurrent_loads,
            },
            "display": {
                "default_card_size": self.display.default_card_size.name,
                "card_spacing": self.display.card_spacing,
                "content_margins": self.display.content_margins,
                "min_columns": self.display.min_columns,
                "max_columns": self.display.max_columns,
                "responsive_layout": self.display.responsive_layout,
                "enable_animations": self.display.enable_animations,
                "animation_duration_ms": self.display.animation_duration_ms,
                "smooth_scrolling": self.display.smooth_scrolling,
                "scroll_per_pixel": self.display.scroll_per_pixel,
            },
            "interaction": {
                "filter_debounce_delay_ms": self.interaction.filter_debounce_delay_ms,
                "search_debounce_delay_ms": self.interaction.search_debounce_delay_ms,
                "resize_debounce_delay_ms": self.interaction.resize_debounce_delay_ms,
                "multi_select_enabled": self.interaction.multi_select_enabled,
                "selection_persist_navigation": self.interaction.selection_persist_navigation,
                "double_click_to_open": self.interaction.double_click_to_open,
                "right_click_menu": self.interaction.right_click_menu,
                "keyboard_navigation_enabled": self.interaction.keyboard_navigation_enabled,
                "tab_navigation_enabled": self.interaction.tab_navigation_enabled,
            },
            "features": {
                "enable_progressive_rendering": self.features.enable_progressive_rendering,
                "enable_object_pooling": self.features.enable_object_pooling,
                "enable_cache": self.features.enable_cache,
                "enable_performance_monitoring": self.features.enable_performance_monitoring,
                "enable_render_timing": self.features.enable_render_timing,
                "enable_cache_metrics": self.features.enable_cache_metrics,
                "enable_virtual_scrolling": self.features.enable_virtual_scrolling,
                "enable_infinite_scroll": self.features.enable_infinite_scroll,
                "enable_prefetching": self.features.enable_prefetching,
                "enable_debug_overlay": self.features.enable_debug_overlay,
                "enable_verbose_logging": self.features.enable_verbose_logging,
            },
            "defaults": {
                "default_sort_option": self.defaults.default_sort_option,
                "default_category": self.defaults.default_category,
                "default_favorites_only": self.defaults.default_favorites_only,
                "default_view_mode": self.defaults.default_view_mode,
                "default_items_per_page": self.defaults.default_items_per_page,
                "default_search_scope": self.defaults.default_search_scope,
                "case_sensitive_search": self.defaults.case_sensitive_search,
            },
            "enable_telemetry": self.enable_telemetry,
            "config_version": self.config_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecipeBrowserConfig":
        """Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            RecipeBrowserConfig: Configured instance
        """
        config = cls()

        # Load performance settings
        if perf_data := data.get("performance", {}):
            config.performance.progressive_rendering_enabled = perf_data.get("progressive_rendering_enabled", True)
            config.performance.batch_size = perf_data.get("batch_size", 8)
            config.performance.render_delay_ms = perf_data.get("render_delay_ms", 16)
            config.performance.card_pool_size = perf_data.get("card_pool_size", 30)
            # ... additional fields as needed

        # Load display settings
        if display_data := data.get("display", {}):
            if card_size := display_data.get("default_card_size"):
                try:
                    config.display.default_card_size = LayoutSize[card_size]
                except KeyError:
                    pass
            # ... additional fields as needed

        # Load other sections similarly
        # ...

        return config

    def get_optimized_settings(self, recipe_count: int) -> dict:
        """Get optimized settings based on recipe count.

        Dynamically adjusts configuration based on the number of recipes
        to be displayed for optimal performance.

        Args:
            recipe_count: Number of recipes to display

        Returns:
            dict: Optimized settings for the given recipe count
        """
        settings = {}

        # Adjust batch size based on recipe count
        if recipe_count < 10:
            settings["batch_size"] = recipe_count
            settings["progressive_rendering"] = False
        elif recipe_count < 50:
            settings["batch_size"] = min(10, self.performance.batch_size)
            settings["progressive_rendering"] = True
        else:
            settings["batch_size"] = self.performance.batch_size
            settings["progressive_rendering"] = True
            settings["enable_prefetching"] = True

        # Adjust pool size based on recipe count
        settings["pool_size"] = min(
            recipe_count + 5,  # Small buffer
            self.performance.card_pool_size
        )

        return settings


# ── Factory Functions ────────────────────────────────────────────────────────────────────────────────────────
def create_default_config() -> RecipeBrowserConfig:
    """Create default RecipeBrowser configuration.

    Returns:
        RecipeBrowserConfig: Default configuration instance
    """
    return RecipeBrowserConfig()


def create_performance_config() -> RecipeBrowserConfig:
    """Create performance-optimized configuration.

    Optimized for large datasets and slower systems.

    Returns:
        RecipeBrowserConfig: Performance-optimized configuration
    """
    config = RecipeBrowserConfig()
    config.performance.progressive_rendering_enabled = True
    config.performance.batch_size = 5
    config.performance.card_pool_size = 20
    config.performance.cache_strategy = CacheStrategy.AGGRESSIVE
    config.display.enable_animations = False
    config.display.smooth_scrolling = False
    return config


def create_quality_config() -> RecipeBrowserConfig:
    """Create quality-optimized configuration.

    Optimized for best visual quality and user experience.

    Returns:
        RecipeBrowserConfig: Quality-optimized configuration
    """
    config = RecipeBrowserConfig()
    config.performance.progressive_rendering_enabled = False
    config.performance.batch_size = 20
    config.performance.card_pool_size = 50
    config.display.enable_animations = True
    config.display.animation_duration_ms = 350
    config.display.smooth_scrolling = True
    config.interaction.filter_debounce_delay_ms = 150
    return config


# ── Module Exports ───────────────────────────────────────────────────────────────────────────────────────────
__all__ = [
    "RecipeBrowserConfig",
    "PerformanceConfig",
    "DisplayConfig",
    "InteractionConfig",
    "FeatureFlags",
    "DefaultsConfig",
    "CacheStrategy",
    "RenderingMode",
    "create_default_config",
    "create_performance_config",
    "create_quality_config",
]
