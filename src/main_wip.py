# app/main_wip.py
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from core.container.root import RootContainer
from loaders.trading_config_loader import TradingConfigLoader

# Load environment variables
load_dotenv()

# Initialize container with paths from environment
container = RootContainer()

# At module level
PROJECT_ROOT = Path(__file__).parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"

# Then use these constants for configuration
container.config.strategies.dir.from_value(CONFIGS_DIR / "strategies")
container.config.step_registry.registry_file.from_value(CONFIGS_DIR / "strategy_steps.yaml")
container.config.price_feeds.providers_dir.from_value(CONFIGS_DIR / "providers")


@inject
def run_trading_system(
    strategies = Provide[RootContainer.strategies.strategies],
    price_feeds = Provide[RootContainer.price_feeds.all_providers]
):
    """
    Main entry point for the trading system.
    
    This orchestrates the complete trading workflow:
    1. Load portfolio configuration
    2. Load trading session configurations  
    3. Initialize sessions with providers
    4. Execute strategies within sessions
    5. Track P&L and risk
    """
    
    # Step 1: Load system configuration
    config_loader = TradingConfigLoader(CONFIGS_DIR / "trading_config.yaml")
    system_config = config_loader.load()
    
    # Step 2: Initialize portfolio
    portfolio = config_loader.create_portfolio()
    print(f"Initialized portfolio: {portfolio.name} with ${portfolio.initial_capital}")
    
    # Step 3: Create price feeds
    price_feeds = config_loader.create_price_feeds()
    print(f"Created {len(price_feeds)} price feeds")
    
    # Step 4: Create trading sessions
    sessions = config_loader.create_trading_sessions(price_feeds, portfolio)
    print(f"Created {len(sessions)} trading sessions")
    
    # Step 5: Execute trading workflow
    for session_name, session in sessions.items():
        print(f"\n--- Executing Session: {session_name} ---")
        execute_session(session, strategies)
    
    # Step 6: Portfolio summary
    print("\n--- Portfolio Summary ---")
    print(f"Total P&L: ${portfolio.get_total_pnl()}")
    print(f"Current Capital: ${portfolio.get_current_capital()}")


def execute_session(session, strategies):
    """
    Execute all strategies within a trading session.
    
    Args:
        session: Trading session instance
        strategies: Available strategies
    """
    print(f"Session: {session.name}")
    print(f"Symbols: {list(session.symbols.keys())}")
    
    # For each symbol in the session
    for symbol_name, symbol_config in session.symbols.items():
        print(f"\n  Processing symbol: {symbol_name}")
        
        # Get price data for the symbol
        try:
            price_data = session.get_price_data(symbol_name)
            print(f"    Loaded {len(price_data)} bars of price data")
            
            # Execute strategies for this symbol
            for strategy_name in session.strategies:
                if strategy_name in strategies:
                    strategy = strategies[strategy_name]
                    print(f"    Running strategy: {strategy.name}")
                    
                    # TODO: Execute strategy with price data
                    # This will be implemented in Phase 3 of the project plan
                    print("      Strategy execution not yet implemented")
                else:
                    print(f"    Warning: Strategy '{strategy_name}' not found")
                    
        except Exception as e:
            print(f"    Error processing {symbol_name}: {e}")


if __name__ == "__main__":
    container.wire(modules=[__name__])
    run_trading_system()