from pathlib import Path

import pytest

from core.execution_provider.providers.file import (
    FileExecutionProviderConfig,
    RawFileExecutionProviderConfig,
    resolve_file_execution_provider_config,
)


@pytest.fixture
def raw_file_exec_config(tmp_path: Path) -> RawFileExecutionProviderConfig:
    # Create a dummy file
    dummy_file = tmp_path / "orders.csv"
    dummy_file.write_text("symbol,timeframe,order_type,quantity,price\nBTC,1m,buy,1,50000")

    return RawFileExecutionProviderConfig(
        name="file_exec",
        file_path=str(dummy_file)
    )


def test_resolve_file_execution_provider_config_success(raw_file_exec_config):
    resolved: FileExecutionProviderConfig = resolve_file_execution_provider_config(raw_file_exec_config)

    assert resolved.name == "file_exec"
    assert isinstance(resolved.file_path, Path)
    assert resolved.file_path.name == "orders.csv"
    assert resolved.file_path.exists()


def test_resolve_file_execution_provider_config_raises_if_file_missing():
    raw = RawFileExecutionProviderConfig(
        name="missing_file",
        file_path="nonexistent/path/to/missing.csv"
    )

    with pytest.raises(FileNotFoundError, match="Execution file does not exist at:"):
        resolve_file_execution_provider_config(raw)