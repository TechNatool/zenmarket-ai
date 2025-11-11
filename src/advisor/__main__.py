#!/usr/bin/env python3
"""
Main entry point for AI Trading Advisor.
Can be run as: python -m src.advisor
"""

import argparse
import sys

from .advisor_report import AdvisorReportGenerator
from ..utils.logger import setup_logger, get_logger
from ..utils.config_loader import get_config

logger = None


def main():
    """Main function."""
    global logger

    parser = argparse.ArgumentParser(
        description="ZenMarket AI - Trading Advisor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.advisor                              # Analyze default tickers
  python -m src.advisor --tickers "^GDAXI,^IXIC"    # Analyze specific tickers
  python -m src.advisor --no-charts                  # Skip chart generation
  python -m src.advisor --log-level DEBUG            # Enable debug logging
        """
    )

    parser.add_argument(
        "--tickers",
        type=str,
        help="Comma-separated list of tickers (default: from config)"
    )

    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation (faster)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="ZenMarket AI Trading Advisor v1.0.0"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logger(level=args.log_level, console=True)

    # Load config
    config = get_config()
    validation_errors = config.validate()

    if validation_errors:
        logger.error("Configuration validation failed:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Parse tickers
    tickers = None
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(",")]

    # Generate report
    generator = AdvisorReportGenerator()

    result = generator.generate_full_report(
        tickers=tickers,
        generate_charts=not args.no_charts
    )

    if result["success"]:
        logger.info("Trading advisor report generated successfully!")
        sys.exit(0)
    else:
        logger.error(f"Failed to generate report: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
