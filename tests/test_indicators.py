"""
Tests for technical indicators calculator.
"""

import numpy as np
import pandas as pd
import pytest

from src.advisor.indicators import IndicatorCalculator, TechnicalIndicators


@pytest.fixture
def calculator():
    """Create an indicator calculator instance."""
    return IndicatorCalculator()


@pytest.fixture
def sample_data():
    """Create sample OHLCV data."""
    dates = pd.date_range(start="2025-01-01", periods=100, freq="D")

    # Create synthetic price data
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 0.5)
    high = close + np.random.rand(100) * 2
    low = close - np.random.rand(100) * 2
    open_price = close + (np.random.rand(100) - 0.5)
    volume = np.random.randint(1000000, 10000000, 100)

    return pd.DataFrame(
        {"Open": open_price, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


def test_calculator_initialization(calculator):
    """Test calculator can be initialized."""
    assert calculator is not None


def test_calculate_rsi(calculator, sample_data):
    """Test RSI calculation."""
    rsi = calculator.calculate_rsi(sample_data["Close"])

    assert isinstance(rsi, pd.Series)
    assert len(rsi) == len(sample_data)
    # RSI should be between 0 and 100 (after initial period)
    assert rsi.dropna().min() >= 0
    assert rsi.dropna().max() <= 100


def test_calculate_bollinger_bands(calculator, sample_data):
    """Test Bollinger Bands calculation."""
    upper, middle, lower = calculator.calculate_bollinger_bands(sample_data["Close"])

    assert isinstance(upper, pd.Series)
    assert isinstance(middle, pd.Series)
    assert isinstance(lower, pd.Series)

    # All series should have same length
    assert len(upper) == len(middle) == len(lower) == len(sample_data)

    # Upper should be >= middle >= lower (after initial period)
    valid_data = ~middle.isna()
    assert (upper[valid_data] >= middle[valid_data]).all()
    assert (middle[valid_data] >= lower[valid_data]).all()


def test_calculate_atr(calculator, sample_data):
    """Test ATR calculation."""
    atr = calculator.calculate_atr(sample_data["High"], sample_data["Low"], sample_data["Close"])

    assert isinstance(atr, pd.Series)
    assert len(atr) == len(sample_data)
    # ATR should be positive
    assert (atr.dropna() >= 0).all()


def test_calculate_all_indicators(calculator, sample_data):
    """Test calculating all indicators together."""
    indicators = calculator.calculate_all_indicators(ticker="TEST", df=sample_data)

    assert isinstance(indicators, TechnicalIndicators)
    assert indicators.ticker == "TEST"
    assert indicators.current_price > 0
    assert indicators.ma_20 > 0
    assert indicators.ma_50 > 0
    assert 0 <= indicators.rsi <= 100
    assert indicators.bb_upper > indicators.bb_middle > indicators.bb_lower


def test_calculate_all_indicators_insufficient_data(calculator):
    """Test handling of insufficient data."""
    # Create dataframe with only 10 rows (need 50 for MA50)
    dates = pd.date_range(start="2025-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "Open": range(100, 110),
            "High": range(102, 112),
            "Low": range(98, 108),
            "Close": range(100, 110),
            "Volume": [1000000] * 10,
        },
        index=dates,
    )

    indicators = calculator.calculate_all_indicators(ticker="TEST", df=df)

    # Should return None for insufficient data
    assert indicators is None


def test_calculate_all_indicators_empty_df(calculator):
    """Test handling of empty dataframe."""
    df = pd.DataFrame()

    indicators = calculator.calculate_all_indicators(ticker="TEST", df=df)

    assert indicators is None


def test_get_indicator_summary(calculator, sample_data):
    """Test indicator summary generation."""
    indicators = calculator.calculate_all_indicators(ticker="TEST", df=sample_data)

    summary = calculator.get_indicator_summary(indicators)

    assert isinstance(summary, str)
    assert "TEST" in summary
    assert "RSI" in summary
    assert "MA" in summary or "trend" in summary


def test_technical_indicators_to_dict(calculator, sample_data):
    """Test converting indicators to dictionary."""
    indicators = calculator.calculate_all_indicators(ticker="TEST", df=sample_data)

    ind_dict = indicators.to_dict()

    assert isinstance(ind_dict, dict)
    assert "ticker" in ind_dict
    assert "current_price" in ind_dict
    assert "ma_20" in ind_dict
    assert "rsi" in ind_dict
    assert ind_dict["ticker"] == "TEST"


def test_rsi_extreme_values(calculator):
    """Test RSI with extreme price movements."""
    # Strongly uptrending prices
    dates = pd.date_range(start="2025-01-01", periods=50, freq="D")
    prices_up = pd.Series(range(100, 150), index=dates)

    rsi_up = calculator.calculate_rsi(prices_up)

    # Should show high RSI (overbought)
    assert rsi_up.iloc[-1] > 70

    # Strongly downtrending prices
    prices_down = pd.Series(range(150, 100, -1), index=dates)

    rsi_down = calculator.calculate_rsi(prices_down)

    # Should show low RSI (oversold)
    assert rsi_down.iloc[-1] < 30


def test_bollinger_bands_volatility(calculator):
    """Test Bollinger Bands with different volatility."""
    dates = pd.date_range(start="2025-01-01", periods=100, freq="D")

    # Low volatility prices
    np.random.seed(42)
    prices_stable = pd.Series(100 + np.random.randn(100) * 0.1, index=dates)

    upper_stable, _middle_stable, lower_stable = calculator.calculate_bollinger_bands(prices_stable)

    # High volatility prices
    prices_volatile = pd.Series(100 + np.random.randn(100) * 5, index=dates)

    upper_volatile, _middle_volatile, lower_volatile = calculator.calculate_bollinger_bands(
        prices_volatile
    )

    # Band width should be larger for volatile prices
    stable_width = upper_stable.iloc[-1] - lower_stable.iloc[-1]
    volatile_width = upper_volatile.iloc[-1] - lower_volatile.iloc[-1]

    assert volatile_width > stable_width
