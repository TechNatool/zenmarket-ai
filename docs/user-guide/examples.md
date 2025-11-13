# Examples & Tutorials

Practical examples to get you started with ZenMarket AI.

---

## Example 1: Daily Financial Brief

Generate a comprehensive market brief for your portfolio.

```bash
python -m src.cli brief --symbols AAPL,MSFT,GOOGL,AMZN,TSLA
```

**What it does:**
- Fetches latest news for each symbol
- Analyzes sentiment
- Generates AI-powered insights
- Provides trading recommendations

**Expected output:**
```markdown
# Daily Financial Brief - 2024-01-15

## Market Overview
Mixed sentiment across tech sector...

## Apple Inc. (AAPL)
Sentiment: Positive (75% confidence)
Latest news: Strong Q4 earnings...

## Recommendations
1. Consider scaling into AAPL on pullbacks
2. Monitor TSLA for volatility
...
```

---

## Example 2: Technical Analysis

Get trading signals with technical analysis.

```bash
python -m src.cli advisor --symbol AAPL --period 6mo
```

**What it does:**
- Calculates technical indicators
- Generates BUY/SELL/HOLD signal
- Creates visual chart
- Provides confidence score

**Expected output:**
```
Signal: BUY
Confidence: 78%
Reason: RSI oversold (28), Price below BB lower, MA20 > MA50

Technical Indicators:
- RSI(14): 28.5 (Oversold)
- Price: $150.25
- MA20: $155.30
- MA50: $148.75
- BB Lower: $147.50

Chart saved to: reports/AAPL_analysis.png
```

---

## Example 3: Paper Trading Simulation

Test a strategy without risking real money.

```bash
python -m src.cli simulate \
  --symbol AAPL \
  --strategy conservative \
  --capital 100000 \
  --period 6mo
```

**What it does:**
- Simulates trades based on signals
- Applies realistic slippage and commissions
- Tracks P&L
- Reports performance metrics

**Expected output:**
```
Simulation Results:
==================
Initial Capital: $100,000
Final Capital: $108,500
Total Return: 8.5%
Number of Trades: 23
Win Rate: 65.2%
Sharpe Ratio: 1.85
Max Drawdown: -4.2%
```

---

## Example 4: Strategy Backtesting

Test how a strategy would have performed historically.

```bash
python -m src.cli backtest \
  --symbol AAPL \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --strategy mean_reversion \
  --capital 100000 \
  --report
```

**What it does:**
- Runs strategy on historical data
- Calculates comprehensive metrics
- Generates visual reports
- Compares to buy-and-hold

**Expected output:**
```
Backtest Results - AAPL (2023-01-01 to 2023-12-31)
=================================================

Performance:
- Total Return: 15.8%
- CAGR: 15.8%
- Sharpe Ratio: 2.15
- Sortino Ratio: 3.02
- Calmar Ratio: 3.78

Risk:
- Max Drawdown: -4.2%
- Volatility: 14.5%
- VaR (95%): -2.1%

Trading:
- Total Trades: 47
- Win Rate: 63.8%
- Profit Factor: 2.15
- Avg Win: $850
- Avg Loss: $395

Report saved to: backtests/AAPL_2023_report.pdf
```

---

## Example 5: Multi-Symbol Analysis

Analyze multiple stocks simultaneously.

```python
# analyze_portfolio.py
from src.advisor.signal_generator import SignalGenerator

symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
generator = SignalGenerator()

for symbol in symbols:
    signal = generator.generate_signal(symbol, period="6mo")
    print(f"{symbol}: {signal.signal} ({signal.confidence}%)")
    
# Get market bias
signals = [generator.generate_signal(s) for s in symbols]
bias = generator.get_market_bias(signals)
print(f"\nMarket Bias: {bias}")
```

**Output:**
```
AAPL: BUY (78%)
MSFT: HOLD (55%)
GOOGL: BUY (82%)
AMZN: SELL (65%)
TSLA: HOLD (48%)

Market Bias: BULLISH
```

---

## Example 6: Custom Strategy

Implement and test your own strategy.

```python
# my_strategy.py
from src.advisor.signal_generator import SignalGenerator
from src.advisor.indicators import TechnicalIndicators

class MyStrategy:
    def __init__(self):
        self.signal_gen = SignalGenerator()
        self.indicators = TechnicalIndicators()
        
    def should_buy(self, symbol):
        # Get technical data
        data = self.indicators.get_market_data(symbol)
        indicators = self.indicators.calculate_all(data)
        
        # Custom logic
        rsi = indicators['rsi'].iloc[-1]
        ma20 = indicators['ma20'].iloc[-1]
        price = data['Close'].iloc[-1]
        
        # Buy when RSI < 25 and price > MA20
        return rsi < 25 and price > ma20
        
    def should_sell(self, symbol):
        # Similar logic for selling
        pass

# Use strategy
strategy = MyStrategy()
if strategy.should_buy("AAPL"):
    print("BUY signal generated!")
```

---

## Example 7: Automated Daily Workflow

Create a script that runs every day.

```bash
#!/bin/bash
# daily_workflow.sh

DATE=$(date +%Y-%m-%d)
LOG_FILE="logs/daily_${DATE}.log"

echo "=== Daily Workflow - $DATE ===" | tee -a $LOG_FILE

# 1. Generate morning brief
echo "Generating brief..." | tee -a $LOG_FILE
python -m src.cli brief \
  --symbols AAPL,MSFT,GOOGL \
  --output reports/brief_${DATE}.md \
  >> $LOG_FILE 2>&1

# 2. Check technical signals
echo "Checking signals..." | tee -a $LOG_FILE
for symbol in AAPL MSFT GOOGL; do
  python -m src.cli advisor \
    --symbol $symbol \
    --output reports/signals_${DATE} \
    >> $LOG_FILE 2>&1
done

# 3. Update simulations
echo "Running simulations..." | tee -a $LOG_FILE
python -m src.cli simulate \
  --symbol AAPL \
  --period 1mo \
  >> $LOG_FILE 2>&1

echo "Workflow complete!" | tee -a $LOG_FILE
```

Schedule with cron:
```bash
# Run every day at 9:00 AM
0 9 * * * cd /path/to/zenmarket-ai && ./daily_workflow.sh
```

---

## Example 8: Real-Time Monitoring

Monitor positions in real-time.

```python
# monitor.py
import time
from src.execution.pnl_tracker import PnLTracker
from src.execution.broker_simulator import BrokerSimulator

broker = BrokerSimulator(initial_capital=100000)
tracker = PnLTracker(initial_capital=100000)

print("Starting real-time monitoring...")

while True:
    # Get current positions
    positions = broker.get_positions()
    
    # Update P&L
    for pos in positions:
        current_price = broker.get_current_price(pos.symbol)
        unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
        
        print(f"{pos.symbol}: ${unrealized_pnl:+.2f}")
    
    # Check risk limits
    if tracker.drawdown_pct > 10:
        print("⚠️  Max drawdown exceeded!")
        break
        
    # Update every 5 seconds
    time.sleep(5)
```

---

## Example 9: Walk-Forward Optimization

Optimize and validate strategy parameters.

```python
# walk_forward.py
from src.backtest.backtest_engine import BacktestEngine

# Define parameter ranges
rsi_values = [20, 25, 30, 35]
ma_periods = [10, 20, 30, 50]

# Walk-forward periods
train_periods = [
    ("2022-01-01", "2022-06-30"),
    ("2022-07-01", "2022-12-31"),
    ("2023-01-01", "2023-06-30"),
]

test_periods = [
    ("2022-07-01", "2022-12-31"),
    ("2023-01-01", "2023-06-30"),
    ("2023-07-01", "2023-12-31"),
]

best_params = {}

for i, (train_start, train_end) in enumerate(train_periods):
    best_sharpe = 0
    
    # Optimize on training data
    for rsi in rsi_values:
        for ma in ma_periods:
            strategy = MyStrategy(rsi_threshold=rsi, ma_period=ma)
            results = backtest(strategy, train_start, train_end)
            
            if results.sharpe_ratio > best_sharpe:
                best_sharpe = results.sharpe_ratio
                best_params[i] = {'rsi': rsi, 'ma': ma}
    
    # Test on out-of-sample data
    test_start, test_end = test_periods[i]
    strategy = MyStrategy(**best_params[i])
    results = backtest(strategy, test_start, test_end)
    
    print(f"Period {i+1} Test Results:")
    print(f"  Params: {best_params[i]}")
    print(f"  Sharpe: {results.sharpe_ratio:.2f}")
```

---

## Best Practices from Examples

### 1. Always Start with Paper Trading
Test strategies extensively before risking capital.

### 2. Use Multiple Timeframes
Analyze short-term (1mo), medium-term (6mo), and long-term (2y).

### 3. Validate with Walk-Forward
Don't just optimize on all historical data.

### 4. Monitor Risk Continuously
Set up alerts for drawdowns and position limits.

### 5. Keep Detailed Logs
Log all decisions and performance for later analysis.

---

## Next Steps

- [Understand risk management](../trading-logic/risk_management.md)
- [Learn signal generation](../trading-logic/signal_logic.md)
- [Study performance metrics](../trading-logic/performance_metrics.md)
