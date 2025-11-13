"""Extended tests for position sizing module.

Tests for methods and edge cases not covered by test_position_sizing.py.
Targets: error validations, utility methods, and convenience functions.
"""

from decimal import Decimal

import pytest

from src.execution.position_sizing import (
    PositionSizer,
    SizingMethod,
    calculate_position_size,
)


@pytest.fixture
def sizer():
    """Create a position sizer instance."""
    return PositionSizer()


class TestErrorValidations:
    """Test error handling and input validation."""

    def test_fixed_fractional_negative_entry_price(self, sizer):
        """Test fixed_fractional rejects negative entry price."""
        with pytest.raises(ValueError, match="Prices must be positive"):
            sizer.fixed_fractional(
                equity=Decimal("100000"),
                risk_percent=0.01,
                entry_price=Decimal("-100"),
                stop_loss_price=Decimal("95"),
            )

    def test_fixed_fractional_zero_entry_price(self, sizer):
        """Test fixed_fractional rejects zero entry price."""
        with pytest.raises(ValueError, match="Prices must be positive"):
            sizer.fixed_fractional(
                equity=Decimal("100000"),
                risk_percent=0.01,
                entry_price=Decimal("0"),
                stop_loss_price=Decimal("95"),
            )

    def test_fixed_fractional_negative_equity(self, sizer):
        """Test fixed_fractional rejects negative equity."""
        with pytest.raises(ValueError, match="Equity must be positive"):
            sizer.fixed_fractional(
                equity=Decimal("-1000"),
                risk_percent=0.01,
                entry_price=Decimal("100"),
                stop_loss_price=Decimal("95"),
            )

    def test_kelly_invalid_win_rate_zero(self, sizer):
        """Test Kelly rejects win rate of 0."""
        with pytest.raises(ValueError, match="Win rate must be between 0 and 1"):
            sizer.kelly_criterion(
                equity=Decimal("100000"),
                win_rate=0.0,
                avg_win=100.0,
                avg_loss=50.0,
            )

    def test_kelly_invalid_win_rate_one(self, sizer):
        """Test Kelly rejects win rate of 1."""
        with pytest.raises(ValueError, match="Win rate must be between 0 and 1"):
            sizer.kelly_criterion(
                equity=Decimal("100000"),
                win_rate=1.0,
                avg_win=100.0,
                avg_loss=50.0,
            )

    def test_kelly_negative_avg_win(self, sizer):
        """Test Kelly rejects negative avg win."""
        with pytest.raises(ValueError, match="Average win and loss must be positive"):
            sizer.kelly_criterion(
                equity=Decimal("100000"),
                win_rate=0.6,
                avg_win=-100.0,
                avg_loss=50.0,
            )

    def test_kelly_zero_avg_loss(self, sizer):
        """Test Kelly rejects zero avg loss."""
        with pytest.raises(ValueError, match="Average win and loss must be positive"):
            sizer.kelly_criterion(
                equity=Decimal("100000"),
                win_rate=0.6,
                avg_win=100.0,
                avg_loss=0.0,
            )

    def test_fixed_dollar_negative_amount(self, sizer):
        """Test fixed_dollar rejects negative amount."""
        with pytest.raises(ValueError, match="Dollar amount and price must be positive"):
            sizer.fixed_dollar(
                dollar_amount=Decimal("-1000"),
                entry_price=Decimal("100"),
            )

    def test_fixed_shares_negative(self, sizer):
        """Test fixed_shares rejects negative shares."""
        with pytest.raises(ValueError, match="Shares must be positive"):
            sizer.fixed_shares(Decimal("-100"))

    def test_fixed_shares_zero(self, sizer):
        """Test fixed_shares rejects zero shares."""
        with pytest.raises(ValueError, match="Shares must be positive"):
            sizer.fixed_shares(Decimal("0"))

    def test_percent_of_equity_negative_equity(self, sizer):
        """Test percent_of_equity rejects negative equity."""
        with pytest.raises(ValueError, match="Equity must be positive"):
            sizer.percent_of_equity(
                equity=Decimal("-100000"),
                percent=0.1,
                entry_price=Decimal("100"),
            )

    def test_percent_of_equity_negative_percent(self, sizer):
        """Test percent_of_equity rejects negative percent."""
        with pytest.raises(ValueError, match="Percent must be positive"):
            sizer.percent_of_equity(
                equity=Decimal("100000"),
                percent=-0.1,
                entry_price=Decimal("100"),
            )

    def test_percent_of_equity_negative_price(self, sizer):
        """Test percent_of_equity rejects negative price."""
        with pytest.raises(ValueError, match="Entry price must be positive"):
            sizer.percent_of_equity(
                equity=Decimal("100000"),
                percent=0.1,
                entry_price=Decimal("-100"),
            )

    def test_r_multiple_sizing_negative_equity(self, sizer):
        """Test r_multiple_sizing rejects negative equity."""
        with pytest.raises(ValueError, match="Equity must be positive"):
            sizer.r_multiple_sizing(
                equity=Decimal("-100000"),
                r_amount=Decimal("1000"),
                entry_price=Decimal("100"),
                stop_loss_price=Decimal("95"),
            )

    def test_r_multiple_sizing_negative_r_amount(self, sizer):
        """Test r_multiple_sizing rejects negative R amount."""
        with pytest.raises(ValueError, match="R amount must be positive"):
            sizer.r_multiple_sizing(
                equity=Decimal("100000"),
                r_amount=Decimal("-1000"),
                entry_price=Decimal("100"),
                stop_loss_price=Decimal("95"),
            )

    def test_r_multiple_sizing_negative_price(self, sizer):
        """Test r_multiple_sizing rejects negative prices."""
        with pytest.raises(ValueError, match="Prices must be positive"):
            sizer.r_multiple_sizing(
                equity=Decimal("100000"),
                r_amount=Decimal("1000"),
                entry_price=Decimal("-100"),
                stop_loss_price=Decimal("95"),
            )

    def test_r_multiple_sizing_negative_target(self, sizer):
        """Test r_multiple_sizing rejects negative target R."""
        with pytest.raises(ValueError, match="Target R must be positive"):
            sizer.r_multiple_sizing(
                equity=Decimal("100000"),
                r_amount=Decimal("1000"),
                entry_price=Decimal("100"),
                stop_loss_price=Decimal("95"),
                target_r=-1.0,
            )


class TestFixedShares:
    """Test fixed_shares method."""

    def test_fixed_shares_basic(self, sizer):
        """Test fixed_shares returns input."""
        shares = Decimal("100")
        result = sizer.fixed_shares(shares)
        assert result == shares

    def test_fixed_shares_fractional(self, sizer):
        """Test fixed_shares with fractional shares."""
        shares = Decimal("100.5")
        result = sizer.fixed_shares(shares)
        assert result == shares


class TestRMultiple:
    """Test R-multiple calculations."""

    def test_calculate_r_multiple_profit(self, sizer):
        """Test R-multiple calculation with profit."""
        entry = Decimal("100")
        exit_price = Decimal("110")  # $10 profit
        stop = Decimal("95")  # $5 risk

        r_multiple = sizer.calculate_r_multiple(entry, exit_price, stop)

        # Profit: $10, Risk: $5 => 2R
        assert r_multiple == 2.0

    def test_calculate_r_multiple_loss(self, sizer):
        """Test R-multiple calculation with loss."""
        entry = Decimal("100")
        exit_price = Decimal("90")  # $10 loss
        stop = Decimal("95")  # $5 risk

        r_multiple = sizer.calculate_r_multiple(entry, exit_price, stop)

        # Loss: -$10, Risk: $5 => -2R
        assert r_multiple == -2.0

    def test_calculate_r_multiple_zero_risk(self, sizer):
        """Test R-multiple with zero risk raises error."""
        entry = Decimal("100")
        exit_price = Decimal("110")
        stop = Decimal("100")  # Same as entry = no risk

        with pytest.raises(ValueError, match="Stop loss cannot equal entry price"):
            sizer.calculate_r_multiple(entry, exit_price, stop)

    def test_r_multiple_sizing_zero_risk(self, sizer):
        """Test r_multiple_sizing returns 0 with zero risk."""
        result = sizer.r_multiple_sizing(
            equity=Decimal("100000"),
            r_amount=Decimal("1000"),
            entry_price=Decimal("100"),
            stop_loss_price=Decimal("100"),  # Same as entry
        )

        assert result == Decimal("0")


class TestRiskRewardRatio:
    """Test risk/reward ratio calculation."""

    def test_calculate_risk_reward_ratio_basic(self, sizer):
        """Test basic risk/reward calculation."""
        entry = Decimal("100")
        target = Decimal("115")  # $15 profit
        stop = Decimal("95")  # $5 risk

        rr_ratio = sizer.calculate_risk_reward_ratio(entry, target, stop)

        # Reward: $15, Risk: $5 => 3:1 RR
        assert rr_ratio == 3.0

    def test_calculate_risk_reward_ratio_poor(self, sizer):
        """Test poor risk/reward ratio."""
        entry = Decimal("100")
        target = Decimal("105")  # $5 profit
        stop = Decimal("90")  # $10 risk

        rr_ratio = sizer.calculate_risk_reward_ratio(entry, target, stop)

        # Reward: $5, Risk: $10 => 0.5:1 RR (poor)
        assert rr_ratio == 0.5


class TestVolatilityAdjustment:
    """Test volatility-based position adjustment."""

    def test_adjust_for_volatility_disabled(self, sizer):
        """Test no adjustment when disabled."""
        base_size = Decimal("100")
        result = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=10.0,
            average_atr=5.0,
            volatility_adjustment=False,
        )

        assert result == base_size

    def test_adjust_for_volatility_high(self, sizer):
        """Test adjustment reduces size in high volatility."""
        base_size = Decimal("100")
        result = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=10.0,  # High volatility
            average_atr=5.0,  # Normal
            volatility_adjustment=True,
        )

        # Should reduce size (ATR ratio = 2.0, adjustment = 0.5)
        assert result < base_size
        assert result == Decimal("50")

    def test_adjust_for_volatility_low(self, sizer):
        """Test adjustment increases size in low volatility."""
        base_size = Decimal("100")
        result = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=5.0,  # Low volatility
            average_atr=10.0,  # Normal
            volatility_adjustment=True,
        )

        # Should increase size (ATR ratio = 0.5, adjustment = 2.0)
        assert result > base_size
        assert result == Decimal("200")

    def test_adjust_for_volatility_capped(self, sizer):
        """Test adjustment is capped between 0.5x and 2.0x."""
        base_size = Decimal("100")

        # Very high volatility (would be 0.1x without cap)
        result_high = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=100.0,
            average_atr=10.0,
            volatility_adjustment=True,
        )

        # Should be capped at 0.5x
        assert result_high == Decimal("50")

        # Very low volatility (would be 10x without cap)
        result_low = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=1.0,
            average_atr=10.0,
            volatility_adjustment=True,
        )

        # Should be capped at 2.0x
        assert result_low == Decimal("200")

    def test_adjust_for_volatility_invalid_atr(self, sizer, caplog):
        """Test adjustment returns base size with invalid ATR."""
        base_size = Decimal("100")

        # Zero ATR
        result = sizer.adjust_for_volatility(
            base_size=base_size,
            current_atr=0.0,
            average_atr=10.0,
            volatility_adjustment=True,
        )

        assert result == base_size
        assert "Invalid ATR values" in caplog.text


class TestUtilityMethods:
    """Test utility calculation methods."""

    def test_calculate_position_value(self, sizer):
        """Test position value calculation."""
        quantity = Decimal("100")
        price = Decimal("50")

        value = sizer.calculate_position_value(quantity, price)

        assert value == Decimal("5000")

    def test_calculate_max_position_size(self, sizer):
        """Test maximum position size calculation."""
        equity = Decimal("100000")
        max_percent = 0.20  # 20% max per position
        price = Decimal("100")

        max_size = sizer.calculate_max_position_size(equity, max_percent, price)

        # 20% of $100k = $20k
        # $20k / $100 = 200 shares
        assert max_size == Decimal("200")


class TestKellyWithEntryPrice:
    """Test Kelly criterion with entry_price parameter."""

    def test_kelly_with_entry_price(self, sizer):
        """Test Kelly returns quantity when entry_price provided."""
        equity = Decimal("100000")
        win_rate = 0.6
        avg_win = 600.0
        avg_loss = 400.0
        entry_price = Decimal("100")

        quantity = sizer.kelly_criterion(
            equity=equity,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            entry_price=entry_price,
        )

        # Should return whole number of shares
        assert isinstance(quantity, Decimal)
        assert quantity > Decimal("0")
        assert quantity == int(quantity)  # Whole shares

    def test_kelly_without_entry_price(self, sizer):
        """Test Kelly returns dollar amount when no entry_price."""
        equity = Decimal("100000")
        win_rate = 0.6
        avg_win = 600.0
        avg_loss = 400.0

        amount = sizer.kelly_criterion(
            equity=equity,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            entry_price=None,
        )

        # Should return dollar amount
        assert isinstance(amount, Decimal)
        assert amount > Decimal("0")


class TestConvenienceFunction:
    """Test calculate_position_size convenience function."""

    def test_calculate_position_size_fixed_fractional(self):
        """Test convenience function with FIXED_FRACTIONAL."""
        size = calculate_position_size(
            method=SizingMethod.FIXED_FRACTIONAL,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
            stop_loss_price=Decimal("95"),
            risk_percent=0.01,
        )

        assert size == Decimal("200")

    def test_calculate_position_size_fixed_fractional_missing_stop(self):
        """Test FIXED_FRACTIONAL requires stop_loss_price."""
        with pytest.raises(ValueError, match="stop_loss_price required"):
            calculate_position_size(
                method=SizingMethod.FIXED_FRACTIONAL,
                equity=Decimal("100000"),
                entry_price=Decimal("100"),
                risk_percent=0.01,
            )

    def test_calculate_position_size_kelly(self):
        """Test convenience function with KELLY."""
        size = calculate_position_size(
            method=SizingMethod.KELLY,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
            win_rate=0.6,
            avg_win=500.0,
            avg_loss=300.0,
            kelly_fraction=0.25,
        )

        assert size >= Decimal("0")

    def test_calculate_position_size_fixed_dollar(self):
        """Test convenience function with FIXED_DOLLAR."""
        size = calculate_position_size(
            method=SizingMethod.FIXED_DOLLAR,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
            dollar_amount=Decimal("10000"),
        )

        assert size == Decimal("100")

    def test_calculate_position_size_fixed_dollar_default(self):
        """Test FIXED_DOLLAR uses default 1% of equity."""
        size = calculate_position_size(
            method=SizingMethod.FIXED_DOLLAR,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
        )

        # Should use 1% of equity = $1000
        # $1000 / $100 = 10 shares
        assert size == Decimal("10")

    def test_calculate_position_size_fixed_shares(self):
        """Test convenience function with FIXED_SHARES."""
        size = calculate_position_size(
            method=SizingMethod.FIXED_SHARES,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
            shares=Decimal("50"),
        )

        assert size == Decimal("50")

    def test_calculate_position_size_fixed_shares_default(self):
        """Test FIXED_SHARES uses default 100 shares."""
        size = calculate_position_size(
            method=SizingMethod.FIXED_SHARES,
            equity=Decimal("100000"),
            entry_price=Decimal("100"),
        )

        # Should use default 100 shares
        assert size == Decimal("100")

    def test_calculate_position_size_unknown_method(self):
        """Test unknown method raises ValueError."""
        with pytest.raises(ValueError, match="Unknown sizing method"):
            # Create a fake method
            calculate_position_size(
                method="UNKNOWN_METHOD",  # type: ignore
                equity=Decimal("100000"),
                entry_price=Decimal("100"),
            )


class TestSizingMethodEnum:
    """Test SizingMethod enum."""

    def test_sizing_method_values(self):
        """Test all sizing method enum values."""
        assert SizingMethod.FIXED_FRACTIONAL.value == "fixed_fractional"
        assert SizingMethod.KELLY.value == "kelly"
        assert SizingMethod.FIXED_DOLLAR.value == "fixed_dollar"
        assert SizingMethod.FIXED_SHARES.value == "fixed_shares"

    def test_sizing_method_comparison(self):
        """Test enum comparison."""
        assert SizingMethod.FIXED_FRACTIONAL == SizingMethod.FIXED_FRACTIONAL
        assert SizingMethod.FIXED_FRACTIONAL != SizingMethod.KELLY
