import inspect
from collections import Counter
from enum import StrEnum
from typing import Callable, Dict, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from util.fn_loader import function_loader


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
    def check_duplicate_input_mappings(self) -> "StrategyStepDefinition":
        mappings = [binding.mapping for binding in self.input_bindings.values()]
        duplicates = [item for item, count in Counter(mappings).items() if count > 1]
        if duplicates:
            raise ValueError(f"Duplicate input mappings found: {duplicates}")
        return self
    
    @model_validator(mode="after")
    def load_and_validate_function(self) -> "StrategyStepDefinition":
        func = function_loader(self.function_path)
        sig = inspect.signature(func)

        # Validate that all input_bindings are satisfied by function parameters
        expected_inputs = set(self.input_bindings.keys())
        actual_inputs = set(sig.parameters.keys())

        missing = expected_inputs - actual_inputs
        if missing:
            raise ValueError(f"Function '{self.function_path}' missing params: {missing}")

        # Store the actual function object in a private field
        self._function = func
        return self
    
    @property
    def callable_fn(self) -> Callable:
        return self._function