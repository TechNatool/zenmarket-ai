# CLI Reference

Complete command-line interface reference for ZenMarket AI.

---

## Usage

```bash
python -m src.cli [COMMAND] [OPTIONS]
```

---

## Commands

### `brief` - Generate Financial Brief

Generate a comprehensive financial brief with news, sentiment, and AI insights.

```bash
python -m src.cli brief [OPTIONS]
```

**Options:**

- `--symbols TEXT` - Comma-separated stock symbols (required)
- `--format TEXT` - Output format: `markdown`, `html`, `pdf` (default: markdown)
- `--output PATH` - Output file path (optional)
- `--use-ai` - Enable AI summarization (default: true)

**Examples:**

```bash
# Single symbol
python -m src.cli brief --symbols AAPL

# Multiple symbols
python -m src.cli brief --symbols AAPL,MSFT,GOOGL

# Save to file
python -m src.cli brief --symbols AAPL --output brief.md

# PDF format
python -m src.cli brief --symbols AAPL --format pdf
```

---

### `advisor` - Generate Trading Signals

Generate technical analysis and trading signals.

```bash
python -m src.cli advisor [OPTIONS]
```

**Options:**

- `--symbol TEXT` - Stock symbol (required)
- `--period TEXT` - Data period: `1mo`, `3mo`, `6mo`, `1y`, `2y` (default: 6mo)
- `--chart` - Generate chart (default: true)
- `--output PATH` - Output directory

**Examples:**

```bash
# Basic analysis
python -m src.cli advisor --symbol AAPL

# Custom period
python -m src.cli advisor --symbol AAPL --period 1y

# Save chart
python -m src.cli advisor --symbol AAPL --output ./reports
```

---

### `simulate` - Run Trading Simulation

Run paper trading simulation with a strategy.

```bash
python -m src.cli simulate [OPTIONS]
```

**Options:**

- `--symbol TEXT` - Stock symbol (required)
- `--strategy TEXT` - Strategy name: `conservative`, `moderate`, `aggressive`
- `--capital FLOAT` - Initial capital (default: 100000)
- `--period TEXT` - Simulation period (default: 6mo)
- `--realtime` - Enable real-time simulation

**Examples:**

```bash
# Basic simulation
python -m src.cli simulate --symbol AAPL

# Custom capital and strategy
python -m src.cli simulate --symbol AAPL --capital 50000 --strategy aggressive

# Real-time simulation
python -m src.cli simulate --symbol AAPL --realtime
```

---

### `backtest` - Run Historical Backtest

Backtest a trading strategy against historical data.

```bash
python -m src.cli backtest [OPTIONS]
```

**Options:**

- `--symbol TEXT` - Stock symbol (required)
- `--start DATE` - Start date (YYYY-MM-DD)
- `--end DATE` - End date (YYYY-MM-DD)
- `--strategy TEXT` - Strategy name
- `--capital FLOAT` - Initial capital (default: 100000)
- `--report` - Generate detailed report (default: true)
- `--output PATH` - Output directory

**Examples:**

```bash
# Basic backtest
python -m src.cli backtest --symbol AAPL --start 2024-01-01 --end 2024-12-31

# With custom strategy
python -m src.cli backtest --symbol AAPL --strategy mean_reversion --start 2023-01-01

# Save detailed report
python -m src.cli backtest --symbol AAPL --report --output ./backtests
```

---

### `live` - Run Live Trading

**⚠️ Use with extreme caution! Only for experienced traders.**

```bash
python -m src.cli live [OPTIONS]
```

**Options:**

- `--strategy TEXT` - Strategy name (required)
- `--symbols TEXT` - Comma-separated symbols
- `--broker TEXT` - Broker: `paper`, `ibkr`, `mt5` (default: paper)
- `--dry-run` - Simulate without executing trades

**Examples:**

```bash
# Paper trading (safe)
python -m src.cli live --strategy conservative --symbols AAPL --broker paper

# Dry run (no actual trades)
python -m src.cli live --strategy moderate --symbols AAPL,MSFT --dry-run
```

!!! danger "Live Trading Warning"
    - Always start with paper trading
    - Test thoroughly before going live
    - Use small position sizes initially
    - Monitor constantly
    - Understand the risks

---

## Global Options

Available for all commands:

- `--help` - Show help message
- `--version` - Show version
- `--config PATH` - Path to config file
- `--verbose` - Enable verbose output
- `--quiet` - Suppress output
- `--log-level TEXT` - Set log level: DEBUG, INFO, WARNING, ERROR

**Examples:**

```bash
# Verbose output
python -m src.cli brief --symbols AAPL --verbose

# Custom config
python -m src.cli brief --symbols AAPL --config ./my-config.env

# Debug logging
python -m src.cli brief --symbols AAPL --log-level DEBUG
```

---

## Output Formats

### Markdown (default)

```bash
python -m src.cli brief --symbols AAPL --format markdown
```

Output: Human-readable markdown file

### HTML

```bash
python -m src.cli brief --symbols AAPL --format html
```

Output: Styled HTML report

### PDF

```bash
python -m src.cli brief --symbols AAPL --format pdf
```

Output: Professional PDF document

### JSON

```bash
python -m src.cli backtest --symbol AAPL --format json
```

Output: Machine-readable JSON

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - API error
- `4` - Data error
- `5` - Trading error

---

## Environment Variables

Override config with environment variables:

```bash
# Set API key
export OPENAI_API_KEY=sk-your-key

# Run command
python -m src.cli brief --symbols AAPL
```

---

## Batch Processing

### Multiple Symbols

```bash
# Process multiple symbols
for symbol in AAPL MSFT GOOGL AMZN; do
  python -m src.cli advisor --symbol $symbol
done
```

### Scheduled Execution

```bash
# Run daily at 9:00 AM (cron)
0 9 * * * cd /path/to/zenmarket-ai && python -m src.cli brief --symbols AAPL >> daily.log 2>&1
```

---

## Piping and Redirection

### Save Output

```bash
python -m src.cli brief --symbols AAPL > brief.txt
```

### Pipe to Other Commands

```bash
python -m src.cli brief --symbols AAPL | grep "BUY"
```

### Append to Log

```bash
python -m src.cli advisor --symbol AAPL >> advisor.log 2>&1
```

---

## Debugging

### Enable Debug Logging

```bash
python -m src.cli --log-level DEBUG brief --symbols AAPL
```

### Verbose Output

```bash
python -m src.cli --verbose advisor --symbol AAPL
```

### Stack Traces

```bash
# Python will show full stack trace on errors
python -m src.cli brief --symbols INVALID_SYMBOL
```

---

## Performance Tips

### Parallel Processing

```bash
# Run multiple commands in parallel
python -m src.cli advisor --symbol AAPL &
python -m src.cli advisor --symbol MSFT &
python -m src.cli advisor --symbol GOOGL &
wait
```

### Caching

```bash
# Enable caching (in .env)
ENABLE_CACHING=true
```

---

## Common Workflows

### Daily Morning Routine

```bash
#!/bin/bash
# daily_routine.sh

# Generate brief
python -m src.cli brief --symbols AAPL,MSFT,GOOGL,AMZN

# Check signals
python -m src.cli advisor --symbol AAPL
python -m src.cli advisor --symbol MSFT

# Run simulation
python -m src.cli simulate --symbol AAPL --period 1mo
```

### Weekly Backtest

```bash
#!/bin/bash
# weekly_backtest.sh

SYMBOLS="AAPL MSFT GOOGL AMZN TSLA"
START="2024-01-01"
END="2024-12-31"

for symbol in $SYMBOLS; do
  python -m src.cli backtest \
    --symbol $symbol \
    --start $START \
    --end $END \
    --output ./backtests
done
```

---

## Troubleshooting

### Command Not Found

```bash
# Make sure you're in the project directory
cd /path/to/zenmarket-ai

# Or use absolute path
python -m src.cli --help
```

### Module Import Error

```bash
# Install package
pip install -e .
```

### API Key Error

```bash
# Check .env file exists
ls -la .env

# Verify key is set
python -c "from src.utils.config_loader import get_config; print(get_config().openai_api_key)"
```

---

## Next Steps

- [See examples](examples.md)
- [Understand trading logic](../trading-logic/signal_logic.md)
- [Configure risk management](../trading-logic/risk_management.md)
