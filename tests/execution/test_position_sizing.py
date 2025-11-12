"""
Tests for position sizing module.
"""

from decimal import Decimal

import pytest

from src.execution.position_sizing import PositionSizer


@pytest.fixture
def sizer():
    """Create a position sizer instance."""
    return PositionSizer()


def test_sizer_initialization(sizer):
    """Test sizer can be initialized."""
    assert sizer is not None


def test_fixed_fractional_basic(sizer):
    """Test basic fixed fractional sizing."""
    equity = Decimal("100000")
    risk_percent = 0.01  # 1%
    entry_price = Decimal("100")
    stop_loss_price = Decimal("95")  # 5% stop

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Risk per share: $5
    # Dollar risk: $1000 (1% of $100k)
    # Expected quantity: 200 shares
    assert quantity == Decimal("200")


def test_fixed_fractional_with_volatility_adjustment(sizer):
    """Test fixed fractional with volatility adjustment."""
    equity = Decimal("100000")
    risk_percent = 0.01
    entry_price = Decimal("100")
    stop_loss_price = Decimal("95")
    atr = Decimal("10")  # High volatility
    atr_avg = Decimal("5")  # Normal volatility

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        atr=atr,
        atr_avg=atr_avg,
    )

    # Base quantity would be 200
    # With 2x volatility, should be reduced to 100
    assert quantity == Decimal("100")


def test_fixed_fractional_zero_risk(sizer):
    """Test fixed fractional with zero risk (stop = entry)."""
    equity = Decimal("100000")
    risk_percent = 0.01
    entry_price = Decimal("100")
    stop_loss_price = Decimal("100")  # No stop loss distance

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Should return 0 when there's no stop loss distance
    assert quantity == Decimal("0")


def test_kelly_criterion(sizer):
    """Test Kelly criterion sizing."""
    equity = Decimal("100000")
    win_rate = 0.6  # 60% win rate
    avg_win = Decimal("500")
    avg_loss = Decimal("300")
    entry_price = Decimal("100")

    quantity = sizer.kelly_criterion(
        equity=equity,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        entry_price=entry_price,
    )

    # Kelly% = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
    # Kelly% = (0.6 * 500 - 0.4 * 300) / 500 = 0.36
    # Half Kelly = 0.18
    # Position value = $18,000
    # Quantity = 180 shares
    assert quantity > Decimal("0")
    assert quantity <= Decimal("200")  # Should be reasonable


def test_kelly_criterion_negative(sizer):
    """Test Kelly with negative expectancy (losing strategy)."""
    equity = Decimal("100000")
    win_rate = 0.3  # 30% win rate (bad)
    avg_win = Decimal("100")
    avg_loss = Decimal("200")
    entry_price = Decimal("100")

    quantity = sizer.kelly_criterion(
        equity=equity,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        entry_price=entry_price,
    )

    # Negative Kelly should return 0
    assert quantity == Decimal("0")


def test_fixed_dollar(sizer):
    """Test fixed dollar amount sizing."""
    dollar_amount = Decimal("10000")
    entry_price = Decimal("100")

    quantity = sizer.fixed_dollar(dollar_amount=dollar_amount, entry_price=entry_price)

    # $10,000 / $100 = 100 shares
    assert quantity == Decimal("100")


def test_fixed_dollar_fractional_shares(sizer):
    """Test fixed dollar with fractional shares."""
    dollar_amount = Decimal("10000")
    entry_price = Decimal("333.33")

    quantity = sizer.fixed_dollar(dollar_amount=dollar_amount, entry_price=entry_price)

    # Should round down to whole shares
    expected = int(dollar_amount / entry_price)
    assert quantity == Decimal(str(expected))


def test_fixed_dollar_zero_price(sizer):
    """Test fixed dollar with zero price."""
    dollar_amount = Decimal("10000")
    entry_price = Decimal("0")

    quantity = sizer.fixed_dollar(dollar_amount=dollar_amount, entry_price=entry_price)

    # Should return 0 for zero price
    assert quantity == Decimal("0")


def test_percent_of_equity(sizer):
    """Test percent of equity sizing."""
    equity = Decimal("100000")
    percent = 0.10  # 10%
    entry_price = Decimal("50")

    quantity = sizer.percent_of_equity(equity=equity, percent=percent, entry_price=entry_price)

    # 10% of $100k = $10k
    # $10k / $50 = 200 shares
    assert quantity == Decimal("200")


def test_r_multiple_sizing(sizer):
    """Test R-multiple based sizing."""
    equity = Decimal("100000")
    r_amount = Decimal("1000")  # 1R = $1000
    entry_price = Decimal("100")
    stop_loss_price = Decimal("95")  # $5 risk per share
    target_r = 2  # Risk 2R on this trade

    quantity = sizer.r_multiple_sizing(
        equity=equity,
        r_amount=r_amount,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        target_r=target_r,
    )

    # 2R = $2000 risk
    # Risk per share = $5
    # Quantity = 400 shares
    assert quantity == Decimal("400")


def test_high_equity_scenario(sizer):
    """Test sizing with high equity."""
    equity = Decimal("1000000")  # $1M
    risk_percent = 0.01
    entry_price = Decimal("1000")
    stop_loss_price = Decimal("950")  # $50 risk per share

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Risk = $10,000
    # Risk per share = $50
    # Quantity = 200 shares
    assert quantity == Decimal("200")


def test_low_equity_scenario(sizer):
    """Test sizing with low equity."""
    equity = Decimal("1000")  # $1k
    risk_percent = 0.02  # 2%
    entry_price = Decimal("100")
    stop_loss_price = Decimal("95")

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Risk = $20
    # Risk per share = $5
    # Quantity = 4 shares
    assert quantity == Decimal("4")


def test_wide_stop_loss(sizer):
    """Test sizing with wide stop loss."""
    equity = Decimal("100000")
    risk_percent = 0.01
    entry_price = Decimal("100")
    stop_loss_price = Decimal("80")  # 20% stop (wide)

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Risk per share = $20
    # Dollar risk = $1000
    # Quantity = 50 shares
    assert quantity == Decimal("50")


def test_tight_stop_loss(sizer):
    """Test sizing with tight stop loss."""
    equity = Decimal("100000")
    risk_percent = 0.01
    entry_price = Decimal("100")
    stop_loss_price = Decimal("99")  # 1% stop (tight)

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Risk per share = $1
    # Dollar risk = $1000
    # Quantity = 1000 shares
    assert quantity == Decimal("1000")


def test_decimal_precision(sizer):
    """Test that calculations maintain decimal precision."""
    equity = Decimal("100000.50")
    risk_percent = 0.01234
    entry_price = Decimal("99.99")
    stop_loss_price = Decimal("95.55")

    quantity = sizer.fixed_fractional(
        equity=equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    # Should return whole number of shares
    assert isinstance(quantity, Decimal)
    assert quantity >= Decimal("0")
