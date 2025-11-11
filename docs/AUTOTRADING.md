# 🤖 ZenMarket AI - Auto-Trading System

**⚠️ IMPORTANT: Paper Trading by Default - Live Trading Requires Explicit Confirmation**

Complete automated trading system with AI-powered signals, advanced risk management, and comprehensive safety mechanisms.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Security & Safety](#security--safety)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [Risk Management](#risk-management)
- [Position Sizing](#position-sizing)
- [Compliance](#compliance)
- [Trade Journaling](#trade-journaling)
- [Configuration](#configuration)
- [Backtesting](#backtesting)
- [Live Trading](#live-trading)
- [FAQ](#faq)

---

## 🎯 Overview

ZenMarket AI Auto-Trading integrates:

- **AI Trading Advisor**: Technical analysis with BUY/SELL/HOLD signals
- **Execution Engine**: Complete pipeline from signal to order execution
- **Risk Management**: Circuit breakers, position limits, drawdown protection
- **Position Sizing**: Multiple methods (Fixed Fractional, Kelly, Fixed Dollar)
- **Compliance**: Market hours, Pattern Day Trader rule checking
- **Trade Journaling**: Mandatory CSV + JSON logging

### Key Features

✅ **Paper Trading Default** - Simulate with realistic execution
✅ **Circuit Breakers** - Automatic trading halt on risk violations
✅ **Multi-Layer Validation** - Risk → Compliance → Execution
✅ **Comprehensive Logging** - Every trade tracked and auditable
✅ **Dry-Run Mode** - Test strategies without placing orders
✅ **Real-Time Monitoring** - Track performance and risk metrics

---

## 🏗️ Architecture

### Complete Trading Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ZENMARKET AI PIPELINE                     │
└─────────────────────────────────────────────────────────────┘

1. SIGNAL GENERATION (Advisor Module)
   ├── Fetch market data (yfinance)
   ├── Calculate indicators (MA20/50, RSI, BB, ATR)
   └── Generate signal (BUY/SELL/HOLD + confidence)
                      ↓
2. POSITION SIZING
   ├── Fixed Fractional (risk-based)
   ├── Kelly Criterion (win rate-based)
   └── Fixed Dollar (static allocation)
                      ↓
3. RISK VALIDATION
   ├── Per-trade risk limit (default: 1%)
   ├── Daily risk limit (default: 3%)
   ├── Max drawdown check (default: 5%)
   ├── Position size limit (default: 20%)
   ├── Max positions (default: 5)
   └── Consecutive losses (default: 3)
                      ↓
4. COMPLIANCE CHECK
   ├── Market hours validation
   ├── Pattern Day Trader rule
   └── Pre-trade checklist
                      ↓
5. ORDER EXECUTION
   ├── Calculate stop loss (ATR-based or 2%)
   ├── Calculate take profit (2:1 R/R default)
   ├── Place order via broker
   └── Monitor fill
                      ↓
6. LOGGING & TRACKING
   ├── Trade journal (CSV + JSON)
   ├── PnL tracker (equity curve, drawdown)
   └── Performance metrics (win rate, profit factor)
```

### Module Structure

```
src/
├── execution/
│   ├── execution_engine.py      # Main orchestrator
│   ├── broker_base.py            # Abstract broker interface
│   ├── broker_simulator.py       # Paper trading simulator
│   ├── position_sizing.py        # Sizing algorithms
│   ├── risk_manager.py           # Risk validation + circuit breakers
│   ├── compliance.py             # Regulatory checks
│   ├── journal.py                # Trade logging
│   ├── pnl_tracker.py            # Performance tracking
│   └── order_types.py            # Data structures
├── advisor/
│   ├── signal_generator.py       # Trading signals
│   └── indicators.py             # Technical indicators
└── cli.py                        # Command-line interface
```

---

## 🔒 Security & Safety

### 1. Paper Trading Default

**ALL trading starts in simulation mode by default.**

```bash
# Safe - Paper trading (default)
python -m src.cli simulate --symbols "^GDAXI,BTC-USD"

# DANGEROUS - Live trading (requires double confirmation)
python -m src.cli live --symbols "^GDAXI" --confirm-live
```

### 2. Circuit Breakers

Automatic trading halt when:

| Trigger | Default Limit | Action |
|---------|--------------|--------|
| **Daily Drawdown** | 5% | HALT - Manual resume required |
| **Consecutive Losses** | 3 trades | HALT - Manual resume required |
| **Daily Risk Used** | 3% | Block new orders until next day |
| **Daily Loss Dollar** | Optional | HALT if set |

### 3. Multi-Layer Validation

Every order passes through:

```
Order Request
     ↓
[1. Trading Halted?] → REJECT if yes
     ↓
[2. Position Size OK?] → REJECT if > 20% equity
     ↓
[3. Risk Per Trade OK?] → REJECT if > 1% equity
     ↓
[4. Daily Risk OK?] → REJECT if daily limit reached
     ↓
[5. Max Positions?] → REJECT if at limit (allow close)
     ↓
[6. Market Open?] → REJECT if closed
     ↓
[7. Compliance OK?] → REJECT if PDT violation
     ↓
EXECUTE ORDER
```

### 4. Mandatory Journaling

**No order is placed without logging.**

All trades recorded in:
- `data/journal/orders_YYYY-MM-DD.csv`
- `data/journal/journal_YYYY-MM-DD.json`
- `data/journal/ledger_YYYY-MM-DD.json` (simulator)

### 5. Dry-Run Mode

Test strategies without placing orders:

```bash
python -m src.cli simulate --symbols "AAPL,MSFT" --dry-run
```

Validates entire pipeline but **doesn't execute orders**.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. First Simulation

```bash
# Paper trade with default settings
python -m src.cli simulate \
    --symbols "^GDAXI,BTC-USD" \
    --risk-per-trade 0.01 \
    --initial-capital 100000
```

### 3. Dry Run (Validation Only)

```bash
# Test without placing orders
python -m src.cli simulate \
    --symbols "AAPL,MSFT,GOOGL" \
    --dry-run
```

### 4. Check Results

```bash
# View trade journal
cat data/journal/orders_$(date +%Y-%m-%d).csv

# View ledger (paper trading)
cat data/journal/ledger_$(date +%Y-%m-%d).json
```

---

## 💻 CLI Commands

### Simulate (Paper Trading)

```bash
python -m src.cli simulate [OPTIONS]

Options:
  --symbols TEXT              Comma-separated tickers (required)
  --order-type TEXT          market|limit|stop|stop_limit (default: market)
  --risk-per-trade FLOAT     Risk per trade (default: 0.01 = 1%)
  --risk-per-day FLOAT       Max daily risk (default: 0.03 = 3%)
  --max-daily-drawdown FLOAT Max drawdown (default: 0.05 = 5%)
  --max-consecutive-losses INT  Max losses (default: 3)
  --max-positions INT        Max positions (default: 5)
  --sizing-method TEXT       fixed_fractional|kelly|fixed_dollar
  --initial-capital FLOAT    Starting cash (default: 100000)
  --slippage-bps FLOAT       Slippage (default: 1.5 bps)
  --commission FLOAT         Commission (default: 2.0 USD)
  --dry-run                  Validate only, don't execute
  --journal-pdf              Generate PDF report

Examples:
  # Conservative trading
  python -m src.cli simulate --symbols "^GDAXI" --risk-per-trade 0.005

  # Crypto trading with higher slippage
  python -m src.cli simulate --symbols "BTC-USD,ETH-USD" --slippage-bps 5.0

  # Test mode
  python -m src.cli simulate --symbols "AAPL,MSFT" --dry-run
```

### Backtest (Historical)

```bash
python -m src.cli backtest [OPTIONS]

Options:
  --symbols TEXT        Comma-separated tickers (required)
  --from TEXT          Start date YYYY-MM-DD (required)
  --to TEXT            End date YYYY-MM-DD (required)
  --interval TEXT      1d|1h|15m|5m (default: 1d)
  --initial-capital FLOAT  Starting cash (default: 100000)

Examples:
  # Backtest 2024
  python -m src.cli backtest \
      --symbols "^GDAXI" \
      --from 2024-01-01 \
      --to 2024-12-31

  # Intraday backtest
  python -m src.cli backtest \
      --symbols "SPY" \
      --from 2024-11-01 \
      --to 2024-11-10 \
      --interval 15m
```

### Live (Real Trading) ⚠️

```bash
python -m src.cli live [OPTIONS]

Options:
  --symbols TEXT        Comma-separated tickers (required)
  --broker TEXT         ibkr|mt5 (required)
  --confirm-live        REQUIRED safety flag
  (... same options as simulate ...)

⚠️ WARNING: REAL MONEY AT RISK ⚠️

Example:
  python -m src.cli live \
      --symbols "^GDAXI" \
      --broker ibkr \
      --confirm-live \
      --risk-per-trade 0.005
```

**Live trading requires:**
1. `--confirm-live` flag
2. Interactive confirmation: Type "I UNDERSTAND THE RISKS"
3. Broker API credentials in `.env`

**Note:** Live broker integration not yet implemented. Use `simulate` for paper trading.

---

## 🛡️ Risk Management

### Risk Limits Configuration

```python
from src.execution.risk_manager import RiskLimits

limits = RiskLimits(
    max_risk_per_trade_pct=0.01,      # 1% max risk per trade
    max_position_size_pct=0.20,       # 20% max position size
    max_risk_per_day_pct=0.03,        # 3% max daily risk
    max_daily_drawdown_pct=0.05,      # 5% max daily drawdown
    max_open_positions=5,             # 5 max simultaneous positions
    max_consecutive_losses=3,         # Halt after 3 losses
    max_atr_multiplier=3.0            # Halt if volatility > 3x normal
)
```

### Risk Validation Example

```python
# Validate order before placement
is_valid, error_msg = risk_manager.validate_order(
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=Decimal('100'),
    entry_price=Decimal('150'),
    stop_loss=Decimal('145')
)

if not is_valid:
    print(f"Order rejected: {error_msg}")
```

### Circuit Breaker Recovery

```python
# Check if trading is halted
if risk_manager.state.trading_halted:
    print(f"Trading halted: {risk_manager.state.halt_reason}")
    print(f"Halted at: {risk_manager.state.halt_timestamp}")

# Manually resume (use with caution)
risk_manager.force_resume()
```

---

## 📏 Position Sizing

### 1. Fixed Fractional (Default)

Risk-based sizing: **Risk 1% of equity per trade**

```python
# Formula:
# Dollar Risk = Equity × Risk%
# Risk Per Share = |Entry Price - Stop Loss|
# Position Size = Dollar Risk / Risk Per Share

# Example:
# Equity: $100,000
# Risk: 1% = $1,000
# Entry: $100, Stop: $95 → Risk per share = $5
# Position: $1,000 / $5 = 200 shares
```

### 2. Kelly Criterion

Optimal sizing based on win rate and avg win/loss:

```python
# Formula:
# Kelly% = (Win Rate × Avg Win - (1 - Win Rate) × Avg Loss) / Avg Win
# Half Kelly% = Kelly% / 2 (safer)

# Example:
# Win Rate: 60%, Avg Win: $500, Avg Loss: $300
# Kelly% = (0.6 × 500 - 0.4 × 300) / 500 = 0.36 = 36%
# Half Kelly = 18% of equity
```

### 3. Fixed Dollar

Fixed dollar amount per trade:

```python
# Example:
# Always risk $10,000 per trade
# Entry: $100 → 100 shares
```

### Volatility Adjustment

Reduce size in high volatility:

```python
# If ATR > Average ATR:
# Adjusted Size = Base Size × (Average ATR / Current ATR)

# Example:
# Base: 200 shares
# Normal ATR: $2, Current ATR: $4 (2x higher)
# Adjusted: 200 × (2/4) = 100 shares
```

---

## ⚖️ Compliance

### Market Hours Checking

```python
from src.execution.compliance import ComplianceChecker

compliance = ComplianceChecker()

is_open, status, message = compliance.check_market_hours("AAPL")

if not is_open:
    print(f"Market closed: {message}")
```

**Market Hours:**
- US Markets: 9:30 AM - 4:00 PM EST
- Extended Hours: 4:00 AM - 9:30 AM, 4:00 PM - 8:00 PM EST

### Pattern Day Trader (PDT) Rule

**Rule:** Cannot execute 4+ day trades within 5 business days unless account equity ≥ $25,000.

```python
is_compliant, message = compliance.check_pattern_day_trader(
    day_trades_count=3,
    account_equity=Decimal('20000')
)

if not is_compliant:
    print(f"PDT violation risk: {message}")
```

### Pre-Trade Checklist

```python
checklist = compliance.get_pre_trade_checklist("AAPL")

for item, passed in checklist.items():
    print(f"{item}: {'✓' if passed else '✗'}")
```

---

## 📓 Trade Journaling

### Automatic Logging

Every order is logged to:

**CSV Format** (`data/journal/orders_YYYY-MM-DD.csv`):
```csv
timestamp,order_id,symbol,side,quantity,order_type,status,filled_price,stop_loss,take_profit
2025-11-11T10:30:00,ORD_001,AAPL,BUY,100,MARKET,FILLED,150.25,145.00,160.00
```

**JSON Format** (`data/journal/journal_YYYY-MM-DD.json`):
```json
{
  "date": "2025-11-11",
  "orders": [
    {
      "order_id": "ORD_001",
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": "100",
      "status": "FILLED",
      "filled_price": "150.25",
      "stop_loss": "145.00",
      "take_profit": "160.00",
      "metadata": {
        "strategy": "advisor_signal",
        "signal_confidence": 0.75
      }
    }
  ]
}
```

### Manual Journal Access

```python
from src.execution.journal import TradeJournal

journal = TradeJournal()

# Log custom order
journal.log_order(order)

# Save to disk
journal.save_json()
journal.save_csv()

# Get all orders
all_orders = journal.get_all_orders()
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# === Trading Configuration ===
TRADING_MODE=simulate                    # simulate|backtest|live
RISK_PER_TRADE=0.0075                   # 0.75% risk per trade
RISK_PER_DAY=0.02                       # 2% max daily risk
MAX_DRAWDOWN_DAILY=0.03                 # 3% circuit breaker
MAX_CONSECUTIVE_LOSSES=3                # Halt after 3 losses
MAX_OPEN_POSITIONS=5                    # Max 5 positions

# Position Sizing
POSITION_SIZING_METHOD=fixed_fractional # fixed_fractional|kelly|fixed_dollar
DEFAULT_ORDER_TYPE=market               # market|limit|stop|stop_limit

# Paper Trading Simulation
SIM_INITIAL_CAPITAL=100000.0            # $100k starting
SIM_SLIPPAGE_BPS=1.5                    # 1.5 bps slippage
SIM_COMMISSION_PER_TRADE=2.0            # $2 per trade

# Trading Advisor
ADVISOR_ENABLED=true
ADVISOR_MA_SHORT=20
ADVISOR_MA_LONG=50
ADVISOR_RSI_PERIOD=14
ADVISOR_RSI_OVERBOUGHT=70
ADVISOR_RSI_OVERSOLD=30
ADVISOR_MIN_CONFIDENCE=0.5              # Min confidence to trade

# Journaling
JOURNAL_ENABLED=true
JOURNAL_EXPORT_CSV=true
JOURNAL_EXPORT_JSON=true
JOURNAL_EXPORT_PDF=false
```

---

## 📊 Backtesting

### Run Historical Backtest

```bash
python -m src.cli backtest \
    --symbols "^GDAXI,^IXIC" \
    --from 2024-01-01 \
    --to 2024-12-31 \
    --risk-per-trade 0.01 \
    --sizing-method fixed_fractional
```

### Performance Metrics

Backtest generates:

- **Total Return** (%)
- **Sharpe Ratio** (risk-adjusted return)
- **Sortino Ratio** (downside risk-adjusted)
- **Max Drawdown** (%)
- **Win Rate** (%)
- **Profit Factor** (gross profit / gross loss)
- **Average Win** ($)
- **Average Loss** ($)
- **Total Trades** (#)

**Note:** Full backtest module coming soon. Use `simulate` for forward testing.

---

## 🔴 Live Trading

### Prerequisites

1. **Broker Account** (Interactive Brokers or MetaTrader 5)
2. **API Credentials** (in `.env`)
3. **Minimum Capital** ($25k recommended to avoid PDT restrictions)
4. **Risk Understanding** (you can lose money)

### Enable Live Trading

**Step 1:** Configure broker in `.env`

```bash
TRADING_MODE=live
BROKER=ibkr
BROKER_ACCOUNT=your_account_id
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret
```

**Step 2:** Run with confirmation

```bash
python -m src.cli live \
    --symbols "^GDAXI" \
    --broker ibkr \
    --confirm-live \
    --risk-per-trade 0.005  # 0.5% conservative
```

**Step 3:** Type confirmation

```
⚠️  LIVE TRADING MODE - REAL MONEY AT RISK
You are about to trade with REAL MONEY
All orders will be sent to your broker account

Type 'I UNDERSTAND THE RISKS' to proceed:
```

### Live Trading Safety

- Start with **minimal position sizes**
- Use **tight risk limits** (0.5% per trade)
- **Monitor closely** for first week
- Keep **emergency stop** accessible (`Ctrl+C`)
- **Review journals** daily

**⚠️ CURRENT STATUS:** Live broker integration not yet implemented. Paper trading fully functional.

---

## ❓ FAQ

### General

**Q: Is this safe to use?**
A: In **simulate mode**, yes - it's 100% paper trading. In **live mode**, NO - you're trading with real money and can lose capital.

**Q: Do I need API keys?**
A: For paper trading (simulate/backtest), you only need **yfinance** (free, no API key). For live trading, you need broker API credentials.

**Q: What brokers are supported?**
A: Currently, only **simulator** (paper trading) is fully implemented. Interactive Brokers (IBKR) and MetaTrader 5 (MT5) will be added.

### Trading

**Q: How do I start paper trading?**
A: `python -m src.cli simulate --symbols "AAPL,MSFT"`

**Q: Can I customize risk limits?**
A: Yes, via CLI flags (e.g., `--risk-per-trade 0.02`) or `.env` file.

**Q: What happens if I hit circuit breaker?**
A: Trading is **immediately halted**. You must manually resume with `force_resume()` after reviewing logs.

**Q: How are stop losses calculated?**
A: Default: 2x ATR (if available) or 2% fixed. Customizable in code.

**Q: What's the default risk/reward ratio?**
A: 2:1 (risk $1 to make $2). Adjustable in `execution_engine.py`.

### Technical

**Q: Where are logs stored?**
A: `data/journal/` directory with daily files.

**Q: Can I run multiple instances?**
A: Not recommended - race conditions on journal files.

**Q: How do I test without orders?**
A: Use `--dry-run` flag.

**Q: What's the difference between simulate and backtest?**
A: **Simulate** = forward testing with current data. **Backtest** = historical testing with past data.

### Errors

**Q: "Trading halted: max consecutive losses"**
A: Circuit breaker triggered. Review your strategy and manually resume if desired.

**Q: "Insufficient funds" in simulator**
A: Increase `--initial-capital` or reduce position sizes.

**Q: "Market closed" error**
A: US markets are closed. Wait for market hours or disable compliance check (not recommended).

---

## 📞 Support

- **Documentation**: [docs/](../docs/)
- **GitHub Issues**: [Report bugs](https://github.com/TechNatool/zenmarket-ai/issues)
- **Trading Advisor Docs**: [TRADING_ADVISOR.md](TRADING_ADVISOR.md)

---

## ⚠️ Disclaimer

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY.**

Trading financial instruments involves substantial risk of loss. Past performance does not guarantee future results. The authors and contributors are **NOT responsible for any financial losses** incurred through the use of this software.

**NEVER TRADE WITH MONEY YOU CANNOT AFFORD TO LOSE.**

Always start with paper trading and thoroughly test any strategy before risking real capital.

---

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Last Updated:** 2025-11-11
**Version:** 1.0.0 (Étape 3 - Auto-Trading)
