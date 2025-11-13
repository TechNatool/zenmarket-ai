# Execution Module

The Execution module handles trade execution, order management, position sizing, and risk management.

---

## Overview

The Execution module provides:

- Realistic order execution simulation
- Multiple position sizing strategies
- Comprehensive risk management
- P&L tracking and trade journaling
- Compliance checks and circuit breakers

---

## Components

### 1. Execution Engine (`execution_engine.py`)

Core orchestrator for trade execution.

#### Responsibilities

- Order validation and routing
- Fill simulation with realistic slippage
- Position management
- Event notification
- Trade logging

#### Order Flow

```
Order Submission
    ↓
Pre-Trade Validation
    ↓
Risk Manager Check
    ↓
Position Size Calculation
    ↓
Broker Execution
    ↓
Fill Confirmation
    ↓
P&L Update
    ↓
Trade Journal Entry
```

#### Usage

```python
from src.execution.execution_engine import ExecutionEngine
from src.execution.order_types import MarketOrder

engine = ExecutionEngine(broker=paper_broker)
order = MarketOrder(symbol="AAPL", quantity=10, side="BUY")

fill = engine.execute_order(order)
print(f"Filled {fill.quantity} @ ${fill.price}")
```

---

### 2. Broker Simulator (`broker_simulator.py`)

Paper trading broker with realistic execution.

#### Features

- Realistic fill prices (bid/ask spread)
- Configurable slippage
- Commission calculation
- Order type support (Market, Limit, Stop)
- Position tracking

#### Slippage Model

```python
# Market orders: Price + (spread/2) + slippage
fill_price = current_price * (1 + slippage_pct)

# Limit orders: Only fill if price reached
if side == "BUY" and market_price <= limit_price:
    fill_price = limit_price
```

#### Configuration

```python
broker = BrokerSimulator(
    initial_capital=100000,
    commission_pct=0.001,  # 0.1%
    slippage_pct=0.0005    # 0.05%
)
```

---

### 3. Position Sizing (`position_sizing.py`)

Multiple position sizing strategies.

#### Strategies

##### Fixed Size
```python
# Always trade fixed quantity
size = 100  # shares
```

##### Percent of Equity
```python
# Risk X% of account per trade
size = (account_value * risk_pct) / price
```

##### Kelly Criterion
```python
# Optimal bet sizing
kelly_fraction = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
size = account_value * kelly_fraction / price
```

##### R-Multiple (ATR-based)
```python
# Size based on risk per share (ATR)
risk_per_share = ATR * atr_multiplier
size = (account_value * risk_pct) / risk_per_share
```

#### Usage

```python
from src.execution.position_sizing import PositionSizer, SizingMethod

sizer = PositionSizer(
    method=SizingMethod.PERCENT_EQUITY,
    risk_per_trade=0.02  # 2% per trade
)

size = sizer.calculate_size(
    account_value=100000,
    price=150,
    stop_loss=145
)
```

---

### 4. Risk Manager (`risk_manager.py`)

Comprehensive risk controls.

#### Risk Checks

##### Pre-Trade Checks
- Account balance sufficient
- Position size within limits
- Daily loss limit not exceeded
- Maximum positions not exceeded
- Concentration limits

##### Post-Trade Monitoring
- Stop-loss automation
- Take-profit automation
- Trailing stop management
- Drawdown monitoring

#### Circuit Breakers

```python
# Triggered when:
- Daily loss > max_daily_loss (default 5%)
- Drawdown > max_drawdown (default 10%)
- Volatility spike > threshold
- Rapid consecutive losses

# Action: Halt all new trades
```

#### Configuration

```python
risk_manager = RiskManager(
    max_position_size=0.10,      # 10% of account
    max_daily_loss_pct=0.05,     # 5% daily loss limit
    max_drawdown_pct=0.10,       # 10% max drawdown
    max_open_positions=5,        # Max 5 concurrent positions
    max_single_symbol_pct=0.20   # 20% per symbol
)
```

---

### 5. Order Types (`order_types.py`)

Supported order types with validation.

#### Order Types

##### Market Order
- Executes immediately at current market price
- Guaranteed fill
- Variable price

```python
order = MarketOrder(symbol="AAPL", quantity=10, side="BUY")
```

##### Limit Order
- Executes at specified price or better
- May not fill
- Price control

```python
order = LimitOrder(
    symbol="AAPL",
    quantity=10,
    side="BUY",
    limit_price=150.00
)
```

##### Stop-Loss Order
- Triggers market order when price reached
- Risk management
- Slippage possible

```python
order = StopLossOrder(
    symbol="AAPL",
    quantity=10,
    side="SELL",
    stop_price=145.00
)
```

##### Take-Profit Order
- Automatically closes position at profit target
- Locks in gains

```python
order = TakeProfitOrder(
    symbol="AAPL",
    quantity=10,
    side="SELL",
    target_price=160.00
)
```

##### Trailing Stop Order
- Follows price by fixed percentage
- Protects profits while allowing upside

```python
order = TrailingStopOrder(
    symbol="AAPL",
    quantity=10,
    side="SELL",
    trail_percent=0.05  # 5%
)
```

---

### 6. P&L Tracker (`pnl_tracker.py`)

Real-time profit/loss monitoring.

#### Metrics Tracked

- **Realized P&L**: Closed position profits/losses
- **Unrealized P&L**: Open position mark-to-market
- **Total P&L**: Realized + Unrealized
- **Return %**: Total P&L / Initial Capital
- **Daily P&L**: Current day profits/losses
- **Peak Equity**: Highest account value
- **Drawdown**: Current decline from peak

#### Usage

```python
from src.execution.pnl_tracker import PnLTracker

tracker = PnLTracker(initial_capital=100000)

# Record trade
tracker.record_trade(
    symbol="AAPL",
    quantity=10,
    entry_price=150,
    exit_price=155,
    commission=2.00
)

# Get P&L
print(f"Total P&L: ${tracker.total_pnl}")
print(f"Return: {tracker.return_pct}%")
print(f"Drawdown: {tracker.drawdown_pct}%")
```

---

### 7. Trade Journal (`journal.py`)

Comprehensive trade logging and analysis.

#### Logged Information

- Entry/exit timestamps
- Symbol and quantity
- Entry/exit prices
- Commission and slippage
- P&L (realized)
- Trade reason/strategy
- Market conditions
- Performance metrics

#### Export Formats

- CSV for spreadsheet analysis
- JSON for programmatic access
- SQLite for queryable database

#### Usage

```python
from src.execution.journal import TradeJournal

journal = TradeJournal()

journal.log_trade(
    symbol="AAPL",
    side="BUY",
    quantity=10,
    price=150,
    reason="RSI oversold + bullish MA cross",
    strategy="mean_reversion"
)

# Export trades
journal.to_csv("trades.csv")
```

---

### 8. Compliance (`compliance.py`)

Trading rule enforcement.

#### Rules Enforced

- Pattern day trader rules
- Short sale restrictions
- Wash sale detection
- Position limit enforcement
- Margin requirement checks

---

## Architecture

```
┌──────────────────────────────────────┐
│      Execution Engine                │
├──────────────────────────────────────┤
│                                      │
│  Strategy Signal                     │
│         ↓                            │
│  ┌─────────────────┐                │
│  │  Risk Manager   │                │
│  └────────┬────────┘                │
│           ↓                          │
│  ┌─────────────────┐                │
│  │ Position Sizer  │                │
│  └────────┬────────┘                │
│           ↓                          │
│  ┌─────────────────┐                │
│  │  Order Manager  │                │
│  └────────┬────────┘                │
│           ↓                          │
│  ┌─────────────────┐                │
│  │     Broker      │                │
│  └────────┬────────┘                │
│           ↓                          │
│  ┌─────────────────┐                │
│  │   P&L Tracker   │                │
│  └────────┬────────┘                │
│           ↓                          │
│  ┌─────────────────┐                │
│  │ Trade Journal   │                │
│  └─────────────────┘                │
│                                      │
└──────────────────────────────────────┘
```

---

## Best Practices

### 1. Always Use Stop-Losses

```python
# Never enter without a stop
entry_order = MarketOrder("AAPL", 10, "BUY")
stop_order = StopLossOrder("AAPL", 10, "SELL", stop_price=145)

engine.execute_order(entry_order)
engine.place_order(stop_order)
```

### 2. Size Positions Appropriately

```python
# Never risk more than 2% per trade
sizer = PositionSizer(
    method=SizingMethod.PERCENT_EQUITY,
    risk_per_trade=0.02
)
```

### 3. Monitor Drawdowns

```python
# Stop trading if drawdown exceeds limit
if tracker.drawdown_pct > 10:
    print("Max drawdown exceeded - halting trades")
    engine.halt_trading()
```

---

## Testing

Comprehensive test coverage:

- `tests/execution/test_execution_engine.py` - 21 tests
- `tests/execution/test_broker_simulator.py` - 24 tests
- `tests/execution/test_position_sizing.py` - 16 tests
- `tests/execution/test_risk_manager.py` - 18 tests

Total: 85 execution tests
Coverage: 78-86% across modules
