"""
Tests for broker simulator (paper trading).
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.execution.broker_simulator import BrokerSimulator
from src.execution.order_types import OrderSide, OrderType, OrderStatus


@pytest.fixture
def broker():
    """Create a broker simulator instance."""
    return BrokerSimulator(
        initial_cash=Decimal('100000'),
        slippage_bps=1.5,
        commission_per_trade=Decimal('2.0')
    )


def test_broker_initialization(broker):
    """Test broker can be initialized."""
    assert broker is not None
    assert broker.broker_name == "Simulator"
    assert not broker.is_connected()


def test_broker_connect_disconnect(broker):
    """Test broker connection."""
    assert not broker.is_connected()

    broker.connect()
    assert broker.is_connected()

    broker.disconnect()
    assert not broker.is_connected()


def test_get_account_initial(broker):
    """Test getting initial account state."""
    broker.connect()
    account = broker.get_account()

    assert account.equity == Decimal('100000')
    assert account.cash == Decimal('100000')
    assert account.buying_power == Decimal('100000')
    assert account.total_pnl == Decimal('0')


def test_place_market_order_buy(broker):
    """Test placing a market buy order."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET
    )

    assert order is not None
    assert order.symbol == "AAPL"
    assert order.side == OrderSide.BUY
    assert order.quantity == Decimal('100')
    assert order.status == OrderStatus.FILLED


def test_place_market_order_sell(broker):
    """Test placing a market sell order."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    # First buy
    broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET
    )

    # Then sell
    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.SELL,
        quantity=Decimal('50'),
        order_type=OrderType.MARKET
    )

    assert order is not None
    assert order.side == OrderSide.SELL
    assert order.status == OrderStatus.FILLED


def test_get_positions_after_buy(broker):
    """Test getting positions after buying."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET
    )

    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "AAPL"
    assert positions[0].quantity == Decimal('100')


def test_get_positions_multiple_symbols(broker):
    """Test positions with multiple symbols."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price
    broker._mock_prices["MSFT"] = Decimal('300')  # Mock price

    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)
    broker.place_order("MSFT", OrderSide.BUY, Decimal('50'), OrderType.MARKET)

    positions = broker.get_positions()
    assert len(positions) == 2

    symbols = [p.symbol for p in positions]
    assert "AAPL" in symbols
    assert "MSFT" in symbols


def test_get_position_by_symbol(broker):
    """Test getting specific position."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    position = broker.get_position("AAPL")
    assert position is not None
    assert position.symbol == "AAPL"
    assert position.quantity == Decimal('100')

    # Non-existent position
    position = broker.get_position("NONEXISTENT")
    assert position is None


def test_slippage_applied(broker):
    """Test that slippage is applied to orders."""
    broker.connect()

    # Mock current price at $100
    broker._mock_prices["AAPL"] = Decimal('100')

    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET
    )

    # With 1.5 bps slippage, filled price should be slightly higher than $100
    # Slippage = 100 * 0.00015 = 0.015
    # Expected filled price: ~100.015
    assert order.filled_price > Decimal('100')


def test_commission_applied(broker):
    """Test that commission is deducted."""
    broker.connect()
    initial_cash = broker.get_account().cash

    broker._mock_prices["AAPL"] = Decimal('100')

    broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('10'),
        order_type=OrderType.MARKET
    )

    account = broker.get_account()

    # Cash should be reduced by: (10 shares * ~$100) + $2 commission
    # Should be approximately $1002 reduction
    cash_used = initial_cash - account.cash
    assert cash_used > Decimal('1000')  # At least the position value
    assert cash_used < Decimal('1010')  # Not too much more


def test_insufficient_funds(broker):
    """Test order rejection with insufficient funds."""
    broker.connect()

    # Try to buy $200k worth with $100k cash
    broker._mock_prices["AAPL"] = Decimal('1000')

    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('300'),
        order_type=OrderType.MARKET
    )

    # Should be rejected
    assert order.status == OrderStatus.REJECTED
    assert "Insufficient funds" in order.rejection_reason


def test_insufficient_position(broker):
    """Test sell rejection with insufficient position."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    # Try to sell without owning
    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.SELL,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET
    )

    assert order.status == OrderStatus.REJECTED
    assert "Insufficient position" in order.rejection_reason


def test_partial_position_tracking(broker):
    """Test position tracking with multiple orders."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    # Buy 100 shares
    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    # Buy 50 more
    broker.place_order("AAPL", OrderSide.BUY, Decimal('50'), OrderType.MARKET)

    position = broker.get_position("AAPL")
    assert position.quantity == Decimal('150')

    # Sell 75
    broker.place_order("AAPL", OrderSide.SELL, Decimal('75'), OrderType.MARKET)

    position = broker.get_position("AAPL")
    assert position.quantity == Decimal('75')


def test_close_entire_position(broker):
    """Test closing an entire position."""
    broker.connect()

    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)
    broker.place_order("AAPL", OrderSide.SELL, Decimal('100'), OrderType.MARKET)

    position = broker.get_position("AAPL")
    # Position should be None or have quantity 0
    assert position is None or position.quantity == Decimal('0')


def test_get_orders(broker):
    """Test getting order history."""
    broker.connect()

    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)
    broker.place_order("MSFT", OrderSide.BUY, Decimal('50'), OrderType.MARKET)

    orders = broker.get_orders()
    assert len(orders) >= 2


def test_get_order_by_id(broker):
    """Test getting specific order."""
    broker.connect()

    placed_order = broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    retrieved_order = broker.get_order(placed_order.order_id)
    assert retrieved_order is not None
    assert retrieved_order.order_id == placed_order.order_id


def test_cancel_order_not_supported(broker):
    """Test that canceling market orders is not supported."""
    broker.connect()

    order = broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    # Should not be able to cancel filled order
    result = broker.cancel_order(order.order_id)
    assert not result


def test_current_price_fetching(broker):
    """Test getting current price."""
    broker.connect()

    # Set mock price
    broker._mock_prices["AAPL"] = Decimal('150.50')

    price = broker.get_current_price("AAPL")
    assert price == Decimal('150.50')


def test_ledger_persistence(broker, tmp_path):
    """Test that ledger is saved."""
    import os

    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price
    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    # Ledger should have entries
    assert len(broker.ledger) > 0


def test_stop_loss_and_take_profit(broker):
    """Test orders with stop loss and take profit."""
    broker.connect()

    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET,
        stop_loss=Decimal('95'),
        take_profit=Decimal('110')
    )

    assert order.stop_loss == Decimal('95')
    assert order.take_profit == Decimal('110')


def test_buying_power_calculation(broker):
    """Test buying power after trades."""
    broker.connect()

    initial_bp = broker.get_account().buying_power

    broker._mock_prices["AAPL"] = Decimal('100')
    broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    account = broker.get_account()

    # Buying power should be reduced
    assert account.buying_power < initial_bp


def test_multiple_fills_same_order(broker):
    """Test that orders create fill records."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    order = broker.place_order("AAPL", OrderSide.BUY, Decimal('100'), OrderType.MARKET)

    # Should have at least one fill
    assert len(order.fills) > 0
    assert order.fills[0].quantity == Decimal('100')


def test_order_metadata(broker):
    """Test order metadata storage."""
    broker.connect()
    broker._mock_prices["AAPL"] = Decimal('150')  # Mock price

    order = broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        order_type=OrderType.MARKET,
        strategy="test_strategy",
        signal_confidence=0.85
    )

    assert order.strategy == "test_strategy"
    assert order.signal_confidence == 0.85


def test_simulator_with_zero_commission(broker):
    """Test simulator with no commission."""
    broker_no_commission = BrokerSimulator(
        initial_cash=Decimal('100000'),
        commission_per_trade=Decimal('0')
    )
    broker_no_commission.connect()

    initial_cash = broker_no_commission.get_account().cash

    broker_no_commission._mock_prices["AAPL"] = Decimal('100')
    broker_no_commission.place_order("AAPL", OrderSide.BUY, Decimal('10'), OrderType.MARKET)

    account = broker_no_commission.get_account()

    # Cash reduction should be close to exactly $1000 (10 * $100) plus small slippage
    cash_used = initial_cash - account.cash
    assert Decimal('999') < cash_used < Decimal('1005')
