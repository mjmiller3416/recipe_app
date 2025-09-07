"""Example usage of RecipeBrowser configuration.

This module demonstrates how to use the RecipeBrowserConfig class
for different scenarios and configurations.
"""

from app.ui.views.recipe_browser import (
    RecipeBrowser,
    RecipeBrowserConfig,
    create_default_config,
    create_performance_config,
    create_quality_config,
)

def example_default_usage():
    """Example: Using default configuration."""
    # Create browser with default config
    browser = RecipeBrowser(selection_mode=False)
    
    # Access config
    config = browser.get_config()
    print(f"Default batch size: {config.performance.batch_size}")
    print(f"Progressive rendering: {config.performance.progressive_rendering_enabled}")


def example_custom_configuration():
    """Example: Creating custom configuration."""
    # Create custom config
    config = RecipeBrowserConfig()
    
    # Customize performance settings
    config.performance.batch_size = 12
    config.performance.card_pool_size = 40
    config.performance.progressive_rendering_enabled = True
    
    # Customize interaction settings
    config.interaction.filter_debounce_delay_ms = 150  # More responsive
    config.interaction.multi_select_enabled = True
    
    # Customize display settings
    config.display.enable_animations = True
    config.display.animation_duration_ms = 200
    
    # Validate configuration
    config.validate()
    
    # Create browser with custom config
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    return browser


def example_performance_optimized():
    """Example: Using performance-optimized configuration for slow systems."""
    # Use factory for performance config
    config = create_performance_config()
    
    # Further customize if needed
    config.performance.batch_size = 3  # Even smaller batches for very slow systems
    
    # Create browser
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    print("Performance config:")
    print(f"  Batch size: {config.performance.batch_size}")
    print(f"  Pool size: {config.performance.card_pool_size}")
    print(f"  Animations: {config.display.enable_animations}")
    
    return browser


def example_quality_optimized():
    """Example: Using quality-optimized configuration for powerful systems."""
    # Use factory for quality config
    config = create_quality_config()
    
    # Create browser
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    print("Quality config:")
    print(f"  Batch size: {config.performance.batch_size}")
    print(f"  Pool size: {config.performance.card_pool_size}")
    print(f"  Animations: {config.display.enable_animations}")
    print(f"  Animation duration: {config.display.animation_duration_ms}ms")
    
    return browser


def example_runtime_configuration_update():
    """Example: Updating configuration at runtime."""
    # Start with default config
    browser = RecipeBrowser(selection_mode=False)
    
    # Get current config
    current_config = browser.get_config()
    print(f"Initial batch size: {current_config.performance.batch_size}")
    
    # Create new config based on conditions
    if get_recipe_count() > 100:  # Hypothetical function
        # Switch to performance mode for large dataset
        new_config = create_performance_config()
        browser.update_config(new_config)
        print("Switched to performance configuration")
    
    # Refresh to apply changes
    browser.refresh_recipes()


def example_environment_configuration():
    """Example: Configuration from environment variables.
    
    Set these environment variables before running:
    - RECIPE_BROWSER_PERFORMANCE__BATCH_SIZE=15
    - RECIPE_BROWSER_FEATURES__ENABLE_CACHE=true
    - RECIPE_BROWSER_DEFAULTS__DEFAULT_SORT_OPTION=Z-A
    """
    # Config will automatically load from environment
    config = RecipeBrowserConfig()
    
    print("Configuration from environment:")
    print(f"  Batch size: {config.performance.batch_size}")
    print(f"  Cache enabled: {config.features.enable_cache}")
    print(f"  Default sort: {config.defaults.default_sort_option}")
    
    # Create browser with environment config
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    return browser


def example_adaptive_configuration():
    """Example: Adaptive configuration based on recipe count."""
    config = RecipeBrowserConfig()
    
    # Get recipe count (hypothetical)
    recipe_count = get_recipe_count()
    
    # Get optimized settings for this dataset size
    optimized = config.get_optimized_settings(recipe_count)
    
    # Apply optimized settings
    config.performance.batch_size = optimized["batch_size"]
    config.performance.progressive_rendering_enabled = optimized["progressive_rendering"]
    
    # Create browser with adaptive config
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    print(f"Adaptive config for {recipe_count} recipes:")
    print(f"  Batch size: {optimized['batch_size']}")
    print(f"  Progressive: {optimized['progressive_rendering']}")
    
    return browser


def example_monitoring_configuration():
    """Example: Configuration for performance monitoring."""
    config = RecipeBrowserConfig()
    
    # Enable all monitoring features
    config.features.enable_performance_monitoring = True
    config.features.enable_render_timing = True
    config.features.enable_cache_metrics = True
    config.features.enable_verbose_logging = True
    
    # Set thresholds for monitoring
    config.performance.slow_render_threshold_ms = 50.0  # Strict threshold
    
    # Create browser
    browser = RecipeBrowser(selection_mode=False, config=config)
    
    # Connect to performance signals
    browser.rendering_completed.connect(
        lambda count, time: print(f"Rendered {count} recipes in {time:.2f}ms")
    )
    browser.cache_performance_changed.connect(
        lambda rate: print(f"Cache hit rate: {rate:.1f}%")
    )
    
    return browser


def example_config_serialization():
    """Example: Saving and loading configuration."""
    import json

    # Create config
    config = RecipeBrowserConfig()
    config.performance.batch_size = 10
    config.display.enable_animations = False
    
    # Convert to dict for saving
    config_dict = config.to_dict()
    
    # Save to JSON
    with open("recipe_browser_config.json", "w") as f:
        json.dump(config_dict, f, indent=2)
    
    print("Configuration saved to recipe_browser_config.json")
    
    # Load from JSON
    with open("recipe_browser_config.json", "r") as f:
        loaded_dict = json.load(f)
    
    # Create config from dict
    loaded_config = RecipeBrowserConfig.from_dict(loaded_dict)
    
    print(f"Loaded config batch size: {loaded_config.performance.batch_size}")
    
    return loaded_config


# Helper function (placeholder for actual implementation)
def get_recipe_count() -> int:
    """Get the current recipe count from database."""
    # This would be replaced with actual service call
    return 50


if __name__ == "__main__":
    # Run examples
    print("RecipeBrowser Configuration Examples\n")
    print("=" * 50)
    
    print("\n1. Default Configuration:")
    example_default_usage()
    
    print("\n2. Performance Configuration:")
    example_performance_optimized()
    
    print("\n3. Quality Configuration:")
    example_quality_optimized()
    
    print("\n4. Adaptive Configuration:")
    example_adaptive_configuration()
    
    print("\n" + "=" * 50)
    print("Configuration examples completed!")