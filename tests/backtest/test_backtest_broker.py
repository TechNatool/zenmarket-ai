"""Tests for BacktestBroker."""

from datetime import datetime
from decimal import Decimal

import pandas as pd
import pytest

from src.backtest.backtest_broker import BacktestBroker
from src.execution.order_types import OrderSide, OrderType


@pytest.fixture
def sample_historical_data():
    """Create sample historical data for testing."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    data = {
        "AAPL": pd.DataFrame(
            {
                "Open": [150.0 + i for i in range(10)],
                "High": [152.0 + i for i in range(10)],
                "Low": [149.0 + i for i in range(10)],
                "Close": [151.0 + i for i in range(10)],
                "Volume": [1000000] * 10,
            },
            index=dates,
        )
    }
    return data


@pytest.fixture
def backtest_broker(sample_historical_data):
    """Create a backtest broker instance."""
    return BacktestBroker(
        historical_data=sample_historical_data,
        initial_cash=Decimal("100000"),
        slippage_bps=1.5,
        commission_per_trade=Decimal("2.0"),
    )


def test_broker_initialization(backtest_broker):
    """Test broker initializes correctly."""
    assert backtest_broker is not None
    assert backtest_broker.broker_name == "BacktestBroker"
    assert backtest_broker._account.cash == Decimal("100000")
    assert backtest_broker._account.equity == Decimal("100000")


def test_connect_disconnect(backtest_broker):
    """Test connection methods."""
    assert backtest_broker.connect() is True
    assert backtest_broker.is_connected() is True
    
    backtest_broker.disconnect()
    assert backtest_broker.is_connected() is False


def test_set_current_bar(backtest_broker, sample_historical_data):
    """Test setting current bar data."""
    timestamp = sample_historical_data["AAPL"].index[0]
    bar_data = {
        "AAPL": {
            "Open": 150.0,
            "High": 152.0,
            "Low": 149.0,
            "Close": 151.0,
            "Volume": 1000000,
        }
    }
    
    backtest_broker.set_current_bar(timestamp, bar_data)
    
    assert backtest_broker.current_timestamp == timestamp
    assert backtest_broker._current_bar == bar_data


def test_place_market_order(backtest_broker, sample_historical_data):
    """Test placing a market order."""
    backtest_broker.connect()
    
    # Set current bar
    timestamp = sample_historical_data["AAPL"].index[0]
    bar_data = {
        "AAPL": {
            "Open": 150.0,
            "High": 152.0,
            "Low": 149.0,
            "Close": 151.0,
            "Volume": 1000000,
        }
    }
    backtest_broker.set_current_bar(timestamp, bar_data)
    
    # Place buy order
    order = backtest_broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal("10"),
        order_type=OrderType.MARKET,
    )
    
    assert order is not None
    assert order.symbol == "AAPL"
    assert order.side == OrderSide.BUY
    assert order.quantity == Decimal("10")
    
    # Check position was created
    position = backtest_broker.get_position("AAPL")
    assert position is not None
    assert position.quantity == Decimal("10")


def test_account_updates_after_trade(backtest_broker, sample_historical_data):
    """Test account equity updates after trade."""
    backtest_broker.connect()
    
    initial_cash = backtest_broker._account.cash
    
    # Set current bar
    timestamp = sample_historical_data["AAPL"].index[0]
    bar_data = {
        "AAPL": {
            "Open": 150.0,
            "High": 152.0,
            "Low": 149.0,
            "Close": 151.0,
            "Volume": 1000000,
        }
    }
    backtest_broker.set_current_bar(timestamp, bar_data)
    
    # Place buy order
    backtest_broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal("10"),
        order_type=OrderType.MARKET,
    )
    
    # Cash should decrease (price * quantity + commission + slippage)
    assert backtest_broker._account.cash < initial_cash
    
    # Equity should include position value
    assert backtest_broker._account.equity > 0


def test_insufficient_funds(backtest_broker, sample_historical_data):
    """Test order rejection with insufficient funds."""
    backtest_broker.connect()
    
    # Set current bar
    timestamp = sample_historical_data["AAPL"].index[0]
    bar_data = {
        "AAPL": {
            "Open": 150.0,
            "High": 152.0,
            "Low": 149.0,
            "Close": 151.0,
            "Volume": 1000000,
        }
    }
    backtest_broker.set_current_bar(timestamp, bar_data)
    
    # Try to buy more than we can afford
    order = backtest_broker.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal("10000"),  # Way too many shares
        order_type=OrderType.MARKET,
    )
    
    # Order should be rejected
    from src.execution.order_types import OrderStatus
    assert order.status == OrderStatus.REJECTED
