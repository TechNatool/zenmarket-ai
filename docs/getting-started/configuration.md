# Configuration

## Environment Variables

ZenMarket AI uses a `.env` file for configuration.

### Setup

```bash
# Copy example configuration
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

### Required Variables

```bash
# AI Providers (at least one required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: News API
NEWS_API_KEY=your_newsapi_key_here
```

### Optional Variables

```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Trading (Paper trading by default)
TRADING_MODE=paper  # paper or live
INITIAL_CASH=100000

# Risk Management
MAX_POSITION_SIZE_PCT=0.20
MAX_RISK_PER_TRADE_PCT=0.01
MAX_DAILY_DRAWDOWN_PCT=0.05
```

## Security

!!! warning "API Key Security"
    - Never commit `.env` file to version control
    - Keep your API keys confidential
    - Rotate keys regularly
    - Use separate keys for development and production

## Next Steps

- [Quick Start Guide](quickstart.md)
- [CLI Usage](../user-guide/cli.md)
