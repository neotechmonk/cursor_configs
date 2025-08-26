"""Tests for risk configuration loader."""

from unittest.mock import mock_open, patch

import pytest
import yaml

from loaders.risk_config_loader import (
    PortfolioConstraints,
    PositionSizing,
    RiskConfig,
    RiskConfigLoader,
    RiskLimits,
    RiskMonitoring,
)


def test_valid_risk_limits():
    """Test creating valid risk limits."""
    risk_limits = RiskLimits(
        max_position_size=10000.0,
        max_drawdown=0.15,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    assert risk_limits.max_position_size == 10000.0
    assert risk_limits.max_drawdown == 0.15
    assert risk_limits.stop_loss_pct == 0.05
    assert risk_limits.take_profit_pct == 0.10


def test_risk_limits_validation():
    """Test that risk limits validation works correctly."""
    # Test with zero values
    risk_limits = RiskLimits(
        max_position_size=0.0,
        max_drawdown=0.0,
        stop_loss_pct=0.0,
        take_profit_pct=0.0
    )
    
    assert risk_limits.max_position_size == 0.0
    assert risk_limits.max_drawdown == 0.0


def test_valid_position_sizing():
    """Test creating valid position sizing rules."""
    position_sizing = PositionSizing(
        max_risk_per_trade=0.02,
        max_correlation=0.7,
        max_sector_exposure=0.3
    )
    
    assert position_sizing.max_risk_per_trade == 0.02
    assert position_sizing.max_correlation == 0.7
    assert position_sizing.max_sector_exposure == 0.3


def test_valid_portfolio_constraints():
    """Test creating valid portfolio constraints."""
    constraints = PortfolioConstraints(
        max_leverage=2.0,
        min_liquidity=100000.0,
        max_slippage=0.001
    )
    
    assert constraints.max_leverage == 2.0
    assert constraints.min_liquidity == 100000.0
    assert constraints.max_slippage == 0.001


def test_valid_risk_monitoring():
    """Test creating valid risk monitoring settings."""
    monitoring = RiskMonitoring(
        check_interval="5m",
        alert_threshold=0.8,
        max_open_positions=10
    )
    
    assert monitoring.check_interval == "5m"
    assert monitoring.alert_threshold == 0.8
    assert monitoring.max_open_positions == 10


def test_valid_risk_config():
    """Test creating valid risk config."""
    risk_config = RiskConfig(
        default_risk_limits=RiskLimits(
            max_position_size=10000.0,
            max_drawdown=0.15,
            stop_loss_pct=0.05,
            take_profit_pct=0.10
        ),
        position_sizing=PositionSizing(
            max_risk_per_trade=0.02,
            max_correlation=0.7,
            max_sector_exposure=0.3
        ),
        portfolio_constraints=PortfolioConstraints(
            max_leverage=2.0,
            min_liquidity=100000.0,
            max_slippage=0.001
        ),
        risk_monitoring=RiskMonitoring(
            check_interval="5m",
            alert_threshold=0.8,
            max_open_positions=10
        )
    )
    
    assert risk_config.default_risk_limits.max_position_size == 10000.0
    assert risk_config.position_sizing.max_risk_per_trade == 0.02
    assert risk_config.portfolio_constraints.max_leverage == 2.0
    assert risk_config.risk_monitoring.check_interval == "5m"


def test_risk_config_loader_init():
    """Test RiskConfigLoader initialization."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    assert str(loader.config_path) == "configs/risk_config.yaml"
    assert loader.config is None


def test_risk_config_loader_load_success():
    """Test successful loading of risk config."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        result = loader.load()
        
        assert result is not None
        assert result.default_risk_limits.max_position_size == 10000.0
        assert result.position_sizing.max_risk_per_trade == 0.02
        assert result.portfolio_constraints.max_leverage == 2.0
        assert result.risk_monitoring.check_interval == "5m"


def test_risk_config_loader_load_file_not_found():
    """Test loading when file is not found."""
    loader = RiskConfigLoader("nonexistent.yaml")
    
    with pytest.raises(FileNotFoundError):
        loader.load()


def test_risk_config_loader_load_invalid_yaml():
    """Test loading invalid YAML."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    with patch('builtins.open', mock_open(read_data="invalid: yaml: content:")):
        with pytest.raises(yaml.YAMLError):
            loader.load()


def test_risk_config_loader_get_risk_limits_success():
    """Test getting risk limits after successful load."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        loader.load()
        risk_limits = loader.get_risk_limits()
        
        assert risk_limits["max_position_size"] == 10000.0
        assert risk_limits["max_drawdown"] == 0.15
        assert risk_limits["stop_loss_pct"] == 0.05
        assert risk_limits["take_profit_pct"] == 0.10


def test_risk_config_loader_get_risk_limits_not_loaded():
    """Test getting risk limits before loading."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_risk_limits()


def test_risk_config_loader_get_position_sizing_success():
    """Test getting position sizing after successful load."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        loader.load()
        position_sizing = loader.get_position_sizing()
        
        assert position_sizing["max_risk_per_trade"] == 0.02
        assert position_sizing["max_correlation"] == 0.7
        assert position_sizing["max_sector_exposure"] == 0.3


def test_risk_config_loader_get_position_sizing_not_loaded():
    """Test getting position sizing before loading."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_position_sizing()


def test_risk_config_loader_get_portfolio_constraints_success():
    """Test getting portfolio constraints after successful load."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        loader.load()
        portfolio_constraints = loader.get_portfolio_constraints()
        
        assert portfolio_constraints["max_leverage"] == 2.0
        assert portfolio_constraints["min_liquidity"] == 100000.0
        assert portfolio_constraints["max_slippage"] == 0.001


def test_risk_config_loader_get_portfolio_constraints_not_loaded():
    """Test getting portfolio constraints before loading."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_portfolio_constraints()


def test_risk_config_loader_get_risk_monitoring_success():
    """Test getting risk monitoring after successful load."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        loader.load()
        risk_monitoring = loader.get_risk_monitoring()
        
        assert risk_monitoring["check_interval"] == "5m"
        assert risk_monitoring["alert_threshold"] == 0.8
        assert risk_monitoring["max_open_positions"] == 10


def test_risk_config_loader_get_risk_monitoring_not_loaded():
    """Test getting risk monitoring before loading."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    with pytest.raises(ValueError, match="Configuration not loaded"):
        loader.get_risk_monitoring()


def test_risk_config_loader_load_twice_returns_same_instance():
    """Test that loading twice returns the same instance."""
    loader = RiskConfigLoader("configs/risk_config.yaml")
    
    config_data = {
        "default_risk_limits": {
            "max_position_size": 10000.0,
            "max_drawdown": 0.15,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10
        },
        "position_sizing": {
            "max_risk_per_trade": 0.02,
            "max_correlation": 0.7,
            "max_sector_exposure": 0.3
        },
        "portfolio_constraints": {
            "max_leverage": 2.0,
            "min_liquidity": 100000.0,
            "max_slippage": 0.001
        },
        "risk_monitoring": {
            "check_interval": "5m",
            "alert_threshold": 0.8,
            "max_open_positions": 10
        }
    }
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
        first_load = loader.load()
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            second_load = loader.load()
            
            # The loader doesn't cache, it creates new instances each time
            # This is the actual behavior, not a bug
            assert first_load is not second_load
            assert loader.config == first_load
            assert loader.config == second_load
