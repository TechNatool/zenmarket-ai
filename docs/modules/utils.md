# Utilities Module

The Utils module provides core utilities for configuration, logging, and date handling.

---

## Components

### 1. Configuration Loader (`config_loader.py`)

Loads and validates configuration from environment variables.

```python
from src.utils.config_loader import get_config

config = get_config()

# Access configuration
api_key = config.openai_api_key
data_dir = config.data_directory
log_level = config.log_level
```

**Features:**
- Environment variable loading
- Pydantic validation
- Type checking
- Default values
- Secret masking in logs

**Configuration:**
```python
@dataclass
class Config:
    # API Keys
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    
    # Directories
    data_directory: Path
    report_output_dir: Path
    log_directory: Path
    
    # Logging
    log_level: str = "INFO"
    
    # Trading
    initial_capital: float = 100000.0
    commission_pct: float = 0.001
    slippage_pct: float = 0.0005
```

---

### 2. Logger (`logger.py`)

Structured logging with colors and formatting.

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting backtest")
logger.warning("High volatility detected")
logger.error("Order execution failed")
logger.debug("Technical details...")
```

**Features:**
- Colored console output
- File rotation
- Structured logging
- Multiple log levels
- Exception tracking

**Log Levels:**
- `DEBUG`: Detailed diagnostic info
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical failures

**Configuration:**
```bash
# .env
LOG_LEVEL=INFO
LOG_DIRECTORY=logs
LOG_FILE_MAX_BYTES=10485760  # 10MB
LOG_FILE_BACKUP_COUNT=5
```

---

### 3. Date Utils (`date_utils.py`)

Date and time handling utilities.

```python
from src.utils.date_utils import (
    parse_date,
    is_market_open,
    get_trading_days,
    convert_timezone
)

# Parse various date formats
date = parse_date("2024-01-15")
date = parse_date("Jan 15, 2024")

# Check if market is open
if is_market_open():
    print("Market is open")

# Get trading days
days = get_trading_days(start="2024-01-01", end="2024-12-31")
print(f"Trading days: {len(days)}")

# Timezone conversion
utc_time = convert_timezone(local_time, from_tz="US/Eastern", to_tz="UTC")
```

**Functions:**

#### Market Hours
```python
def is_market_open(dt: datetime = None) -> bool:
    """Check if US market is currently open."""
    # NYSE: 9:30 AM - 4:00 PM ET, Mon-Fri
```

#### Trading Calendar
```python
def get_trading_days(start: str, end: str) -> List[datetime]:
    """Get list of trading days (excluding weekends and holidays)."""
```

#### Date Parsing
```python
def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    # Supports: YYYY-MM-DD, MM/DD/YYYY, etc.
```

---

## Environment Variables

Complete list of supported environment variables:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Data Sources
NEWSAPI_KEY=...

# Directories
DATA_DIRECTORY=data
REPORT_OUTPUT_DIR=reports
LOG_DIRECTORY=logs

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Trading Configuration
INITIAL_CAPITAL=100000
COMMISSION_PCT=0.001
SLIPPAGE_PCT=0.0005

# Risk Management
MAX_POSITION_SIZE=0.10
MAX_DAILY_LOSS_PCT=0.05
MAX_DRAWDOWN_PCT=0.10

# Broker
BROKER_TYPE=paper  # paper, ibkr, mt5
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
MT5_LOGIN=...
MT5_PASSWORD=...
MT5_SERVER=...

# Advisor
ADVISOR_RSI_OVERSOLD=30
ADVISOR_RSI_OVERBOUGHT=70
ADVISOR_MIN_CONFIDENCE=50

# AI
AI_PROVIDER=openai  # openai, anthropic
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-opus-20240229
```

---

## Best Practices

### 1. Use Environment Variables

Never hardcode secrets:

```python
# ❌ BAD
api_key = "sk-1234567890"

# ✅ GOOD
from src.utils.config_loader import get_config
api_key = get_config().openai_api_key
```

### 2. Structured Logging

Use appropriate log levels:

```python
logger.debug("Fetching market data for AAPL")  # Development only
logger.info("Backtest completed successfully")  # Normal operation
logger.warning("Position size exceeds 10% of portfolio")  # Caution
logger.error("Failed to connect to broker")  # Errors
logger.critical("Circuit breaker triggered")  # Critical issues
```

### 3. Date Handling

Always use timezone-aware datetimes:

```python
from datetime import datetime
import pytz

# ✅ GOOD
now = datetime.now(pytz.UTC)
eastern = datetime.now(pytz.timezone('US/Eastern'))

# ❌ BAD
now = datetime.now()  # Naive datetime
```

---

## Testing

- `tests/utils/test_utils.py` - 25 tests

Coverage:
- `config_loader.py`: 90.54%
- `logger.py`: 100%
- `date_utils.py`: 94.12%
