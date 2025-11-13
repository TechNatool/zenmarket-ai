"""Tests for CLI module."""

import sys
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.cli import (
    add_common_args,
    create_risk_limits,
    get_order_type,
    get_sizing_method,
    main,
    parse_args,
    run_backtest,
    run_live,
    run_simulate,
)
from src.execution.order_types import OrderType
from src.execution.position_sizing import SizingMethod
from src.execution.risk_manager import RiskLimits


def test_cli_help_output():
    """Test CLI help output."""
    with pytest.raises(SystemExit) as exc_info:
        with patch.object(sys, "argv", ["cli.py", "--help"]):
            parse_args()
    assert exc_info.value.code == 0


def test_cli_backtest_runs():
    """Test CLI backtest command runs without errors with mocked dependencies."""
    test_args = [
        "cli.py",
        "backtest",
        "--symbols",
        "AAPL",
        "--from",
        "2024-01-01",
        "--to",
        "2024-12-31",
        "--initial-capital",
        "100000",
    ]

    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.command == "backtest"
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.initial_capital == 100000.0


def test_cli_backtest_invalid_symbol():
    """Test CLI backtest with invalid symbol still parses correctly."""
    test_args = [
        "cli.py",
        "backtest",
        "--symbols",
        "INVALID_SYMBOL_12345",
        "--from",
        "2024-01-01",
        "--to",
        "2024-12-31",
    ]

    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.command == "backtest"
        symbols = [s.strip() for s in args.symbols.split(",")]
        assert "INVALID_SYMBOL_12345" in symbols


def test_cli_live_requires_confirmation():
    """Test that live mode requires --confirm-live flag."""
    test_args = ["cli.py", "live", "--symbols", "AAPL", "--broker", "ibkr"]

    # Missing --confirm-live should fail
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", test_args):
            parse_args()


def test_cli_live_dry_run():
    """Test CLI live mode with dry-run flag."""
    test_args = [
        "cli.py",
        "live",
        "--symbols",
        "AAPL",
        "--broker",
        "ibkr",
        "--confirm-live",
        "--dry-run",
    ]

    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.command == "live"
        assert args.dry_run is True
        assert args.confirm_live is True


def test_cli_invalid_command_returns_error():
    """Test that invalid commands are rejected."""
    test_args = ["cli.py", "invalid_command"]

    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", test_args):
            parse_args()


def test_cli_config_loading():
    """Test CLI configuration parameters."""
    test_args = [
        "cli.py",
        "simulate",
        "--symbols",
        "AAPL,MSFT",
        "--risk-per-trade",
        "0.02",
        "--risk-per-day",
        "0.05",
        "--max-daily-drawdown",
        "0.10",
        "--max-consecutive-losses",
        "5",
        "--max-positions",
        "10",
        "--sizing-method",
        "kelly",
        "--order-type",
        "limit",
        "--dry-run",
    ]

    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.command == "simulate"
        assert args.risk_per_trade == 0.02
        assert args.risk_per_day == 0.05
        assert args.max_daily_drawdown == 0.10
        assert args.max_consecutive_losses == 5
        assert args.max_positions == 10
        assert args.sizing_method == "kelly"
        assert args.order_type == "limit"
        assert args.dry_run is True

        # Test helper functions
        risk_limits = create_risk_limits(args)
        assert isinstance(risk_limits, RiskLimits)
        assert risk_limits.max_risk_per_trade_pct == 0.02

        order_type = get_order_type(args.order_type)
        assert order_type == OrderType.LIMIT

        sizing_method = get_sizing_method(args.sizing_method)
        assert sizing_method == SizingMethod.KELLY


def test_get_order_type_mapping():
    """Test order type string to enum mapping."""
    assert get_order_type("market") == OrderType.MARKET
    assert get_order_type("limit") == OrderType.LIMIT
    assert get_order_type("stop") == OrderType.STOP
    assert get_order_type("stop_limit") == OrderType.STOP_LIMIT
    assert get_order_type("invalid") == OrderType.MARKET  # Default


def test_get_sizing_method_mapping():
    """Test sizing method string to enum mapping."""
    assert get_sizing_method("fixed_fractional") == SizingMethod.FIXED_FRACTIONAL
    assert get_sizing_method("kelly") == SizingMethod.KELLY
    assert get_sizing_method("fixed_dollar") == SizingMethod.FIXED_DOLLAR
    assert get_sizing_method("invalid") == SizingMethod.FIXED_FRACTIONAL  # Default


def test_add_common_args():
    """Test that common args are added correctly."""
    import argparse

    parser = argparse.ArgumentParser()
    add_common_args(parser)

    test_args = [
        "--symbols",
        "AAPL",
        "--order-type",
        "market",
        "--risk-per-trade",
        "0.01",
    ]

    args = parser.parse_args(test_args)
    assert args.symbols == "AAPL"
    assert args.order_type == "market"
    assert args.risk_per_trade == 0.01


def test_run_simulate_with_mocks():
    """Test run_simulate function with mocked dependencies."""
    test_args_list = [
        "cli.py",
        "simulate",
        "--symbols",
        "AAPL",
        "--dry-run",
    ]

    with patch.object(sys, "argv", test_args_list):
        args = parse_args()

    with (
        patch("src.cli.BrokerSimulator") as mock_broker_cls,
        patch("src.cli.ExecutionEngine") as mock_engine_cls,
        patch("src.cli.IndicatorCalculator") as mock_indicator_cls,
        patch("src.cli.SignalGenerator") as mock_signal_cls,
        patch("src.cli.yf.Ticker") as mock_ticker,
    ):
        # Setup mocks
        mock_broker = MagicMock()
        mock_broker_cls.return_value = mock_broker

        mock_engine = MagicMock()
        mock_engine.get_status.return_value = {
            "broker": "simulator",
            "connected": True,
            "performance": {
                "initial_equity": "$100,000",
                "current_equity": "$105,000",
                "total_return": "5.0%",
                "max_drawdown": "-2.0%",
                "total_trades": 10,
                "win_rate": "60%",
            },
            "risk_summary": {
                "state": {
                    "trading_halted": False,
                    "consecutive_losses": 0,
                    "daily_pnl": "$500",
                }
            },
        }
        mock_engine_cls.return_value = mock_engine

        mock_indicator = MagicMock()
        mock_indicator_cls.return_value = mock_indicator

        mock_signal_gen = MagicMock()
        mock_signal = MagicMock()
        mock_signal.signal.value = "BUY"
        mock_signal.confidence = 0.75
        mock_signal.reasons = ["RSI oversold", "MACD crossover"]
        mock_signal_gen.generate_signal.return_value = mock_signal
        mock_signal_cls.return_value = mock_signal_gen

        # Mock yfinance data
        mock_hist_df = MagicMock()
        mock_hist_df.empty = False
        mock_hist_df.__len__ = lambda self: 100
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist_df
        mock_ticker.return_value = mock_ticker_instance

        mock_indicator.calculate_all_indicators.return_value = {"rsi": 30, "macd": 0.5}

        # Run the function
        run_simulate(args)

        # Verify calls
        mock_broker_cls.assert_called_once()
        mock_broker.connect.assert_called_once()
        mock_engine_cls.assert_called_once()
        mock_engine.shutdown.assert_called_once()


def test_run_backtest_success():
    """Test run_backtest function returns 0 on success."""
    test_args_list = [
        "cli.py",
        "backtest",
        "--symbols",
        "AAPL",
        "--from",
        "2024-01-01",
        "--to",
        "2024-12-31",
    ]

    with patch.object(sys, "argv", test_args_list):
        args = parse_args()

    with patch("src.cli.run_backtest_cli") as mock_backtest:
        mock_backtest.return_value = None
        result = run_backtest(args)
        assert result == 0
        mock_backtest.assert_called_once()


def test_run_backtest_failure():
    """Test run_backtest function returns 1 on failure."""
    test_args_list = [
        "cli.py",
        "backtest",
        "--symbols",
        "AAPL",
        "--from",
        "2024-01-01",
        "--to",
        "2024-12-31",
    ]

    with patch.object(sys, "argv", test_args_list):
        args = parse_args()

    with patch("src.cli.run_backtest_cli") as mock_backtest:
        mock_backtest.side_effect = ValueError("Test error")
        result = run_backtest(args)
        assert result == 1


def test_run_live_without_confirmation():
    """Test run_live returns 1 without user confirmation."""
    test_args_list = [
        "cli.py",
        "live",
        "--symbols",
        "AAPL",
        "--broker",
        "ibkr",
        "--confirm-live",
    ]

    with patch.object(sys, "argv", test_args_list):
        args = parse_args()

    # Mock input to return wrong confirmation
    with patch("builtins.input", return_value="NO"):
        result = run_live(args)
        assert result == 0  # Cancelled


def test_run_live_broker_connection_failure():
    """Test run_live returns 1 when broker connection fails."""
    test_args_list = [
        "cli.py",
        "live",
        "--symbols",
        "AAPL",
        "--broker",
        "ibkr",
        "--confirm-live",
    ]

    with patch.object(sys, "argv", test_args_list):
        args = parse_args()

    with (
        patch("builtins.input", return_value="I UNDERSTAND THE RISKS"),
        patch("src.cli.BrokerFactory.create_from_env") as mock_factory,
    ):
        mock_broker = MagicMock()
        mock_broker.connect.return_value = False
        mock_factory.return_value = mock_broker

        result = run_live(args)
        assert result == 1


def test_main_simulate_command():
    """Test main() with simulate command."""
    test_args = ["cli.py", "simulate", "--symbols", "AAPL", "--dry-run"]

    with (
        patch.object(sys, "argv", test_args),
        patch("src.cli.run_simulate") as mock_simulate,
    ):
        mock_simulate.return_value = None
        result = main()
        mock_simulate.assert_called_once()
        assert result is None


def test_main_backtest_command():
    """Test main() with backtest command."""
    test_args = [
        "cli.py",
        "backtest",
        "--symbols",
        "AAPL",
        "--from",
        "2024-01-01",
        "--to",
        "2024-12-31",
    ]

    with (
        patch.object(sys, "argv", test_args),
        patch("src.cli.run_backtest") as mock_backtest,
    ):
        mock_backtest.return_value = 0
        result = main()
        mock_backtest.assert_called_once()
        assert result == 0


def test_main_live_command():
    """Test main() with live command."""
    test_args = [
        "cli.py",
        "live",
        "--symbols",
        "AAPL",
        "--broker",
        "ibkr",
        "--confirm-live",
    ]

    with (
        patch.object(sys, "argv", test_args),
        patch("src.cli.run_live") as mock_live,
    ):
        mock_live.return_value = 0
        result = main()
        mock_live.assert_called_once()
        assert result == 0


def test_main_keyboard_interrupt():
    """Test main() handles KeyboardInterrupt gracefully."""
    test_args = ["cli.py", "simulate", "--symbols", "AAPL"]

    with (
        patch.object(sys, "argv", test_args),
        patch("src.cli.run_simulate") as mock_simulate,
    ):
        mock_simulate.side_effect = KeyboardInterrupt()
        result = main()
        assert result == 0


def test_main_exception_handling():
    """Test main() handles exceptions and returns 1."""
    test_args = ["cli.py", "simulate", "--symbols", "AAPL"]

    with (
        patch.object(sys, "argv", test_args),
        patch("src.cli.run_simulate") as mock_simulate,
    ):
        mock_simulate.side_effect = RuntimeError("Test error")
        result = main()
        assert result == 1


def test_create_risk_limits():
    """Test create_risk_limits helper function."""
    args = Mock()
    args.risk_per_trade = 0.02
    args.risk_per_day = 0.05
    args.max_daily_drawdown = 0.10
    args.max_consecutive_losses = 5
    args.max_positions = 10

    risk_limits = create_risk_limits(args)

    assert isinstance(risk_limits, RiskLimits)
    assert risk_limits.max_risk_per_trade_pct == 0.02
    assert risk_limits.max_risk_per_day_pct == 0.05
    assert risk_limits.max_daily_drawdown_pct == 0.10
    assert risk_limits.max_consecutive_losses == 5
    assert risk_limits.max_open_positions == 10
