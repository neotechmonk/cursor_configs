
from core.strategy.steps.model import StrategyStepDefinition
from util.custom_cache import Cache


class StrategyStepService:
    def __init__(self, cache:Cache[StrategyStepDefinition]):
        self.cache: Cache = cache

    def get(self, name: str) -> StrategyStepDefinition:
        if not (step := self.cache.get(name)):
            raise ValueError(f"Step {name} not found in the cache. Check if container is properly initialized.")
        return step

    def get_all(self) -> list[StrategyStepDefinition]:
        return self.cache.get_all()

    def clear_cache(self) -> None:
        self.cache.clear()