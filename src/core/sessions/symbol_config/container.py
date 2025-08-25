from dependency_injector import containers, providers

from core.sessions.symbol_config.adapter import SymbolDictAdapter, SymbolYamlAdapter
from core.sessions.symbol_config.model import RawSymbolConfig, SymbolConfigModel
from core.sessions.symbol_config.transformer import (
    SymbolTransformer,  # if class/callable
)
from core.shared.config import ReadOnlyConfigService


class SymbolsContainer(containers.DeclarativeContainer):
    # --- config / deps -------------------------------------------------------
    config = providers.Configuration()  # expects: adapter.kind in {"dict","yaml","external"}

    # When using dict-adapter (mapping comes from the loaded session)
    symbols_mapping = providers.Dependency()  # dict[str, dict] or Mapping[str, Any]

    # When using yaml-adapter
    yaml_path = providers.Configuration("yaml").path  # e.g., "session.yaml"

    # Optional external adapter override (for tests/custom sources)
    external_adapter = providers.Dependency()

    # Optional cache
    cache = providers.Dependency()

    # --- adapter providers ---------------------------------------------------
    dict_adapter = providers.Factory(
        SymbolDictAdapter,
        symbols=symbols_mapping,
    )

    yaml_adapter = providers.Factory(
        SymbolYamlAdapter,
        path=yaml_path,
    )

    adapter = providers.Selector(
        config.adapter.kind,
        dict=dict_adapter,
        yaml=yaml_adapter,
        external=external_adapter,
    )

    # --- transformer provider ------------------------------------------------
    transformer = providers.Factory(SymbolTransformer)

    # --- service -------------------------------------------------------------
    service = providers.Factory(
        ReadOnlyConfigService[str, RawSymbolConfig, SymbolConfigModel],
        adapter=adapter,
        transformer=transformer,
        cache=cache,
    )