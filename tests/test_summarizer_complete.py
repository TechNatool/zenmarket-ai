"""Comprehensive tests for summarizer.py to reach 90% coverage."""

from unittest.mock import Mock, patch

import pytest

from src.core.summarizer import AISummarizer


@pytest.fixture
def mock_config_openai():
    """Mock config with OpenAI provider."""
    config = Mock()
    config.ai_provider = "openai"
    config.openai_api_key = "sk-test123"
    config.openai_model = "gpt-3.5-turbo"
    config.anthropic_api_key = None
    config.anthropic_model = None
    return config


@pytest.fixture
def mock_config_anthropic():
    """Mock config with Anthropic provider."""
    config = Mock()
    config.ai_provider = "anthropic"
    config.anthropic_api_key = "sk-ant-test123"
    config.anthropic_model = "claude-3-sonnet-20240229"
    config.openai_api_key = None
    config.openai_model = None
    return config


@pytest.fixture
def mock_config_no_ai():
    """Mock config without AI provider."""
    config = Mock()
    config.ai_provider = "none"
    config.openai_api_key = None
    config.anthropic_api_key = None
    return config


@pytest.fixture
def sample_articles():
    """Sample news articles for testing."""
    return [
        {
            "title": "Fed Raises Interest Rates by 0.25%",
            "description": "Federal Reserve announces rate hike to combat inflation",
            "source": "Reuters",
            "url": "https://example.com/1",
        },
        {
            "title": "Tech Stocks Rally on Earnings Beat",
            "description": "NASDAQ surges as major tech companies exceed earnings expectations",
            "source": "Bloomberg",
            "url": "https://example.com/2",
        },
        {
            "title": "Bitcoin Hits New All-Time High",
            "description": "Cryptocurrency market rallies amid institutional adoption",
            "source": "CoinDesk",
            "url": "https://example.com/3",
        },
        {
            "title": "Geopolitical Tensions Rise in Europe",
            "description": "Trade sanctions announced affecting global supply chains",
            "source": "Financial Times",
            "url": "https://example.com/4",
        },
    ]


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "^GSPC": {
            "name": "S&P 500",
            "last_price": 4500.0,
            "change_percent": 1.2,
            "volatility": 15.5,
        },
        "^IXIC": {
            "name": "NASDAQ",
            "last_price": 14000.0,
            "change_percent": 2.1,
            "volatility": 18.3,
        },
        "BTC-USD": {
            "name": "Bitcoin",
            "last_price": 50000.0,
            "change_percent": -3.5,
            "volatility": 45.2,
        },
    }


# ============================================================================
# Test summarize_article()
# ============================================================================


def test_summarize_article_openai(mock_config_openai):
    """Test summarize_article with OpenAI provider."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_openai):
        summarizer = AISummarizer()

        # Mock openai module before it's imported
        mock_openai_module = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Markets rally on positive earnings."
        mock_openai_module.chat.completions.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": mock_openai_module}):
            # Test
            result = summarizer.summarize_article(
                title="Stocks Rise", content="Markets continue upward trend with strong volume"
            )

            assert result == "Markets rally on positive earnings."
            mock_openai_module.chat.completions.create.assert_called_once()


def test_summarize_article_anthropic(mock_config_anthropic):
    """Test summarize_article with Anthropic provider."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_anthropic):
        summarizer = AISummarizer()

        # Mock anthropic module
        mock_anthropic_module = Mock()
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = "Tech stocks lead market gains."
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_module.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
            # Test
            result = summarizer.summarize_article(
                title="Tech Rally", content="Technology sector outperforms broader market"
            )

            assert result == "Tech stocks lead market gains."
            mock_client.messages.create.assert_called_once()


def test_summarize_article_no_ai_fallback(mock_config_no_ai):
    """Test summarize_article fallback when no AI provider."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_no_ai):
        summarizer = AISummarizer()

        # Test fallback (truncation)
        long_content = " ".join(["word"] * 100)
        result = summarizer.summarize_article(
            title="Test", content=long_content, max_words=10
        )

        assert result.endswith("...")
        word_count = len(result.split()) - 1  # -1 for "..."
        assert word_count <= 10


def test_summarize_article_exception_fallback(mock_config_openai):
    """Test summarize_article fallback on AI exception."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_openai):
        summarizer = AISummarizer()

        # Mock openai module that raises exception
        mock_openai_module = Mock()
        mock_openai_module.chat.completions.create.side_effect = Exception("API error")

        with patch.dict("sys.modules", {"openai": mock_openai_module}):
            # Should fallback to truncation
            content = "This is a test article with important financial information"
            result = summarizer.summarize_article(title="Test", content=content, max_words=5)

            assert result.endswith("...")
            assert len(result.split()) <= 6  # 5 words + "..."


# ============================================================================
# Test generate_market_insights()
# ============================================================================


def test_generate_market_insights_openai(mock_config_openai, sample_market_data):
    """Test generate_market_insights with OpenAI."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_openai):
        summarizer = AISummarizer()

        # Mock openai module
        mock_openai_module = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Markets show strong momentum with tech leading gains."
        mock_openai_module.chat.completions.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": mock_openai_module}):
            result = summarizer.generate_market_insights(
                news_summaries=["Stock rally continues", "Tech beats expectations"],
                market_data=sample_market_data,
                sentiment_overall="positive",
            )

            assert "Markets show strong momentum" in result
            mock_openai_module.chat.completions.create.assert_called_once()


def test_generate_market_insights_anthropic(mock_config_anthropic, sample_market_data):
    """Test generate_market_insights with Anthropic."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_anthropic):
        summarizer = AISummarizer()

        # Mock anthropic module
        mock_anthropic_module = Mock()
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = "Bearish signals emerging across indices."
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_module.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
            result = summarizer.generate_market_insights(
                news_summaries=["Market selloff", "Volatility spikes"],
                market_data=sample_market_data,
                sentiment_overall="negative",
            )

            assert "Bearish signals" in result
            mock_client.messages.create.assert_called_once()


def test_generate_market_insights_fallback(mock_config_no_ai, sample_market_data):
    """Test generate_market_insights fallback when no AI."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_no_ai):
        summarizer = AISummarizer()

        result = summarizer.generate_market_insights(
            news_summaries=["News 1", "News 2"],
            market_data=sample_market_data,
            sentiment_overall="positive",
        )

        # Should return fallback insights
        assert "optimistic" in result.lower() or "positive" in result.lower()


def test_generate_market_insights_exception(mock_config_openai, sample_market_data):
    """Test generate_market_insights exception handling."""
    with patch("src.core.summarizer.get_config", return_value=mock_config_openai):
        summarizer = AISummarizer()

        # Mock openai module that raises exception
        mock_openai_module = Mock()
        mock_openai_module.chat.completions.create.side_effect = Exception("Network error")

        with patch.dict("sys.modules", {"openai": mock_openai_module}):
            result = summarizer.generate_market_insights(
                news_summaries=["Test"], market_data=sample_market_data, sentiment_overall="neutral"
            )

            # Should fallback gracefully
            assert "mixed signals" in result.lower() or "balanced" in result.lower()


def test_generate_fallback_insights_positive():
    """Test _generate_fallback_insights with positive sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()
        result = summarizer._generate_fallback_insights("positive")

        assert "optimistic" in result.lower() or "positive" in result.lower()


def test_generate_fallback_insights_negative():
    """Test _generate_fallback_insights with negative sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()
        result = summarizer._generate_fallback_insights("negative")

        assert "concern" in result.lower() or "caution" in result.lower()


def test_generate_fallback_insights_neutral():
    """Test _generate_fallback_insights with neutral sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()
        result = summarizer._generate_fallback_insights("neutral")

        assert "mixed" in result.lower() or "balanced" in result.lower()


def test_generate_fallback_insights_unknown():
    """Test _generate_fallback_insights with unknown sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()
        result = summarizer._generate_fallback_insights("unknown_sentiment")

        # Should default to neutral
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# Test categorize_news()
# ============================================================================


def test_categorize_news(sample_articles):
    """Test categorize_news with various articles."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        categories = summarizer.categorize_news(sample_articles)

        # Verify structure
        assert isinstance(categories, dict)
        assert "interest_rates" in categories
        assert "crypto" in categories
        assert "geopolitics" in categories
        assert "earnings" in categories

        # Verify ALL articles were categorized
        total_categorized = sum(len(cat) for cat in categories.values())
        assert total_categorized == len(sample_articles)

        # Verify at least some non-empty categories exist
        non_empty_categories = [cat for cat, articles in categories.items() if len(articles) > 0]
        assert len(non_empty_categories) > 0


def test_categorize_news_empty():
    """Test categorize_news with empty list."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        categories = summarizer.categorize_news([])

        # Should return empty categories
        assert isinstance(categories, dict)
        assert all(len(articles) == 0 for articles in categories.values())


def test_categorize_news_other_category():
    """Test categorize_news with uncategorized articles."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        articles = [
            {
                "title": "Random Company News",
                "description": "Something unrelated to financial keywords",
            }
        ]

        categories = summarizer.categorize_news(articles)

        # Should go to "other" category
        assert len(categories["other"]) == 1


def test_categorize_news_multiple_keywords():
    """Test categorize_news with articles matching multiple keywords."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        articles = [
            {
                "title": "Fed Interest Rate Decision Impacts NASDAQ",
                "description": "Central bank policy affects stock indices",
            }
        ]

        categories = summarizer.categorize_news(articles)

        # Should be categorized into first matching category
        categorized_count = sum(len(cat) for cat in categories.values())
        assert categorized_count == 1


# ============================================================================
# Test generate_recommendations()
# ============================================================================


def test_generate_recommendations_positive_sentiment(sample_market_data):
    """Test generate_recommendations with positive sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="positive", news_categories={}
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("positive" in rec.lower() or "long" in rec.lower() for rec in recommendations)


def test_generate_recommendations_negative_sentiment(sample_market_data):
    """Test generate_recommendations with negative sentiment."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="negative", news_categories={}
        )

        assert isinstance(recommendations, list)
        assert any("defensive" in rec.lower() or "hedg" in rec.lower() for rec in recommendations)


def test_generate_recommendations_high_volatility(sample_market_data):
    """Test generate_recommendations with high volatility markets."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        # BTC-USD has volatility > 25
        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="neutral", news_categories={}
        )

        assert any("volatility" in rec.lower() or "stop" in rec.lower() for rec in recommendations)


def test_generate_recommendations_interest_rates(sample_market_data):
    """Test generate_recommendations with interest rate news."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        news_categories = {"interest_rates": [{"title": "Fed hikes rates"}]}

        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="neutral", news_categories=news_categories
        )

        assert any("central bank" in rec.lower() or "rate" in rec.lower() for rec in recommendations)


def test_generate_recommendations_earnings_season(sample_market_data):
    """Test generate_recommendations with earnings news."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        news_categories = {"earnings": [{"title": "Q4 earnings beat"}]}

        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="neutral", news_categories=news_categories
        )

        assert any("earnings" in rec.lower() for rec in recommendations)


def test_generate_recommendations_geopolitics(sample_market_data):
    """Test generate_recommendations with geopolitical news."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        news_categories = {"geopolitics": [{"title": "Trade war escalates"}]}

        recommendations = summarizer.generate_recommendations(
            market_data=sample_market_data, sentiment="neutral", news_categories=news_categories
        )

        assert any("geopolitical" in rec.lower() or "safe-haven" in rec.lower() for rec in recommendations)


def test_generate_recommendations_default(sample_market_data):
    """Test generate_recommendations with no specific triggers."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        # Neutral sentiment, low volatility, no special news
        low_vol_data = {
            "^GSPC": {
                "name": "S&P 500",
                "last_price": 4500.0,
                "change_percent": 0.1,
                "volatility": 10.0,
            }
        }

        recommendations = summarizer.generate_recommendations(
            market_data=low_vol_data, sentiment="neutral", news_categories={}
        )

        # Should return default recommendation
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


def test_generate_recommendations_max_five():
    """Test generate_recommendations returns max 5 recommendations."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        # Create conditions for many recommendations
        market_data = {
            f"TICKER{i}": {"name": f"Asset {i}", "last_price": 100.0, "change_percent": 1.0, "volatility": 30.0}
            for i in range(10)
        }

        news_categories = {
            "interest_rates": [{"title": "Fed"}],
            "earnings": [{"title": "Q4"}],
            "geopolitics": [{"title": "War"}],
        }

        recommendations = summarizer.generate_recommendations(
            market_data=market_data, sentiment="positive", news_categories=news_categories
        )

        assert len(recommendations) <= 5


# ============================================================================
# Test initialization and config
# ============================================================================


def test_init():
    """Test AISummarizer initialization."""
    with patch("src.core.summarizer.get_config", return_value=Mock()):
        summarizer = AISummarizer()

        assert summarizer is not None
        assert hasattr(summarizer, "config")
