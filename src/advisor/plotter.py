"""
Chart plotter for AI Trading Advisor.
Creates technical analysis charts with matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
from datetime import datetime

from .indicators import IndicatorCalculator
from .signal_generator import TradingSignal, SignalType
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')


class TechnicalChartPlotter:
    """Creates technical analysis charts."""

    def __init__(self, output_dir: Path = None):
        """
        Initialize chart plotter.

        Args:
            output_dir: Directory to save charts (default: reports/charts)
        """
        if output_dir is None:
            output_dir = Path("reports/charts")

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_full_technical_chart(
        self,
        ticker: str,
        df: pd.DataFrame,
        signal: Optional[TradingSignal] = None,
        period_days: int = 90
    ) -> Optional[Path]:
        """
        Create comprehensive technical analysis chart.

        Args:
            ticker: Ticker symbol
            df: DataFrame with OHLCV data
            signal: TradingSignal object (optional)
            period_days: Number of days to display

        Returns:
            Path to saved chart or None
        """
        try:
            if df is None or df.empty:
                logger.error(f"Empty dataframe for {ticker}")
                return None

            # Limit to recent data
            df = df.tail(period_days)

            # Calculate indicators
            calc = IndicatorCalculator()

            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df.get('Volume', pd.Series([0] * len(df)))

            ma_20 = close.rolling(window=20).mean()
            ma_50 = close.rolling(window=50).mean()
            rsi = calc.calculate_rsi(close)
            bb_upper, bb_middle, bb_lower = calc.calculate_bollinger_bands(close)

            # Create figure with 3 subplots
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)

            # === Subplot 1: Price + MAs + Bollinger Bands ===
            ax1 = fig.add_subplot(gs[0])

            # Plot price
            ax1.plot(df.index, close, label='Price', color='#2E86C1', linewidth=2, zorder=3)

            # Plot moving averages
            ax1.plot(df.index, ma_20, label='MA20', color='#E74C3C', linewidth=1.5, linestyle='--', alpha=0.8)
            ax1.plot(df.index, ma_50, label='MA50', color='#27AE60', linewidth=1.5, linestyle='--', alpha=0.8)

            # Plot Bollinger Bands
            ax1.plot(df.index, bb_upper, label='BB Upper', color='gray', linewidth=1, linestyle=':', alpha=0.5)
            ax1.plot(df.index, bb_middle, label='BB Middle', color='gray', linewidth=1, linestyle=':', alpha=0.5)
            ax1.plot(df.index, bb_lower, label='BB Lower', color='gray', linewidth=1, linestyle=':', alpha=0.5)
            ax1.fill_between(df.index, bb_upper, bb_lower, alpha=0.1, color='gray')

            # Add signal marker if provided
            if signal:
                signal_color = '#27AE60' if signal.signal == SignalType.BUY else \
                              '#E74C3C' if signal.signal == SignalType.SELL else '#F39C12'
                signal_marker = '^' if signal.signal == SignalType.BUY else \
                               'v' if signal.signal == SignalType.SELL else 'o'

                ax1.scatter(
                    df.index[-1],
                    close.iloc[-1],
                    color=signal_color,
                    s=200,
                    marker=signal_marker,
                    zorder=5,
                    edgecolors='black',
                    linewidths=2,
                    label=f'Signal: {signal.signal.value}'
                )

            ax1.set_title(f'{ticker} - Technical Analysis', fontsize=16, fontweight='bold', pad=20)
            ax1.set_ylabel('Price', fontsize=12)
            ax1.legend(loc='upper left', framealpha=0.9)
            ax1.grid(True, alpha=0.3)

            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.tick_params(axis='x', rotation=45)

            # === Subplot 2: RSI ===
            ax2 = fig.add_subplot(gs[1], sharex=ax1)

            ax2.plot(df.index, rsi, label='RSI(14)', color='#9B59B6', linewidth=2)
            ax2.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Overbought (70)')
            ax2.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.7, label='Oversold (30)')
            ax2.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)
            ax2.fill_between(df.index, 30, 70, alpha=0.1, color='gray')

            ax2.set_ylabel('RSI', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left', framealpha=0.9)
            ax2.grid(True, alpha=0.3)

            # === Subplot 3: Volume ===
            ax3 = fig.add_subplot(gs[2], sharex=ax1)

            # Color bars based on price change
            colors = ['#27AE60' if close.iloc[i] >= close.iloc[i-1] else '#E74C3C'
                     for i in range(1, len(close))]
            colors.insert(0, '#3498DB')  # First bar neutral

            ax3.bar(df.index, volume, color=colors, alpha=0.7, width=0.8)
            ax3.set_ylabel('Volume', fontsize=12)
            ax3.set_xlabel('Date', fontsize=12)
            ax3.grid(True, alpha=0.3, axis='y')

            # Format numbers
            ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))

            # Final formatting
            plt.tight_layout()

            # Save chart
            filename = f"{ticker.replace('^', '').replace('=X', '').replace('-', '')}_technical_chart.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            logger.info(f"Technical chart saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating chart for {ticker}: {e}", exc_info=True)
            plt.close()
            return None

    def plot_signals_overview(
        self,
        signals: list,
        title: str = "Trading Signals Overview"
    ) -> Optional[Path]:
        """
        Create overview chart of all signals.

        Args:
            signals: List of TradingSignal objects
            title: Chart title

        Returns:
            Path to saved chart or None
        """
        try:
            if not signals:
                logger.warning("No signals to plot")
                return None

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # === Subplot 1: Signal Distribution ===
            signal_counts = {
                'BUY': sum(1 for s in signals if s.signal == SignalType.BUY),
                'SELL': sum(1 for s in signals if s.signal == SignalType.SELL),
                'HOLD': sum(1 for s in signals if s.signal == SignalType.HOLD)
            }

            colors_dist = ['#27AE60', '#E74C3C', '#F39C12']
            ax1.pie(
                signal_counts.values(),
                labels=[f'{k}\n({v})' for k, v in signal_counts.items()],
                autopct='%1.1f%%',
                colors=colors_dist,
                startangle=90,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            ax1.set_title('Signal Distribution', fontsize=14, fontweight='bold', pad=20)

            # === Subplot 2: Confidence by Ticker ===
            tickers = [s.ticker for s in signals]
            confidences = [s.confidence for s in signals]
            signal_colors = [
                '#27AE60' if s.signal == SignalType.BUY else
                '#E74C3C' if s.signal == SignalType.SELL else
                '#F39C12'
                for s in signals
            ]

            bars = ax2.barh(tickers, confidences, color=signal_colors, alpha=0.8)
            ax2.set_xlabel('Confidence', fontsize=12)
            ax2.set_title('Signal Confidence by Ticker', fontsize=14, fontweight='bold', pad=20)
            ax2.set_xlim(0, 1)
            ax2.grid(True, alpha=0.3, axis='x')

            # Add value labels
            for i, (bar, conf) in enumerate(zip(bars, confidences)):
                ax2.text(
                    conf + 0.02,
                    i,
                    f'{conf:.2f}',
                    va='center',
                    fontsize=9,
                    weight='bold'
                )

            plt.tight_layout()

            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"signals_overview_{timestamp}.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            logger.info(f"Signals overview chart saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating signals overview chart: {e}", exc_info=True)
            plt.close()
            return None

    def plot_rsi_heatmap(
        self,
        signals: list
    ) -> Optional[Path]:
        """
        Create RSI heatmap for all tickers.

        Args:
            signals: List of TradingSignal objects

        Returns:
            Path to saved chart or None
        """
        try:
            if not signals:
                return None

            fig, ax = plt.subplots(figsize=(10, 6))

            tickers = [s.ticker for s in signals]
            rsi_values = [s.indicators.rsi for s in signals]

            # Create color map based on RSI
            colors = []
            for rsi in rsi_values:
                if rsi > 70:
                    colors.append('#E74C3C')  # Red - Overbought
                elif rsi < 30:
                    colors.append('#27AE60')  # Green - Oversold
                else:
                    colors.append('#3498DB')  # Blue - Neutral

            bars = ax.barh(tickers, rsi_values, color=colors, alpha=0.8)

            # Add reference lines
            ax.axvline(x=70, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Overbought')
            ax.axvline(x=30, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Oversold')
            ax.axvline(x=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)

            ax.set_xlabel('RSI Value', fontsize=12)
            ax.set_title('RSI Heatmap', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlim(0, 100)
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3, axis='x')

            # Add value labels
            for i, (bar, rsi) in enumerate(zip(bars, rsi_values)):
                ax.text(
                    rsi + 2,
                    i,
                    f'{rsi:.1f}',
                    va='center',
                    fontsize=10,
                    weight='bold'
                )

            plt.tight_layout()

            # Save
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"rsi_heatmap_{timestamp}.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            logger.info(f"RSI heatmap saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating RSI heatmap: {e}", exc_info=True)
            plt.close()
            return None
