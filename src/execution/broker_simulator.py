"""
Simulated broker for paper trading.
Provides realistic order execution with slippage, fees, and latency simulation.
"""

import uuid
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from decimal import Decimal
from pathlib import Path
import json

from .broker_base import BrokerBase
from .order_types import (
    Order, Position, Fill, Account,
    OrderSide, OrderType, OrderStatus, TimeInForce
)
from ..utils.logger import get_logger
from ..utils.config_loader import get_config

logger = get_logger(__name__)


class BrokerSimulator(BrokerBase):
    """
    Simulated broker for paper trading.

    Features:
    - Realistic order execution
    - Configurable slippage and fees
    - Position tracking
    - Ledger persistence (JSON)
    """

    def __init__(
        self,
        initial_cash: Decimal = Decimal('100000'),
        slippage_bps: float = 1.5,
        commission_per_trade: Decimal = Decimal('2.0'),
        ledger_dir: Optional[Path] = None
    ):
        """
        Initialize simulator.

        Args:
            initial_cash: Starting cash balance
            slippage_bps: Slippage in basis points (default: 1.5)
            commission_per_trade: Fixed commission per trade
            ledger_dir: Directory to save ledger (default: data/journal)
        """
        super().__init__("simulator")

        self.config = get_config()

        # Account state
        self._account = Account(
            equity=initial_cash,
            cash=initial_cash
        )

        # Trading state
        self._positions: Dict[str, Position] = {}
        self._orders: Dict[str, Order] = {}
        self._fills: List[Fill] = []

        # Configuration
        self.slippage_bps = slippage_bps / 10000.0  # Convert to decimal
        self.commission_per_trade = commission_per_trade

        # Ledger
        if ledger_dir is None:
            ledger_dir = Path("data/journal")

        self.ledger_dir = ledger_dir
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

        # Connection state
        self._connected = False

        self.logger.info(
            f"Initialized simulator with ${initial_cash}, "
            f"slippage={slippage_bps}bps, commission=${commission_per_trade}"
        )

    def connect(self) -> bool:
        """Connect to simulator (always succeeds)."""
        self._connected = True
        self.logger.info("Simulator connected")
        return True

    def disconnect(self):
        """Disconnect from simulator."""
        if self._connected:
            self._save_ledger()
            self._connected = False
            self.logger.info("Simulator disconnected")

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    def get_account(self) -> Account:
        """Get account state."""
        # Update equity with current positions
        total_position_value = Decimal('0')

        for symbol, position in self._positions.items():
            try:
                current_price = self.get_current_price(symbol)
                position.update_price(current_price)
                total_position_value += position.unrealized_pnl
            except Exception as e:
                self.logger.warning(f"Error updating position {symbol}: {e}")

        self._account.equity = self._account.cash + total_position_value
        self._account.update_equity(self._account.equity)

        return self._account

    def get_positions(self) -> List[Position]:
        """Get all positions."""
        # Update positions with current prices
        for symbol, position in self._positions.items():
            try:
                current_price = self.get_current_price(symbol)
                position.update_price(current_price)
            except Exception as e:
                self.logger.warning(f"Error updating position {symbol}: {e}")

        return list(self._positions.values())

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        position = self._positions.get(symbol)

        if position:
            try:
                current_price = self.get_current_price(symbol)
                position.update_price(current_price)
            except Exception as e:
                self.logger.warning(f"Error updating position {symbol}: {e}")

        return position

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
        strategy: Optional[str] = None,
        **kwargs
    ) -> Order:
        """Place an order in simulator."""

        if not self.is_connected():
            raise RuntimeError("Simulator not connected")

        # Validate parameters
        self.validate_order_params(symbol, side, quantity, order_type, limit_price, stop_price)

        # Create order
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            stop_price=stop_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy,
            time_in_force=kwargs.get('time_in_force', TimeInForce.DAY),
            signal_confidence=kwargs.get('signal_confidence')
        )

        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.now()

        self._orders[order.order_id] = order

        self.logger.info(
            f"Order placed: {order.order_id} | {symbol} {side.value} {quantity} @ {order_type.value}"
        )

        # Execute immediately for MARKET orders (simplified simulation)
        if order_type == OrderType.MARKET:
            self._execute_market_order(order)

        return order

    def _execute_market_order(self, order: Order):
        """Execute market order immediately."""
        try:
            # Get current price
            current_price = self.get_current_price(order.symbol)

            # Apply slippage (worse fill for buyer, better for seller in illiquid markets)
            # For simplicity, always apply slippage against the trader
            if order.side == OrderSide.BUY:
                fill_price = current_price * Decimal(str(1.0 + self.slippage_bps))
            else:
                fill_price = current_price * Decimal(str(1.0 - self.slippage_bps))

            # Calculate commission
            commission = self.commission_per_trade

            # Check if enough cash
            if order.side == OrderSide.BUY:
                required_cash = fill_price * order.quantity + commission
                if required_cash > self._account.cash:
                    order.status = OrderStatus.REJECTED
                    order.notes = f"Insufficient cash: need ${required_cash}, have ${self._account.cash}"
                    self.logger.error(order.notes)
                    return

            # Create fill
            fill = Fill(
                fill_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                commission=commission
            )

            self._fills.append(fill)

            # Update order
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
            order.filled_quantity = order.quantity
            order.avg_fill_price = fill_price
            order.commission = commission

            # Update position
            self._update_position(order, fill)

            # Update account cash
            if order.side == OrderSide.BUY:
                self._account.cash -= (fill_price * order.quantity + commission)
            else:
                self._account.cash += (fill_price * order.quantity - commission)

            self.logger.info(
                f"Order filled: {order.order_id} | {order.symbol} {order.side.value} "
                f"{order.quantity} @ ${fill_price} (commission: ${commission})"
            )

        except Exception as e:
            order.status = OrderStatus.REJECTED
            order.notes = f"Execution error: {str(e)}"
            self.logger.error(f"Error executing order {order.order_id}: {e}", exc_info=True)

    def _update_position(self, order: Order, fill: Fill):
        """Update position after fill."""
        symbol = order.symbol

        if symbol not in self._positions:
            # New position
            self._positions[symbol] = Position(
                symbol=symbol,
                quantity=Decimal('0'),
                avg_entry_price=Decimal('0'),
                current_price=fill.price,
                strategy=order.strategy
            )

        position = self._positions[symbol]

        if order.side == OrderSide.BUY:
            # Adding to long or reducing short
            new_quantity = position.quantity + fill.quantity
            if position.quantity >= Decimal('0'):  # Long or flat
                # Averaging up/down
                total_cost = (position.avg_entry_price * position.quantity +
                             fill.price * fill.quantity)
                position.avg_entry_price = total_cost / new_quantity if new_quantity > Decimal('0') else Decimal('0')
            else:  # Closing short
                if new_quantity == Decimal('0'):
                    # Position fully closed
                    realized_pnl = (position.avg_entry_price - fill.price) * fill.quantity
                    position.realized_pnl += realized_pnl
                    self._account.total_pnl += realized_pnl

            position.quantity = new_quantity

        else:  # SELL
            # Adding to short or reducing long
            new_quantity = position.quantity - fill.quantity
            if position.quantity <= Decimal('0'):  # Short or flat
                # Averaging down/up
                total_cost = (position.avg_entry_price * abs(position.quantity) +
                             fill.price * fill.quantity)
                position.avg_entry_price = total_cost / abs(new_quantity) if new_quantity != Decimal('0') else Decimal('0')
            else:  # Closing long
                if new_quantity == Decimal('0'):
                    # Position fully closed
                    realized_pnl = (fill.price - position.avg_entry_price) * fill.quantity
                    position.realized_pnl += realized_pnl
                    self._account.total_pnl += realized_pnl

            position.quantity = new_quantity

        # Remove position if flat
        if position.quantity == Decimal('0'):
            del self._positions[symbol]

        position.update_price(fill.price)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel order."""
        order = self._orders.get(order_id)

        if order is None:
            self.logger.warning(f"Order not found: {order_id}")
            return False

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            self.logger.warning(f"Cannot cancel order in status {order.status.value}")
            return False

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now()

        self.logger.info(f"Order cancelled: {order_id}")
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self._orders.get(order_id)

    def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get orders with optional filters."""
        orders = list(self._orders.values())

        if symbol:
            orders = [o for o in orders if o.symbol == symbol]

        if status:
            orders = [o for o in orders if o.status == status]

        return orders

    def get_fills(
        self,
        symbol: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> List[Fill]:
        """Get fills with optional filters."""
        fills = self._fills

        if symbol:
            fills = [f for f in fills if f.symbol == symbol]

        if order_id:
            fills = [f for f in fills if f.order_id == order_id]

        return fills

    def get_current_price(self, symbol: str) -> Decimal:
        """Get current price from yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                raise ValueError(f"No price data for {symbol}")

            last_price = data['Close'].iloc[-1]
            return Decimal(str(last_price))

        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            raise

    def get_market_hours(self, symbol: str) -> Dict[str, bool]:
        """Check market hours (simplified)."""
        # Simplified: assume market open Mon-Fri 9:30-16:00 ET
        now = datetime.now()
        is_weekend = now.weekday() >= 5

        return {
            'is_open': not is_weekend,  # Simplified
            'session': 'regular' if not is_weekend else 'closed'
        }

    def _save_ledger(self):
        """Save ledger to JSON file."""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            ledger_file = self.ledger_dir / f"ledger_{date_str}.json"

            ledger = {
                'date': date_str,
                'account': self._account.to_dict(),
                'positions': [p.to_dict() for p in self._positions.values()],
                'orders': [o.to_dict() for o in self._orders.values()],
                'fills': [f.to_dict() for f in self._fills]
            }

            with open(ledger_file, 'w') as f:
                json.dump(ledger, f, indent=2)

            self.logger.info(f"Ledger saved: {ledger_file}")

        except Exception as e:
            self.logger.error(f"Error saving ledger: {e}", exc_info=True)
