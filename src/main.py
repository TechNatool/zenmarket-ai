#!/usr/bin/env python3
"""
ZenMarket AI - Main Entry Point
Automated financial intelligence and market analysis system.
"""

import argparse
import sys

from .advisor.advisor_report import AdvisorReportGenerator
from .core.market_data import MarketDataFetcher
from .core.news_fetcher import NewsFetcher
from .core.report_generator import ReportGenerator
from .core.sentiment_analyzer import SentimentAnalyzer
from .core.summarizer import AISummarizer
from .utils.config_loader import get_config
from .utils.date_utils import now
from .utils.logger import get_logger, setup_logger


def run_daily_report(use_ai: bool = True, output_formats: list | None = None) -> dict:
    """
    Run the complete daily report generation pipeline.

    Args:
        use_ai: Whether to use AI for summaries and insights
        output_formats: List of output formats (default: from config)

    Returns:
        Dictionary with report paths and statistics
    """
    logger = get_logger(__name__)
    config = get_config()

    logger.info("=" * 70)
    logger.info("ZenMarket AI - Daily Financial Report Generation")
    logger.info("=" * 70)

    try:
        # === Step 1: Fetch News ===
        logger.info("Step 1/6: Fetching financial news...")
        news_fetcher = NewsFetcher()
        articles = news_fetcher.fetch_all(
            use_newsapi=True, use_rss=True, filter_relevant=True, deduplicate=True
        )

        if not articles:
            logger.warning("No news articles fetched. Report may be incomplete.")
            articles = []

        logger.info(f"✓ Fetched {len(articles)} relevant articles")

        # === Step 2: Fetch Market Data ===
        logger.info("Step 2/6: Fetching market data...")
        market_fetcher = MarketDataFetcher()
        market_snapshots = market_fetcher.fetch_all_markets()

        logger.info(f"✓ Fetched data for {len(market_snapshots)} markets")

        # === Step 3: Sentiment Analysis ===
        logger.info("Step 3/6: Analyzing sentiment...")
        sentiment_analyzer = SentimentAnalyzer()

        # Analyze top articles
        texts_to_analyze = [
            f"{article.title} {article.description}"
            for article in articles[:20]  # Limit to top 20 for speed
        ]

        sentiment_results = sentiment_analyzer.analyze_batch(texts_to_analyze, use_ai=False)

        # Attach sentiment to articles
        for i, article in enumerate(articles[:20]):
            if i < len(sentiment_results):
                article.sentiment = sentiment_results[i].sentiment

        # Overall sentiment
        overall_sentiment, overall_score = sentiment_analyzer.get_overall_sentiment(
            sentiment_results
        )
        sentiment_distribution = sentiment_analyzer.get_sentiment_distribution(sentiment_results)

        sentiment_data = {
            "overall_sentiment": overall_sentiment,
            "overall_score": overall_score,
            "distribution": sentiment_distribution,
        }

        logger.info(f"✓ Overall sentiment: {overall_sentiment.upper()} ({overall_score:.2f})")

        # === Step 4: Generate Summaries ===
        logger.info("Step 4/6: Generating summaries...")
        summarizer = AISummarizer()

        # Summarize top articles
        for article in articles[:7]:  # Top 7 for report
            if use_ai:
                try:
                    article.summary = summarizer.summarize_article(
                        article.title, article.description, max_words=50
                    )
                except Exception as e:
                    logger.warning(f"AI summary failed for article, using description: {e}")
                    article.summary = article.description[:200] + "..."
            else:
                article.summary = article.description[:200] + "..."

        logger.info("✓ Summaries generated")

        # === Step 5: Generate AI Insights ===
        logger.info("Step 5/6: Generating AI insights...")

        news_summaries = [
            article.summary for article in articles[:10] if hasattr(article, "summary")
        ]

        market_data_dict = {
            ticker: snapshot.to_dict() for ticker, snapshot in market_snapshots.items()
        }

        if use_ai:
            try:
                ai_insights = summarizer.generate_market_insights(
                    news_summaries, market_data_dict, overall_sentiment
                )
            except Exception as e:
                logger.warning(f"AI insights generation failed: {e}")
                ai_insights = summarizer._generate_fallback_insights(overall_sentiment)
        else:
            ai_insights = summarizer._generate_fallback_insights(overall_sentiment)

        logger.info("✓ AI insights generated")

        # === Step 6: Categorize News ===
        articles_dicts = [article.to_dict() for article in articles]
        news_categories = summarizer.categorize_news(articles_dicts)

        # === Step 7: Generate Recommendations ===
        recommendations = summarizer.generate_recommendations(
            market_data_dict, overall_sentiment, news_categories
        )

        logger.info(f"✓ Generated {len(recommendations)} recommendations")

        # === Step 8: Generate Report ===
        logger.info("Step 6/6: Generating report files...")
        report_generator = ReportGenerator()

        # Override formats if specified
        if output_formats:
            original_formats = config.report_formats
            config.report_formats = output_formats

        output_files = report_generator.generate_report(
            news_articles=articles_dicts[:7],
            market_snapshots=market_data_dict,
            sentiment_data=sentiment_data,
            ai_insights=ai_insights,
            recommendations=recommendations,
            report_date=now(config.timezone),
        )

        # Restore original formats
        if output_formats:
            config.report_formats = original_formats

        logger.info("✓ Report generation complete!")
        logger.info("=" * 70)

        # Print output files
        logger.info("Generated files:")
        for fmt, path in output_files.items():
            logger.info(f"  - {fmt.upper()}: {path}")

        logger.info("=" * 70)

        return {
            "success": True,
            "output_files": output_files,
            "statistics": {
                "articles_fetched": len(articles),
                "markets_tracked": len(market_snapshots),
                "overall_sentiment": overall_sentiment,
                "sentiment_score": overall_score,
            },
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def main() -> None:
    """Main entry point with CLI argument parsing."""

    parser = argparse.ArgumentParser(
        description="ZenMarket AI - Automated Financial Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                    # Generate daily report
  python -m src.main --no-ai            # Generate without AI (faster)
  python -m src.main --format markdown  # Generate only Markdown
  python -m src.main --format pdf html  # Generate PDF and HTML only
  python -m src.main --trading-advisor  # Generate trading advisor report too
  python -m src.main --trading-only     # Generate only trading advisor report
  python -m src.main --log-level DEBUG  # Enable debug logging
        """,
    )

    parser.add_argument(
        "--no-ai", action="store_true", help="Disable AI summarization (uses fallback methods)"
    )

    parser.add_argument(
        "--format",
        nargs="+",
        choices=["markdown", "html", "pdf"],
        help="Output formats (default: all configured formats)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--trading-advisor",
        action="store_true",
        help="Also generate trading advisor report with technical analysis",
    )

    parser.add_argument(
        "--trading-only",
        action="store_true",
        help="Generate only trading advisor report (skip news report)",
    )

    parser.add_argument(
        "--no-charts", action="store_true", help="Skip chart generation in trading advisor"
    )

    parser.add_argument("--version", action="version", version="ZenMarket AI v1.0.0")

    args = parser.parse_args()

    # Setup logging
    logger = setup_logger(level=args.log_level, console=True)

    # Load and validate config
    config = get_config()
    validation_errors = config.validate()

    if validation_errors:
        logger.error("Configuration validation failed:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        logger.error("Please check your .env file")
        sys.exit(1)

    logger.info("Configuration loaded successfully")
    logger.info(f"AI Provider: {config.ai_provider}")
    logger.info(f"Output formats: {', '.join(args.format or config.report_formats)}")

    success = True

    # Generate financial brief (unless trading-only)
    if not args.trading_only:
        logger.info("\n📰 Generating Financial Brief...")
        result = run_daily_report(use_ai=not args.no_ai, output_formats=args.format)

        if not result["success"]:
            logger.error(
                f"Financial brief generation failed: {result.get('error', 'Unknown error')}"
            )
            success = False

    # Generate trading advisor report (if requested or trading-only)
    if args.trading_advisor or args.trading_only:
        logger.info("\n📈 Generating Trading Advisor Report...")
        try:
            advisor = AdvisorReportGenerator()
            advisor_result = advisor.generate_full_report(generate_charts=not args.no_charts)

            if advisor_result["success"]:
                logger.info("Trading advisor report generated successfully!")
            else:
                logger.error(
                    f"Trading advisor report failed: {advisor_result.get('error', 'Unknown')}"
                )
                success = False

        except Exception as e:
            logger.error(f"Error generating trading advisor report: {e}", exc_info=True)
            success = False

    if success:
        logger.info("\n" + "=" * 70)
        logger.info("✅ All reports generated successfully!")
        logger.info("=" * 70)
        sys.exit(0)
    else:
        logger.error("\n❌ Some reports failed to generate")
        sys.exit(1)


if __name__ == "__main__":
    main()
