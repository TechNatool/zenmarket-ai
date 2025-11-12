"""
Tests for configuration loader module.
"""

from src.utils.config_loader import Config, get_config


def test_config_initialization():
    """Test that Config can be initialized."""
    config = Config()
    assert config is not None
    assert hasattr(config, "newsapi_key")
    assert hasattr(config, "market_indices")


def test_config_default_values():
    """Test that Config has reasonable defaults."""
    config = Config()
    assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
    assert isinstance(config.market_indices, list)
    assert len(config.market_indices) > 0
    assert config.news_lookback_hours > 0
    assert config.ai_provider in ["openai", "anthropic"]


def test_config_directories_created():
    """Test that Config creates necessary directories."""
    config = Config()
    assert config.report_output_dir.exists()
    assert config.data_cache_dir.exists()


def test_config_to_dict():
    """Test config serialization to dict."""
    config = Config()
    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert "ai_provider" in config_dict
    assert "market_indices" in config_dict

    # Sensitive data should not be in dict
    assert "openai_api_key" not in config_dict
    assert "newsapi_key" not in config_dict


def test_get_api_key():
    """Test get_api_key method."""
    config = Config()

    # Should return empty string for non-existent keys
    key = config.get_api_key("nonexistent")
    assert key == ""

    # Should return configured keys
    newsapi_key = config.get_api_key("newsapi")
    assert isinstance(newsapi_key, str)


def test_config_validation():
    """Test configuration validation."""
    config = Config()
    errors = config.validate()

    assert isinstance(errors, list)
    # Errors depend on environment, so just check structure


def test_get_config_singleton():
    """Test that get_config returns singleton."""
    config1 = get_config()
    config2 = get_config()

    assert config1 is config2


def test_config_reload():
    """Test config reload functionality."""
    config1 = get_config()
    config2 = get_config(reload=True)

    # Should be different instances after reload
    assert config1 is not config2
