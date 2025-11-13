# Backtesting Guide

ZenMarket AI provides professional-grade backtesting capabilities to test trading strategies on historical data before deploying them live.

## Overview

The backtesting engine simulates historical order execution with realistic:
- **Slippage**: Configurable basis points (default: 1.5 bps)
- **Commissions**: Per-trade fees (default: $2.00)
- **Fill Simulation**: Uses OHLC data for realistic fills
- **Risk Management**: Full integration with existing risk limits

## Quick Start

### Basic Backtest

```bash
python -m src.cli backtest \
  --symbols "AAPL,MSFT,GOOGL" \
  --from 2024-01-01 \
  --to 2024-12-31 \
  --initial-capital 100000
```

### Advanced Configuration

```bash
python -m src.cli backtest \
  --symbols "AAPL" \
  --from 2023-01-01 \
  --to 2024-01-01 \
  --initial-capital 50000 \
  --risk-per-trade 0.02 \
  --max-positions 3 \
  --sizing-method kelly \
  --interval 1d
```

## Architecture

```
┌─────────────────────────────────────────────┐
│          BacktestEngine                     │
│  - Orchestrates entire backtest             │
│  - Loads historical data                    │
│  - Iterates through time                    │
└─────────────────┬───────────────────────────┘
                  │
                  ├─► ┌──────────────────────┐
                  │   │   BacktestBroker     │
                  │   │  - OHLC-based fills  │
                  │   │  - Position tracking │
                  │   └──────────────────────┘
                  │
                  ├─► ┌──────────────────────┐
                  │   │  ExecutionEngine     │
                  │   │  - Signal execution  │
                  │   │  - Risk validation   │
                  │   └──────────────────────┘
                  │
                  ├─► ┌──────────────────────┐
                  │   │  SignalGenerator     │
                  │   │  - Technical signals │
                  │   └──────────────────────┘
                  │
                  └─► ┌──────────────────────┐
                      │ PerformanceMetrics   │
                      │  - Sharpe/Sortino    │
                      │  - Drawdown analysis │
                      └──────────────────────┘
```

## Performance Metrics

The backtesting engine calculates comprehensive performance metrics:

### Returns Metrics
- **Total Return**: Overall percentage gain/loss
- **Annualized Return**: CAGR (Compound Annual Growth Rate)
- **Average Daily Return**: Mean daily percentage change

### Risk Metrics
- **Sharpe Ratio**: Risk-adjusted return (>1.0 is good, >2.0 is excellent)
- **Sortino Ratio**: Downside risk-adjusted return
- **Calmar Ratio**: Return relative to maximum drawdown
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Annualized standard deviation

### Trade Statistics
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss ratio
- **Average Win/Loss**: Mean profit and loss per trade
- **Expectancy**: Expected value per trade
- **Risk/Reward Ratio**: Average win / average loss

## Output Reports

### Console Output
Prints detailed performance summary to terminal:
```
PERFORMANCE SUMMARY
-------------------
Total Return: 15.23%
Sharpe Ratio: 1.85
Max Drawdown: -8.45%
Win Rate: 62.5%
```

### Markdown Report
Detailed markdown report with tables:
- `reports/backtest/TechnicalStrategy_YYYYMMDD_HHMMSS_report.md`

### PDF Report
Professional PDF with metrics and metadata:
- `reports/backtest/TechnicalStrategy_YYYYMMDD_HHMMSS_report.pdf`

### Visualizations
PNG charts saved to `reports/backtest/`:
- **Equity Curve**: Portfolio value over time
- **Drawdown Plot**: Underwater equity chart
- **Returns Distribution**: Histogram of trade P&L

## Parallel Backtesting

Test multiple configurations simultaneously:

```python
from src.backtest.backtest_engine import BacktestEngine, BacktestConfig
from decimal import Decimal

configs = [
    BacktestConfig(
        symbols=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        risk_per_trade_pct=0.01,
        strategy_name="Conservative"
    ),
    BacktestConfig(
        symbols=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        risk_per_trade_pct=0.02,
        strategy_name="Aggressive"
    ),
]

results = BacktestEngine.run_parallel(configs, max_workers=4)

for result in results:
    print(f"{result.config.strategy_name}: {result.metrics.total_return_pct:.2f}%")
```

## Best Practices

### 1. Data Quality
- Ensure sufficient historical data (minimum 3 months)
- Account for corporate actions (splits, dividends)
- Use adjusted close prices

### 2. Realistic Assumptions
- Include commissions and slippage
- Account for market hours
- Consider liquidity constraints

### 3. Overfitting Prevention
- Test on out-of-sample data
- Use walk-forward analysis
- Avoid curve-fitting parameters

### 4. Risk Management
- Always include stop losses
- Limit position sizes
- Test circuit breakers

## Example: Custom Backtest

```python
from src.backtest.backtest_engine import BacktestEngine, BacktestConfig
from src.backtest.visualizer import BacktestVisualizer
from decimal import Decimal
from pathlib import Path

# Configure backtest
config = BacktestConfig(
    symbols=["AAPL", "MSFT"],
    start_date="2023-01-01",
    end_date="2024-01-01",
    initial_capital=Decimal("100000"),
    slippage_bps=2.0,  # More conservative slippage
    commission_per_trade=Decimal("5.0"),
    risk_per_trade_pct=0.015,  # 1.5% risk per trade
    max_positions=3,
    strategy_name="MyStrategy"
)

# Run backtest
engine = BacktestEngine(config)
result = engine.run()

# Print summary
BacktestVisualizer.print_summary(result.metrics, "MyStrategy")

# Generate reports
output_dir = Path("my_backtests")
output_dir.mkdir(exist_ok=True)

BacktestVisualizer.plot_equity_curve(
    result.equity_curve,
    output_dir / "equity.png"
)

BacktestVisualizer.generate_markdown_report(
    result.metrics,
    "MyStrategy",
    ["AAPL", "MSFT"],
    output_dir / "report.md"
)
```

## Limitations

- **Slippage**: Simplified model (constant basis points)
- **Market Impact**: Not modeled for large orders
- **Liquidity**: Assumes all orders can be filled
- **Dividends**: Not currently included
- **Corporate Actions**: Requires pre-adjusted data

## Troubleshooting

### Insufficient Data Error
**Problem**: `No data available for symbol`
**Solution**: Check symbol name, date range, and internet connection

### Low Win Rate
**Problem**: Win rate < 40%
**Solution**: Review signal generation logic, adjust indicators

### High Drawdown
**Problem**: Max drawdown > 20%
**Solution**: Tighten stop losses, reduce position sizes, increase diversification

## Next Steps

- Review [BROKERS.md](BROKERS.md) for live trading
- See [examples/](../examples/) for sample strategies
- Check [API documentation](api/backtest.md) for programmatic access

---

*For questions or issues, visit: https://github.com/TechNatool/zenmarket-ai/issues*
