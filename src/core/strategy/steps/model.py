import inspect
import traceback
from collections import Counter
from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
)

from core.strategy.steps.protocol import ErrProtocol, OkProtocol, ResultProtocol
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

    # Model validation feature flags
    _validate_signature: bool = PrivateAttr(default=False) 
    _validate_result_protocol: bool = PrivateAttr(default=False)

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
    def load_function_and_validate_signature(self) -> "StrategyStepDefinition":
        self._function = function_loader(self.function_path)

        if self._validate_signature:
            sig = inspect.signature(self._function)
            expected_inputs = set(self.input_bindings.keys())
            actual_inputs = set(sig.parameters.keys())

            missing = expected_inputs - actual_inputs
            if missing:
                raise ValueError(f"Function '{self.function_path}' missing params: {missing}")

        return self

    @model_validator(mode="after")
    def validate_output_binding_structure(self) -> "StrategyStepDefinition":
        """
        Validates that the function's return type is compatible with the declared output bindings.

        If output bindings are specified, this check ensures the associated function is callable
        and its return annotation (if provided) is a dictionary type. This guards against structural
        mismatches between the function's return value and the expected output bindings,
        without executing the function.

        Raises:
            ValueError: If the function is not callable or its return type is not dict-like
                        while output bindings are defined.
        """
        if not self._validate_result_protocol: 
            return self
        
        LEGAL_RETURN_TYPES = (dict, Dict[str, Any], ResultProtocol)
        if not callable(self._function):
            raise ValueError(f"Function at path '{self.function_path}' is not callable")

        if self.output_bindings:
            sig = inspect.signature(self._function)

            if sig.return_annotation != inspect.Signature.empty:
                if sig.return_annotation not in (LEGAL_RETURN_TYPES):
                    raise ValueError(
                        f"Function '{self.function_path}' does not conform to ResultProtocol "
                        f"(expected return type to be a dict)"
                    )
        return self
    @property
    def callable_fn(self) -> Callable:
        return self._function
    

class StrategyStepResult(BaseModel):
    """
    Represents the outcome of executing a strategy step.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(...,)
    message: Optional[str] = Field( default=None, description="Human-readable additional info")
    price_index: Optional[pd.Timestamp] = Field(default=None,description="Index (pd.Timestamp) of the price bar related to the step")
    result_time: datetime = Field(default_factory=datetime.now,description="Time when the step execution completed.")
    outputs: Dict[str, object] = Field(default_factory=dict, description="Named return values produced by the step.")

    # Stack trace or debug info - not meant for public API consumers
    _stack: Optional[str] = PrivateAttr(default=None)

    @property
    def stack_trace(self) -> Optional[str]:
        return self._stack
    
    # TODO : could just use .from_result() for both ok and err? 
    @staticmethod
    def ok(
        outputs: Dict[str, object],
        price_index: Optional[pd.Timestamp] = None,
    ) -> "StrategyStepResult":
        """
        Create a successful result.
        """
        return StrategyStepResult(
            success=True,
            outputs=outputs,
            price_index=price_index,
        )
    # TODO : could just use .from_result() for both ok and err?
    @staticmethod
    def err(
        message: str,
        stack: Optional[str] = None,
    ) -> "StrategyStepResult":
        """
        Create a failure result.
        """
        result = StrategyStepResult(
            success=False,
            message=message,
        )
        result._stack = stack
        return result
    
    @classmethod
    def from_result(
            cls,
            result: Union[ResultProtocol[Dict[str, object], Exception], OkProtocol[Dict[str, object]], ErrProtocol[Exception]],
            price_index: Optional[pd.Timestamp] = None
        ) -> "StrategyStepResult":
            match result:
                case OkProtocol(value=outputs):
                    return cls.ok(outputs=outputs, price_index=price_index)
                case ErrProtocol(error=exc):
                    return cls.err(
                        message=str(exc),
                        stack="".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                    )
                case _:
                    raise TypeError(f"Unsupported result type: {type(result)}")