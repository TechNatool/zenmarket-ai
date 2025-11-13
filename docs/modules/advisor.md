# Advisor Module

The Advisor module provides technical analysis, signal generation, and market insights for trading decisions.

---

## Overview

The Advisor module is responsible for:

- Calculating technical indicators (MA, RSI, Bollinger Bands, MACD, ATR)
- Generating trading signals (BUY/SELL/HOLD) with confidence scores
- Creating visual charts with indicator overlays
- Generating comprehensive trading advisor reports

---

## Components

### 1. Technical Indicators (`indicators.py`)

Calculates standard technical indicators used in trading analysis.

#### Key Indicators

- **Moving Averages**: MA20, MA50
- **RSI**: Relative Strength Index (14-period)
- **Bollinger Bands**: 20-period with 2 standard deviations
- **MACD**: Moving Average Convergence Divergence
- **ATR**: Average True Range (14-period)

#### Usage Example

```python
from src.advisor.indicators import TechnicalIndicators

indicators = TechnicalIndicators()
data = indicators.calculate_all(market_data)

# Access indicators
rsi = data['rsi'].iloc[-1]
ma20 = data['ma20'].iloc[-1]
bb_upper = data['bb_upper'].iloc[-1]
```

---

### 2. Signal Generator (`signal_generator.py`)

Generates trading signals based on technical indicators and market conditions.

#### Signal Types

- **BUY**: Bullish conditions detected
- **SELL**: Bearish conditions detected
- **HOLD**: Neutral or unclear conditions

#### Signal Logic

```
BUY Conditions:
- RSI < 30 (oversold)
- Price < BB_lower (undervalued)
- MA20 > MA50 (bullish trend)
- MACD > Signal line (momentum)

SELL Conditions:
- RSI > 70 (overbought)
- Price > BB_upper (overvalued)
- MA20 < MA50 (bearish trend)
- MACD < Signal line (negative momentum)

HOLD Conditions:
- None of the above conditions met
- Mixed signals
- Low confidence
```

#### Signal Confidence

Confidence scores (0-100%) are calculated based on:
- Number of confirming indicators
- Strength of each indicator signal
- Consistency across timeframes

#### Usage Example

```python
from src.advisor.signal_generator import SignalGenerator

generator = SignalGenerator()
signal = generator.generate_signal(symbol="AAPL", period="6mo")

print(f"Signal: {signal.signal}")  # BUY/SELL/HOLD
print(f"Confidence: {signal.confidence}%")
print(f"Reason: {signal.reason}")
```

---

### 3. Plotter (`plotter.py`)

Creates professional charts with technical indicators.

#### Chart Features

- OHLC candlestick charts
- Moving average overlays
- RSI subplot
- MACD subplot
- Bollinger Bands
- Volume bars
- Buy/Sell signal markers

#### Usage Example

```python
from src.advisor.plotter import Plotter

plotter = Plotter()
plotter.plot_technical_analysis(
    data=market_data,
    indicators=indicators,
    signals=signals,
    output_path="chart.png"
)
```

---

### 4. Advisor Report (`advisor_report.py`)

Generates comprehensive trading advisor reports.

#### Report Sections

1. **Market Summary**: Current price, change, volume
2. **Technical Indicators**: All indicator values
3. **Trading Signal**: Recommendation with confidence
4. **Risk Assessment**: Volatility, trend strength
5. **Key Levels**: Support/Resistance levels

#### Usage Example

```python
from src.advisor.advisor_report import generate_advisor_report

report = generate_advisor_report(
    symbol="AAPL",
    period="6mo",
    output_format="markdown"
)
```

---

## API Reference

### TechnicalIndicators

```python
class TechnicalIndicators:
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        
    def calculate_macd(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line."""
        
    def calculate_bollinger_bands(
        self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands."""
```

### SignalGenerator

```python
class SignalGenerator:
    def generate_signal(
        self, symbol: str, period: str = "6mo"
    ) -> TradingSignal:
        """Generate trading signal for a symbol."""
        
    def get_market_bias(self, signals: List[TradingSignal]) -> str:
        """Get overall market bias from multiple signals."""
```

---

## Configuration

Configure advisor settings in `.env`:

```bash
# RSI thresholds
ADVISOR_RSI_OVERSOLD=30
ADVISOR_RSI_OVERBOUGHT=70

# Confidence thresholds
ADVISOR_MIN_CONFIDENCE=50

# Moving average periods
ADVISOR_MA_SHORT=20
ADVISOR_MA_LONG=50
```

---

## Best Practices

### 1. Multiple Timeframes

Always analyze multiple timeframes:
- Short-term: 1-3 months
- Medium-term: 6 months
- Long-term: 1-2 years

### 2. Confirmation

Wait for confirmation before acting:
- Multiple indicators agreeing
- Confidence above threshold
- Volume confirmation

### 3. Context Matters

Consider market context:
- Overall market trend
- News and events
- Sector performance

---

## Examples

### Example 1: Basic Signal Generation

```python
from src.advisor.signal_generator import SignalGenerator

generator = SignalGenerator()
signal = generator.generate_signal("AAPL")

if signal.signal == "BUY" and signal.confidence > 70:
    print(f"Strong BUY signal: {signal.reason}")
```

### Example 2: Batch Analysis

```python
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
generator = SignalGenerator()

signals = [generator.generate_signal(s) for s in symbols]
bias = generator.get_market_bias(signals)

print(f"Market Bias: {bias}")
```

---

## Testing

The advisor module has comprehensive test coverage:

- `tests/advisor/test_advisors.py` - 15 tests
- `tests/test_signal_generator.py` - 13 tests
- `tests/test_signal_generator_complete.py` - 25 tests

Coverage: 95.32% for signal_generator.py
