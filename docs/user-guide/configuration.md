# Configuration Guide

This guide covers all configuration options for ZenMarket AI.

---

## Configuration File

ZenMarket AI uses environment variables loaded from a `.env` file.

### Creating Configuration

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

---

## API Keys

### OpenAI Configuration

```bash
# Required for AI features
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Optional: Organization ID
OPENAI_ORG_ID=org-your-org-id
```

### Anthropic Configuration

```bash
# Alternative AI provider
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229
```

### AI Provider Selection

```bash
# Choose provider (openai or anthropic)
AI_PROVIDER=openai
```

---

## Trading Configuration

### Capital & Fees

```bash
# Initial trading capital
INITIAL_CAPITAL=100000

# Commission per trade (0.1% = 0.001)
COMMISSION_PCT=0.001

# Slippage per trade (0.05% = 0.0005)
SLIPPAGE_PCT=0.0005
```

### Position Sizing

```bash
# Position sizing method
# Options: fixed, percent_equity, kelly, r_multiple
POSITION_SIZING_METHOD=percent_equity

# Risk per trade (2% = 0.02)
RISK_PER_TRADE=0.02

# Fixed position size (if using fixed method)
FIXED_POSITION_SIZE=100
```

---

## Risk Management

### Position Limits

```bash
# Maximum position size (10% = 0.10)
MAX_POSITION_SIZE=0.10

# Maximum positions open simultaneously
MAX_OPEN_POSITIONS=5

# Maximum allocation per symbol (20% = 0.20)
MAX_SINGLE_SYMBOL_PCT=0.20
```

### Loss Limits

```bash
# Maximum daily loss (5% = 0.05)
MAX_DAILY_LOSS_PCT=0.05

# Maximum total drawdown (10% = 0.10)
MAX_DRAWDOWN_PCT=0.10
```

### Circuit Breakers

```bash
# Enable circuit breakers
ENABLE_CIRCUIT_BREAKERS=true

# Halt trading on high volatility
CIRCUIT_BREAKER_VOLATILITY_THRESHOLD=0.05
```

---

## Advisor Configuration

### Technical Indicators

```bash
# RSI thresholds
ADVISOR_RSI_OVERSOLD=30
ADVISOR_RSI_OVERBOUGHT=70

# Moving average periods
ADVISOR_MA_SHORT=20
ADVISOR_MA_LONG=50

# Bollinger Bands
ADVISOR_BB_PERIOD=20
ADVISOR_BB_STD_DEV=2.0
```

### Signal Generation

```bash
# Minimum confidence for signals (50% = 50)
ADVISOR_MIN_CONFIDENCE=50

# Signal generation frequency
ADVISOR_UPDATE_INTERVAL=300  # seconds
```

---

## Broker Configuration

### Broker Selection

```bash
# Broker type: paper, ibkr, mt5
BROKER_TYPE=paper
```

### Interactive Brokers (IBKR)

```bash
IBKR_HOST=127.0.0.1
IBKR_PORT=7497  # 7497 for paper, 7496 for live
IBKR_CLIENT_ID=1
IBKR_ACCOUNT=DU1234567
```

### MetaTrader 5 (MT5)

```bash
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo
MT5_PATH=/path/to/terminal64.exe  # Windows only
```

---

## Data Configuration

### Directories

```bash
# Data storage directory
DATA_DIRECTORY=data

# Report output directory
REPORT_OUTPUT_DIR=reports

# Log directory
LOG_DIRECTORY=logs
```

### Market Data

```bash
# Default data period for analysis
DEFAULT_PERIOD=6mo  # 1mo, 3mo, 6mo, 1y, 2y, 5y, max

# Data update interval (seconds)
DATA_UPDATE_INTERVAL=300
```

---

## Logging

### Log Levels

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### Log Files

```bash
# Maximum log file size (bytes)
LOG_FILE_MAX_BYTES=10485760  # 10MB

# Number of backup files
LOG_FILE_BACKUP_COUNT=5

# Log format
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

---

## Performance

### Caching

```bash
# Enable data caching
ENABLE_CACHING=true

# Cache TTL (seconds)
CACHE_TTL=300  # 5 minutes
```

### Parallel Processing

```bash
# Number of worker threads
NUM_WORKERS=4

# Enable parallel backtesting
ENABLE_PARALLEL_BACKTEST=true
```

---

## Complete Configuration Example

```bash
# ==============================================
# ZenMarket AI Configuration
# ==============================================

# ----------------------------------------------
# API Keys
# ----------------------------------------------
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
AI_PROVIDER=openai

# ----------------------------------------------
# Trading
# ----------------------------------------------
INITIAL_CAPITAL=100000
COMMISSION_PCT=0.001
SLIPPAGE_PCT=0.0005
POSITION_SIZING_METHOD=percent_equity
RISK_PER_TRADE=0.02

# ----------------------------------------------
# Risk Management
# ----------------------------------------------
MAX_POSITION_SIZE=0.10
MAX_DAILY_LOSS_PCT=0.05
MAX_DRAWDOWN_PCT=0.10
MAX_OPEN_POSITIONS=5
ENABLE_CIRCUIT_BREAKERS=true

# ----------------------------------------------
# Advisor
# ----------------------------------------------
ADVISOR_RSI_OVERSOLD=30
ADVISOR_RSI_OVERBOUGHT=70
ADVISOR_MA_SHORT=20
ADVISOR_MA_LONG=50
ADVISOR_MIN_CONFIDENCE=50

# ----------------------------------------------
# Broker
# ----------------------------------------------
BROKER_TYPE=paper

# ----------------------------------------------
# Directories
# ----------------------------------------------
DATA_DIRECTORY=data
REPORT_OUTPUT_DIR=reports
LOG_DIRECTORY=logs

# ----------------------------------------------
# Logging
# ----------------------------------------------
LOG_LEVEL=INFO
```

---

## Environment-Specific Configurations

### Development

```bash
# .env.development
LOG_LEVEL=DEBUG
BROKER_TYPE=paper
ENABLE_CACHING=false
```

### Production

```bash
# .env.production
LOG_LEVEL=WARNING
BROKER_TYPE=ibkr
ENABLE_CACHING=true
ENABLE_CIRCUIT_BREAKERS=true
```

---

## Configuration Validation

Validate your configuration:

```bash
python -m src.utils.config_loader --validate
```

---

## Best Practices

### 1. Use Environment-Specific Files

```
.env.development
.env.staging
.env.production
```

### 2. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.*
```

### 3. Document Custom Settings

Add comments to your `.env`:
```bash
# Custom RSI threshold for my strategy
ADVISOR_RSI_OVERSOLD=25  # More aggressive
```

### 4. Backup Configuration

```bash
cp .env .env.backup
```

---

## Troubleshooting

### Issue: Configuration not loading

**Solution**: Check file location and name
```bash
ls -la .env  # Should be in project root
```

### Issue: API key not working

**Solution**: Check for extra spaces
```bash
# Bad
OPENAI_API_KEY= sk-key-with-space

# Good
OPENAI_API_KEY=sk-key-no-space
```

---

## Next Steps

- [Learn CLI commands](cli.md)
- [Try examples](examples.md)
- [Understand risk management](../trading-logic/risk_management.md)
