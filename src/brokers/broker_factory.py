"""Broker factory for dynamic broker selection.

Provides a factory pattern to create broker instances based on configuration.
Supports simulator, backtest, IBKR, and MT5 brokers.
"""

from decimal import Decimal
from enum import Enum
from typing import Any

from src.execution.broker_base import BrokerBase
from src.execution.broker_simulator import BrokerSimulator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BrokerType(str, Enum):
    """Supported broker types."""

    SIMULATOR = "simulator"
    BACKTEST = "backtest"
    IBKR = "ibkr"
    MT5 = "mt5"


class BrokerFactory:
    """Factory for creating broker instances."""

    @staticmethod
    def create_broker(
        broker_type: BrokerType | str,
        **kwargs: Any,
    ) -> BrokerBase:
        """Create a broker instance.

        Args:
            broker_type: Type of broker to create
            **kwargs: Broker-specific configuration

        Returns:
            BrokerBase instance

        Raises:
            ValueError: If broker type is not supported

        Example:
            >>> broker = BrokerFactory.create_broker(
            ...     BrokerType.SIMULATOR,
            ...     initial_cash=100000,
            ...     slippage_bps=1.5
            ... )
        """
        if isinstance(broker_type, str):
            broker_type = BrokerType(broker_type.lower())

        logger.info(f"Creating broker: {broker_type.value}")

        if broker_type == BrokerType.SIMULATOR:
            return BrokerFactory._create_simulator(**kwargs)

        if broker_type == BrokerType.BACKTEST:
            return BrokerFactory._create_backtest_broker(**kwargs)

        if broker_type == BrokerType.IBKR:
            return BrokerFactory._create_ibkr(**kwargs)

        if broker_type == BrokerType.MT5:
            return BrokerFactory._create_mt5(**kwargs)

        raise ValueError(f"Unsupported broker type: {broker_type}")

    @staticmethod
    def _create_simulator(**kwargs: Any) -> BrokerSimulator:
        """Create a simulator broker."""
        return BrokerSimulator(
            initial_cash=kwargs.get("initial_cash", Decimal("100000")),
            slippage_bps=kwargs.get("slippage_bps", 1.5),
            commission_per_trade=kwargs.get("commission_per_trade", Decimal("2.0")),
            ledger_dir=kwargs.get("ledger_dir"),
        )

    @staticmethod
    def _create_backtest_broker(**kwargs: Any) -> Any:
        """Create a backtest broker."""
        from src.backtest.backtest_broker import BacktestBroker

        historical_data = kwargs.get("historical_data")
        if not historical_data:
            raise ValueError("historical_data is required for backtest broker")

        return BacktestBroker(
            historical_data=historical_data,
            initial_cash=kwargs.get("initial_cash", Decimal("100000")),
            slippage_bps=kwargs.get("slippage_bps", 1.5),
            commission_per_trade=kwargs.get("commission_per_trade", Decimal("2.0")),
        )

    @staticmethod
    def _create_ibkr(**kwargs: Any) -> Any:
        """Create an IBKR broker."""
        from src.brokers.ibkr_adapter import IBKRAdapter

        return IBKRAdapter(
            host=kwargs.get("host"),
            port=kwargs.get("port"),
            client_id=kwargs.get("client_id"),
            paper_trading=kwargs.get("paper_trading", True),
        )

    @staticmethod
    def _create_mt5(**kwargs: Any) -> Any:
        """Create an MT5 broker."""
        from src.brokers.mt5_adapter import MT5Adapter

        return MT5Adapter(
            login=kwargs.get("login"),
            password=kwargs.get("password"),
            server=kwargs.get("server"),
        )

    @staticmethod
    def create_from_env(
        broker_type: BrokerType | str | None = None,
    ) -> BrokerBase:
        """Create broker from environment variables.

        Reads configuration from:
        - BROKER_TYPE (simulator, ibkr, mt5)
        - IBKR_* for IBKR configuration
        - MT5_* for MT5 configuration

        Args:
            broker_type: Override broker type (default: from BROKER_TYPE env)

        Returns:
            BrokerBase instance
        """
        import os

        if broker_type is None:
            broker_type_str = os.getenv("BROKER_TYPE", "simulator")
            broker_type = BrokerType(broker_type_str.lower())

        if isinstance(broker_type, str):
            broker_type = BrokerType(broker_type.lower())

        # Create broker based on type
        if broker_type == BrokerType.SIMULATOR:
            return BrokerFactory.create_broker(BrokerType.SIMULATOR)

        if broker_type == BrokerType.IBKR:
            return BrokerFactory.create_broker(
                BrokerType.IBKR,
                host=os.getenv("IBKR_HOST"),
                port=int(os.getenv("IBKR_PORT", "7497")),
                client_id=int(os.getenv("IBKR_CLIENT_ID", "1")),
                paper_trading=os.getenv("IBKR_PAPER_TRADING", "true").lower() == "true",
            )

        if broker_type == BrokerType.MT5:
            login = os.getenv("MT5_LOGIN")
            return BrokerFactory.create_broker(
                BrokerType.MT5,
                login=int(login) if login else None,
                password=os.getenv("MT5_PASSWORD"),
                server=os.getenv("MT5_SERVER"),
            )

        raise ValueError(f"Unsupported broker type: {broker_type}")
