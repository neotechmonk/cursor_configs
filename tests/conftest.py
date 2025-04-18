import pandas as pd
import pytest
import yaml

from utils import PriceLabel


@pytest.fixture
def uptrending_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [95, 96, 97, 98, 99],
        PriceLabel.HIGH:  [95, 96, 97, 98, 100],
        PriceLabel.LOW:   [70, 81, 82, 83, 81],
        PriceLabel.CLOSE: [70, 81, 82, 83, 84]
    }, index=dates)


@pytest.fixture
def downtrending_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [105, 104, 103, 102, 101],
        PriceLabel.HIGH:  [106, 105, 104, 103, 102],
        PriceLabel.LOW:   [95, 94, 93, 92, 91],
        PriceLabel.CLOSE: [96, 95, 94, 93, 92]
    }, index=dates)


# Fix : unrealistic data - identical highs and lows
@pytest.fixture
def rangebound_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [100, 101, 100, 99, 100],
        PriceLabel.HIGH:  [105, 105, 105, 105, 105],
        PriceLabel.LOW:   [90,  90,  90,  90,  90],
        PriceLabel.CLOSE: [100, 100, 101, 100, 99]
    }, index=dates)


@pytest.fixture
def sample_strategy_config(tmp_path):
    """Create a temporary strategy config file for testing"""
    config_dir = tmp_path / "configs" / "strategies"
    config_dir.mkdir(parents=True)
    
    config_data = {
        "name": "Test Strategy",
        "steps": [
            {
                "id": "detect_trend",
                "name": "Detect Trend",
                "description": "Determine market trend direction",
                "evaluation_fn": "test_strategy.mock_get_trend",
                "config": {},  # No config needed for trend detection
                "reevaluates": {}
            },
            {
                "id": "find_extreme",
                "name": "Find Extreme Bar",
                "description": "Check if current bar is an extreme",
                "evaluation_fn": "test_strategy.mock_is_extreme_bar",
                "config": {
                    "frame_size": 5  # Number of bars to look back
                },
                "reevaluates": {}
            },
            {
                "id": "validate_pullback",
                "name": "Validate Pullback",
                "description": "Ensure pullback has enough bars",
                "evaluation_fn": "test_strategy.mock_is_bars_since_extreme_pivot_valid",
                "config": {
                    "min_bars": 3,  # Minimum bars required
                    "max_bars": 10  # Maximum bars allowed
                },
                "reevaluates": {}
            },
            {
                "id": "check_fib",
                "name": "Check Fibonacci Extension",
                "description": "Verify Fibonacci extension criteria",
                "evaluation_fn": "test_strategy.mock_is_within_fib_extension",
                "config": {
                    "min_extension": 1.35,  # Minimum Fibonacci extension
                    "max_extension": 1.875  # Maximum Fibonacci extension
                },
                "reevaluates": {
                    "validate_pullback": True  # Reference step ID
                }
            }
        ]
    }
    
    config_file = config_dir / "test_strategy.yaml"
    config_file.write_text(yaml.dump(config_data))
    
    return config_dir