# TradeX Strategy Platform

Based on LOM lesson (Inside the Pressure Cooker)[https://languageofmarkets.com/inside-the-pressure-cooker/]

A flexible trading strategy execution platform with clear separation between decision logic and execution infrastructure.

## Domain Architecture

### Core Principles

The platform follows a clear separation of concerns:

- **Strategies** = Trade Decision Logic
- **Providers** = Trade Execution Infrastructure

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Strategies    │    │ Trading Session │    │   Providers     │
│                 │    │                 │    │                 │
│ • Decision      │◄──►│ • Orchestration │◄──►│ • Data Sources  │
│ • Analysis      │    │ • Symbol Mapping│    │ • Execution     │
│ • Signals       │    │ • Risk Mgmt     │    │ • Order Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
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
- Provider-agnostic (don't know about specific data sources or brokers)
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
    static_config: {}
    dynamic_config: {}
  
  - system_step_id: find_extreme
    description: "Identify extreme pivot points in the trend"
    static_config: {}
    dynamic_config:
      trend: "trend"  # From detect_trend step
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
- **Yahoo Finance Provider**: Fetch real-time and historical data

#### Execution Providers

Planned support for:
- Interactive Brokers
- Alpaca
- TD Ameritrade
- Other brokers and exchanges

### 3. Trading Sessions (Orchestration)

**Purpose**: Coordinate between strategies and providers

**Responsibilities**:
- Map strategy symbols to provider symbols
- Manage data provider and execution provider connections
- Apply session-level constraints and risk limits
- Coordinate strategy execution with available data/execution

## Real-World Constraints

### Data vs Execution Separation

In real trading environments:
- **Data Source**: Get market data from Provider A (e.g., CSV files, Bloomberg)
- **Execution**: Execute trades on Provider B (e.g., Interactive Brokers, Alpaca)
- **Instrument Availability**: Not all instruments are available on all providers

### Symbol Configuration Split

To handle these constraints, symbol configuration is split into two parts:

```python
# Data Provider Configuration
class DataSymbolConfig:
    symbol: str
    provider: str  # "csv", "yahoo", "bloomberg"
    timeframe: CustomTimeframe
    feed_config: Dict[str, str]
    available: bool = True

# Trading/Execution Configuration  
class TradingSymbolConfig:
    symbol: str
    execution_provider: str  # "ib", "alpaca", "tda"
    data_provider: str  # Where to get data from
    risk_limits: Optional[RiskConfig] = None
    enabled: bool = True
```

## Configuration Flow

1. **Strategy Definition**: Define decision logic and required symbols
2. **Session Configuration**: Map strategy symbols to available providers
3. **Provider Setup**: Configure data and execution providers
4. **Runtime Execution**: Session orchestrates strategy execution using configured providers

## Example Configuration

```yaml
# Strategy (Decision Logic)
strategies:
  trend_following:
    name: "Trend Following Strategy"
    symbols: ["AAPL", "MSFT"]  # What to trade
    steps: [...]  # How to trade

# Session (Orchestration)
trading_sessions:
  main_session:
    name: "Main Trading Session"
    strategies: ["trend_following"]
    symbol_mapping:
      AAPL:
        data_provider: "csv"
        execution_provider: "ib"
      MSFT:
        data_provider: "yahoo"
        execution_provider: "alpaca"

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

## Benefits of This Architecture

1. **Flexibility**: Strategies can work with any combination of data/execution providers
2. **Reusability**: Strategies are provider-agnostic and can be deployed across different environments
3. **Maintainability**: Clear separation makes it easier to modify decision logic or infrastructure independently
4. **Scalability**: Easy to add new providers or strategies without affecting existing components
5. **Real-world Compliance**: Handles the reality that data sources and execution venues are often separate

## Getting Started

[Documentation for setup and usage will go here]

## Development

[Development guidelines will go here]