"""
Trade journal with CSV, JSON, and PDF export.
Mandatory logging of all trading activity.
"""

import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.utils.logger import get_logger

from .order_types import Fill, Order, Position

logger = get_logger(__name__)


class TradeJournal:
    """
    Trade journal with multiple export formats.

    Logs all trading activity to CSV and JSON for analysis and compliance.
    """

    def __init__(self, journal_dir: Path | None = None) -> None:
        """
        Initialize trade journal.

        Args:
            journal_dir: Directory for journal files (default: data/journal)
        """
        if journal_dir is None:
            journal_dir = Path("data/journal")

        self.journal_dir = journal_dir
        self.journal_dir.mkdir(parents=True, exist_ok=True)

        self.trades: list[dict] = []
        self.orders: list[Order] = []  # Keep track of orders separately for tests
        self.date_str = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Trade journal initialized: {self.journal_dir}")

    def log_order(self, order: Order) -> None:
        """
        Log order to journal.

        Args:
            order: Order to log
        """
        entry = {"timestamp": datetime.now().isoformat(), "type": "order", "data": order.to_dict()}

        self.trades.append(entry)
        self.orders.append(order)  # Keep order objects for easy access

        # Append to CSV
        self._append_to_csv("orders", entry["data"])

        logger.debug(f"Order logged: {order.order_id}")

    def log_fill(self, fill: Fill) -> None:
        """
        Log fill to journal.

        Args:
            fill: Fill to log
        """
        entry = {"timestamp": datetime.now().isoformat(), "type": "fill", "data": fill.to_dict()}

        self.trades.append(entry)

        # Append to CSV
        self._append_to_csv("fills", entry["data"])

        logger.debug(f"Fill logged: {fill.fill_id}")

    def log_position(self, position: Position) -> None:
        """
        Log position snapshot.

        Args:
            position: Position to log
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "position",
            "data": position.to_dict(),
        }

        self.trades.append(entry)

        logger.debug(f"Position logged: {position.symbol}")

    def _append_to_csv(self, file_type: str, data: dict) -> None:
        """Append entry to CSV file."""
        csv_file = self.journal_dir / f"{file_type}_{self.date_str}.csv"

        file_exists = csv_file.exists()

        try:
            with open(csv_file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())

                if not file_exists:
                    writer.writeheader()

                writer.writerow(data)

        except Exception as e:
            logger.error(f"Error writing to CSV: {e}", exc_info=True)

    def save_json(self) -> None:
        """Save journal to JSON file."""
        json_file = self.journal_dir / f"journal_{self.date_str}.json"

        try:
            with open(json_file, "w") as f:
                json.dump({"date": self.date_str, "entries": self.trades}, f, indent=2, default=str)

            logger.info(f"Journal saved to JSON: {json_file}")

        except Exception as e:
            logger.error(f"Error saving JSON: {e}", exc_info=True)

    def generate_daily_summary(self) -> dict:
        """
        Generate daily trading summary.

        Returns:
            Dictionary with summary statistics
        """
        orders = [e for e in self.trades if e["type"] == "order"]
        fills = [e for e in self.trades if e["type"] == "fill"]

        total_commission = sum(Decimal(f["data"].get("commission", "0")) for f in fills)

        return {
            "date": self.date_str,
            "total_orders": len(orders),
            "total_fills": len(fills),
            "total_commission": str(total_commission),
            "entries": len(self.trades),
        }

    def export_to_pdf(self, output_dir: Path | None = None) -> None:
        """
        Export journal to PDF (placeholder for future implementation).

        Args:
            output_dir: Output directory (default: reports/trades)
        """
        # Placeholder - would use WeasyPrint to generate PDF report
        logger.warning("PDF export not yet implemented")
