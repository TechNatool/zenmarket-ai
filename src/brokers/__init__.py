"""Real broker integrations for live trading.

This module provides adapters for real brokers:
- Interactive Brokers (IBKR) via ib_insync
- MetaTrader 5 (MT5) via MetaTrader5

All brokers implement the BrokerBase interface for consistency.

SECURITY WARNING:
Live trading with real brokers involves real money. Always:
1. Test thoroughly in paper trading mode first
2. Use environment variables for API credentials (never hardcode)
3. Implement proper risk management
4. Start with small position sizes
5. Monitor positions actively
"""

from src.brokers.broker_factory import BrokerFactory, BrokerType
from src.brokers.ibkr_adapter import IBKRAdapter
from src.brokers.mt5_adapter import MT5Adapter

__all__ = [
    "BrokerFactory",
    "BrokerType",
    "IBKRAdapter",
    "MT5Adapter",
]
