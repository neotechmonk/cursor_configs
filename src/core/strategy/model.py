from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.strategy.steps.model import StrategyStepDefinition


class RawStrategyStepInstance(BaseModel):
    """
    Represents an instance of a strategy step referring to a system-defined StrategyStepDefinition.
    """
    id: str = Field(..., description="ID matching a StrategyStepDefinition in the registry")
    description: Optional[str] = Field(default=None, description="Optional explanation of the step's purpose")

    config_bindings: Dict[str, str] = Field(default_factory=dict, description="Config-time input bindings")
    runtime_bindings: Dict[str, str] = Field(default_factory=dict, description="Runtime input bindings")
    reevaluates: List[str] = Field(default_factory=list, description="Steps to re-trigger based on conditions")


class RawStrategyConfig(BaseModel):
    """
    Raw representation of a strategy loaded from YAML.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: Optional[str] = None  # Injected after loading if needed
    steps: List[RawStrategyStepInstance]


class StrategyStepInstance(BaseModel):
    """
    Represents an instance of a strategy step referring to a system-defined StrategyStepDefinition.
    """
    step_definition: StrategyStepDefinition = Field(..., description="ID matching a StrategyStepDefinition in the registry")
    description: Optional[str] = Field(default=None, description="Optional explanation of the step's purpose")

    config_bindings: Dict[str, str] = Field(default_factory=dict, description="Config-time input bindings")
    runtime_bindings: Dict[str, str] = Field(default_factory=dict, description="Runtime input bindings")
    reevaluates: List[StrategyStepDefinition] = Field(default_factory=list, description="Steps to re-trigger based on conditions")


class StrategyConfig(BaseModel):
    """
    Raw representation of a strategy loaded from YAML.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    name: Optional[str] = None  # Injected after loading if needed
    steps: List[StrategyStepInstance]


StrategyStepInstance.model_rebuild()


class Strategy(BaseModel):
    """Implements the StrategyProtocol"""
    config: StrategyConfig
