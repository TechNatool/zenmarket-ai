"""Comprehensive tests for MarketDataFetcher module."""

from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from src.core.market_data import MarketAnalysis, MarketDataFetcher, MarketSnapshot


class TestMarketSnapshot:
    """Test MarketSnapshot dataclass."""

    def test_market_snapshot_creation(self):
        """Test creating a MarketSnapshot."""
        snapshot = MarketSnapshot(
            ticker="AAPL",
            name="Apple Inc.",
            last_price=150.0,
            change=2.5,
            change_percent=1.69,
            volume=100000,
            high=152.0,
            low=149.0,
            open_price=150.5,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            volatility=25.5,
            trend="bullish",
        )

        assert snapshot.ticker == "AAPL"
        assert snapshot.name == "Apple Inc."
        assert snapshot.last_price == 150.0
        assert snapshot.change == 2.5
        assert snapshot.change_percent == 1.69

    def test_market_snapshot_to_dict_with_timestamp(self):
        """Test converting MarketSnapshot to dict with timestamp."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        snapshot = MarketSnapshot(
            ticker="AAPL",
            name="Apple Inc.",
            last_price=150.0,
            change=2.5,
            change_percent=1.69,
            timestamp=timestamp,
        )

        data = snapshot.to_dict()
        assert data["ticker"] == "AAPL"
        assert data["timestamp"] == timestamp.isoformat()

    def test_market_snapshot_to_dict_without_timestamp(self):
        """Test converting MarketSnapshot to dict without timestamp."""
        snapshot = MarketSnapshot(
            ticker="AAPL",
            name="Apple Inc.",
            last_price=150.0,
            change=2.5,
            change_percent=1.69,
            timestamp=None,
        )

        data = snapshot.to_dict()
        assert data["ticker"] == "AAPL"
        assert data["timestamp"] is None


class TestMarketAnalysis:
    """Test MarketAnalysis dataclass."""

    def test_market_analysis_creation(self):
        """Test creating a MarketAnalysis."""
        analysis = MarketAnalysis(
            ticker="AAPL",
            trend="bullish",
            volatility="medium",
            support_level=145.0,
            resistance_level=155.0,
            rsi=65.5,
            moving_avg_20=148.5,
            moving_avg_50=147.0,
        )

        assert analysis.ticker == "AAPL"
        assert analysis.trend == "bullish"
        assert analysis.volatility == "medium"

    def test_market_analysis_to_dict(self):
        """Test converting MarketAnalysis to dict."""
        analysis = MarketAnalysis(
            ticker="AAPL",
            trend="bullish",
            volatility="medium",
            support_level=145.0,
            resistance_level=155.0,
        )

        data = analysis.to_dict()
        assert data["ticker"] == "AAPL"
        assert data["trend"] == "bullish"
        assert data["volatility"] == "medium"


class TestMarketDataFetcherInit:
    """Test MarketDataFetcher initialization."""

    @patch("src.core.market_data.get_config")
    def test_initialization(self, mock_get_config):
        """Test MarketDataFetcher initialization."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config

        fetcher = MarketDataFetcher()

        assert fetcher.config == mock_config
        mock_get_config.assert_called_once()


class TestGetTickerName:
    """Test get_ticker_name method."""

    @patch("src.core.market_data.get_config")
    def test_get_ticker_name_known(self, mock_get_config):
        """Test getting friendly name for known ticker."""
        fetcher = MarketDataFetcher()

        assert fetcher.get_ticker_name("^GDAXI") == "DAX"
        assert fetcher.get_ticker_name("^IXIC") == "NASDAQ"
        assert fetcher.get_ticker_name("^GSPC") == "S&P 500"
        assert fetcher.get_ticker_name("BTC-USD") == "Bitcoin"

    @patch("src.core.market_data.get_config")
    def test_get_ticker_name_unknown(self, mock_get_config):
        """Test getting name for unknown ticker returns ticker itself."""
        fetcher = MarketDataFetcher()

        assert fetcher.get_ticker_name("UNKNOWN") == "UNKNOWN"


class TestFetchSnapshot:
    """Test fetch_snapshot method."""

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_snapshot_success(self, mock_ticker_class, mock_get_config):
        """Test successful snapshot fetch."""
        fetcher = MarketDataFetcher()

        # Mock historical data
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        hist = pd.DataFrame(
            {
                "Open": [150.0, 151.0, 152.0, 153.0, 154.0],
                "High": [152.0, 153.0, 154.0, 155.0, 156.0],
                "Low": [149.0, 150.0, 151.0, 152.0, 153.0],
                "Close": [151.0, 152.0, 153.0, 154.0, 155.0],
                "Volume": [100000, 110000, 120000, 130000, 140000],
            },
            index=dates,
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        snapshot = fetcher.fetch_snapshot("AAPL")

        assert snapshot is not None
        assert snapshot.ticker == "AAPL"
        assert snapshot.last_price == 155.0
        assert snapshot.change == 1.0  # 155.0 - 154.0
        assert snapshot.open_price == 154.0
        assert snapshot.high == 156.0
        assert snapshot.low == 153.0
        assert snapshot.volume == 140000

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_snapshot_empty_data(self, mock_ticker_class, mock_get_config):
        """Test snapshot fetch with empty data."""
        fetcher = MarketDataFetcher()

        mock_stock = Mock()
        mock_stock.history.return_value = pd.DataFrame()  # Empty DataFrame
        mock_ticker_class.return_value = mock_stock

        snapshot = fetcher.fetch_snapshot("INVALID")

        assert snapshot is None

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_snapshot_single_row(self, mock_ticker_class, mock_get_config):
        """Test snapshot fetch with single data point."""
        fetcher = MarketDataFetcher()

        # Single row
        hist = pd.DataFrame(
            {
                "Open": [150.0],
                "High": [152.0],
                "Low": [149.0],
                "Close": [151.0],
                "Volume": [100000],
            },
            index=[pd.Timestamp("2024-01-01")],
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        snapshot = fetcher.fetch_snapshot("AAPL")

        assert snapshot is not None
        # With single row, change should be 0
        assert snapshot.change == 0.0
        assert snapshot.change_percent == 0.0

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_snapshot_missing_volume(self, mock_ticker_class, mock_get_config):
        """Test snapshot fetch with missing volume."""
        fetcher = MarketDataFetcher()

        hist = pd.DataFrame(
            {
                "Open": [150.0, 151.0],
                "High": [152.0, 153.0],
                "Low": [149.0, 150.0],
                "Close": [151.0, 152.0],
                "Volume": [100000, pd.NA],  # Missing volume for second row
            },
            index=pd.date_range("2024-01-01", periods=2, freq="D"),
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        snapshot = fetcher.fetch_snapshot("AAPL")

        assert snapshot is not None
        assert snapshot.volume is None  # Should handle missing volume

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_snapshot_exception(self, mock_ticker_class, mock_get_config):
        """Test snapshot fetch handles exceptions."""
        fetcher = MarketDataFetcher()

        mock_ticker_class.side_effect = Exception("Network error")

        snapshot = fetcher.fetch_snapshot("AAPL")

        assert snapshot is None


class TestFetchHistorical:
    """Test fetch_historical method."""

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_historical_success(self, mock_ticker_class, mock_get_config):
        """Test successful historical data fetch."""
        fetcher = MarketDataFetcher()

        hist = pd.DataFrame(
            {
                "Open": [150.0] * 10,
                "High": [152.0] * 10,
                "Low": [149.0] * 10,
                "Close": [151.0] * 10,
                "Volume": [100000] * 10,
            },
            index=pd.date_range("2024-01-01", periods=10, freq="D"),
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        result = fetcher.fetch_historical("AAPL", period="1mo", interval="1d")

        assert result is not None
        assert len(result) == 10
        mock_stock.history.assert_called_once_with(period="1mo", interval="1d")

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_historical_empty(self, mock_ticker_class, mock_get_config):
        """Test historical fetch with empty data."""
        fetcher = MarketDataFetcher()

        mock_stock = Mock()
        mock_stock.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_stock

        result = fetcher.fetch_historical("INVALID")

        assert result is None

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_historical_exception(self, mock_ticker_class, mock_get_config):
        """Test historical fetch handles exceptions."""
        fetcher = MarketDataFetcher()

        mock_ticker_class.side_effect = Exception("API error")

        result = fetcher.fetch_historical("AAPL")

        assert result is None


class TestAnalyzeMarket:
    """Test analyze_market method."""

    @patch("src.core.market_data.get_config")
    def test_analyze_market_with_provided_hist(self, mock_get_config):
        """Test market analysis with provided historical data."""
        fetcher = MarketDataFetcher()

        # Create historical data with sufficient length
        hist = pd.DataFrame(
            {
                "Open": [150.0] * 60,
                "High": [155.0] * 60,
                "Low": [145.0] * 60,
                "Close": [150.0 + i * 0.5 for i in range(60)],  # Upward trend
                "Volume": [100000] * 60,
            },
            index=pd.date_range("2024-01-01", periods=60, freq="D"),
        )

        analysis = fetcher.analyze_market("AAPL", hist=hist)

        assert analysis is not None
        assert analysis.ticker == "AAPL"
        assert analysis.trend in ["bullish", "bearish", "neutral"]
        assert analysis.volatility in ["low", "medium", "high"]
        assert analysis.support_level is not None
        assert analysis.resistance_level is not None
        assert analysis.moving_avg_20 is not None
        assert analysis.moving_avg_50 is not None
        assert analysis.rsi is not None

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_analyze_market_without_hist(self, mock_ticker_class, mock_get_config):
        """Test market analysis fetches hist if not provided."""
        fetcher = MarketDataFetcher()

        # Mock fetch_historical
        hist = pd.DataFrame(
            {
                "Open": [150.0] * 60,
                "High": [155.0] * 60,
                "Low": [145.0] * 60,
                "Close": [150.0] * 60,
                "Volume": [100000] * 60,
            },
            index=pd.date_range("2024-01-01", periods=60, freq="D"),
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        analysis = fetcher.analyze_market("AAPL")

        assert analysis is not None
        assert analysis.ticker == "AAPL"

    @patch("src.core.market_data.get_config")
    def test_analyze_market_empty_hist(self, mock_get_config):
        """Test market analysis with empty historical data."""
        fetcher = MarketDataFetcher()

        analysis = fetcher.analyze_market("AAPL", hist=pd.DataFrame())

        assert analysis is None

    @patch("src.core.market_data.get_config")
    def test_analyze_market_short_hist_no_ma50(self, mock_get_config):
        """Test market analysis with insufficient data for MA50."""
        fetcher = MarketDataFetcher()

        # Only 30 days - enough for MA20 but not MA50
        hist = pd.DataFrame(
            {
                "Open": [150.0] * 30,
                "High": [155.0] * 30,
                "Low": [145.0] * 30,
                "Close": [150.0] * 30,
                "Volume": [100000] * 30,
            },
            index=pd.date_range("2024-01-01", periods=30, freq="D"),
        )

        analysis = fetcher.analyze_market("AAPL", hist=hist)

        assert analysis is not None
        assert analysis.moving_avg_20 is not None  # Should have MA20
        assert analysis.moving_avg_50 is None  # Should not have MA50

    @patch("src.core.market_data.get_config")
    def test_analyze_market_low_volatility(self, mock_get_config):
        """Test market analysis classifies low volatility."""
        fetcher = MarketDataFetcher()

        # Very stable prices
        hist = pd.DataFrame(
            {
                "Open": [150.0] * 60,
                "High": [150.1] * 60,
                "Low": [149.9] * 60,
                "Close": [150.0 + np.random.uniform(-0.1, 0.1) for _ in range(60)],
                "Volume": [100000] * 60,
            },
            index=pd.date_range("2024-01-01", periods=60, freq="D"),
        )

        analysis = fetcher.analyze_market("AAPL", hist=hist)

        assert analysis is not None
        assert analysis.volatility == "low"

    @patch("src.core.market_data.get_config")
    def test_analyze_market_high_volatility(self, mock_get_config):
        """Test market analysis classifies high volatility."""
        fetcher = MarketDataFetcher()

        # Very volatile prices
        hist = pd.DataFrame(
            {
                "Open": [150.0] * 60,
                "High": [160.0] * 60,
                "Low": [140.0] * 60,
                "Close": [150.0 + np.random.uniform(-20, 20) for _ in range(60)],
                "Volume": [100000] * 60,
            },
            index=pd.date_range("2024-01-01", periods=60, freq="D"),
        )

        analysis = fetcher.analyze_market("AAPL", hist=hist)

        assert analysis is not None
        assert analysis.volatility == "high"

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_analyze_market_exception(self, mock_ticker_class, mock_get_config):
        """Test market analysis handles exceptions."""
        fetcher = MarketDataFetcher()

        # Mock fetch_historical to raise exception
        mock_ticker_class.side_effect = Exception("Network error")

        analysis = fetcher.analyze_market("AAPL")

        assert analysis is None


class TestFetchAllMarkets:
    """Test fetch_all_markets method."""

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_all_markets_success(self, mock_ticker_class, mock_get_config):
        """Test fetching all market snapshots."""
        # Mock config
        mock_config = Mock()
        mock_config.market_indices = ["^GDAXI", "^IXIC", "BTC-USD"]
        mock_get_config.return_value = mock_config

        fetcher = MarketDataFetcher()

        # Mock historical data
        hist = pd.DataFrame(
            {
                "Open": [150.0, 151.0],
                "High": [152.0, 153.0],
                "Low": [149.0, 150.0],
                "Close": [151.0, 152.0],
                "Volume": [100000, 110000],
            },
            index=pd.date_range("2024-01-01", periods=2, freq="D"),
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        snapshots = fetcher.fetch_all_markets()

        assert len(snapshots) == 3
        assert "^GDAXI" in snapshots
        assert "^IXIC" in snapshots
        assert "BTC-USD" in snapshots

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_fetch_all_markets_partial_failure(self, mock_ticker_class, mock_get_config):
        """Test fetching all markets with some failures."""
        # Mock config
        mock_config = Mock()
        mock_config.market_indices = ["^GDAXI", "INVALID"]
        mock_get_config.return_value = mock_config

        fetcher = MarketDataFetcher()

        # Mock responses: success for first, empty for second
        def history_side_effect(period):
            if not hasattr(history_side_effect, "call_count"):
                history_side_effect.call_count = 0
            history_side_effect.call_count += 1

            if history_side_effect.call_count == 1:
                # First call succeeds
                return pd.DataFrame(
                    {
                        "Open": [150.0, 151.0],
                        "High": [152.0, 153.0],
                        "Low": [149.0, 150.0],
                        "Close": [151.0, 152.0],
                        "Volume": [100000, 110000],
                    },
                    index=pd.date_range("2024-01-01", periods=2, freq="D"),
                )
            else:
                # Second call returns empty
                return pd.DataFrame()

        mock_stock = Mock()
        mock_stock.history.side_effect = history_side_effect
        mock_ticker_class.return_value = mock_stock

        snapshots = fetcher.fetch_all_markets()

        # Should only have one successful snapshot
        assert len(snapshots) == 1
        assert "^GDAXI" in snapshots


class TestDetermineTrend:
    """Test _determine_trend private method."""

    @patch("src.core.market_data.get_config")
    def test_determine_trend_bullish(self, mock_get_config):
        """Test trend determination for bullish market."""
        fetcher = MarketDataFetcher()

        # Upward trend
        hist = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0, 103.0, 105.0]},
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )

        trend = fetcher._determine_trend(hist)

        assert trend == "bullish"

    @patch("src.core.market_data.get_config")
    def test_determine_trend_bearish(self, mock_get_config):
        """Test trend determination for bearish market."""
        fetcher = MarketDataFetcher()

        # Downward trend
        hist = pd.DataFrame(
            {"Close": [105.0, 103.0, 102.0, 101.0, 100.0]},
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )

        trend = fetcher._determine_trend(hist)

        assert trend == "bearish"

    @patch("src.core.market_data.get_config")
    def test_determine_trend_neutral(self, mock_get_config):
        """Test trend determination for neutral market."""
        fetcher = MarketDataFetcher()

        # Stable prices (less than 1% change)
        hist = pd.DataFrame(
            {"Close": [100.0, 100.2, 100.5, 100.3, 100.4]},
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )

        trend = fetcher._determine_trend(hist)

        assert trend == "neutral"

    @patch("src.core.market_data.get_config")
    def test_determine_trend_insufficient_data(self, mock_get_config):
        """Test trend determination with insufficient data."""
        fetcher = MarketDataFetcher()

        # Less than 5 data points
        hist = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0]}, index=pd.date_range("2024-01-01", periods=3, freq="D")
        )

        trend = fetcher._determine_trend(hist)

        assert trend == "neutral"


class TestCalculateRSI:
    """Test _calculate_rsi private method."""

    @patch("src.core.market_data.get_config")
    def test_calculate_rsi_success(self, mock_get_config):
        """Test RSI calculation with sufficient data."""
        fetcher = MarketDataFetcher()

        # Create price series with upward trend
        prices = pd.Series([100 + i for i in range(20)])

        rsi = fetcher._calculate_rsi(prices, period=14)

        assert rsi is not None
        assert 0 <= rsi <= 100

    @patch("src.core.market_data.get_config")
    def test_calculate_rsi_insufficient_data(self, mock_get_config):
        """Test RSI calculation with insufficient data."""
        fetcher = MarketDataFetcher()

        # Only 10 data points, need 15 for period=14
        prices = pd.Series([100 + i for i in range(10)])

        rsi = fetcher._calculate_rsi(prices, period=14)

        assert rsi is None

    @patch("src.core.market_data.get_config")
    def test_calculate_rsi_overbought(self, mock_get_config):
        """Test RSI calculation with overbought conditions."""
        fetcher = MarketDataFetcher()

        # Strong upward trend
        prices = pd.Series([100 + i * 2 for i in range(20)])

        rsi = fetcher._calculate_rsi(prices, period=14)

        assert rsi is not None
        assert rsi > 50  # Should be in overbought territory

    @patch("src.core.market_data.get_config")
    def test_calculate_rsi_oversold(self, mock_get_config):
        """Test RSI calculation with oversold conditions."""
        fetcher = MarketDataFetcher()

        # Strong downward trend
        prices = pd.Series([100 - i * 2 for i in range(20)])

        rsi = fetcher._calculate_rsi(prices, period=14)

        assert rsi is not None
        assert rsi < 50  # Should be in oversold territory


class TestGetMarketSummary:
    """Test get_market_summary method."""

    @patch("src.core.market_data.get_config")
    @patch("src.core.market_data.yf.Ticker")
    def test_get_market_summary_success(self, mock_ticker_class, mock_get_config):
        """Test getting market summary."""
        # Mock config
        mock_config = Mock()
        mock_config.market_indices = ["^GDAXI"]
        mock_get_config.return_value = mock_config

        fetcher = MarketDataFetcher()

        # Mock historical data
        hist = pd.DataFrame(
            {
                "Open": [150.0, 151.0],
                "High": [152.0, 153.0],
                "Low": [149.0, 150.0],
                "Close": [151.0, 152.0],
                "Volume": [100000, 110000],
            },
            index=pd.date_range("2024-01-01", periods=2, freq="D"),
        )

        mock_stock = Mock()
        mock_stock.history.return_value = hist
        mock_ticker_class.return_value = mock_stock

        summary = fetcher.get_market_summary()

        assert "Market Overview:" in summary
        assert "DAX" in summary  # Ticker name mapping

    @patch("src.core.market_data.get_config")
    def test_get_market_summary_no_data(self, mock_get_config):
        """Test market summary with no data."""
        # Mock config with no indices
        mock_config = Mock()
        mock_config.market_indices = []
        mock_get_config.return_value = mock_config

        fetcher = MarketDataFetcher()

        summary = fetcher.get_market_summary()

        assert summary == "No market data available."
