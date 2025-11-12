"""
ZenMarket AI - Command Line Interface
Secure trading CLI with simulate/backtest/live modes.
"""

import argparse
import sys
from decimal import Decimal

from .advisor.indicators import IndicatorCalculator
from .advisor.signal_generator import SignalGenerator
from .execution.broker_simulator import BrokerSimulator
from .execution.execution_engine import ExecutionEngine
from .execution.order_types import OrderType
from .execution.position_sizing import SizingMethod
from .execution.risk_manager import RiskLimits
from .utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ZenMarket AI - AI-powered trading system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Paper trading (safe mode)
  python -m src.cli simulate --symbols "^GDAXI,BTC-USD" --order-type market

  # Backtest historical data
  python -m src.cli backtest --symbols "^GDAXI" --from 2024-01-01 --to 2025-01-01

  # Live trading (REQUIRES CONFIRMATION)
  python -m src.cli live --symbols "^GDAXI" --order-type limit --confirm-live

  # Dry run (test without placing orders)
  python -m src.cli simulate --symbols "AAPL,MSFT" --dry-run
        """,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True, help="Trading mode")

    # === SIMULATE command (paper trading) ===
    simulate_parser = subparsers.add_parser(
        "simulate", help="Paper trading mode (safe, simulated execution)"
    )
    add_common_args(simulate_parser)
    simulate_parser.add_argument(
        "--slippage-bps", type=float, default=1.5, help="Slippage in basis points (default: 1.5)"
    )
    simulate_parser.add_argument(
        "--commission",
        type=float,
        default=2.0,
        help="Commission per trade in dollars (default: 2.0)",
    )

    # === BACKTEST command ===
    backtest_parser = subparsers.add_parser("backtest", help="Historical backtesting mode")
    add_common_args(backtest_parser)
    backtest_parser.add_argument(
        "--from", dest="start_date", type=str, required=True, help="Start date (YYYY-MM-DD)"
    )
    backtest_parser.add_argument(
        "--to", dest="end_date", type=str, required=True, help="End date (YYYY-MM-DD)"
    )
    backtest_parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        choices=["1d", "1h", "15m", "5m"],
        help="Backtest interval (default: 1d)",
    )

    # === LIVE command (DANGEROUS) ===
    live_parser = subparsers.add_parser("live", help="⚠️  LIVE TRADING MODE (real money at risk)")
    add_common_args(live_parser)
    live_parser.add_argument(
        "--confirm-live",
        action="store_true",
        required=True,
        help="REQUIRED: Confirm you understand this is live trading with real money",
    )
    live_parser.add_argument(
        "--broker",
        type=str,
        choices=["ibkr", "mt5"],
        required=True,
        help="Broker to use (ibkr, mt5)",
    )

    return parser.parse_args()


def add_common_args(parser) -> None:
    """Add common arguments to a subcommand parser."""
    parser.add_argument(
        "--symbols",
        type=str,
        required=True,
        help='Comma-separated list of symbols (e.g., "^GDAXI,BTC-USD,AAPL")',
    )
    parser.add_argument(
        "--order-type",
        type=str,
        default="market",
        choices=["market", "limit", "stop", "stop_limit"],
        help="Order type (default: market)",
    )
    parser.add_argument(
        "--risk-per-trade",
        type=float,
        default=0.01,
        help="Risk per trade as decimal (default: 0.01 = 1%%)",
    )
    parser.add_argument(
        "--risk-per-day",
        type=float,
        default=0.03,
        help="Max risk per day as decimal (default: 0.03 = 3%%)",
    )
    parser.add_argument(
        "--max-daily-drawdown",
        type=float,
        default=0.05,
        help="Max daily drawdown as decimal (default: 0.05 = 5%%)",
    )
    parser.add_argument(
        "--max-consecutive-losses",
        type=int,
        default=3,
        help="Max consecutive losses before halt (default: 3)",
    )
    parser.add_argument(
        "--max-positions", type=int, default=5, help="Max open positions (default: 5)"
    )
    parser.add_argument(
        "--sizing-method",
        type=str,
        default="fixed_fractional",
        choices=["fixed_fractional", "kelly", "fixed_dollar"],
        help="Position sizing method (default: fixed_fractional)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode: validate but don't place orders"
    )
    parser.add_argument("--journal-pdf", action="store_true", help="Generate PDF journal report")
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Initial capital in dollars (default: 100000)",
    )


def create_risk_limits(args) -> RiskLimits:
    """Create risk limits from command line arguments."""
    return RiskLimits(
        max_risk_per_trade_pct=args.risk_per_trade,
        max_risk_per_day_pct=args.risk_per_day,
        max_daily_drawdown_pct=args.max_daily_drawdown,
        max_consecutive_losses=args.max_consecutive_losses,
        max_open_positions=args.max_positions,
    )


def get_order_type(order_type_str: str) -> OrderType:
    """Convert string to OrderType enum."""
    mapping = {
        "market": OrderType.MARKET,
        "limit": OrderType.LIMIT,
        "stop": OrderType.STOP,
        "stop_limit": OrderType.STOP_LIMIT,
    }
    return mapping.get(order_type_str, OrderType.MARKET)


def get_sizing_method(method_str: str) -> SizingMethod:
    """Convert string to SizingMethod enum."""
    mapping = {
        "fixed_fractional": SizingMethod.FIXED_FRACTIONAL,
        "kelly": SizingMethod.KELLY,
        "fixed_dollar": SizingMethod.FIXED_DOLLAR,
    }
    return mapping.get(method_str, SizingMethod.FIXED_FRACTIONAL)


def run_simulate(args) -> None:
    """Run paper trading simulation."""
    logger.info("=" * 60)
    logger.info("PAPER TRADING MODE - Simulation")
    logger.info("=" * 60)

    # Parse symbols
    symbols = [s.strip() for s in args.symbols.split(",")]
    logger.info(f"Trading symbols: {symbols}")

    # Create simulator broker
    broker = BrokerSimulator(
        initial_cash=Decimal(str(args.initial_capital)),
        slippage_bps=args.slippage_bps,
        commission_per_trade=Decimal(str(args.commission)),
    )
    broker.connect()

    # Create risk limits
    risk_limits = create_risk_limits(args)

    # Create execution engine
    engine = ExecutionEngine(
        broker=broker,
        risk_limits=risk_limits,
        sizing_method=get_sizing_method(args.sizing_method),
        journal_enabled=True,
    )

    logger.info("Execution engine initialized")
    logger.info(f"Risk per trade: {args.risk_per_trade:.2%}")
    logger.info(f"Risk per day: {args.risk_per_day:.2%}")
    logger.info(f"Max drawdown: {args.max_daily_drawdown:.2%}")
    logger.info(f"Sizing method: {args.sizing_method}")

    # Initialize advisor
    indicator_calculator = IndicatorCalculator()
    signal_generator = SignalGenerator()

    # Fetch data and generate signals
    logger.info("\nFetching market data and generating signals...")

    import yfinance as yf

    for symbol in symbols:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Analyzing {symbol}")
            logger.info("=" * 60)

            # Fetch historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo", interval="1d")

            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                continue

            # Calculate indicators
            indicators = indicator_calculator.calculate_all_indicators(symbol, df)

            if not indicators:
                logger.warning(f"Could not calculate indicators for {symbol}")
                continue

            # Generate signal
            signal = signal_generator.generate_signal(indicators)

            logger.info(f"\nSignal: {signal.signal.value} (confidence: {signal.confidence:.2%})")
            logger.info(f"Reasons: {', '.join(signal.reasons)}")

            # Execute signal
            order = engine.execute_signal(
                signal=signal,
                order_type=get_order_type(args.order_type),
                risk_percent=args.risk_per_trade,
                dry_run=args.dry_run,
            )

            if order:
                logger.info(f"✓ Order executed: {order.order_id}")

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}", exc_info=True)

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("SESSION SUMMARY")
    logger.info("=" * 60)

    status = engine.get_status()
    logger.info(f"\nBroker: {status['broker']}")
    logger.info(f"Connected: {status['connected']}")

    if status.get("performance"):
        perf = status["performance"]
        logger.info("\nPerformance:")
        logger.info(f"  Initial Equity: {perf.get('initial_equity', 'N/A')}")
        logger.info(f"  Current Equity: {perf.get('current_equity', 'N/A')}")
        logger.info(f"  Total Return: {perf.get('total_return', 'N/A')}")
        logger.info(f"  Max Drawdown: {perf.get('max_drawdown', 'N/A')}")
        logger.info(f"  Total Trades: {perf.get('total_trades', 0)}")
        logger.info(f"  Win Rate: {perf.get('win_rate', 'N/A')}")

    risk_summary = status.get("risk_summary", {})
    risk_state = risk_summary.get("state", {})
    logger.info("\nRisk Status:")
    logger.info(f"  Trading Halted: {risk_state.get('trading_halted', False)}")
    if risk_state.get("halt_reason"):
        logger.info(f"  Halt Reason: {risk_state['halt_reason']}")
    logger.info(f"  Consecutive Losses: {risk_state.get('consecutive_losses', 0)}")
    logger.info(f"  Daily PnL: {risk_state.get('daily_pnl', 'N/A')}")

    # Shutdown
    engine.shutdown()

    logger.info("\n" + "=" * 60)
    logger.info("Paper trading session completed")
    logger.info("=" * 60)


def run_backtest(args) -> int:
    """Run historical backtest."""
    logger.info("=" * 60)
    logger.info("BACKTEST MODE")
    logger.info("=" * 60)

    logger.info(f"Period: {args.start_date} to {args.end_date}")
    logger.info(f"Interval: {args.interval}")

    # TODO: Implement backtest runner
    logger.warning("Backtest module not yet implemented")
    logger.info("This will be implemented in src/backtest/runner.py")

    return 1


def run_live(args) -> int:
    """Run live trading (DANGEROUS)."""
    logger.critical("=" * 60)
    logger.critical("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK")
    logger.critical("=" * 60)

    if not args.confirm_live:
        logger.error("ERROR: --confirm-live flag is required for live trading")
        logger.error("This is a safety check to prevent accidental live trading")
        return 1

    logger.warning(f"Broker: {args.broker}")
    logger.warning("You are about to trade with REAL MONEY")
    logger.warning("All orders will be sent to your broker account")

    # Final confirmation prompt
    try:
        confirmation = input("\nType 'I UNDERSTAND THE RISKS' to proceed: ")
        if confirmation != "I UNDERSTAND THE RISKS":
            logger.info("Live trading cancelled - confirmation not received")
            return 0
    except KeyboardInterrupt:
        logger.info("\nLive trading cancelled by user")
        return 0

    logger.error("ERROR: Live broker connections not yet implemented")
    logger.info("Supported brokers will be added in future releases:")
    logger.info("  - Interactive Brokers (IBKR)")
    logger.info("  - MetaTrader 5 (MT5)")
    logger.info("\nFor now, please use 'simulate' mode for paper trading")

    return 1


def main():
    """Main CLI entry point."""
    try:
        args = parse_args()

        # Route to appropriate command
        if args.command == "simulate":
            return run_simulate(args)
        if args.command == "backtest":
            return run_backtest(args)
        if args.command == "live":
            return run_live(args)
        logger.error(f"Unknown command: {args.command}")
        return 1

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
