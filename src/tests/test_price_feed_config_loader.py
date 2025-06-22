"""Tests for price feed configuration loader."""

from pathlib import Path

import pytest

from src.loaders.price_feed_config_loader import PriceFeedConfigLoader


@pytest.fixture
def price_feed_config_path(tmp_path):
    """Create a temporary price feed configuration file."""
    config = {
        "yahoo": {
            "cache": {
                "duration": "1h",
                "max_size": "1GB",
                "cleanup_interval": "1d"
            },
            "rate_limits": {
                "requests_per_minute": 60,
                "requests_per_day": 2000,
                "retry_delay": 5
            },
            "data_quality": {
                "min_bars": 100,
                "max_gap_days": 3,
                "required_fields": ["Open", "High", "Low", "Close", "Volume"]
            },
            "supported_timeframes": ["1d", "1w"]
        }
    }
    
    config_path = tmp_path / "price_feed_config.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f)
    return config_path


def test_load_price_feed_config(price_feed_config_path):
    """Test loading price feed configuration."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    config = loader.load()
    
    assert config.yahoo.cache.duration == "1h"
    assert config.yahoo.rate_limits.requests_per_minute == 60
    assert config.yahoo.data_quality.min_bars == 100
    assert config.yahoo.supported_timeframes == ["1d", "1w"]


def test_get_provider_config(price_feed_config_path):
    """Test getting provider configuration."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    config = loader.get_provider_config("yahoo")
    assert config["cache"]["duration"] == "1h"
    assert config["rate_limits"]["requests_per_minute"] == 60
    assert config["data_quality"]["min_bars"] == 100
    assert config["supported_timeframes"] == ["1d", "1w"]


def test_get_cache_settings(price_feed_config_path):
    """Test getting cache settings."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    cache = loader.get_cache_settings("yahoo")
    assert cache["duration"] == "1h"
    assert cache["max_size"] == "1GB"
    assert cache["cleanup_interval"] == "1d"


def test_get_rate_limits(price_feed_config_path):
    """Test getting rate limits."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    limits = loader.get_rate_limits("yahoo")
    assert limits["requests_per_minute"] == 60
    assert limits["requests_per_day"] == 2000
    assert limits["retry_delay"] == 5


def test_get_data_quality(price_feed_config_path):
    """Test getting data quality requirements."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    quality = loader.get_data_quality("yahoo")
    assert quality["min_bars"] == 100
    assert quality["max_gap_days"] == 3
    assert quality["required_fields"] == ["Open", "High", "Low", "Close", "Volume"]


def test_get_supported_timeframes(price_feed_config_path):
    """Test getting supported timeframes."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    timeframes = loader.get_supported_timeframes("yahoo")
    assert timeframes == ["1d", "1w"]


def test_config_not_loaded():
    """Test error when config is not loaded."""
    loader = PriceFeedConfigLoader(Path("nonexistent.yaml"))
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_provider_config("yahoo")


def test_invalid_provider(price_feed_config_path):
    """Test error for invalid provider."""
    loader = PriceFeedConfigLoader(price_feed_config_path)
    loader.load()
    
    with pytest.raises(ValueError, match="Provider invalid not found in configuration"):
        loader.get_provider_config("invalid") 