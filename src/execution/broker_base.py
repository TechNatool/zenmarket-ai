"""
Abstract base class for broker implementations.
Defines the interface that all brokers must implement.
"""

from abc import ABC, abstractmethod
from decimal import Decimal

from src.utils.logger import get_logger

from .order_types import Account, Fill, Order, OrderSide, OrderStatus, OrderType, Position

logger = get_logger(__name__)


class BrokerBase(ABC):
    """
    Abstract base class for broker implementations.

    All broker connectors (simulator, IBKR, MT5, etc.) must implement these methods.
    """

    def __init__(self, broker_name: str) -> None:
        """
        Initialize broker.

        Args:
            broker_name: Name of the broker (for logging)
        """
        self.broker_name = broker_name
        self.logger = get_logger(f"broker.{broker_name}")

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to broker.

        Returns:
            True if connected successfully
        """

    @abstractmethod
    def disconnect(self):
        """Disconnect from broker."""

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to broker.

        Returns:
            True if connected
        """

    @abstractmethod
    def get_account(self) -> Account:
        """
        Get account information.

        Returns:
            Account object with current state
        """

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """
        Get all open positions.

        Returns:
            List of Position objects
        """

    @abstractmethod
    def get_position(self, symbol: str) -> Position | None:
        """
        Get position for specific symbol.

        Args:
            symbol: Symbol to query

        Returns:
            Position object or None if no position
        """

    @abstractmethod
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
        **kwargs,
    ) -> Order:
        """
        Place an order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: Type of order
            limit_price: Limit price (for LIMIT and STOP_LIMIT orders)
            stop_price: Stop price (for STOP and STOP_LIMIT orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            strategy: Strategy name (for tracking)
            **kwargs: Additional broker-specific parameters

        Returns:
            Order object

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If order placement fails
        """

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully
        """

    @abstractmethod
    def get_order(self, order_id: str) -> Order | None:
        """
        Get order status.

        Args:
            order_id: Order ID

        Returns:
            Order object or None if not found
        """

    @abstractmethod
    def get_orders(
        self, symbol: str | None = None, status: OrderStatus | None = None
    ) -> list[Order]:
        """
        Get orders.

        Args:
            symbol: Filter by symbol (optional)
            status: Filter by status (optional)

        Returns:
            List of Order objects
        """

    @abstractmethod
    def get_fills(self, symbol: str | None = None, order_id: str | None = None) -> list[Fill]:
        """
        Get trade fills/executions.

        Args:
            symbol: Filter by symbol (optional)
            order_id: Filter by order ID (optional)

        Returns:
            List of Fill objects
        """

    @abstractmethod
    def get_current_price(self, symbol: str) -> Decimal:
        """
        Get current market price for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Current price as Decimal
        """

    @abstractmethod
    def get_market_hours(self, symbol: str) -> dict[str, bool]:
        """
        Check if market is open.

        Args:
            symbol: Trading symbol

        Returns:
            Dictionary with 'is_open' and 'next_open'/'next_close' info
        """

    # Helper methods (can be overridden if needed)

    def validate_order_params(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType,
        limit_price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> bool:
        """
        Validate order parameters.

        Args:
            symbol: Trading symbol
            side: Order side
            quantity: Quantity
            order_type: Order type
            limit_price: Limit price
            stop_price: Stop price

        Returns:
            True if valid

        Raises:
            ValueError: If parameters are invalid
        """
        if quantity <= Decimal("0"):
            raise ValueError(f"Quantity must be positive: {quantity}")

        if order_type == OrderType.LIMIT and limit_price is None:
            raise ValueError("LIMIT order requires limit_price")

        if order_type == OrderType.STOP and stop_price is None:
            raise ValueError("STOP order requires stop_price")

        if order_type == OrderType.STOP_LIMIT:
            if limit_price is None or stop_price is None:
                raise ValueError("STOP_LIMIT order requires both limit_price and stop_price")

        return True

    def close_position(self, symbol: str, order_type: OrderType = OrderType.MARKET) -> Order | None:
        """
        Close position for a symbol.

        Args:
            symbol: Symbol to close
            order_type: Order type to use

        Returns:
            Order object or None if no position to close
        """
        position = self.get_position(symbol)

        if position is None or position.quantity == Decimal("0"):
            self.logger.warning(f"No position to close for {symbol}")
            return None

        # Determine side (opposite of current position)
        side = OrderSide.SELL if position.quantity > Decimal("0") else OrderSide.BUY
        quantity = abs(position.quantity)

        self.logger.info(f"Closing position: {symbol} {side.value} {quantity}")

        return self.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            strategy="close_position",
        )

    def get_equity(self) -> Decimal:
        """
        Get current account equity.

        Returns:
            Equity as Decimal
        """
        account = self.get_account()
        return account.equity

    def get_cash(self) -> Decimal:
        """
        Get current cash balance.

        Returns:
            Cash as Decimal
        """
        account = self.get_account()
        return account.cash
