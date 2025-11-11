"""
Order types and data structures for execution system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from decimal import Decimal


class OrderSide(Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimeInForce(Enum):
    """Time in force."""
    DAY = "DAY"
    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


@dataclass
class Order:
    """Trading order."""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    status: OrderStatus = OrderStatus.PENDING

    # Optional parameters
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

    time_in_force: TimeInForce = TimeInForce.DAY

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Execution details
    filled_quantity: Decimal = Decimal('0')
    avg_fill_price: Optional[Decimal] = None
    commission: Decimal = Decimal('0')

    # Metadata
    strategy: Optional[str] = None
    signal_confidence: Optional[float] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': str(self.quantity),
            'status': self.status.value,
            'limit_price': str(self.limit_price) if self.limit_price else None,
            'stop_price': str(self.stop_price) if self.stop_price else None,
            'stop_loss': str(self.stop_loss) if self.stop_loss else None,
            'take_profit': str(self.take_profit) if self.take_profit else None,
            'time_in_force': self.time_in_force.value,
            'created_at': self.created_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'filled_quantity': str(self.filled_quantity),
            'avg_fill_price': str(self.avg_fill_price) if self.avg_fill_price else None,
            'commission': str(self.commission),
            'strategy': self.strategy,
            'signal_confidence': self.signal_confidence,
            'notes': self.notes
        }


@dataclass
class Position:
    """Trading position."""

    symbol: str
    quantity: Decimal  # Positive = long, Negative = short
    avg_entry_price: Decimal
    current_price: Decimal

    # PnL
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Decimal = Decimal('0')

    # Risk management
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

    # Metadata
    opened_at: datetime = field(default_factory=datetime.now)
    strategy: Optional[str] = None

    def update_price(self, current_price: Decimal):
        """Update current price and recalculate unrealized PnL."""
        self.current_price = current_price

        if self.quantity > 0:  # Long position
            self.unrealized_pnl = (current_price - self.avg_entry_price) * self.quantity
        else:  # Short position
            self.unrealized_pnl = (self.avg_entry_price - current_price) * abs(self.quantity)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'quantity': str(self.quantity),
            'avg_entry_price': str(self.avg_entry_price),
            'current_price': str(self.current_price),
            'unrealized_pnl': str(self.unrealized_pnl),
            'realized_pnl': str(self.realized_pnl),
            'stop_loss': str(self.stop_loss) if self.stop_loss else None,
            'take_profit': str(self.take_profit) if self.take_profit else None,
            'opened_at': self.opened_at.isoformat(),
            'strategy': self.strategy
        }


@dataclass
class Fill:
    """Order fill/execution."""

    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    commission: Decimal
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'fill_id': self.fill_id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': str(self.quantity),
            'price': str(self.price),
            'commission': str(self.commission),
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class Account:
    """Trading account state."""

    equity: Decimal
    cash: Decimal
    margin_used: Decimal = Decimal('0')
    margin_available: Decimal = Decimal('0')

    # Performance metrics
    total_pnl: Decimal = Decimal('0')
    daily_pnl: Decimal = Decimal('0')

    # Risk metrics
    max_drawdown: Decimal = Decimal('0')
    peak_equity: Decimal = Decimal('0')

    # Timestamp
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize derived fields."""
        if self.peak_equity == Decimal('0'):
            self.peak_equity = self.equity

        self.margin_available = self.cash - self.margin_used

    def update_equity(self, new_equity: Decimal):
        """Update equity and calculate metrics."""
        self.equity = new_equity

        # Update peak
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity

        # Calculate drawdown
        if self.peak_equity > Decimal('0'):
            current_drawdown = (self.peak_equity - new_equity) / self.peak_equity
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown

        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'equity': str(self.equity),
            'cash': str(self.cash),
            'margin_used': str(self.margin_used),
            'margin_available': str(self.margin_available),
            'total_pnl': str(self.total_pnl),
            'daily_pnl': str(self.daily_pnl),
            'max_drawdown': str(self.max_drawdown),
            'peak_equity': str(self.peak_equity),
            'updated_at': self.updated_at.isoformat()
        }
