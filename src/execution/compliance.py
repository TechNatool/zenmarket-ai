"""
Compliance and market rules checker.
Validates trading hours, market calendar, and regulatory constraints.
"""

from datetime import datetime, time
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MarketStatus(Enum):
    """Market status."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    AFTER_HOURS = "AFTER_HOURS"


class ComplianceChecker:
    """
    Compliance and regulatory checker.

    Validates:
    - Trading hours
    - Market holidays
    - Regulatory constraints
    """

    # Simplified market hours (in ET/local time)
    MARKET_HOURS = {
        "US_STOCKS": {
            "regular_open": time(9, 30),
            "regular_close": time(16, 0),
            "pre_market_open": time(4, 0),
            "after_hours_close": time(20, 0),
        },
        "FOREX": {"regular_open": time(0, 0), "regular_close": time(23, 59)},  # 24h
        "CRYPTO": {"regular_open": time(0, 0), "regular_close": time(23, 59)},  # 24/7
    }

    def __init__(self) -> None:
        """Initialize compliance checker."""

    def check_market_hours(
        self, symbol: str, allow_extended_hours: bool = False
    ) -> tuple[bool, MarketStatus, str | None]:
        """
        Check if market is open for symbol.

        Args:
            symbol: Trading symbol
            allow_extended_hours: Allow pre/post market trading

        Returns:
            Tuple of (is_open, status, message)
        """
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()

        # Determine market type
        market_type = self._get_market_type(symbol)

        # Check weekend
        if market_type == "US_STOCKS" and weekday >= 5:  # Saturday or Sunday
            return False, MarketStatus.CLOSED, "Market closed: Weekend"

        # Get market hours
        hours = self.MARKET_HOURS.get(market_type, self.MARKET_HOURS["US_STOCKS"])

        regular_open = hours["regular_open"]
        regular_close = hours["regular_close"]

        # Check regular hours
        if regular_open <= current_time <= regular_close:
            return True, MarketStatus.OPEN, None

        # Check extended hours (if allowed and applicable)
        if allow_extended_hours and market_type == "US_STOCKS":
            pre_market_open = hours.get("pre_market_open", regular_open)
            after_hours_close = hours.get("after_hours_close", regular_close)

            if pre_market_open <= current_time < regular_open:
                return True, MarketStatus.PRE_MARKET, "Pre-market hours"

            if regular_close < current_time <= after_hours_close:
                return True, MarketStatus.AFTER_HOURS, "After-hours trading"

        return False, MarketStatus.CLOSED, f"Market closed (current time: {current_time})"

    def _get_market_type(self, symbol: str) -> str:
        """Determine market type from symbol."""
        symbol_upper = symbol.upper()

        # Forex pairs
        if "=" in symbol_upper or len(symbol_upper) == 6:  # e.g., EURUSD=X or EURUSD
            return "FOREX"

        # Crypto
        if "BTC" in symbol_upper or "ETH" in symbol_upper or "-USD" in symbol_upper:
            return "CRYPTO"

        # Default to stocks
        return "US_STOCKS"

    def validate_order_compliance(
        self, symbol: str, quantity: float, price: float | None = None
    ) -> tuple[bool, str | None]:
        """
        Validate order compliance.

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            price: Order price (optional)

        Returns:
            Tuple of (is_compliant, error_message)
        """
        # Check quantity
        if quantity <= 0:
            return False, "Quantity must be positive"

        # Check price
        if price is not None and price <= 0:
            return False, "Price must be positive"

        # All checks passed
        return True, None

    def check_pattern_day_trader(
        self, day_trades_count: int, account_equity: float, min_equity_threshold: float = 25000.0
    ) -> tuple[bool, str | None]:
        """
        Check Pattern Day Trader (PDT) rule compliance.

        PDT rule: If you make 4+ day trades in 5 business days,
        you need $25k+ equity.

        Args:
            day_trades_count: Number of day trades in last 5 days
            account_equity: Current account equity
            min_equity_threshold: Minimum equity required (default: $25,000)

        Returns:
            Tuple of (is_compliant, warning_message)
        """
        if day_trades_count >= 4:
            if account_equity < min_equity_threshold:
                return False, (
                    f"PDT rule violation: {day_trades_count} day trades but "
                    f"equity ${account_equity:,.2f} < ${min_equity_threshold:,.2f}"
                )
            return True, f"PDT compliant with {day_trades_count} day trades"

        return True, None

    def get_pre_trade_checklist(
        self, symbol: str, account_equity: float
    ) -> dict[str, tuple[bool, str | None]]:
        """
        Get pre-trade compliance checklist.

        Args:
            symbol: Trading symbol
            account_equity: Account equity

        Returns:
            Dictionary of check_name: (passed, message)
        """
        checklist = {}

        # Market hours check
        is_open, status, message = self.check_market_hours(symbol)
        checklist["market_hours"] = (is_open, message or f"Market is {status.value}")

        # Weekend check
        now = datetime.now()
        is_weekday = now.weekday() < 5
        checklist["weekday"] = (is_weekday, None if is_weekday else "Weekend - markets closed")

        # Account equity check
        has_equity = account_equity > 0
        checklist["account_equity"] = (
            has_equity,
            None if has_equity else "Zero or negative equity",
        )

        return checklist

    def log_compliance_check(self, symbol: str, result: bool, message: str | None = None) -> None:
        """
        Log compliance check result.

        Args:
            symbol: Trading symbol
            result: Check result
            message: Optional message
        """
        if result:
            logger.info(f"Compliance OK: {symbol} - {message or 'Passed'}")
        else:
            logger.warning(f"Compliance FAILED: {symbol} - {message or 'Failed'}")
