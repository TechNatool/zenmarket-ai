"""
Execution engine - orchestrates the complete trading pipeline.
Signal → Sizing → Risk Check → Order → Monitoring → Journal
"""

from decimal import Decimal
from typing import Optional, Dict
from datetime import datetime

from .broker_base import BrokerBase
from .order_types import Order, OrderSide, OrderType
from .position_sizing import PositionSizer, SizingMethod
from .risk_manager import RiskManager, RiskLimits
from .compliance import ComplianceChecker
from .journal import TradeJournal
from .pnl_tracker import PnLTracker
from ..advisor.signal_generator import TradingSignal, SignalType
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionEngine:
    """
    Complete execution engine.

    Pipeline:
    1. Receive trading signal
    2. Calculate position size
    3. Validate risk
    4. Check compliance
    5. Place order
    6. Monitor execution
    7. Log to journal
    8. Update PnL
    """

    def __init__(
        self,
        broker: BrokerBase,
        risk_limits: Optional[RiskLimits] = None,
        sizing_method: SizingMethod = SizingMethod.FIXED_FRACTIONAL,
        journal_enabled: bool = True
    ):
        """
        Initialize execution engine.

        Args:
            broker: Broker instance
            risk_limits: Risk limits configuration
            sizing_method: Position sizing method
            journal_enabled: Enable trade journaling
        """
        self.broker = broker
        self.sizer = PositionSizer()
        self.risk_manager = RiskManager(broker, risk_limits)
        self.compliance = ComplianceChecker()

        self.journal = TradeJournal() if journal_enabled else None
        self.pnl_tracker = PnLTracker(broker.get_equity())

        self.sizing_method = sizing_method

        logger.info("Execution engine initialized")
        logger.info(f"Sizing method: {sizing_method.value}")
        logger.info(f"Journal enabled: {journal_enabled}")

    def execute_signal(
        self,
        signal: TradingSignal,
        order_type: OrderType = OrderType.MARKET,
        risk_percent: float = 0.01,
        dry_run: bool = False
    ) -> Optional[Order]:
        """
        Execute trading signal.

        Args:
            signal: Trading signal from advisor
            order_type: Type of order to place
            risk_percent: Risk percentage for sizing
            dry_run: If True, validate but don't place order

        Returns:
            Order object if successful, None otherwise
        """
        logger.info("=" * 60)
        logger.info(f"Executing signal: {signal.ticker} {signal.signal.value}")
        logger.info("=" * 60)

        try:
            # Step 1: Check if action needed
            if signal.signal == SignalType.HOLD:
                logger.info("Signal is HOLD - no action taken")
                return None

            # Step 2: Determine order side
            side = OrderSide.BUY if signal.signal == SignalType.BUY else OrderSide.SELL

            # Step 3: Check compliance
            is_compliant, status, message = self.compliance.check_market_hours(signal.ticker)
            if not is_compliant:
                logger.warning(f"Compliance check failed: {message}")
                if not dry_run:
                    return None

            # Step 4: Get current price and calculate stop loss
            try:
                current_price = self.broker.get_current_price(signal.ticker)
            except Exception as e:
                logger.error(f"Failed to get price for {signal.ticker}: {e}")
                return None

            # Calculate stop loss based on indicators
            stop_loss = self._calculate_stop_loss(
                current_price,
                signal,
                side
            )

            # Step 5: Calculate position size
            account = self.broker.get_account()
            equity = account.equity

            quantity = self._calculate_position_size(
                equity=equity,
                entry_price=current_price,
                stop_loss=stop_loss,
                risk_percent=risk_percent
            )

            if quantity <= Decimal('0'):
                logger.error("Calculated position size is zero or negative")
                return None

            logger.info(
                f"Position sizing: equity=${equity}, entry=${current_price}, "
                f"stop=${stop_loss}, risk={risk_percent*100}%, quantity={quantity}"
            )

            # Step 6: Validate risk
            is_valid, error_msg = self.risk_manager.validate_order(
                symbol=signal.ticker,
                side=side,
                quantity=quantity,
                entry_price=current_price,
                stop_loss=stop_loss
            )

            if not is_valid:
                logger.error(f"Risk validation failed: {error_msg}")
                return None

            logger.info("✓ Risk validation passed")

            # Step 7: Calculate take profit (optional)
            take_profit = self._calculate_take_profit(
                current_price,
                stop_loss,
                side,
                risk_reward_ratio=2.0  # Default 2:1 RR
            )

            # Dry run - stop here
            if dry_run:
                logger.info("DRY RUN - Order would be placed:")
                logger.info(f"  Symbol: {signal.ticker}")
                logger.info(f"  Side: {side.value}")
                logger.info(f"  Quantity: {quantity}")
                logger.info(f"  Type: {order_type.value}")
                logger.info(f"  Stop Loss: ${stop_loss}")
                logger.info(f"  Take Profit: ${take_profit}")
                logger.info("=" * 60)
                return None

            # Step 8: Place order
            logger.info(f"Placing order: {signal.ticker} {side.value} {quantity}")

            order = self.broker.place_order(
                symbol=signal.ticker,
                side=side,
                quantity=quantity,
                order_type=order_type,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy="advisor_signal",
                signal_confidence=signal.confidence
            )

            logger.info(f"✓ Order placed: {order.order_id}")

            # Step 9: Log to journal
            if self.journal:
                self.journal.log_order(order)

            # Step 10: Update PnL tracker
            self._update_pnl_tracker()

            logger.info("=" * 60)
            return order

        except Exception as e:
            logger.error(f"Error executing signal: {e}", exc_info=True)
            return None

    def _calculate_stop_loss(
        self,
        entry_price: Decimal,
        signal: TradingSignal,
        side: OrderSide
    ) -> Decimal:
        """Calculate stop loss based on indicators."""
        # Use ATR or fixed percentage
        indicators = signal.indicators

        # Default: 2% stop
        stop_distance_pct = Decimal('0.02')

        # Use ATR if available
        if indicators.atr:
            # Use 2x ATR as stop distance
            stop_distance = Decimal(str(indicators.atr)) * Decimal('2')
        else:
            stop_distance = entry_price * stop_distance_pct

        if side == OrderSide.BUY:
            stop_loss = entry_price - stop_distance
        else:
            stop_loss = entry_price + stop_distance

        return stop_loss

    def _calculate_take_profit(
        self,
        entry_price: Decimal,
        stop_loss: Decimal,
        side: OrderSide,
        risk_reward_ratio: float = 2.0
    ) -> Decimal:
        """Calculate take profit based on risk/reward ratio."""
        risk = abs(entry_price - stop_loss)
        reward = risk * Decimal(str(risk_reward_ratio))

        if side == OrderSide.BUY:
            take_profit = entry_price + reward
        else:
            take_profit = entry_price - reward

        return take_profit

    def _calculate_position_size(
        self,
        equity: Decimal,
        entry_price: Decimal,
        stop_loss: Decimal,
        risk_percent: float
    ) -> Decimal:
        """Calculate position size using configured method."""
        if self.sizing_method == SizingMethod.FIXED_FRACTIONAL:
            return self.sizer.fixed_fractional(
                equity=equity,
                risk_percent=risk_percent,
                entry_price=entry_price,
                stop_loss_price=stop_loss
            )

        elif self.sizing_method == SizingMethod.FIXED_DOLLAR:
            dollar_amount = equity * Decimal(str(risk_percent))
            return self.sizer.fixed_dollar(
                dollar_amount=dollar_amount,
                entry_price=entry_price
            )

        else:
            # Fallback to fixed fractional
            return self.sizer.fixed_fractional(
                equity=equity,
                risk_percent=risk_percent,
                entry_price=entry_price,
                stop_loss_price=stop_loss
            )

    def _update_pnl_tracker(self):
        """Update PnL tracker with current account state."""
        account = self.broker.get_account()

        self.pnl_tracker.add_snapshot(
            equity=account.equity,
            realized_pnl=account.total_pnl,
            unrealized_pnl=Decimal('0'),  # Would calculate from positions
            cash=account.cash
        )

    def get_status(self) -> Dict:
        """
        Get engine status.

        Returns:
            Dictionary with status information
        """
        return {
            'broker': self.broker.broker_name,
            'connected': self.broker.is_connected(),
            'risk_summary': self.risk_manager.get_risk_summary(),
            'performance': self.pnl_tracker.get_performance_metrics() if self.pnl_tracker else {},
            'journal_enabled': self.journal is not None
        }

    def shutdown(self):
        """Shutdown engine and save journals."""
        logger.info("Shutting down execution engine")

        if self.journal:
            self.journal.save_json()

        if self.broker.is_connected():
            self.broker.disconnect()

        logger.info("Execution engine shutdown complete")
