"""Extended tests for BacktestBroker to improve coverage."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.backtest.backtest_broker import BacktestBroker
from src.execution.order_types import OrderSide, OrderStatus, OrderType, Position


@pytest.fixture
def sample_historical_data():
    """Create sample historical data for testing."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    return {
        "AAPL": pd.DataFrame(
            {
                "Open": [150.0 + i for i in range(10)],
                "High": [152.0 + i for i in range(10)],
                "Low": [149.0 + i for i in range(10)],
                "Close": [151.0 + i for i in range(10)],
                "Volume": [1000000] * 10,
            },
            index=dates,
        ),
        "GOOGL": pd.DataFrame(
            {
                "Open": [100.0 + i for i in range(10)],
                "High": [102.0 + i for i in range(10)],
                "Low": [99.0 + i for i in range(10)],
                "Close": [101.0 + i for i in range(10)],
                "Volume": [500000] * 10,
            },
            index=dates,
        ),
    }


@pytest.fixture
def backtest_broker(sample_historical_data):
    """Create a backtest broker instance."""
    return BacktestBroker(
        historical_data=sample_historical_data,
        initial_cash=Decimal("100000"),
        slippage_bps=1.5,
        commission_per_trade=Decimal("2.0"),
    )


class TestAccountMethods:
    """Test account-related methods."""

    def test_get_account(self, backtest_broker):
        """Test get_account returns current account state."""
        account = backtest_broker.get_account()
        assert account.cash == Decimal("100000")
        assert account.equity == Decimal("100000")

    def test_get_equity(self, backtest_broker):
        """Test get_equity returns current equity."""
        equity = backtest_broker.get_equity()
        assert equity == Decimal("100000")

    def test_get_cash(self, backtest_broker):
        """Test get_cash returns current cash balance."""
        cash = backtest_broker.get_cash()
        assert cash == Decimal("100000")


class TestPositionMethods:
    """Test position-related methods."""

    def test_get_positions_empty(self, backtest_broker):
        """Test get_positions returns empty list when no positions."""
        positions = backtest_broker.get_positions()
        assert positions == []

    def test_get_positions_with_positions(self, backtest_broker, sample_historical_data):
        """Test get_positions returns only non-zero positions."""
        # Set current bar
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place buy order to create position
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        positions = backtest_broker.get_positions()
        assert len(positions) == 1
        assert positions[0].symbol == "AAPL"
        assert positions[0].quantity == Decimal("10")

    def test_get_position_not_exists(self, backtest_broker):
        """Test get_position returns None when position doesn't exist."""
        position = backtest_broker.get_position("AAPL")
        assert position is None

    def test_get_position_zero_quantity(self, backtest_broker):
        """Test get_position returns None for zero quantity position."""
        # Create position with zero quantity
        backtest_broker._positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=Decimal("0"),
            avg_entry_price=Decimal("150"),
            unrealized_pnl=Decimal("0"),
            current_price=Decimal("151"),
        )

        position = backtest_broker.get_position("AAPL")
        assert position is None


class TestPriceHandling:
    """Test price handling methods."""

    def test_get_current_bar_price_missing_symbol(self, backtest_broker, sample_historical_data):
        """Test _get_current_bar_price raises error for missing symbol."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        with pytest.raises(ValueError, match="No data for symbol MISSING"):
            backtest_broker._get_current_bar_price("MISSING", "Close")

    def test_get_current_bar_price_missing_price_type(
        self, backtest_broker, sample_historical_data
    ):
        """Test _get_current_bar_price raises error for missing price type."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        with pytest.raises(ValueError, match="Price type Invalid not found"):
            backtest_broker._get_current_bar_price("AAPL", "Invalid")

    def test_get_current_price(self, backtest_broker, sample_historical_data):
        """Test get_current_price returns close price."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        price = backtest_broker.get_current_price("AAPL")
        assert price == Decimal("151.0")


class TestPositionUpdates:
    """Test position update logic."""

    def test_update_positions_with_existing_position(
        self, backtest_broker, sample_historical_data
    ):
        """Test _update_positions updates existing positions."""
        # Set initial bar and create position
        timestamp1 = sample_historical_data["AAPL"].index[0]
        bar_data1 = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp1, bar_data1)

        # Place buy order
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Update to new bar with different price
        timestamp2 = sample_historical_data["AAPL"].index[1]
        bar_data2 = {
            "AAPL": {"Open": 151.0, "High": 153.0, "Low": 150.0, "Close": 152.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp2, bar_data2)

        # Check position was updated
        position = backtest_broker.get_position("AAPL")
        assert position.current_price == Decimal("152.0")
        assert position.unrealized_pnl > Decimal("0")  # Price increased


class TestSellOrders:
    """Test sell order scenarios."""

    def test_sell_order_insufficient_shares(self, backtest_broker, sample_historical_data):
        """Test sell order is rejected with insufficient shares."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Try to sell without any position
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        assert order.status == OrderStatus.REJECTED

    def test_sell_order_insufficient_quantity(self, backtest_broker, sample_historical_data):
        """Test sell order is rejected when trying to sell more than owned."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Buy 10 shares
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Try to sell 20 shares
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=Decimal("20"), order_type=OrderType.MARKET
        )

        assert order.status == OrderStatus.REJECTED

    def test_sell_order_success(self, backtest_broker, sample_historical_data):
        """Test successful sell order."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Buy 10 shares
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        initial_cash = backtest_broker.get_cash()

        # Sell 5 shares
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        assert order.status == OrderStatus.FILLED
        # Cash should increase after sell
        assert backtest_broker.get_cash() > initial_cash

        # Position should be reduced
        position = backtest_broker.get_position("AAPL")
        assert position.quantity == Decimal("5")

    def test_sell_order_close_position(self, backtest_broker, sample_historical_data):
        """Test selling entire position closes it."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Buy 10 shares
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Sell all 10 shares
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        assert order.status == OrderStatus.FILLED

        # Position should be closed (None or zero quantity)
        position = backtest_broker.get_position("AAPL")
        assert position is None


class TestLimitOrders:
    """Test limit order handling."""

    def test_limit_order_not_executed_immediately(self, backtest_broker, sample_historical_data):
        """Test limit orders are not executed immediately."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place limit order
        order = backtest_broker.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("150.0"),
        )

        # Limit orders should stay PENDING (not filled immediately)
        assert order.status == OrderStatus.PENDING


class TestOrderManagement:
    """Test order management methods."""

    def test_get_order(self, backtest_broker, sample_historical_data):
        """Test get_order retrieves order by ID."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place order
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Retrieve order
        retrieved_order = backtest_broker.get_order(order.order_id)
        assert retrieved_order is not None
        assert retrieved_order.order_id == order.order_id

    def test_get_order_not_found(self, backtest_broker):
        """Test get_order returns None for non-existent order."""
        order = backtest_broker.get_order("non-existent-id")
        assert order is None

    def test_get_orders_no_filter(self, backtest_broker, sample_historical_data):
        """Test get_orders returns all orders."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
            "GOOGL": {"Open": 100.0, "High": 102.0, "Low": 99.0, "Close": 101.0, "Volume": 500000},
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place multiple orders
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        backtest_broker.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        orders = backtest_broker.get_orders()
        assert len(orders) == 2

    def test_get_orders_filter_by_symbol(self, backtest_broker, sample_historical_data):
        """Test get_orders filters by symbol."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
            "GOOGL": {"Open": 100.0, "High": 102.0, "Low": 99.0, "Close": 101.0, "Volume": 500000},
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place orders for different symbols
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        backtest_broker.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        orders = backtest_broker.get_orders(symbol="AAPL")
        assert len(orders) == 1
        assert orders[0].symbol == "AAPL"

    def test_get_orders_filter_by_status(self, backtest_broker, sample_historical_data):
        """Test get_orders filters by status."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place market order (will be filled)
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Place limit order (will stay pending)
        backtest_broker.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("140.0"),
        )

        filled_orders = backtest_broker.get_orders(status=OrderStatus.FILLED)
        assert len(filled_orders) == 1
        assert filled_orders[0].status == OrderStatus.FILLED

        pending_orders = backtest_broker.get_orders(status=OrderStatus.PENDING)
        assert len(pending_orders) == 1
        assert pending_orders[0].status == OrderStatus.PENDING


class TestFills:
    """Test fill management methods."""

    def test_get_fills_no_filter(self, backtest_broker, sample_historical_data):
        """Test get_fills returns all fills."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
            "GOOGL": {"Open": 100.0, "High": 102.0, "Low": 99.0, "Close": 101.0, "Volume": 500000},
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place orders
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        backtest_broker.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        fills = backtest_broker.get_fills()
        assert len(fills) == 2

    def test_get_fills_filter_by_symbol(self, backtest_broker, sample_historical_data):
        """Test get_fills filters by symbol."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
            "GOOGL": {"Open": 100.0, "High": 102.0, "Low": 99.0, "Close": 101.0, "Volume": 500000},
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place orders
        backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )
        backtest_broker.place_order(
            symbol="GOOGL", side=OrderSide.BUY, quantity=Decimal("5"), order_type=OrderType.MARKET
        )

        fills = backtest_broker.get_fills(symbol="AAPL")
        assert len(fills) == 1
        assert fills[0].symbol == "AAPL"

    def test_get_fills_filter_by_order_id(self, backtest_broker, sample_historical_data):
        """Test get_fills filters by order_id."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place order
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        fills = backtest_broker.get_fills(order_id=order.order_id)
        assert len(fills) == 1
        assert fills[0].order_id == order.order_id


class TestCancelOrder:
    """Test order cancellation."""

    def test_cancel_order_success(self, backtest_broker, sample_historical_data):
        """Test successful order cancellation."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place limit order (stays PENDING)
        order = backtest_broker.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("140.0"),
        )

        # Cancel order
        result = backtest_broker.cancel_order(order.order_id)
        assert result is True
        assert order.status == OrderStatus.CANCELLED

    def test_cancel_order_not_found(self, backtest_broker):
        """Test cancelling non-existent order returns False."""
        result = backtest_broker.cancel_order("non-existent-id")
        assert result is False

    def test_cancel_order_already_filled(self, backtest_broker, sample_historical_data):
        """Test cannot cancel already filled order."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place market order (gets filled immediately)
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Try to cancel filled order
        result = backtest_broker.cancel_order(order.order_id)
        assert result is False

    def test_cancel_order_already_cancelled(self, backtest_broker, sample_historical_data):
        """Test cannot cancel already cancelled order."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Place limit order
        order = backtest_broker.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
            order_type=OrderType.LIMIT,
            limit_price=Decimal("140.0"),
        )

        # Cancel once
        backtest_broker.cancel_order(order.order_id)

        # Try to cancel again
        result = backtest_broker.cancel_order(order.order_id)
        assert result is False

    def test_cancel_order_already_rejected(self, backtest_broker, sample_historical_data):
        """Test cannot cancel already rejected order."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Try to sell without position (gets rejected)
        order = backtest_broker.place_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=Decimal("10"), order_type=OrderType.MARKET
        )

        # Try to cancel rejected order
        result = backtest_broker.cancel_order(order.order_id)
        assert result is False


class TestMarketHours:
    """Test market hours method."""

    def test_get_market_hours(self, backtest_broker):
        """Test get_market_hours always returns open for backtest."""
        market_hours = backtest_broker.get_market_hours("AAPL")
        assert market_hours["is_open"] is True
        assert market_hours["session"] == "backtest"


class TestExceptionHandling:
    """Test exception handling in order execution."""

    def test_order_execution_exception(self, backtest_broker, sample_historical_data):
        """Test order execution handles exceptions gracefully."""
        timestamp = sample_historical_data["AAPL"].index[0]
        bar_data = {
            "AAPL": {"Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000}
        }
        backtest_broker.set_current_bar(timestamp, bar_data)

        # Mock _get_current_bar_price to raise exception
        with patch.object(
            backtest_broker,
            "_get_current_bar_price",
            side_effect=Exception("Unexpected error"),
        ):
            order = backtest_broker.place_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=Decimal("10"),
                order_type=OrderType.MARKET,
            )

            # Order should be rejected due to exception
            assert order.status == OrderStatus.REJECTED
