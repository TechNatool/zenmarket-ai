"""
Technical indicators calculator for AI Trading Advisor.
Computes moving averages, RSI, Bollinger Bands, and volume indicators.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TechnicalIndicators:
    """Container for technical indicators."""

    ticker: str
    current_price: float
    ma_20: float
    ma_50: float
    rsi: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    volume_avg: float
    current_volume: float | None = None
    atr: float | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "current_price": self.current_price,
            "ma_20": self.ma_20,
            "ma_50": self.ma_50,
            "rsi": self.rsi,
            "bb_upper": self.bb_upper,
            "bb_middle": self.bb_middle,
            "bb_lower": self.bb_lower,
            "volume_avg": self.volume_avg,
            "current_volume": self.current_volume,
            "atr": self.atr,
        }


class IndicatorCalculator:
    """Calculates technical indicators from price data."""

    def __init__(self) -> None:
        """Initialize indicator calculator."""

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            prices: Series of prices
            period: RSI period (default: 14)

        Returns:
            Series of RSI values
        """
        try:
            delta = prices.diff()

            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            return 100 - (100 / (1 + rs))

        except Exception as e:
            logger.exception(f"Error calculating RSI: {e}")
            return pd.Series([50] * len(prices), index=prices.index)

    def calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            prices: Series of prices
            period: Moving average period (default: 20)
            std_dev: Number of standard deviations (default: 2.0)

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        try:
            middle_band = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()

            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)

            return upper_band, middle_band, lower_band

        except Exception as e:
            logger.exception(f"Error calculating Bollinger Bands: {e}")
            middle = pd.Series([prices.mean()] * len(prices), index=prices.index)
            return middle, middle, middle

    def calculate_atr(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (ATR).

        Args:
            high: Series of high prices
            low: Series of low prices
            close: Series of close prices
            period: ATR period (default: 14)

        Returns:
            Series of ATR values
        """
        try:
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())

            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            return true_range.rolling(window=period).mean()

        except Exception as e:
            logger.exception(f"Error calculating ATR: {e}")
            return pd.Series([0] * len(high), index=high.index)

    def calculate_all_indicators(
        self,
        ticker: str,
        df: pd.DataFrame,
        ma_short: int = 20,
        ma_long: int = 50,
        rsi_period: int = 14,
        bb_period: int = 20,
        volume_period: int = 10,
    ) -> TechnicalIndicators | None:
        """
        Calculate all technical indicators for a given dataframe.

        Args:
            ticker: Ticker symbol
            df: DataFrame with OHLCV data
            ma_short: Short moving average period (default: 20)
            ma_long: Long moving average period (default: 50)
            rsi_period: RSI period (default: 14)
            bb_period: Bollinger Bands period (default: 20)
            volume_period: Volume average period (default: 10)

        Returns:
            TechnicalIndicators object or None
        """
        try:
            if df is None or df.empty:
                logger.error(f"Empty dataframe for {ticker}")
                return None

            if len(df) < ma_long:
                logger.warning(f"Insufficient data for {ticker}: {len(df)} rows (need {ma_long})")
                return None

            # Get close prices
            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            volume = df.get("Volume", pd.Series([0] * len(df)))

            # Current values
            current_price = float(close.iloc[-1])
            current_volume = float(volume.iloc[-1]) if not pd.isna(volume.iloc[-1]) else None

            # Moving averages
            ma_20 = close.rolling(window=ma_short).mean()
            ma_50 = close.rolling(window=ma_long).mean()

            # RSI
            rsi_series = self.calculate_rsi(close, rsi_period)

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close, bb_period)

            # Volume average
            volume_avg_series = volume.rolling(window=volume_period).mean()

            # ATR
            atr_series = self.calculate_atr(high, low, close)

            # Get latest values
            indicators = TechnicalIndicators(
                ticker=ticker,
                current_price=current_price,
                ma_20=float(ma_20.iloc[-1]) if not pd.isna(ma_20.iloc[-1]) else current_price,
                ma_50=float(ma_50.iloc[-1]) if not pd.isna(ma_50.iloc[-1]) else current_price,
                rsi=float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0,
                bb_upper=(
                    float(bb_upper.iloc[-1])
                    if not pd.isna(bb_upper.iloc[-1])
                    else current_price * 1.02
                ),
                bb_middle=(
                    float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else current_price
                ),
                bb_lower=(
                    float(bb_lower.iloc[-1])
                    if not pd.isna(bb_lower.iloc[-1])
                    else current_price * 0.98
                ),
                volume_avg=(
                    float(volume_avg_series.iloc[-1])
                    if not pd.isna(volume_avg_series.iloc[-1])
                    else 0
                ),
                current_volume=current_volume,
                atr=float(atr_series.iloc[-1]) if not pd.isna(atr_series.iloc[-1]) else None,
            )

            logger.info(
                f"Calculated indicators for {ticker}: "
                f"Price={current_price:.2f}, MA20={indicators.ma_20:.2f}, "
                f"MA50={indicators.ma_50:.2f}, RSI={indicators.rsi:.1f}"
            )

            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators for {ticker}: {e}", exc_info=True)
            return None

    def get_indicator_summary(self, indicators: TechnicalIndicators) -> str:
        """
        Get a human-readable summary of indicators.

        Args:
            indicators: TechnicalIndicators object

        Returns:
            Summary string
        """
        ma_trend = "bullish" if indicators.ma_20 > indicators.ma_50 else "bearish"
        rsi_level = (
            "overbought"
            if indicators.rsi > 70
            else "oversold" if indicators.rsi < 30 else "neutral"
        )

        # Position relative to Bollinger Bands
        bb_position = (
            "above upper"
            if indicators.current_price > indicators.bb_upper
            else "below lower" if indicators.current_price < indicators.bb_lower else "within bands"
        )

        return (
            f"{indicators.ticker}: Price {indicators.current_price:.2f} | "
            f"MA trend: {ma_trend} | RSI: {indicators.rsi:.1f} ({rsi_level}) | "
            f"BB: {bb_position}"
        )
