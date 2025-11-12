"""
Position sizing calculators for risk management.
Implements various sizing methods: fixed fractional, Kelly criterion, fixed dollar.
"""

from decimal import Decimal
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SizingMethod(Enum):
    """Position sizing method."""

    FIXED_FRACTIONAL = "fixed_fractional"
    KELLY = "kelly"
    FIXED_DOLLAR = "fixed_dollar"
    FIXED_SHARES = "fixed_shares"


class PositionSizer:
    """
    Calculate position sizes based on risk parameters.

    Supports multiple sizing methods to adapt to different strategies.
    """

    def __init__(self) -> None:
        """Initialize position sizer."""

    def fixed_fractional(
        self,
        equity: Decimal,
        risk_percent: float,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        atr: Decimal | None = None,
        atr_avg: Decimal | None = None,
        tick_value: Decimal = Decimal("1.0"),
    ) -> Decimal:
        """
        Calculate position size using fixed fractional method.

        Risks a fixed percentage of equity on each trade.

        Args:
            equity: Current account equity
            risk_percent: Risk per trade as percentage (e.g., 0.01 = 1%)
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            atr: Current ATR (optional, for volatility adjustment)
            atr_avg: Average ATR (optional, for volatility adjustment)
            tick_value: Value per price tick (default: 1.0)

        Returns:
            Position size (quantity)

        Example:
            Equity: $100,000
            Risk: 1% = $1,000
            Entry: $100
            Stop: $95
            Risk per share: $5
            Position: $1,000 / $5 = 200 shares
        """
        if entry_price <= Decimal("0") or stop_loss_price <= Decimal("0"):
            raise ValueError("Prices must be positive")

        if equity <= Decimal("0"):
            raise ValueError("Equity must be positive")

        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price) * tick_value

        if risk_per_share <= Decimal("0"):
            # If stop loss equals entry price, return 0
            return Decimal("0")

        # Calculate dollar risk
        dollar_risk = equity * Decimal(str(risk_percent))

        # Calculate position size
        position_size = dollar_risk / risk_per_share

        # Apply volatility adjustment if ATR provided
        if atr is not None and atr_avg is not None and atr_avg > Decimal("0"):
            volatility_ratio = atr / atr_avg
            if volatility_ratio > Decimal("1.0"):
                # Reduce position size in high volatility
                position_size = position_size / volatility_ratio

        logger.debug(
            f"Fixed fractional: equity=${equity}, risk={risk_percent*100}%, "
            f"entry=${entry_price}, stop=${stop_loss_price}, "
            f"risk/share=${risk_per_share}, size={position_size}"
        )

        return position_size

    def kelly_criterion(
        self,
        equity: Decimal,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        entry_price: Decimal | None = None,
        kelly_fraction: float = 0.25,
    ) -> Decimal:
        """
        Calculate position size using Kelly criterion.

        Kelly formula: f = (bp - q) / b
        Where:
        - f = fraction of capital to bet
        - b = ratio of win to loss (avg_win / avg_loss)
        - p = probability of winning (win_rate)
        - q = probability of losing (1 - win_rate)

        Args:
            equity: Current account equity
            win_rate: Historical win rate (0.0 to 1.0)
            avg_win: Average winning trade size (absolute)
            avg_loss: Average losing trade size (absolute, positive)
            entry_price: Entry price per share (if provided, returns quantity, else returns dollar amount)
            kelly_fraction: Fraction of Kelly to use (default: 0.25 for quarter-Kelly)

        Returns:
            Quantity of shares (if entry_price provided) or dollar amount to risk

        Note:
            Full Kelly can be aggressive. quarter-Kelly (0.25) is more conservative.
        """
        if not (0.0 < win_rate < 1.0):
            raise ValueError("Win rate must be between 0 and 1")

        # Convert to Decimal for calculations
        avg_win_d = Decimal(str(avg_win)) if not isinstance(avg_win, Decimal) else avg_win
        avg_loss_d = Decimal(str(avg_loss)) if not isinstance(avg_loss, Decimal) else avg_loss

        if avg_win_d <= 0 or avg_loss_d <= 0:
            raise ValueError("Average win and loss must be positive")

        # Win/loss ratio
        win_loss_ratio = float(avg_win_d / avg_loss_d)

        # Kelly percentage
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Cap at 0 if negative (don't bet if edge is negative)
        kelly_pct = max(0.0, kelly_pct)

        # Apply Kelly fraction (for safety)
        kelly_pct *= kelly_fraction

        # Calculate dollar amount
        position_value = equity * Decimal(str(kelly_pct))

        logger.debug(
            f"Kelly: equity=${equity}, win_rate={win_rate}, "
            f"avg_win={avg_win}, avg_loss={avg_loss}, "
            f"kelly%={kelly_pct*100:.2f}%, position=${position_value}"
        )

        # Convert to quantity if entry_price provided
        if entry_price is not None and entry_price > Decimal("0"):
            quantity = int(position_value / entry_price)
            return Decimal(str(quantity))

        return position_value

    def fixed_dollar(self, dollar_amount: Decimal, entry_price: Decimal) -> Decimal:
        """
        Calculate position size for fixed dollar amount.

        Args:
            dollar_amount: Dollar amount to invest
            entry_price: Entry price

        Returns:
            Position size (quantity) - whole shares only
        """
        if dollar_amount <= Decimal("0"):
            raise ValueError("Dollar amount and price must be positive")

        if entry_price <= Decimal("0"):
            return Decimal("0")

        # Calculate quantity and round down to whole shares
        quantity = int(dollar_amount / entry_price)

        logger.debug(
            f"Fixed dollar: amount=${dollar_amount}, price=${entry_price}, size={quantity}"
        )

        return Decimal(str(quantity))

    def fixed_shares(self, shares: Decimal) -> Decimal:
        """
        Return fixed number of shares.

        Args:
            shares: Number of shares

        Returns:
            Position size (same as input)
        """
        if shares <= Decimal("0"):
            raise ValueError("Shares must be positive")

        return shares

    def percent_of_equity(self, equity: Decimal, percent: float, entry_price: Decimal) -> Decimal:
        """
        Calculate position size as percentage of equity.

        Args:
            equity: Current account equity
            percent: Percentage of equity to allocate (e.g., 0.10 = 10%)
            entry_price: Entry price per share

        Returns:
            Position size (quantity of shares)

        Example:
            Equity: $100,000
            Percent: 10% = 0.10
            Entry: $50
            Position value: $10,000
            Quantity: 200 shares
        """
        if equity <= Decimal("0"):
            raise ValueError("Equity must be positive")

        if percent <= 0.0:
            raise ValueError("Percent must be positive")

        if entry_price <= Decimal("0"):
            raise ValueError("Entry price must be positive")

        # Calculate dollar amount to invest
        position_value = equity * Decimal(str(percent))

        # Calculate quantity
        quantity = int(position_value / entry_price)

        logger.debug(
            f"Percent of equity: equity=${equity}, percent={percent*100}%, "
            f"entry=${entry_price}, position=${position_value}, quantity={quantity}"
        )

        return Decimal(str(quantity))

    def r_multiple_sizing(
        self,
        equity: Decimal,
        r_amount: Decimal,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        target_r: float = 1.0,
    ) -> Decimal:
        """
        Calculate position size based on R-multiples.

        R is the initial risk amount. This method allows you to size
        positions based on multiples of R.

        Args:
            equity: Current account equity
            r_amount: Dollar amount for 1R (e.g., $1000 = 1R)
            entry_price: Entry price per share
            stop_loss_price: Stop loss price
            target_r: Number of R to risk (default: 1.0)

        Returns:
            Position size (quantity of shares)

        Example:
            1R = $1000
            Target = 2R (risk $2000)
            Entry: $100, Stop: $95
            Risk per share: $5
            Quantity: $2000 / $5 = 400 shares
        """
        if equity <= Decimal("0"):
            raise ValueError("Equity must be positive")

        if r_amount <= Decimal("0"):
            raise ValueError("R amount must be positive")

        if entry_price <= Decimal("0") or stop_loss_price <= Decimal("0"):
            raise ValueError("Prices must be positive")

        if target_r <= 0:
            raise ValueError("Target R must be positive")

        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == Decimal("0"):
            return Decimal("0")

        # Calculate total dollar risk
        total_risk = r_amount * Decimal(str(target_r))

        # Calculate quantity
        quantity = int(total_risk / risk_per_share)

        logger.debug(
            f"R-multiple sizing: 1R=${r_amount}, target_r={target_r}, "
            f"entry=${entry_price}, stop=${stop_loss_price}, "
            f"risk/share=${risk_per_share}, quantity={quantity}"
        )

        return Decimal(str(quantity))

    def calculate_r_multiple(
        self, entry_price: Decimal, exit_price: Decimal, stop_loss_price: Decimal
    ) -> float:
        """
        Calculate R-multiple for a trade.

        R-multiple = (Exit - Entry) / (Entry - Stop)

        Args:
            entry_price: Entry price
            exit_price: Exit price (actual or target)
            stop_loss_price: Stop loss price

        Returns:
            R-multiple (e.g., 2.0 = 2R profit)
        """
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == Decimal("0"):
            raise ValueError("Stop loss cannot equal entry price")

        profit_per_share = exit_price - entry_price

        return float(profit_per_share / risk_per_share)

    def calculate_risk_reward_ratio(
        self, entry_price: Decimal, target_price: Decimal, stop_loss_price: Decimal
    ) -> float:
        """
        Calculate risk/reward ratio.

        RR = (Target - Entry) / (Entry - Stop)

        Args:
            entry_price: Entry price
            target_price: Target/take-profit price
            stop_loss_price: Stop loss price

        Returns:
            Risk/reward ratio (e.g., 3.0 = 3:1 RR)
        """
        return self.calculate_r_multiple(entry_price, target_price, stop_loss_price)

    def adjust_for_volatility(
        self,
        base_size: Decimal,
        current_atr: float,
        average_atr: float,
        volatility_adjustment: bool = True,
    ) -> Decimal:
        """
        Adjust position size based on volatility (ATR).

        If volatility is higher, reduce position size.

        Args:
            base_size: Base position size
            current_atr: Current ATR value
            average_atr: Average/normal ATR value
            volatility_adjustment: Enable volatility adjustment

        Returns:
            Adjusted position size
        """
        if not volatility_adjustment:
            return base_size

        if current_atr <= 0 or average_atr <= 0:
            logger.warning("Invalid ATR values, no adjustment")
            return base_size

        # Adjustment factor (inverse relationship)
        adjustment_factor = average_atr / current_atr

        # Cap adjustment between 0.5x and 2.0x
        adjustment_factor = max(0.5, min(2.0, adjustment_factor))

        adjusted_size = base_size * Decimal(str(adjustment_factor))

        logger.debug(
            f"Volatility adjustment: base={base_size}, "
            f"current_atr={current_atr}, avg_atr={average_atr}, "
            f"factor={adjustment_factor:.2f}, adjusted={adjusted_size}"
        )

        return adjusted_size

    def calculate_position_value(self, quantity: Decimal, price: Decimal) -> Decimal:
        """
        Calculate total position value.

        Args:
            quantity: Position size
            price: Price per unit

        Returns:
            Total value
        """
        return quantity * price

    def calculate_max_position_size(
        self, equity: Decimal, max_position_percent: float, price: Decimal
    ) -> Decimal:
        """
        Calculate maximum position size based on portfolio allocation.

        Args:
            equity: Account equity
            max_position_percent: Max % of equity per position (e.g., 0.10 = 10%)
            price: Entry price

        Returns:
            Maximum position size
        """
        max_dollar_value = equity * Decimal(str(max_position_percent))
        max_position = max_dollar_value / price

        logger.debug(
            f"Max position: equity=${equity}, max%={max_position_percent*100}%, "
            f"price=${price}, max_size={max_position}"
        )

        return max_position


# Convenience function
def calculate_position_size(
    method: SizingMethod,
    equity: Decimal,
    entry_price: Decimal,
    stop_loss_price: Decimal | None = None,
    risk_percent: float = 0.01,
    **kwargs,
) -> Decimal:
    """
    Calculate position size using specified method.

    Args:
        method: Sizing method to use
        equity: Account equity
        entry_price: Entry price
        stop_loss_price: Stop loss price (required for some methods)
        risk_percent: Risk percentage (for fixed_fractional)
        **kwargs: Additional method-specific parameters

    Returns:
        Position size

    Example:
        >>> size = calculate_position_size(
        ...     method=SizingMethod.FIXED_FRACTIONAL,
        ...     equity=Decimal('100000'),
        ...     entry_price=Decimal('100'),
        ...     stop_loss_price=Decimal('95'),
        ...     risk_percent=0.01
        ... )
    """
    sizer = PositionSizer()

    if method == SizingMethod.FIXED_FRACTIONAL:
        if stop_loss_price is None:
            raise ValueError("stop_loss_price required for fixed_fractional method")

        return sizer.fixed_fractional(
            equity=equity,
            risk_percent=risk_percent,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            tick_value=kwargs.get("tick_value", Decimal("1.0")),
        )

    if method == SizingMethod.KELLY:
        return sizer.kelly_criterion(
            equity=equity,
            win_rate=kwargs.get("win_rate", 0.5),
            avg_win=kwargs.get("avg_win", 1.0),
            avg_loss=kwargs.get("avg_loss", 1.0),
            kelly_fraction=kwargs.get("kelly_fraction", 0.25),
        )

    if method == SizingMethod.FIXED_DOLLAR:
        return sizer.fixed_dollar(
            dollar_amount=kwargs.get("dollar_amount", equity * Decimal("0.01")),
            entry_price=entry_price,
        )

    if method == SizingMethod.FIXED_SHARES:
        return sizer.fixed_shares(shares=kwargs.get("shares", Decimal("100")))

    raise ValueError(f"Unknown sizing method: {method}")
