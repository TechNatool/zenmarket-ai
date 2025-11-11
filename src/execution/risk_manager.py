"""
Risk manager with circuit breakers and safety mechanisms.
Implements kill-switches, position limits, and risk validation.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .order_types import Order, Position, OrderSide
from .broker_base import BrokerBase
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RiskLimits:
    """Risk limit configuration."""

    # Per-trade limits
    max_risk_per_trade_pct: float = 0.01  # 1%
    max_position_size_pct: float = 0.20   # 20% of equity per position

    # Daily limits
    max_risk_per_day_pct: float = 0.03    # 3%
    max_daily_drawdown_pct: float = 0.05  # 5%
    max_daily_loss_dollar: Optional[Decimal] = None

    # Position limits
    max_open_positions: int = 5
    max_correlated_positions: int = 3

    # Consecutive loss limits
    max_consecutive_losses: int = 3

    # Volatility limits
    max_atr_multiplier: float = 3.0  # Stop trading if ATR > 3x average

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'max_risk_per_trade_pct': self.max_risk_per_trade_pct,
            'max_position_size_pct': self.max_position_size_pct,
            'max_risk_per_day_pct': self.max_risk_per_day_pct,
            'max_daily_drawdown_pct': self.max_daily_drawdown_pct,
            'max_daily_loss_dollar': str(self.max_daily_loss_dollar) if self.max_daily_loss_dollar else None,
            'max_open_positions': self.max_open_positions,
            'max_correlated_positions': self.max_correlated_positions,
            'max_consecutive_losses': self.max_consecutive_losses,
            'max_atr_multiplier': self.max_atr_multiplier
        }


@dataclass
class RiskState:
    """Current risk state tracking."""

    # Daily tracking
    daily_pnl: Decimal = Decimal('0')
    daily_risk_used_pct: float = 0.0
    trades_today: int = 0
    losses_today: int = 0

    # Consecutive tracking
    consecutive_losses: int = 0
    consecutive_wins: int = 0

    # Circuit breaker status
    trading_halted: bool = False
    halt_reason: Optional[str] = None
    halt_timestamp: Optional[datetime] = None

    # Daily reset
    last_reset_date: datetime = field(default_factory=lambda: datetime.now().date())

    def reset_daily(self):
        """Reset daily counters."""
        self.daily_pnl = Decimal('0')
        self.daily_risk_used_pct = 0.0
        self.trades_today = 0
        self.losses_today = 0
        self.last_reset_date = datetime.now().date()
        logger.info("Daily risk state reset")

    def halt_trading(self, reason: str):
        """Halt trading with reason."""
        self.trading_halted = True
        self.halt_reason = reason
        self.halt_timestamp = datetime.now()
        logger.critical(f"🚨 TRADING HALTED: {reason}")

    def resume_trading(self):
        """Resume trading."""
        self.trading_halted = False
        self.halt_reason = None
        self.halt_timestamp = None
        logger.info("Trading resumed")

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'daily_pnl': str(self.daily_pnl),
            'daily_risk_used_pct': self.daily_risk_used_pct,
            'trades_today': self.trades_today,
            'losses_today': self.losses_today,
            'consecutive_losses': self.consecutive_losses,
            'consecutive_wins': self.consecutive_wins,
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'halt_timestamp': self.halt_timestamp.isoformat() if self.halt_timestamp else None
        }


class RiskManager:
    """
    Risk manager with circuit breakers and safety mechanisms.

    Features:
    - Per-trade risk validation
    - Daily loss limits
    - Drawdown circuit breaker
    - Position limits
    - Consecutive loss protection
    """

    def __init__(
        self,
        broker: BrokerBase,
        limits: Optional[RiskLimits] = None
    ):
        """
        Initialize risk manager.

        Args:
            broker: Broker instance
            limits: Risk limits configuration
        """
        self.broker = broker
        self.limits = limits or RiskLimits()
        self.state = RiskState()

        self.logger = get_logger(__name__)
        self.logger.info("Risk manager initialized")
        self.logger.info(f"Limits: {self.limits.to_dict()}")

    def check_daily_reset(self):
        """Check if daily counters need reset."""
        today = datetime.now().date()

        if today > self.state.last_reset_date:
            self.state.reset_daily()

    def validate_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        entry_price: Decimal,
        stop_loss: Optional[Decimal] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate order against risk limits.

        Args:
            symbol: Trading symbol
            side: Order side
            quantity: Order quantity
            entry_price: Entry price
            stop_loss: Stop loss price (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        self.check_daily_reset()

        # Check if trading is halted
        if self.state.trading_halted:
            return False, f"Trading halted: {self.state.halt_reason}"

        # Get account info
        account = self.broker.get_account()
        equity = account.equity

        if equity <= Decimal('0'):
            return False, "Account equity is zero or negative"

        # Calculate position value
        position_value = quantity * entry_price

        # 1. Check position size limit
        position_pct = float(position_value / equity)
        if position_pct > self.limits.max_position_size_pct:
            return False, (
                f"Position size {position_pct:.2%} exceeds limit "
                f"{self.limits.max_position_size_pct:.2%}"
            )

        # 2. Check per-trade risk limit (if stop loss provided)
        if stop_loss:
            risk_per_share = abs(entry_price - stop_loss)
            dollar_risk = risk_per_share * quantity
            risk_pct = float(dollar_risk / equity)

            if risk_pct > self.limits.max_risk_per_trade_pct:
                return False, (
                    f"Trade risk {risk_pct:.2%} exceeds limit "
                    f"{self.limits.max_risk_per_trade_pct:.2%}"
                )

        # 3. Check daily risk limit
        if self.state.daily_risk_used_pct >= self.limits.max_risk_per_day_pct:
            return False, (
                f"Daily risk limit reached: {self.state.daily_risk_used_pct:.2%} / "
                f"{self.limits.max_risk_per_day_pct:.2%}"
            )

        # 4. Check max open positions
        positions = self.broker.get_positions()
        if len(positions) >= self.limits.max_open_positions:
            # Allow closing orders
            if not self._is_closing_order(symbol, side, positions):
                return False, (
                    f"Max open positions reached: {len(positions)} / "
                    f"{self.limits.max_open_positions}"
                )

        # 5. Check daily drawdown
        if account.max_drawdown >= Decimal(str(self.limits.max_daily_drawdown_pct)):
            self.state.halt_trading(
                f"Daily drawdown limit reached: {account.max_drawdown:.2%}"
            )
            return False, self.state.halt_reason

        # 6. Check consecutive losses
        if self.state.consecutive_losses >= self.limits.max_consecutive_losses:
            self.state.halt_trading(
                f"Max consecutive losses reached: {self.state.consecutive_losses}"
            )
            return False, self.state.halt_reason

        # 7. Check daily loss dollar limit
        if self.limits.max_daily_loss_dollar:
            if self.state.daily_pnl < -abs(self.limits.max_daily_loss_dollar):
                self.state.halt_trading(
                    f"Daily loss limit reached: ${self.state.daily_pnl}"
                )
                return False, self.state.halt_reason

        # All checks passed
        return True, None

    def _is_closing_order(
        self,
        symbol: str,
        side: OrderSide,
        positions: List[Position]
    ) -> bool:
        """Check if order would close an existing position."""
        for position in positions:
            if position.symbol == symbol:
                if side == OrderSide.SELL and position.quantity > Decimal('0'):
                    return True  # Closing long
                if side == OrderSide.BUY and position.quantity < Decimal('0'):
                    return True  # Closing short
        return False

    def record_trade_result(
        self,
        pnl: Decimal,
        risk_pct: float
    ):
        """
        Record trade result and update state.

        Args:
            pnl: Trade PnL
            risk_pct: Risk percentage used
        """
        self.check_daily_reset()

        # Update daily counters
        self.state.daily_pnl += pnl
        self.state.daily_risk_used_pct += risk_pct
        self.state.trades_today += 1

        # Update consecutive counters
        if pnl < Decimal('0'):
            self.state.losses_today += 1
            self.state.consecutive_losses += 1
            self.state.consecutive_wins = 0

            self.logger.warning(
                f"Trade loss: ${pnl} | "
                f"Consecutive losses: {self.state.consecutive_losses}"
            )

        else:
            self.state.consecutive_wins += 1
            self.state.consecutive_losses = 0

            self.logger.info(
                f"Trade win: ${pnl} | "
                f"Consecutive wins: {self.state.consecutive_wins}"
            )

        # Check circuit breakers
        self._check_circuit_breakers()

    def _check_circuit_breakers(self):
        """Check all circuit breakers."""

        # Daily drawdown breaker
        account = self.broker.get_account()
        if account.max_drawdown >= Decimal(str(self.limits.max_daily_drawdown_pct)):
            self.state.halt_trading(
                f"Circuit breaker: Daily drawdown {account.max_drawdown:.2%} >= "
                f"{self.limits.max_daily_drawdown_pct:.2%}"
            )

        # Consecutive loss breaker
        if self.state.consecutive_losses >= self.limits.max_consecutive_losses:
            self.state.halt_trading(
                f"Circuit breaker: {self.state.consecutive_losses} consecutive losses"
            )

        # Daily loss breaker
        if self.limits.max_daily_loss_dollar:
            if self.state.daily_pnl < -abs(self.limits.max_daily_loss_dollar):
                self.state.halt_trading(
                    f"Circuit breaker: Daily loss ${self.state.daily_pnl} exceeds "
                    f"${self.limits.max_daily_loss_dollar}"
                )

    def get_risk_summary(self) -> Dict:
        """
        Get risk summary.

        Returns:
            Dictionary with risk metrics
        """
        self.check_daily_reset()

        account = self.broker.get_account()
        positions = self.broker.get_positions()

        return {
            'limits': self.limits.to_dict(),
            'state': self.state.to_dict(),
            'account': {
                'equity': str(account.equity),
                'drawdown': f"{account.max_drawdown:.2%}"
            },
            'positions': {
                'count': len(positions),
                'max': self.limits.max_open_positions
            },
            'daily': {
                'pnl': str(self.state.daily_pnl),
                'trades': self.state.trades_today,
                'risk_used': f"{self.state.daily_risk_used_pct:.2%}"
            }
        }

    def force_halt(self, reason: str):
        """
        Manually halt trading.

        Args:
            reason: Reason for halt
        """
        self.state.halt_trading(reason)

    def force_resume(self):
        """Manually resume trading (use with caution)."""
        self.logger.warning("Manually resuming trading")
        self.state.resume_trading()

    def check_volatility_limit(
        self,
        current_atr: float,
        average_atr: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if volatility is within acceptable limits.

        Args:
            current_atr: Current ATR
            average_atr: Average/normal ATR

        Returns:
            Tuple of (is_acceptable, warning_message)
        """
        if current_atr <= 0 or average_atr <= 0:
            return True, None

        atr_ratio = current_atr / average_atr

        if atr_ratio > self.limits.max_atr_multiplier:
            warning = (
                f"High volatility detected: ATR ratio {atr_ratio:.2f}x "
                f"(limit: {self.limits.max_atr_multiplier}x)"
            )
            self.logger.warning(warning)
            return False, warning

        return True, None
