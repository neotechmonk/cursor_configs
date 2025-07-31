from pathlib import Path
import pytest
from dataclasses import dataclass

from core.execution_provider.providers.file import FileExecutionProvider, FileExecutionProviderConfig


@dataclass
class MockOrder:
    """
    Mock Order class of Order model
    """
    symbol: str
    quantity: float
    price: float


# --- Fixtures ---

@pytest.fixture
def mock_config():
    """Fixture for FileExecutionProviderConfig."""
    return FileExecutionProviderConfig(
        name="file_exec", 
        file_path=Path("fake/path.txt")
    )


@pytest.fixture
def file_provider(mock_config):
    """Fixture for FileExecutionProvider instance."""
    return FileExecutionProvider(config=mock_config)


@pytest.fixture
def sample_order():
    """Fixture for a sample MockOrder."""
    return MockOrder(
        symbol="BTCUSD", 
        quantity=1.0, 
        price=50000.0
    )


@pytest.fixture
def sample_order_eth():
    """Fixture for a sample ETH order."""
    return MockOrder(
        symbol="ETHUSD", 
        quantity=2.5, 
        price=3000.0
    )


# --- Basic Tests ---



def test_submit_order_prints_and_returns_true(file_provider, sample_order, capfd):
    """Test that submit_order prints expected output and returns True."""
    result = file_provider.submit_order(sample_order)
    
    # Capture stdout
    out, _ = capfd.readouterr()

    assert "Sumitting Order" in out
    assert "BTCUSD" in out
    assert result is True


