import traceback
from datetime import datetime
from typing import Dict, Optional, Protocol, TypeVar, Union, runtime_checkable

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

T = TypeVar("T")
E = TypeVar("E")

# protocol for result types from result package
@runtime_checkable
class ResultProtocol(Protocol[T, E]):
    ...

# protocol for ok result types
@runtime_checkable
class OkProtocol(Protocol[T]):
    value: T

# protocol for err result types
@runtime_checkable
class ErrProtocol(Protocol[E]):
    error: E


class StrategyStepResult(BaseModel):
    """
    Represents the outcome of executing a strategy step.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(..., description="Indicates whether the step succeeded or failed.")
    message: Optional[str] = Field(
        default=None,
        description="Human-readable status or error message, if applicable."
    )
    price_index: Optional[pd.Timestamp] = Field(
        default=None,
        description="Timestamp of the price bar related to the step's output."
    )
    result_time: datetime = Field(
        default_factory=datetime.now,
        description="Time when the step execution completed."
    )
    outputs: Dict[str, object] = Field(
        default_factory=dict,
        description="Named return values produced by the step."
    )

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