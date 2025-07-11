from typing import Dict

from core.strategy.model import RawStrategyConfig, StrategyConfig, StrategyStepInstance
from core.strategy.steps.model import StrategyStepDefinition


def hydrate_strategy_config(
    raw_config: RawStrategyConfig,
    step_registry: Dict[str, StrategyStepDefinition]
) -> StrategyConfig:
    """
    Convert RawStrategyConfig into fully hydrated StrategyConfig with references resolved.

    This hydrates:
    - `id` → StrategyStepDefinition
    - `reevaluates` → List[StrategyStepInstance]
    """

    # First pass: build StrategyStepInstance WITHOUT reevaluates
    instance_map = {}
    for raw_step in raw_config.steps:
        definition = step_registry.get(raw_step.id)
        if not definition:
            raise ValueError(f"Step definition with id '{raw_step.id}' not found in registry")

        instance = StrategyStepInstance(
            id=definition,
            description=raw_step.description,
            config_bindings=raw_step.config_bindings,
            runtime_bindings=raw_step.runtime_bindings,
            reevaluates=[]  # To be populated in second pass
        )
        instance_map[raw_step.id] = instance

    # Second pass: resolve reevaluates to StrategyStepInstance references
    for raw_step in raw_config.steps:
        current_instance = instance_map[raw_step.id]
        current_instance.reevaluates = []
        for reevaluate_id in raw_step.reevaluates:
            reevaluated_instance = instance_map.get(reevaluate_id)
            if not reevaluated_instance:
                raise ValueError(f"Reevaluated step id '{reevaluate_id}' not found in strategy steps")
            current_instance.reevaluates.append(reevaluated_instance)

    return StrategyConfig(
        name=raw_config.name,
        steps=list(instance_map.values())
    )
