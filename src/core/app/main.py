import os
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.app.container import AppContainer


def main():
    # Initialize rich console
    console = Console()
    
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

    # Create a beautiful header
    console.print(Panel.fit(
        "[bold blue]TradeX Strategy Platform[/bold blue]\n[dim]Trading System Status Dashboard[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))

    # Get the data provider service and list all available providers
    data_provider_service = container.data_provider.service()
    providers = data_provider_service.get_all()
    
    # Create providers table
    providers_table = Table(title="📊 Data Providers", box=box.ROUNDED, show_header=True)
    providers_table.add_column("Name", style="cyan", no_wrap=True)
    providers_table.add_column("Type", style="green")
    providers_table.add_column("Status", style="yellow")
    
    for provider in providers:
        providers_table.add_row(
            provider.name,
            type(provider).__name__,
            "✅ Active"
        )

    # Strategy service
    strategy_container = container.strategy
    strategy_service = strategy_container.service()
    strategies = strategy_service.get_all()
    
    # Create strategies table
    strategies_table = Table(title="�� Trading Strategies", box=box.ROUNDED, show_header=True)
    strategies_table.add_column("Name", style="cyan", no_wrap=True)
    strategies_table.add_column("Steps", style="green")
    strategies_table.add_column("Status", style="yellow")
    
    for strategy in strategies:
        step_count = len(strategy.config.steps) if strategy.config.steps else 0
        strategies_table.add_row(
            strategy.config.name,
            f"{step_count} steps",
            "✅ Active"
        )

    # Portfolio service
    portfolio_container = container.portfolio
    portfolio = portfolio_container.service()
    portfolios = portfolio.get_all()
    
    # Create portfolios table
    portfolios_table = Table(title="💰 Portfolios", box=box.ROUNDED, show_header=True)
    portfolios_table.add_column("Name", style="cyan", no_wrap=True)
    portfolios_table.add_column("Capital", style="green")
    portfolios_table.add_column("Status", style="yellow")
    
    for portfolio in portfolios:
        portfolios_table.add_row(
            portfolio.name,
            f"${portfolio.initial_capital:,.2f}",
            "✅ Active"
        )

    # Sessions service
    sessions_service = container.sessions.service()
    sessions = sessions_service.get_all()
    
    # Create sessions table
    sessions_table = Table(title=" Trading Sessions", box=box.ROUNDED, show_header=True)
    sessions_table.add_column("Name", style="cyan", no_wrap=True)
    sessions_table.add_column("Symbols", style="green")
    sessions_table.add_column("Allocation", style="yellow")
    sessions_table.add_column("Status", style="magenta")
    
    for session in sessions:
        enabled_symbols = session.get_enabled_symbols()
        symbol_count = len(enabled_symbols)
        sessions_table.add_row(
            session.name,
            f"{symbol_count} symbols",
            f"${session.capital_allocation:,.2f}",
            "✅ Active"
        )

    # Display all tables in a nice layout
    console.print("\n")
    console.print(Columns([providers_table, strategies_table], equal=True, expand=True))
    console.print("\n")
    console.print(Columns([portfolios_table, sessions_table], equal=True, expand=True))

    # Show detailed session information
    if sessions:
        console.print("\n")
        console.print(Panel.fit(
            "[bold]Session Details[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))
        
        for session in sessions:
            if session.get_enabled_symbols():
                session_table = Table(title=f"📈 {session.name}", box=box.ROUNDED, show_header=True)
                session_table.add_column("Symbol", style="cyan", no_wrap=True)
                session_table.add_column("Timeframe", style="green")
                session_table.add_column("Data Provider", style="yellow")
                session_table.add_column("Execution Provider", style="magenta")
                
                for symbol in session.get_enabled_symbols():
                    config = session.get_symbol_config(symbol)
                    # Convert CustomTimeframe to string
                    timeframe_str = str(config.timeframe) if config.timeframe else "N/A"
                    session_table.add_row(
                        symbol,
                        timeframe_str,
                        type(config.data_provider).__name__,
                        type(config.execution_provider).__name__
                    )
                
                console.print(session_table)

    # Create a summary panel
    total_providers = len(providers)
    total_strategies = len(strategies)
    total_portfolios = len(portfolios)
    total_sessions = len(sessions)
    
    summary_text = f"""
    [bold]System Summary:[/bold]
    • Data Providers: {total_providers}
    • Strategies: {total_strategies}
    • Portfolios: {total_portfolios}
    • Trading Sessions: {total_sessions}
    
    [dim]All systems operational and ready for trading[/dim]
    """
    
    console.print("\n")
    console.print(Panel(
        summary_text,
        title="🎯 System Status",
        border_style="green",
        padding=(1, 2)
    ))

    logger.info("Shutting down")


if __name__ == "__main__":
    main()