"""Performance metrics calculator for backtesting.

Provides comprehensive performance metrics including:
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Profit Factor
- Win Rate
- Risk/Reward Ratios
- And more...
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class PerformanceMetrics:
    """Complete performance metrics for a backtest."""

    # Time period
    start_date: datetime
    end_date: datetime
    duration_days: int

    # Returns
    total_return_pct: float
    annualized_return_pct: float
    cagr_pct: float

    # Risk metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown_pct: float
    max_drawdown_duration_days: int

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    avg_win: Decimal
    avg_loss: Decimal
    avg_trade: Decimal
    largest_win: Decimal
    largest_loss: Decimal

    # Risk/Reward
    avg_risk_reward_ratio: float
    expectancy: Decimal

    # Equity metrics
    final_equity: Decimal
    peak_equity: Decimal
    avg_daily_return_pct: float
    volatility_annualized_pct: float

    # Consecutive statistics
    max_consecutive_wins: int
    max_consecutive_losses: int

    @staticmethod
    def calculate(
        equity_curve: pd.DataFrame,
        trades: list[dict[str, Any]],
        initial_capital: Decimal,
        risk_free_rate: float = 0.02,
    ) -> "PerformanceMetrics":
        """Calculate all performance metrics from equity curve and trades.

        Args:
            equity_curve: DataFrame with columns ['timestamp', 'equity', 'drawdown']
            trades: List of trade dictionaries with 'pnl', 'entry_price', 'exit_price', etc.
            initial_capital: Starting capital
            risk_free_rate: Annual risk-free rate (default 2%)

        Returns:
            PerformanceMetrics object with all calculated metrics
        """
        # Time period
        start_date = equity_curve["timestamp"].iloc[0]
        end_date = equity_curve["timestamp"].iloc[-1]
        duration_days = (end_date - start_date).days

        # Returns
        final_equity = Decimal(str(equity_curve["equity"].iloc[-1]))
        total_return = (final_equity - initial_capital) / initial_capital
        total_return_pct = float(total_return * 100)

        # Annualized return
        years = duration_days / 365.25
        annualized_return_pct = (
            (float(final_equity / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        )

        # CAGR
        cagr_pct = annualized_return_pct  # Same calculation

        # Daily returns
        equity_curve["daily_return"] = equity_curve["equity"].pct_change()
        daily_returns = equity_curve["daily_return"].dropna()

        # Volatility
        volatility_daily = daily_returns.std()
        volatility_annualized_pct = float(volatility_daily * np.sqrt(252) * 100)

        # Sharpe Ratio
        excess_returns = daily_returns - (risk_free_rate / 252)
        sharpe_ratio = (
            float(excess_returns.mean() / excess_returns.std() * np.sqrt(252))
            if excess_returns.std() > 0
            else 0
        )

        # Sortino Ratio (only downside volatility)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = (
            float(excess_returns.mean() / downside_std * np.sqrt(252))
            if downside_std > 0 and len(downside_returns) > 0
            else 0
        )

        # Max Drawdown
        max_drawdown_pct = float(equity_curve["drawdown"].min() * 100)

        # Max Drawdown Duration
        max_dd_duration = _calculate_max_drawdown_duration(equity_curve)

        # Calmar Ratio (return / max drawdown)
        calmar_ratio = (
            float(annualized_return_pct / abs(max_drawdown_pct)) if max_drawdown_pct != 0 else 0
        )

        # Trade statistics
        if trades:
            winning_trades_list = [t for t in trades if Decimal(str(t["pnl"])) > 0]
            losing_trades_list = [t for t in trades if Decimal(str(t["pnl"])) < 0]

            total_trades = len(trades)
            winning_trades = len(winning_trades_list)
            losing_trades = len(losing_trades_list)
            win_rate_pct = (winning_trades / total_trades * 100) if total_trades > 0 else 0

            # Profit metrics
            total_profit = sum(Decimal(str(t["pnl"])) for t in winning_trades_list)
            total_loss = abs(sum(Decimal(str(t["pnl"])) for t in losing_trades_list))
            profit_factor = float(total_profit / total_loss) if total_loss > 0 else 0

            avg_win = total_profit / winning_trades if winning_trades > 0 else Decimal("0")
            avg_loss = -total_loss / losing_trades if losing_trades > 0 else Decimal("0")
            avg_trade = sum(Decimal(str(t["pnl"])) for t in trades) / total_trades

            largest_win = max((Decimal(str(t["pnl"])) for t in trades), default=Decimal("0"))
            largest_loss = min((Decimal(str(t["pnl"])) for t in trades), default=Decimal("0"))

            # Risk/Reward
            avg_risk_reward_ratio = float(abs(avg_win / avg_loss)) if avg_loss != 0 else 0

            # Expectancy (average profit per trade)
            expectancy = avg_trade

            # Consecutive wins/losses
            max_consecutive_wins = _calculate_max_consecutive(trades, win=True)
            max_consecutive_losses = _calculate_max_consecutive(trades, win=False)

        else:
            # No trades
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            win_rate_pct = 0
            profit_factor = 0
            avg_win = Decimal("0")
            avg_loss = Decimal("0")
            avg_trade = Decimal("0")
            largest_win = Decimal("0")
            largest_loss = Decimal("0")
            avg_risk_reward_ratio = 0
            expectancy = Decimal("0")
            max_consecutive_wins = 0
            max_consecutive_losses = 0

        # Peak equity
        peak_equity = Decimal(str(equity_curve["equity"].max()))

        # Average daily return
        avg_daily_return_pct = float(daily_returns.mean() * 100)

        return PerformanceMetrics(
            start_date=start_date.to_pydatetime(),
            end_date=end_date.to_pydatetime(),
            duration_days=duration_days,
            total_return_pct=total_return_pct,
            annualized_return_pct=annualized_return_pct,
            cagr_pct=cagr_pct,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown_pct=max_drawdown_pct,
            max_drawdown_duration_days=max_dd_duration,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate_pct=win_rate_pct,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_trade=avg_trade,
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_risk_reward_ratio=avg_risk_reward_ratio,
            expectancy=expectancy,
            final_equity=final_equity,
            peak_equity=peak_equity,
            avg_daily_return_pct=avg_daily_return_pct,
            volatility_annualized_pct=volatility_annualized_pct,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration_days": self.duration_days,
            "total_return_pct": self.total_return_pct,
            "annualized_return_pct": self.annualized_return_pct,
            "cagr_pct": self.cagr_pct,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "calmar_ratio": self.calmar_ratio,
            "max_drawdown_pct": self.max_drawdown_pct,
            "max_drawdown_duration_days": self.max_drawdown_duration_days,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate_pct": self.win_rate_pct,
            "profit_factor": self.profit_factor,
            "avg_win": float(self.avg_win),
            "avg_loss": float(self.avg_loss),
            "avg_trade": float(self.avg_trade),
            "largest_win": float(self.largest_win),
            "largest_loss": float(self.largest_loss),
            "avg_risk_reward_ratio": self.avg_risk_reward_ratio,
            "expectancy": float(self.expectancy),
            "final_equity": float(self.final_equity),
            "peak_equity": float(self.peak_equity),
            "avg_daily_return_pct": self.avg_daily_return_pct,
            "volatility_annualized_pct": self.volatility_annualized_pct,
            "max_consecutive_wins": self.max_consecutive_wins,
            "max_consecutive_losses": self.max_consecutive_losses,
        }


def _calculate_max_drawdown_duration(equity_curve: pd.DataFrame) -> int:
    """Calculate the maximum drawdown duration in days."""
    peak = equity_curve["equity"].expanding().max()
    drawdown_periods = (equity_curve["equity"] < peak).astype(int)

    max_duration = 0
    current_duration = 0

    for in_drawdown in drawdown_periods:
        if in_drawdown:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0

    return max_duration


def _calculate_max_consecutive(trades: list[dict[str, Any]], win: bool) -> int:
    """Calculate maximum consecutive wins or losses."""
    max_consecutive = 0
    current_consecutive = 0

    for trade in trades:
        pnl = Decimal(str(trade["pnl"]))
        is_win = pnl > 0

        if is_win == win:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0

    return max_consecutive
