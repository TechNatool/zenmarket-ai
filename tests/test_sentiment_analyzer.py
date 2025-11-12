"""
Tests for sentiment analyzer module.
"""

import pytest

from src.core.sentiment_analyzer import SentimentAnalyzer, SentimentResult


@pytest.fixture
def analyzer():
    """Create a sentiment analyzer instance."""
    return SentimentAnalyzer()


def test_analyzer_initialization(analyzer):
    """Test analyzer can be initialized."""
    assert analyzer is not None
    assert hasattr(analyzer, "POSITIVE_WORDS")
    assert hasattr(analyzer, "NEGATIVE_WORDS")


def test_positive_sentiment(analyzer):
    """Test detection of positive sentiment."""
    text = "Stocks surge as profits soar and market rallies with strong gains"
    result = analyzer.analyze_lexicon(text)

    assert isinstance(result, SentimentResult)
    assert result.sentiment == "positive"
    assert result.score > 0


def test_negative_sentiment(analyzer):
    """Test detection of negative sentiment."""
    text = "Market crashes as losses mount, stocks plunge amid recession fears"
    result = analyzer.analyze_lexicon(text)

    assert isinstance(result, SentimentResult)
    assert result.sentiment == "negative"
    assert result.score < 0


def test_neutral_sentiment(analyzer):
    """Test detection of neutral sentiment."""
    text = "The company held a meeting to discuss the quarterly report"
    result = analyzer.analyze_lexicon(text)

    assert isinstance(result, SentimentResult)
    assert result.sentiment == "neutral"
    assert -0.3 < result.score < 0.3


def test_negation_handling(analyzer):
    """Test that negations are handled correctly."""
    positive_text = "Profits are rising"
    negative_negated = "Profits are not rising"

    result_pos = analyzer.analyze_lexicon(positive_text)
    result_neg = analyzer.analyze_lexicon(negative_negated)

    assert result_pos.score > result_neg.score


def test_batch_analysis(analyzer):
    """Test analyzing multiple texts."""
    texts = [
        "Stock prices surge with excellent gains",
        "Market crashes with heavy losses",
        "The meeting was held today",
    ]

    results = analyzer.analyze_batch(texts, use_ai=False)

    assert len(results) == 3
    assert all(isinstance(r, SentimentResult) for r in results)
    assert results[0].sentiment == "positive"
    assert results[1].sentiment == "negative"


def test_overall_sentiment(analyzer):
    """Test overall sentiment calculation."""
    results = [
        SentimentResult("text1", "positive", 0.8, 0.9, "lexicon"),
        SentimentResult("text2", "positive", 0.6, 0.8, "lexicon"),
        SentimentResult("text3", "negative", -0.4, 0.7, "lexicon"),
    ]

    sentiment, score = analyzer.get_overall_sentiment(results)

    assert sentiment in ["positive", "negative", "neutral"]
    assert isinstance(score, float)
    assert -1.0 <= score <= 1.0


def test_sentiment_distribution(analyzer):
    """Test sentiment distribution calculation."""
    results = [
        SentimentResult("text1", "positive", 0.8, 0.9, "lexicon"),
        SentimentResult("text2", "positive", 0.6, 0.8, "lexicon"),
        SentimentResult("text3", "negative", -0.4, 0.7, "lexicon"),
        SentimentResult("text4", "neutral", 0.1, 0.5, "lexicon"),
    ]

    distribution = analyzer.get_sentiment_distribution(results)

    assert isinstance(distribution, dict)
    assert distribution["positive"] == 2
    assert distribution["negative"] == 1
    assert distribution["neutral"] == 1
    assert sum(distribution.values()) == 4


def test_empty_text(analyzer):
    """Test handling of empty text."""
    result = analyzer.analyze_lexicon("")

    assert result.sentiment == "neutral"
    assert result.score == 0.0


def test_intensifiers(analyzer):
    """Test that intensifiers boost sentiment."""
    normal_text = "good gains in the market"
    intensified_text = "very good gains in the market"

    result_normal = analyzer.analyze_lexicon(normal_text)
    result_intensified = analyzer.analyze_lexicon(intensified_text)

    # Intensified should have stronger sentiment
    assert result_intensified.score >= result_normal.score
