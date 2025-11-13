"""Comprehensive tests for report_generator module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from src.core.report_generator import ReportGenerator


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    config = Mock()
    config.report_output_dir = Path("/tmp/reports")
    config.report_formats = ["markdown"]
    config.report_include_charts = False
    config.report_chart_style = "default"
    config.timezone = "UTC"
    return config


@pytest.fixture
def sample_news_articles():
    """Sample news articles for testing."""
    return [
        {
            "title": "Stock Market Surges",
            "source": "Financial Times",
            "sentiment": "positive",
            "summary": "Markets reached new highs today.",
            "description": "Detailed description",
            "url": "https://example.com/article1",
        },
        {
            "title": "Economic Concerns",
            "source": "WSJ",
            "sentiment": "negative",
            "summary": "Recession fears grow.",
            "description": "Economic analysis",
            "url": "https://example.com/article2",
        },
        {
            "title": "Neutral News",
            "source": "Reuters",
            "sentiment": "neutral",
            "summary": "Markets hold steady.",
            "url": "https://example.com/article3",
        },
    ]


@pytest.fixture
def sample_market_snapshots():
    """Sample market snapshots for testing."""
    return {
        "AAPL": {
            "name": "Apple Inc.",
            "last_price": 175.50,
            "change": 2.50,
            "change_percent": 1.45,
            "trend": "bullish",
            "volatility": 12.5,
        },
        "MSFT": {
            "name": "Microsoft",
            "last_price": 380.25,
            "change": -1.25,
            "change_percent": -0.33,
            "trend": "bearish",
            "volatility": 18.7,
        },
        "GOOGL": {
            "name": "Alphabet",
            "last_price": 140.00,
            "change": 0.0,
            "change_percent": 0.0,
            "trend": "neutral",
            "volatility": 15.2,
        },
    }


@pytest.fixture
def sample_sentiment_data():
    """Sample sentiment data for testing."""
    return {
        "overall_sentiment": "positive",
        "overall_score": 0.65,
        "distribution": {"positive": 5, "negative": 2, "neutral": 3},
    }


def test_init_default_style():
    """Test ReportGenerator initialization with default style."""
    with patch("src.core.report_generator.get_config") as mock_get_config:
        mock_cfg = Mock()
        mock_cfg.report_output_dir = Path("/tmp")
        mock_cfg.report_chart_style = "default"
        mock_get_config.return_value = mock_cfg

        with patch("src.core.report_generator.plt.style.use") as mock_style_use:
            generator = ReportGenerator()

            assert generator.config == mock_cfg
            assert generator.report_dir == Path("/tmp")
            mock_style_use.assert_called_once_with("default")


def test_init_seaborn_style():
    """Test ReportGenerator initialization with seaborn style."""
    with patch("src.core.report_generator.get_config") as mock_get_config:
        mock_cfg = Mock()
        mock_cfg.report_output_dir = Path("/tmp")
        mock_cfg.report_chart_style = "seaborn"
        mock_get_config.return_value = mock_cfg

        with patch("src.core.report_generator.sns.set_theme") as mock_set_theme:
            generator = ReportGenerator()

            assert generator.config == mock_cfg
            mock_set_theme.assert_called_once_with(style="darkgrid")


def test_generate_report_markdown_only(
    mock_config, sample_news_articles, sample_market_snapshots, sample_sentiment_data
):
    """Test generate_report with markdown format only."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_date = datetime(2025, 1, 15, 12, 0, 0)

        with (
            patch.object(
                generator, "_generate_markdown", return_value="# Test Report"
            ) as mock_gen_md,
            patch.object(
                generator, "_save_markdown", return_value=Path("/tmp/test.md")
            ) as mock_save_md,
        ):
            result = generator.generate_report(
                news_articles=sample_news_articles,
                market_snapshots=sample_market_snapshots,
                sentiment_data=sample_sentiment_data,
                ai_insights="Test insights",
                recommendations=["Rec 1", "Rec 2"],
                report_date=mock_date,
            )

            assert result == {"markdown": Path("/tmp/test.md")}
            mock_gen_md.assert_called_once()
            mock_save_md.assert_called_once_with("# Test Report", "zenmarket_report_2025-01-15")


def test_generate_report_all_formats(
    mock_config, sample_news_articles, sample_market_snapshots, sample_sentiment_data
):
    """Test generate_report with all formats."""
    mock_config.report_formats = ["markdown", "html", "pdf"]

    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        with (
            patch.object(generator, "_generate_markdown", return_value="# Test"),
            patch.object(generator, "_save_markdown", return_value=Path("/tmp/test.md")),
            patch.object(generator, "_save_html", return_value=Path("/tmp/test.html")),
            patch.object(generator, "_save_pdf", return_value=Path("/tmp/test.pdf")),
        ):
            result = generator.generate_report(
                news_articles=sample_news_articles,
                market_snapshots=sample_market_snapshots,
                sentiment_data=sample_sentiment_data,
                ai_insights="Test",
                recommendations=[],
            )

            assert "markdown" in result
            assert "html" in result
            assert "pdf" in result


def test_generate_report_with_charts(
    mock_config, sample_news_articles, sample_market_snapshots, sample_sentiment_data
):
    """Test generate_report with charts enabled."""
    mock_config.report_include_charts = True

    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        chart_files = {"performance": Path("/tmp/perf.png")}

        with (
            patch.object(generator, "_generate_markdown", return_value="# Test"),
            patch.object(generator, "_save_markdown", return_value=Path("/tmp/test.md")),
            patch.object(generator, "_generate_charts", return_value=chart_files) as mock_charts,
        ):
            result = generator.generate_report(
                news_articles=sample_news_articles,
                market_snapshots=sample_market_snapshots,
                sentiment_data=sample_sentiment_data,
                ai_insights="Test",
                recommendations=[],
            )

            mock_charts.assert_called_once()
            assert "markdown" in result


def test_generate_report_uses_default_date(
    mock_config, sample_news_articles, sample_market_snapshots, sample_sentiment_data
):
    """Test generate_report uses current date when not provided."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_now = datetime(2025, 1, 15, 10, 30)

        with (
            patch("src.utils.date_utils.now", return_value=mock_now),
            patch.object(generator, "_generate_markdown", return_value="# Test"),
            patch.object(generator, "_save_markdown", return_value=Path("/tmp/test.md")),
        ):
            result = generator.generate_report(
                news_articles=sample_news_articles,
                market_snapshots=sample_market_snapshots,
                sentiment_data=sample_sentiment_data,
                ai_insights="Test",
                recommendations=[],
                report_date=None,
            )

            assert result == {"markdown": Path("/tmp/test.md")}


def test_generate_markdown_content(
    mock_config, sample_news_articles, sample_market_snapshots, sample_sentiment_data
):
    """Test _generate_markdown creates proper content."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_date = datetime(2025, 1, 15, 12, 0)

        with patch("src.core.report_generator.format_friendly_date", return_value="Jan 15, 2025"):
            content = generator._generate_markdown(
                news_articles=sample_news_articles,
                market_snapshots=sample_market_snapshots,
                sentiment_data=sample_sentiment_data,
                ai_insights="Market looks strong today.",
                recommendations=["Watch inflation", "Monitor tech stocks"],
                report_date=mock_date,
            )

            # Check structure
            assert "# ZenMarket AI" in content
            assert "Jan 15, 2025" in content
            assert "Market looks strong today" in content
            assert "POSITIVE" in content
            assert "0.65" in content

            # Check news articles (top 7, but we only have 3)
            assert "Stock Market Surges" in content
            assert "Economic Concerns" in content
            assert "Neutral News" in content

            # Check market table
            assert "Apple Inc." in content
            assert "175.50" in content
            assert "Microsoft" in content
            assert "380.25" in content

            # Check sentiment distribution
            assert "positive" in content.lower()
            assert "negative" in content.lower()
            assert "neutral" in content.lower()

            # Check recommendations
            assert "Watch inflation" in content
            assert "Monitor tech stocks" in content

            # Check disclaimer
            assert "Disclaimer" in content
            assert "ZenMarket AI" in content


def test_generate_markdown_handles_missing_fields(mock_config):
    """Test _generate_markdown handles missing optional fields."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        # Articles with missing fields
        articles = [{"title": "Title Only"}]
        snapshots = {"TEST": {"name": "Test"}}
        sentiment = {}

        with patch("src.core.report_generator.format_friendly_date", return_value="Jan 15, 2025"):
            content = generator._generate_markdown(
                news_articles=articles,
                market_snapshots=snapshots,
                sentiment_data=sentiment,
                ai_insights="Test",
                recommendations=[],
                report_date=datetime.now(),
            )

            assert "Title Only" in content
            assert "Unknown" in content  # Default source
            assert "neutral" in content.lower()  # Default sentiment


def test_generate_markdown_empty_sentiment_distribution(mock_config):
    """Test _generate_markdown with empty sentiment distribution."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        sentiment = {"overall_sentiment": "neutral", "overall_score": 0.5, "distribution": {}}

        with patch("src.core.report_generator.format_friendly_date", return_value="Jan 15"):
            content = generator._generate_markdown(
                news_articles=[],
                market_snapshots={},
                sentiment_data=sentiment,
                ai_insights="Test",
                recommendations=[],
                report_date=datetime.now(),
            )

            assert "NEUTRAL" in content


def test_save_markdown(mock_config):
    """Test _save_markdown writes file correctly."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        m_open = mock_open()

        with patch("builtins.open", m_open):
            result = generator._save_markdown("# Test Content", "report_2025-01-15")

            assert result == Path("/tmp/reports/report_2025-01-15.md")
            m_open.assert_called_once_with(
                Path("/tmp/reports/report_2025-01-15.md"), "w", encoding="utf-8"
            )
            m_open().write.assert_called_once_with("# Test Content")


def test_save_html_success(mock_config):
    """Test _save_html successfully converts and saves."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_markdown2 = Mock()
        mock_markdown2.markdown.return_value = "<h1>Test</h1>"

        m_open = mock_open()

        with (
            patch.dict("sys.modules", {"markdown2": mock_markdown2}),
            patch("builtins.open", m_open),
        ):
            result = generator._save_html("# Test", "report_2025", {})

            assert result == Path("/tmp/reports/report_2025.html")
            mock_markdown2.markdown.assert_called_once()

            # Check HTML was written
            written_content = "".join(call.args[0] for call in m_open().write.call_args_list)
            assert "<!DOCTYPE html>" in written_content
            assert "<h1>Test</h1>" in written_content


def test_save_html_import_error(mock_config):
    """Test _save_html handles markdown2 ImportError."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        # Mock the import to raise ImportError
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "markdown2":
                raise ImportError("markdown2 not installed")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = generator._save_html("# Test", "report", {})

            assert result is None


def test_save_html_exception(mock_config):
    """Test _save_html handles general exceptions."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_markdown2 = Mock()
        mock_markdown2.markdown.side_effect = Exception("Conversion error")

        with patch.dict("sys.modules", {"markdown2": mock_markdown2}):
            result = generator._save_html("# Test", "report", {})

            assert result is None


def test_save_pdf_success(mock_config):
    """Test _save_pdf successfully generates PDF."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_markdown2 = Mock()
        mock_markdown2.markdown.return_value = "<h1>Test</h1>"

        mock_weasy = Mock()
        mock_html_obj = Mock()
        mock_weasy.HTML.return_value = mock_html_obj

        with patch.dict("sys.modules", {"markdown2": mock_markdown2, "weasyprint": mock_weasy}):
            result = generator._save_pdf("# Test", "report_2025", {})

            assert result == Path("/tmp/reports/report_2025.pdf")
            mock_weasy.HTML.assert_called_once()
            mock_html_obj.write_pdf.assert_called_once_with(Path("/tmp/reports/report_2025.pdf"))


def test_save_pdf_import_error(mock_config):
    """Test _save_pdf handles ImportError."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        # Mock the import to raise ImportError
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ("markdown2", "weasyprint"):
                raise ImportError(f"{name} not installed")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = generator._save_pdf("# Test", "report", {})

            assert result is None


def test_save_pdf_exception(mock_config):
    """Test _save_pdf handles conversion exceptions."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_markdown2 = Mock()
        mock_markdown2.markdown.side_effect = Exception("Conversion error")

        with patch.dict("sys.modules", {"markdown2": mock_markdown2}):
            result = generator._save_pdf("# Test", "report", {})

            assert result is None


def test_generate_charts(mock_config, sample_market_snapshots):
    """Test _generate_charts creates both charts."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        perf_path = Path("/tmp/perf.png")
        vol_path = Path("/tmp/vol.png")

        with (
            patch.object(generator, "_create_performance_chart", return_value=perf_path),
            patch.object(generator, "_create_volatility_chart", return_value=vol_path),
        ):
            result = generator._generate_charts(sample_market_snapshots, "report_2025")

            assert result == {"performance": perf_path, "volatility": vol_path}


def test_generate_charts_handles_errors(mock_config, sample_market_snapshots):
    """Test _generate_charts handles exceptions gracefully."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        with patch.object(
            generator, "_create_performance_chart", side_effect=Exception("Chart error")
        ):
            result = generator._generate_charts(sample_market_snapshots, "report")

            assert result == {}


def test_create_performance_chart(mock_config, sample_market_snapshots):
    """Test _create_performance_chart creates chart correctly."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_fig = Mock()
        mock_ax = Mock()
        mock_bars = [Mock(), Mock(), Mock()]
        mock_ax.barh.return_value = mock_bars

        with (
            patch("src.core.report_generator.plt.subplots", return_value=(mock_fig, mock_ax)),
            patch("src.core.report_generator.plt.tight_layout"),
            patch("src.core.report_generator.plt.savefig") as mock_savefig,
            patch("src.core.report_generator.plt.close") as mock_close,
        ):
            result = generator._create_performance_chart(sample_market_snapshots, "report_2025")

            assert result == Path("/tmp/reports/report_2025_performance.png")
            mock_ax.barh.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()


def test_create_performance_chart_handles_error(mock_config, sample_market_snapshots):
    """Test _create_performance_chart handles exceptions."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        with (
            patch("src.core.report_generator.plt.subplots", side_effect=Exception("Plot error")),
            patch("src.core.report_generator.plt.close") as mock_close,
        ):
            result = generator._create_performance_chart(sample_market_snapshots, "report")

            assert result is None
            mock_close.assert_called_once()


def test_create_volatility_chart(mock_config, sample_market_snapshots):
    """Test _create_volatility_chart creates chart correctly."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        mock_fig = Mock()
        mock_ax = Mock()
        mock_bars = [Mock(), Mock(), Mock()]
        mock_ax.bar.return_value = mock_bars

        # Mock bar dimensions
        for bar, vol in zip(mock_bars, [12.5, 18.7, 15.2]):
            bar.get_height.return_value = vol
            bar.get_x.return_value = 0
            bar.get_width.return_value = 1

        with (
            patch("src.core.report_generator.plt.subplots", return_value=(mock_fig, mock_ax)),
            patch("src.core.report_generator.plt.xticks"),
            patch("src.core.report_generator.plt.tight_layout"),
            patch("src.core.report_generator.plt.savefig") as mock_savefig,
            patch("src.core.report_generator.plt.close") as mock_close,
        ):
            result = generator._create_volatility_chart(sample_market_snapshots, "report_2025")

            assert result == Path("/tmp/reports/report_2025_volatility.png")
            mock_ax.bar.assert_called_once()
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()


def test_create_volatility_chart_empty_data(mock_config):
    """Test _create_volatility_chart with no volatility data."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        # Market snapshots without volatility
        snapshots = {"TEST": {"name": "Test", "volatility": None}}

        result = generator._create_volatility_chart(snapshots, "report")

        assert result is None


def test_create_volatility_chart_handles_error(mock_config, sample_market_snapshots):
    """Test _create_volatility_chart handles exceptions."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        with (
            patch("src.core.report_generator.plt.subplots", side_effect=Exception("Plot error")),
            patch("src.core.report_generator.plt.close") as mock_close,
        ):
            result = generator._create_volatility_chart(sample_market_snapshots, "report")

            assert result is None
            mock_close.assert_called_once()


def test_get_sentiment_emoji():
    """Test _get_sentiment_emoji returns correct emojis."""
    with patch("src.core.report_generator.get_config") as mock_get_config:
        mock_cfg = Mock()
        mock_cfg.report_output_dir = Path("/tmp")
        mock_cfg.report_chart_style = "default"
        mock_get_config.return_value = mock_cfg

        generator = ReportGenerator()

        assert generator._get_sentiment_emoji("positive") == "🔺"
        assert generator._get_sentiment_emoji("POSITIVE") == "🔺"
        assert generator._get_sentiment_emoji("negative") == "🔻"
        assert generator._get_sentiment_emoji("NEGATIVE") == "🔻"
        assert generator._get_sentiment_emoji("neutral") == "➖"
        assert generator._get_sentiment_emoji("unknown") == "➖"
        assert generator._get_sentiment_emoji("anything") == "➖"


def test_get_trend_emoji():
    """Test _get_trend_emoji returns correct emojis."""
    with patch("src.core.report_generator.get_config") as mock_get_config:
        mock_cfg = Mock()
        mock_cfg.report_output_dir = Path("/tmp")
        mock_cfg.report_chart_style = "default"
        mock_get_config.return_value = mock_cfg

        generator = ReportGenerator()

        assert generator._get_trend_emoji("bullish") == "🔼"
        assert generator._get_trend_emoji("BULLISH") == "🔼"
        assert generator._get_trend_emoji("bearish") == "🔽"
        assert generator._get_trend_emoji("BEARISH") == "🔽"
        assert generator._get_trend_emoji("neutral") == "➡️"
        assert generator._get_trend_emoji("unknown") == "➡️"


def test_generate_markdown_more_than_7_articles(mock_config):
    """Test _generate_markdown limits news to top 7 articles."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        # Create 10 articles
        articles = [
            {
                "title": f"Article {i}",
                "source": "Test",
                "sentiment": "neutral",
                "summary": "Summary",
                "url": f"https://example.com/{i}",
            }
            for i in range(10)
        ]

        with patch("src.core.report_generator.format_friendly_date", return_value="Jan 15"):
            content = generator._generate_markdown(
                news_articles=articles,
                market_snapshots={},
                sentiment_data={"distribution": {}},
                ai_insights="Test",
                recommendations=[],
                report_date=datetime.now(),
            )

            # Should only include first 7
            assert "Article 0" in content
            assert "Article 6" in content
            assert "Article 7" not in content
            assert "Article 9" not in content


def test_generate_markdown_change_emoji_logic(mock_config, sample_market_snapshots):
    """Test _generate_markdown uses correct change emojis."""
    with patch("src.core.report_generator.get_config", return_value=mock_config):
        generator = ReportGenerator()

        with patch("src.core.report_generator.format_friendly_date", return_value="Jan 15"):
            content = generator._generate_markdown(
                news_articles=[],
                market_snapshots=sample_market_snapshots,
                sentiment_data={"distribution": {}},
                ai_insights="Test",
                recommendations=[],
                report_date=datetime.now(),
            )

            # AAPL has positive change -> 📈
            assert "📈" in content
            # MSFT has negative change -> 📉
            assert "📉" in content
            # GOOGL has zero change -> ➖
            assert "➖" in content
