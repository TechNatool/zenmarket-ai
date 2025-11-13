"""Comprehensive tests for BacktestEngine.

Tests cover the main backtesting orchestration logic including:
- Configuration validation
- Historical data loading
- Strategy execution simulation
- Performance metrics calculation
- Parallel backtesting
- CLI interface
"""

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from src.advisor.signal_generator import SignalType, TradingSignal
from src.backtest.backtest_engine import (
    BacktestConfig,
    BacktestEngine,
    BacktestResult,
    _run_backtest_worker,
    run_backtest_cli,
)
from src.backtest.metrics import PerformanceMetrics
from src.execution.position_sizing import SizingMethod


@pytest.fixture
def sample_config() -> BacktestConfig:
    """Create a sample backtest configuration."""
    return BacktestConfig(
        symbols=["AAPL", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-01-31",
        initial_capital=Decimal("100000"),
        slippage_bps=1.5,
        commission_per_trade=Decimal("2.0"),
        risk_per_trade_pct=0.01,
        max_positions=5,
        sizing_method=SizingMethod.FIXED_FRACTIONAL,
        strategy_name="TestStrategy",
    )


@pytest.fixture
def sample_historical_data() -> dict[str, pd.DataFrame]:
    """Create sample historical price data for testing."""
    dates = pd.date_range("2024-01-01", periods=20, freq="D")

    def create_df(base_price: float) -> pd.DataFrame:
        """Create a DataFrame with realistic price movements."""
        return pd.DataFrame(
            {
                "Open": [base_price + i * 0.5 for i in range(20)],
                "High": [base_price + i * 0.5 + 2 for i in range(20)],
                "Low": [base_price + i * 0.5 - 2 for i in range(20)],
                "Close": [base_price + i * 0.5 + 1 for i in range(20)],
                "Volume": [1000000 + i * 10000 for i in range(20)],
            },
            index=dates,
        )

    return {
        "AAPL": create_df(150.0),
        "MSFT": create_df(300.0),
    }


@pytest.fixture
def mock_yfinance_ticker():
    """Create a mock yfinance Ticker object."""
    def create_ticker(symbol: str, data: pd.DataFrame) -> Mock:
        ticker = Mock()
        ticker.history = Mock(return_value=data)
        return ticker
    return create_ticker


class TestBacktestConfig:
    """Test BacktestConfig dataclass."""

    def test_config_initialization(self):
        """Test configuration initializes with correct defaults."""
        config = BacktestConfig(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert config.symbols == ["AAPL"]
        assert config.start_date == "2024-01-01"
        assert config.end_date == "2024-12-31"
        assert config.initial_capital == Decimal("100000")
        assert config.slippage_bps == 1.5
        assert config.commission_per_trade == Decimal("2.0")
        assert config.risk_per_trade_pct == 0.01
        assert config.max_positions == 5
        assert config.sizing_method == SizingMethod.FIXED_FRACTIONAL
        assert config.strategy_name == "TechnicalStrategy"

    def test_config_custom_values(self):
        """Test configuration with custom values."""
        config = BacktestConfig(
            symbols=["AAPL", "MSFT", "GOOGL"],
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=Decimal("500000"),
            slippage_bps=2.0,
            commission_per_trade=Decimal("5.0"),
            risk_per_trade_pct=0.02,
            max_positions=10,
            sizing_method=SizingMethod.KELLY,
            strategy_name="CustomStrategy",
        )

        assert config.symbols == ["AAPL", "MSFT", "GOOGL"]
        assert config.initial_capital == Decimal("500000")
        assert config.slippage_bps == 2.0
        assert config.commission_per_trade == Decimal("5.0")
        assert config.risk_per_trade_pct == 0.02
        assert config.max_positions == 10
        assert config.sizing_method == SizingMethod.KELLY
        assert config.strategy_name == "CustomStrategy"


class TestBacktestResult:
    """Test BacktestResult dataclass."""

    def test_result_initialization(self, sample_config):
        """Test result dataclass initialization."""
        # Use mock metrics instead of creating with full signature
        metrics = Mock(spec=PerformanceMetrics)
        metrics.total_return_pct = 25.5
        metrics.total_trades = 100

        equity_df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=10),
            "equity": [100000 + i * 1000 for i in range(10)],
            "cash": [50000 + i * 500 for i in range(10)],
            "drawdown": [0.0] * 10,
        })

        trades = [
            {"symbol": "AAPL", "side": "BUY", "quantity": 10, "price": 150.0},
            {"symbol": "MSFT", "side": "SELL", "quantity": 5, "price": 300.0},
        ]

        signals = [Mock(spec=TradingSignal)]

        result = BacktestResult(
            config=sample_config,
            metrics=metrics,
            equity_curve=equity_df,
            trades=trades,
            signals=signals,
        )

        assert result.config == sample_config
        assert result.metrics == metrics
        assert len(result.equity_curve) == 10
        assert len(result.trades) == 2
        assert len(result.signals) == 1


class TestBacktestEngine:
    """Test BacktestEngine class."""

    def test_engine_initialization(self, sample_config):
        """Test engine initializes correctly."""
        engine = BacktestEngine(sample_config)

        assert engine.config == sample_config
        assert engine.logger is not None

    def test_calculate_drawdown_no_drawdown(self):
        """Test drawdown calculation with increasing equity."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        # Increasing equity = no drawdown
        equity = pd.Series([100000, 105000, 110000, 115000, 120000])
        drawdown = engine._calculate_drawdown(equity)

        # All drawdowns should be 0 (or very close due to floating point)
        assert all(dd <= 0.001 for dd in drawdown)

    def test_calculate_drawdown_with_decline(self):
        """Test drawdown calculation with equity decline."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        # Peak at 120000, then decline
        equity = pd.Series([100000, 110000, 120000, 108000, 96000])
        drawdown = engine._calculate_drawdown(equity)

        # Should have negative drawdown after peak
        assert drawdown.iloc[0] == 0  # At first peak
        assert drawdown.iloc[2] == 0  # At new peak
        assert drawdown.iloc[3] < 0  # Drawdown
        assert drawdown.iloc[4] < drawdown.iloc[3]  # Larger drawdown

    def test_get_common_timestamps_empty_data(self):
        """Test getting common timestamps with empty data."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        timestamps = engine._get_common_timestamps({})
        assert timestamps == []

    def test_get_common_timestamps_single_symbol(self, sample_historical_data):
        """Test getting common timestamps with single symbol."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        data = {"AAPL": sample_historical_data["AAPL"]}
        timestamps = engine._get_common_timestamps(data)

        assert len(timestamps) == len(sample_historical_data["AAPL"])
        assert all(isinstance(ts, datetime) for ts in timestamps)

    def test_get_common_timestamps_multiple_symbols(self, sample_historical_data):
        """Test getting common timestamps across multiple symbols."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL", "MSFT"], start_date="2024-01-01", end_date="2024-12-31")
        )

        timestamps = engine._get_common_timestamps(sample_historical_data)

        # Both symbols have same dates, should return all timestamps
        assert len(timestamps) == len(sample_historical_data["AAPL"])
        assert timestamps == sorted(timestamps)  # Should be sorted

    def test_get_common_timestamps_misaligned_data(self):
        """Test getting common timestamps with misaligned data."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL", "MSFT"], start_date="2024-01-01", end_date="2024-12-31")
        )

        # Create misaligned data
        dates1 = pd.date_range("2024-01-01", periods=10, freq="D")
        dates2 = pd.date_range("2024-01-05", periods=10, freq="D")  # Offset by 5 days

        data = {
            "AAPL": pd.DataFrame({"Close": range(10)}, index=dates1),
            "MSFT": pd.DataFrame({"Close": range(10)}, index=dates2),
        }

        timestamps = engine._get_common_timestamps(data)

        # Should only return overlapping dates (6 days)
        assert len(timestamps) == 6

    @patch("src.backtest.backtest_engine.yf.Ticker")
    def test_load_historical_data(self, mock_ticker_class, sample_config, sample_historical_data):
        """Test loading historical data from yfinance."""
        # Setup mock
        def mock_ticker(symbol):
            ticker = Mock()
            ticker.history = Mock(return_value=sample_historical_data.get(symbol, pd.DataFrame()))
            return ticker

        mock_ticker_class.side_effect = mock_ticker

        engine = BacktestEngine(sample_config)
        data = engine._load_historical_data()

        assert "AAPL" in data
        assert "MSFT" in data
        assert len(data["AAPL"]) == 20
        assert len(data["MSFT"]) == 20

        # Verify yfinance was called correctly
        assert mock_ticker_class.call_count == 2

    @patch("src.backtest.backtest_engine.yf.Ticker")
    def test_load_historical_data_missing_symbol(self, mock_ticker_class, sample_config):
        """Test handling of missing symbol data."""
        # Setup mock to return empty DataFrame for one symbol
        def mock_ticker(symbol):
            ticker = Mock()
            if symbol == "AAPL":
                ticker.history = Mock(return_value=pd.DataFrame())  # Empty data
            else:
                dates = pd.date_range("2024-01-01", periods=20, freq="D")
                ticker.history = Mock(
                    return_value=pd.DataFrame({"Close": range(20)}, index=dates)
                )
            return ticker

        mock_ticker_class.side_effect = mock_ticker

        engine = BacktestEngine(sample_config)
        data = engine._load_historical_data()

        # AAPL should be skipped, only MSFT should be in data
        assert "AAPL" not in data
        assert "MSFT" in data

    def test_calculate_trade_pnl_no_fills(self, sample_config):
        """Test PnL calculation with no fills."""
        engine = BacktestEngine(sample_config)

        # Create mock order with no fills
        mock_order = Mock()
        mock_order.order_id = "test-123"

        mock_broker = Mock()
        mock_broker.get_fills = Mock(return_value=[])

        pnl = engine._calculate_trade_pnl(mock_order, mock_broker)

        assert pnl == Decimal("0")

    @patch("src.backtest.backtest_engine.yf.Ticker")
    @patch("src.backtest.backtest_engine.SignalGenerator")
    @patch("src.backtest.backtest_engine.IndicatorCalculator")
    def test_run_backtest_basic(
        self,
        mock_indicator_calc_class,
        mock_signal_gen_class,
        mock_ticker_class,
        sample_config,
        sample_historical_data,
    ):
        """Test basic backtest execution."""
        # Setup mocks
        def mock_ticker(symbol):
            ticker = Mock()
            ticker.history = Mock(return_value=sample_historical_data.get(symbol, pd.DataFrame()))
            return ticker

        mock_ticker_class.side_effect = mock_ticker

        # Mock signal generator to return HOLD signals
        mock_signal_gen = Mock()
        mock_signal = Mock(spec=TradingSignal)
        mock_signal.signal = Mock()
        mock_signal.signal.value = "HOLD"
        mock_signal_gen.generate_signal = Mock(return_value=mock_signal)
        mock_signal_gen_class.return_value = mock_signal_gen

        # Mock indicator calculator
        mock_indicator_calc = Mock()
        mock_indicators = Mock()
        mock_indicators.symbol = "AAPL"
        mock_indicator_calc.calculate_all_indicators = Mock(return_value=mock_indicators)
        mock_indicator_calc_class.return_value = mock_indicator_calc

        # Run backtest
        engine = BacktestEngine(sample_config)
        result = engine.run()

        # Verify result structure
        assert isinstance(result, BacktestResult)
        assert result.config == sample_config
        assert isinstance(result.metrics, PerformanceMetrics)
        assert isinstance(result.equity_curve, pd.DataFrame)
        assert isinstance(result.trades, list)
        assert isinstance(result.signals, list)

        # Verify equity curve structure
        assert "timestamp" in result.equity_curve.columns
        assert "equity" in result.equity_curve.columns
        assert "cash" in result.equity_curve.columns
        assert "drawdown" in result.equity_curve.columns
        assert len(result.equity_curve) > 0

    @patch("src.backtest.backtest_engine.yf.Ticker")
    @patch("src.backtest.backtest_engine.SignalGenerator")
    @patch("src.backtest.backtest_engine.IndicatorCalculator")
    def test_run_backtest_with_trades(
        self,
        mock_indicator_calc_class,
        mock_signal_gen_class,
        mock_ticker_class,
        sample_config,
        sample_historical_data,
    ):
        """Test backtest with actual BUY/SELL signals."""
        # Setup mocks
        def mock_ticker(symbol):
            ticker = Mock()
            ticker.history = Mock(return_value=sample_historical_data.get(symbol, pd.DataFrame()))
            return ticker

        mock_ticker_class.side_effect = mock_ticker

        # Mock signal generator to alternate between BUY and SELL
        mock_signal_gen = Mock()
        call_count = [0]

        def generate_signal_side_effect(indicators):
            call_count[0] += 1
            signal_type = SignalType.BUY if call_count[0] % 2 == 0 else SignalType.HOLD
            mock_sig = Mock(spec=TradingSignal)
            mock_sig.signal = Mock()
            mock_sig.signal.value = signal_type.value
            mock_sig.ticker = indicators.symbol
            return mock_sig

        mock_signal_gen.generate_signal = Mock(side_effect=generate_signal_side_effect)
        mock_signal_gen_class.return_value = mock_signal_gen

        # Mock indicator calculator
        mock_indicator_calc = Mock()

        def calc_indicators_side_effect(symbol, df):
            indicators = Mock()
            indicators.symbol = symbol
            return indicators

        mock_indicator_calc.calculate_all_indicators = Mock(side_effect=calc_indicators_side_effect)
        mock_indicator_calc_class.return_value = mock_indicator_calc

        # Run backtest
        engine = BacktestEngine(sample_config)
        result = engine.run()

        # Should have generated signals (may be 0 with mocked data)
        # The backtest completes successfully
        assert isinstance(result, BacktestResult)
        assert result.config == sample_config


class TestParallelBacktesting:
    """Test parallel backtesting functionality."""

    @patch("src.backtest.backtest_engine.ProcessPoolExecutor")
    def test_run_parallel_basic(self, mock_executor_class):
        """Test parallel backtest execution."""
        # Create multiple configs
        configs = [
            BacktestConfig(
                symbols=["AAPL"],
                start_date="2024-01-01",
                end_date="2024-01-31",
                strategy_name=f"Strategy{i}",
            )
            for i in range(3)
        ]

        # Mock executor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Mock futures
        mock_futures = {}
        for config in configs:
            mock_future = Mock()
            mock_metrics = Mock(spec=PerformanceMetrics)
            mock_metrics.total_return_pct = 10.0
            mock_metrics.total_trades = 50
            mock_result = BacktestResult(
                config=config,
                metrics=mock_metrics,
                equity_curve=pd.DataFrame(),
                trades=[],
                signals=[],
            )
            mock_future.result = Mock(return_value=mock_result)
            mock_futures[mock_future] = config

        mock_executor.submit = Mock(side_effect=lambda fn, cfg: list(mock_futures.keys())[configs.index(cfg)])

        with patch("src.backtest.backtest_engine.as_completed", return_value=mock_futures.keys()):
            results = BacktestEngine.run_parallel(configs, max_workers=2)

        assert len(results) == 3

    def test_run_backtest_worker(self):
        """Test backtest worker function."""
        config = BacktestConfig(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        with patch.object(BacktestEngine, "run") as mock_run:
            mock_result = Mock(spec=BacktestResult)
            mock_run.return_value = mock_result

            result = _run_backtest_worker(config)

            assert result == mock_result
            mock_run.assert_called_once()


class TestCLIInterface:
    """Test CLI interface for backtesting."""

    @patch("src.backtest.backtest_engine.yf.Ticker")
    @patch("src.backtest.backtest_engine.SignalGenerator")
    @patch("src.backtest.backtest_engine.IndicatorCalculator")
    @patch("src.backtest.backtest_engine.BacktestVisualizer")
    def test_run_backtest_cli_basic(
        self,
        mock_visualizer_class,
        mock_indicator_calc_class,
        mock_signal_gen_class,
        mock_ticker_class,
        tmp_path,
    ):
        """Test CLI backtest execution."""
        # Setup mocks similar to basic backtest test
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        sample_data = pd.DataFrame(
            {
                "Open": [150.0] * 10,
                "High": [152.0] * 10,
                "Low": [149.0] * 10,
                "Close": [151.0] * 10,
                "Volume": [1000000] * 10,
            },
            index=dates,
        )

        mock_ticker = Mock()
        mock_ticker.history = Mock(return_value=sample_data)
        mock_ticker_class.return_value = mock_ticker

        mock_signal_gen = Mock()
        mock_signal = Mock(spec=TradingSignal)
        mock_signal.signal = Mock()
        mock_signal.signal.value = "HOLD"
        mock_signal.ticker = "AAPL"
        mock_signal_gen.generate_signal = Mock(return_value=mock_signal)
        mock_signal_gen_class.return_value = mock_signal_gen

        mock_indicator_calc = Mock()
        mock_indicators = Mock()
        mock_indicators.symbol = "AAPL"
        mock_indicator_calc.calculate_all_indicators = Mock(return_value=mock_indicators)
        mock_indicator_calc_class.return_value = mock_indicator_calc

        # Mock visualizer methods
        mock_visualizer_class.print_summary = Mock()
        mock_visualizer_class.plot_equity_curve = Mock()
        mock_visualizer_class.plot_drawdown = Mock()
        mock_visualizer_class.generate_markdown_report = Mock()
        mock_visualizer_class.generate_pdf_report = Mock()

        # Run CLI backtest
        output_dir = tmp_path / "backtest_output"
        result = run_backtest_cli(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            initial_capital=100000.0,
            output_dir=output_dir,
        )

        # Verify result
        assert isinstance(result, BacktestResult)
        assert result.config.symbols == ["AAPL"]
        assert result.config.initial_capital == Decimal("100000")

        # Verify output directory was created
        assert output_dir.exists()

        # Verify visualizer methods were called
        mock_visualizer_class.print_summary.assert_called_once()
        mock_visualizer_class.plot_equity_curve.assert_called_once()
        mock_visualizer_class.plot_drawdown.assert_called_once()
        mock_visualizer_class.generate_markdown_report.assert_called_once()
        mock_visualizer_class.generate_pdf_report.assert_called_once()

    @patch("src.backtest.backtest_engine.yf.Ticker")
    @patch("src.backtest.backtest_engine.SignalGenerator")
    @patch("src.backtest.backtest_engine.IndicatorCalculator")
    @patch("src.backtest.backtest_engine.BacktestVisualizer")
    def test_run_backtest_cli_default_output_dir(
        self,
        mock_visualizer_class,
        mock_indicator_calc_class,
        mock_signal_gen_class,
        mock_ticker_class,
    ):
        """Test CLI backtest with default output directory."""
        # Setup minimal mocks
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        sample_data = pd.DataFrame(
            {
                "Open": [150.0] * 10,
                "High": [152.0] * 10,
                "Low": [149.0] * 10,
                "Close": [151.0] * 10,
                "Volume": [1000000] * 10,
            },
            index=dates,
        )

        mock_ticker = Mock()
        mock_ticker.history = Mock(return_value=sample_data)
        mock_ticker_class.return_value = mock_ticker

        mock_signal_gen = Mock()
        mock_signal = Mock(spec=TradingSignal)
        mock_signal.signal = Mock()
        mock_signal.signal.value = "HOLD"
        mock_signal.ticker = "AAPL"
        mock_signal_gen.generate_signal = Mock(return_value=mock_signal)
        mock_signal_gen_class.return_value = mock_signal_gen

        mock_indicator_calc = Mock()
        mock_indicators = Mock()
        mock_indicators.symbol = "AAPL"
        mock_indicator_calc.calculate_all_indicators = Mock(return_value=mock_indicators)
        mock_indicator_calc_class.return_value = mock_indicator_calc

        mock_visualizer_class.print_summary = Mock()
        mock_visualizer_class.plot_equity_curve = Mock()
        mock_visualizer_class.plot_drawdown = Mock()
        mock_visualizer_class.generate_markdown_report = Mock()
        mock_visualizer_class.generate_pdf_report = Mock()

        # Run with default output dir
        result = run_backtest_cli(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            initial_capital=50000.0,
        )

        assert isinstance(result, BacktestResult)
        assert result.config.initial_capital == Decimal("50000")

        # Default output directory should be created
        default_output = Path("reports/backtest")
        assert default_output.exists()


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_backtest_with_no_symbols(self):
        """Test backtest initialization with empty symbol list."""
        config = BacktestConfig(
            symbols=[],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # Engine should initialize even with no symbols
        engine = BacktestEngine(config)
        assert engine.config.symbols == []

        # Verify _get_common_timestamps handles empty data
        timestamps = engine._get_common_timestamps({})
        assert timestamps == []

    @patch("src.backtest.backtest_engine.yf.Ticker")
    def test_backtest_with_insufficient_data(self, mock_ticker_class):
        """Test backtest with insufficient data for indicators."""
        # Create very short dataset (less than 50 bars needed for indicators)
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        short_data = pd.DataFrame(
            {
                "Open": [150.0] * 5,
                "High": [152.0] * 5,
                "Low": [149.0] * 5,
                "Close": [151.0] * 5,
                "Volume": [1000000] * 5,
            },
            index=dates,
        )

        mock_ticker = Mock()
        mock_ticker.history = Mock(return_value=short_data)
        mock_ticker_class.return_value = mock_ticker

        config = BacktestConfig(
            symbols=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-01-05",
        )

        engine = BacktestEngine(config)
        result = engine.run()

        # Should complete but skip signal generation due to insufficient data
        assert len(result.trades) == 0

    def test_calculate_drawdown_empty_series(self):
        """Test drawdown calculation with empty series."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        empty_series = pd.Series([])
        drawdown = engine._calculate_drawdown(empty_series)

        assert len(drawdown) == 0

    def test_calculate_drawdown_single_value(self):
        """Test drawdown calculation with single value."""
        engine = BacktestEngine(
            BacktestConfig(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-12-31")
        )

        single_value = pd.Series([100000])
        drawdown = engine._calculate_drawdown(single_value)

        assert len(drawdown) == 1
        assert drawdown.iloc[0] == 0.0
