# TradeX Strategy Platform

Based on LOM lesson (Inside the Pressure Cooker)[https://languageofmarkets.com/inside-the-pressure-cooker/]

A flexible trading strategy execution platform with clear separation between decision logic and execution infrastructure.

## 🎯 Current Status

### ✅ System Running Successfully
The trading system is now operational with proper protocol compliance:

- **✅ Portfolio Management**: Capital management with $100,000 initial capital, proper P&L tracking
- **✅ Price Feed Integration**: Successfully loads 4308 bars of price data for CL symbol
- **✅ Session Orchestration**: Sessions coordinate between strategies and providers correctly
- **✅ Protocol Compliance**: All Portfolio and TradingSession protocols properly implemented
- **✅ Configuration System**: YAML configurations validated and loaded successfully
- **✅ End-to-End Execution**: Main workflow runs from portfolio initialization to P&L reporting

### 🚧 Next Phase: Strategy Execution Integration
The foundation is solid. Next priority is integrating the existing strategy framework with trading sessions for actual strategy execution.

## Domain Architecture

### Core Principles

The platform follows a clear separation of concerns:

- **Strategies** = Trade Decision Logic
- **Providers** = Trade Execution Infrastructure
- **Portfolios** = Capital Management
- **Sessions** = Strategy Orchestration

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Strategies    │    │ Trading Session │    │   Providers     │
│                 │    │                 │    │                 │
│ • Decision      │◄──►│ • Orchestration │◄──►│ • Data Sources  │
│ • Analysis      │    │ • Symbol Mapping│    │ • Execution     │
│ • Signals       │    │ • P&L Tracking  │    │ • Order Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Portfolio     │
                    │                 │
                    │ • Capital Mgmt  │
                    │ • Risk Limits   │
                    │ • P&L Rollup    │
                    └─────────────────┘
```

## Key Components

### 1. Strategies (Decision Logic)

**Purpose**: Define how to analyze market data and make trading decisions

**Responsibilities**:
- Market analysis (trend detection, pattern recognition)
- Signal generation (entry/exit points)
- Position sizing logic
- Risk management rules

**Characteristics**:
- **Provider-agnostic**: Don't know about specific data sources or brokers
- **Data-agnostic**: Don't specify where data comes from
- **Execution-agnostic**: Don't specify where trades are executed
- **Symbol-agnostic**: Don't specify which symbols to trade
- Pure business logic
- Configurable via YAML files

#### Strategy Configuration System

Strategies are defined using a step-based configuration system:

```yaml
# configs/strategies/trend_following.yaml
name: "Trend Following Strategy"
steps:
  - system_step_id: detect_trend
    description: "Determine the current market trend direction"
    static_config: {} # No config via yaml
    dynamic_config: {}
  
  # Step 4: Check Fibonacci extension
  - system_step_id: check_fib
    description: "Verify if price action meets Fibonacci extension criteria"
    static_config: # preconfigured via yaml 
      min: 0.50
      max: 0.75  
    dynamic_config:
      trend: "trend"  # From detect_trend step
      ref_swing_start_idx: "bar_index_start"  # From find_extreme step
      ref_swing_end_idx: "bar_index_end"  # From find_extreme step
    reevaluates:
      - detect_trend # check if first step still passes
```

**Key Features**:
- **Step-based execution**: Strategies are composed of reusable steps
- **Dependency management**: Steps can depend on outputs from previous steps
- **Reevaluation logic**: Steps can be re-evaluated when dependencies change
- **Dynamic configuration**: Steps can receive both static and dynamic parameters

**Step Registry**: All available steps are registered in `configs/strategy_steps.yaml`:

```yaml
steps:
  detect_trend:
    function: "src.utils.get_trend"
    input_params_map: {}
    return_map:
      trend: "_"  # Direct value from function return
```

Therefore strategies are recipes created using steps as ingredients 

### 2. Providers (Execution Infrastructure)

**Purpose**: Handle data access and trade execution

**Responsibilities**:
- Market data feeds (CSV, Yahoo Finance, real-time feeds)
- Order execution (brokers, exchanges)
- Position tracking
- Account management

**Characteristics**:
- Infrastructure-specific
- Handle real-world constraints (API limits, connectivity)
- Manage data formats and protocols

#### Data Providers

Currently supported:
- **CSV Provider**: Load historical data from CSV files
- **Yahoo Finance Provider**: Fetch real-time and historical data # TODO : needs refactoring. #YAGNI

#### Execution Providers #TODO : borrow from previous codebase

Planned support for:
- Interactive Brokers
- Binance

### 3. Portfolios (Capital Management)

**Purpose**: Manage capital allocation and centralized risk across multiple trading sessions

**Responsibilities**:
- Initial capital management
- **Centralized risk limits** (drawdown, position size, VaR)
- P&L aggregation from all sessions
- Account balance management
- Cross-session risk monitoring

**Characteristics**:
- **Multi-session support**: One portfolio can fund multiple sessions
- **Centralized risk management**: All risk limits managed at portfolio level
- **Capital allocation**: Control how much money goes to each session
- **Total portfolio protection**: Risk limits apply across all sessions
- **P&L rollup**: Aggregates P&L from all sessions

#### Portfolio Configuration Example

```yaml
# configs/portfolios/main_account.yaml
name: "Main Trading Account"
description: "Primary trading account for multiple strategies"

# Capital configuration
initial_capital: 100000.00
currency: "USD"

# Allocation strategy (extensible for future complex strategies)
allocation_strategy: "fixed"  # Current: fixed allocation based on initial capital

# Portfolio-level risk limits (apply across ALL sessions)
risk_limits:
  max_drawdown: 0.20          # 20% max loss across all sessions
  max_position_size: 10000.00 # Max $10K in any position
  var_limit: 5000.00          # Max $5K Value at Risk

# Session allocations
session_allocations:
  day_trading: 30000.00       # $30K for day trading
  swing_trading: 40000.00     # $40K for swing trading
  options_trading: 30000.00   # $30K for options
```

### 4. Trading Sessions (Orchestration)

**Purpose**: Coordinate between strategies and providers within allocated capital

**Responsibilities**:
- **Provider Mapping**: Map strategy symbols to specific data and execution providers
- **Symbol Configuration**: Define which symbols are available and how they're configured
- **Execution Constraints**: Apply session-level execution limits
- **Strategy Execution**: Coordinate strategy execution with available data/execution
- **Session P&L Tracking**: Track session-specific P&L for portfolio rollup

**Key Principle**: **Session-Based Mapping**
- All provider mapping decisions are made at the session level
- Sessions handle the complexity of connecting strategies to real-world providers
- **Single Source of Truth**: Session configuration is the only place where symbol-to-provider mapping is defined

#### Trading Session Configuration Example

```yaml
# configs/trading_sessions/day_trading.yaml
name: "Day Trading Session"
description: "High-frequency trading session for intraday strategies"

# Portfolio reference
portfolio: "main_account"
capital_allocation: 30000.00  # $30K from main account

# Strategies to run in this session
strategies:
  - "scalping"
  - "mean_reversion"

# Session-level execution constraints (not risk limits)
execution_limits:
  max_open_positions: 3       # Max 3 concurrent positions
  max_order_size: 5000.00     # Max order size for this session
  trading_hours:
    start: "09:30"
    end: "16:00"

# Symbol mapping - connects strategies to providers
symbol_mapping:
  AAPL:
    data_provider: "csv"           # Where to get market data
    execution_provider: "ib"       # Where to execute trades
    timeframe: "5m"               # Data timeframe
    enabled: true
  
  SPY:
    data_provider: "yahoo"
    execution_provider: "alpaca"
    timeframe: "1m"               # Higher frequency for SPY
    enabled: true
```

## P&L and Capital Management Architecture

### P&L Tracking Hierarchy
```
Session P&L → Portfolio P&L Rollup
```

- **Session Level**: Tracks session-specific P&L and equity
- **Portfolio Level**: Aggregates P&L from all sessions
- **Single Source of Truth**: Portfolio level for total P&L

### Capital Allocation Strategy
- **Current**: Fixed allocation based on initial capital
- **Extensible**: API designed to support complex allocation strategies
- **Risk Limits**: Always based on initial capital (conservative approach)

## Real-World Constraints

### Data vs Execution Separation

In real trading environments:
- **Data Source**: Get market data from Provider A (e.g., CSV files, Bloomberg)
- **Execution**: Execute trades on Provider B (e.g., Interactive Brokers, Alpaca)
- **Instrument Availability**: Not all instruments are available on all providers

### Session-Based Symbol Configuration

The trading session configuration handles all symbol-to-provider mapping:

```yaml
symbol_mapping:
  SYMBOL_NAME:
    data_provider: "provider_name"      # Where to get data
    execution_provider: "provider_name" # Where to execute trades
    timeframe: "timeframe"             # Data timeframe
    enabled: true/false               # Whether symbol is active
```

This single configuration handles:
- Data provider mapping
- Execution provider mapping  
- Timeframe configuration
- Symbol enable/disable

## Configuration Flow

1. **Portfolio Definition**: Define capital and centralized risk limits
2. **Strategy Definition**: Define decision logic (agnostic to providers/symbols)
3. **Session Configuration**: Map strategy symbols to available providers and allocate capital
4. **Provider Setup**: Configure data and execution providers
5. **Runtime Execution**: Session orchestrates strategy execution using configured providers within portfolio limits

## Example Configuration

```yaml
# Portfolio (Capital Management)
portfolios:
  main_account:
    name: "Main Trading Account"
    initial_capital: 100000.00
    allocation_strategy: "fixed"
    risk_limits:
      max_drawdown: 0.20          # 20% max loss across all sessions
      max_position_size: 10000.00 # Max $10K in any position
      var_limit: 5000.00          # Max $5K Value at Risk

# Strategy (Decision Logic) - Completely agnostic
strategies:
  trend_following:
    name: "Trend Following Strategy"
    steps: [...]  # How to trade (no symbol/provider references)

# Session (Orchestration) - Handles all mapping
trading_sessions:
  day_trading:
    name: "Day Trading Session"
    portfolio: "main_account"
    capital_allocation: 30000.00
    strategies: ["trend_following"]
    
    # Session handles all provider mapping
    symbol_mapping:
      AAPL:
        data_provider: "csv"        # Where to get data
        execution_provider: "ib"    # Where to execute trades
        timeframe: "5m"            # Data timeframe
        enabled: true
      SPY:
        data_provider: "yahoo"
        execution_provider: "alpaca"
        timeframe: "1m"
        enabled: true
    
    # Execution constraints (not risk limits)
    execution_limits:
      max_open_positions: 3
      trading_hours:
        start: "09:30"
        end: "16:00"

# Providers (Infrastructure)
providers:
  csv:
    type: "data"
    config: {...}
  yahoo:
    type: "data" 
    config: {...}
  ib:
    type: "execution"
    config: {...}
  alpaca:
    type: "execution"
    config: {...}
```

## Architecture Decisions

### Strategy Agnosticism
- **Data-agnostic**: Strategies don't specify data sources
- **Execution-agnostic**: Strategies don't specify execution venues
- **Symbol-agnostic**: Strategies don't specify which symbols to trade
- **Provider-agnostic**: Strategies don't know about specific providers

### Session-Based Mapping
- **Single Source of Truth**: Session configuration handles all symbol-to-provider mapping
- **Data Provider Mapping**: Sessions decide which data provider to use for each symbol
- **Execution Provider Mapping**: Sessions decide which execution provider to use for each symbol
- **Symbol Configuration**: Sessions define which symbols are available and their configurations

### Portfolio-Session Relationship
- **One-to-Many**: One portfolio can fund multiple sessions
- **Capital Allocation**: Sessions operate within allocated portfolio capital
- **Centralized Risk**: All risk management at portfolio level
- **Execution Constraints**: Session-level execution limits only

### Risk Management Approach
- **Portfolio Level**: All risk limits (drawdown, position size, VaR)
- **Session Level**: Only execution constraints (position count, trading hours, order size)
- **Rationale**: Protect total portfolio value regardless of which session is trading

### P&L and Capital Management
- **P&L Hierarchy**: Session P&L rolls up to portfolio level
- **Allocation Strategy**: Fixed allocation based on initial capital (extensible API)
- **Risk Limits**: Always based on initial capital (conservative approach)

## Service Architecture Pattern

The platform follows a clean service architecture pattern that separates business logic from infrastructure concerns:

### Protocol → Service → Container Pattern

Each component follows a three-layer architecture, using **Portfolio** as the example:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Protocol      │    │   Service       │    │   Container     │
│                 │    │                 │    │                 │
│ • Interface     │◄──►│ • Business      │◄──►│ • DI            │
│ • Contract      │    │   Logic         │    │   Configuration │
│ • Type Safety   │    │ • Pure Logic    │    │ • Dependencies  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### 1. Protocol Layer (Interface Definition)
- **Purpose**: Define contracts and interfaces
- **Characteristics**: Pure interface definitions, no implementation
- **Portfolio Example**: `PortfolioProtocol`, `PortfolioServiceProtocol`
- **Benefits**: Type safety, clear contracts, runtime checking

```python
# src/core/portfolio/protocol.py
@runtime_checkable
class PortfolioProtocol(Protocol):
    """Protocol for portfolio implementations."""
    
    @property
    def name(self) -> str: ...
    @property
    def initial_capital(self) -> Decimal: ...
    def get_current_equity(self) -> Decimal: ...
    def can_open_position(self, symbol: str, quantity: Decimal, price: Decimal) -> bool: ...

class PortfolioServiceProtocol(Protocol):
    """Protocol for portfolio services."""
    def get(self, name: str) -> PortfolioProtocol: ...
    def get_all(self) -> list[PortfolioProtocol]: ...
```

#### 2. Service Layer (Business Logic)
- **Purpose**: Implement business logic and domain operations
- **Characteristics**: Pure business logic, no infrastructure dependencies
- **Portfolio Example**: `PortfolioService`, `Portfolio` (concrete implementation)
- **Benefits**: Testable, reusable, infrastructure-agnostic

```python
# src/core/portfolio/portfolio.py
class PortfolioService:
    """Portfolio business logic service."""
    
    def __init__(self, settings: PortfolioSettings, cache: Dict[str, PortfolioProtocol]):
        self.settings = settings
        self.cache = cache

    def get(self, name: str) -> PortfolioProtocol:
        """Get portfolio by name with caching."""
        if name not in self.cache:
            self.cache[name] = self._load_portfolio_by_name(name)
        return self.cache[name]

    def _load_portfolio_by_name(self, name: str) -> PortfolioProtocol:
        """Load portfolio from configuration."""
        path = self.settings.config_dir / f"{name}.yaml"
        config = load_yaml_config(path, PortfolioConfig)
        return Portfolio(name=name, description=config.description, initial_capital=config.initial_capital)
```

#### 3. Container Layer (Dependency Injection)
- **Purpose**: Configure dependencies and wire components together
- **Characteristics**: Infrastructure concerns, dependency management
- **Portfolio Example**: `PortfolioContainer`
- **Benefits**: Loose coupling, testable, configurable

```python
# src/core/portfolio/container.py
class PortfolioContainer(containers.DeclarativeContainer):
    """Dependency injection container for portfolio components."""
    
    config = providers.Configuration()
    settings = providers.Dependency(instance_of=PortfolioSettings)
    portfolio_cache = providers.Singleton(dict)

    service = providers.Factory(
        PortfolioService,
        settings=settings,
        cache=portfolio_cache,
    )
```

### Settings Management

Settings follow a hierarchical configuration pattern:

#### 1. Application Settings
- **Purpose**: Global application configuration
- **Source**: Environment variables, config files, command line
- **Example**: `AppSettings`

```python
# src/core/app/settings.py
class AppSettings(BaseSettings):
    """Global application settings."""
    portfolio: PortfolioSettings
    # Other component settings...
```

#### 2. Component Settings
- **Purpose**: Component-specific configuration
- **Source**: YAML files, environment variables
- **Portfolio Example**: `PortfolioSettings`

```python
# src/core/portfolio/portfolio.py
class PortfolioSettings(BaseSettings):
    """Portfolio-specific settings."""
    config_dir: Path = Field(default=Path("configs/portfolios"))
```

#### 3. Configuration Models
- **Purpose**: Validate and structure configuration data
- **Source**: YAML files
- **Portfolio Example**: `PortfolioConfig`

```python
# src/core/portfolio/portfolio.py
class PortfolioConfig(BaseModel):
    """Pydantic model for portfolio configuration."""
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    initial_capital: float = Field(..., gt=0)
```

### Configuration Flow

```
YAML File → PortfolioConfig → Portfolio → PortfolioService → PortfolioContainer
```

1. **YAML File** (`configs/portfolios/demo.yaml`):
   ```yaml
   description: Demo Portfolio
   initial_capital: 10000
   ```

2. **PortfolioConfig** (Validation):
   ```python
   config = load_yaml_config(path, PortfolioConfig)
   # Validates: name required, initial_capital > 0
   ```

3. **Portfolio** (Concrete Implementation):
   ```python
   portfolio = Portfolio(
       name=name,
       description=config.description,
       initial_capital=config.initial_capital
   )
   ```

4. **PortfolioService** (Business Logic):
   ```python
   service = PortfolioService(settings, cache)
   portfolio = service.get("demo")  # Loads and caches
   ```

5. **PortfolioContainer** (DI Configuration):
   ```python
   container = PortfolioContainer()
   service = container.service()  # Injected dependencies
   ```

### Benefits of This Architecture

#### 1. Separation of Concerns
- **Protocols**: Define what components can do
- **Services**: Implement how they do it
- **Containers**: Configure when and where they do it
- **Settings**: Control what they work with

#### 2. Testability
- **Services**: Can be tested without DI framework
- **Protocols**: Enable mocking and interface testing
- **Containers**: Can be tested independently
- **Settings**: Can be mocked for testing

#### 3. Flexibility
- **Protocols**: Enable multiple implementations
- **Services**: Can be swapped without changing business logic
- **Containers**: Can configure different dependency combinations
- **Settings**: Can adapt to different environments

#### 4. Maintainability
- **Clear Boundaries**: Each layer has a specific responsibility
- **Loose Coupling**: Changes in one layer don't affect others
- **Type Safety**: Protocols ensure correct implementations
- **Configuration**: Settings centralize configuration management

### Usage Example

```python
# Clean import from module
from core.portfolio import Portfolio, PortfolioService, PortfolioProtocol

# Create service with settings
settings = PortfolioSettings(config_dir=Path("configs/portfolios"))
service = PortfolioService(settings=settings, cache={})

# Use service (business logic)
portfolio = service.get("demo")
assert isinstance(portfolio, PortfolioProtocol)  # Runtime checking

# Or use container (DI)
container = PortfolioContainer()
container.settings.override(settings)
service = container.service()
portfolio = service.get("demo")
```

This architecture ensures that business logic is clean, testable, and independent of infrastructure concerns while maintaining type safety and clear contracts.

## Benefits of This Architecture

1. **Flexibility**: Strategies can work with any combination of data/execution providers
2. **Reusability**: Strategies are provider-agnostic and can be deployed across different environments
3. **Maintainability**: Clear separation makes it easier to modify decision logic or infrastructure independently
4. **Scalability**: Easy to add new providers or strategies without affecting existing components
5. **Real-world Compliance**: Handles the reality that data sources and execution venues are often separate
6. **Strategy Portability**: Strategies can be moved between different trading environments without modification
7. **Simplicity**: Single configuration point for all symbol-to-provider mapping
8. **Capital Management**: Proper separation of capital management from strategy execution
9. **Centralized Risk**: Portfolio-level risk management protects total capital across all sessions
10. **Clear Separation**: Risk limits vs execution constraints are clearly separated
11. **P&L Transparency**: Clear hierarchy of P&L tracking from session to portfolio
12. **Extensible Allocation**: API designed to support future complex allocation strategies

## Getting Started

### Prerequisites
- Python 3.12+
- uv package manager

### Quick Start

1. **Clone and setup**:
```bash
git clone <repository-url>
cd tradex_strategy_pc
uv sync
```

2. **Run the trading system**:
```bash
uv run python -m src.main_wip
```

This will:
- Load portfolio configuration with $100,000 initial capital
- Initialize CSV price feed provider
- Create trading session with CL symbol
- Load 4308 bars of price data
- Execute session workflow
- Display portfolio P&L summary

### Expected Output
```
Initialized portfolio: Main Portfolio with $100000.0
Created 1 price feeds
Created 1 trading sessions

--- Executing Session: main_session ---
Session: Main Trading Session
Symbols: ['CL']

  Processing symbol: CL
    Loaded 4308 bars of price data
    Warning: Strategy 'trend_following' not found

--- Portfolio Summary ---
Total P&L: $0
Current Capital: $100000.0
```

### Configuration
The system uses YAML configuration files in the `configs/` directory:
- `trading_config.yaml` - Main system configuration
- `strategies/` - Strategy definitions
- `providers/` - Provider configurations

## Development

[Development guidelines will go here]