"""Regression tests for Phase 4 - Backtesting & Broker Integration.

These tests ensure that previously fixed bugs do not reoccur:
1. Enum import error (PositionSizingMethod -> SizingMethod)
2. Position dataclass market_value field error
"""

from decimal import Decimal

import pandas as pd
import pytest

from src.backtest.backtest_broker import BacktestBroker
from src.execution.broker_simulator import BrokerSimulator
from src.execution.order_types import OrderSide, Position
from src.execution.position_sizing import SizingMethod


class TestEnumImport:
    """Test that the correct enum names are used and importable."""

    def test_sizing_method_enum_importable(self):
        """Ensure the SizingMethod enum is importable and valid."""
        # This should not raise ImportError
        assert hasattr(SizingMethod, "FIXED_FRACTIONAL")
        assert hasattr(SizingMethod, "KELLY")
        assert hasattr(SizingMethod, "FIXED_DOLLAR")

    def test_sizing_method_enum_values(self):
        """Verify SizingMethod enum has correct values."""
        assert SizingMethod.FIXED_FRACTIONAL.value == "fixed_fractional"
        assert SizingMethod.KELLY.value == "kelly"
        assert SizingMethod.FIXED_DOLLAR.value == "fixed_dollar"

    def test_backtest_engine_uses_correct_enum(self):
        """Ensure backtest_engine can import SizingMethod correctly."""
        from src.backtest.backtest_engine import BacktestConfig

        # Should not raise ImportError
        config = BacktestConfig(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            sizing_method=SizingMethod.FIXED_FRACTIONAL,
        )
        assert config.sizing_method == SizingMethod.FIXED_FRACTIONAL


class TestPositionMarketValue:
    """Test that market_value is computed dynamically, not stored."""

    def test_position_no_market_value_field(self):
        """Ensure Position dataclass does not have market_value field."""
        # Create a position
        position = Position(
            symbol="AAPL",
            quantity=Decimal("10"),
            avg_entry_price=Decimal("150.0"),
            current_price=Decimal("155.0"),
        )

        # market_value should not be a stored field
        with pytest.raises(AttributeError):
            _ = position.market_value

    def test_market_value_computed_correctly(self):
        """Verify market_value can be computed correctly from position data."""
        position = Position(
            symbol="AAPL",
            quantity=Decimal("10"),
            avg_entry_price=Decimal("150.0"),
            current_price=Decimal("155.0"),
        )

        # Compute market_value manually
        market_value = position.quantity * position.current_price
        assert market_value == Decimal("1550.0")

    def test_backtest_broker_computes_market_value(self):
        """Ensure BacktestBroker computes market_value without storing it."""
        # Create sample historical data
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        data = {
            "AAPL": pd.DataFrame(
                {
                    "Open": [150.0, 151.0, 152.0, 153.0, 154.0],
                    "High": [151.0, 152.0, 153.0, 154.0, 155.0],
                    "Low": [149.0, 150.0, 151.0, 152.0, 153.0],
                    "Close": [150.5, 151.5, 152.5, 153.5, 154.5],
                    "Volume": [1000000] * 5,
                },
                index=dates,
            )
        }

        broker = BacktestBroker(
            historical_data=data,
            initial_cash=Decimal("100000"),
        )
        broker.connect()

        # Set current bar
        timestamp = dates[0]
        bar_data = {
            "AAPL": {
                "Open": 150.0,
                "High": 151.0,
                "Low": 149.0,
                "Close": 150.5,
                "Volume": 1000000,
            }
        }
        broker.set_current_bar(timestamp, bar_data)

        # Place an order
        broker.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=Decimal("10"),
        )

        # Get position
        position = broker.get_position("AAPL")

        # Position should not have market_value field
        with pytest.raises(AttributeError):
            _ = position.market_value

        # But we can compute it
        computed_value = position.quantity * position.current_price
        assert computed_value > Decimal("0")


class TestBrokerSimulatorCompatibility:
    """Test that BrokerSimulator is compatible with new changes."""

    def test_broker_simulator_position_tracking(self):
        """Ensure BrokerSimulator correctly tracks positions without market_value field."""
        broker = BrokerSimulator(
            initial_cash=Decimal("100000"),
        )
        broker.connect()

        # Positions should work correctly
        positions = broker.get_positions()
        assert isinstance(positions, list)
        assert len(positions) == 0  # No positions yet


class TestBacktestEngineIntegration:
    """Integration tests for BacktestEngine."""

    def test_backtest_config_initialization(self):
        """Test that BacktestConfig initializes with correct enum."""
        from src.backtest.backtest_engine import BacktestConfig

        config = BacktestConfig(
            symbols=["AAPL", "MSFT"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            initial_capital=Decimal("100000"),
            sizing_method=SizingMethod.KELLY,
        )

        assert config.sizing_method == SizingMethod.KELLY
        assert config.initial_capital == Decimal("100000")
        assert len(config.symbols) == 2

    def test_backtest_result_structure(self):
        """Test BacktestResult dataclass structure."""
        from src.backtest.backtest_engine import BacktestConfig, BacktestResult
        from src.backtest.metrics import PerformanceMetrics

        # Create mock data for testing
        config = BacktestConfig(
            symbols=["TEST"],
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        # Create minimal equity curve
        equity_df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=2),
                "equity": [100000.0, 101000.0],
                "drawdown": [0.0, 0.0],
            }
        )

        # Calculate minimal metrics
        metrics = PerformanceMetrics.calculate(
            equity_curve=equity_df,
            trades=[],
            initial_capital=Decimal("100000"),
        )

        # Create result
        result = BacktestResult(
            config=config,
            metrics=metrics,
            equity_curve=equity_df,
            trades=[],
            signals=[],
        )

        assert result.config == config
        assert result.metrics == metrics
        assert len(result.equity_curve) == 2


# Add marker for regression tests
pytestmark = pytest.mark.unit
