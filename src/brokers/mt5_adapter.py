"""MetaTrader 5 adapter.

Provides integration with MetaTrader 5 for live trading.

PREREQUISITES:
1. Install MetaTrader 5 terminal (Windows only)
2. Install MetaTrader5 Python package: pip install MetaTrader5
3. Set environment variables (optional):
   - MT5_LOGIN
   - MT5_PASSWORD
   - MT5_SERVER

SAFETY:
- Always test with demo account first
- Live trading requires explicit confirmation
- Implement circuit breakers and risk limits
- MT5 is primarily for forex/CFD trading
"""

import os
import platform
from decimal import Decimal
from typing import Any

# MT5 is Windows-only
if platform.system() == "Windows":
    try:
        import MetaTrader5 as mt5
    except ImportError:
        mt5 = None  # type: ignore
else:
    mt5 = None  # type: ignore

from src.execution.broker_base import BrokerBase
from src.execution.order_types import (
    Account,
    Fill,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MT5Adapter(BrokerBase):
    """MetaTrader 5 adapter.

    Connects to MT5 terminal for live/demo trading.
    Note: MT5 is Windows-only.
    """

    def __init__(
        self,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
    ) -> None:
        """Initialize MT5 adapter.

        Args:
            login: MT5 account number (default: from env)
            password: MT5 password (default: from env)
            server: MT5 server (default: from env)

        Raises:
            RuntimeError: If not on Windows or MT5 not installed
        """
        super().__init__("MT5")

        if platform.system() != "Windows":
            raise RuntimeError("MetaTrader 5 is only available on Windows")

        if mt5 is None:
            raise ImportError("MetaTrader5 is not installed. Install with: pip install MetaTrader5")

        # Configuration
        self.login = login or (int(os.getenv("MT5_LOGIN")) if os.getenv("MT5_LOGIN") else None)
        self.password = password or os.getenv("MT5_PASSWORD")
        self.server = server or os.getenv("MT5_SERVER")

        # State tracking
        self._orders: dict[str, Order] = {}

        self.logger.info("Initialized MT5 adapter")

    def connect(self) -> bool:
        """Connect to MT5 terminal."""
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                self.logger.error(f"MT5 initialization failed: {error}")
                return False

            # Login if credentials provided
            if self.login and self.password and self.server:
                if not mt5.login(self.login, password=self.password, server=self.server):
                    error = mt5.last_error()
                    self.logger.error(f"MT5 login failed: {error}")
                    return False

            self.logger.info("Connected to MT5")
            return True

        except Exception as e:
            self.logger.exception(f"Failed to connect to MT5: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from MT5."""
        mt5.shutdown()
        self.logger.info("Disconnected from MT5")

    def is_connected(self) -> bool:
        """Check if connected to MT5."""
        try:
            return mt5.terminal_info() is not None
        except Exception:
            return False

    def get_account(self) -> Account:
        """Get account information."""
        if not self.is_connected():
            raise RuntimeError("Not connected to MT5")

        account_info = mt5.account_info()
        if account_info is None:
            raise RuntimeError("Failed to get account info")

        return Account(
            equity=Decimal(str(account_info.equity)),
            cash=Decimal(str(account_info.balance)),
        )

    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        if not self.is_connected():
            raise RuntimeError("Not connected to MT5")

        mt5_positions = mt5.positions_get()
        if mt5_positions is None:
            return []

        positions = []
        for mt5_pos in mt5_positions:
            positions.append(
                Position(
                    symbol=mt5_pos.symbol,
                    quantity=Decimal(str(mt5_pos.volume))
                    * (1 if mt5_pos.type == mt5.ORDER_TYPE_BUY else -1),
                    avg_entry_price=Decimal(str(mt5_pos.price_open)),
                    market_value=Decimal(str(mt5_pos.volume * mt5_pos.price_current)),
                    unrealized_pnl=Decimal(str(mt5_pos.profit)),
                    current_price=Decimal(str(mt5_pos.price_current)),
                )
            )

        return positions

    def get_position(self, symbol: str) -> Position | None:
        """Get position for a specific symbol."""
        positions = self.get_positions()
        for pos in positions:
            if pos.symbol == symbol:
                return pos
        return None

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
        """Place an order with MT5."""
        if not self.is_connected():
            raise RuntimeError("Not connected to MT5")

        # Validate parameters
        self.validate_order_params(symbol, side, quantity, order_type, limit_price, stop_price)

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise ValueError(f"Symbol {symbol} not found")

        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(quantity),
            "type": mt5.ORDER_TYPE_BUY if side == OrderSide.BUY else mt5.ORDER_TYPE_SELL,
            "magic": 123456,  # Magic number for tracking
            "comment": strategy or "ZenMarket AI",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if order_type == OrderType.MARKET:
            price = (
                mt5.symbol_info_tick(symbol).ask
                if side == OrderSide.BUY
                else mt5.symbol_info_tick(symbol).bid
            )
            request["price"] = price
        elif order_type == OrderType.LIMIT:
            request["price"] = float(limit_price)  # type: ignore
            request["type"] = (
                mt5.ORDER_TYPE_BUY_LIMIT if side == OrderSide.BUY else mt5.ORDER_TYPE_SELL_LIMIT
            )
        else:
            raise ValueError(f"Order type {order_type} not yet implemented for MT5")

        # Add SL/TP if provided
        if stop_loss:
            request["sl"] = float(stop_loss)
        if take_profit:
            request["tp"] = float(take_profit)

        # Send order
        result = mt5.order_send(request)

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            error = result.comment if result else "Unknown error"
            raise RuntimeError(f"Order failed: {error}")

        # Create our Order object
        order = Order(
            order_id=str(result.order),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=(
                OrderStatus.FILLED
                if result.retcode == mt5.TRADE_RETCODE_DONE
                else OrderStatus.PENDING
            ),
            limit_price=limit_price,
            stop_price=stop_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy,
        )

        self._orders[order.order_id] = order

        self.logger.info(f"Placed order: {side.value} {quantity} {symbol}")

        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        # MT5 cancel implementation
        # Note: Filled orders cannot be cancelled
        order = self._orders.get(order_id)
        # Would implement MT5 order cancellation here
        return bool(order and order.status == OrderStatus.PENDING)

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
        """Get fills (deals)."""
        # Note: This is a simplified implementation
        # Full implementation would query MT5 deal history
        return []
        # TODO: Implement fill tracking from MT5 deals

    def get_current_price(self, symbol: str) -> Decimal:
        """Get current market price."""
        if not self.is_connected():
            raise RuntimeError("Not connected to MT5")

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise ValueError(f"No price data available for {symbol}")

        # Return mid price
        return Decimal(str((tick.ask + tick.bid) / 2))

    def get_market_hours(self, symbol: str) -> dict[str, bool]:
        """Check if market is open."""
        if not self.is_connected():
            raise RuntimeError("Not connected to MT5")

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"is_open": False}

        # Check if trading is allowed
        is_open = symbol_info.trade_mode in [
            mt5.SYMBOL_TRADE_MODE_FULL,
            mt5.SYMBOL_TRADE_MODE_LONGONLY,
            mt5.SYMBOL_TRADE_MODE_SHORTONLY,
        ]

        return {"is_open": is_open, "session": "market"}
