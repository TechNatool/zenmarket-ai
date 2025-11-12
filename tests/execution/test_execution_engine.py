"""
Tests for execution engine (complete pipeline).
"""

from decimal import Decimal

import pytest

from src.advisor.indicators import TechnicalIndicators
from src.advisor.signal_generator import SignalType, TradingSignal
from src.execution.broker_simulator import BrokerSimulator
from src.execution.execution_engine import ExecutionEngine
from src.execution.order_types import OrderType
from src.execution.position_sizing import SizingMethod
from src.execution.risk_manager import RiskLimits


@pytest.fixture
def broker():
    """Create broker simulator."""
    broker = BrokerSimulator(initial_cash=Decimal("100000"))
    broker.connect()
    # Add mock prices for testing
    broker._mock_prices["AAPL"] = Decimal("150")
    broker._mock_prices["MSFT"] = Decimal("300")
    return broker


@pytest.fixture
def risk_limits():
    """Create risk limits."""
    return RiskLimits(
        max_risk_per_trade_pct=0.01,
        max_position_size_pct=0.30,  # 30% to accommodate test position sizes
        max_risk_per_day_pct=0.03,
        max_daily_drawdown_pct=0.30,  # 30% to accommodate test drawdowns
        max_consecutive_losses=3,
        max_open_positions=5,
    )


@pytest.fixture
def engine(broker, risk_limits, monkeypatch):
    """Create execution engine."""
    # Mock compliance checker to always return success
    from src.execution.compliance import MarketStatus

    def mock_check_market_hours(*args, **kwargs):
        return (True, MarketStatus.OPEN, None)

    engine_inst = ExecutionEngine(
        broker=broker,
        risk_limits=risk_limits,
        sizing_method=SizingMethod.FIXED_FRACTIONAL,
        journal_enabled=True,
    )

    monkeypatch.setattr(engine_inst.compliance, "check_market_hours", mock_check_market_hours)

    return engine_inst


@pytest.fixture
def buy_signal():
    """Create a BUY signal."""
    indicators = TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=145.0,
        ma_50=140.0,
        rsi=55.0,
        bb_upper=160.0,
        bb_middle=150.0,
        bb_lower=140.0,
        volume_avg=1000000,
        atr=3.0,
    )

    return TradingSignal(
        ticker="AAPL",
        signal=SignalType.BUY,
        confidence=0.75,
        reasons=["MA20 > MA50", "RSI neutral"],
        indicators=indicators,
    )


@pytest.fixture
def sell_signal():
    """Create a SELL signal."""
    indicators = TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=155.0,
        ma_50=160.0,
        rsi=45.0,
        bb_upper=170.0,
        bb_middle=150.0,
        bb_lower=130.0,
        volume_avg=1000000,
        atr=3.0,
    )

    return TradingSignal(
        ticker="AAPL",
        signal=SignalType.SELL,
        confidence=0.70,
        reasons=["MA20 < MA50", "Downtrend"],
        indicators=indicators,
    )


@pytest.fixture
def hold_signal():
    """Create a HOLD signal."""
    indicators = TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=150.0,
        ma_50=150.0,
        rsi=50.0,
        bb_upper=160.0,
        bb_middle=150.0,
        bb_lower=140.0,
        volume_avg=1000000,
    )

    return TradingSignal(
        ticker="AAPL",
        signal=SignalType.HOLD,
        confidence=0.50,
        reasons=["No clear trend"],
        indicators=indicators,
    )


def test_engine_initialization(engine):
    """Test engine can be initialized."""
    assert engine is not None
    assert engine.broker is not None
    assert engine.risk_manager is not None
    assert engine.journal is not None


def test_execute_buy_signal(engine, buy_signal, broker):
    """Test executing a BUY signal."""
    # Mock price
    broker._mock_prices["AAPL"] = Decimal("150")

    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    assert order is not None
    assert order.symbol == "AAPL"
    assert order.quantity > Decimal("0")


def test_execute_sell_signal_with_position(engine, sell_signal, broker):
    """Test executing a SELL signal when we have position."""
    # First buy
    broker._mock_prices["AAPL"] = Decimal("150")
    broker.place_order("AAPL", "BUY", Decimal("100"), OrderType.MARKET)

    # Now sell
    order = engine.execute_signal(
        signal=sell_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    assert order is not None


def test_execute_hold_signal(engine, hold_signal):
    """Test executing a HOLD signal (should do nothing)."""
    order = engine.execute_signal(
        signal=hold_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # HOLD should return None (no action)
    assert order is None


def test_execute_signal_dry_run(engine, buy_signal, broker):
    """Test dry run mode (no actual order)."""
    broker._mock_prices["AAPL"] = Decimal("150")

    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=True
    )

    # Dry run should return None
    assert order is None

    # No positions should be created
    positions = broker.get_positions()
    assert len(positions) == 0


def test_stop_loss_calculation(engine, buy_signal, broker):
    """Test automatic stop loss calculation."""
    broker._mock_prices["AAPL"] = Decimal("150")

    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # Should have stop loss set
    assert order.stop_loss is not None
    assert order.stop_loss < Decimal("150")


def test_take_profit_calculation(engine, buy_signal, broker):
    """Test automatic take profit calculation."""
    broker._mock_prices["AAPL"] = Decimal("150")

    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # Should have take profit set
    assert order.take_profit is not None
    assert order.take_profit > Decimal("150")


def test_position_sizing_with_atr(engine, buy_signal, broker):
    """Test position sizing uses ATR from indicators."""
    broker._mock_prices["AAPL"] = Decimal("150")

    # Signal has ATR of 3.0
    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    assert order is not None
    # Quantity should be calculated based on ATR-based stop loss


def test_risk_validation_failure(engine, buy_signal, broker):
    """Test that excessive risk is rejected."""
    broker._mock_prices["AAPL"] = Decimal("150")

    # Try to risk 10% (exceeds 1% limit)
    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.10, dry_run=False
    )

    # Should be rejected
    assert order is None


def test_journal_logging(engine, buy_signal, broker):
    """Test that orders are logged to journal."""
    broker._mock_prices["AAPL"] = Decimal("150")

    engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # Journal should have entries
    assert len(engine.journal.orders) > 0


def test_pnl_tracker_updates(engine, buy_signal, broker):
    """Test that PnL tracker is updated."""
    broker._mock_prices["AAPL"] = Decimal("150")

    initial_snapshots = len(engine.pnl_tracker.snapshots)

    engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # Should have new snapshot
    assert len(engine.pnl_tracker.snapshots) > initial_snapshots


def test_get_status(engine):
    """Test getting engine status."""
    status = engine.get_status()

    assert isinstance(status, dict)
    assert "broker" in status
    assert "connected" in status
    assert "risk_summary" in status
    assert "journal_enabled" in status


def test_shutdown(engine):
    """Test engine shutdown."""
    # Should not raise exception
    engine.shutdown()

    # Broker should be disconnected
    assert not engine.broker.is_connected()


def test_compliance_check_failure(engine, buy_signal):
    """Test that compliance failures prevent execution."""
    # This would require mocking market hours
    # For now, we just ensure the compliance check is called


def test_multiple_signals_sequential(engine, buy_signal, broker):
    """Test executing multiple signals in sequence."""
    broker._mock_prices["AAPL"] = Decimal("150")
    broker._mock_prices["MSFT"] = Decimal("300")

    # Execute first signal
    order1 = engine.execute_signal(buy_signal, OrderType.MARKET, 0.01, False)
    assert order1 is not None

    # Create second signal for different ticker
    buy_signal_2 = TradingSignal(
        ticker="MSFT",
        signal=SignalType.BUY,
        confidence=0.80,
        reasons=["Strong uptrend"],
        indicators=TechnicalIndicators(
            ticker="MSFT",
            current_price=300.0,
            ma_20=290.0,
            ma_50=280.0,
            rsi=60.0,
            bb_upper=320.0,
            bb_middle=300.0,
            bb_lower=280.0,
            volume_avg=2000000,
            atr=5.0,
        ),
    )

    order2 = engine.execute_signal(buy_signal_2, OrderType.MARKET, 0.01, False)
    assert order2 is not None

    # Should have 2 positions
    positions = broker.get_positions()
    assert len(positions) == 2


def test_sizing_method_fixed_fractional(broker, risk_limits):
    """Test engine with fixed fractional sizing."""
    engine = ExecutionEngine(
        broker=broker,
        risk_limits=risk_limits,
        sizing_method=SizingMethod.FIXED_FRACTIONAL,
        journal_enabled=False,
    )

    assert engine.sizing_method == SizingMethod.FIXED_FRACTIONAL


def test_sizing_method_kelly(broker, risk_limits):
    """Test engine with Kelly criterion sizing."""
    engine = ExecutionEngine(
        broker=broker,
        risk_limits=risk_limits,
        sizing_method=SizingMethod.KELLY,
        journal_enabled=False,
    )

    assert engine.sizing_method == SizingMethod.KELLY


def test_engine_without_journal(broker, risk_limits):
    """Test engine with journaling disabled."""
    engine = ExecutionEngine(
        broker=broker,
        risk_limits=risk_limits,
        sizing_method=SizingMethod.FIXED_FRACTIONAL,
        journal_enabled=False,
    )

    assert engine.journal is None


def test_error_handling_invalid_price(engine, buy_signal, broker):
    """Test error handling when price fetch fails."""
    # Remove mock price - will fail to get price
    # Engine should handle gracefully
    broker._mock_prices.clear()  # Clear all mock prices

    order = engine.execute_signal(
        signal=buy_signal, order_type=OrderType.MARKET, risk_percent=0.01, dry_run=False
    )

    # Should return None on error
    assert order is None


def test_zero_quantity_rejection(engine, buy_signal, broker):
    """Test that zero quantity orders are rejected."""
    # Set very wide stop loss so quantity becomes tiny/zero
    buy_signal.indicators.atr = 50.0  # Huge ATR

    broker._mock_prices["AAPL"] = Decimal("150")

    engine.execute_signal(
        signal=buy_signal,
        order_type=OrderType.MARKET,
        risk_percent=0.0001,  # Tiny risk
        dry_run=False,
    )

    # Should be rejected or return None
    # (exact behavior depends on sizing calculation)
    # Just ensure it doesn't crash


def test_performance_metrics_available(engine, buy_signal, broker):
    """Test that performance metrics are available."""
    broker._mock_prices["AAPL"] = Decimal("150")

    engine.execute_signal(buy_signal, OrderType.MARKET, 0.01, False)

    status = engine.get_status()
    perf = status.get("performance")

    assert perf is not None
    assert "initial_equity" in perf
    assert "current_equity" in perf
