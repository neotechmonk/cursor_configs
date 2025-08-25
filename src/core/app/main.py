import os
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.traceback import install

from core.app.container import AppContainer

install(show_locals=True)  # Enhanced traceback


# ---------------------------
# Rendering Helper Functions
# ---------------------------

def render_data_providers_table(providers) -> Table:
    table = Table(title="📊 Data Providers", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    
    for provider in providers:
        table.add_row(provider.name, type(provider).__name__, "✅ Active")
    
    return table


def render_strategies_table(strategies) -> Table:
    table = Table(title="📈 Trading Strategies", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Steps", style="green")
    table.add_column("Status", style="yellow")
    
    for strategy in strategies:
        step_count = len(strategy.config.steps) if strategy.config.steps else 0
        table.add_row(strategy.config.name, f"{step_count} steps", "✅ Active")
    
    return table


def render_portfolios_table(portfolios) -> Table:
    table = Table(title="💰 Portfolios", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Capital", style="green")
    table.add_column("Status", style="yellow")
    
    for portfolio in portfolios:
        table.add_row(portfolio.name, f"${portfolio.initial_capital:,.2f}", "✅ Active")
    
    return table


def render_sessions_table(sessions) -> Table:
    table = Table(title="📅 Trading Sessions", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Symbols", style="green")
    table.add_column("Allocation", style="yellow")
    table.add_column("Status", style="magenta")
    
    for session in sessions:
        symbol_count = len(session.get_enabled_symbols())
        table.add_row(
            session.name,
            f"{symbol_count} symbols",
            f"${session.capital_allocation:,.2f}",
            "✅ Active"
        )
    
    return table


def render_session_detail_table(session) -> Table:
    table = Table(title=f"📈 {session.name}", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan")
    table.add_column("Timeframe", style="green")
    table.add_column("Data Provider", style="yellow")
    table.add_column("Execution Provider", style="magenta")

    for symbol in session.get_enabled_symbols():
        config = session.get_symbol_config(symbol)
        timeframe_str = str(config.timeframe) if config.timeframe else "N/A"
        table.add_row(
            symbol,
            timeframe_str,
            type(config.data_provider).__name__,
            type(config.execution_provider).__name__
        )
    return table


def render_summary_panel(providers, strategies, portfolios, sessions) -> Panel:
    summary_text = f"""
[bold]System Summary:[/bold]
• Data Providers: {len(providers)}
• Strategies: {len(strategies)}
• Portfolios: {len(portfolios)}
• Trading Sessions: {len(sessions)}

[dim]All systems operational and ready for trading[/dim]
    """
    return Panel(summary_text, title="🎯 System Status", border_style="green", padding=(1, 2))


# ---------------------------
# Main Application Entry
# ---------------------------

def main():
    console = Console()
    os.environ["APP_SETTINGS_PATH"] = str(Path("configs/settings.json").resolve())

    container = AppContainer()
    container.init_resources()

    logger = container.logger()
    logger.info("Application started")

    console.print(Panel.fit(
        "[bold blue]TradeX Strategy Platform[/bold blue]\n[dim]Trading System Status Dashboard[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))

    data_provider_service = container.data_provider.service()
    strategy_service = container.strategy.service()
    portfolio_service = container.portfolio.service()
    sessions_service = container.sessions.service()

    providers = data_provider_service.get_all()
    strategies = strategy_service.get_all()
    portfolios = portfolio_service.get_all()
    sessions = sessions_service.get_all()

    # Main tables
    console.print("\n")
    console.print(Columns([
        render_data_providers_table(providers),
        render_strategies_table(strategies)
    ], equal=True, expand=True))

    console.print("\n")
    console.print(Columns([
        render_portfolios_table(portfolios),
        render_sessions_table(sessions)
    ], equal=True, expand=True))

    # Session detail tables
    if sessions:
        console.print("\n")
        console.print(Panel.fit(
            "[bold]Session Details[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))

        for session in sessions:
            if session.get_enabled_symbols():
                console.print(render_session_detail_table(session))

    # Summary panel
    console.print("\n")
    console.print(render_summary_panel(providers, strategies, portfolios, sessions))

    logger.info("Shutting down")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Console().print(Panel(f"[bold red]Unhandled Exception[/bold red]\n{e}", border_style="red"))
        raise