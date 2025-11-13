"""Additional comprehensive tests for sentiment_analyzer module."""

from unittest.mock import Mock, patch

import pytest

from src.core.sentiment_analyzer import SentimentAnalyzer, SentimentResult


@pytest.fixture
def analyzer():
    """Create a sentiment analyzer instance."""
    return SentimentAnalyzer()


@pytest.fixture
def mock_config_openai():
    """Mock configuration with OpenAI."""
    config = Mock()
    config.ai_provider = "openai"
    config.openai_api_key = "test-key-openai"
    config.openai_model = "gpt-4"
    config.anthropic_api_key = None
    return config


@pytest.fixture
def mock_config_anthropic():
    """Mock configuration with Anthropic."""
    config = Mock()
    config.ai_provider = "anthropic"
    config.anthropic_api_key = "test-key-anthropic"
    config.anthropic_model = "claude-3-5-sonnet-20241022"
    config.openai_api_key = None
    return config


@pytest.fixture
def mock_config_no_ai():
    """Mock configuration without AI."""
    config = Mock()
    config.ai_provider = None
    config.openai_api_key = None
    config.anthropic_api_key = None
    return config


def test_analyze_with_ai_openai(analyzer, mock_config_openai):
    """Test analyze_with_ai using OpenAI."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_openai):
        analyzer.config = mock_config_openai

        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sentiment": "positive", "score": 0.8, "confidence": 0.9}'
        mock_openai.chat.completions.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": mock_openai}):
            result = analyzer.analyze_with_ai("Great news about the market!")

            assert result is not None
            assert result.sentiment == "positive"
            assert result.score == 0.8
            assert result.confidence == 0.9
            assert result.method == "openai"


def test_analyze_with_ai_anthropic(analyzer, mock_config_anthropic):
    """Test analyze_with_ai using Anthropic."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_anthropic):
        analyzer.config = mock_config_anthropic

        mock_anthropic = Mock()
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = '{"sentiment": "negative", "score": -0.6, "confidence": 0.85}'
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = analyzer.analyze_with_ai("Market crashes today")

            assert result is not None
            assert result.sentiment == "negative"
            assert result.score == -0.6
            assert result.confidence == 0.85
            assert result.method == "anthropic"


def test_analyze_with_ai_no_provider(analyzer, mock_config_no_ai):
    """Test analyze_with_ai with no AI provider configured."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_no_ai):
        analyzer.config = mock_config_no_ai

        result = analyzer.analyze_with_ai("Test text")

        assert result is None


def test_analyze_with_ai_exception_handling(analyzer, mock_config_openai):
    """Test analyze_with_ai handles exceptions."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_openai):
        analyzer.config = mock_config_openai

        mock_openai = Mock()
        mock_openai.chat.completions.create.side_effect = Exception("API Error")

        with patch.dict("sys.modules", {"openai": mock_openai}):
            result = analyzer.analyze_with_ai("Test text")

            assert result is None


def test_analyze_openai_long_text(analyzer, mock_config_openai):
    """Test _analyze_with_openai truncates long text in result."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_openai):
        analyzer.config = mock_config_openai

        long_text = "A" * 200  # Text longer than 100 chars

        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sentiment": "neutral", "score": 0.1, "confidence": 0.7}'
        mock_openai.chat.completions.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": mock_openai}):
            result = analyzer._analyze_with_openai(long_text)

            assert result.text.endswith("...")
            assert len(result.text) == 103  # 100 chars + "..."


def test_analyze_anthropic_long_text(analyzer, mock_config_anthropic):
    """Test _analyze_with_anthropic truncates long text in result."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_anthropic):
        analyzer.config = mock_config_anthropic

        long_text = "B" * 250

        mock_anthropic = Mock()
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = '{"sentiment": "positive", "score": 0.5, "confidence": 0.8}'
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = analyzer._analyze_with_anthropic(long_text)

            assert result.text.endswith("...")


def test_analyze_with_use_ai_true(analyzer, mock_config_openai):
    """Test analyze() method with use_ai=True."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_openai):
        analyzer.config = mock_config_openai

        mock_ai_result = SentimentResult("text", "positive", 0.9, 0.95, "openai")

        with patch.object(analyzer, "analyze_with_ai", return_value=mock_ai_result):
            result = analyzer.analyze("Great market news", use_ai=True)

            assert result.method == "openai"
            assert result.score == 0.9


def test_analyze_with_use_ai_true_fallback(analyzer, mock_config_no_ai):
    """Test analyze() with use_ai=True falls back to lexicon when AI unavailable."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_no_ai):
        analyzer.config = mock_config_no_ai

        with patch.object(analyzer, "analyze_with_ai", return_value=None):
            result = analyzer.analyze("Market gains are strong", use_ai=True)

            assert result.method == "lexicon"


def test_analyze_batch_with_exception(analyzer):
    """Test analyze_batch handles exceptions for individual texts."""
    texts = ["Good text", "Bad text that causes error", "Another good text"]

    with patch.object(analyzer, "analyze") as mock_analyze:
        # First and third succeed, second fails
        mock_analyze.side_effect = [
            SentimentResult("text1", "positive", 0.8, 0.9, "lexicon"),
            Exception("Analysis error"),
            SentimentResult("text3", "neutral", 0.1, 0.6, "lexicon"),
        ]

        results = analyzer.analyze_batch(texts, use_ai=False)

        assert len(results) == 3
        assert results[0].sentiment == "positive"
        assert results[1].sentiment == "neutral"  # Error fallback
        assert results[1].method == "error"
        assert results[1].score == 0.0
        assert results[2].sentiment == "neutral"


def test_analyze_batch_logging_every_10(analyzer):
    """Test analyze_batch logs progress every 10 items."""
    texts = [f"Text {i}" for i in range(25)]

    with patch.object(analyzer, "analyze") as mock_analyze:
        mock_analyze.return_value = SentimentResult("text", "neutral", 0.0, 0.5, "lexicon")

        results = analyzer.analyze_batch(texts, use_ai=False)

        assert len(results) == 25
        # Progress should be logged at items 10, 20


def test_get_overall_sentiment_empty_list(analyzer):
    """Test get_overall_sentiment with empty results list."""
    sentiment, score = analyzer.get_overall_sentiment([])

    assert sentiment == "neutral"
    assert score == 0.0


def test_get_overall_sentiment_all_zero_confidence(analyzer):
    """Test get_overall_sentiment when all confidences are zero."""
    results = [
        SentimentResult("text1", "positive", 0.8, 0.0, "lexicon"),
        SentimentResult("text2", "negative", -0.6, 0.0, "lexicon"),
    ]

    sentiment, score = analyzer.get_overall_sentiment(results)

    assert sentiment == "neutral"
    assert score == 0.0


def test_get_overall_sentiment_positive(analyzer):
    """Test get_overall_sentiment returns positive."""
    results = [
        SentimentResult("text1", "positive", 0.8, 1.0, "lexicon"),
        SentimentResult("text2", "positive", 0.6, 1.0, "lexicon"),
        SentimentResult("text3", "neutral", 0.1, 0.5, "lexicon"),
    ]

    sentiment, score = analyzer.get_overall_sentiment(results)

    assert sentiment == "positive"
    assert score > 0.2


def test_get_overall_sentiment_negative(analyzer):
    """Test get_overall_sentiment returns negative."""
    results = [
        SentimentResult("text1", "negative", -0.8, 1.0, "lexicon"),
        SentimentResult("text2", "negative", -0.6, 1.0, "lexicon"),
        SentimentResult("text3", "neutral", -0.1, 0.5, "lexicon"),
    ]

    sentiment, score = analyzer.get_overall_sentiment(results)

    assert sentiment == "negative"
    assert score < -0.2


def test_get_overall_sentiment_neutral_boundary(analyzer):
    """Test get_overall_sentiment returns neutral for boundary scores."""
    results = [
        SentimentResult("text1", "positive", 0.15, 1.0, "lexicon"),
        SentimentResult("text2", "negative", -0.05, 1.0, "lexicon"),
    ]

    sentiment, score = analyzer.get_overall_sentiment(results)

    assert sentiment == "neutral"
    assert -0.2 <= score <= 0.2


def test_analyze_lexicon_negated_positive_word(analyzer):
    """Test negation flips positive sentiment to negative."""
    text = "not rising profits and no gains"
    result = analyzer.analyze_lexicon(text)

    # Negated positive words should reduce or flip score
    assert result.score < 0.5  # Should be less positive or negative


def test_analyze_lexicon_negated_negative_word(analyzer):
    """Test negation flips negative sentiment to positive."""
    text = "not falling and no losses here"
    result = analyzer.analyze_lexicon(text)

    # Negated negative words should increase score
    assert result.score > -0.5  # Should be less negative or positive


def test_analyze_lexicon_intensifier_negative(analyzer):
    """Test intensifier boosts negative sentiment."""
    normal_text = "losses in the market"
    intensified_text = "very losses in the market"  # Intensifier before negative word

    result_normal = analyzer.analyze_lexicon(normal_text)
    result_intensified = analyzer.analyze_lexicon(intensified_text)

    # Intensified negative should be more negative
    assert result_intensified.score <= result_normal.score


def test_analyze_lexicon_text_truncation(analyzer):
    """Test analyze_lexicon truncates long text in result."""
    long_text = "Market " * 50 + "gains"  # Long text with positive word

    result = analyzer.analyze_lexicon(long_text)

    assert len(result.text) <= 103  # 100 chars + "..."
    if len(long_text) > 100:
        assert result.text.endswith("...")


def test_analyze_lexicon_confidence_scaling(analyzer):
    """Test confidence scales with number of sentiment words."""
    # Text with 2 sentiment words
    text_few = "gains and profits"
    # Text with many sentiment words
    text_many = "gains profits rise surge rally growth strong bullish beat advance soar"

    result_few = analyzer.analyze_lexicon(text_few)
    result_many = analyzer.analyze_lexicon(text_many)

    # More sentiment words should give higher confidence (capped at 1.0)
    assert result_many.confidence >= result_few.confidence


def test_get_sentiment_distribution_multiple_same(analyzer):
    """Test sentiment distribution with multiple of same sentiment."""
    results = [
        SentimentResult("text1", "positive", 0.8, 0.9, "lexicon"),
        SentimentResult("text2", "positive", 0.7, 0.8, "lexicon"),
        SentimentResult("text3", "positive", 0.9, 0.95, "lexicon"),
    ]

    distribution = analyzer.get_sentiment_distribution(results)

    assert distribution["positive"] == 3
    assert distribution["negative"] == 0
    assert distribution["neutral"] == 0


def test_sentiment_result_dataclass():
    """Test SentimentResult dataclass creation."""
    result = SentimentResult(
        text="Test text", sentiment="positive", score=0.75, confidence=0.85, method="lexicon"
    )

    assert result.text == "Test text"
    assert result.sentiment == "positive"
    assert result.score == 0.75
    assert result.confidence == 0.85
    assert result.method == "lexicon"


def test_analyze_lexicon_score_clamping(analyzer):
    """Test that scores are clamped to [-1.0, 1.0] range."""
    # Create text with extreme sentiment words to test clamping
    extreme_positive = " ".join(list(analyzer.POSITIVE_WORDS)[:20])

    result = analyzer.analyze_lexicon(extreme_positive)

    assert -1.0 <= result.score <= 1.0


def test_openai_model_configuration(analyzer, mock_config_openai):
    """Test that OpenAI uses configured model."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_openai):
        analyzer.config = mock_config_openai

        mock_openai = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sentiment": "neutral", "score": 0.0, "confidence": 0.5}'
        mock_openai.chat.completions.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": mock_openai}):
            analyzer._analyze_with_openai("Test")

            # Verify model was passed correctly
            call_kwargs = mock_openai.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["temperature"] == 0.0
            assert call_kwargs["max_tokens"] == 100


def test_anthropic_model_configuration(analyzer, mock_config_anthropic):
    """Test that Anthropic uses configured model."""
    with patch("src.core.sentiment_analyzer.get_config", return_value=mock_config_anthropic):
        analyzer.config = mock_config_anthropic

        mock_anthropic = Mock()
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = '{"sentiment": "neutral", "score": 0.0, "confidence": 0.5}'
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            analyzer._analyze_with_anthropic("Test")

            # Verify model was passed correctly
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
            assert call_kwargs["temperature"] == 0.0
            assert call_kwargs["max_tokens"] == 100
