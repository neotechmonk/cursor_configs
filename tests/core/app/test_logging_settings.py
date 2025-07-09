import json
import tempfile
from pathlib import Path

from core.app.logging import LoggingSettings, load_logging_config


def test_logging_settings_defaults():
    """Test LoggingSettings defaults without config_path."""
    settings = LoggingSettings()
    assert settings.config_path is None


def test_logging_settings_with_config_path():
    """Test LoggingSettings with a config_path."""
    config_path = Path("test/logging.json")
    settings = LoggingSettings(config_path=config_path)
    assert settings.config_path == config_path


def test_load_logging_config_with_valid_file():
    """Test load_logging_config loads values from a valid JSON config."""
    json_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        json.dump(json_config, tmp)
        tmp_path = Path(tmp.name)

    try:
        # Test that the function loads the config without error
        load_logging_config(tmp_path)
        
        # Verify that logging was configured (check that the root logger has the expected level)
        import logging
        root_logger = logging.getLogger()
        assert root_logger.level == 10  # DEBUG level is 10
        
    finally:
        tmp_path.unlink()  # Clean up


def test_load_logging_config_with_nonexistent_file(caplog):
    """Test load_logging_config handles nonexistent file gracefully."""
    nonexistent_path = Path("/nonexistent/path/logging.json")
    
    # Set caplog to capture warnings but don't change root logger level
    caplog.set_level("WARNING")
    
    # Should not crash, should use default logging config
    load_logging_config(nonexistent_path)
    
    # Verify that default logging is configured
    import logging
    root_logger = logging.getLogger()
    assert root_logger.level == 20  # INFO level is 20 (default)


def test_load_logging_config_with_invalid_json(caplog):
    """Test load_logging_config handles invalid JSON gracefully."""
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        tmp.write('{"invalid": json}')  # Invalid JSON
        tmp_path = Path(tmp.name)

    try:
        # Set caplog to capture errors but don't change root logger level
        caplog.set_level("ERROR")
        
        # Should not crash, should use default logging config
        load_logging_config(tmp_path)
        
        # Verify that default logging is configured
        import logging
        root_logger = logging.getLogger()
        assert root_logger.level == 20  # INFO level is 20 (default)
        
    finally:
        tmp_path.unlink()  # Clean up


def test_load_logging_config_with_none():
    """Test load_logging_config handles None config_path gracefully."""
    # Should not crash, should use default logging config
    load_logging_config(None)
    
    # Verify that default logging is configured
    import logging
    root_logger = logging.getLogger()
    assert root_logger.level == 20  # INFO level is 20 (default)