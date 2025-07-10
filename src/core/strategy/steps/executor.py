from typing import Any, Callable, Dict

from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.protocol import (
    RuntimeContextProtocol,
    StrategyStepConfigProtocol,
)
from util import function_loader


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
            if binding.mapping not in source_data:
                raise KeyError(
                    f"Missing input key '{binding.mapping}' in expected source: {binding.source}"
                )
            kwargs[param_name] = source_data[binding.mapping]

        result = fn(**kwargs)

        output = {}
        for result_key, binding in self.step.output_bindings.items():
            value = result.get(result_key)
            if binding.mapping is not None:
                output[binding.mapping] = value
            else:
                output[result_key] = value
        return output