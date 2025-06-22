"""Tests for risk configuration loader."""

from pathlib import Path

import pytest

from src.loaders.risk_config_loader import RiskConfigLoader


@pytest.fixture
def risk_config_path(tmp_path):
    """Create a temporary risk configuration file."""
    config = {
        "default_risk_limits": {
            "max_position_size": 100000.0,
            "max_drawdown": 0.1,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.04
        },
        "position_sizing": {
            "max_risk_per_trade": 0.01,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 1000000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "1h",
            "alert_threshold": 0.05,
            "max_open_positions": 10
        }
    }
    
    config_path = tmp_path / "risk_config.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f)
    return config_path


def test_load_risk_config(risk_config_path):
    """Test loading risk configuration."""
    loader = RiskConfigLoader(risk_config_path)
    config = loader.load()
    
    assert config.default_risk_limits.max_position_size == 100000.0
    assert config.default_risk_limits.max_drawdown == 0.1
    assert config.position_sizing.max_risk_per_trade == 0.01
    assert config.portfolio_constraints.max_leverage == 2.0
    assert config.risk_monitoring.max_open_positions == 10


def test_get_risk_limits(risk_config_path):
    """Test getting risk limits."""
    loader = RiskConfigLoader(risk_config_path)
    loader.load()
    
    limits = loader.get_risk_limits()
    assert limits["max_position_size"] == 100000.0
    assert limits["max_drawdown"] == 0.1
    assert limits["stop_loss_pct"] == 0.02
    assert limits["take_profit_pct"] == 0.04


def test_get_position_sizing(risk_config_path):
    """Test getting position sizing rules."""
    loader = RiskConfigLoader(risk_config_path)
    loader.load()
    
    sizing = loader.get_position_sizing()
    assert sizing["max_risk_per_trade"] == 0.01
    assert sizing["max_correlation"] == 0.7
    assert sizing["max_sector_exposure"] == 0.3


def test_get_portfolio_constraints(risk_config_path):
    """Test getting portfolio constraints."""
    loader = RiskConfigLoader(risk_config_path)
    loader.load()
    
    constraints = loader.get_portfolio_constraints()
    assert constraints["max_leverage"] == 2.0
    assert constraints["min_liquidity"] == 1000000.0
    assert constraints["max_slippage"] == 0.001


def test_get_risk_monitoring(risk_config_path):
    """Test getting risk monitoring settings."""
    loader = RiskConfigLoader(risk_config_path)
    loader.load()
    
    monitoring = loader.get_risk_monitoring()
    assert monitoring["check_interval"] == "1h"
    assert monitoring["alert_threshold"] == 0.05
    assert monitoring["max_open_positions"] == 10


def test_config_not_loaded():
    """Test error when config is not loaded."""
    loader = RiskConfigLoader(Path("nonexistent.yaml"))
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_risk_limits()
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_position_sizing()
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_portfolio_constraints()
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_risk_monitoring() 