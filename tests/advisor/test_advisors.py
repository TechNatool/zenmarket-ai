"""Tests for advisor modules (signal generator, sentiment analyzer, etc.)."""

import pandas as pd

from src.advisor.indicators import IndicatorCalculator, TechnicalIndicators
from src.advisor.signal_generator import SignalGenerator, SignalType, TradingSignal
from src.core.sentiment_analyzer import SentimentAnalyzer, SentimentResult


def test_signal_generator_basic_signal():
    """Test signal generator produces basic BUY/SELL/HOLD signals."""
    generator = SignalGenerator()

    # Create bullish indicators
    bullish_indicators = TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=145.0,
        ma_50=140.0,
        rsi=45.0,  # Neutral RSI
        bb_upper=155.0,
        bb_middle=150.0,
        bb_lower=145.0,
        volume_avg=950000.0,
        current_volume=1000000,
        atr=2.5,
    )

    signal = generator.generate_signal(bullish_indicators)

    assert isinstance(signal, TradingSignal)
    assert signal.ticker == "AAPL"
    assert signal.signal in [SignalType.BUY, SignalType.SELL, SignalType.HOLD]
    assert 0.0 <= signal.confidence <= 1.0
    assert isinstance(signal.reasons, list)


def test_signal_generator_extreme_values():
    """Test signal generator with extreme RSI values."""
    generator = SignalGenerator()

    # Extremely overbought
    overbought_indicators = TechnicalIndicators(
        ticker="TEST",
        current_price=200.0,
        ma_20=190.0,
        ma_50=180.0,
        rsi=85.0,  # Very overbought
        bb_upper=210.0,
        bb_middle=200.0,
        bb_lower=190.0,
        volume_avg=1500000.0,
        current_volume=2000000,
        atr=3.0,
    )

    signal = generator.generate_signal(overbought_indicators)
    # Should likely be SELL or HOLD with high RSI
    assert signal.signal in [SignalType.SELL, SignalType.HOLD]

    # Extremely oversold
    oversold_indicators = TechnicalIndicators(
        ticker="TEST",
        current_price=100.0,
        ma_20=110.0,
        ma_50=120.0,
        rsi=15.0,  # Very oversold
        bb_upper=130.0,
        bb_middle=110.0,
        bb_lower=90.0,
        volume_avg=2000000.0,
        current_volume=3000000,
        atr=4.0,
    )

    signal = generator.generate_signal(oversold_indicators)
    # Should likely be BUY with very low RSI
    assert signal.signal in [SignalType.BUY, SignalType.HOLD]


def test_news_analyzer_with_missing_data():
    """Test sentiment analyzer handles missing/empty data."""
    analyzer = SentimentAnalyzer()

    # Empty text
    result = analyzer.analyze("")
    assert isinstance(result, SentimentResult)
    assert result.sentiment in ["positive", "negative", "neutral"]

    # None text (should handle gracefully)
    try:
        result = analyzer.analyze(None)
        assert isinstance(result, SentimentResult)
    except (TypeError, AttributeError):
        # Acceptable to raise error for None
        pass


def test_sentiment_analyzer_outputs_range():
    """Test sentiment analyzer outputs are in correct range."""
    analyzer = SentimentAnalyzer()

    positive_text = "Great profit! Strong growth and bullish momentum!"
    negative_text = "Terrible loss! Falling prices and bearish sentiment!"
    neutral_text = "The company announced a meeting."

    pos_result = analyzer.analyze(positive_text)
    assert -1.0 <= pos_result.score <= 1.0
    assert 0.0 <= pos_result.confidence <= 1.0
    assert pos_result.sentiment == "positive"

    neg_result = analyzer.analyze(negative_text)
    assert -1.0 <= neg_result.score <= 1.0
    assert 0.0 <= neg_result.confidence <= 1.0
    assert neg_result.sentiment == "negative"

    neu_result = analyzer.analyze(neutral_text)
    assert -1.0 <= neu_result.score <= 1.0
    assert 0.0 <= neu_result.confidence <= 1.0


def test_advisor_pipeline_runs():
    """Test complete advisor pipeline (indicators -> signals)."""
    # Create sample data
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    data = {
        "Open": [100 + i * 0.5 for i in range(100)],
        "High": [102 + i * 0.5 for i in range(100)],
        "Low": [98 + i * 0.5 for i in range(100)],
        "Close": [101 + i * 0.5 for i in range(100)],
        "Volume": [1000000 + i * 1000 for i in range(100)],
    }
    df = pd.DataFrame(data, index=dates)

    # Calculate indicators
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_all_indicators("AAPL", df)

    assert indicators is not None
    assert isinstance(indicators, TechnicalIndicators)

    # Generate signal
    generator = SignalGenerator()
    signal = generator.generate_signal(indicators)

    assert isinstance(signal, TradingSignal)
    assert signal.ticker == "AAPL"


def test_signal_generator_confidence_calculation():
    """Test signal confidence is calculated correctly."""
    generator = SignalGenerator()

    # Strong bullish setup
    strong_bull = TechnicalIndicators(
        ticker="TEST",
        current_price=150.0,
        ma_20=148.0,
        ma_50=140.0,  # MA20 > MA50
        rsi=35.0,  # Slightly oversold
        bb_upper=155.0,
        bb_middle=150.0,
        bb_lower=145.0,
        volume_avg=1500000.0,
        current_volume=2000000,
        atr=2.0,
    )

    signal = generator.generate_signal(strong_bull)
    assert signal.confidence > 0.0


def test_signal_to_dict():
    """Test signal serialization to dictionary."""
    indicators = TechnicalIndicators(
        ticker="AAPL",
        current_price=150.0,
        ma_20=145.0,
        ma_50=140.0,
        rsi=50.0,
        bb_upper=160.0,
        bb_middle=150.0,
        bb_lower=140.0,
        volume_avg=900000.0,
        current_volume=1000000,
        atr=2.5,
    )

    generator = SignalGenerator()
    signal = generator.generate_signal(indicators)

    signal_dict = signal.to_dict()

    assert isinstance(signal_dict, dict)
    assert "ticker" in signal_dict
    assert "signal" in signal_dict
    assert "confidence" in signal_dict
    assert "reasons" in signal_dict
    assert "indicators" in signal_dict
    assert signal_dict["ticker"] == "AAPL"


def test_signal_get_emoji():
    """Test signal emoji generation."""
    indicators = TechnicalIndicators(
        ticker="TEST",
        current_price=100.0,
        ma_20=100.0,
        ma_50=100.0,
        rsi=50.0,
        bb_upper=110.0,
        bb_middle=100.0,
        bb_lower=90.0,
        volume_avg=1000000.0,
        current_volume=1000000,
        atr=2.0,
    )

    signal = TradingSignal(
        ticker="TEST",
        signal=SignalType.BUY,
        confidence=0.8,
        reasons=["Test"],
        indicators=indicators,
    )

    emoji = signal.get_emoji()
    assert emoji in ["📈", "📉", "⚖️", "➖"]


def test_signal_generator_batch_processing():
    """Test signal generator can process multiple indicators."""
    generator = SignalGenerator()

    indicators_list = []
    for i in range(5):
        indicators = TechnicalIndicators(
            ticker=f"STOCK{i}",
            current_price=100.0 + i * 10,
            ma_20=100.0 + i * 9,
            ma_50=100.0 + i * 8,
            rsi=50.0 + i,
            bb_upper=110.0 + i * 10,
            bb_middle=100.0 + i * 10,
            bb_lower=90.0 + i * 10,
            volume_avg=950000.0,
            current_volume=1000000,
            atr=2.0,
        )
        indicators_list.append(indicators)

    signals = [generator.generate_signal(ind) for ind in indicators_list]

    assert len(signals) == 5
    assert all(isinstance(s, TradingSignal) for s in signals)


def test_sentiment_analyzer_batch():
    """Test sentiment analyzer batch processing."""
    analyzer = SentimentAnalyzer()

    texts = [
        "Great profit and strong growth!",
        "Terrible loss and declining revenue!",
        "Neutral statement about the market.",
    ]

    results = analyzer.analyze_batch(texts)

    assert len(results) == 3
    assert all(isinstance(r, SentimentResult) for r in results)
    assert results[0].sentiment == "positive"
    assert results[1].sentiment == "negative"


def test_sentiment_overall():
    """Test overall sentiment calculation."""
    analyzer = SentimentAnalyzer()

    texts = [
        "Excellent performance!",
        "Strong buy!",
        "Minor decline",
    ]

    # First analyze the texts
    results = analyzer.analyze_batch(texts)

    # Then get overall sentiment
    sentiment, avg_score = analyzer.get_overall_sentiment(results)

    assert isinstance(sentiment, str)
    assert sentiment in ["positive", "negative", "neutral"]
    assert isinstance(avg_score, float)
    assert -1.0 <= avg_score <= 1.0


def test_indicator_calculator_edge_cases():
    """Test indicator calculator with edge cases."""
    calculator = IndicatorCalculator()

    # Insufficient data
    small_df = pd.DataFrame(
        {
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Volume": [1000, 1100],
        }
    )

    result = calculator.calculate_all_indicators("TEST", small_df)
    # Should return None or handle gracefully
    assert result is None

    # All same values (no volatility)
    flat_df = pd.DataFrame(
        {
            "Open": [100] * 60,
            "High": [100] * 60,
            "Low": [100] * 60,
            "Close": [100] * 60,
            "Volume": [1000] * 60,
        }
    )

    result = calculator.calculate_all_indicators("FLAT", flat_df)
    if result:
        # ATR should be very low or zero
        assert result.atr >= 0


def test_signal_generator_custom_thresholds():
    """Test signal generator with custom RSI thresholds."""
    generator = SignalGenerator(
        rsi_overbought=75.0,
        rsi_oversold=25.0,
        rsi_strong_overbought=85.0,
        rsi_strong_oversold=15.0,
    )

    assert generator.rsi_overbought == 75.0
    assert generator.rsi_oversold == 25.0

    indicators = TechnicalIndicators(
        ticker="TEST",
        current_price=100.0,
        ma_20=100.0,
        ma_50=95.0,
        rsi=72.0,  # Between 70 and 75
        bb_upper=105.0,
        bb_middle=100.0,
        bb_lower=95.0,
        volume_avg=950000.0,
        current_volume=1000000,
        atr=2.0,
    )

    signal = generator.generate_signal(indicators)
    # With custom threshold, 72 RSI might not be considered overbought
    assert isinstance(signal, TradingSignal)


def test_sentiment_distribution():
    """Test sentiment distribution calculation."""
    analyzer = SentimentAnalyzer()

    texts = [
        "Great!",
        "Excellent!",
        "Terrible!",
        "Awful!",
        "Neutral statement",
        "Another neutral one",
    ]

    results = analyzer.analyze_batch(texts)
    distribution = analyzer.get_sentiment_distribution(results)

    assert isinstance(distribution, dict)
    assert "positive" in distribution
    assert "negative" in distribution
    assert "neutral" in distribution
    # Distribution returns counts, not percentages
    assert distribution["positive"] + distribution["negative"] + distribution["neutral"] == len(
        texts
    )


def test_signal_trend_description():
    """Test signal trend description generation."""
    # MA20 > MA50 (bullish trend)
    indicators_bull = TechnicalIndicators(
        ticker="TEST",
        current_price=100.0,
        ma_20=105.0,
        ma_50=95.0,
        rsi=50.0,
        bb_upper=110.0,
        bb_middle=100.0,
        bb_lower=90.0,
        volume_avg=950000.0,
        current_volume=1000000,
        atr=2.0,
    )

    signal_bull = TradingSignal(
        ticker="TEST",
        signal=SignalType.BUY,
        confidence=0.7,
        reasons=["Bullish setup"],
        indicators=indicators_bull,
    )

    trend = signal_bull.get_trend_description()
    assert "Haussière" in trend or "haussi" in trend.lower()

    # MA20 < MA50 (bearish trend)
    indicators_bear = TechnicalIndicators(
        ticker="TEST",
        current_price=100.0,
        ma_20=95.0,
        ma_50=105.0,
        rsi=50.0,
        bb_upper=110.0,
        bb_middle=100.0,
        bb_lower=90.0,
        volume_avg=950000.0,
        current_volume=1000000,
        atr=2.0,
    )

    signal_bear = TradingSignal(
        ticker="TEST",
        signal=SignalType.SELL,
        confidence=0.7,
        reasons=["Bearish setup"],
        indicators=indicators_bear,
    )

    trend = signal_bear.get_trend_description()
    assert "Baissière" in trend or "baissi" in trend.lower()
