from core.strategy.model import RawStrategyConfig, StrategyConfig, StrategyStepInstance
from core.strategy.steps.service import StrategyStepService


def hydrate_strategy_config(raw_config: RawStrategyConfig, step_service: StrategyStepService) -> StrategyConfig:
    """Convert raw YAML strategy config into a fully hydrated, linked StrategyConfig."""

    # First pass: build all step instances with placeholder reevaluates
    step_instances = []
    step_lookup = {}

    for raw_step in raw_config.steps:
        definition = step_service.get(raw_step.id)
        if not definition:
            raise ValueError(f"Step definition with id '{raw_step.id}' not found in StrategyStepService")

        instance = StrategyStepInstance(
            step_definition=definition,
            description=raw_step.description,
            config_bindings=raw_step.config_bindings,
            runtime_bindings=raw_step.runtime_bindings,
            reevaluates=[],  # temporarily empty
        )
        step_instances.append(instance)
        step_lookup[definition.id] = instance

    # Second pass: resolve reevaluate references to actual step definitions
    for raw_step, instance in zip(raw_config.steps, step_instances):
        for reevaluate_id in raw_step.reevaluates:
            if reevaluate_id not in step_lookup:
                raise ValueError(f"Reevaluated step id '{reevaluate_id}' not found in strategy steps")
            # Add the step definition, not the instance
            instance.reevaluates.append(step_lookup[reevaluate_id].step_definition)

    return StrategyConfig(name=raw_config.name, steps=step_instances)