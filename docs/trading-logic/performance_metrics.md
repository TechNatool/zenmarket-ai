# Performance Metrics

Understanding how to measure and evaluate trading performance.

---

## Metric Categories

```
Performance Metrics
├── Returns
│   ├── Total Return
│   ├── CAGR
│   └── Period Returns
├── Risk-Adjusted
│   ├── Sharpe Ratio
│   ├── Sortino Ratio
│   └── Calmar Ratio
├── Risk
│   ├── Maximum Drawdown
│   ├── Volatility
│   ├── VaR
│   └── CVaR
└── Trading Stats
    ├── Win Rate
    ├── Profit Factor
    ├── Expectancy
    └── Trade Distribution
```

---

## Return Metrics

### Total Return

Simple percentage gain/loss:

```python
total_return = (final_equity - initial_equity) / initial_equity

# Example
initial = 100000
final = 115000
total_return = (115000 - 100000) / 100000 = 0.15 = 15%
```

### CAGR (Compound Annual Growth Rate)

Annualized return rate:

```python
years = days / 365.25
cagr = ((final_equity / initial_equity) ** (1 / years)) - 1

# Example: $100k → $115k in 6 months
years = 183 / 365.25 = 0.5
cagr = ((115000 / 100000) ** (1 / 0.5)) - 1
     = (1.15 ** 2) - 1
     = 0.3225 = 32.25% annualized
```

### Period Returns

```python
# Monthly returns
monthly_returns = equity.resample('M').last().pct_change()

# Daily returns
daily_returns = equity.pct_change()

# Rolling returns
rolling_30d = equity.pct_change(periods=30)
```

---

## Risk-Adjusted Metrics

### Sharpe Ratio

Measures risk-adjusted returns (higher is better):

```python
sharpe_ratio = (avg_return - risk_free_rate) / std_dev_return

# Example
avg_annual_return = 0.15  # 15%
risk_free_rate = 0.03  # 3% (T-bills)
annual_volatility = 0.12  # 12%

sharpe = (0.15 - 0.03) / 0.12 = 1.0

Interpretation:
< 1.0  : Not good
1.0-2.0: Good
2.0-3.0: Very good
> 3.0  : Excellent
```

### Sortino Ratio

Like Sharpe but only penalizes downside volatility:

```python
sortino_ratio = (avg_return - risk_free_rate) / downside_deviation

# Only count negative returns for std dev
downside_returns = returns[returns < 0]
downside_dev = downside_returns.std()

sortino = (avg_return - risk_free_rate) / downside_dev
```

**Better than Sharpe because:**
- Upside volatility is good (not penalized)
- Only downside risk matters

### Calmar Ratio

Return relative to maximum drawdown:

```python
calmar_ratio = cagr / abs(max_drawdown)

# Example
cagr = 0.20  # 20%
max_dd = 0.10  # 10%

calmar = 0.20 / 0.10 = 2.0

Interpretation:
> 1.0: Good (return exceeds max risk)
> 3.0: Excellent
```

---

## Risk Metrics

### Maximum Drawdown

Largest peak-to-trough decline:

```python
# Calculate running maximum
running_max = equity.cummax()

# Calculate drawdown at each point
drawdown = (equity - running_max) / running_max

# Maximum drawdown
max_drawdown = drawdown.min()

# Example
peak = 110000
trough = 95000
max_dd = (95000 - 110000) / 110000 = -0.1364 = -13.64%
```

### Volatility

Standard deviation of returns (annualized):

```python
# Daily volatility
daily_vol = daily_returns.std()

# Annualized volatility
annual_vol = daily_vol * sqrt(252)  # 252 trading days

# Example
daily_vol = 0.015  # 1.5%
annual_vol = 0.015 * sqrt(252) = 0.238 = 23.8%
```

### Value at Risk (VaR)

Maximum expected loss at confidence level:

```python
# 95% VaR - expect to lose no more than this 95% of the time
var_95 = np.percentile(returns, 5)

# Example
# If VaR(95%) = -2.5%, you can expect:
# - 95% of days: loss < 2.5%
# - 5% of days: loss > 2.5%
```

### Conditional VaR (CVaR)

Average loss when VaR is exceeded:

```python
# Average loss in worst 5% of cases
cvar_95 = returns[returns <= var_95].mean()

# Example
# VaR(95%) = -2.5%
# CVaR(95%) = -3.8% (average loss when exceeding VaR)
```

---

## Trading Statistics

### Win Rate

Percentage of profitable trades:

```python
win_rate = num_winning_trades / total_trades

# Example
wins = 65
total = 100
win_rate = 65 / 100 = 0.65 = 65%

Targets:
Day trading: 55-60%
Swing trading: 50-55%
Position trading: 40-50%
```

### Profit Factor

Ratio of gross profit to gross loss:

```python
profit_factor = gross_profit / gross_loss

# Example
gross_profit = 50000  # Sum of all wins
gross_loss = 25000    # Sum of all losses
profit_factor = 50000 / 25000 = 2.0

Interpretation:
< 1.0: Losing strategy
1.0-1.5: Marginal
1.5-2.0: Good
> 2.0: Excellent
```

### Expectancy

Average profit/loss per trade:

```python
expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)

# Example
win_rate = 0.60
avg_win = 500
loss_rate = 0.40
avg_loss = 300

expectancy = (0.60 * 500) - (0.40 * 300)
           = 300 - 120
           = $180 per trade

Must be positive for profitable strategy
```

### Average Win / Average Loss

```python
avg_win_loss = average_winning_trade / average_losing_trade

# Example
avg_win = 500
avg_loss = 300
ratio = 500 / 300 = 1.67

Target: > 1.5 (wins 50% larger than losses)
```

---

## Advanced Metrics

### Ulcer Index

Measures depth and duration of drawdowns:

```python
# More weight on deep, prolonged drawdowns
ulcer_index = sqrt(mean(drawdown ** 2))
```

### Omega Ratio

Probability-weighted ratio of gains vs losses:

```python
threshold = 0.0  # Usually 0% or risk-free rate
omega = sum(returns - threshold for r in returns if r > threshold) / \
        sum(threshold - returns for r in returns if r < threshold)
```

### Recovery Factor

```python
recovery_factor = total_return / abs(max_drawdown)

# How quickly strategy recovers from drawdowns
```

---

## Benchmark Comparison

Always compare to relevant benchmark:

```python
# Your strategy
strategy_return = 0.15  # 15%

# S&P 500
sp500_return = 0.12  # 12%

# Outperformance (alpha)
alpha = strategy_return - sp500_return = 0.03 = 3%

# Risk-adjusted comparison
strategy_sharpe = 1.8
sp500_sharpe = 1.2

# Better risk-adjusted return
```

---

## Example: Complete Performance Report

```python
from src.backtest.metrics import calculate_metrics

# Run backtest
results = backtest(symbol="AAPL", start="2023-01-01", end="2023-12-31")

# Calculate metrics
metrics = calculate_metrics(
    trades=results.trades,
    equity_curve=results.equity,
    initial_capital=100000
)

# Print report
print("="*50)
print("PERFORMANCE REPORT")
print("="*50)

print("\n📈 RETURNS")
print(f"Total Return:     {metrics.total_return_pct:.2f}%")
print(f"CAGR:             {metrics.cagr:.2f}%")
print(f"Best Month:       {metrics.best_month:.2f}%")
print(f"Worst Month:      {metrics.worst_month:.2f}%")

print("\n⚖️  RISK-ADJUSTED")
print(f"Sharpe Ratio:     {metrics.sharpe_ratio:.2f}")
print(f"Sortino Ratio:    {metrics.sortino_ratio:.2f}")
print(f"Calmar Ratio:     {metrics.calmar_ratio:.2f}")

print("\n⚠️  RISK")
print(f"Max Drawdown:     {metrics.max_drawdown_pct:.2f}%")
print(f"Volatility:       {metrics.volatility_pct:.2f}%")
print(f"VaR (95%):        {metrics.var_95:.2f}%")
print(f"CVaR (95%):       {metrics.cvar_95:.2f}%")

print("\n📊 TRADING STATS")
print(f"Total Trades:     {metrics.num_trades}")
print(f"Win Rate:         {metrics.win_rate:.2f}%")
print(f"Profit Factor:    {metrics.profit_factor:.2f}")
print(f"Expectancy:       ${metrics.expectancy:.2f}")
print(f"Avg Win:          ${metrics.avg_win:.2f}")
print(f"Avg Loss:         ${metrics.avg_loss:.2f}")
print(f"Largest Win:      ${metrics.largest_win:.2f}")
print(f"Largest Loss:     ${metrics.largest_loss:.2f}")

print("\n" + "="*50)
```

---

## Interpreting Results

### Good Strategy Characteristics

```
✅ Sharpe Ratio: > 2.0
✅ Win Rate: > 55%
✅ Profit Factor: > 1.5
✅ Max Drawdown: < 15%
✅ Positive Expectancy
✅ Consistent monthly returns
✅ Outperforms benchmark
```

### Red Flags

```
❌ Sharpe Ratio: < 0.5
❌ Win Rate: < 40%
❌ Profit Factor: < 1.0
❌ Max Drawdown: > 30%
❌ Negative Expectancy
❌ Large losing streaks
❌ Underperforms benchmark
```

---

## Monitoring Performance

### Daily Monitoring

```python
# Check at end of each day
- Current P&L
- Open positions
- Drawdown from peak
- Daily loss limit
```

### Weekly Review

```python
# Review each week
- Weekly return
- Number of trades
- Win rate this week
- Any red flags?
```

### Monthly Analysis

```python
# Deep dive monthly
- Monthly return vs target
- Risk metrics
- Strategy performance by symbol
- Adjust parameters if needed
```

---

## Performance Visualization

```python
import matplotlib.pyplot as plt

# Equity curve
plt.figure(figsize=(12, 6))
plt.plot(equity_curve, label='Strategy')
plt.plot(sp500_curve, label='S&P 500', alpha=0.7)
plt.title('Equity Curve')
plt.legend()
plt.grid(True)

# Drawdown chart
plt.figure(figsize=(12, 4))
plt.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.3, color='red')
plt.title('Drawdown')
plt.ylabel('Drawdown %')

# Monthly returns heatmap
monthly_returns_table = returns.resample('M').sum()
sns.heatmap(monthly_returns_table.values.reshape(-1, 12), annot=True, fmt='.1%')
plt.title('Monthly Returns')
```

---

## Best Practices

1. **Track all trades** - Keep detailed logs
2. **Compare to benchmark** - Measure alpha
3. **Monitor drawdowns** - Act when limits breached
4. **Review regularly** - Weekly/monthly analysis
5. **Focus on risk-adjusted returns** - Not just raw returns
6. **Be consistent** - Use same metrics over time
7. **Document changes** - Track parameter adjustments

---

## Related Documentation

- [Risk Management](risk_management.md)
- [Signal Generation](signal_logic.md)
- [Backtest Module](../modules/backtest.md)
