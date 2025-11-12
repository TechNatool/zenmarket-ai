"""Backtesting engine for historical strategy testing.

Orchestrates historical data replay, signal generation, order execution,
and performance analysis.
"""

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from src.advisor.indicators import IndicatorCalculator
from src.advisor.signal_generator import SignalGenerator, TradingSignal
from src.backtest.backtest_broker import BacktestBroker
from src.backtest.metrics import PerformanceMetrics
from src.backtest.visualizer import BacktestVisualizer
from src.execution.execution_engine import ExecutionEngine
from src.execution.position_sizing import PositionSizingMethod
from src.execution.risk_manager import RiskLimits
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""

    symbols: list[str]
    start_date: str
    end_date: str
    initial_capital: Decimal = Decimal("100000")
    slippage_bps: float = 1.5
    commission_per_trade: Decimal = Decimal("2.0")
    risk_per_trade_pct: float = 0.01
    max_positions: int = 5
    sizing_method: PositionSizingMethod = PositionSizingMethod.FIXED_FRACTIONAL
    strategy_name: str = "TechnicalStrategy"


@dataclass
class BacktestResult:
    """Results from a backtest run."""

    config: BacktestConfig
    metrics: PerformanceMetrics
    equity_curve: pd.DataFrame
    trades: list[dict[str, Any]]
    signals: list[TradingSignal]


class BacktestEngine:
    """Main backtesting engine."""

    def __init__(self, config: BacktestConfig) -> None:
        """Initialize backtest engine.

        Args:
            config: Backtest configuration
        """
        self.config = config
        self.logger = get_logger(f"backtest.{config.strategy_name}")

    def run(self) -> BacktestResult:
        """Run the backtest.

        Returns:
            BacktestResult with performance metrics and trade history
        """
        self.logger.info(
            f"Starting backtest: {self.config.symbols} "
            f"from {self.config.start_date} to {self.config.end_date}"
        )

        # 1. Load historical data
        historical_data = self._load_historical_data()

        # 2. Initialize broker
        broker = BacktestBroker(
            historical_data=historical_data,
            initial_cash=self.config.initial_capital,
            slippage_bps=self.config.slippage_bps,
            commission_per_trade=self.config.commission_per_trade,
        )
        broker.connect()

        # 3. Initialize execution engine
        risk_limits = RiskLimits(
            max_risk_per_trade_pct=self.config.risk_per_trade_pct,
            max_open_positions=self.config.max_positions,
        )

        execution_engine = ExecutionEngine(
            broker=broker,
            risk_limits=risk_limits,
            default_sizing_method=self.config.sizing_method,
            dry_run=False,  # Execute in backtest
        )

        # 4. Initialize signal generator and indicator calculator
        signal_generator = SignalGenerator()
        indicator_calculator = IndicatorCalculator()

        # 5. Run simulation
        equity_curve_data = []
        all_signals = []
        all_trades = []

        # Get common timestamps across all symbols
        timestamps = self._get_common_timestamps(historical_data)

        self.logger.info(f"Simulating {len(timestamps)} bars...")

        for i, timestamp in enumerate(timestamps):
            # Set current bar for all symbols
            current_bars = {}
            for symbol in self.config.symbols:
                df = historical_data[symbol]
                bar_data = df[df.index == timestamp]
                if not bar_data.empty:
                    current_bars[symbol] = {
                        "Open": bar_data["Open"].iloc[0],
                        "High": bar_data["High"].iloc[0],
                        "Low": bar_data["Low"].iloc[0],
                        "Close": bar_data["Close"].iloc[0],
                        "Volume": bar_data["Volume"].iloc[0],
                    }

            broker.set_current_bar(timestamp, current_bars)

            # Generate signals for each symbol
            for symbol in self.config.symbols:
                if symbol not in current_bars:
                    continue

                # Calculate indicators up to current bar
                df_up_to_now = historical_data[symbol][historical_data[symbol].index <= timestamp]
                if len(df_up_to_now) < 50:  # Need minimum bars for indicators
                    continue

                try:
                    indicators = indicator_calculator.calculate_all_indicators(symbol, df_up_to_now)
                    signal = signal_generator.generate_signal(indicators)
                    all_signals.append(signal)

                    # Execute signal if actionable
                    if signal.signal.value != "HOLD":
                        orders = execution_engine.execute_signal(signal)
                        # Track filled orders as trades
                        for order in orders:
                            if order.filled_quantity > 0:
                                all_trades.append(
                                    {
                                        "timestamp": timestamp,
                                        "symbol": order.symbol,
                                        "side": order.side.value,
                                        "quantity": float(order.filled_quantity),
                                        "price": float(order.avg_fill_price or Decimal("0")),
                                        "pnl": self._calculate_trade_pnl(order, broker),
                                    }
                                )

                except Exception as e:
                    self.logger.warning(f"Error processing {symbol} at {timestamp}: {e}")

            # Record equity curve
            account = broker.get_account()
            equity_curve_data.append(
                {
                    "timestamp": timestamp,
                    "equity": float(account.equity),
                    "cash": float(account.cash),
                    "drawdown": 0.0,  # Will calculate later
                }
            )

            # Progress logging
            if (i + 1) % 100 == 0:
                self.logger.info(f"Processed {i + 1}/{len(timestamps)} bars")

        broker.disconnect()

        # 6. Build equity curve DataFrame
        equity_df = pd.DataFrame(equity_curve_data)
        equity_df["drawdown"] = self._calculate_drawdown(equity_df["equity"])

        # 7. Calculate performance metrics
        metrics = PerformanceMetrics.calculate(
            equity_curve=equity_df,
            trades=all_trades,
            initial_capital=self.config.initial_capital,
        )

        self.logger.info(
            f"Backtest complete: {metrics.total_trades} trades, {metrics.total_return_pct:.2f}% return"
        )

        return BacktestResult(
            config=self.config,
            metrics=metrics,
            equity_curve=equity_df,
            trades=all_trades,
            signals=all_signals,
        )

    def _load_historical_data(self) -> dict[str, pd.DataFrame]:
        """Load historical data for all symbols.

        Returns:
            Dict mapping symbols to DataFrames
        """
        data = {}
        for symbol in self.config.symbols:
            self.logger.info(f"Loading data for {symbol}...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=self.config.start_date, end=self.config.end_date)

            if df.empty:
                self.logger.warning(f"No data available for {symbol}")
                continue

            data[symbol] = df

        return data

    def _get_common_timestamps(self, data: dict[str, pd.DataFrame]) -> list[datetime]:
        """Get timestamps common across all symbols."""
        if not data:
            return []

        # Get intersection of all timestamps
        common_timestamps = None
        for df in data.values():
            timestamps = set(df.index.to_pydatetime())
            if common_timestamps is None:
                common_timestamps = timestamps
            else:
                common_timestamps = common_timestamps.intersection(timestamps)

        if common_timestamps is None:
            return []

        return sorted(common_timestamps)

    def _calculate_drawdown(self, equity: pd.Series) -> pd.Series:
        """Calculate drawdown series.

        Args:
            equity: Equity curve series

        Returns:
            Drawdown series (negative values)
        """
        peak = equity.expanding().max()
        return (equity - peak) / peak

    def _calculate_trade_pnl(self, order: Any, broker: BacktestBroker) -> Decimal:
        """Calculate PnL for a trade.

        This is a simplified calculation. In reality, you'd track entry/exit pairs.
        """
        # Get fills for this order
        fills = broker.get_fills(order_id=order.order_id)
        if not fills:
            return Decimal("0")

        # For now, return 0 as we track realized PnL separately
        # This would need to be enhanced to match entry/exit trades
        return Decimal("0")

    @staticmethod
    def run_parallel(
        configs: list[BacktestConfig],
        max_workers: int | None = None,
    ) -> list[BacktestResult]:
        """Run multiple backtests in parallel.

        Args:
            configs: List of backtest configurations
            max_workers: Maximum number of parallel workers (default: CPU count)

        Returns:
            List of BacktestResults
        """
        if max_workers is None:
            max_workers = mp.cpu_count()

        results = []

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all backtests
            futures = {executor.submit(_run_backtest_worker, config): config for config in configs}

            # Collect results as they complete
            for future in as_completed(futures):
                config = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed backtest: {config.strategy_name}")
                except Exception as e:
                    logger.exception(f"Backtest failed for {config.strategy_name}: {e}")

        return results


def _run_backtest_worker(config: BacktestConfig) -> BacktestResult:
    """Worker function for parallel backtesting."""
    engine = BacktestEngine(config)
    return engine.run()


def run_backtest_cli(
    symbols: list[str],
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0,
    output_dir: Path | None = None,
) -> BacktestResult:
    """Run a backtest from CLI.

    Args:
        symbols: List of symbols to trade
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_capital: Initial capital
        output_dir: Directory to save reports (default: reports/backtest)

    Returns:
        BacktestResult
    """
    if output_dir is None:
        output_dir = Path("reports/backtest")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create config
    config = BacktestConfig(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=Decimal(str(initial_capital)),
    )

    # Run backtest
    engine = BacktestEngine(config)
    result = engine.run()

    # Generate reports
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    strategy_name = config.strategy_name

    # Print summary
    BacktestVisualizer.print_summary(result.metrics, strategy_name)

    # Save equity curve plot
    equity_plot_path = output_dir / f"{strategy_name}_{timestamp_str}_equity.png"
    BacktestVisualizer.plot_equity_curve(result.equity_curve, equity_plot_path)
    logger.info(f"Saved equity curve: {equity_plot_path}")

    # Save drawdown plot
    drawdown_plot_path = output_dir / f"{strategy_name}_{timestamp_str}_drawdown.png"
    BacktestVisualizer.plot_drawdown(result.equity_curve, drawdown_plot_path)
    logger.info(f"Saved drawdown plot: {drawdown_plot_path}")

    # Save markdown report
    md_report_path = output_dir / f"{strategy_name}_{timestamp_str}_report.md"
    BacktestVisualizer.generate_markdown_report(
        result.metrics, strategy_name, symbols, md_report_path
    )
    logger.info(f"Saved markdown report: {md_report_path}")

    # Save PDF report
    pdf_report_path = output_dir / f"{strategy_name}_{timestamp_str}_report.pdf"
    BacktestVisualizer.generate_pdf_report(
        result.metrics,
        strategy_name,
        symbols,
        result.equity_curve,
        result.trades,
        pdf_report_path,
    )
    logger.info(f"Saved PDF report: {pdf_report_path}")

    return result
