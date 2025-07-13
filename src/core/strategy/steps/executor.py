from dataclasses import dataclass
from typing import Any, Callable, Dict

from typing_extensions import deprecated

from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.protocol import (
    RuntimeContextProtocol,
    StrategyStepConfigProtocol,
)
from util import function_loader


def bind_params(
    step: StrategyStepDefinition, 
    config_data: dict, 
    runtime_data: dict
) -> Dict[str, Any]:
    """Resolve input bindings to actual parameter values.
    
    Args:
        step: Step definition with input bindings
        config_data: Static configuration data
        runtime_data: Dynamic runtime data
        
    Returns:
        kwargs dictionary ready for function call
        
    Raises:
        KeyError: If required data is missing
    """
    kwargs = {}
    for param_name, binding in step.input_bindings.items():
        source_data = runtime_data if binding.source == step.ParamSource.RUNTIME else config_data
        if binding.mapping not in source_data:
            raise KeyError(
                f"Missing input key '{binding.mapping}' in expected source: {binding.source}"
            )
        kwargs[param_name] = source_data[binding.mapping]
    return kwargs


def execute(fn: Callable, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute function with provided parameters.
    
    Args:
        fn: Function to execute
        params: Parameters to pass to function
        
    Returns:
        Raw results from function execution
    """
    # Handle functions that don't accept keyword arguments
    try:
        return fn(**params)
    except TypeError:
        # If keyword arguments fail, try positional arguments
        return fn(*params.values())


def map_results(
    step: StrategyStepDefinition, 
    raw_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Map function results according to output bindings.
    
    Args:
        step: Step definition with output bindings
        raw_results: Raw results from function execution
        
    Returns:
        Mapped results according to output bindings, or raw results if no bindings
    """
    # If no output bindings, return raw results as-is
    if not step.output_bindings:
        return raw_results
    
    # Otherwise, apply output bindings
    output = {}
    for result_key, binding in step.output_bindings.items():
        value = raw_results.get(result_key)
        if binding.mapping is not None:
            output[binding.mapping] = value
        else:
            output[result_key] = value
    return output


@dataclass
class StrategyStepFunctionResolver:
    step_definition: StrategyStepDefinition
    config_data: dict[str, str]
    runtime_data: dict[str, Any]
    _function_loader: Callable[[str], Callable] = function_loader

    def __call__(self) -> Dict[str, Any]:  
        resolved_input_params = bind_params(self.step_definition, self.config_data, self.runtime_data)
        step_function = self._function_loader(self.step_definition.function_path)
        raw_results = execute(step_function, resolved_input_params) 
        return map_results(self.step_definition, raw_results)


@deprecated("Use StrategyFunctionResolver instead")
class StrategyStepExecutor:
    def __init__(
        self,
        step: StrategyStepDefinition,
        context: RuntimeContextProtocol,
        config: StrategyStepConfigProtocol,
        function_loader: Callable[[str], Callable] = function_loader
    ):
        self.step = step
        self.context = context
        self.config = config
        self.function_loader = function_loader

    def execute(self) -> Dict[str, Any]:
        fn = self.function_loader(self.step.function_path)

        kwargs = {}
        for param_name, binding in self.step.input_bindings.items():
            source_data = self.context if binding.source == self.step.ParamSource.RUNTIME else self.config
            if not source_data.has(binding.mapping):
                raise KeyError(
                    f"Missing input key '{binding.mapping}' in expected source: {binding.source}"
                )
            kwargs[param_name] = source_data.get(binding.mapping)

        result = fn(**kwargs)

        output = {}
        for result_key, binding in self.step.output_bindings.items():
            value = result.get(result_key)
            if binding.mapping is not None:
                output[binding.mapping] = value
            else:
                output[result_key] = value
        return output