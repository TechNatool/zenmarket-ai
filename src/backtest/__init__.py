"""Backtesting module for historical strategy simulation.

This module provides comprehensive backtesting capabilities for ZenMarket AI,
including historical data replay, performance metrics, and visualization.

Main Components:
    - BacktestBroker: Historical simulation broker extending BrokerBase
    - BacktestEngine: Historical data replay and strategy testing
    - PerformanceMetrics: Calculate Sharpe, Sortino, Max Drawdown, etc.
    - BacktestVisualizer: Generate equity curves, drawdown plots, and reports
"""

from src.backtest.backtest_broker import BacktestBroker
from src.backtest.backtest_engine import BacktestEngine, BacktestResult
from src.backtest.metrics import PerformanceMetrics
from src.backtest.visualizer import BacktestVisualizer

__all__ = [
    "BacktestBroker",
    "BacktestEngine",
    "BacktestResult",
    "BacktestVisualizer",
    "PerformanceMetrics",
]
