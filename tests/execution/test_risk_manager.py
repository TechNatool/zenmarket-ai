"""
Tests for risk manager with circuit breakers.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.execution.risk_manager import RiskManager, RiskLimits, RiskState
from src.execution.broker_simulator import BrokerSimulator
from src.execution.order_types import OrderSide


@pytest.fixture
def broker():
    """Create a broker simulator instance."""
    broker = BrokerSimulator(initial_cash=Decimal('100000'))
    broker.connect()
    return broker


@pytest.fixture
def risk_limits():
    """Create risk limits with tight restrictions for testing."""
    return RiskLimits(
        max_risk_per_trade_pct=0.01,
        max_position_size_pct=0.20,
        max_risk_per_day_pct=0.03,
        max_daily_drawdown_pct=0.05,
        max_open_positions=5,
        max_consecutive_losses=3
    )


@pytest.fixture
def risk_manager(broker, risk_limits):
    """Create a risk manager instance."""
    return RiskManager(broker, risk_limits)


def test_risk_manager_initialization(risk_manager):
    """Test risk manager can be initialized."""
    assert risk_manager is not None
    assert isinstance(risk_manager.state, RiskState)
    assert not risk_manager.state.trading_halted


def test_validate_order_basic(risk_manager):
    """Test basic order validation."""
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        entry_price=Decimal('150'),
        stop_loss=Decimal('145')
    )

    # Should pass with reasonable parameters
    assert is_valid
    assert error is None


def test_validate_order_oversized_position(risk_manager):
    """Test rejection of oversized position."""
    # Try to buy $50k worth with $100k equity (50% position size)
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('500'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('95')
    )

    # Should fail (exceeds 20% position size limit)
    assert not is_valid
    assert "Position size" in error


def test_validate_order_excessive_risk(risk_manager):
    """Test rejection of excessive risk per trade."""
    # Position: 150 shares @ $100 = $15,000 (15% of equity) - under 20% position limit
    # Risk: $7/share * 150 = $1,050 (1.05% of equity) - exceeds 1% trade risk limit
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('150'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('93')
    )

    # Should fail (exceeds 1% risk per trade limit)
    assert not is_valid
    assert "Trade risk" in error


def test_validate_order_no_stop_loss(risk_manager):
    """Test validation without stop loss (should still work)."""
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('100'),
        entry_price=Decimal('100'),
        stop_loss=None
    )

    # Should pass but only check position size
    assert is_valid


def test_max_positions_limit(risk_manager, broker):
    """Test max open positions limit."""
    # Setup mock prices for test symbols
    for i in range(6):
        broker._mock_prices[f"TEST{i}"] = Decimal('100')

    # Place 5 orders to reach limit
    for i in range(5):
        broker.place_order(
            symbol=f"TEST{i}",
            side=OrderSide.BUY,
            quantity=Decimal('10'),
            order_type="market"
        )

    # Try to place 6th order
    is_valid, error = risk_manager.validate_order(
        symbol="TEST6",
        side=OrderSide.BUY,
        quantity=Decimal('10'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('95')
    )

    # Should fail (max 5 positions)
    assert not is_valid
    assert "Max open positions" in error


def test_consecutive_losses_circuit_breaker(risk_manager):
    """Test consecutive losses circuit breaker."""
    # Record 3 consecutive losses
    for _ in range(3):
        risk_manager.record_trade_result(
            pnl=Decimal('-100'),
            risk_pct=0.01
        )

    # Should halt trading
    assert risk_manager.state.trading_halted
    assert "consecutive losses" in risk_manager.state.halt_reason.lower()

    # Try to place order
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('10'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('95')
    )

    assert not is_valid
    assert "Trading halted" in error


def test_consecutive_wins_reset_losses(risk_manager):
    """Test that wins reset consecutive losses counter."""
    # Record 2 losses
    risk_manager.record_trade_result(Decimal('-100'), 0.01)
    risk_manager.record_trade_result(Decimal('-100'), 0.01)

    assert risk_manager.state.consecutive_losses == 2

    # Record a win
    risk_manager.record_trade_result(Decimal('200'), 0.01)

    # Should reset consecutive losses
    assert risk_manager.state.consecutive_losses == 0
    assert risk_manager.state.consecutive_wins == 1
    assert not risk_manager.state.trading_halted


def test_daily_reset(risk_manager):
    """Test daily state reset."""
    # Record some trades
    risk_manager.state.trades_today = 10
    risk_manager.state.daily_pnl = Decimal('500')
    risk_manager.state.daily_risk_used_pct = 0.02

    # Manually change last reset date to yesterday
    from datetime import date, timedelta
    risk_manager.state.last_reset_date = date.today() - timedelta(days=1)

    # Trigger reset check
    risk_manager.check_daily_reset()

    # Should be reset
    assert risk_manager.state.trades_today == 0
    assert risk_manager.state.daily_pnl == Decimal('0')
    assert risk_manager.state.daily_risk_used_pct == 0.0


def test_risk_state_halt_and_resume(risk_manager):
    """Test manual halt and resume."""
    # Halt trading
    risk_manager.force_halt("Manual test halt")

    assert risk_manager.state.trading_halted
    assert risk_manager.state.halt_reason == "Manual test halt"
    assert risk_manager.state.halt_timestamp is not None

    # Resume trading
    risk_manager.force_resume()

    assert not risk_manager.state.trading_halted
    assert risk_manager.state.halt_reason is None


def test_get_risk_summary(risk_manager):
    """Test risk summary generation."""
    summary = risk_manager.get_risk_summary()

    assert isinstance(summary, dict)
    assert 'limits' in summary
    assert 'state' in summary
    assert 'account' in summary
    assert 'positions' in summary
    assert 'daily' in summary


def test_risk_limits_to_dict(risk_limits):
    """Test risk limits to dict conversion."""
    limits_dict = risk_limits.to_dict()

    assert isinstance(limits_dict, dict)
    assert 'max_risk_per_trade_pct' in limits_dict
    assert 'max_daily_drawdown_pct' in limits_dict
    assert limits_dict['max_risk_per_trade_pct'] == 0.01


def test_risk_state_to_dict(risk_manager):
    """Test risk state to dict conversion."""
    state_dict = risk_manager.state.to_dict()

    assert isinstance(state_dict, dict)
    assert 'trading_halted' in state_dict
    assert 'consecutive_losses' in state_dict
    assert 'daily_pnl' in state_dict


def test_volatility_limit_check(risk_manager):
    """Test volatility limit checking."""
    # Normal volatility
    is_ok, msg = risk_manager.check_volatility_limit(
        current_atr=2.0,
        average_atr=2.0
    )
    assert is_ok
    assert msg is None

    # High volatility (3.5x normal)
    is_ok, msg = risk_manager.check_volatility_limit(
        current_atr=7.0,
        average_atr=2.0
    )
    assert not is_ok
    assert "High volatility" in msg


def test_daily_risk_accumulation(risk_manager):
    """Test daily risk accumulation."""
    # Use up 2% of daily risk (limit is 3%)
    risk_manager.record_trade_result(Decimal('-100'), 0.02)

    assert risk_manager.state.daily_risk_used_pct == 0.02

    # Try to place order that would exceed daily limit
    is_valid, error = risk_manager.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('200'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('95')  # Would use another 1%
    )

    # Should fail (2% + 1% = 3%, at the limit)
    assert not is_valid
    assert "Daily risk limit" in error


def test_closing_order_allowed_when_at_max_positions(risk_manager, broker):
    """Test that closing orders are allowed even at max positions."""
    # Setup mock prices for 5 different symbols
    for i in range(5):
        broker._mock_prices[f"TEST{i}"] = Decimal('100')

    # Open 5 positions on different symbols to reach max positions limit
    # Use small quantities to avoid triggering drawdown circuit breaker
    for i in range(5):
        broker.place_order(
            symbol=f"TEST{i}",
            side=OrderSide.BUY,
            quantity=Decimal('5'),
            order_type="market"
        )

    # Try to sell (close position) on TEST0 - should be allowed even at max positions
    is_valid, error = risk_manager.validate_order(
        symbol="TEST0",
        side=OrderSide.SELL,
        quantity=Decimal('5'),
        entry_price=Decimal('100'),
        stop_loss=None
    )

    assert is_valid


def test_record_trade_updates_counters(risk_manager):
    """Test that recording trades updates all counters."""
    initial_trades = risk_manager.state.trades_today

    risk_manager.record_trade_result(Decimal('100'), 0.01)

    assert risk_manager.state.trades_today == initial_trades + 1
    assert risk_manager.state.daily_pnl == Decimal('100')
    assert risk_manager.state.consecutive_wins == 1


def test_zero_equity_rejection(broker, risk_limits):
    """Test that zero equity prevents trading."""
    # Create broker with zero cash
    broker_broke = BrokerSimulator(initial_cash=Decimal('0'))
    broker_broke.connect()

    risk_manager_broke = RiskManager(broker_broke, risk_limits)

    is_valid, error = risk_manager_broke.validate_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=Decimal('10'),
        entry_price=Decimal('100'),
        stop_loss=Decimal('95')
    )

    assert not is_valid
    assert "equity is zero" in error.lower()
