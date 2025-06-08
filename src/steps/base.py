"""Base strategy step implementations.

This module contains common/base implementations of strategy steps that can be
used across different types of strategies.
"""

from typing import Any, Dict

import pandas as pd

from src.models.strategy import (StrategyStepEvaluationResult,
                                 StrategyExecutionContext, StrategyStepEvalFn)


def validate_data(
    data: pd.DataFrame,
    context: StrategyExecutionContext,
    config: Dict[str, Any]
) -> StrategyStepEvaluationResult:
    """Validate the input price data.
    
    Args:
        data: Price data to validate
        context: Current strategy execution context
        config: Configuration parameters
        
    Returns:
        Result of the validation step
    """
    # TODO: Implement data validation logic
    return StrategyStepEvaluationResult(
        is_success=True,
        message="Data validation not yet implemented",
        timestamp=data.index[-1] if not data.empty else None,
        step_output={}
    )         message="Data validation not yet implemented",
        timestamp=data.index[-1] if not data.empty else None,
        step_output={}
    ) 