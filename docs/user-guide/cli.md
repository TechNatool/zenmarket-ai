# CLI Usage

## Overview

ZenMarket AI provides a comprehensive command-line interface for all operations.

## General Syntax

```bash
python -m src.cli [COMMAND] [OPTIONS]
```

## Global Options

```bash
--help, -h          Show help message
--version, -v       Show version
--verbose           Enable verbose output
--config FILE       Use custom config file
```

## Commands

### brief

Generate financial analysis briefing.

```bash
python -m src.cli brief [OPTIONS]

Options:
  --symbols TEXT         Comma-separated symbols (required)
  --output PATH         Output file path
  --format [pdf|html]   Output format (default: pdf)
  --ai-provider TEXT    AI provider (openai|anthropic)
  --start DATE          Start date (YYYY-MM-DD)
  --end DATE            End date (YYYY-MM-DD)
```

**Examples:**

```bash
# Basic usage
python -m src.cli brief --symbols AAPL

# Multiple symbols with custom output
python -m src.cli brief --symbols AAPL,MSFT,GOOGL --output my_brief.pdf

# With date range
python -m src.cli brief --symbols AAPL --start 2024-01-01 --end 2024-12-31
```

### simulate

Run trading simulator (paper trading).

```bash
python -m src.cli simulate [OPTIONS]

Options:
  --symbol TEXT              Trading symbol (required)
  --strategy TEXT            Strategy name
  --risk-percent FLOAT       Risk per trade (default: 0.01)
  --max-position-size FLOAT  Max position size (default: 0.20)
  --max-daily-drawdown FLOAT Max daily drawdown (default: 0.05)
  --initial-cash FLOAT       Initial cash (default: 100000)
```

**Examples:**

```bash
# Conservative strategy
python -m src.cli simulate --symbol AAPL --strategy conservative

# Custom risk parameters
python -m src.cli simulate --symbol MSFT \
    --risk-percent 0.02 \
    --max-position-size 0.15
```

### backtest

Run historical backtest.

```bash
python -m src.cli backtest [OPTIONS]

Options:
  --symbols TEXT        Comma-separated symbols
  --start DATE          Start date (YYYY-MM-DD)
  --end DATE            End date (YYYY-MM-DD)
  --strategy TEXT       Strategy name
  --output PATH         Output directory
  --parallel            Run in parallel (for multiple symbols)
```

**Examples:**

```bash
# Single symbol backtest
python -m src.cli backtest --symbol AAPL --start 2024-01-01

# Multiple symbols in parallel
python -m src.cli backtest --symbols AAPL,MSFT,GOOGL --parallel

# With custom output
python -m src.cli backtest --symbol AAPL --output reports/backtests/
```

## Configuration

CLI respects environment variables from `.env`:

```bash
# Override with environment variables
TRADING_MODE=paper python -m src.cli simulate --symbol AAPL

# Use custom config file
python -m src.cli --config my_config.env brief --symbols AAPL
```

## Logging

Control log level:

```bash
# Debug mode
LOG_LEVEL=DEBUG python -m src.cli simulate --symbol AAPL

# Quiet mode (errors only)
LOG_LEVEL=ERROR python -m src.cli simulate --symbol AAPL
```

## Output Files

Default output locations:

- **Reports**: `reports/`
- **Logs**: `logs/`
- **Backtests**: `reports/backtests/`
- **Journal**: `data/journal/`

## Error Handling

The CLI provides clear error messages:

```bash
# Missing required argument
$ python -m src.cli brief
Error: Missing required option '--symbols'

# Invalid symbol
$ python -m src.cli simulate --symbol INVALID
Error: Symbol 'INVALID' not found

# API key missing
$ python -m src.cli brief --symbols AAPL
Error: OPENAI_API_KEY or ANTHROPIC_API_KEY required in .env
```

## Shell Completion

Generate shell completion:

```bash
# Bash
python -m src.cli --install-completion bash

# Zsh
python -m src.cli --install-completion zsh

# Fish
python -m src.cli --install-completion fish
```

## Tips & Tricks

### Batch Processing

```bash
# Process multiple symbols
for symbol in AAPL MSFT GOOGL; do
    python -m src.cli brief --symbols $symbol --output reports/${symbol}_brief.pdf
done
```

### Cron Jobs

```bash
# Daily briefing at 6 AM
0 6 * * * cd /path/to/zenmarket-ai && python -m src.cli brief --symbols AAPL,MSFT
```

### Docker Usage

```bash
docker run -it --rm \
    -v $(pwd):/app \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    zenmarket-ai:latest \
    python -m src.cli brief --symbols AAPL
```
