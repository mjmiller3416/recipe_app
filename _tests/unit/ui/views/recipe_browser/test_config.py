"""Unit tests for RecipeBrowser configuration module."""

import pytest
import os
from unittest.mock import patch

from app.ui.views.recipe_browser.config import (
    RecipeBrowserConfig,
    PerformanceConfig,
    DisplayConfig,
    InteractionConfig,
    FeatureFlags,
    DefaultsConfig,
    CacheStrategy,
    RenderingMode,
    create_default_config,
    create_performance_config,
    create_quality_config,
)
from app.ui.components.composite.recipe_card import LayoutSize


class TestRecipeBrowserConfig:
    """Test RecipeBrowserConfig class."""
    
    def test_default_initialization(self):
        """Test default configuration values."""
        config = RecipeBrowserConfig()
        
        # Check performance defaults
        assert config.performance.progressive_rendering_enabled is True
        assert config.performance.batch_size == 8
        assert config.performance.card_pool_size == 30
        assert config.performance.cache_strategy == CacheStrategy.MEMORY
        
        # Check display defaults
        assert config.display.default_card_size == LayoutSize.MEDIUM
        assert config.display.card_spacing == 10
        assert config.display.enable_animations is True
        
        # Check interaction defaults
        assert config.interaction.filter_debounce_delay_ms == 250
        assert config.interaction.search_debounce_delay_ms == 300
        assert config.interaction.resize_debounce_delay_ms == 50
        
        # Check feature flags
        assert config.features.enable_progressive_rendering is True
        assert config.features.enable_cache is True
        assert config.features.enable_performance_monitoring is True
        
        # Check defaults
        assert config.defaults.default_sort_option == "A-Z"
        assert config.defaults.default_category == "All"
        assert config.defaults.default_favorites_only is False
    
    def test_validation_valid_config(self):
        """Test validation with valid configuration."""
        config = RecipeBrowserConfig()
        config.validate()  # Should not raise
    
    def test_validation_invalid_batch_size(self):
        """Test validation with invalid batch size."""
        config = RecipeBrowserConfig()
        config.performance.batch_size = 0
        
        with pytest.raises(ValueError, match="batch_size must be between 1 and 50"):
            config.validate()
    
    def test_validation_invalid_pool_size(self):
        """Test validation with pool size less than batch size."""
        config = RecipeBrowserConfig()
        config.performance.batch_size = 10
        config.performance.card_pool_size = 5
        
        with pytest.raises(ValueError, match="card_pool_size .* must be >= batch_size"):
            config.validate()
    
    def test_validation_invalid_debounce_delay(self):
        """Test validation with invalid debounce delay."""
        config = RecipeBrowserConfig()
        config.interaction.filter_debounce_delay_ms = -1
        
        with pytest.raises(ValueError, match="filter_debounce_delay_ms must be between 0 and 2000"):
            config.validate()
    
    def test_validation_invalid_sort_option(self):
        """Test validation with invalid sort option."""
        config = RecipeBrowserConfig()
        config.defaults.default_sort_option = "Invalid"
        
        with pytest.raises(ValueError, match="Invalid default_sort_option"):
            config.validate()
    
    @patch.dict(os.environ, {"RECIPE_BROWSER_PERFORMANCE__BATCH_SIZE": "12"})
    def test_environment_override_batch_size(self):
        """Test environment variable override for batch size."""
        config = RecipeBrowserConfig()
        assert config.performance.batch_size == 12
    
    @patch.dict(os.environ, {"RECIPE_BROWSER_PERFORMANCE__PROGRESSIVE_RENDERING_ENABLED": "false"})
    def test_environment_override_progressive_rendering(self):
        """Test environment variable override for progressive rendering."""
        config = RecipeBrowserConfig()
        assert config.performance.progressive_rendering_enabled is False
    
    @patch.dict(os.environ, {"RECIPE_BROWSER_INTERACTION__FILTER_DEBOUNCE_DELAY_MS": "500"})
    def test_environment_override_debounce(self):
        """Test environment variable override for debounce delay."""
        config = RecipeBrowserConfig()
        assert config.interaction.filter_debounce_delay_ms == 500
    
    @patch.dict(os.environ, {"RECIPE_BROWSER_DEFAULTS__DEFAULT_SORT_OPTION": "Z-A"})
    def test_environment_override_sort_option(self):
        """Test environment variable override for default sort option."""
        config = RecipeBrowserConfig()
        assert config.defaults.default_sort_option == "Z-A"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = RecipeBrowserConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "performance" in config_dict
        assert "display" in config_dict
        assert "interaction" in config_dict
        assert "features" in config_dict
        assert "defaults" in config_dict
        
        # Check nested values
        assert config_dict["performance"]["batch_size"] == 8
        assert config_dict["display"]["default_card_size"] == "MEDIUM"
        assert config_dict["interaction"]["filter_debounce_delay_ms"] == 250
    
    def test_get_optimized_settings_small_dataset(self):
        """Test optimized settings for small dataset."""
        config = RecipeBrowserConfig()
        settings = config.get_optimized_settings(5)
        
        assert settings["batch_size"] == 5
        assert settings["progressive_rendering"] is False
        assert settings["pool_size"] == 10  # 5 + 5 buffer
    
    def test_get_optimized_settings_medium_dataset(self):
        """Test optimized settings for medium dataset."""
        config = RecipeBrowserConfig()
        settings = config.get_optimized_settings(25)
        
        assert settings["batch_size"] == 8  # Uses config default
        assert settings["progressive_rendering"] is True
        assert settings["pool_size"] == 30  # 25 + 5 buffer, capped at max
    
    def test_get_optimized_settings_large_dataset(self):
        """Test optimized settings for large dataset."""
        config = RecipeBrowserConfig()
        settings = config.get_optimized_settings(100)
        
        assert settings["batch_size"] == 8
        assert settings["progressive_rendering"] is True
        assert settings["enable_prefetching"] is True
        assert settings["pool_size"] == 30  # Capped at max


class TestConfigFactories:
    """Test configuration factory functions."""
    
    def test_create_default_config(self):
        """Test default configuration factory."""
        config = create_default_config()
        
        assert isinstance(config, RecipeBrowserConfig)
        assert config.performance.progressive_rendering_enabled is True
        assert config.performance.batch_size == 8
    
    def test_create_performance_config(self):
        """Test performance configuration factory."""
        config = create_performance_config()
        
        assert config.performance.progressive_rendering_enabled is True
        assert config.performance.batch_size == 5  # Smaller batches
        assert config.performance.card_pool_size == 20  # Smaller pool
        assert config.performance.cache_strategy == CacheStrategy.AGGRESSIVE
        assert config.display.enable_animations is False
        assert config.display.smooth_scrolling is False
    
    def test_create_quality_config(self):
        """Test quality configuration factory."""
        config = create_quality_config()
        
        assert config.performance.progressive_rendering_enabled is False
        assert config.performance.batch_size == 20  # Larger batches
        assert config.performance.card_pool_size == 50  # Larger pool
        assert config.display.enable_animations is True
        assert config.display.animation_duration_ms == 350
        assert config.display.smooth_scrolling is True
        assert config.interaction.filter_debounce_delay_ms == 150  # More responsive


class TestPerformanceConfig:
    """Test PerformanceConfig class."""
    
    def test_validation_valid(self):
        """Test validation with valid values."""
        config = PerformanceConfig()
        config.validate()  # Should not raise
    
    def test_validation_invalid_batch_size(self):
        """Test validation with invalid batch size."""
        config = PerformanceConfig()
        config.batch_size = 51
        
        with pytest.raises(ValueError, match="batch_size must be between 1 and 50"):
            config.validate()
    
    def test_validation_negative_cache_ttl(self):
        """Test validation with negative cache TTL."""
        config = PerformanceConfig()
        config.cache_ttl_seconds = -1
        
        with pytest.raises(ValueError, match="cache_ttl_seconds must be non-negative"):
            config.validate()


class TestDisplayConfig:
    """Test DisplayConfig class."""
    
    def test_validation_valid(self):
        """Test validation with valid values."""
        config = DisplayConfig()
        config.validate()  # Should not raise
    
    def test_validation_invalid_columns(self):
        """Test validation with invalid column configuration."""
        config = DisplayConfig()
        config.min_columns = 5
        config.max_columns = 3
        
        with pytest.raises(ValueError, match="Invalid column range"):
            config.validate()
    
    def test_validation_invalid_spacing(self):
        """Test validation with invalid card spacing."""
        config = DisplayConfig()
        config.card_spacing = 101
        
        with pytest.raises(ValueError, match="card_spacing must be between 0 and 100"):
            config.validate()


class TestInteractionConfig:
    """Test InteractionConfig class."""
    
    def test_validation_valid(self):
        """Test validation with valid values."""
        config = InteractionConfig()
        config.validate()  # Should not raise
    
    def test_validation_invalid_filter_debounce(self):
        """Test validation with invalid filter debounce."""
        config = InteractionConfig()
        config.filter_debounce_delay_ms = 2001
        
        with pytest.raises(ValueError, match="filter_debounce_delay_ms must be between 0 and 2000"):
            config.validate()


class TestCacheStrategy:
    """Test CacheStrategy enum."""
    
    def test_enum_values(self):
        """Test cache strategy enum values."""
        assert CacheStrategy.NONE.value == "none"
        assert CacheStrategy.MEMORY.value == "memory"
        assert CacheStrategy.AGGRESSIVE.value == "aggressive"


class TestRenderingMode:
    """Test RenderingMode enum."""
    
    def test_enum_values(self):
        """Test rendering mode enum values."""
        assert RenderingMode.IMMEDIATE.value == "immediate"
        assert RenderingMode.PROGRESSIVE.value == "progressive"
        assert RenderingMode.VIRTUAL.value == "virtual"