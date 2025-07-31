import json
from pathlib import Path

import pytest

from core.execution_provider.providers.file import (
    FileExecutionProvider,
    FileExecutionProviderConfig,
)
from core.order.models import Order, OrderSide, OrderType

# --- Fixtures ---


@pytest.fixture
def temp_order_file(tmp_path) -> Path:
    return tmp_path / "orders.jsonl"


@pytest.fixture
def file_provider(temp_order_file) -> FileExecutionProvider:
    config = FileExecutionProviderConfig(name="test_provider", file_path=temp_order_file)
    return FileExecutionProvider(config=config)


@pytest.fixture
def sample_order():
    """Fixture for a sample MockOrder."""
    return Order(
        symbol="BTCUSD", 
        quantity=1, 
        entry_price=50000,
        stop_price=49000,
        target_price=51000,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        timeframe="1m",
        tag="test"
    )


# --- Basic Tests ---


def test_submit_order_writes_expected_json(file_provider, sample_order, temp_order_file):
    """Test that submit_order writes valid JSON content to the file."""
    result = file_provider.submit_order(sample_order)

    assert result is True
    assert temp_order_file.exists()

    lines = temp_order_file.read_text().strip().splitlines()
    assert len(lines) == 1

    order_json = json.loads(lines[0])

    # Basic structure assertions
    assert "timestamp" in order_json
    assert order_json["symbol"] == "BTCUSD"
    assert order_json["side"] == "buy"
    assert order_json["order_type"] == "market"
    assert order_json["quantity"] == "1"
    assert order_json["entry_price"] == "50000"
    assert order_json["stop_price"] == "49000"
    assert order_json["target_price"] == "51000"
    assert order_json["tag"] == "test"

    with pytest.raises(KeyError):
        order_json["ttl_bars"] #optional field and not set at instantiation