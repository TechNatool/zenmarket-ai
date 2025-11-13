# Signal Generation Logic

Understanding how ZenMarket AI generates trading signals.

---

## Signal Types

ZenMarket AI generates three types of signals:

- **BUY**: Bullish conditions detected, consider entering long position
- **SELL**: Bearish conditions detected, consider exiting or shorting
- **HOLD**: Neutral conditions, maintain current positions

Each signal includes:
- Confidence score (0-100%)
- Reasoning/explanation
- Supporting technical indicators

---

## Signal Generation Process

```
Market Data
    ↓
Technical Indicators
    ↓
Individual Signals
    ↓
Signal Aggregation
    ↓
Confidence Scoring
    ↓
Final Signal + Recommendation
```

---

## Technical Indicators Used

### 1. RSI (Relative Strength Index)

**Period:** 14
**Range:** 0-100

```python
RSI < 30  → Oversold (Bullish)
RSI > 70  → Overbought (Bearish)
30-70     → Neutral
```

**Signal Logic:**
```python
if rsi < 30:
    signal = "BUY"
    reason = "RSI oversold"
elif rsi > 70:
    signal = "SELL"
    reason = "RSI overbought"
```

### 2. Moving Averages

**Periods:** MA20, MA50

**Golden Cross (Bullish):**
```python
if ma20 > ma50 and previous_ma20 <= previous_ma50:
    signal = "BUY"
    reason = "Golden cross (MA20 > MA50)"
```

**Death Cross (Bearish):**
```python
if ma20 < ma50 and previous_ma20 >= previous_ma50:
    signal = "SELL"
    reason = "Death cross (MA20 < MA50)"
```

**Price vs MA:**
```python
if price < ma20 < ma50:
    signal = "BUY"
    reason = "Price below both MAs, oversold"
    
if price > ma20 > ma50:
    signal = "SELL"
    reason = "Price above both MAs, overbought"
```

### 3. Bollinger Bands

**Parameters:** 20-period, 2 std dev

```python
bb_lower = ma20 - (2 * std_dev)
bb_upper = ma20 + (2 * std_dev)

if price < bb_lower:
    signal = "BUY"
    reason = "Price below lower BB, undervalued"
    
if price > bb_upper:
    signal = "SELL"
    reason = "Price above upper BB, overvalued"
```

### 4. MACD

**Parameters:** 12, 26, 9

```python
macd = ema12 - ema26
signal_line = ema9(macd)

if macd > signal_line and previous_macd <= previous_signal:
    signal = "BUY"
    reason = "MACD bullish crossover"
    
if macd < signal_line and previous_macd >= previous_signal:
    signal = "SELL"
    reason = "MACD bearish crossover"
```

---

## Signal Aggregation

Multiple indicators are combined to generate final signal:

```python
def generate_signal(indicators):
    buy_signals = 0
    sell_signals = 0
    reasons = []
    
    # RSI
    if indicators['rsi'] < 30:
        buy_signals += 1
        reasons.append("RSI oversold")
    elif indicators['rsi'] > 70:
        sell_signals += 1
        reasons.append("RSI overbought")
    
    # Moving Averages
    if indicators['ma20'] > indicators['ma50']:
        buy_signals += 1
        reasons.append("MA20 > MA50")
    else:
        sell_signals += 1
        reasons.append("MA20 < MA50")
    
    # Bollinger Bands
    if indicators['price'] < indicators['bb_lower']:
        buy_signals += 1
        reasons.append("Price < BB lower")
    elif indicators['price'] > indicators['bb_upper']:
        sell_signals += 1
        reasons.append("Price > BB upper")
    
    # MACD
    if indicators['macd'] > indicators['macd_signal']:
        buy_signals += 1
        reasons.append("MACD positive")
    else:
        sell_signals += 1
        reasons.append("MACD negative")
    
    # Determine final signal
    if buy_signals > sell_signals:
        return TradingSignal(
            signal="BUY",
            confidence=calculate_confidence(buy_signals, sell_signals),
            reasons=reasons
        )
    elif sell_signals > buy_signals:
        return TradingSignal(
            signal="SELL",
            confidence=calculate_confidence(sell_signals, buy_signals),
            reasons=reasons
        )
    else:
        return TradingSignal(
            signal="HOLD",
            confidence=50,
            reasons=["Mixed signals"]
        )
```

---

## Confidence Scoring

Confidence is calculated based on:

1. **Number of confirming indicators**
2. **Strength of each indicator**
3. **Consistency across timeframes**

```python
def calculate_confidence(confirming, contradicting):
    total = confirming + contradicting
    if total == 0:
        return 50  # Neutral
    
    # Base confidence from ratio
    ratio = confirming / total
    base_confidence = ratio * 100
    
    # Boost for strong confirmation
    if confirming >= 3 and contradicting == 0:
        base_confidence = min(base_confidence + 10, 100)
    
    # Penalty for mixed signals
    if contradicting > 0:
        base_confidence -= (contradicting * 5)
    
    return max(0, min(100, base_confidence))
```

**Example:**
```python
# 4 BUY signals, 0 SELL signals
confidence = calculate_confidence(4, 0)
# = (4/4) * 100 + 10 = 110 → capped at 100%

# 3 BUY signals, 1 SELL signal
confidence = calculate_confidence(3, 1)
# = (3/4) * 100 - 5 = 70%

# 2 BUY signals, 2 SELL signals
confidence = calculate_confidence(2, 2)
# = (2/4) * 100 - 10 = 40%
```

---

## Signal Interpretation

### High Confidence (> 70%)

```python
if signal.confidence > 70:
    if signal.signal == "BUY":
        action = "Strong buy - consider full position"
    elif signal.signal == "SELL":
        action = "Strong sell - exit positions"
```

### Medium Confidence (50-70%)

```python
if 50 < signal.confidence <= 70:
    if signal.signal == "BUY":
        action = "Moderate buy - start with half position"
    elif signal.signal == "SELL":
        action = "Consider reducing exposure"
```

### Low Confidence (< 50%)

```python
if signal.confidence <= 50:
    action = "Wait for clearer signals"
```

---

## Market Bias

Aggregate signals across multiple symbols to determine overall market sentiment:

```python
def get_market_bias(signals):
    buy_count = sum(1 for s in signals if s.signal == "BUY")
    sell_count = sum(1 for s in signals if s.signal == "SELL")
    
    buy_pct = buy_count / len(signals)
    
    if buy_pct >= 0.6:
        return "BULLISH"
    elif buy_pct <= 0.4:
        return "BEARISH"
    else:
        return "NEUTRAL"
```

---

## Timeframe Analysis

Analyze multiple timeframes for confirmation:

```python
# Short-term (1 month)
signal_1m = generate_signal("AAPL", period="1mo")

# Medium-term (6 months)
signal_6m = generate_signal("AAPL", period="6mo")

# Long-term (1 year)
signal_1y = generate_signal("AAPL", period="1y")

# Confirm alignment
if (signal_1m.signal == signal_6m.signal == signal_1y.signal == "BUY"):
    print("Strong BUY across all timeframes")
```

---

## Advanced Signal Logic

### Divergence Detection

```python
def detect_divergence(price_data, rsi_data):
    # Bullish divergence: price making lower lows, RSI making higher lows
    if (price_data[-1] < price_data[-10] and
        rsi_data[-1] > rsi_data[-10]):
        return "bullish_divergence"
    
    # Bearish divergence: price making higher highs, RSI making lower highs
    if (price_data[-1] > price_data[-10] and
        rsi_data[-1] < rsi_data[-10]):
        return "bearish_divergence"
    
    return None
```

### Trend Strength

```python
def calculate_trend_strength(ma20, ma50, ma200):
    # Strong uptrend: MA20 > MA50 > MA200
    if ma20 > ma50 > ma200:
        return "strong_uptrend"
    
    # Strong downtrend: MA20 < MA50 < MA200
    if ma20 < ma50 < ma200:
        return "strong_downtrend"
    
    # Weak/choppy trend
    return "weak_trend"
```

### Volume Confirmation

```python
def check_volume_confirmation(price_change, volume, avg_volume):
    # Price up with high volume = bullish confirmation
    if price_change > 0 and volume > avg_volume * 1.5:
        return "bullish_volume"
    
    # Price down with high volume = bearish confirmation
    if price_change < 0 and volume > avg_volume * 1.5:
        return "bearish_volume"
    
    # Low volume = weak signal
    return "low_volume"
```

---

## Signal Filters

### Volatility Filter

```python
def volatility_filter(atr, avg_atr):
    # Skip trading if volatility too high
    if atr > avg_atr * 2:
        return "volatility_too_high"
    
    # Skip if volatility too low (choppy market)
    if atr < avg_atr * 0.5:
        return "volatility_too_low"
    
    return "volatility_ok"
```

### Trend Filter

```python
def trend_filter(ma20, ma50):
    # Only trade in direction of trend
    if strategy == "trend_following":
        if ma20 > ma50:
            return "uptrend_only"
        else:
            return "downtrend_only"
    
    # Counter-trend strategy
    if strategy == "mean_reversion":
        return "any_trend"
```

---

## Example: Complete Signal Generation

```python
from src.advisor.signal_generator import SignalGenerator
from src.advisor.indicators import TechnicalIndicators

# Initialize
generator = SignalGenerator()
indicators = TechnicalIndicators()

# Get data and calculate indicators
data = indicators.get_market_data("AAPL", period="6mo")
ind = indicators.calculate_all(data)

# Generate signal
signal = generator.generate_signal("AAPL", period="6mo")

print(f"Signal: {signal.signal}")
print(f"Confidence: {signal.confidence}%")
print(f"Reasons: {', '.join(signal.reasons)}")

# Interpretation
if signal.signal == "BUY" and signal.confidence > 70:
    print("\n✅ Action: Strong BUY signal")
    print("Consider: Full position, tight stop-loss")
elif signal.signal == "BUY" and signal.confidence > 50:
    print("\n⚠️  Action: Moderate BUY signal")
    print("Consider: Half position, wider stop-loss")
else:
    print("\n❌ Action: WAIT for clearer signals")
```

---

## Backtesting Signals

Always backtest signal logic before trading:

```python
from src.backtest.backtest_engine import BacktestEngine

# Test signal generator on historical data
results = backtest_signals(
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    signal_generator=generator
)

print(f"Win rate: {results.win_rate:.1f}%")
print(f"Profit factor: {results.profit_factor:.2f}")
print(f"Sharpe ratio: {results.sharpe_ratio:.2f}")
```

---

## Best Practices

1. **Wait for confirmation** - Multiple indicators agreeing
2. **Check multiple timeframes** - Alignment increases probability
3. **Consider market context** - News, events, overall trend
4. **Use stop-losses always** - Protect against wrong signals
5. **Track signal performance** - Keep statistics on win rate
6. **Don't overtrade** - Quality over quantity
7. **Be patient** - Wait for high-confidence signals

---

## Related Documentation

- [Risk Management](risk_management.md)
- [Performance Metrics](performance_metrics.md)
- [Advisor Module](../modules/advisor.md)
