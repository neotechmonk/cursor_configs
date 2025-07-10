from enum import StrEnum
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class StrategyStepDefinition(BaseModel):
    """
    Declarative model representing a strategy step.

    Includes:
    - Function location (to resolve at runtime)
    - Input bindings from config or context
    - Output bindings: where to store the result
    """

    id: str = Field(..., description="Unique identifier of the step.")
    function_path: str = Field(..., description="Path to function to be executed, e.g., 'module.func_name'")

    input_bindings: Dict[str, "InputBinding"] = Field(
        default_factory=dict,
        description="Mapping from function parameter names to bindings (from context or config)"
    )

    output_bindings: Dict[str, "OutputBinding"] = Field(
        default_factory=dict,
        description="Mapping from function return keys to output names in context"
    )

    class ParamSource(StrEnum):
        RUNTIME = "runtime"
        CONFIG = "config"

    class InputBinding(BaseModel):
        """
        Maps a function input to a value source: either 'runtime' or 'config'.
        - `lookup_name`: the key to use in that source.
        """
        source: "StrategyStepDefinition.ParamSource"
        mapping: str

    class OutputBinding(BaseModel):
        """
        Maps a return value from the function to a name in the context.
        - If `target_name == "_"`, the value is returned directly (treated as positional/implicit).
        """
        mapping: Optional[str] = Field(
            default=None,
            description="Name to store in context. Use '_' to return directly."
        )

        @field_validator("mapping", mode="before")
        @classmethod
        def normalize_target_name(cls, v):
            if v == "_":
                return None
            return v
    
    @model_validator(mode="after")
    def check_duplicate_input_sources(self) -> "StrategyStepDefinition":
        seen = {}
        for param_name, binding in self.input_bindings.items():
            key = binding.mapping
            if key in seen:
                other_source = seen[key]
                if other_source != binding.source:
                    raise ValueError(
                        f"Input parameter '{param_name}' has conflicting sources for '{key}': "
                        f"{binding.source} vs {other_source}"
                    )
            else:
                seen[key] = binding.source
        return self