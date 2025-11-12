"""Backtesting broker for historical simulation.

Extends BrokerBase to provide historical order execution simulation
using pre-loaded historical data.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

import pandas as pd

from src.execution.broker_base import BrokerBase
from src.execution.order_types import (
    Account,
    Fill,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    TimeInForce,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BacktestBroker(BrokerBase):
    """Broker implementation for historical backtesting.

    Uses pre-loaded historical OHLC data to simulate realistic order fills.
    Supports configurable slippage, commissions, and fill simulation.

    Attributes:
        historical_data: Dict mapping symbols to DataFrames with OHLC data
        current_timestamp: Current simulation timestamp
        slippage_bps: Slippage in basis points
        commission_per_trade: Fixed commission per trade
    """

    def __init__(
        self,
        historical_data: dict[str, pd.DataFrame],
        initial_cash: Decimal = Decimal("100000"),
        slippage_bps: float = 1.5,
        commission_per_trade: Decimal = Decimal("2.0"),
    ) -> None:
        """Initialize backtest broker.

        Args:
            historical_data: Dict of symbol -> DataFrame with OHLC data
            initial_cash: Starting cash balance
            slippage_bps: Slippage in basis points
            commission_per_trade: Fixed commission per trade
        """
        super().__init__("BacktestBroker")

        # Historical data
        self.historical_data = historical_data
        self.current_timestamp: datetime | None = None
        self._current_bar: dict[str, dict[str, Any]] = {}

        # Account state
        self._account = Account(equity=initial_cash, cash=initial_cash)

        # Trading state
        self._positions: dict[str, Position] = {}
        self._orders: dict[str, Order] = {}
        self._fills: list[Fill] = []

        # Configuration
        self.slippage_bps = slippage_bps / 10000.0
        self.commission_per_trade = commission_per_trade

        # Connection state
        self._connected = False

        self.logger.info(
            f"Initialized BacktestBroker with ${initial_cash}, "
            f"slippage={slippage_bps}bps, commission=${commission_per_trade}"
        )

    def set_current_bar(self, timestamp: datetime, bar_data: dict[str, dict[str, Any]]) -> None:
        """Set current bar data for simulation.

        Args:
            timestamp: Current simulation timestamp
            bar_data: Dict mapping symbols to OHLC data
        """
        self.current_timestamp = timestamp
        self._current_bar = bar_data

        # Update positions with current prices
        self._update_positions()

    def _update_positions(self) -> None:
        """Update position values based on current prices."""
        total_position_value = Decimal("0")

        for symbol, position in self._positions.items():
            if position.quantity != Decimal("0"):
                current_price = self._get_current_bar_price(symbol, "Close")
                position.current_price = current_price
                position.market_value = position.quantity * current_price
                position.unrealized_pnl = (
                    current_price - position.avg_entry_price
                ) * position.quantity

                total_position_value += position.market_value

        # Update equity
        self._account.equity = self._account.cash + total_position_value

    def _get_current_bar_price(self, symbol: str, price_type: str = "Close") -> Decimal:
        """Get price from current bar.

        Args:
            symbol: Symbol to get price for
            price_type: Price type (Open, High, Low, Close)

        Returns:
            Price as Decimal

        Raises:
            ValueError: If symbol or price type not found
        """
        if symbol not in self._current_bar:
            raise ValueError(f"No data for symbol {symbol} at current timestamp")

        if price_type not in self._current_bar[symbol]:
            raise ValueError(f"Price type {price_type} not found for {symbol}")

        return Decimal(str(self._current_bar[symbol][price_type]))

    # ==================== Connection Methods ====================

    def connect(self) -> bool:
        """Connect to backtest broker (always succeeds)."""
        self._connected = True
        self.logger.info("BacktestBroker connected")
        return True

    def disconnect(self) -> None:
        """Disconnect from backtest broker."""
        self._connected = False
        self.logger.info("BacktestBroker disconnected")

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    # ==================== Account Methods ====================

    def get_account(self) -> Account:
        """Get current account state."""
        return self._account

    def get_equity(self) -> Decimal:
        """Get current equity."""
        return self._account.equity

    def get_cash(self) -> Decimal:
        """Get current cash balance."""
        return self._account.cash

    # ==================== Position Methods ====================

    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        return [p for p in self._positions.values() if p.quantity != Decimal("0")]

    def get_position(self, symbol: str) -> Position | None:
        """Get position for a specific symbol."""
        position = self._positions.get(symbol)
        if position and position.quantity != Decimal("0"):
            return position
        return None

    # ==================== Order Methods ====================

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Decimal | None = None,
        stop_price: Decimal | None = None,
        stop_loss: Decimal | None = None,
        take_profit: Decimal | None = None,
        strategy: str | None = None,
        **kwargs: Any,
    ) -> Order:
        """Place an order.

        In backtesting, market orders are filled immediately at current bar's close
        with simulated slippage.
        """
        # Validate parameters
        self.validate_order_params(symbol, side, quantity, order_type, limit_price, stop_price)

        # Create order
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=OrderStatus.PENDING,
            limit_price=limit_price,
            stop_price=stop_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            time_in_force=TimeInForce.DAY,
            created_at=self.current_timestamp or datetime.now(),
            strategy=strategy,
        )

        self._orders[order_id] = order

        # Execute order immediately for market orders
        if order_type == OrderType.MARKET:
            self._execute_market_order(order)

        return order

    def _execute_market_order(self, order: Order) -> None:
        """Execute a market order with slippage simulation."""
        try:
            # Get fill price (close price with slippage)
            base_price = self._get_current_bar_price(order.symbol, "Close")

            # Apply slippage (unfavorable to the trader)
            slippage_factor = Decimal(
                str(1 + self.slippage_bps if order.side == OrderSide.BUY else 1 - self.slippage_bps)
            )
            fill_price = base_price * slippage_factor

            # Check if we have sufficient funds
            if order.side == OrderSide.BUY:
                required_cash = fill_price * order.quantity + self.commission_per_trade
                if required_cash > self._account.cash:
                    order.status = OrderStatus.REJECTED
                    order.updated_at = self.current_timestamp or datetime.now()
                    self.logger.warning(
                        f"Insufficient funds for {order.symbol}: "
                        f"required ${required_cash}, available ${self._account.cash}"
                    )
                    return

            # Check if we have the position to sell
            if order.side == OrderSide.SELL:
                position = self._positions.get(order.symbol)
                if position is None or position.quantity < order.quantity:
                    order.status = OrderStatus.REJECTED
                    order.updated_at = self.current_timestamp or datetime.now()
                    self.logger.warning(f"Insufficient shares to sell {order.symbol}")
                    return

            # Create fill
            fill = Fill(
                fill_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                commission=self.commission_per_trade,
                timestamp=self.current_timestamp or datetime.now(),
            )

            self._fills.append(fill)

            # Update order
            order.filled_quantity = order.quantity
            order.avg_fill_price = fill_price
            order.status = OrderStatus.FILLED
            order.updated_at = self.current_timestamp or datetime.now()

            # Update position
            self._update_position_from_fill(fill)

            self.logger.info(
                f"Filled {order.side.value} {order.quantity} {order.symbol} @ ${fill_price:.2f}"
            )

        except Exception as e:
            order.status = OrderStatus.REJECTED
            order.updated_at = self.current_timestamp or datetime.now()
            self.logger.exception(f"Failed to execute order: {e}")

    def _update_position_from_fill(self, fill: Fill) -> None:
        """Update position based on fill."""
        # Get or create position
        if fill.symbol not in self._positions:
            self._positions[fill.symbol] = Position(
                symbol=fill.symbol,
                quantity=Decimal("0"),
                avg_entry_price=Decimal("0"),
                market_value=Decimal("0"),
                unrealized_pnl=Decimal("0"),
                current_price=fill.price,
            )

        position = self._positions[fill.symbol]

        if fill.side == OrderSide.BUY:
            # Add to position
            total_cost = position.avg_entry_price * position.quantity
            new_cost = fill.price * fill.quantity
            new_quantity = position.quantity + fill.quantity

            position.avg_entry_price = (
                (total_cost + new_cost) / new_quantity if new_quantity > 0 else Decimal("0")
            )
            position.quantity = new_quantity

            # Deduct cash
            self._account.cash -= fill.price * fill.quantity + fill.commission

        else:  # SELL
            # Reduce position
            position.quantity -= fill.quantity

            # Add cash (proceeds minus commission)
            proceeds = fill.price * fill.quantity
            self._account.cash += proceeds - fill.commission

            # If position is fully closed, realize PnL
            if position.quantity == Decimal("0"):
                position.avg_entry_price = Decimal("0")

        # Update current price
        position.current_price = fill.price
        position.market_value = position.quantity * fill.price
        position.unrealized_pnl = (fill.price - position.avg_entry_price) * position.quantity

        # Update account equity
        total_position_value = sum(p.market_value for p in self._positions.values())
        self._account.equity = self._account.cash + total_position_value

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        order = self._orders.get(order_id)
        if order is None:
            return False

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False

        order.status = OrderStatus.CANCELLED
        order.updated_at = self.current_timestamp or datetime.now()
        return True

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ID."""
        return self._orders.get(order_id)

    def get_orders(
        self, symbol: str | None = None, status: OrderStatus | None = None
    ) -> list[Order]:
        """Get orders with optional filters."""
        orders = list(self._orders.values())

        if symbol:
            orders = [o for o in orders if o.symbol == symbol]

        if status:
            orders = [o for o in orders if o.status == status]

        return orders

    def get_fills(self, symbol: str | None = None, order_id: str | None = None) -> list[Fill]:
        """Get fills with optional filters."""
        fills = self._fills

        if symbol:
            fills = [f for f in fills if f.symbol == symbol]

        if order_id:
            fills = [f for f in fills if f.order_id == order_id]

        return fills

    # ==================== Market Data Methods ====================

    def get_current_price(self, symbol: str) -> Decimal:
        """Get current price for a symbol."""
        return self._get_current_bar_price(symbol, "Close")

    def get_market_hours(self, symbol: str) -> dict[str, bool]:
        """Check if market is open (always True in backtest)."""
        return {"is_open": True, "session": "backtest"}
