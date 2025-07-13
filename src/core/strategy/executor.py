from core.strategy.model import StrategyConfig, StrategyStepInstance
from core.strategy.steps.executor import StrategyStepFunctionResolver
from core.strategy.steps.protocol import RuntimeContextProtocol


class StrategyExecutor:
    def __init__(
        self,
        config: StrategyConfig,
        context: RuntimeContextProtocol,
    ):
        self.config = config
        self.context = context

    def run(self) -> None:
        """Executes the steps sequentially and handles reevaluations."""
        executed_steps: list[StrategyStepInstance] = []

        for step_instance in self.config.steps:
            self._run_step(step_instance, executed_steps)

    def _create_resolver(self, step_instance: StrategyStepInstance) -> StrategyStepFunctionResolver:
        """Factory for creating the step function resolver."""
        return StrategyStepFunctionResolver(
            step_definition=step_instance.step_definition,
            config_data=self.config,
            runtime_data=self.context,
        )

    def _write_result_to_context(self, step_id: str, result: dict) -> None:
        self.context.set(step_id, result)

    def _run_step(self, step_instance: StrategyStepInstance, executed_steps: list[StrategyStepInstance]) -> dict:
        step_id = step_instance.step_definition.id
        if step_id in [s.step_definition.id for s in executed_steps]:
            return self.context.get(step_id)  # Already executed, return cached result

        resolver = self._create_resolver(step_instance)
        step_result = resolver()

        self._write_result_to_context(step_id, step_result)
        executed_steps.append(step_instance)

        for reevaluated_instance in step_instance.reevaluates:
            self._run_step(reevaluated_instance, executed_steps)

        return step_result