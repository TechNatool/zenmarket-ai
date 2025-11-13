"""Comprehensive tests for cli.py to reach 90% coverage."""

import sys
from argparse import Namespace
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.advisor.indicators import TechnicalIndicators
from src.advisor.signal_generator import SignalType, TradingSignal
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


@pytest.fixture
def mock_args_simulate():
    """Create mock args for simulate command."""
    return Namespace(
        command="simulate",
        symbols="AAPL,MSFT",
        order_type="market",
        risk_per_trade=0.01,
        risk_per_day=0.03,
        max_daily_drawdown=0.05,
        max_consecutive_losses=3,
        max_positions=5,
        sizing_method="fixed_fractional",
        dry_run=False,
        journal_pdf=False,
        initial_capital=100000.0,
        slippage_bps=1.5,
        commission=2.0,
    )


@pytest.fixture
def mock_args_backtest():
    """Create mock args for backtest command."""
    return Namespace(
        command="backtest",
        symbols="^GDAXI",
        start_date="2024-01-01",
        end_date="2024-12-31",
        interval="1d",
        order_type="market",
        risk_per_trade=0.01,
        risk_per_day=0.03,
        max_daily_drawdown=0.05,
        max_consecutive_losses=3,
        max_positions=5,
        sizing_method="fixed_fractional",
        dry_run=False,
        journal_pdf=False,
        initial_capital=100000.0,
    )


@pytest.fixture
def mock_args_live():
    """Create mock args for live command."""
    return Namespace(
        command="live",
        symbols="BTC-USD",
        broker="ibkr",
        confirm_live=True,
        order_type="limit",
        risk_per_trade=0.01,
        risk_per_day=0.03,
        max_daily_drawdown=0.05,
        max_consecutive_losses=3,
        max_positions=5,
        sizing_method="kelly",
        dry_run=False,
        journal_pdf=False,
        initial_capital=100000.0,
    )


@pytest.fixture
def mock_market_data():
    """Create mock market data (yfinance ticker history)."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    data = {
        "Open": [100 + i * 0.5 for i in range(100)],
        "High": [102 + i * 0.5 for i in range(100)],
        "Low": [98 + i * 0.5 for i in range(100)],
        "Close": [101 + i * 0.5 for i in range(100)],
        "Volume": [1000000 + i * 1000 for i in range(100)],
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def mock_indicators():
    """Create mock technical indicators."""
    return TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=148.0,
        ma_50=145.0,
        rsi=55.0,
        bb_upper=155.0,
        bb_middle=150.0,
        bb_lower=145.0,
        volume_avg=1000000.0,
        current_volume=1200000,
        atr=2.5,
    )


@pytest.fixture
def mock_signal(mock_indicators):
    """Create mock trading signal."""
    return TradingSignal(
        ticker="AAPL",
        signal=SignalType.BUY,
        confidence=0.75,
        reasons=["MA crossover", "RSI neutral"],
        indicators=mock_indicators,
    )


# ============================================================================
# Test Argument Parsing
# ============================================================================


def test_parse_args_simulate():
    """Test parse_args for simulate command."""
    with patch.object(
        sys,
        "argv",
        [
            "cli",
            "simulate",
            "--symbols",
            "AAPL,MSFT",
            "--order-type",
            "market",
            "--risk-per-trade",
            "0.02",
        ],
    ):
        args = parse_args()
        assert args.command == "simulate"
        assert args.symbols == "AAPL,MSFT"
        assert args.order_type == "market"
        assert args.risk_per_trade == 0.02


def test_parse_args_backtest():
    """Test parse_args for backtest command."""
    with patch.object(
        sys,
        "argv",
        [
            "cli",
            "backtest",
            "--symbols",
            "^GDAXI",
            "--from",
            "2024-01-01",
            "--to",
            "2024-12-31",
            "--interval",
            "1d",
        ],
    ):
        args = parse_args()
        assert args.command == "backtest"
        assert args.symbols == "^GDAXI"
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.interval == "1d"


def test_parse_args_live():
    """Test parse_args for live command."""
    with patch.object(
        sys,
        "argv",
        [
            "cli",
            "live",
            "--symbols",
            "BTC-USD",
            "--broker",
            "ibkr",
            "--confirm-live",
            "--order-type",
            "limit",
        ],
    ):
        args = parse_args()
        assert args.command == "live"
        assert args.broker == "ibkr"
        assert args.confirm_live is True


def test_add_common_args():
    """Test add_common_args adds all required arguments."""
    import argparse

    parser = argparse.ArgumentParser()
    add_common_args(parser)

    # Parse with required symbols
    args = parser.parse_args(["--symbols", "AAPL"])

    assert args.symbols == "AAPL"
    assert args.order_type == "market"  # default
    assert args.risk_per_trade == 0.01  # default
    assert args.max_positions == 5  # default


def test_create_risk_limits(mock_args_simulate):
    """Test create_risk_limits creates correct RiskLimits object."""
    risk_limits = create_risk_limits(mock_args_simulate)

    assert risk_limits.max_risk_per_trade_pct == 0.01
    assert risk_limits.max_risk_per_day_pct == 0.03
    assert risk_limits.max_daily_drawdown_pct == 0.05
    assert risk_limits.max_consecutive_losses == 3
    assert risk_limits.max_open_positions == 5


def test_get_order_type():
    """Test get_order_type converts strings to OrderType enum."""
    assert get_order_type("market") == OrderType.MARKET
    assert get_order_type("limit") == OrderType.LIMIT
    assert get_order_type("stop") == OrderType.STOP
    assert get_order_type("stop_limit") == OrderType.STOP_LIMIT
    assert get_order_type("invalid") == OrderType.MARKET  # default fallback


def test_get_sizing_method():
    """Test get_sizing_method converts strings to SizingMethod enum."""
    assert get_sizing_method("fixed_fractional") == SizingMethod.FIXED_FRACTIONAL
    assert get_sizing_method("kelly") == SizingMethod.KELLY
    assert get_sizing_method("fixed_dollar") == SizingMethod.FIXED_DOLLAR
    assert get_sizing_method("invalid") == SizingMethod.FIXED_FRACTIONAL  # default


# ============================================================================
# Test run_simulate()
# ============================================================================


def test_run_simulate_success(mock_args_simulate, mock_market_data, mock_indicators, mock_signal):
    """Test run_simulate executes successfully with valid data."""
    with (
        patch("src.cli.BrokerSimulator") as MockBrokerSimulator,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        # Setup mocks
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        MockBrokerSimulator.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.execute_signal.return_value = Mock(order_id="ORDER123")
        mock_engine.get_status.return_value = {
            "broker": "Simulator",
            "connected": True,
            "performance": {
                "initial_equity": 100000,
                "current_equity": 105000,
                "total_return": "5.00%",
                "max_drawdown": "-2.50%",
                "total_trades": 5,
                "win_rate": "60.00%",
            },
            "risk_summary": {
                "state": {
                    "trading_halted": False,
                    "consecutive_losses": 0,
                    "daily_pnl": "500.00",
                }
            },
        }
        mock_engine.shutdown.return_value = None
        MockExecutionEngine.return_value = mock_engine

        mock_calculator = Mock()
        mock_calculator.calculate_all_indicators.return_value = mock_indicators
        MockIndicatorCalculator.return_value = mock_calculator

        mock_generator = Mock()
        mock_generator.generate_signal.return_value = mock_signal
        MockSignalGenerator.return_value = mock_generator

        # Setup yfinance mock
        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_market_data
        mock_ticker_class.return_value = mock_ticker

        # Execute
        run_simulate(mock_args_simulate)

        # Verify
        MockBrokerSimulator.assert_called_once()
        mock_broker.connect.assert_called_once()
        MockExecutionEngine.assert_called_once()
        mock_calculator.calculate_all_indicators.assert_called()
        mock_generator.generate_signal.assert_called()
        mock_engine.execute_signal.assert_called()
        mock_engine.shutdown.assert_called_once()


def test_run_simulate_insufficient_data(mock_args_simulate):
    """Test run_simulate handles insufficient data gracefully."""
    with (
        patch("src.cli.BrokerSimulator") as MockBrokerSimulator,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        MockBrokerSimulator.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.get_status.return_value = {
            "broker": "Simulator",
            "connected": True,
            "risk_summary": {"state": {}},
        }
        MockExecutionEngine.return_value = mock_engine

        MockIndicatorCalculator.return_value = Mock()
        MockSignalGenerator.return_value = Mock()

        # Empty dataframe (insufficient data)
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker

        # Should not crash
        run_simulate(mock_args_simulate)

        mock_engine.shutdown.assert_called_once()


def test_run_simulate_no_indicators(mock_args_simulate, mock_market_data):
    """Test run_simulate when indicators calculation fails."""
    with (
        patch("src.cli.BrokerSimulator") as MockBrokerSimulator,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        MockBrokerSimulator.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.get_status.return_value = {
            "broker": "Simulator",
            "connected": True,
            "risk_summary": {"state": {}},
        }
        MockExecutionEngine.return_value = mock_engine

        # Indicators calculation returns None
        mock_calculator = Mock()
        mock_calculator.calculate_all_indicators.return_value = None
        MockIndicatorCalculator.return_value = mock_calculator

        MockSignalGenerator.return_value = Mock()

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_market_data
        mock_ticker_class.return_value = mock_ticker

        # Should handle gracefully
        run_simulate(mock_args_simulate)

        mock_engine.shutdown.assert_called_once()


def test_run_simulate_symbol_error(mock_args_simulate, mock_market_data):
    """Test run_simulate handles symbol processing errors."""
    with (
        patch("src.cli.BrokerSimulator") as MockBrokerSimulator,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        MockBrokerSimulator.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.get_status.return_value = {
            "broker": "Simulator",
            "connected": True,
            "risk_summary": {"state": {}},
        }
        MockExecutionEngine.return_value = mock_engine

        MockIndicatorCalculator.return_value = Mock()
        MockSignalGenerator.return_value = Mock()

        # Simulate yfinance error
        mock_ticker_class.side_effect = Exception("Network error")

        # Should handle error and continue
        run_simulate(mock_args_simulate)

        mock_engine.shutdown.assert_called_once()


def test_run_simulate_dry_run(mock_args_simulate, mock_market_data, mock_indicators, mock_signal):
    """Test run_simulate with dry-run mode enabled."""
    mock_args_simulate.dry_run = True

    with (
        patch("src.cli.BrokerSimulator") as MockBrokerSimulator,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        mock_broker = Mock()
        MockBrokerSimulator.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.get_status.return_value = {
            "broker": "Simulator",
            "connected": True,
            "risk_summary": {"state": {}},
        }
        MockExecutionEngine.return_value = mock_engine

        mock_calculator = Mock()
        mock_calculator.calculate_all_indicators.return_value = mock_indicators
        MockIndicatorCalculator.return_value = mock_calculator

        mock_generator = Mock()
        mock_generator.generate_signal.return_value = mock_signal
        MockSignalGenerator.return_value = mock_generator

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_market_data
        mock_ticker_class.return_value = mock_ticker

        run_simulate(mock_args_simulate)

        # Verify dry_run was passed to execute_signal
        mock_engine.execute_signal.assert_called()
        call_kwargs = mock_engine.execute_signal.call_args[1]
        assert call_kwargs["dry_run"] is True


# ============================================================================
# Test run_backtest()
# ============================================================================


def test_run_backtest_success(mock_args_backtest):
    """Test run_backtest executes successfully."""
    with patch("src.cli.run_backtest_cli") as mock_run_backtest_cli:
        mock_run_backtest_cli.return_value = None

        result = run_backtest(mock_args_backtest)

        assert result == 0
        mock_run_backtest_cli.assert_called_once()
        call_kwargs = mock_run_backtest_cli.call_args[1]
        assert call_kwargs["symbols"] == ["^GDAXI"]
        assert call_kwargs["start_date"] == "2024-01-01"
        assert call_kwargs["end_date"] == "2024-12-31"
        assert call_kwargs["initial_capital"] == 100000.0


def test_run_backtest_failure(mock_args_backtest):
    """Test run_backtest handles errors."""
    with patch("src.cli.run_backtest_cli") as mock_run_backtest_cli:
        mock_run_backtest_cli.side_effect = Exception("Backtest engine error")

        result = run_backtest(mock_args_backtest)

        assert result == 1


def test_run_backtest_multiple_symbols(mock_args_backtest):
    """Test run_backtest with multiple symbols."""
    mock_args_backtest.symbols = "AAPL,MSFT,GOOGL"

    with patch("src.cli.run_backtest_cli") as mock_run_backtest_cli:
        run_backtest(mock_args_backtest)

        call_kwargs = mock_run_backtest_cli.call_args[1]
        assert call_kwargs["symbols"] == ["AAPL", "MSFT", "GOOGL"]


# ============================================================================
# Test run_live()
# ============================================================================


def test_run_live_no_confirmation(mock_args_live):
    """Test run_live returns error without confirmation flag."""
    mock_args_live.confirm_live = False

    result = run_live(mock_args_live)

    assert result == 1


def test_run_live_user_cancels(mock_args_live):
    """Test run_live when user cancels at confirmation prompt."""
    with patch("builtins.input", return_value="NO"):
        result = run_live(mock_args_live)

        assert result == 0  # Graceful exit


def test_run_live_keyboard_interrupt(mock_args_live):
    """Test run_live handles Ctrl+C at confirmation."""
    with patch("builtins.input", side_effect=KeyboardInterrupt()):
        result = run_live(mock_args_live)

        assert result == 0  # Graceful exit


def test_run_live_broker_connection_fails(mock_args_live):
    """Test run_live when broker connection fails."""
    with (
        patch("builtins.input", return_value="I UNDERSTAND THE RISKS"),
        patch("src.cli.BrokerFactory") as MockBrokerFactory,
    ):
        mock_broker = Mock()
        mock_broker.connect.return_value = False
        MockBrokerFactory.create_from_env.return_value = mock_broker

        result = run_live(mock_args_live)

        assert result == 1
        mock_broker.connect.assert_called_once()


def test_run_live_success(mock_args_live, mock_market_data, mock_indicators, mock_signal):
    """Test run_live executes successfully."""
    with (
        patch("builtins.input", return_value="I UNDERSTAND THE RISKS"),
        patch("src.cli.BrokerFactory") as MockBrokerFactory,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        # Setup broker
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        mock_broker.disconnect.return_value = None
        MockBrokerFactory.create_from_env.return_value = mock_broker

        # Setup execution engine
        mock_engine = Mock()
        mock_engine.execute_signal.return_value = [Mock(order_id="LIVE123")]
        mock_engine.get_status.return_value = {
            "broker": "IBKR",
            "connected": True,
        }
        mock_engine.shutdown.return_value = None
        MockExecutionEngine.return_value = mock_engine

        # Setup indicators and signals
        mock_calculator = Mock()
        mock_calculator.calculate_all_indicators.return_value = mock_indicators
        MockIndicatorCalculator.return_value = mock_calculator

        mock_generator = Mock()
        mock_generator.generate_signal.return_value = mock_signal
        MockSignalGenerator.return_value = mock_generator

        # Setup market data
        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_market_data
        mock_ticker_class.return_value = mock_ticker

        # Execute
        result = run_live(mock_args_live)

        # Verify
        assert result == 0
        mock_broker.connect.assert_called_once()
        mock_broker.disconnect.assert_called_once()
        mock_engine.execute_signal.assert_called()
        mock_engine.shutdown.assert_called_once()


def test_run_live_mt5_broker(mock_args_live, mock_market_data, mock_indicators, mock_signal):
    """Test run_live with MT5 broker."""
    mock_args_live.broker = "mt5"

    with (
        patch("builtins.input", return_value="I UNDERSTAND THE RISKS"),
        patch("src.cli.BrokerFactory") as MockBrokerFactory,
        patch("src.cli.ExecutionEngine") as MockExecutionEngine,
        patch("src.cli.IndicatorCalculator") as MockIndicatorCalculator,
        patch("src.cli.SignalGenerator") as MockSignalGenerator,
        patch("yfinance.Ticker") as mock_ticker_class,
    ):
        mock_broker = Mock()
        mock_broker.connect.return_value = True
        MockBrokerFactory.create_from_env.return_value = mock_broker

        mock_engine = Mock()
        mock_engine.get_status.return_value = {"broker": "MT5", "connected": True}
        MockExecutionEngine.return_value = mock_engine

        mock_calculator = Mock()
        mock_calculator.calculate_all_indicators.return_value = mock_indicators
        MockIndicatorCalculator.return_value = mock_calculator

        mock_generator = Mock()
        mock_generator.generate_signal.return_value = mock_signal
        MockSignalGenerator.return_value = mock_generator

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_market_data
        mock_ticker_class.return_value = mock_ticker

        result = run_live(mock_args_live)

        assert result == 0


def test_run_live_exception(mock_args_live):
    """Test run_live handles general exceptions."""
    with (
        patch("builtins.input", return_value="I UNDERSTAND THE RISKS"),
        patch("src.cli.BrokerFactory") as MockBrokerFactory,
    ):
        MockBrokerFactory.create_from_env.side_effect = Exception("Critical error")

        result = run_live(mock_args_live)

        assert result == 1


# ============================================================================
# Test main()
# ============================================================================


def test_main_simulate():
    """Test main() routes to simulate command."""
    with (
        patch.object(sys, "argv", ["cli", "simulate", "--symbols", "AAPL"]),
        patch("src.cli.run_simulate") as mock_run_simulate,
    ):
        mock_run_simulate.return_value = None

        result = main()

        mock_run_simulate.assert_called_once()


def test_main_backtest():
    """Test main() routes to backtest command."""
    with (
        patch.object(
            sys,
            "argv",
            [
                "cli",
                "backtest",
                "--symbols",
                "^GDAXI",
                "--from",
                "2024-01-01",
                "--to",
                "2024-12-31",
            ],
        ),
        patch("src.cli.run_backtest") as mock_run_backtest,
    ):
        mock_run_backtest.return_value = 0

        result = main()

        mock_run_backtest.assert_called_once()


def test_main_live():
    """Test main() routes to live command."""
    with (
        patch.object(
            sys,
            "argv",
            ["cli", "live", "--symbols", "BTC-USD", "--broker", "ibkr", "--confirm-live"],
        ),
        patch("src.cli.run_live") as mock_run_live,
    ):
        mock_run_live.return_value = 0

        result = main()

        mock_run_live.assert_called_once()


def test_main_exception():
    """Test main() handles exceptions."""
    with (
        patch.object(sys, "argv", ["cli", "simulate", "--symbols", "AAPL"]),
        patch("src.cli.run_simulate") as mock_run_simulate,
    ):
        mock_run_simulate.side_effect = Exception("Unexpected error")

        result = main()

        # Should return non-zero on error
        assert result is not None
