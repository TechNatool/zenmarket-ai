"""
Market data fetcher for ZenMarket AI.
Retrieves stock, index, forex, and crypto data from various sources.
"""

from dataclasses import asdict, dataclass
from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

from src.utils.config_loader import get_config
from src.utils.date_utils import now
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MarketSnapshot:
    """Data class for market snapshot."""

    ticker: str
    name: str
    last_price: float
    change: float
    change_percent: float
    volume: int | None = None
    high: float | None = None
    low: float | None = None
    open_price: float | None = None
    timestamp: datetime | None = None
    volatility: float | None = None
    trend: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class MarketAnalysis:
    """Market analysis data."""

    ticker: str
    trend: str  # "bullish", "bearish", "neutral"
    volatility: str  # "low", "medium", "high"
    support_level: float | None = None
    resistance_level: float | None = None
    rsi: float | None = None
    moving_avg_20: float | None = None
    moving_avg_50: float | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class MarketDataFetcher:
    """Fetches and analyzes market data."""

    # Ticker name mappings
    TICKER_NAMES = {
        "^GDAXI": "DAX",
        "^IXIC": "NASDAQ",
        "^GSPC": "S&P 500",
        "EURUSD=X": "EUR/USD",
        "BTC-USD": "Bitcoin",
        "^DJI": "Dow Jones",
        "^FTSE": "FTSE 100",
        "GC=F": "Gold",
        "CL=F": "Crude Oil",
    }

    def __init__(self) -> None:
        """Initialize market data fetcher."""
        self.config = get_config()

    def get_ticker_name(self, ticker: str) -> str:
        """
        Get friendly name for ticker.

        Args:
            ticker: Ticker symbol

        Returns:
            Friendly name
        """
        return self.TICKER_NAMES.get(ticker, ticker)

    def fetch_snapshot(self, ticker: str) -> MarketSnapshot | None:
        """
        Fetch current market snapshot for a ticker.

        Args:
            ticker: Ticker symbol (e.g., '^GDAXI', 'BTC-USD')

        Returns:
            MarketSnapshot object or None if error
        """
        try:
            logger.info(f"Fetching snapshot for {ticker}")

            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")

            if hist.empty:
                logger.warning(f"No data available for {ticker}")
                return None

            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest

            last_price = float(latest["Close"])
            prev_close = float(previous["Close"])
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

            # Calculate volatility (standard deviation of returns)
            returns = hist["Close"].pct_change().dropna()
            volatility = float(returns.std() * np.sqrt(252) * 100) if len(returns) > 0 else None

            # Determine trend
            trend = self._determine_trend(hist)

            snapshot = MarketSnapshot(
                ticker=ticker,
                name=self.get_ticker_name(ticker),
                last_price=last_price,
                change=change,
                change_percent=change_percent,
                volume=(
                    int(latest["Volume"])
                    if "Volume" in latest and not pd.isna(latest["Volume"])
                    else None
                ),
                high=float(latest["High"]),
                low=float(latest["Low"]),
                open_price=float(latest["Open"]),
                timestamp=(
                    latest.name.to_pydatetime() if hasattr(latest.name, "to_pydatetime") else now()
                ),
                volatility=volatility,
                trend=trend,
            )

            logger.info(
                f"Successfully fetched snapshot for {ticker}: {last_price:.2f} ({change_percent:+.2f}%)"
            )
            return snapshot

        except Exception as e:
            logger.exception(f"Error fetching snapshot for {ticker}: {e}")
            return None

    def fetch_historical(
        self, ticker: str, period: str = "1mo", interval: str = "1d"
    ) -> pd.DataFrame | None:
        """
        Fetch historical data for a ticker.

        Args:
            ticker: Ticker symbol
            period: Data period ('1d', '5d', '1mo', '3mo', '1y', etc.)
            interval: Data interval ('1m', '5m', '1h', '1d', etc.)

        Returns:
            DataFrame with historical data or None
        """
        try:
            logger.info(
                f"Fetching historical data for {ticker} (period={period}, interval={interval})"
            )

            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return None

            logger.info(f"Fetched {len(hist)} data points for {ticker}")
            return hist

        except Exception as e:
            logger.exception(f"Error fetching historical data for {ticker}: {e}")
            return None

    def analyze_market(
        self, ticker: str, hist: pd.DataFrame | None = None
    ) -> MarketAnalysis | None:
        """
        Perform technical analysis on market data.

        Args:
            ticker: Ticker symbol
            hist: Historical data. If None, fetches it.

        Returns:
            MarketAnalysis object
        """
        try:
            if hist is None:
                hist = self.fetch_historical(ticker, period="3mo", interval="1d")

            if hist is None or hist.empty:
                return None

            # Calculate technical indicators
            close = hist["Close"]

            # Moving averages
            ma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
            ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None

            # RSI (Relative Strength Index)
            rsi = self._calculate_rsi(close)

            # Support and resistance (simple approximation)
            support = float(hist["Low"].tail(20).min())
            resistance = float(hist["High"].tail(20).max())

            # Trend determination
            trend = self._determine_trend(hist)

            # Volatility classification
            returns = close.pct_change().dropna()
            volatility_value = returns.std() * np.sqrt(252) * 100

            if volatility_value < 15:
                volatility = "low"
            elif volatility_value < 30:
                volatility = "medium"
            else:
                volatility = "high"

            analysis = MarketAnalysis(
                ticker=ticker,
                trend=trend,
                volatility=volatility,
                support_level=support,
                resistance_level=resistance,
                rsi=rsi,
                moving_avg_20=float(ma_20) if ma_20 and not pd.isna(ma_20) else None,
                moving_avg_50=float(ma_50) if ma_50 and not pd.isna(ma_50) else None,
            )

            logger.info(f"Analysis for {ticker}: {trend} trend, {volatility} volatility")
            return analysis

        except Exception as e:
            logger.exception(f"Error analyzing market for {ticker}: {e}")
            return None

    def fetch_all_markets(self) -> dict[str, MarketSnapshot]:
        """
        Fetch snapshots for all configured markets.

        Returns:
            Dictionary of ticker: MarketSnapshot
        """
        logger.info("Fetching snapshots for all markets")

        snapshots = {}

        for ticker in self.config.market_indices:
            snapshot = self.fetch_snapshot(ticker)
            if snapshot:
                snapshots[ticker] = snapshot

        logger.info(
            f"Successfully fetched {len(snapshots)}/{len(self.config.market_indices)} market snapshots"
        )
        return snapshots

    def _determine_trend(self, hist: pd.DataFrame) -> str:
        """
        Determine trend from historical data.

        Args:
            hist: Historical DataFrame

        Returns:
            Trend string: "bullish", "bearish", or "neutral"
        """
        if len(hist) < 5:
            return "neutral"

        close = hist["Close"]
        recent = close.tail(5)

        # Simple trend: compare first and last of recent period
        first_price = recent.iloc[0]
        last_price = recent.iloc[-1]

        change_pct = ((last_price - first_price) / first_price) * 100

        if change_pct > 1.0:
            return "bullish"
        if change_pct < -1.0:
            return "bearish"
        return "neutral"

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float | None:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            prices: Price series
            period: RSI period

        Returns:
            RSI value (0-100) or None
        """
        if len(prices) < period + 1:
            return None

        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

    def get_market_summary(self) -> str:
        """
        Get a text summary of current market conditions.

        Returns:
            Summary string
        """
        snapshots = self.fetch_all_markets()

        if not snapshots:
            return "No market data available."

        summary_lines = ["Market Overview:"]

        for _ticker, snapshot in snapshots.items():
            emoji = (
                "📈"
                if snapshot.change_percent > 0
                else "📉" if snapshot.change_percent < 0 else "➖"
            )
            trend_emoji = {"bullish": "🔼", "bearish": "🔽", "neutral": "➡️"}.get(snapshot.trend, "")

            line = (
                f"{emoji} {snapshot.name}: {snapshot.last_price:.2f} "
                f"({snapshot.change_percent:+.2f}%) {trend_emoji}"
            )

            summary_lines.append(line)

        return "\n".join(summary_lines)
