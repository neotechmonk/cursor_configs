from dataclasses import dataclass
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict

from core.data_provider.error import SymbolError, TimeframeError
from core.order.models import Order
from core.time import CustomTimeframe


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
    Implements `ExecutionProvider`
    """
    
    config: FileExecutionProviderConfig
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return self.config.name
    
    def submit_order(self, order:Order)-> bool:
        print(f"Sumitting Order : {order}")

        return True