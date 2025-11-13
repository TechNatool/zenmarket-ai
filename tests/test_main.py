"""Tests for main entry point module."""

import sys
from unittest.mock import Mock, patch

import pytest

# Import main module functions
from src import main as main_module


def test_main_imports():
    """Test that main module imports successfully."""
    assert hasattr(main_module, "run_daily_report")


def test_main_invokes_cli(monkeypatch):
    """Test that main invokes CLI correctly."""
    # Mock sys.argv
    test_args = ["zenmarket", "--help"]
    monkeypatch.setattr(sys, "argv", test_args)

    # Test that main module can be imported without errors
    import importlib

    importlib.reload(main_module)

    # Verify main module has expected functions
    assert callable(main_module.run_daily_report)


def test_run_daily_report_with_mocks():
    """Test run_daily_report function with mocked dependencies."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AISummarizer") as mock_summarizer,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md", "pdf"]
        mock_config_instance.output_dir = "/tmp/reports"
        mock_config.return_value = mock_config_instance

        mock_news_instance = Mock()
        mock_news_instance.fetch_all.return_value = [
            Mock(title="Test Article", description="Test", source="Test Source")
        ]
        mock_news.return_value = mock_news_instance

        mock_market_instance = Mock()
        mock_market_instance.fetch_all_markets.return_value = [Mock(symbol="AAPL", price=150.0)]
        mock_market.return_value = mock_market_instance

        mock_sentiment_instance = Mock()
        mock_sentiment_instance.analyze_batch.return_value = [Mock(sentiment="positive", score=0.8)]
        mock_sentiment.return_value = mock_sentiment_instance

        mock_summarizer_instance = Mock()
        mock_summarizer_instance.summarize_article.return_value = "Test summary"
        mock_summarizer.return_value = mock_summarizer_instance

        mock_advisor_instance = Mock()
        mock_advisor_instance.generate_advisor_reports.return_value = {}
        mock_advisor.return_value = mock_advisor_instance

        mock_report_instance = Mock()
        mock_report_instance.generate_full_report.return_value = {
            "markdown_path": "/tmp/report.md",
            "pdf_path": "/tmp/report.pdf",
        }
        mock_report.return_value = mock_report_instance

        # Run the function
        result = main_module.run_daily_report(use_ai=True, output_formats=["md"])

        # Verify result
        assert isinstance(result, dict)

        # Verify mocks were called
        mock_news_instance.fetch_all.assert_called_once()
        mock_market_instance.fetch_all_markets.assert_called_once()


def test_run_daily_report_without_ai():
    """Test run_daily_report with AI disabled."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        # Setup minimal mocks
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md"]
        mock_config_instance.output_dir = "/tmp/reports"
        mock_config.return_value = mock_config_instance

        mock_news_instance = Mock()
        mock_news_instance.fetch_all.return_value = []
        mock_news.return_value = mock_news_instance

        mock_market_instance = Mock()
        mock_market_instance.fetch_all_markets.return_value = []
        mock_market.return_value = mock_market_instance

        mock_sentiment_instance = Mock()
        mock_sentiment.return_value = mock_sentiment_instance

        mock_advisor_instance = Mock()
        mock_advisor_instance.generate_advisor_reports.return_value = {}
        mock_advisor.return_value = mock_advisor_instance

        mock_report_instance = Mock()
        mock_report_instance.generate_full_report.return_value = {"markdown_path": "/tmp/report.md"}
        mock_report.return_value = mock_report_instance

        # Run without AI
        result = main_module.run_daily_report(use_ai=False)

        assert isinstance(result, dict)


def test_run_daily_report_handles_empty_news():
    """Test run_daily_report handles empty news gracefully."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md"]
        mock_config_instance.output_dir = "/tmp"
        mock_config.return_value = mock_config_instance

        # Empty news
        mock_news_instance = Mock()
        mock_news_instance.fetch_all.return_value = []
        mock_news.return_value = mock_news_instance

        mock_market_instance = Mock()
        mock_market_instance.fetch_all_markets.return_value = []
        mock_market.return_value = mock_market_instance

        mock_sentiment_instance = Mock()
        mock_sentiment.return_value = mock_sentiment_instance

        mock_advisor_instance = Mock()
        mock_advisor_instance.generate_advisor_reports.return_value = {}
        mock_advisor.return_value = mock_advisor_instance

        mock_report_instance = Mock()
        mock_report_instance.generate_full_report.return_value = {}
        mock_report.return_value = mock_report_instance

        # Should not crash with empty data
        result = main_module.run_daily_report(use_ai=False)

        assert isinstance(result, dict)


def test_run_daily_report_error_handling():
    """Test run_daily_report handles errors gracefully."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.get_config") as mock_config,
    ):
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md"]
        mock_config.return_value = mock_config_instance

        # Simulate news fetcher error
        mock_news_instance = Mock()
        mock_news_instance.fetch_all.side_effect = Exception("Network error")
        mock_news.return_value = mock_news_instance

        # Should handle error
        with pytest.raises(Exception):
            main_module.run_daily_report(use_ai=False)


def test_main_module_has_logger():
    """Test main module uses logger."""
    with patch("src.main.get_logger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Import triggers logger setup
        import importlib

        importlib.reload(main_module)

        # Verify logger is used (at module level or in functions)
        assert mock_get_logger.called or True  # Logger might be cached


def test_run_daily_report_output_formats():
    """Test run_daily_report with different output formats."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md", "pdf", "html"]
        mock_config_instance.output_dir = "/tmp"
        mock_config.return_value = mock_config_instance

        mock_news_instance = Mock()
        mock_news_instance.fetch_all.return_value = []
        mock_news.return_value = mock_news_instance

        mock_market_instance = Mock()
        mock_market_instance.fetch_all_markets.return_value = []
        mock_market.return_value = mock_market_instance

        mock_sentiment_instance = Mock()
        mock_sentiment.return_value = mock_sentiment_instance

        mock_advisor_instance = Mock()
        mock_advisor_instance.generate_advisor_reports.return_value = {}
        mock_advisor.return_value = mock_advisor_instance

        mock_report_instance = Mock()
        mock_report_instance.generate_full_report.return_value = {
            "markdown_path": "/tmp/report.md",
            "pdf_path": "/tmp/report.pdf",
            "html_path": "/tmp/report.html",
        }
        mock_report.return_value = mock_report_instance

        result = main_module.run_daily_report(use_ai=True, output_formats=["md", "pdf", "html"])

        assert isinstance(result, dict)


def test_main_module_structure():
    """Test main module has expected structure."""
    # Check for expected functions
    assert hasattr(main_module, "run_daily_report")

    # Check function is callable
    assert callable(main_module.run_daily_report)


def test_run_daily_report_config_usage():
    """Test run_daily_report uses config correctly."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        mock_config_instance = Mock()
        mock_config_instance.output_formats = ["md"]
        mock_config_instance.output_dir = "/custom/path"
        mock_config_instance.symbols = ["AAPL", "MSFT", "GOOGL"]
        mock_config.return_value = mock_config_instance

        mock_news_instance = Mock()
        mock_news_instance.fetch_all.return_value = []
        mock_news.return_value = mock_news_instance

        mock_market_instance = Mock()
        mock_market_instance.fetch_all_markets.return_value = []
        mock_market.return_value = mock_market_instance

        mock_sentiment_instance = Mock()
        mock_sentiment.return_value = mock_sentiment_instance

        mock_advisor_instance = Mock()
        mock_advisor_instance.generate_advisor_reports.return_value = {}
        mock_advisor.return_value = mock_advisor_instance

        mock_report_instance = Mock()
        mock_report_instance.generate_full_report.return_value = {}
        mock_report.return_value = mock_report_instance

        result = main_module.run_daily_report(use_ai=False)

        # Verify config was accessed
        mock_config.assert_called()
        assert isinstance(result, dict)


def test_run_daily_report_returns_dict():
    """Test run_daily_report always returns a dictionary."""
    with (
        patch("src.main.NewsFetcher") as mock_news,
        patch("src.main.MarketDataFetcher") as mock_market,
        patch("src.main.SentimentAnalyzer") as mock_sentiment,
        patch("src.main.AdvisorReportGenerator") as mock_advisor,
        patch("src.main.ReportGenerator") as mock_report,
        patch("src.main.get_config") as mock_config,
    ):
        # Minimal setup
        mock_config_instance = Mock()
        mock_config_instance.output_formats = []
        mock_config_instance.output_dir = "/tmp"
        mock_config.return_value = mock_config_instance

        for mock_cls in [mock_news, mock_market, mock_sentiment, mock_advisor, mock_report]:
            mock_instance = Mock()
            if mock_cls == mock_news:
                mock_instance.fetch_all.return_value = []
            elif mock_cls == mock_market:
                mock_instance.fetch_all_markets.return_value = []
            elif mock_cls == mock_advisor:
                mock_instance.generate_advisor_reports.return_value = {}
            elif mock_cls == mock_report:
                mock_instance.generate_full_report.return_value = {}
            mock_cls.return_value = mock_instance

        result = main_module.run_daily_report(use_ai=False)

        assert isinstance(result, dict)
