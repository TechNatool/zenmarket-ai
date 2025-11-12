"""
Tests for signal generator.
"""

import pytest

from src.advisor.indicators import TechnicalIndicators
from src.advisor.signal_generator import SignalGenerator, SignalType, TradingSignal


@pytest.fixture
def generator():
    """Create a signal generator instance."""
    return SignalGenerator()


@pytest.fixture
def bullish_indicators():
    """Create bullish technical indicators."""
    return TechnicalIndicators(
        ticker="BULL",
        current_price=105.0,
        ma_20=104.0,
        ma_50=100.0,  # MA20 > MA50 = bullish
        rsi=55.0,  # Neutral RSI
        bb_upper=110.0,
        bb_middle=105.0,
        bb_lower=100.0,
        volume_avg=1000000,
        current_volume=1200000,
    )


@pytest.fixture
def bearish_indicators():
    """Create bearish technical indicators."""
    return TechnicalIndicators(
        ticker="BEAR",
        current_price=95.0,
        ma_20=96.0,
        ma_50=100.0,  # MA20 < MA50 = bearish
        rsi=45.0,  # Neutral RSI
        bb_upper=110.0,
        bb_middle=100.0,
        bb_lower=90.0,
        volume_avg=1000000,
        current_volume=800000,
    )


@pytest.fixture
def oversold_indicators():
    """Create oversold indicators."""
    return TechnicalIndicators(
        ticker="OVERSOLD",
        current_price=90.0,
        ma_20=92.0,
        ma_50=95.0,
        rsi=25.0,  # Oversold
        bb_upper=110.0,
        bb_middle=100.0,
        bb_lower=90.0,
        volume_avg=1000000,
    )


@pytest.fixture
def overbought_indicators():
    """Create overbought indicators."""
    return TechnicalIndicators(
        ticker="OVERBOUGHT",
        current_price=110.0,
        ma_20=108.0,
        ma_50=105.0,
        rsi=75.0,  # Overbought
        bb_upper=110.0,
        bb_middle=105.0,
        bb_lower=100.0,
        volume_avg=1000000,
    )


def test_generator_initialization(generator):
    """Test generator can be initialized."""
    assert generator is not None
    assert generator.rsi_overbought == 70.0
    assert generator.rsi_oversold == 30.0


def test_bullish_signal(generator, bullish_indicators):
    """Test generation of bullish signal."""
    signal = generator.generate_signal(bullish_indicators)

    assert isinstance(signal, TradingSignal)
    assert signal.ticker == "BULL"
    assert signal.signal in [SignalType.BUY, SignalType.HOLD]
    assert 0.0 <= signal.confidence <= 1.0
    assert len(signal.reasons) > 0


def test_bearish_signal(generator, bearish_indicators):
    """Test generation of bearish signal."""
    signal = generator.generate_signal(bearish_indicators)

    assert isinstance(signal, TradingSignal)
    assert signal.ticker == "BEAR"
    assert signal.signal in [SignalType.SELL, SignalType.HOLD]
    assert 0.0 <= signal.confidence <= 1.0


def test_oversold_signal(generator, oversold_indicators):
    """Test signal for oversold conditions."""
    signal = generator.generate_signal(oversold_indicators)

    # Oversold should favor BUY or HOLD
    assert signal.signal in [SignalType.BUY, SignalType.HOLD]
    # Should mention RSI in reasons
    assert any("RSI" in reason for reason in signal.reasons)


def test_overbought_signal(generator, overbought_indicators):
    """Test signal for overbought conditions."""
    signal = generator.generate_signal(overbought_indicators)

    # Overbought should favor SELL or HOLD
    assert signal.signal in [SignalType.SELL, SignalType.HOLD]
    # Should mention RSI in reasons
    assert any("RSI" in reason for reason in signal.reasons)


def test_generate_signals_batch(generator, bullish_indicators, bearish_indicators):
    """Test batch signal generation."""
    indicators_list = [bullish_indicators, bearish_indicators]

    signals = generator.generate_signals_batch(indicators_list)

    assert len(signals) == 2
    assert all(isinstance(s, TradingSignal) for s in signals)
    assert signals[0].ticker == "BULL"
    assert signals[1].ticker == "BEAR"


def test_get_market_bias(generator):
    """Test market bias calculation."""
    # Create mixed signals
    signals = [
        TradingSignal("TEST1", SignalType.BUY, 0.8, [], None),
        TradingSignal("TEST2", SignalType.BUY, 0.7, [], None),
        TradingSignal("TEST3", SignalType.SELL, 0.5, [], None),
    ]

    bias, score = generator.get_market_bias(signals)

    assert isinstance(bias, str)
    assert isinstance(score, float)
    assert -1.0 <= score <= 1.0
    # Should be bullish (2 buy vs 1 sell)
    assert score > 0


def test_get_signal_summary(generator):
    """Test signal summary generation."""
    signals = [
        TradingSignal("TEST1", SignalType.BUY, 0.8, [], None),
        TradingSignal("TEST2", SignalType.SELL, 0.7, [], None),
        TradingSignal("TEST3", SignalType.HOLD, 0.5, [], None),
        TradingSignal("TEST4", SignalType.BUY, 0.6, [], None),
    ]

    summary = generator.get_signal_summary(signals)

    assert isinstance(summary, dict)
    assert summary["total"] == 4
    assert summary["buy"] == 2
    assert summary["sell"] == 1
    assert summary["hold"] == 1
    assert summary["buy_pct"] == 50.0
    assert "avg_confidence" in summary


def test_signal_emoji(generator, bullish_indicators):
    """Test signal emoji generation."""
    signal = generator.generate_signal(bullish_indicators)

    emoji = signal.get_emoji()

    assert isinstance(emoji, str)
    assert len(emoji) > 0


def test_signal_trend_description(generator, bullish_indicators, bearish_indicators):
    """Test trend description."""
    bullish_signal = generator.generate_signal(bullish_indicators)
    bearish_signal = generator.generate_signal(bearish_indicators)

    bullish_desc = bullish_signal.get_trend_description()
    bearish_desc = bearish_signal.get_trend_description()

    assert isinstance(bullish_desc, str)
    assert isinstance(bearish_desc, str)
    assert "Haussière" in bullish_desc or "Baissière" in bullish_desc or "Neutre" in bullish_desc


def test_signal_to_dict(generator, bullish_indicators):
    """Test signal to dictionary conversion."""
    signal = generator.generate_signal(bullish_indicators)

    signal_dict = signal.to_dict()

    assert isinstance(signal_dict, dict)
    assert "ticker" in signal_dict
    assert "signal" in signal_dict
    assert "confidence" in signal_dict
    assert "reasons" in signal_dict
    assert "trend" in signal_dict


def test_strong_oversold_signal(generator):
    """Test very strong oversold condition."""
    indicators = TechnicalIndicators(
        ticker="STRONG_OVERSOLD",
        current_price=80.0,
        ma_20=85.0,
        ma_50=90.0,
        rsi=15.0,  # Very oversold
        bb_upper=100.0,
        bb_middle=90.0,
        bb_lower=80.0,
        volume_avg=1000000,
    )

    signal = generator.generate_signal(indicators)

    # Should generate BUY or HOLD (not SELL at extreme oversold)
    assert signal.signal != SignalType.SELL
    assert signal.confidence > 0.0


def test_strong_overbought_signal(generator):
    """Test very strong overbought condition."""
    indicators = TechnicalIndicators(
        ticker="STRONG_OVERBOUGHT",
        current_price=120.0,
        ma_20=115.0,
        ma_50=110.0,
        rsi=85.0,  # Very overbought
        bb_upper=120.0,
        bb_middle=110.0,
        bb_lower=100.0,
        volume_avg=1000000,
    )

    signal = generator.generate_signal(indicators)

    # Should generate SELL or HOLD (not BUY at extreme overbought)
    assert signal.signal != SignalType.BUY
