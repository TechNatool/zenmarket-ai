"""Comprehensive tests for IBKRAdapter module."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.execution.order_types import OrderSide, OrderStatus, OrderType


class TestIBKRAdapterImportError:
    """Test IBKR adapter when ib_insync is not installed."""

    @patch("src.brokers.ibkr_adapter.IB", None)
    def test_initialization_without_ib_insync(self):
        """Test initialization raises ImportError when ib_insync not installed."""
        # Clear module cache to force re-import
        import sys

        if "src.brokers.ibkr_adapter" in sys.modules:
            del sys.modules["src.brokers.ibkr_adapter"]

        # Re-import with IB = None
        with patch.dict("sys.modules", {"ib_insync": None}):
            from src.brokers.ibkr_adapter import IBKRAdapter

            # Should raise ImportError
            with pytest.raises(ImportError, match="ib_insync is not installed"):
                IBKRAdapter()


class TestIBKRAdapterInitialization:
    """Test IBKR adapter initialization."""

    @patch("src.brokers.ibkr_adapter.IB")
    def test_initialization_default_params(self, mock_ib_class):
        """Test initialization with default parameters."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        assert adapter.broker_name == "IBKR"
        assert adapter.host == "127.0.0.1"
        assert adapter.port == 7497  # Paper trading default
        assert adapter.client_id == 1
        assert adapter.paper_trading is True

    @patch("src.brokers.ibkr_adapter.IB")
    def test_initialization_custom_params(self, mock_ib_class):
        """Test initialization with custom parameters."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter(host="192.168.1.100", port=4001, client_id=5, paper_trading=False)

        assert adapter.host == "192.168.1.100"
        assert adapter.port == 4001
        assert adapter.client_id == 5
        assert adapter.paper_trading is False

    @patch("src.brokers.ibkr_adapter.IB")
    @patch.dict("os.environ", {"IBKR_HOST": "localhost", "IBKR_PORT": "7496", "IBKR_CLIENT_ID": "3"})
    def test_initialization_from_env(self, mock_ib_class):
        """Test initialization from environment variables."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        assert adapter.host == "localhost"
        assert adapter.port == 7496
        assert adapter.client_id == 3


class TestConnectionMethods:
    """Test connection methods."""

    @patch("src.brokers.ibkr_adapter.IB")
    def test_connect_success(self, mock_ib_class):
        """Test successful connection."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.connect.return_value = None
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        result = adapter.connect()

        assert result is True
        mock_ib_instance.connect.assert_called_once_with("127.0.0.1", 7497, clientId=1)

    @patch("src.brokers.ibkr_adapter.IB")
    def test_connect_failure(self, mock_ib_class):
        """Test connection failure."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.connect.side_effect = Exception("Connection refused")
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        result = adapter.connect()

        assert result is False

    @patch("src.brokers.ibkr_adapter.IB")
    def test_disconnect(self, mock_ib_class):
        """Test disconnection."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        adapter.disconnect()

        mock_ib_instance.disconnect.assert_called_once()

    @patch("src.brokers.ibkr_adapter.IB")
    def test_disconnect_not_connected(self, mock_ib_class):
        """Test disconnection when not connected."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = False
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        adapter.disconnect()

        # Should not call disconnect if not connected
        mock_ib_instance.disconnect.assert_not_called()

    @patch("src.brokers.ibkr_adapter.IB")
    def test_is_connected(self, mock_ib_class):
        """Test is_connected method."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        assert adapter.is_connected() is True


class TestAccountMethods:
    """Test account-related methods."""

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_account_success(self, mock_ib_class):
        """Test getting account information."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock account values
        account_value1 = Mock()
        account_value1.tag = "NetLiquidation"
        account_value1.value = "100000.50"

        account_value2 = Mock()
        account_value2.tag = "TotalCashValue"
        account_value2.value = "50000.25"

        mock_ib_instance.accountValues.return_value = [account_value1, account_value2]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        account = adapter.get_account()

        assert account.equity == Decimal("100000.50")
        assert account.cash == Decimal("50000.25")

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_account_not_connected(self, mock_ib_class):
        """Test get_account raises error when not connected."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = False
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(RuntimeError, match="Not connected to IBKR"):
            adapter.get_account()


class TestPositionMethods:
    """Test position-related methods."""

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_positions_success(self, mock_ib_class):
        """Test getting positions."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock IB position
        mock_contract = Mock()
        mock_contract.symbol = "AAPL"

        mock_ib_position = Mock()
        mock_ib_position.contract = mock_contract
        mock_ib_position.position = 100.0
        mock_ib_position.avgCost = 15000.0
        mock_ib_position.marketValue = 15500.0
        mock_ib_position.unrealizedPNL = 500.0
        mock_ib_position.marketPrice = 155.0

        mock_ib_instance.positions.return_value = [mock_ib_position]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        positions = adapter.get_positions()

        assert len(positions) == 1
        assert positions[0].symbol == "AAPL"
        assert positions[0].quantity == Decimal("100.0")
        assert positions[0].avg_entry_price == Decimal("150.0")  # 15000/100

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_positions_zero_position(self, mock_ib_class):
        """Test getting position with zero quantity."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock IB position with zero quantity
        mock_contract = Mock()
        mock_contract.symbol = "AAPL"

        mock_ib_position = Mock()
        mock_ib_position.contract = mock_contract
        mock_ib_position.position = 0.0  # Zero position
        mock_ib_position.avgCost = 0.0
        mock_ib_position.marketValue = 0.0
        mock_ib_position.unrealizedPNL = 0.0
        mock_ib_position.marketPrice = 150.0

        mock_ib_instance.positions.return_value = [mock_ib_position]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        positions = adapter.get_positions()

        assert len(positions) == 1
        assert positions[0].avg_entry_price == Decimal("0")  # Should handle division by zero

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_positions_not_connected(self, mock_ib_class):
        """Test get_positions raises error when not connected."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = False
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(RuntimeError, match="Not connected to IBKR"):
            adapter.get_positions()

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_position_found(self, mock_ib_class):
        """Test getting specific position."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock IB position
        mock_contract = Mock()
        mock_contract.symbol = "AAPL"

        mock_ib_position = Mock()
        mock_ib_position.contract = mock_contract
        mock_ib_position.position = 100.0
        mock_ib_position.avgCost = 15000.0
        mock_ib_position.marketValue = 15500.0
        mock_ib_position.unrealizedPNL = 500.0
        mock_ib_position.marketPrice = 155.0

        mock_ib_instance.positions.return_value = [mock_ib_position]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        position = adapter.get_position("AAPL")

        assert position is not None
        assert position.symbol == "AAPL"

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_position_not_found(self, mock_ib_class):
        """Test getting non-existent position."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True
        mock_ib_instance.positions.return_value = []
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        position = adapter.get_position("AAPL")

        assert position is None


class TestOrderPlacement:
    """Test order placement."""

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.MarketOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_place_market_order(self, mock_ib_class, mock_market_order, mock_stock):
        """Test placing a market order."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock trade response
        mock_trade = Mock()
        mock_trade.order.orderId = 12345
        mock_ib_instance.placeOrder.return_value = mock_trade

        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        order = adapter.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        assert order is not None
        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.quantity == Decimal("10")
        assert order.order_type == OrderType.MARKET
        assert order.order_id == "12345"
        assert order.status == OrderStatus.PENDING

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.LimitOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_place_limit_order(self, mock_ib_class, mock_limit_order, mock_stock):
        """Test placing a limit order."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock trade response
        mock_trade = Mock()
        mock_trade.order.orderId = 12346
        mock_ib_instance.placeOrder.return_value = mock_trade

        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        order = adapter.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("150.00"),
        )

        assert order is not None
        assert order.order_type == OrderType.LIMIT
        assert order.limit_price == Decimal("150.00")

    @patch("src.brokers.ibkr_adapter.IB")
    def test_place_order_not_connected(self, mock_ib_class):
        """Test place_order raises error when not connected."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = False
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(RuntimeError, match="Not connected to IBKR"):
            adapter.place_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=Decimal("10"),
                order_type=OrderType.MARKET,
            )

    @patch("src.brokers.ibkr_adapter.IB")
    def test_place_order_unsupported_type(self, mock_ib_class):
        """Test place_order raises error for unsupported order type."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(ValueError, match="Order type .* not yet implemented"):
            adapter.place_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=Decimal("10"),
                order_type=OrderType.STOP,
                stop_price=Decimal("145.00"),  # Provide stop_price to pass validation
            )


class TestOrderManagement:
    """Test order management methods."""

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.MarketOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_order(self, mock_ib_class, mock_market_order, mock_stock):
        """Test getting order by ID."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        mock_trade = Mock()
        mock_trade.order.orderId = 12345
        mock_ib_instance.placeOrder.return_value = mock_trade

        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        # Place order first
        order = adapter.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Retrieve order
        retrieved_order = adapter.get_order(order.order_id)

        assert retrieved_order is not None
        assert retrieved_order.order_id == order.order_id

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_order_not_found(self, mock_ib_class):
        """Test getting non-existent order."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        order = adapter.get_order("non-existent-id")

        assert order is None

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.MarketOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_orders_no_filter(self, mock_ib_class, mock_market_order, mock_stock):
        """Test getting all orders."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        mock_trade1 = Mock()
        mock_trade1.order.orderId = 12345

        mock_trade2 = Mock()
        mock_trade2.order.orderId = 12346

        mock_ib_instance.placeOrder.side_effect = [mock_trade1, mock_trade2]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        # Place two orders
        adapter.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        adapter.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        orders = adapter.get_orders()

        assert len(orders) == 2

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.MarketOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_orders_filter_by_symbol(self, mock_ib_class, mock_market_order, mock_stock):
        """Test getting orders filtered by symbol."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        mock_trade1 = Mock()
        mock_trade1.order.orderId = 12345

        mock_trade2 = Mock()
        mock_trade2.order.orderId = 12346

        mock_ib_instance.placeOrder.side_effect = [mock_trade1, mock_trade2]
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        # Place orders for different symbols
        adapter.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        adapter.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        orders = adapter.get_orders(symbol="AAPL")

        assert len(orders) == 1
        assert orders[0].symbol == "AAPL"

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.MarketOrder")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_orders_filter_by_status(self, mock_ib_class, mock_market_order, mock_stock):
        """Test getting orders filtered by status."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        mock_trade = Mock()
        mock_trade.order.orderId = 12345
        mock_ib_instance.placeOrder.return_value = mock_trade

        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        # Place order
        adapter.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        orders = adapter.get_orders(status=OrderStatus.PENDING)

        assert len(orders) == 1
        assert orders[0].status == OrderStatus.PENDING

    @patch("src.brokers.ibkr_adapter.IB")
    def test_cancel_order_success(self, mock_ib_class):
        """Test successful order cancellation."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.cancelOrder.return_value = None
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        result = adapter.cancel_order("12345")

        assert result is True
        mock_ib_instance.cancelOrder.assert_called_once_with(12345)

    @patch("src.brokers.ibkr_adapter.IB")
    def test_cancel_order_failure(self, mock_ib_class):
        """Test order cancellation failure."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.cancelOrder.side_effect = Exception("Order not found")
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        result = adapter.cancel_order("12345")

        assert result is False


class TestFillMethods:
    """Test fill-related methods."""

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_fills(self, mock_ib_class):
        """Test getting fills (currently returns empty list)."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        fills = adapter.get_fills()

        # Currently returns empty list (TODO in implementation)
        assert fills == []


class TestMarketDataMethods:
    """Test market data methods."""

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_current_price_with_last(self, mock_ib_class, mock_stock):
        """Test getting current price using last price."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock ticker data
        mock_ticker = Mock()
        mock_ticker.last = 150.5
        mock_ticker.close = 149.0

        mock_ib_instance.reqMktData.return_value = mock_ticker
        mock_ib_instance.sleep.return_value = None
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        price = adapter.get_current_price("AAPL")

        assert price == Decimal("150.5")

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_current_price_with_close(self, mock_ib_class, mock_stock):
        """Test getting current price using close price when last unavailable."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock ticker data with no last price
        mock_ticker = Mock()
        mock_ticker.last = 0  # No last price
        mock_ticker.close = 149.0

        mock_ib_instance.reqMktData.return_value = mock_ticker
        mock_ib_instance.sleep.return_value = None
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        price = adapter.get_current_price("AAPL")

        assert price == Decimal("149.0")

    @patch("src.brokers.ibkr_adapter.Stock")
    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_current_price_no_data(self, mock_ib_class, mock_stock):
        """Test getting current price with no data available."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = True

        # Mock ticker data with no price data
        mock_ticker = Mock()
        mock_ticker.last = 0
        mock_ticker.close = 0

        mock_ib_instance.reqMktData.return_value = mock_ticker
        mock_ib_instance.sleep.return_value = None
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(ValueError, match="No price data available"):
            adapter.get_current_price("AAPL")

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_current_price_not_connected(self, mock_ib_class):
        """Test get_current_price raises error when not connected."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_instance.isConnected.return_value = False
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()

        with pytest.raises(RuntimeError, match="Not connected to IBKR"):
            adapter.get_current_price("AAPL")

    @patch("src.brokers.ibkr_adapter.IB")
    def test_get_market_hours(self, mock_ib_class):
        """Test getting market hours (simplified implementation)."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        mock_ib_instance = Mock()
        mock_ib_class.return_value = mock_ib_instance

        adapter = IBKRAdapter()
        market_hours = adapter.get_market_hours("AAPL")

        assert market_hours["is_open"] is True
        assert market_hours["session"] == "regular"
