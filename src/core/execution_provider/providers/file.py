import json
import logging
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from filelock import FileLock
from pydantic import BaseModel, ConfigDict

from core.order.models import Order

logger = logging.getLogger(__name__)


class RawFileExecutionProviderConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: Optional[str] = None # assigned post instantiation as its the name of the yaml file
    file_path: str


class FileExecutionProviderConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    name: str
    file_path: Path
    
    def model_post_init(self, __context) -> None:
        """Ensure the directory exists for the file path."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)


def resolve_file_execution_provider_config(raw: RawFileExecutionProviderConfig) -> FileExecutionProviderConfig:
    warnings.warn(
        "resolve_file_execution_provider_config is deprecated. "
        "Use FileExecutionProviderConfig model validator instead.",
        DeprecationWarning
    )

    file_path = Path(raw.file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Execution file does not exist at: {file_path}")

    return FileExecutionProviderConfig(
        name=raw.name or "file_execution_provider",
        file_path=file_path
    )


@dataclass
class FileExecutionProvider:
    """
    Implements `ExecutionProvider` - writes orders to a flat file.
    
    Each order is written as a JSON line to the configured file path.
    The file is created if it doesn't exist, and orders are appended.
    Uses file locking for thread-safe operations.
    """
    
    config: FileExecutionProviderConfig

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self.config.name

    def submit_order(self, order: Order) -> bool:
        """
        Submit an order by writing it to the configured file.
        
        Args:
            order: The order to submit
            
        Returns:
            True if order was successfully written to file
            
        Raises:
            IOError: If there's an error writing to the file
        """
        try:
            order_data = {
                "timestamp": datetime.now().isoformat(),
                **order.model_dump(mode="json", exclude_unset=True)
            }

            lock_path = f"{self.config.file_path}.lock"
            with FileLock(lock_path):
                with open(self.config.file_path, 'a', encoding='utf-8') as f:
                    json.dump(order_data, f)
                    f.write('\n')

            logger.info(f"Order submitted: {order.symbol} {order.side.value} {order.quantity} @ {order.entry_price}")
            return True

        except Exception as e:
            logger.exception(f"Failed to write order to file {self.config.file_path}")
            raise IOError(f"Failed to write order to file: {e}") from e