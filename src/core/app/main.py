import os
from pathlib import Path

from core.app.container import AppContainer


def main():
    # Explicitly set the config path via environment variable
    os.environ["APP_SETTINGS_PATH"] = str(Path("configs/settings.json").resolve())

    # Initialise the container
    container = AppContainer()
    container.init_resources()  # Triggers logging setup, etc.

    # Access the logger (DI provided)
    logger = container.logger()
    logger.info("Application started")

    # Access config for further use
    logger.debug("Settings loaded successfully")

    # Example: use a subcontainer or resource

    # Get the data provider service and list all available providers
    data_provider_service = container.data_provider.service()
    providers = data_provider_service.get_all()
    print(f"Available data providers: {[provider.name for provider in providers]}")

    # Strategy service
    strategy_container = container.strategy
    # strategy_container.init_resources()
    strategies = strategy_container.service().get_all()
    print(f"Available strategies: {[strategy.config.name for strategy in strategies]}")

    logger.info("Shutting down")

if __name__ == "__main__":
    main()