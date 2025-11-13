# Broker Module

The Broker module provides adapters for connecting to real brokers and paper trading.

---

## Overview

Supported brokers:
- **Paper Trading** (default) - Simulated execution
- **Interactive Brokers** (IBKR) - Professional trading platform
- **MetaTrader 5** (MT5) - Forex and CFD trading

---

## Broker Interface

All brokers implement the `BrokerInterface` protocol:

```python
class BrokerInterface(Protocol):
    def connect(self) -> bool:
        """Establish connection to broker."""
        
    def disconnect(self) -> None:
        """Close connection."""
        
    def place_order(self, order: Order) -> OrderResult:
        """Submit order for execution."""
        
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order."""
        
    def get_positions(self) -> List[Position]:
        """Get current open positions."""
        
    def get_account_info(self) -> AccountInfo:
        """Get account balance and info."""
```

---

## Paper Trading (Default)

Simulated broker for testing without risk.

### Features
- Zero risk - no real money
- Realistic execution
- Commission simulation
- Slippage modeling
- Instant setup

### Usage

```python
from src.execution.broker_simulator import BrokerSimulator

broker = BrokerSimulator(
    initial_capital=100000,
    commission_pct=0.001,
    slippage_pct=0.0005
)

broker.connect()
result = broker.place_order(order)
```

---

## Interactive Brokers (IBKR)

Professional broker integration.

### Setup

1. **Install IBKR Gateway or TWS**
2. **Enable API access** in settings
3. **Configure connection**:

```bash
# .env
IBKR_HOST=127.0.0.1
IBKR_PORT=7497  # Paper trading: 7497, Live: 7496
IBKR_CLIENT_ID=1
```

### Usage

```python
from src.brokers.ibkr_adapter import IBKRAdapter

broker = IBKRAdapter()
broker.connect()

# Place order
order = MarketOrder(symbol="AAPL", quantity=10, side="BUY")
result = broker.place_order(order)

# Get positions
positions = broker.get_positions()
```

### Features
- Real-time data
- Multiple order types
- Options trading
- Futures support
- Global markets

### Requirements
- IBKR account
- TWS or Gateway running
- `ib-insync` library

---

## MetaTrader 5 (MT5)

Forex and CFD trading platform.

### Setup

1. **Install MT5 terminal**
2. **Enable algo trading** in settings
3. **Configure**:

```bash
# .env
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo
```

### Usage

```python
from src.brokers.mt5_adapter import MT5Adapter

broker = MT5Adapter()
broker.connect()

# Place order
order = MarketOrder(symbol="EURUSD", quantity=1.0, side="BUY")
result = broker.place_order(order)
```

### Features
- Forex majors/minors
- CFDs on stocks, indices, commodities
- Micro/mini/standard lots
- Hedging allowed
- MetaQuotes platform

### Requirements
- MT5 account
- MT5 terminal installed (Windows)
- `MetaTrader5` Python library

---

## Broker Factory

Automatically selects broker based on configuration.

```python
from src.brokers.broker_factory import create_broker

# Reads from .env: BROKER_TYPE=paper|ibkr|mt5
broker = create_broker()
broker.connect()
```

---

## Switching Brokers

### Development → Production

```python
# Development (paper trading)
if ENV == "development":
    broker = BrokerSimulator(initial_capital=100000)
    
# Production (real broker)
elif ENV == "production":
    broker = IBKRAdapter()  # or MT5Adapter()
```

---

## Safety Features

### Paper Trading First
Always test strategies in paper trading before going live.

### Risk Limits
All brokers enforce:
- Position size limits
- Daily loss limits
- Maximum drawdown
- Circuit breakers

### Fail-Safe Defaults
- Paper trading by default
- Confirmation required for live trading
- Emergency stop mechanism

---

## Best Practices

### 1. Test Thoroughly

```python
# Minimum 3 months paper trading
paper_results = backtest_paper(strategy, "3mo")
if paper_results.sharpe > 2.0 and paper_results.win_rate > 0.60:
    # Consider live trading
    pass
```

### 2. Start Small

```python
# Start with minimum position sizes
position_size = min_lot_size * 1.0
```

### 3. Monitor Closely

```python
# Real-time monitoring
while trading:
    check_pnl()
    check_positions()
    check_risk_limits()
```

---

## Troubleshooting

### IBKR Connection Issues

```python
# Check TWS/Gateway is running
# Check port number (7497 for paper)
# Check client ID is not in use
# Check API permissions enabled
```

### MT5 Connection Issues

```python
# Check MT5 terminal is running
# Check algo trading is enabled
# Check login credentials
# Check server name is correct
```

---

## Testing

Test coverage:
- Broker simulator: 78.93%
- IBKR adapter: 20.26% (requires live connection)
- MT5 adapter: 14.36% (Windows-only)
