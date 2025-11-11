"""
PnL (Profit & Loss) tracker with performance metrics.
Tracks realized/unrealized PnL, equity curve, and drawdown.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PnLSnapshot:
    """PnL snapshot at a point in time."""

    timestamp: datetime
    equity: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    cash: Decimal
    drawdown: Decimal

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'equity': str(self.equity),
            'realized_pnl': str(self.realized_pnl),
            'unrealized_pnl': str(self.unrealized_pnl),
            'cash': str(self.cash),
            'drawdown': str(self.drawdown)
        }


class PnLTracker:
    """
    Track PnL and performance metrics.

    Features:
    - Equity curve
    - Realized/unrealized PnL
    - Drawdown tracking
    - Performance metrics
    """

    def __init__(self, initial_equity: Decimal = Decimal('100000')):
        """
        Initialize PnL tracker.

        Args:
            initial_equity: Starting equity
        """
        self.initial_equity = initial_equity
        self.peak_equity = initial_equity

        self.snapshots: List[PnLSnapshot] = []
        self.trades: List[Dict] = []

        self.total_realized_pnl = Decimal('0')
        self.total_unrealized_pnl = Decimal('0')

        logger.info(f"PnL tracker initialized with equity: ${initial_equity}")

    def add_snapshot(
        self,
        equity: Decimal,
        realized_pnl: Decimal,
        unrealized_pnl: Decimal,
        cash: Decimal
    ):
        """
        Add equity snapshot.

        Args:
            equity: Current equity
            realized_pnl: Realized PnL
            unrealized_pnl: Unrealized PnL
            cash: Cash balance
        """
        # Update peak
        if equity > self.peak_equity:
            self.peak_equity = equity

        # Calculate drawdown
        drawdown = (self.peak_equity - equity) / self.peak_equity if self.peak_equity > Decimal('0') else Decimal('0')

        snapshot = PnLSnapshot(
            timestamp=datetime.now(),
            equity=equity,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            cash=cash,
            drawdown=drawdown
        )

        self.snapshots.append(snapshot)
        self.total_realized_pnl = realized_pnl
        self.total_unrealized_pnl = unrealized_pnl

    def record_trade(
        self,
        symbol: str,
        pnl: Decimal,
        quantity: Decimal,
        entry_price: Decimal,
        exit_price: Decimal
    ):
        """
        Record closed trade.

        Args:
            symbol: Trading symbol
            pnl: Trade PnL
            quantity: Trade quantity
            entry_price: Entry price
            exit_price: Exit price
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'pnl': str(pnl),
            'quantity': str(quantity),
            'entry_price': str(entry_price),
            'exit_price': str(exit_price),
            'return_pct': float((exit_price - entry_price) / entry_price * 100) if entry_price > Decimal('0') else 0.0
        }

        self.trades.append(trade)
        logger.info(f"Trade recorded: {symbol} PnL=${pnl}")

    def get_equity_curve(self) -> List[Dict]:
        """
        Get equity curve data.

        Returns:
            List of timestamp/equity pairs
        """
        return [
            {'timestamp': s.timestamp.isoformat(), 'equity': str(s.equity)}
            for s in self.snapshots
        ]

    def get_drawdown_curve(self) -> List[Dict]:
        """
        Get drawdown curve data.

        Returns:
            List of timestamp/drawdown pairs
        """
        return [
            {'timestamp': s.timestamp.isoformat(), 'drawdown': str(s.drawdown)}
            for s in self.snapshots
        ]

    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics.

        Returns:
            Dictionary with metrics
        """
        if not self.snapshots:
            return {}

        current_equity = self.snapshots[-1].equity
        total_return = (current_equity - self.initial_equity) / self.initial_equity

        # Calculate max drawdown
        max_drawdown = max([s.drawdown for s in self.snapshots], default=Decimal('0'))

        # Win rate
        winning_trades = sum(1 for t in self.trades if Decimal(t['pnl']) > Decimal('0'))
        total_trades = len(self.trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        # Average win/loss
        winning_pnls = [Decimal(t['pnl']) for t in self.trades if Decimal(t['pnl']) > Decimal('0')]
        losing_pnls = [abs(Decimal(t['pnl'])) for t in self.trades if Decimal(t['pnl']) < Decimal('0')]

        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else Decimal('0')
        avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else Decimal('0')

        profit_factor = avg_win / avg_loss if avg_loss > Decimal('0') else Decimal('0')

        return {
            'initial_equity': str(self.initial_equity),
            'current_equity': str(current_equity),
            'total_return': f"{total_return:.2%}",
            'total_return_dollar': str(current_equity - self.initial_equity),
            'realized_pnl': str(self.total_realized_pnl),
            'unrealized_pnl': str(self.total_unrealized_pnl),
            'max_drawdown': f"{max_drawdown:.2%}",
            'peak_equity': str(self.peak_equity),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': f"{win_rate:.2%}",
            'avg_win': str(avg_win),
            'avg_loss': str(avg_loss),
            'profit_factor': str(profit_factor)
        }
