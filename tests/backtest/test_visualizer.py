"""Tests for backtest visualizer module."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.backtest.metrics import PerformanceMetrics
from src.backtest.visualizer import BacktestVisualizer


@pytest.fixture
def sample_equity_curve():
    """Create sample equity curve data."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    equity = [100000 + i * 100 + (i % 10) * 50 for i in range(100)]
    drawdown = [-0.01 * (i % 5) for i in range(100)]

    return pd.DataFrame({"timestamp": dates, "equity": equity, "drawdown": drawdown})


@pytest.fixture
def sample_trades():
    """Create sample trades data."""
    return [
        {"symbol": "AAPL", "pnl": Decimal("150.50"), "entry_price": 150, "exit_price": 155},
        {"symbol": "MSFT", "pnl": Decimal("-50.25"), "entry_price": 300, "exit_price": 295},
        {"symbol": "GOOGL", "pnl": Decimal("200.00"), "entry_price": 140, "exit_price": 145},
        {"symbol": "TSLA", "pnl": Decimal("-75.00"), "entry_price": 250, "exit_price": 245},
        {"symbol": "AMZN", "pnl": Decimal("300.00"), "entry_price": 180, "exit_price": 185},
    ]


@pytest.fixture
def sample_metrics():
    """Create sample performance metrics."""
    return PerformanceMetrics(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        duration_days=365,
        total_return_pct=15.0,
        annualized_return_pct=15.5,
        cagr_pct=15.2,
        sharpe_ratio=1.8,
        sortino_ratio=2.2,
        calmar_ratio=3.0,
        max_drawdown_pct=-5.0,
        max_drawdown_duration_days=15,
        total_trades=50,
        winning_trades=32,
        losing_trades=18,
        win_rate_pct=64.0,
        profit_factor=2.1,
        avg_win=Decimal("250.00"),
        avg_loss=Decimal("-120.00"),
        avg_trade=Decimal("150.00"),
        largest_win=Decimal("800.00"),
        largest_loss=Decimal("-400.00"),
        avg_risk_reward_ratio=2.0,
        expectancy=Decimal("160.00"),
        final_equity=Decimal("115000"),
        peak_equity=Decimal("120000"),
        avg_daily_return_pct=0.041,
        volatility_annualized_pct=10.5,
        max_consecutive_wins=7,
        max_consecutive_losses=4,
    )


def test_visualizer_runs_without_error(sample_equity_curve):
    """Test that visualizer methods run without error."""
    visualizer = BacktestVisualizer()

    # Should not raise exceptions
    png_bytes = visualizer.plot_equity_curve(sample_equity_curve)
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0


def test_visualizer_outputs_png(sample_equity_curve, tmp_path):
    """Test that visualizer outputs PNG file."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "equity_curve.png"

    result = visualizer.plot_equity_curve(sample_equity_curve, output_path=output_file)

    assert result is None  # Returns None when output_path is provided
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_visualizer_outputs_markdown(sample_metrics, tmp_path):
    """Test that visualizer outputs Markdown report."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "report.md"

    visualizer.generate_markdown_report(
        metrics=sample_metrics,
        strategy_name="Test Strategy",
        symbols=["AAPL", "MSFT"],
        output_path=output_file,
    )

    assert output_file.exists()
    content = output_file.read_text()

    # Check key sections are present
    assert "# Backtest Report: Test Strategy" in content
    assert "## Performance Summary" in content
    assert "## Trade Statistics" in content
    assert "Total Return" in content
    assert "Sharpe Ratio" in content
    assert "AAPL, MSFT" in content


def test_visualizer_drawdown_curve(sample_equity_curve):
    """Test drawdown curve generation."""
    visualizer = BacktestVisualizer()

    png_bytes = visualizer.plot_drawdown(sample_equity_curve)

    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0


def test_visualizer_drawdown_curve_to_file(sample_equity_curve, tmp_path):
    """Test drawdown curve saved to file."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "drawdown.png"

    result = visualizer.plot_drawdown(sample_equity_curve, output_path=output_file)

    assert result is None
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_visualizer_handles_empty_backtest():
    """Test visualizer handles empty equity curve gracefully."""
    visualizer = BacktestVisualizer()

    # Empty DataFrame
    empty_df = pd.DataFrame({"timestamp": [], "equity": [], "drawdown": []})

    # Should handle empty data without crashing
    try:
        png_bytes = visualizer.plot_equity_curve(empty_df)
        # If it doesn't crash, that's good
        assert png_bytes is None or isinstance(png_bytes, bytes)
    except Exception as e:
        # Empty data might raise an error, which is acceptable
        assert "empty" in str(e).lower() or "no data" in str(e).lower()


def test_visualizer_returns_distribution(sample_trades):
    """Test returns distribution plot."""
    visualizer = BacktestVisualizer()

    png_bytes = visualizer.plot_returns_distribution(sample_trades)

    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0


def test_visualizer_returns_distribution_to_file(sample_trades, tmp_path):
    """Test returns distribution saved to file."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "returns_dist.png"

    result = visualizer.plot_returns_distribution(sample_trades, output_path=output_file)

    assert result is None
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_generate_pdf_report_with_mock(
    sample_metrics, sample_equity_curve, sample_trades, tmp_path
):
    """Test PDF generation with mocked ReportLab."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "report.pdf"

    # Mock ReportLab to avoid actual PDF I/O
    with patch("src.backtest.visualizer.SimpleDocTemplate") as mock_doc:
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        visualizer.generate_pdf_report(
            metrics=sample_metrics,
            strategy_name="Test Strategy",
            symbols=["AAPL", "MSFT"],
            _equity_curve=sample_equity_curve,
            _trades=sample_trades,
            output_path=output_file,
        )

        # Verify SimpleDocTemplate was called
        mock_doc.assert_called_once_with(str(output_file), pagesize=MagicMock())
        mock_doc_instance.build.assert_called_once()


def test_print_summary_runs(sample_metrics):
    """Test print_summary runs without error."""
    visualizer = BacktestVisualizer()

    # Should not raise exceptions
    visualizer.print_summary(sample_metrics, "Test Strategy")


def test_equity_curve_with_different_lengths():
    """Test equity curve with various data lengths."""
    visualizer = BacktestVisualizer()

    # Test with minimal data (2 points)
    dates = pd.date_range(start="2024-01-01", periods=2, freq="D")
    equity = [100000, 105000]
    drawdown = [0, -0.01]
    df = pd.DataFrame({"timestamp": dates, "equity": equity, "drawdown": drawdown})

    png_bytes = visualizer.plot_equity_curve(df)
    assert isinstance(png_bytes, bytes)

    # Test with large dataset (1000 points)
    dates = pd.date_range(start="2024-01-01", periods=1000, freq="H")
    equity = [100000 + i * 10 for i in range(1000)]
    drawdown = [-0.001 * (i % 100) for i in range(1000)]
    df = pd.DataFrame({"timestamp": dates, "equity": equity, "drawdown": drawdown})

    png_bytes = visualizer.plot_equity_curve(df)
    assert isinstance(png_bytes, bytes)


def test_markdown_report_content(sample_metrics, tmp_path):
    """Test markdown report contains all expected metrics."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "report.md"

    visualizer.generate_markdown_report(
        metrics=sample_metrics,
        strategy_name="Advanced Strategy",
        symbols=["AAPL", "MSFT", "GOOGL"],
        output_path=output_file,
    )

    content = output_file.read_text()

    # Check all key metrics are present
    assert "15.00%" in content  # Total return
    assert "1.8" in content or "1.80" in content  # Sharpe ratio
    assert "50" in content  # Total trades
    assert "64.0%" in content or "64.1%" in content  # Win rate
    assert "2.1" in content or "2.10" in content  # Profit factor
    assert "Advanced Strategy" in content
    assert "AAPL, MSFT, GOOGL" in content


def test_visualizer_with_negative_returns():
    """Test visualizer handles negative returns correctly."""
    visualizer = BacktestVisualizer()

    # Create declining equity curve
    dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
    equity = [100000 - i * 500 for i in range(50)]  # Declining
    drawdown = [-i * 0.005 for i in range(50)]
    df = pd.DataFrame({"timestamp": dates, "equity": equity, "drawdown": drawdown})

    png_bytes = visualizer.plot_equity_curve(df)
    assert isinstance(png_bytes, bytes)

    png_bytes = visualizer.plot_drawdown(df)
    assert isinstance(png_bytes, bytes)


def test_visualizer_with_all_losing_trades():
    """Test visualizer handles all losing trades."""
    visualizer = BacktestVisualizer()

    losing_trades = [
        {"symbol": "AAPL", "pnl": Decimal("-100.00")},
        {"symbol": "MSFT", "pnl": Decimal("-50.00")},
        {"symbol": "GOOGL", "pnl": Decimal("-75.00")},
    ]

    png_bytes = visualizer.plot_returns_distribution(losing_trades)
    assert isinstance(png_bytes, bytes)


def test_visualizer_with_all_winning_trades():
    """Test visualizer handles all winning trades."""
    visualizer = BacktestVisualizer()

    winning_trades = [
        {"symbol": "AAPL", "pnl": Decimal("100.00")},
        {"symbol": "MSFT", "pnl": Decimal("50.00")},
        {"symbol": "GOOGL", "pnl": Decimal("75.00")},
    ]

    png_bytes = visualizer.plot_returns_distribution(winning_trades)
    assert isinstance(png_bytes, bytes)


def test_pdf_report_structure(sample_metrics, sample_equity_curve, sample_trades, tmp_path):
    """Test PDF report has correct structure."""
    visualizer = BacktestVisualizer()
    output_file = tmp_path / "report.pdf"

    with (
        patch("src.backtest.visualizer.SimpleDocTemplate") as mock_doc,
        patch("src.backtest.visualizer.Paragraph") as mock_para,
        patch("src.backtest.visualizer.Table") as mock_table,
    ):
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance

        visualizer.generate_pdf_report(
            metrics=sample_metrics,
            strategy_name="Test Strategy",
            symbols=["AAPL"],
            _equity_curve=sample_equity_curve,
            _trades=sample_trades,
            output_path=output_file,
        )

        # Verify Paragraph and Table were called (structure elements)
        assert mock_para.call_count > 0
        assert mock_table.call_count > 0


def test_visualizer_matplotlib_backend():
    """Test that matplotlib uses non-interactive backend."""
    import matplotlib

    backend = matplotlib.get_backend()
    assert backend == "agg" or backend == "Agg"
