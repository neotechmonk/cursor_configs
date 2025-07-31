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

# --- Basic Tests ---

def test_provider_name_property():
    config = FileExecutionProviderConfig(name="file_exec", file_path=Path("fake/path.txt"))
    provider = FileExecutionProvider(config=config)
    
    assert provider.name == "file_exec"

# @pytest.mark.skip(reason="Not implemented")
def test_submit_order_prints_and_returns_true(capfd):
    config = FileExecutionProviderConfig(name="file_exec", file_path=Path("fake/path.txt"))
    provider = FileExecutionProvider(config=config)

    test_order = MockOrder(symbol="BTCUSD", quantity=1.0, price=50000.0, )
    result = provider.submit_order(test_order)
    
    # Capture stdout
    out, _ = capfd.readouterr()

    assert "Sumitting Order" in out
    assert "BTCUSD" in out
    assert result is True