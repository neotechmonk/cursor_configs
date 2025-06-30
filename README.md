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

### 3. Trading Sessions (Orchestration)

**Purpose**: Coordinate between strategies and providers

**Responsibilities**:
- **Provider Mapping**: Map strategy symbols to specific data and execution providers
- **Symbol Configuration**: Define which symbols are available and how they're configured
- **Session Constraints**: Apply session-level limits and rules (to be defined)
- **Strategy Execution**: Coordinate strategy execution with available data/execution

**Key Principle**: **Session-Based Mapping**
- All provider mapping decisions are made at the session level
- Sessions handle the complexity of connecting strategies to real-world providers
- **Single Source of Truth**: Session configuration is the only place where symbol-to-provider mapping is defined

#### Trading Session Configuration Example

```yaml
# configs/trading_sessions/main_session.yaml
name: "Main Trading Session"
description: "Primary trading session for equity strategies"

# Strategies to run in this session
strategies:
  - "trend_following"
  - "mean_reversion"

# Portfolio configuration
portfolio:
  name: "Main Portfolio"
  initial_capital: 100000.00
  risk_limits:
    max_position_size: 10000.00
    max_drawdown: 0.10
    stop_loss_pct: 0.02
    take_profit_pct: 0.04

# Symbol mapping - connects strategies to providers
symbol_mapping:
  AAPL:
    data_provider: "csv"           # Where to get market data
    execution_provider: "ib"       # Where to execute trades
    timeframe: "1d"               # Data timeframe
    enabled: true
    risk_config:
      max_position_size: 5000.00  # Symbol-specific limits
      stop_loss_pct: 0.015
  
  MSFT:
    data_provider: "yahoo"
    execution_provider: "alpaca"
    timeframe: "1d"
    enabled: true
    risk_config:
      max_position_size: 3000.00
  
  CL:  # Crude Oil futures
    data_provider: "csv"
    execution_provider: "ib"
    timeframe: "5m"               # Different timeframe for futures
    enabled: true
    risk_config:
      max_position_size: 2000.00  # Lower limits for futures

# Session-level constraints (to be defined)
constraints:
  trading_hours:
    start: "09:30"
    end: "16:00"
  max_open_positions: 5
  correlation_limit: 0.7
```

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
- Symbol-specific risk limits (when needed)

## Configuration Flow

1. **Strategy Definition**: Define decision logic (agnostic to providers/symbols)
2. **Session Configuration**: Map strategy symbols to available providers
3. **Provider Setup**: Configure data and execution providers
4. **Runtime Execution**: Session orchestrates strategy execution using configured providers

## Example Configuration

```yaml
# Strategy (Decision Logic) - Completely agnostic
strategies:
  trend_following:
    name: "Trend Following Strategy"
    steps: [...]  # How to trade (no symbol/provider references)

# Session (Orchestration) - Handles all mapping
trading_sessions:
  main_session:
    name: "Main Trading Session"
    strategies: ["trend_following"]
    
    # Session handles all provider mapping
    symbol_mapping:
      AAPL:
        data_provider: "csv"        # Where to get data
        execution_provider: "ib"    # Where to execute trades
        timeframe: "1d"            # Data timeframe
        enabled: true
      MSFT:
        data_provider: "yahoo"
        execution_provider: "alpaca"
        timeframe: "1d"
        enabled: true

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

### Trading Session Limits
- **Status**: To be defined based on specific requirements
- **Potential areas**: Risk limits, position size limits, trading hours, compliance rules

## Benefits of This Architecture

1. **Flexibility**: Strategies can work with any combination of data/execution providers
2. **Reusability**: Strategies are provider-agnostic and can be deployed across different environments
3. **Maintainability**: Clear separation makes it easier to modify decision logic or infrastructure independently
4. **Scalability**: Easy to add new providers or strategies without affecting existing components
5. **Real-world Compliance**: Handles the reality that data sources and execution venues are often separate
6. **Strategy Portability**: Strategies can be moved between different trading environments without modification
7. **Simplicity**: Single configuration point for all symbol-to-provider mapping

## Getting Started

[Documentation for setup and usage will go here]

## Development

[Development guidelines will go here]