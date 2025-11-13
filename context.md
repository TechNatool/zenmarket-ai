# ZenMarket AI - Complete Project Context

**Version:** 1.0.0  
**Last Updated:** 2025-01-13  
**Maintainer:** TechNatool  
**Claude Code AI Ready:** ✅

---

## 🎯 Purpose of This Document

This `context.md` file is the **single source of truth** for the ZenMarket AI project. It is specifically designed to enable Claude Code AI and human developers to:

1. **Understand the entire project** in 10-15 minutes
2. **Resume work immediately** without searching through code
3. **Maintain code consistency** across sessions
4. **Add features correctly** following established patterns
5. **Debug efficiently** with full context

**Before making ANY changes to this project, READ THIS FILE FIRST.**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [How Claude Code AI Should Use This File](#claude-code-ai-instructions)
3. [Architecture](#architecture)
4. [Technical Documentation](#technical-documentation)
5. [Development Workflow](#development-workflow)
6. [12-Month Roadmap](#roadmap)
7. [Guide for Nathan](#guide-for-nathan)

---

## 🌟 Project Overview

### What is ZenMarket AI?

ZenMarket AI is a **professional-grade AI-powered financial intelligence and automated trading system** designed for:

- **Quantitative researchers** - Backtest strategies with realistic simulation
- **Algorithmic traders** - Build and test automated trading systems
- **Market analysts** - Monitor news and sentiment across assets
- **Educators & students** - Learn financial markets and trading

### Core Value Proposition

```
Real-Time Market Data + AI Analysis + Technical Signals + Risk Management 
                              ↓
            Actionable Trading Intelligence
```

### Key Statistics (as of 2025-01-13)

- **Lines of Code:** ~8,904 (Python)
- **Test Files:** 27
- **Total Tests:** 378 (100% passing)
- **Test Coverage:** 63.70%
- **Priority Module Coverage:** 95-100%
- **Documentation Pages:** 17
- **Commits:** 46
- **Python Version:** 3.11+
- **License:** MIT

### Project Status

✅ **Production Ready** - Phase 5 completed
- All tests passing
- Comprehensive documentation
- Risk management implemented
- Multiple broker adapters
- CI/CD pipeline configured

---

## 🤖 Claude Code AI Instructions

### How to Use This File

**CRITICAL:** Every time Claude Code AI is invoked to work on this project, follow this workflow:

1. **Read this file first** (top to bottom or relevant sections)
2. **Understand the context** of the task within the architecture
3. **Follow established patterns** documented here
4. **Maintain consistency** with existing code style
5. **Update this file** if making architectural changes

### Typical Claude Workflows

#### Workflow 1: Bug Fix

```
User: "Fix the bug in signal generation where RSI is calculated incorrectly"

Claude Action Plan:
1. Read context.md → Find "Signal Generation" section
2. Understand RSI calculation logic
3. Locate src/advisor/indicators.py
4. Read the function calculate_rsi()
5. Identify the bug
6. Fix using pandas/numpy patterns documented
7. Write/update tests in tests/advisor/
8. Run tests: pytest tests/advisor/
9. Commit: "fix(advisor): correct RSI calculation formula"
```

#### Workflow 2: Add New Feature

```
User: "Add support for Fibonacci retracement levels in technical analysis"

Claude Action Plan:
1. Read context.md → "Adding New Indicators" section
2. Review TechnicalIndicators class structure
3. Create new method: calculate_fibonacci_levels()
4. Follow indicator calculation patterns
5. Add to calculate_all() method
6. Update SignalGenerator to use new indicator
7. Write comprehensive tests
8. Update docs/modules/advisor.md
9. Commit: "feat(advisor): add Fibonacci retracement indicators"
```

#### Workflow 3: Continue Interrupted Work

```
User: "Continue the work from yesterday on implementing portfolio optimization"

Claude Action Plan:
1. Read context.md → Check "Current Work" section
2. Git log to see last commits
3. Check TODO comments in code
4. Review open files/incomplete functions
5. Continue implementation following patterns
6. Complete tests
7. Update documentation
8. Mark task as complete in context.md
```

#### Workflow 4: Generate Tests

```
User: "Generate comprehensive tests for the PnL tracker module"

Claude Action Plan:
1. Read context.md → "Testing Standards" section
2. Understand PnLTracker class (src/execution/pnl_tracker.py)
3. Review existing test patterns in tests/execution/
4. Create tests/execution/test_pnl_tracker.py
5. Cover all methods with unit tests
6. Add edge cases and error conditions
7. Ensure hermetic (no external dependencies)
8. Run: pytest tests/execution/test_pnl_tracker.py -v --cov
9. Commit: "test(execution): add comprehensive PnL tracker tests"
```

#### Workflow 5: Optimize Code

```
User: "Optimize the backtest engine for better performance"

Claude Action Plan:
1. Read context.md → "Performance Optimization" section
2. Profile the code to identify bottlenecks
3. Review optimization guidelines
4. Apply vectorized operations (pandas/numpy)
5. Reduce redundant calculations
6. Add caching where appropriate
7. Ensure tests still pass
8. Benchmark performance improvement
9. Document optimization in code comments
10. Commit: "perf(backtest): optimize engine with vectorization"
```

### Code Reading Strategy for Claude

When asked to work on ZenMarket AI:

```python
# Step 1: Read context.md (THIS FILE)
# - Understand project architecture
# - Find relevant modules
# - Review established patterns

# Step 2: Locate relevant code
# - Use file structure documented below
# - Read related modules (not just target file)

# Step 3: Understand data flow
# - Trace inputs → processing → outputs
# - Check API contracts (types, returns)

# Step 4: Maintain consistency
# - Follow naming conventions
# - Use same libraries (pandas, numpy, pytest)
# - Apply same patterns

# Step 5: Test thoroughly
# - Write tests first (TDD) or alongside
# - Ensure hermetic (mock externals)
# - Run full suite before committing
```

---

## 🏗️ Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ZenMarket AI System                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Data Layer   │  │ Analysis     │  │ Execution    │ │
│  │              │→ │ Engine       │→ │ Layer        │ │
│  │ • Market     │  │              │  │              │ │
│  │ • News       │  │ • Sentiment  │  │ • Risk Mgmt  │ │
│  │ • Prices     │  │ • AI Summary │  │ • Position   │ │
│  └──────────────┘  │ • Indicators │  │ • Orders     │ │
│                    │ • Signals    │  └──────────────┘ │
│                    └──────────────┘         │         │
│                                             ↓         │
│                    ┌──────────────┐  ┌──────────────┐ │
│                    │ Reporting    │  │ Brokers      │ │
│                    │              │  │              │ │
│                    │ • P&L        │  │ • Paper      │ │
│                    │ • Metrics    │  │ • IBKR       │ │
│                    │ • Visualize  │  │ • MT5        │ │
│                    └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow (End-to-End)

```
1. FETCH
   User Request → CLI → MarketData / NewsFetcher
   ↓
   
2. PREPROCESS
   Raw Data → Cleaning → Normalization → Technical Indicators
   ↓
   
3. ANALYZE
   Data → Sentiment Analysis → AI Summarization → Pattern Detection
   ↓
   
4. GENERATE SIGNALS
   Analysis Results → Signal Generator → BUY/SELL/HOLD + Confidence
   ↓
   
5. RISK ASSESSMENT
   Signal → Risk Manager → Position Sizer → Approve/Reject
   ↓
   
6. EXECUTION
   Approved Trade → Execution Engine → Broker (Paper/Live)
   ↓
   
7. TRACK & LOG
   Trade Result → PnL Tracker → Trade Journal → Metrics
   ↓
   
8. REPORT
   Performance Data → Report Generator → Visualizer → PDF/HTML
```

### Module Structure

```
src/
├── advisor/              # Trading signals and technical analysis
│   ├── signal_generator.py    # Core signal generation logic
│   ├── indicators.py          # Technical indicators (RSI, MA, BB, MACD)
│   ├── plotter.py             # Chart generation
│   └── advisor_report.py      # Report generation
│
├── backtest/            # Historical strategy testing
│   ├── backtest_engine.py     # Backtest orchestration
│   ├── backtest_broker.py     # Simulated broker for backtest
│   ├── metrics.py             # Performance calculations
│   └── visualizer.py          # Equity curves, charts
│
├── brokers/             # Broker adapters
│   ├── broker_factory.py      # Broker selection/creation
│   ├── ibkr_adapter.py        # Interactive Brokers
│   └── mt5_adapter.py         # MetaTrader 5
│
├── core/                # Core analysis components
│   ├── market_data.py         # Market data fetching (yfinance)
│   ├── news_fetcher.py        # News aggregation (RSS, APIs)
│   ├── sentiment_analyzer.py  # Sentiment analysis (lexicon + AI)
│   ├── summarizer.py          # AI summarization (OpenAI/Anthropic)
│   └── report_generator.py    # Report creation (MD, HTML, PDF)
│
├── execution/           # Trading execution
│   ├── execution_engine.py    # Core execution orchestrator
│   ├── broker_simulator.py    # Paper trading simulator
│   ├── broker_base.py         # Base broker interface
│   ├── position_sizing.py     # Position sizing strategies
│   ├── risk_manager.py        # Risk controls
│   ├── order_types.py         # Order types (Market, Limit, Stop)
│   ├── pnl_tracker.py         # P&L tracking
│   ├── journal.py             # Trade logging
│   └── compliance.py          # Trading rules enforcement
│
├── utils/               # Utilities
│   ├── config_loader.py       # Configuration management
│   ├── logger.py              # Logging setup
│   └── date_utils.py          # Date/time utilities
│
├── cli.py               # Command-line interface
└── main.py              # Main entry point
```

### Key Design Patterns

1. **Strategy Pattern** - Multiple position sizing strategies
2. **Factory Pattern** - Broker creation (broker_factory.py)
3. **Observer Pattern** - Event notifications in execution
4. **Singleton Pattern** - Configuration (get_config)
5. **Template Method** - Backtest engine flow
6. **Dependency Injection** - Broker passed to execution engine

---

## 📚 Technical Documentation

### Technology Stack

| Category | Technology | Reason |
|----------|-----------|--------|
| **Language** | Python 3.11+ | Type hints, dataclasses, modern features |
| **Data** | pandas, numpy | Vectorized operations, financial data |
| **Market Data** | yfinance | Free, reliable, historical data |
| **AI** | OpenAI, Anthropic | Best-in-class LLMs for analysis |
| **Visualization** | matplotlib, seaborn | Professional charts |
| **Testing** | pytest | Industry standard, plugins |
| **Type Checking** | mypy | Static type checking |
| **Code Quality** | black, isort, ruff | Consistent formatting |
| **Documentation** | MkDocs Material | Beautiful, searchable |

### External APIs

#### 1. yfinance (Market Data)

```python
import yfinance as yf

# Usage pattern
ticker = yf.Ticker("AAPL")
data = ticker.history(period="6mo")

# Returns: DataFrame with OHLCV + indicators
# Columns: Open, High, Low, Close, Volume
```

**Rate Limits:** None (Yahoo Finance is free)  
**Error Handling:** Retry with exponential backoff

#### 2. OpenAI (AI Summarization)

```python
from openai import OpenAI

client = OpenAI(api_key=config.openai_api_key)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

# Returns: AI-generated text
```

**Rate Limits:** 10,000 RPM (Tier 1)  
**Cost:** ~$0.03 per 1K tokens (GPT-4)  
**Fallback:** Use Anthropic or lexicon-based analysis

#### 3. Anthropic (Alternative AI)

```python
from anthropic import Anthropic

client = Anthropic(api_key=config.anthropic_api_key)
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": prompt}]
)

# Returns: AI-generated text
```

**Rate Limits:** 1,000 RPM  
**Cost:** ~$0.015 per 1K tokens  
**Fallback:** OpenAI or lexicon

#### 4. Interactive Brokers (IBKR)

```python
from ib_insync import IB, MarketOrder

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

order = MarketOrder('BUY', 100)
trade = ib.placeOrder(contract, order)

# Returns: Trade confirmation
```

**Requirements:** TWS or Gateway running  
**Ports:** 7497 (paper), 7496 (live)  
**Status:** Windows/Linux/Mac compatible

#### 5. MetaTrader 5 (MT5)

```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(login=config.mt5_login, password=config.mt5_password)

order = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "volume": 1.0,
    "type": mt5.ORDER_TYPE_BUY
}
result = mt5.order_send(order)

# Returns: Order result
```

**Requirements:** MT5 terminal (Windows only)  
**Status:** Forex/CFD trading

### Core Algorithms

#### Signal Generation Algorithm

```python
def generate_signal(data, indicators):
    """
    Multi-indicator signal generation
    
    Logic:
    1. Calculate technical indicators (RSI, MA, BB, MACD)
    2. Count bullish vs bearish signals
    3. Aggregate signals with confidence scoring
    4. Return BUY/SELL/HOLD with confidence
    """
    buy_signals = 0
    sell_signals = 0
    reasons = []
    
    # RSI Analysis
    rsi = indicators['rsi'].iloc[-1]
    if rsi < 30:
        buy_signals += 1
        reasons.append("RSI oversold")
    elif rsi > 70:
        sell_signals += 1
        reasons.append("RSI overbought")
    
    # Moving Average Cross
    ma20 = indicators['ma20'].iloc[-1]
    ma50 = indicators['ma50'].iloc[-1]
    if ma20 > ma50:
        buy_signals += 1
        reasons.append("MA20 > MA50")
    else:
        sell_signals += 1
        reasons.append("MA20 < MA50")
    
    # Bollinger Bands
    price = data['Close'].iloc[-1]
    bb_lower = indicators['bb_lower'].iloc[-1]
    bb_upper = indicators['bb_upper'].iloc[-1]
    if price < bb_lower:
        buy_signals += 1
        reasons.append("Price < BB lower")
    elif price > bb_upper:
        sell_signals += 1
        reasons.append("Price > BB upper")
    
    # MACD
    macd = indicators['macd'].iloc[-1]
    macd_signal = indicators['macd_signal'].iloc[-1]
    if macd > macd_signal:
        buy_signals += 1
        reasons.append("MACD bullish")
    else:
        sell_signals += 1
        reasons.append("MACD bearish")
    
    # Determine signal
    if buy_signals > sell_signals:
        signal = "BUY"
        confidence = calculate_confidence(buy_signals, sell_signals)
    elif sell_signals > buy_signals:
        signal = "SELL"
        confidence = calculate_confidence(sell_signals, buy_signals)
    else:
        signal = "HOLD"
        confidence = 50
    
    return TradingSignal(
        signal=signal,
        confidence=confidence,
        reasons=reasons
    )
```

#### Risk Management Algorithm

```python
def check_trade_risk(trade, account):
    """
    Multi-layer risk validation
    
    Checks:
    1. Position size limits (max 10% per position)
    2. Account balance sufficient
    3. Daily loss limit not exceeded (max 5%)
    4. Maximum drawdown not breached (max 10%)
    5. Max open positions (5 concurrent)
    6. Concentration limits (20% per symbol)
    
    Returns: (approved: bool, reason: str)
    """
    # Check 1: Position size
    position_value = trade.quantity * trade.price
    position_pct = position_value / account.equity
    if position_pct > 0.10:
        return False, "Position exceeds 10% limit"
    
    # Check 2: Account balance
    required_capital = position_value + trade.commission
    if account.available_capital < required_capital:
        return False, "Insufficient capital"
    
    # Check 3: Daily loss limit
    daily_loss_pct = account.daily_loss / account.starting_equity
    if daily_loss_pct >= 0.05:
        return False, "Daily loss limit (5%) exceeded"
    
    # Check 4: Maximum drawdown
    drawdown_pct = (account.peak_equity - account.equity) / account.peak_equity
    if drawdown_pct >= 0.10:
        return False, "Max drawdown (10%) exceeded"
    
    # Check 5: Max open positions
    if len(account.open_positions) >= 5:
        return False, "Maximum 5 positions already open"
    
    # Check 6: Concentration limits
    symbol_exposure = account.get_symbol_exposure(trade.symbol)
    if (symbol_exposure + position_value) / account.equity > 0.20:
        return False, f"{trade.symbol} would exceed 20% concentration"
    
    return True, "Trade approved"
```

#### Performance Metrics Calculation

```python
def calculate_metrics(trades, equity_curve, initial_capital):
    """
    Comprehensive performance metrics
    
    Calculates:
    - Returns: Total, CAGR, Monthly/Annual
    - Risk-Adjusted: Sharpe, Sortino, Calmar
    - Risk: Max DD, Volatility, VaR, CVaR
    - Trading Stats: Win rate, Profit factor, Expectancy
    """
    # Total Return
    final_equity = equity_curve.iloc[-1]
    total_return = (final_equity - initial_capital) / initial_capital
    
    # CAGR
    years = len(equity_curve) / 252  # Trading days
    cagr = ((final_equity / initial_capital) ** (1 / years)) - 1
    
    # Sharpe Ratio
    returns = equity_curve.pct_change().dropna()
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    
    # Maximum Drawdown
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Win Rate
    winning_trades = [t for t in trades if t.pnl > 0]
    win_rate = len(winning_trades) / len(trades) if trades else 0
    
    # Profit Factor
    gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
    gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    return PerformanceMetrics(
        total_return_pct=total_return * 100,
        cagr=cagr * 100,
        sharpe_ratio=sharpe,
        max_drawdown_pct=max_drawdown * 100,
        win_rate=win_rate * 100,
        profit_factor=profit_factor
    )
```

### Configuration Management

**File:** `.env` (never commit this file)

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Trading
INITIAL_CAPITAL=100000
COMMISSION_PCT=0.001
SLIPPAGE_PCT=0.0005

# Risk Management
MAX_POSITION_SIZE=0.10
MAX_DAILY_LOSS_PCT=0.05
MAX_DRAWDOWN_PCT=0.10
MAX_OPEN_POSITIONS=5

# Broker
BROKER_TYPE=paper  # paper, ibkr, mt5
```

**Loading:**

```python
from src.utils.config_loader import get_config

config = get_config()
api_key = config.openai_api_key
capital = config.initial_capital
```

### Testing Standards

#### Test Structure

```python
# tests/module/test_component.py

import pytest
from unittest.mock import Mock, patch
from src.module.component import Component

@pytest.fixture
def component():
    """Fixture for component instance"""
    return Component()

def test_functionality_description(component):
    """Test description in imperative form"""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = component.method(input_data)
    
    # Assert
    assert result == expected_output
    assert component.state == expected_state
```

#### Mocking External Dependencies

```python
# Mock yfinance
with patch("yfinance.Ticker") as mock_ticker:
    mock_ticker_instance = Mock()
    mock_ticker_instance.history.return_value = mock_data
    mock_ticker.return_value = mock_ticker_instance
    # Test code

# Mock OpenAI
with patch.dict("sys.modules", {"openai": mock_openai}):
    # Test code with mocked OpenAI

# Mock file I/O
with patch("builtins.open", mock_open(read_data="data")):
    # Test code with mocked file
```

#### Test Coverage Requirements

- **Priority modules:** ≥90% coverage (advisor, execution, core)
- **Supporting modules:** ≥70% coverage (utils, brokers)
- **All modules:** ≥60% global coverage
- **Current status:** 63.70% global, priority modules 95-100%

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific module
pytest tests/advisor/

# Run in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v
```

---

## ⚙️ Development Workflow

### Git Branch Strategy

```
main
  ├── feature/feature-name
  ├── fix/bug-name
  ├── test/test-coverage-module
  ├── docs/documentation-update
  └── refactor/code-improvement
```

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `test/` - Test additions
- `docs/` - Documentation
- `refactor/` - Code improvements
- `perf/` - Performance optimizations

**Current branch:** `claude/incomplete-description-011CV5cPzTfHiGfDccsfMQ8X`

### Commit Message Conventions

Follow **Conventional Commits:**

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `test` - Add/modify tests
- `docs` - Documentation
- `style` - Formatting (no code change)
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `chore` - Maintenance

**Examples:**

```bash
# Good commits
git commit -m "feat(advisor): add Fibonacci retracement indicators"
git commit -m "fix(execution): correct position size calculation"
git commit -m "test(backtest): add comprehensive engine tests"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(core): extract sentiment logic to separate class"

# Bad commits
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"
```

### Code Style

**Formatting:** Black + isort

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .
```

**Linting:** Ruff

```bash
# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

**Type Checking:** mypy

```bash
# Type check
mypy src/
```

**Style Guidelines:**

1. **Use type hints everywhere**
   ```python
   def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
       ...
   ```

2. **Use dataclasses for structured data**
   ```python
   @dataclass
   class TradingSignal:
       signal: str
       confidence: float
       reasons: List[str]
   ```

3. **Use descriptive variable names**
   ```python
   # Good
   oversold_threshold = 30
   moving_average_20 = data['Close'].rolling(20).mean()
   
   # Bad
   x = 30
   ma = data['Close'].rolling(20).mean()
   ```

4. **Write docstrings (Google style)**
   ```python
   def generate_signal(symbol: str, period: str = "6mo") -> TradingSignal:
       """Generate trading signal for a symbol.
       
       Args:
           symbol: Stock ticker symbol (e.g., 'AAPL')
           period: Data period (e.g., '1mo', '6mo', '1y')
           
       Returns:
           Trading signal with confidence and reasoning
           
       Raises:
           ValueError: If symbol is invalid
       """
       ...
   ```

5. **Keep functions small** (<50 lines)
6. **One responsibility per function**
7. **Avoid global state**
8. **Use early returns** to reduce nesting

### Adding New Features

**Checklist:**

- [ ] Read this context.md file
- [ ] Understand how feature fits in architecture
- [ ] Follow existing patterns
- [ ] Write tests first (TDD) or alongside
- [ ] Update documentation
- [ ] Run full test suite
- [ ] Format code (black, isort)
- [ ] Lint code (ruff)
- [ ] Type check (mypy)
- [ ] Update this context.md if architecture changes
- [ ] Commit with conventional commit message

**Example: Adding a New Indicator**

1. **Add to `src/advisor/indicators.py`:**

```python
def calculate_stochastic_oscillator(
    self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """Calculate Stochastic Oscillator.
    
    Args:
        data: OHLC data
        k_period: Period for %K
        d_period: Period for %D
        
    Returns:
        Tuple of (%K, %D) Series
    """
    low_min = data['Low'].rolling(k_period).min()
    high_max = data['High'].rolling(k_period).max()
    
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    
    return k, d
```

2. **Update `calculate_all()` method:**

```python
def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
    # ... existing indicators ...
    data['stoch_k'], data['stoch_d'] = self.calculate_stochastic_oscillator(data)
    return data
```

3. **Add tests in `tests/advisor/test_indicators.py`:**

```python
def test_calculate_stochastic_oscillator():
    indicators = TechnicalIndicators()
    data = create_test_ohlc_data()
    
    k, d = indicators.calculate_stochastic_oscillator(data)
    
    assert len(k) == len(data)
    assert len(d) == len(data)
    assert k.min() >= 0
    assert k.max() <= 100
    assert d.min() >= 0
    assert d.max() <= 100
```

4. **Update `docs/modules/advisor.md`:**

Add section describing the new indicator.

5. **Run tests and checks:**

```bash
pytest tests/advisor/test_indicators.py -v
black src/advisor/indicators.py tests/advisor/test_indicators.py
ruff check src/advisor/indicators.py
```

6. **Commit:**

```bash
git add src/advisor/indicators.py tests/advisor/test_indicators.py docs/modules/advisor.md
git commit -m "feat(advisor): add Stochastic Oscillator indicator"
```

---

## 🗺️ 12-Month Roadmap

### Current State (Month 0)

✅ **Completed:**
- Core trading logic
- Multiple broker adapters (Paper, IBKR, MT5)
- Risk management system
- Backtesting engine
- Sentiment analysis (lexicon + AI)
- Signal generation (RSI, MA, BB, MACD)
- Comprehensive test coverage (63.70%)
- Complete documentation (17 pages)

### Month 1-3: Stabilization & Enhancement

**Goals:**
- Increase test coverage to 75%
- Add more technical indicators (Fibonacci, Stochastic, Ichimoku)
- Improve AI prompt engineering for better summaries
- Add portfolio-level analysis (multiple symbols)
- Implement real-time data streaming (WebSocket)

**Tasks:**
- [ ] Add Fibonacci retracement/extension
- [ ] Add Stochastic Oscillator
- [ ] Add Ichimoku Cloud
- [ ] Improve OpenAI/Anthropic prompts
- [ ] Add portfolio optimization (Markowitz)
- [ ] Implement WebSocket data feeds
- [ ] Write additional tests for new features
- [ ] Performance optimization (caching, vectorization)

**Risks:**
- API rate limits (OpenAI, Anthropic)
- Data quality from yfinance
- Broker API stability

### Month 3-6: Advanced Features

**Goals:**
- Machine learning for signal generation
- Options trading support
- Advanced risk metrics (Greeks, VaR, CVaR)
- Multi-timeframe analysis
- Automated strategy optimization

**Tasks:**
- [ ] Train ML model (Random Forest, XGBoost) for signals
- [ ] Add options chain data fetching
- [ ] Implement Greeks calculation
- [ ] Add VaR/CVaR risk metrics
- [ ] Multi-timeframe signal alignment
- [ ] Walk-forward optimization
- [ ] Genetic algorithm for parameter tuning

**Risks:**
- ML model overfitting
- Options data availability
- Computational resources for optimization

### Month 6-9: Cloud & Scalability

**Goals:**
- Migrate to cloud (AWS/GCP)
- Microservices architecture
- Real-time monitoring dashboard
- Automated deployment (CI/CD)
- Database integration (PostgreSQL)

**Tasks:**
- [ ] Design microservices architecture
- [ ] Set up Kubernetes cluster
- [ ] Implement message queue (RabbitMQ/Kafka)
- [ ] Create web dashboard (React + FastAPI)
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Implement database layer
- [ ] Configure GitHub Actions for deployment

**Risks:**
- Cloud costs
- Complexity of distributed system
- Learning curve for team

### Month 9-12: Production Ready

**Goals:**
- Live trading with real capital (paper → live)
- Mobile app (iOS/Android)
- User authentication and multi-tenancy
- Compliance and regulatory features
- Comprehensive documentation for end users

**Tasks:**
- [ ] Implement user authentication (OAuth)
- [ ] Add multi-user support
- [ ] Create mobile app (React Native)
- [ ] Add compliance checks (PDT, margin)
- [ ] Implement audit logging
- [ ] Create user onboarding flow
- [ ] Write end-user documentation
- [ ] Conduct security audit

**Risks:**
- Regulatory compliance
- Security vulnerabilities
- User data privacy

### Long-Term Vision (Year 2+)

- **Community Edition:** Open-source community version
- **Enterprise Edition:** White-label for institutions
- **API Service:** Trading-as-a-service
- **Social Trading:** Copy trading, leaderboards
- **Educational Platform:** Courses, simulations

---

## 👨‍💻 Guide for Nathan

### How to Work with Claude Code AI

Nathan, this section is specifically for you to maximize productivity with Claude Code AI on the ZenMarket AI project.

### Setup Workflow

**First Time Setup:**

1. **Clone repo and install**
   ```bash
   git clone https://github.com/TechNatool/zenmarket-ai.git
   cd zenmarket-ai
   pip install -e ".[dev]"
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Open in Claude Code AI**
   - Open the zenmarket-ai directory in your IDE
   - Ensure Claude Code AI has access to the project

3. **Verify everything works**
   ```bash
   pytest  # All tests should pass
   ```

### Daily Workflow with Claude

#### Morning Routine

```
Nathan → Claude:
"Read context.md and give me a summary of the project state and what we should focus on today."

Claude will:
- Read context.md (this file)
- Summarize current project status
- Suggest priorities based on roadmap
- Identify any incomplete work from yesterday
```

#### Bug Fixing

```
Nathan → Claude:
"Read context.md. There's a bug where the RSI calculation returns NaN for the first 14 days. Fix it and write tests."

Claude will:
1. Read context.md
2. Locate src/advisor/indicators.py
3. Find calculate_rsi() method
4. Identify the issue (missing .fillna())
5. Fix the bug
6. Write/update tests
7. Run tests to verify
8. Commit with proper message
```

#### Adding Features

```
Nathan → Claude:
"Read context.md. I want to add support for Fibonacci retracement levels. Implement it following the project patterns."

Claude will:
1. Read context.md → "Adding New Features" section
2. Review TechnicalIndicators class structure
3. Implement calculate_fibonacci_levels()
4. Add to calculate_all()
5. Write comprehensive tests
6. Update documentation
7. Commit properly
```

#### Code Review

```
Nathan → Claude:
"Read context.md and review the code I just wrote in src/execution/order_manager.py. Check for:
- Consistency with project patterns
- Test coverage
- Type hints
- Docstrings
- Potential bugs"

Claude will:
- Read the code
- Compare against patterns in context.md
- Suggest improvements
- Point out missing tests
- Recommend best practices
```

#### Continuing Yesterday's Work

```
Nathan → Claude:
"Read context.md. Yesterday we were working on implementing portfolio optimization. Continue where we left off."

Claude will:
1. Read context.md
2. Check git log for recent commits
3. Look for TODO comments in code
4. Find incomplete functions
5. Continue implementation
6. Complete tests
7. Update docs
```

#### Optimizing Performance

```
Nathan → Claude:
"Read context.md. The backtest engine is slow. Profile it, find bottlenecks, and optimize following the project guidelines."

Claude will:
1. Read performance guidelines in context.md
2. Profile the code
3. Identify bottlenecks (e.g., loops that should be vectorized)
4. Apply optimizations (pandas/numpy vectorization)
5. Benchmark improvement
6. Ensure tests still pass
7. Document changes
```

### Common Commands

#### Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/advisor/test_indicators.py -v

# Format code
black .
isort .

# Lint code
ruff check .

# Type check
mypy src/

# Run all checks
black . && isort . && ruff check . && mypy src/ && pytest
```

#### Git

```bash
# Create feature branch
git checkout -b feature/new-indicator

# Stage changes
git add src/advisor/indicators.py tests/advisor/test_indicators.py

# Commit (following conventions)
git commit -m "feat(advisor): add Fibonacci retracement indicator"

# Push to remote
git push origin feature/new-indicator
```

#### Documentation

```bash
# Preview documentation
mkdocs serve

# Build documentation
mkdocs build

# Deploy documentation (DO NOT DO THIS - private repo)
# mkdocs gh-deploy
```

### When Claude Gets Stuck

If Claude seems confused or makes mistakes:

```
Nathan → Claude:
"Stop. Re-read context.md from the beginning, specifically the [SECTION NAME] section. Then try again."
```

Or:

```
Nathan → Claude:
"Read context.md. You're implementing [FEATURE] incorrectly. The correct pattern is documented in the [SECTION]. Follow that pattern exactly."
```

### Asking for Explanations

```
Nathan → Claude:
"Read context.md. Explain how the risk management system works, step by step."

Nathan → Claude:
"Read context.md. I don't understand the signal generation algorithm. Explain it with examples."

Nathan → Claude:
"Read context.md. What's the difference between backtest_broker and broker_simulator?"
```

### Context Maintenance

**Important:** Keep context.md up to date!

```
Nathan → Claude:
"We just added a major feature [FEATURE NAME]. Update context.md to reflect this change in the architecture and add examples to the guide."

Claude will:
- Update the Architecture section
- Add the feature to module documentation
- Update examples in the guide
- Commit the updated context.md
```

### Debugging Workflow

```
Nathan → Claude:
"Read context.md. The backtest is failing with error: [ERROR MESSAGE]. Debug and fix."

Claude will:
1. Read context.md
2. Understand the backtest flow
3. Locate relevant code
4. Read the error
5. Identify root cause
6. Fix the bug
7. Add test to prevent regression
8. Commit fix
```

### Testing Strategy

```
Nathan → Claude:
"Read context.md. Write comprehensive tests for [MODULE/CLASS]. Follow the testing standards documented."

Claude will:
- Read testing standards section
- Review existing test patterns
- Write unit tests covering all methods
- Add edge cases and error conditions
- Ensure hermetic tests (no external deps)
- Run tests and verify coverage
- Commit tests
```

### Best Practices for Working with Claude

1. **Always start with "Read context.md"** - This ensures Claude has full context

2. **Be specific** - Instead of "fix the bug", say "fix the RSI calculation bug in indicators.py"

3. **Reference sections** - "Read context.md, specifically the Signal Generation section"

4. **Break down complex tasks** - Instead of "build portfolio optimizer", break into smaller tasks

5. **Verify Claude's understanding** - Ask Claude to explain back what you asked

6. **Keep context.md updated** - After major changes, update this file

7. **Use examples** - Show Claude examples of what you want

8. **Trust but verify** - Always review Claude's code, especially for critical logic

### Emergency Procedures

#### If Tests Break

```
Nathan → Claude:
"Read context.md. All tests are failing after my last change. Investigate and fix."

Claude will:
- Read recent commits
- Identify the breaking change
- Fix the issue or revert
- Ensure all tests pass
```

#### If Dependencies Break

```bash
# Reinstall dependencies
pip uninstall zenmarket-ai
pip install -e ".[dev]"

# If still broken, create fresh virtualenv
python -m venv venv-new
source venv-new/bin/activate
pip install -e ".[dev]"
```

#### If Git Issues

```bash
# If confused about branches
git status
git log --oneline --graph --all

# If need to reset
git reset --hard origin/main  # CAREFUL!
```

### Asking for Reports

```
Nathan → Claude:
"Read context.md. Generate a report on:
- Current test coverage by module
- Missing tests
- Technical debt
- Performance bottlenecks
- Security concerns"

Claude will analyze and provide detailed report.
```

---

## 📝 Current Work Status

**Last Updated:** 2025-01-13

**Recent Completed Work:**
- ✅ Phase 5: Test coverage for 5 priority modules (95-100%)
- ✅ Comprehensive documentation (17 files, 5,857 lines)
- ✅ Fixed all legacy tests (378 passing)
- ✅ Black/isort formatting applied
- ✅ CI/CD pipeline verified

**Current Branch:** `claude/incomplete-description-011CV5cPzTfHiGfDccsfMQ8X`

**Next Priorities:**
1. Complete repository audit (Phase 2 of current work)
2. Finalize internal documentation
3. Prepare maintenance tooling
4. Create release checklist

**Known Issues:**
- None critical
- Test coverage could be higher (target 75%)
- Some broker adapters have lower coverage (requires live connection to test)

**Open Tasks:**
- [ ] Increase test coverage to 75%
- [ ] Add more technical indicators
- [ ] Improve AI prompts
- [ ] Performance profiling and optimization

---

## 🔐 Security & Compliance

### Security Guidelines

1. **Never commit secrets**
   - Use `.env` file (in `.gitignore`)
   - Never hardcode API keys
   - Rotate keys regularly

2. **Input validation**
   - Validate all user inputs
   - Sanitize data from external APIs
   - Use Pydantic for data validation

3. **Paper trading by default**
   - Always start with paper trading
   - Require explicit confirmation for live trading
   - Implement kill switches

4. **Audit logging**
   - Log all trades
   - Track P&L changes
   - Monitor for suspicious activity

5. **Code security**
   - Run `bandit` security scanner
   - Keep dependencies updated
   - Review security advisories

### Compliance

**Regulatory Considerations:**

- **Pattern Day Trader (PDT)** - Enforce 3-day-trade limit for accounts <$25k
- **Wash Sale** - Detect and flag wash sales
- **Short Sale Restrictions** - Comply with uptick rule
- **Margin Requirements** - Enforce Reg T requirements

**Implemented in:** `src/execution/compliance.py`

---

## 📞 Support & Resources

### Documentation

- **Main Docs:** `docs/` directory
- **API Reference:** `docs/modules/`
- **User Guide:** `docs/user-guide/`
- **Trading Logic:** `docs/trading-logic/`

### External Resources

- **yfinance:** https://github.com/ranaroussi/yfinance
- **IBKR API:** https://interactivebrokers.github.io/tws-api/
- **MT5 API:** https://www.mql5.com/en/docs/python_metatrader5
- **OpenAI:** https://platform.openai.com/docs
- **Anthropic:** https://docs.anthropic.com/

### Getting Help

1. **Read this file** (`context.md`)
2. **Check documentation** (`docs/`)
3. **Search code** for similar examples
4. **Ask Claude Code AI** to explain
5. **Review tests** for usage examples

---

## 🎓 Learning Resources

### For New Developers

**Must Read:**
1. This file (context.md) - Complete project context
2. `docs/architecture.md` - System architecture
3. `docs/modules/advisor.md` - Signal generation
4. `docs/trading-logic/risk_management.md` - Risk controls

**Code to Study:**
1. `src/advisor/signal_generator.py` - Core signal logic
2. `src/execution/risk_manager.py` - Risk management
3. `src/backtest/backtest_engine.py` - Backtest flow
4. `tests/advisor/test_advisors.py` - Test patterns

### For Traders

**Must Read:**
1. `docs/user-guide/cli.md` - CLI commands
2. `docs/user-guide/configuration.md` - Configuration
3. `docs/trading-logic/signal_logic.md` - Signal generation
4. `docs/trading-logic/risk_management.md` - Risk controls
5. `docs/trading-logic/performance_metrics.md` - Metrics

---

## 🏁 Quick Start Checklist

**For Claude Code AI:**

- [ ] Read this entire context.md file
- [ ] Understand the architecture
- [ ] Review established patterns
- [ ] Check testing standards
- [ ] Follow commit conventions

**For New Features:**

- [ ] Read relevant sections of context.md
- [ ] Review existing similar features
- [ ] Write tests first or alongside
- [ ] Follow code style guidelines
- [ ] Update documentation
- [ ] Run full test suite
- [ ] Commit with conventional message

**For Bug Fixes:**

- [ ] Read context.md to understand affected module
- [ ] Reproduce the bug
- [ ] Write failing test
- [ ] Fix the bug
- [ ] Verify test passes
- [ ] Run full test suite
- [ ] Commit fix

---

## 📌 Key Reminders

1. **Always read context.md before coding** - It has all the answers
2. **Follow established patterns** - Don't reinvent the wheel
3. **Write tests** - Untested code is broken code
4. **Type hints everywhere** - Static typing catches bugs
5. **Keep functions small** - Single responsibility principle
6. **Document your work** - Future you will thank you
7. **Security first** - Never commit secrets, paper trade first
8. **Commit conventions** - Use conventional commits
9. **Update context.md** - Keep this file current
10. **Ask before pushing** - Always confirm with Nathan

---

## 📄 Appendix

### File Locations Quick Reference

```
Key Files:
- context.md                     ← YOU ARE HERE
- README.md                      ← Project README
- .env                           ← Configuration (DO NOT COMMIT)
- pytest.ini                     ← Test configuration
- pyproject.toml                 ← Project metadata
- mkdocs.yml                     ← Documentation config

Code:
- src/cli.py                     ← CLI entry point
- src/main.py                    ← Main entry point
- src/advisor/signal_generator.py ← Signal generation
- src/execution/risk_manager.py   ← Risk management
- src/backtest/backtest_engine.py ← Backtesting

Tests:
- tests/advisor/                 ← Advisor tests
- tests/execution/               ← Execution tests
- tests/backtest/                ← Backtest tests

Docs:
- docs/index.md                  ← Documentation homepage
- docs/architecture.md           ← System architecture
- docs/modules/                  ← Module documentation
- docs/user-guide/               ← User guides
- docs/trading-logic/            ← Trading logic docs
```

### Environment Variables Reference

```bash
# Core
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Trading
INITIAL_CAPITAL=100000
COMMISSION_PCT=0.001
SLIPPAGE_PCT=0.0005

# Risk
MAX_POSITION_SIZE=0.10
MAX_DAILY_LOSS_PCT=0.05
MAX_DRAWDOWN_PCT=0.10
MAX_OPEN_POSITIONS=5

# Broker
BROKER_TYPE=paper
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
MT5_LOGIN=...
MT5_PASSWORD=...
MT5_SERVER=...

# Data
DATA_DIRECTORY=data
REPORT_OUTPUT_DIR=reports
LOG_DIRECTORY=logs

# Logging
LOG_LEVEL=INFO
```

### Command Cheat Sheet

```bash
# Development
pytest                              # Run tests
pytest --cov=src                    # Run with coverage
black .                             # Format code
isort .                             # Sort imports
ruff check .                        # Lint code
mypy src/                           # Type check

# CLI
python -m src.cli brief --symbols AAPL
python -m src.cli advisor --symbol AAPL
python -m src.cli simulate --symbol AAPL
python -m src.cli backtest --symbol AAPL --start 2024-01-01

# Git
git status                          # Check status
git log --oneline --graph           # View history
git checkout -b feature/name        # Create branch
git commit -m "feat: description"   # Commit

# Documentation
mkdocs serve                        # Preview docs
mkdocs build                        # Build docs
```

---

## ✅ Verification Checklist

**This context.md file is complete and ready to use when:**

- [x] Project overview is comprehensive
- [x] Claude instructions are clear and actionable
- [x] Architecture is fully documented
- [x] All modules are described
- [x] APIs are documented
- [x] Algorithms are explained with code
- [x] Development workflow is defined
- [x] Testing standards are clear
- [x] Code style is documented
- [x] 12-month roadmap is planned
- [x] Guide for Nathan is complete
- [x] Examples are provided
- [x] Quick references are included
- [x] Security guidelines are present

---

**Last Updated:** 2025-01-13  
**Version:** 1.0.0  
**Maintained By:** TechNatool + Claude Code AI  

**This file is the heart of the ZenMarket AI project. Keep it updated, keep it accurate, keep it useful.**

---

END OF CONTEXT.MD
