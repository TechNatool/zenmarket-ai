"""Comprehensive tests for main.py to reach 90% coverage."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.core.market_data import MarketSnapshot
from src.core.news_fetcher import NewsArticle
from src.core.sentiment_analyzer import SentimentResult
from src.main import main, run_daily_report


@pytest.fixture
def mock_news_articles():
    """Create mock news articles."""
    return [
        NewsArticle(
            title="Stock Market Surges",
            description="Markets hit new highs today",
            source="Financial Times",
            url="https://example.com/news1",
            published_at=datetime(2024, 1, 15, 10, 0),
        ),
        NewsArticle(
            title="Tech Stocks Rally",
            description="Technology sector leads gains",
            source="WSJ",
            url="https://example.com/news2",
            published_at=datetime(2024, 1, 15, 11, 0),
        ),
    ]


@pytest.fixture
def mock_market_snapshots():
    """Create mock market snapshots."""
    return {
        "^GSPC": MarketSnapshot(
            ticker="^GSPC",
            name="S&P 500",
            last_price=4500.0,
            change=50.0,
            change_percent=1.12,
            volume=1000000,
            high=4510.0,
            low=4450.0,
            open_price=4455.0,
            timestamp=datetime(2024, 1, 15, 16, 0),
            volatility=15.5,
            trend="bullish",
        )
    }


@pytest.fixture
def mock_sentiment_results():
    """Create mock sentiment results."""
    return [
        SentimentResult(
            text="Stock Market Surges",
            sentiment="positive",
            score=0.8,
            confidence=0.9,
            method="lexicon",
        ),
        SentimentResult(
            text="Tech Stocks Rally",
            sentiment="positive",
            score=0.7,
            confidence=0.85,
            method="lexicon",
        ),
    ]


def test_run_daily_report_success_with_ai(
    mock_news_articles, mock_market_snapshots, mock_sentiment_results
):
    """Test successful run_daily_report with AI enabled."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.MarketDataFetcher") as MockMarketDataFetcher,
        patch("src.main.SentimentAnalyzer") as MockSentimentAnalyzer,
        patch("src.main.AISummarizer") as MockAISummarizer,
        patch("src.main.ReportGenerator") as MockReportGenerator,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.now") as mock_now,
    ):
        # Setup config
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_config.report_formats = ["markdown", "html"]
        mock_get_config.return_value = mock_config

        mock_now.return_value = datetime(2024, 1, 15, 12, 0)

        # Setup NewsFetcher
        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.return_value = mock_news_articles
        MockNewsFetcher.return_value = mock_news_fetcher

        # Setup MarketDataFetcher
        mock_market_fetcher = Mock()
        mock_market_fetcher.fetch_all_markets.return_value = mock_market_snapshots
        MockMarketDataFetcher.return_value = mock_market_fetcher

        # Setup SentimentAnalyzer
        mock_sentiment_analyzer = Mock()
        mock_sentiment_analyzer.analyze_batch.return_value = mock_sentiment_results
        mock_sentiment_analyzer.get_overall_sentiment.return_value = ("positive", 0.75)
        mock_sentiment_analyzer.get_sentiment_distribution.return_value = {
            "positive": 2,
            "negative": 0,
            "neutral": 0,
        }
        MockSentimentAnalyzer.return_value = mock_sentiment_analyzer

        # Setup AISummarizer
        mock_summarizer = Mock()
        mock_summarizer.summarize_article.return_value = "AI generated summary"
        mock_summarizer.generate_market_insights.return_value = "Bullish market conditions"
        mock_summarizer.categorize_news.return_value = {"economy": 1, "technology": 1}
        mock_summarizer.generate_recommendations.return_value = ["Consider long positions"]
        MockAISummarizer.return_value = mock_summarizer

        # Setup ReportGenerator
        mock_report_gen = Mock()
        mock_report_gen.generate_report.return_value = {
            "markdown": "/tmp/report.md",
            "html": "/tmp/report.html",
        }
        MockReportGenerator.return_value = mock_report_gen

        # Execute
        result = run_daily_report(use_ai=True, output_formats=None)

        # Verify
        assert result["success"] is True
        assert "output_files" in result
        assert "statistics" in result
        assert result["statistics"]["articles_fetched"] == 2
        assert result["statistics"]["markets_tracked"] == 1
        assert result["statistics"]["overall_sentiment"] == "positive"

        # Verify all components were called
        mock_news_fetcher.fetch_all.assert_called_once()
        mock_market_fetcher.fetch_all_markets.assert_called_once()
        mock_sentiment_analyzer.analyze_batch.assert_called_once()
        mock_summarizer.generate_market_insights.assert_called_once()
        mock_report_gen.generate_report.assert_called_once()


def test_run_daily_report_without_ai(
    mock_news_articles, mock_market_snapshots, mock_sentiment_results
):
    """Test run_daily_report with AI disabled (fallback mode)."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.MarketDataFetcher") as MockMarketDataFetcher,
        patch("src.main.SentimentAnalyzer") as MockSentimentAnalyzer,
        patch("src.main.AISummarizer") as MockAISummarizer,
        patch("src.main.ReportGenerator") as MockReportGenerator,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.now") as mock_now,
    ):
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_now.return_value = datetime(2024, 1, 15, 12, 0)

        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.return_value = mock_news_articles
        MockNewsFetcher.return_value = mock_news_fetcher

        mock_market_fetcher = Mock()
        mock_market_fetcher.fetch_all_markets.return_value = mock_market_snapshots
        MockMarketDataFetcher.return_value = mock_market_fetcher

        mock_sentiment_analyzer = Mock()
        mock_sentiment_analyzer.analyze_batch.return_value = mock_sentiment_results
        mock_sentiment_analyzer.get_overall_sentiment.return_value = ("positive", 0.75)
        mock_sentiment_analyzer.get_sentiment_distribution.return_value = {
            "positive": 2,
            "negative": 0,
            "neutral": 0,
        }
        MockSentimentAnalyzer.return_value = mock_sentiment_analyzer

        mock_summarizer = Mock()
        mock_summarizer._generate_fallback_insights.return_value = "Fallback insights"
        mock_summarizer.categorize_news.return_value = {"economy": 1}
        mock_summarizer.generate_recommendations.return_value = ["Recommendation 1"]
        MockAISummarizer.return_value = mock_summarizer

        mock_report_gen = Mock()
        mock_report_gen.generate_report.return_value = {"markdown": "/tmp/report.md"}
        MockReportGenerator.return_value = mock_report_gen

        result = run_daily_report(use_ai=False)

        assert result["success"] is True
        # Should NOT call AI summarization methods
        mock_summarizer.summarize_article.assert_not_called()
        mock_summarizer.generate_market_insights.assert_not_called()
        # Should use fallback
        mock_summarizer._generate_fallback_insights.assert_called_once()


def test_run_daily_report_no_articles(mock_market_snapshots, mock_sentiment_results):
    """Test run_daily_report handles empty news gracefully."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.MarketDataFetcher") as MockMarketDataFetcher,
        patch("src.main.SentimentAnalyzer") as MockSentimentAnalyzer,
        patch("src.main.AISummarizer") as MockAISummarizer,
        patch("src.main.ReportGenerator") as MockReportGenerator,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.now") as mock_now,
    ):
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_now.return_value = datetime(2024, 1, 15, 12, 0)

        # No articles fetched
        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.return_value = []
        MockNewsFetcher.return_value = mock_news_fetcher

        mock_market_fetcher = Mock()
        mock_market_fetcher.fetch_all_markets.return_value = mock_market_snapshots
        MockMarketDataFetcher.return_value = mock_market_fetcher

        mock_sentiment_analyzer = Mock()
        mock_sentiment_analyzer.analyze_batch.return_value = []
        mock_sentiment_analyzer.get_overall_sentiment.return_value = ("neutral", 0.0)
        mock_sentiment_analyzer.get_sentiment_distribution.return_value = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
        }
        MockSentimentAnalyzer.return_value = mock_sentiment_analyzer

        mock_summarizer = Mock()
        mock_summarizer._generate_fallback_insights.return_value = "No news available"
        mock_summarizer.categorize_news.return_value = {}
        mock_summarizer.generate_recommendations.return_value = []
        MockAISummarizer.return_value = mock_summarizer

        mock_report_gen = Mock()
        mock_report_gen.generate_report.return_value = {"markdown": "/tmp/report.md"}
        MockReportGenerator.return_value = mock_report_gen

        result = run_daily_report(use_ai=False)

        assert result["success"] is True
        assert result["statistics"]["articles_fetched"] == 0


def test_run_daily_report_ai_summary_fails(
    mock_news_articles, mock_market_snapshots, mock_sentiment_results
):
    """Test run_daily_report handles AI summary failures gracefully."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.MarketDataFetcher") as MockMarketDataFetcher,
        patch("src.main.SentimentAnalyzer") as MockSentimentAnalyzer,
        patch("src.main.AISummarizer") as MockAISummarizer,
        patch("src.main.ReportGenerator") as MockReportGenerator,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.now") as mock_now,
    ):
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_now.return_value = datetime(2024, 1, 15, 12, 0)

        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.return_value = mock_news_articles
        MockNewsFetcher.return_value = mock_news_fetcher

        mock_market_fetcher = Mock()
        mock_market_fetcher.fetch_all_markets.return_value = mock_market_snapshots
        MockMarketDataFetcher.return_value = mock_market_fetcher

        mock_sentiment_analyzer = Mock()
        mock_sentiment_analyzer.analyze_batch.return_value = mock_sentiment_results
        mock_sentiment_analyzer.get_overall_sentiment.return_value = ("positive", 0.75)
        mock_sentiment_analyzer.get_sentiment_distribution.return_value = {
            "positive": 2,
            "negative": 0,
            "neutral": 0,
        }
        MockSentimentAnalyzer.return_value = mock_sentiment_analyzer

        # AI summarizer fails
        mock_summarizer = Mock()
        mock_summarizer.summarize_article.side_effect = Exception("AI service unavailable")
        mock_summarizer.generate_market_insights.side_effect = Exception("AI service unavailable")
        mock_summarizer._generate_fallback_insights.return_value = "Fallback insights"
        mock_summarizer.categorize_news.return_value = {}
        mock_summarizer.generate_recommendations.return_value = []
        MockAISummarizer.return_value = mock_summarizer

        mock_report_gen = Mock()
        mock_report_gen.generate_report.return_value = {"markdown": "/tmp/report.md"}
        MockReportGenerator.return_value = mock_report_gen

        # Should handle AI failures gracefully and use fallback
        result = run_daily_report(use_ai=True)

        assert result["success"] is True
        # Should fallback to description truncation for articles
        # Articles should have summary attribute set to truncated description


def test_run_daily_report_critical_error():
    """Test run_daily_report handles critical errors."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.get_config") as mock_get_config,
    ):
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_get_config.return_value = mock_config

        # Simulate critical error in news fetcher
        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.side_effect = Exception("Network error")
        MockNewsFetcher.return_value = mock_news_fetcher

        result = run_daily_report(use_ai=False)

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


def test_run_daily_report_custom_output_formats(
    mock_news_articles, mock_market_snapshots, mock_sentiment_results
):
    """Test run_daily_report with custom output formats."""
    with (
        patch("src.main.NewsFetcher") as MockNewsFetcher,
        patch("src.main.MarketDataFetcher") as MockMarketDataFetcher,
        patch("src.main.SentimentAnalyzer") as MockSentimentAnalyzer,
        patch("src.main.AISummarizer") as MockAISummarizer,
        patch("src.main.ReportGenerator") as MockReportGenerator,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.now") as mock_now,
    ):
        mock_config = Mock()
        mock_config.timezone = "UTC"
        mock_config.report_formats = ["markdown", "html", "pdf"]  # Default formats
        mock_get_config.return_value = mock_config

        mock_now.return_value = datetime(2024, 1, 15, 12, 0)

        mock_news_fetcher = Mock()
        mock_news_fetcher.fetch_all.return_value = mock_news_articles
        MockNewsFetcher.return_value = mock_news_fetcher

        mock_market_fetcher = Mock()
        mock_market_fetcher.fetch_all_markets.return_value = mock_market_snapshots
        MockMarketDataFetcher.return_value = mock_market_fetcher

        mock_sentiment_analyzer = Mock()
        mock_sentiment_analyzer.analyze_batch.return_value = mock_sentiment_results
        mock_sentiment_analyzer.get_overall_sentiment.return_value = ("positive", 0.75)
        mock_sentiment_analyzer.get_sentiment_distribution.return_value = {
            "positive": 2,
            "negative": 0,
            "neutral": 0,
        }
        MockSentimentAnalyzer.return_value = mock_sentiment_analyzer

        mock_summarizer = Mock()
        mock_summarizer._generate_fallback_insights.return_value = "Insights"
        mock_summarizer.categorize_news.return_value = {}
        mock_summarizer.generate_recommendations.return_value = []
        MockAISummarizer.return_value = mock_summarizer

        mock_report_gen = Mock()
        mock_report_gen.generate_report.return_value = {
            "pdf": "/tmp/report.pdf",
            "html": "/tmp/report.html",
        }
        MockReportGenerator.return_value = mock_report_gen

        # Test with custom formats (only pdf and html)
        result = run_daily_report(use_ai=False, output_formats=["pdf", "html"])

        assert result["success"] is True
        assert "output_files" in result

        # Verify that config.report_formats was temporarily overridden
        # but then restored
        assert mock_config.report_formats == ["markdown", "html", "pdf"]  # Should be restored


def test_main_cli_help():
    """Test main() CLI with --help (should exit gracefully)."""
    import sys

    with patch.object(sys, "argv", ["zenmarket", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        # --help exits with code 0
        assert exc_info.value.code == 0


def test_main_cli_invalid_log_level():
    """Test main() CLI with invalid log level."""
    import sys

    with patch.object(sys, "argv", ["zenmarket", "--log-level", "INVALID"]):
        with pytest.raises(SystemExit):
            main()


def test_main_cli_config_validation_fails():
    """Test main() CLI when config validation fails."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = ["Missing API key", "Invalid timezone"]
        mock_get_config.return_value = mock_config

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        # Should log validation errors
        assert mock_logger.error.called


def test_main_cli_daily_report_success():
    """Test main() CLI runs daily report successfully."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket", "--no-ai"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.run_daily_report") as mock_run_daily_report,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_run_daily_report.return_value = {
            "success": True,
            "output_files": {"markdown": "/tmp/report.md"},
            "statistics": {"articles_fetched": 5},
        }

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with success code 0
        assert exc_info.value.code == 0


def test_main_cli_daily_report_failure():
    """Test main() CLI handles report failure."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.run_daily_report") as mock_run_daily_report,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_run_daily_report.return_value = {
            "success": False,
            "error": "Database connection failed",
        }

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code 1
        assert exc_info.value.code == 1


def test_main_cli_trading_advisor():
    """Test main() CLI with --trading-advisor flag."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket", "--trading-advisor"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.run_daily_report") as mock_run_daily_report,
        patch("src.main.AdvisorReportGenerator") as MockAdvisorReportGenerator,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_run_daily_report.return_value = {"success": True, "output_files": {}}

        mock_advisor = Mock()
        mock_advisor.generate_full_report.return_value = {"success": True}
        MockAdvisorReportGenerator.return_value = mock_advisor

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should call both daily report and advisor report
        mock_run_daily_report.assert_called_once()
        mock_advisor.generate_full_report.assert_called_once()
        assert exc_info.value.code == 0


def test_main_cli_trading_only():
    """Test main() CLI with --trading-only flag."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket", "--trading-only"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.run_daily_report") as mock_run_daily_report,
        patch("src.main.AdvisorReportGenerator") as MockAdvisorReportGenerator,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_advisor = Mock()
        mock_advisor.generate_full_report.return_value = {"success": True}
        MockAdvisorReportGenerator.return_value = mock_advisor

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should NOT call daily report, only advisor
        mock_run_daily_report.assert_not_called()
        mock_advisor.generate_full_report.assert_called_once()
        assert exc_info.value.code == 0


def test_main_cli_format_options():
    """Test main() CLI with --format options."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket", "--format", "markdown", "pdf"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.run_daily_report") as mock_run_daily_report,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["html"]  # Default
        mock_get_config.return_value = mock_config

        mock_run_daily_report.return_value = {"success": True, "output_files": {}}

        with pytest.raises(SystemExit):
            main()

        # Should pass custom formats to run_daily_report
        mock_run_daily_report.assert_called_once_with(
            use_ai=True, output_formats=["markdown", "pdf"]
        )


def test_main_cli_no_charts():
    """Test main() CLI with --no-charts flag."""
    import sys

    with (
        patch.object(sys, "argv", ["zenmarket", "--trading-only", "--no-charts"]),
        patch("src.main.setup_logger") as mock_setup_logger,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.AdvisorReportGenerator") as MockAdvisorReportGenerator,
    ):
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_config = Mock()
        mock_config.validate.return_value = []
        mock_config.ai_provider = "openai"
        mock_config.report_formats = ["markdown"]
        mock_get_config.return_value = mock_config

        mock_advisor = Mock()
        mock_advisor.generate_full_report.return_value = {"success": True}
        MockAdvisorReportGenerator.return_value = mock_advisor

        with pytest.raises(SystemExit):
            main()

        # Should pass generate_charts=False
        mock_advisor.generate_full_report.assert_called_once_with(generate_charts=False)
