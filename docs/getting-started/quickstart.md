# Quick Start Guide

## First Steps

### 1. Generate a Financial Brief

```bash
python -m src.cli brief --symbols AAPL,MSFT,GOOGL
```

This will:
- Fetch market data for the specified symbols
- Analyze technical indicators
- Generate AI-powered insights
- Create a comprehensive PDF report

### 2. Run Trading Simulator

```bash
python -m src.cli simulate --symbol AAPL --strategy conservative
```

This will:
- Execute paper trades based on the strategy
- Apply risk management rules
- Track performance metrics
- Generate trade journal

### 3. Run a Backtest

```bash
python -m src.cli backtest --symbol AAPL --start 2024-01-01 --end 2024-12-31
```

This will:
- Simulate historical trading
- Generate performance metrics (Sharpe, Sortino, Max DD)
- Create equity curve visualization
- Export results to HTML/CSV

## Common Commands

### Financial Brief

```bash
# Single symbol with custom output
python -m src.cli brief --symbols AAPL --output reports/aapl_brief.pdf

# Multiple symbols
python -m src.cli brief --symbols AAPL,MSFT,GOOGL --ai-provider openai

# With specific date range
python -m src.cli brief --symbols AAPL --start 2024-01-01 --end 2024-12-31
```

### Trading Simulator

```bash
# Conservative strategy
python -m src.cli simulate --symbol AAPL --strategy conservative

# Aggressive strategy
python -m src.cli simulate --symbol MSFT --strategy aggressive --risk-percent 0.02

# With custom risk limits
python -m src.cli simulate --symbol GOOGL \
    --max-position-size 0.15 \
    --max-daily-drawdown 0.03
```

### Backtest

```bash
# Basic backtest
python -m src.cli backtest --symbol AAPL

# With date range
python -m src.cli backtest --symbol MSFT --start 2023-01-01 --end 2023-12-31

# Multiple symbols
python -m src.cli backtest --symbols AAPL,MSFT,GOOGL --parallel
```

## Makefile Shortcuts

```bash
# Format code
make fmt

# Run all checks
make precommit

# Run tests
make test

# Generate coverage report
make cov

# Build documentation
make docs

# Serve docs locally
make docs-serve
```

## Next Steps

- [CLI Reference](../user-guide/cli.md)
- [Configuration Guide](../user-guide/configuration.md)
- [Examples & Tutorials](../user-guide/examples.md)
- [Backtest Module Documentation](../modules/backtest.md)
