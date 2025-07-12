from dependency_injector import containers, providers

from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.service import StrategyStepService
from core.strategy.steps.settings import StrategyStepSettings
from util.yaml_config_loader import load_yaml_config
from util.custom_cache import ScopedCacheView, WatchedCache

NAMESPACE = "strategy_steps"


class StrategyStepContainer(containers.DeclarativeContainer):
    """Container for managing strategy step dependencies."""

    # Configuration dependency (injected externally)
    settings = providers.Dependency(instance_of=StrategyStepSettings, default=StrategyStepSettings())

    # Cache backend (shared)
    cache_backend = providers.Singleton(WatchedCache)

    # Scoped cache for strategy steps
    cache = providers.Singleton(
        ScopedCacheView,
        cache_backend,
        NAMESPACE,
    )

    # Load strategy steps from YAML
    strategy_steps = providers.Singleton(
        lambda config_path: [
            StrategyStepDefinition(**step)
            for step in load_yaml_config(config_path)
        ],
        settings.provided.config_path,
    )

    # Resource: populate cache as a side effect (runs on container.init_resources())
    cache_populator = providers.Resource(
        lambda cache, steps: [cache.add(step.id, step) for step in steps],
        cache=cache,
        steps=strategy_steps,
    )

    # Main service
    service = providers.Singleton(
        StrategyStepService,
        cache=cache,
    )