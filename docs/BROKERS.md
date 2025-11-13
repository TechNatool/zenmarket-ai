# Live Broker Integration Guide

ZenMarket AI supports live trading through professional broker integrations. This guide covers setup, configuration, and safety guidelines.

⚠️ **WARNING**: Live trading involves real money. Test thoroughly in paper trading mode first.

## Supported Brokers

### 1. Interactive Brokers (IBKR)
- **Platforms**: TWS, IB Gateway
- **Markets**: Stocks, Options, Futures, Forex
- **Regions**: Global
- **Status**: ✅ Implemented

### 2. MetaTrader 5 (MT5)
- **Platforms**: MT5 Terminal
- **Markets**: Forex, CFDs, Futures
- **Regions**: Global (broker-dependent)
- **Status**: ✅ Implemented (Windows only)

### 3. Simulator (Paper Trading)
- **Markets**: All (via yfinance)
- **Status**: ✅ Built-in, always available

---

## Interactive Brokers (IBKR) Setup

### Prerequisites

1. **IBKR Account**
   - Open account at [interactivebrokers.com](https://www.interactivebrokers.com)
   - Enable API access in account settings

2. **Install TWS or IB Gateway**
   - Download from [IBKR website](https://www.interactivebrokers.com/en/trading/tws.php)
   - Configure API settings:
     - Enable "ActiveX and Socket Clients"
     - Set trusted IP: `127.0.0.1`
     - Note the socket port (default: 7496 for live, 7497 for paper)

3. **Install Python Package**
   ```bash
   pip install ib-insync
   ```

### Configuration

Create `.env` file in project root:

```env
# IBKR Configuration
BROKER_TYPE=ibkr
IBKR_HOST=127.0.0.1
IBKR_PORT=7497              # 7497 = paper, 7496 = live
IBKR_CLIENT_ID=1
IBKR_PAPER_TRADING=true     # IMPORTANT: Set to false for live trading
```

### Running Live Trading

```bash
# Always test with paper trading first!
python -m src.cli live \
  --broker ibkr \
  --symbols "AAPL,MSFT" \
  --confirm-live
```

**Safety Confirmation**: You will be prompted to type `I UNDERSTAND THE RISKS` before execution.

### IBKR-Specific Notes

- **Port Selection**:
  - 7497: Paper trading (safe)
  - 7496: Live trading (real money)
  
- **Client ID**: Must be unique per connection (1-999)

- **Market Data**: Requires active market data subscriptions

- **Order Types**: Supports MARKET, LIMIT (STOP coming soon)

---

## MetaTrader 5 (MT5) Setup

### Prerequisites

1. **MT5 Account**
   - Open account with MT5-compatible broker
   - Obtain login credentials and server name

2. **Install MT5 Terminal** (Windows only)
   - Download from your broker or [MetaQuotes](https://www.metatrader5.com)
   - Login to your account

3. **Install Python Package**
   ```bash
   pip install MetaTrader5
   ```

### Configuration

```env
# MT5 Configuration
BROKER_TYPE=mt5
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo  # or YourBroker-Live
```

### Running Live Trading

```bash
python -m src.cli live \
  --broker mt5 \
  --symbols "EURUSD,GBPUSD" \
  --confirm-live
```

### MT5-Specific Notes

- **Windows Only**: MT5 API is Windows-only
- **Symbol Names**: Use broker-specific symbols (e.g., "EURUSD" not "EUR/USD")
- **Lot Sizes**: MT5 uses lots, conversion handled automatically
- **Stop Loss/Take Profit**: Supported natively

---

## Broker Factory (Dynamic Selection)

Programmatically create brokers:

```python
from src.brokers.broker_factory import BrokerFactory, BrokerType

# Create from environment variables
broker = BrokerFactory.create_from_env(BrokerType.IBKR)

# Or create with explicit parameters
broker = BrokerFactory.create_broker(
    BrokerType.IBKR,
    host="127.0.0.1",
    port=7497,
    paper_trading=True
)

broker.connect()
```

---

## Safety Guidelines

### 1. Testing Progression

Follow this sequence:

1. **Backtest**: Test on historical data
   ```bash
   python -m src.cli backtest --symbols "AAPL" --from 2024-01-01 --to 2024-12-31
   ```

2. **Paper Trading**: Test with simulator
   ```bash
   python -m src.cli simulate --symbols "AAPL" --dry-run
   ```

3. **Live Paper**: Test with broker's paper account
   ```bash
   IBKR_PORT=7497 python -m src.cli live --broker ibkr --symbols "AAPL" --confirm-live
   ```

4. **Live (Small)**: Start with minimal position sizes
   ```bash
   python -m src.cli live --broker ibkr --symbols "AAPL" --risk-per-trade 0.005 --confirm-live
   ```

### 2. Risk Management

**Always configure**:
- `--max-positions 5`: Limit open positions
- `--risk-per-trade 0.01`: Risk 1% per trade maximum
- `--max-daily-drawdown 0.05`: Circuit breaker at 5% daily loss
- `--max-consecutive-losses 3`: Stop after 3 losses

**Example**:
```bash
python -m src.cli live \
  --broker ibkr \
  --symbols "AAPL,MSFT" \
  --risk-per-trade 0.01 \
  --max-positions 3 \
  --max-daily-drawdown 0.03 \
  --confirm-live
```

### 3. Security Best Practices

**DO**:
- ✅ Use environment variables for credentials
- ✅ Test on paper accounts first
- ✅ Start with small position sizes
- ✅ Monitor positions actively
- ✅ Use stop losses on all positions
- ✅ Keep API credentials secure

**DON'T**:
- ❌ Hardcode credentials in code
- ❌ Skip paper trading phase
- ❌ Trade with full capital immediately
- ❌ Disable risk limits
- ❌ Share API credentials
- ❌ Run unattended without circuit breakers

### 4. Monitoring

**Real-time Monitoring**:
```python
from src.execution.execution_engine import ExecutionEngine

# After executing trades
status = engine.get_status()
print(f"Equity: {status['performance']['current_equity']}")
print(f"Daily PnL: {status['risk_summary']['state']['daily_pnl']}")
print(f"Open Positions: {len(status.get('positions', []))}")
```

**Trade Journal**: All trades are automatically logged to:
- `data/journal/trades_YYYYMMDD.csv`
- `data/journal/ledger.json`

---

## API Credentials Security

### Environment Variables (Recommended)

```bash
# .env file (add to .gitignore!)
BROKER_TYPE=ibkr
IBKR_PORT=7497
IBKR_PAPER_TRADING=true

MT5_LOGIN=123456
MT5_PASSWORD=secret123
MT5_SERVER=Broker-Demo
```

### Never Commit Credentials

Update `.gitignore`:
```
.env
*.env
config/credentials.json
```

---

## Broker Comparison

| Feature | IBKR | MT5 | Simulator |
|---------|------|-----|-----------|
| **Markets** | Global stocks, options, futures | Forex, CFDs | All (via yfinance) |
| **Platforms** | TWS, Gateway | MT5 Terminal | Built-in |
| **OS Support** | All | Windows only | All |
| **Paper Trading** | ✅ | ✅ | ✅ |
| **Commissions** | Low | Varies | $2 (simulated) |
| **API Stability** | Excellent | Good | N/A |
| **Setup Complexity** | Medium | Easy | None |

---

## Troubleshooting

### IBKR: Connection Failed

**Symptoms**: `Failed to connect to IBKR`

**Solutions**:
1. Ensure TWS/Gateway is running
2. Check API settings enabled
3. Verify port number (7496 or 7497)
4. Check firewall settings
5. Try incrementing `IBKR_CLIENT_ID`

### MT5: Not Available on Linux/Mac

**Symptoms**: `MetaTrader 5 is only available on Windows`

**Solutions**:
- Use Windows machine/VM
- Use Wine (not recommended)
- Switch to IBKR or simulator

### Orders Not Executing

**Symptoms**: Orders placed but not filled

**Solutions**:
1. Check market hours
2. Verify symbol names
3. Check account balance
4. Review risk manager logs
5. Ensure positions limit not reached

### Trading Halted

**Symptoms**: `Trading halted: Max daily drawdown exceeded`

**Solutions**:
1. Review risk limits
2. Wait for daily counter reset (next trading day)
3. Analyze losing trades
4. Adjust strategy or risk parameters

---

## Example: Full Live Trading Session

```python
from src.brokers.broker_factory import BrokerFactory, BrokerType
from src.execution.execution_engine import ExecutionEngine
from src.execution.risk_manager import RiskLimits
from src.advisor.signal_generator import SignalGenerator
from src.advisor.indicators import calculate_indicators
import yfinance as yf

# 1. Create broker
broker = BrokerFactory.create_broker(
    BrokerType.IBKR,
    host="127.0.0.1",
    port=7497,  # Paper trading
    paper_trading=True
)

if not broker.connect():
    print("Failed to connect")
    exit(1)

# 2. Configure risk limits
risk_limits = RiskLimits(
    max_risk_per_trade_pct=0.01,
    max_open_positions=5,
    max_daily_drawdown_pct=0.05
)

# 3. Create execution engine
engine = ExecutionEngine(
    broker=broker,
    risk_limits=risk_limits,
    journal_enabled=True
)

# 4. Generate signals and trade
signal_generator = SignalGenerator()

ticker = yf.Ticker("AAPL")
df = ticker.history(period="3mo")
indicators = calculate_indicators(df)
signal = signal_generator.generate_signal("AAPL", indicators)

if signal.signal.value != "HOLD":
    orders = engine.execute_signal(signal)
    print(f"Executed {len(orders)} orders")

# 5. Monitor and cleanup
status = engine.get_status()
print(f"Current equity: {status['performance']['current_equity']}")

engine.shutdown()
broker.disconnect()
```

---

## Next Steps

- Review [BACKTESTING.md](BACKTESTING.md) for strategy testing
- Check [SECURITY.md](../SECURITY.md) for security guidelines
- See [examples/](../examples/) for complete workflows

---

**DISCLAIMER**: Live trading involves substantial risk of loss. ZenMarket AI is provided as-is without warranties. Always test thoroughly and trade responsibly.

*For questions or issues, visit: https://github.com/TechNatool/zenmarket-ai/issues*
