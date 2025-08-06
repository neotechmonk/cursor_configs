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
    strategy_service = strategy_container.service()
    print(f"Available strategies: {[strategy.config.name for strategy in strategy_service.get_all()]}")
    main_strategy = strategy_service.get("sample_strategy")
    print(f"Strategy steps: {[step for step in main_strategy.config.steps]}")

    # Portfolio service
    portfolio_container = container.portfolio
    # portfolio_container.init_resources()
    portfolio = portfolio_container.service()
    print(f"Available portfolios: {[portfolio.name for portfolio in portfolio.get_all()]}")

    # Sessions service - NEW
    sessions_service = container.sessions.service()
    print(f"Available trading sessions: {[session.name for session in sessions_service.get_all()]}")
    
    # Get a specific session and show details
    if sessions_service.get_all():
        day_trading_session = sessions_service.get("day_trading")
        print(f"Session '{day_trading_session.name}' has {len(day_trading_session.get_enabled_symbols())} enabled symbols")
        
        # Show session details
        for symbol in day_trading_session.get_enabled_symbols():
            config = day_trading_session.get_symbol_config(symbol)
            print(f"  Symbol {symbol}: {config.timeframe} via {type(config.data_provider).__name__}")

    logger.info("Shutting down")

if __name__ == "__main__":
    main()