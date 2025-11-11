"""
Abstract base class for broker implementations.
Defines the interface that all brokers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from decimal import Decimal

from .order_types import (
    Order, Position, Fill, Account,
    OrderSide, OrderType, OrderStatus
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BrokerBase(ABC):
    """
    Abstract base class for broker implementations.

    All broker connectors (simulator, IBKR, MT5, etc.) must implement these methods.
    """

    def __init__(self, broker_name: str):
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
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from broker."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to broker.

        Returns:
            True if connected
        """
        pass

    @abstractmethod
    def get_account(self) -> Account:
        """
        Get account information.

        Returns:
            Account object with current state
        """
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """
        Get all open positions.

        Returns:
            List of Position objects
        """
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for specific symbol.

        Args:
            symbol: Symbol to query

        Returns:
            Position object or None if no position
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully
        """
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order status.

        Args:
            order_id: Order ID

        Returns:
            Order object or None if not found
        """
        pass

    @abstractmethod
    def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """
        Get orders.

        Args:
            symbol: Filter by symbol (optional)
            status: Filter by status (optional)

        Returns:
            List of Order objects
        """
        pass

    @abstractmethod
    def get_fills(
        self,
        symbol: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> List[Fill]:
        """
        Get trade fills/executions.

        Args:
            symbol: Filter by symbol (optional)
            order_id: Filter by order ID (optional)

        Returns:
            List of Fill objects
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Decimal:
        """
        Get current market price for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Current price as Decimal
        """
        pass

    @abstractmethod
    def get_market_hours(self, symbol: str) -> Dict[str, bool]:
        """
        Check if market is open.

        Args:
            symbol: Trading symbol

        Returns:
            Dictionary with 'is_open' and 'next_open'/'next_close' info
        """
        pass

    # Helper methods (can be overridden if needed)

    def validate_order_params(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
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
        if quantity <= Decimal('0'):
            raise ValueError(f"Quantity must be positive: {quantity}")

        if order_type == OrderType.LIMIT and limit_price is None:
            raise ValueError("LIMIT order requires limit_price")

        if order_type == OrderType.STOP and stop_price is None:
            raise ValueError("STOP order requires stop_price")

        if order_type == OrderType.STOP_LIMIT:
            if limit_price is None or stop_price is None:
                raise ValueError("STOP_LIMIT order requires both limit_price and stop_price")

        return True

    def close_position(
        self,
        symbol: str,
        order_type: OrderType = OrderType.MARKET
    ) -> Optional[Order]:
        """
        Close position for a symbol.

        Args:
            symbol: Symbol to close
            order_type: Order type to use

        Returns:
            Order object or None if no position to close
        """
        position = self.get_position(symbol)

        if position is None or position.quantity == Decimal('0'):
            self.logger.warning(f"No position to close for {symbol}")
            return None

        # Determine side (opposite of current position)
        side = OrderSide.SELL if position.quantity > Decimal('0') else OrderSide.BUY
        quantity = abs(position.quantity)

        self.logger.info(f"Closing position: {symbol} {side.value} {quantity}")

        return self.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            strategy="close_position"
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
