# TradeX Strategy Platform - Project Plan

## Project Overview

TradeX Strategy Platform is a flexible trading strategy execution platform with clear separation between decision logic and execution infrastructure, based on the LOM lesson "Inside the Pressure Cooker".

## Architecture Alignment

This project plan follows the core architecture principles defined in README.md:

- **Strategies** = Trade Decision Logic (Provider-agnostic)
- **Providers** = Trade Execution Infrastructure  
- **Portfolios** = Capital Management (Centralized risk)
- **Sessions** = Strategy Orchestration (Provider mapping)

## Current Status

### ✅ Completed Components

#### 1. Core Infrastructure
- [x] Basic project structure and configuration
- [x] Pydantic models for configuration validation
- [x] YAML configuration loading system
- [x] Generic configuration loader with validation
- [x] Basic testing framework setup

#### 2. Portfolio Management
- [x] SimplePortfolio implementation
- [x] Portfolio configuration models
- [x] Basic capital allocation
- [x] Risk limits structure
- [x] Portfolio tests
- [x] **Protocol Compliance**: Fixed all Portfolio protocol method signatures
- [x] **Type Safety**: Resolved Decimal/float type mismatches
- [x] **P&L Tracking**: Implemented get_total_pnl() and get_current_capital() methods

#### 3. Data Providers
- [x] CSV data provider
- [x] Yahoo Finance provider (basic)
- [x] Provider container system
- [x] Price feed protocols
- [x] Data provider tests

#### 4. Trading Sessions (Basic)
- [x] SessionConfig and TradingSessionImpl
- [x] Symbol mapping configuration
- [x] Execution limits structure
- [x] Basic session P&L tracking
- [x] Session configuration from YAML
- [x] Session tests
- [x] **Protocol Compliance**: Fixed TradingSession protocol method signatures
- [x] **Parameter Filtering**: Added intelligent parameter filtering for price feed providers
- [x] **Strategy Association**: Implemented strategy-to-session mapping

#### 5. Strategy Framework
- [x] Step-based strategy configuration system
- [x] Strategy step registry
- [x] Dynamic configuration system
- [x] Strategy execution framework
- [x] Strategy tests

#### 6. System Integration ✅
- [x] **End-to-End Execution**: Main workflow runs successfully
- [x] **Portfolio Initialization**: Proper capital management with $100,000 initial capital
- [x] **Price Feed Integration**: Successfully loads 4308 bars of price data for CL symbol
- [x] **Session Orchestration**: Sessions properly coordinate between strategies and providers
- [x] **P&L Tracking**: Portfolio-level P&L aggregation working correctly
- [x] **Configuration Validation**: All YAML configurations properly validated and loaded

## 🚧 Ready for Higher-Level Refactoring

### Current System Status
The trading system now runs successfully end-to-end with proper protocol compliance:
- Portfolio manages capital and risk limits correctly
- Sessions orchestrate strategy execution within portfolio constraints
- Price feeds provide data with proper parameter handling
- Configuration system validates and loads all components

**Next Priority**: Focus on higher-level architecture improvements and strategy execution integration.

## 📋 Planned Work

### Phase 1: Strategy Execution Integration (Priority: HIGH)

#### 1.1 Strategy-Session Integration
**Goal**: Connect the existing strategy framework to trading sessions

**Tasks**:
- [ ] Integrate strategy step registry with session execution
- [ ] Add strategy execution methods to TradingSessionImpl:
  - `execute_strategy(strategy_name, symbol, price_data)`
  - `get_strategy_signals(strategy_name, symbol)`
  - `validate_strategy_config(strategy_name)`
- [ ] Create strategy context for session-strategy communication
- [ ] Add strategy execution tests

**Files to modify**:
- `src/core/sessions/protocols.py` - Add strategy execution methods
- `src/core/sessions/trading_session.py` - Implement strategy execution
- `src/main_wip.py` - Integrate strategy execution in main workflow

#### 1.2 Execution Provider Integration
**Goal**: Enable actual order execution through execution providers

**Tasks**:
- [ ] Create execution provider protocols
- [ ] Implement mock execution provider for testing
- [ ] Add order execution methods to TradingSessionImpl:
  - `place_order(symbol, side, quantity, order_type)`
  - `cancel_order(order_id)`
  - `get_order_status(order_id)`
  - `get_open_orders()`
- [ ] Add execution provider validation
- [ ] Create execution provider tests

**Files to modify**:
- `src/core/sessions/protocols.py` - Add execution methods
- `src/core/sessions/trading_session.py` - Implement execution methods
- `tests/core/sessions/test_trading_session.py` - Add execution tests

#### 1.3 Position Management
**Goal**: Track and manage open positions within session limits

**Tasks**:
- [ ] Add position tracking to TradingSessionImpl
- [ ] Implement position management methods:
  - `get_positions()` - Get all open positions
  - `get_position(symbol)` - Get specific position
  - `get_total_position_value()` - Calculate total position value
  - `update_position(symbol, quantity, price)` - Update position
- [ ] Add position limit enforcement (`max_open_positions`)
- [ ] Add position sizing based on `max_order_size`
- [ ] Create position management tests

**Files to modify**:
- `src/core/sessions/trading_session.py` - Add position tracking
- `tests/core/sessions/test_trading_session.py` - Add position tests

#### 1.4 Trading Hours Enforcement
**Goal**: Respect market hours and session trading constraints

**Tasks**:
- [ ] Improve ExecutionLimits.trading_hours structure (currently Dict[str, str])
- [ ] Add trading hours validation:
  - `is_within_trading_hours()` - Check if current time allows trading
  - `get_next_trading_time()` - Get next available trading time
- [ ] Integrate with market calendar (holidays, weekends)
- [ ] Add trading hours enforcement to order placement
- [ ] Create trading hours tests

**Files to modify**:
- `src/core/sessions/trading_session.py` - Improve trading hours
- `src/core/sessions/trading_session.py` - Add time validation methods

#### 1.5 Execution Limits Enforcement
**Goal**: Enforce session-level execution constraints

**Tasks**:
- [ ] Add execution limit validation:
  - `can_place_order(symbol, quantity, price)` - Check if order is allowed
  - `check_execution_limits(order_details)` - Validate against all limits
- [ ] Integrate with position management for `max_open_positions`
- [ ] Add order size validation for `max_order_size`
- [ ] Create execution limit tests

**Files to modify**:
- `src/core/sessions/trading_session.py` - Add limit enforcement
- `tests/core/sessions/test_trading_session.py` - Add limit tests

### Phase 2: Portfolio Integration (Priority: HIGH)

#### 2.1 Portfolio Risk Integration
**Goal**: Connect sessions to portfolio risk management

**Tasks**:
- [ ] Add portfolio reference to TradingSessionImpl
- [ ] Implement portfolio risk limit checks:
  - Check against portfolio `max_position_size`
  - Check against portfolio `max_drawdown`
  - Check against portfolio `var_limit`
- [ ] Add portfolio P&L rollup from sessions
- [ ] Create portfolio integration tests

**Files to modify**:
- `src/core/sessions/trading_session.py` - Add portfolio integration
- `src/core/portfolio.py` - Add session P&L rollup
- `tests/core/sessions/test_trading_session.py` - Add portfolio tests

#### 2.2 Capital Allocation Enforcement
**Goal**: Ensure sessions respect allocated capital

**Tasks**:
- [ ] Add capital allocation validation
- [ ] Track session capital usage
- [ ] Prevent over-allocation
- [ ] Add capital allocation tests

### Phase 3: Strategy Integration (Priority: MEDIUM)

#### 3.1 Strategy Execution Coordination
**Goal**: Coordinate strategy execution within sessions

**Tasks**:
- [ ] Add strategy runner to TradingSessionImpl
- [ ] Implement strategy execution methods:
  - `run_strategy(strategy_name, symbol)`
  - `get_strategy_signals(strategy_name, symbol)`
- [ ] Add strategy state management
- [ ] Create strategy integration tests

#### 3.2 Strategy-Session Communication
**Goal**: Enable strategies to interact with session data and execution

**Tasks**:
- [ ] Create strategy context object
- [ ] Add methods for strategies to:
  - Get price data
  - Place orders
  - Check positions
  - Access session configuration
- [ ] Create strategy context tests

### Phase 4: Advanced Features (Priority: LOW)

#### 4.1 Real Execution Providers
**Goal**: Implement real execution providers

**Tasks**:
- [ ] Interactive Brokers provider
- [ ] Alpaca provider
- [ ] Binance provider (crypto)
- [ ] Provider-specific order types and constraints

#### 4.2 Advanced Risk Management
**Goal**: Implement sophisticated risk management

**Tasks**:
- [ ] Real-time VaR calculation
- [ ] Dynamic position sizing
- [ ] Correlation-based risk limits
- [ ] Stress testing framework

#### 4.3 Performance Monitoring
**Goal**: Add comprehensive performance tracking

**Tasks**:
- [ ] Session performance metrics
- [ ] Strategy performance tracking
- [ ] Risk-adjusted returns calculation
- [ ] Performance reporting system

## Implementation Guidelines

### Code Quality Standards
- Follow existing code patterns and architecture
- Maintain provider-agnostic design for strategies
- Ensure comprehensive test coverage
- Use type hints throughout
- Follow Pydantic validation patterns

### Testing Strategy
- Unit tests for all new methods
- Integration tests for session-provider interactions
- Mock providers for testing execution flows
- YAML configuration tests for all new features

### Configuration Management
- All new features should be configurable via YAML
- Maintain backward compatibility
- Use Pydantic models for validation
- Follow existing configuration patterns

## Success Criteria

### Phase 1 Success
- [ ] Sessions can execute orders through providers
- [ ] Position management works correctly
- [ ] Trading hours are enforced
- [ ] Session state is properly managed
- [ ] Execution limits are enforced
- [ ] All features have comprehensive tests

### Phase 2 Success
- [ ] Sessions integrate with portfolio risk management
- [ ] Capital allocation is enforced
- [ ] Portfolio P&L rollup works correctly
- [ ] Risk limits are respected across sessions

### Phase 3 Success
- [ ] Strategies can execute within sessions
- [ ] Strategy-session communication works
- [ ] Strategy state is properly managed

## Risk Mitigation

### Technical Risks
- **Provider Integration Complexity**: Start with mock providers, then real ones
- **State Management**: Use clear state machines and validation
- **Performance**: Monitor and optimize as needed
- **Testing Complexity**: Maintain comprehensive test coverage

### Architecture Risks
- **Tight Coupling**: Maintain provider-agnostic design
- **Configuration Complexity**: Keep configuration simple and validated
- **Risk Management**: Ensure portfolio-level risk is always respected

## Timeline Estimate

- **Phase 1**: 2-3 weeks (Core session features)
- **Phase 2**: 1-2 weeks (Portfolio integration)
- **Phase 3**: 2-3 weeks (Strategy integration)
- **Phase 4**: 4-6 weeks (Advanced features)

**Total Estimated Time**: 9-14 weeks for complete implementation

## Next Steps

1. **Immediate**: Start Phase 1.1 (Execution Provider Integration)
2. **Week 1**: Complete execution provider protocols and mock implementation
3. **Week 2**: Add order execution methods to TradingSessionImpl
4. **Week 3**: Implement position management
5. **Week 4**: Add trading hours enforcement
6. **Week 5**: Complete session state management
7. **Week 6**: Finish execution limits enforcement

This plan ensures alignment with the README.md architecture while systematically building the missing trading session capabilities.
