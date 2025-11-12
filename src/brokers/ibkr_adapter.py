"""Interactive Brokers adapter using ib_insync.

Provides integration with Interactive Brokers for live trading.

PREREQUISITES:
1. Install IB Trader Workstation (TWS) or IB Gateway
2. Enable API connections in TWS/Gateway settings
3. Set environment variables:
   - IBKR_HOST (default: 127.0.0.1)
   - IBKR_PORT (default: 7497 for TWS paper, 7496 for TWS live)
   - IBKR_CLIENT_ID (default: 1)

SAFETY:
- Always test with paper trading account first (port 7497)
- Live trading requires explicit confirmation
- Implement circuit breakers and risk limits
"""

import os
from decimal import Decimal
from typing import Any

try:
    from ib_insync import IB, Contract, LimitOrder, MarketOrder
    from ib_insync import Order as IBOrder
    from ib_insync import Stock
except ImportError:
    # Graceful degradation if ib_insync not installed
    IB = None  # type: ignore
    Contract = None  # type: ignore
    Stock = None  # type: ignore
    MarketOrder = None  # type: ignore
    LimitOrder = None  # type: ignore
    IBOrder = None  # type: ignore

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


class IBKRAdapter(BrokerBase):
    """Interactive Brokers adapter using ib_insync.

    Connects to TWS or IB Gateway for live/paper trading.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        client_id: int | None = None,
        paper_trading: bool = True,
    ) -> None:
        """Initialize IBKR adapter.

        Args:
            host: TWS/Gateway host (default: from env or 127.0.0.1)
            port: TWS/Gateway port (default: from env or 7497 for paper)
            client_id: Client ID (default: from env or 1)
            paper_trading: Whether using paper trading account

        Raises:
            ImportError: If ib_insync is not installed
        """
        super().__init__("IBKR")

        if IB is None:
            raise ImportError("ib_insync is not installed. Install with: pip install ib-insync")

        # Configuration
        self.host = host or os.getenv("IBKR_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("IBKR_PORT", "7497" if paper_trading else "7496"))
        self.client_id = client_id or int(os.getenv("IBKR_CLIENT_ID", "1"))
        self.paper_trading = paper_trading

        # IB connection
        self.ib = IB()

        # State tracking
        self._orders: dict[str, Order] = {}

        self.logger.info(
            f"Initialized IBKR adapter: {self.host}:{self.port} "
            f"(paper={paper_trading}, client_id={self.client_id})"
        )

    def connect(self) -> bool:
        """Connect to TWS/Gateway."""
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.logger.info(f"Connected to IBKR at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to connect to IBKR: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from TWS/Gateway."""
        if self.ib.isConnected():
            self.ib.disconnect()
            self.logger.info("Disconnected from IBKR")

    def is_connected(self) -> bool:
        """Check if connected to IBKR."""
        return self.ib.isConnected()

    def get_account(self) -> Account:
        """Get account information."""
        if not self.is_connected():
            raise RuntimeError("Not connected to IBKR")

        account_values = self.ib.accountValues()

        # Extract key values
        equity = Decimal("0")
        cash = Decimal("0")

        for av in account_values:
            if av.tag == "NetLiquidation":
                equity = Decimal(av.value)
            elif av.tag == "TotalCashValue":
                cash = Decimal(av.value)

        return Account(equity=equity, cash=cash)

    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        if not self.is_connected():
            raise RuntimeError("Not connected to IBKR")

        ib_positions = self.ib.positions()
        positions = []

        for ib_pos in ib_positions:
            positions.append(
                Position(
                    symbol=ib_pos.contract.symbol,
                    quantity=Decimal(str(ib_pos.position)),
                    avg_entry_price=(
                        Decimal(str(ib_pos.avgCost / ib_pos.position))
                        if ib_pos.position != 0
                        else Decimal("0")
                    ),
                    market_value=Decimal(str(ib_pos.marketValue)),
                    unrealized_pnl=Decimal(str(ib_pos.unrealizedPNL)),
                    current_price=Decimal(str(ib_pos.marketPrice)),
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
        """Place an order with IBKR."""
        if not self.is_connected():
            raise RuntimeError("Not connected to IBKR")

        # Validate parameters
        self.validate_order_params(symbol, side, quantity, order_type, limit_price, stop_price)

        # Create contract
        contract = Stock(symbol, "SMART", "USD")

        # Create IB order
        action = "BUY" if side == OrderSide.BUY else "SELL"

        if order_type == OrderType.MARKET:
            ib_order = MarketOrder(action, float(quantity))
        elif order_type == OrderType.LIMIT:
            ib_order = LimitOrder(action, float(quantity), float(limit_price))  # type: ignore
        else:
            raise ValueError(f"Order type {order_type} not yet implemented for IBKR")

        # Place order
        trade = self.ib.placeOrder(contract, ib_order)

        # Create our Order object
        order = Order(
            order_id=str(trade.order.orderId),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            status=OrderStatus.PENDING,
            limit_price=limit_price,
            stop_price=stop_price,
            strategy=strategy,
        )

        self._orders[order.order_id] = order

        self.logger.info(f"Placed order: {side.value} {quantity} {symbol}")

        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        try:
            self.ib.cancelOrder(int(order_id))  # type: ignore
            return True
        except Exception as e:
            self.logger.exception(f"Failed to cancel order {order_id}: {e}")
            return False

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
        """Get fills (executions)."""
        # Note: This is a simplified implementation
        # Full implementation would track all fills from IB
        return []
        # TODO: Implement fill tracking from IB executions

    def get_current_price(self, symbol: str) -> Decimal:
        """Get current market price."""
        if not self.is_connected():
            raise RuntimeError("Not connected to IBKR")

        contract = Stock(symbol, "SMART", "USD")
        ticker = self.ib.reqMktData(contract)
        self.ib.sleep(1)  # Wait for data

        if ticker.last > 0:
            return Decimal(str(ticker.last))
        if ticker.close > 0:
            return Decimal(str(ticker.close))

        raise ValueError(f"No price data available for {symbol}")

    def get_market_hours(self, symbol: str) -> dict[str, bool]:
        """Check if market is open."""
        # Simplified implementation
        # TODO: Query actual market hours from IB
        return {"is_open": True, "session": "regular"}
