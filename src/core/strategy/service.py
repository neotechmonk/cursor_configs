from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core.strategy.hydration import hydrate_strategy_config
from core.strategy.model import RawStrategyConfig, Strategy, StrategyConfig
from core.strategy.protocol import StrategyProtocol
from core.strategy.steps.service import StrategyStepService
from util.yaml_config_loader import load_yaml_config
from util.custom_cache import Cache


@dataclass
class StrategyService:
    config_dir:Path 
    cache: Cache  = field(default_factory=Cache)
    model_hydration_fn: Callable[[RawStrategyConfig, StrategyStepService], StrategyConfig] = field(default_factory=hydrate_strategy_config)
    steps_registry: StrategyStepService = field(default_factory=StrategyStepService)

    def _load_strategy_by_name(self, name: str) -> StrategyProtocol:
            path = self.config_dir / f"{name}.yaml"
            raw_dict = load_yaml_config(path)
            raw_dict["name"] = name  
            raw_config = RawStrategyConfig(**raw_dict)
            hydrated = self.model_hydration_fn(raw_config, self.steps_registry)
            return Strategy(config=hydrated)

    def get(self, name: str) -> StrategyProtocol:
        if not (strategy := self.cache.get(name)):
            strategy = self._load_strategy_by_name(name)
            self.cache.add(name, strategy)
        return strategy

    def get_all(self) -> list[StrategyProtocol]:
        for path in self.config_dir.glob("*.yaml"):
            name = path.stem
            if not self.cache.get(name):
                self.cache.add(name, self._load_strategy_by_name(name))
        return list(self.cache.get_all())

    def clear_cache(self) -> None:
        self.cache.clear()