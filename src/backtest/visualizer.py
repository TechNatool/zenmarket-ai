"""Visualization and reporting for backtest results.

Generates equity curves, drawdown plots, trade distributions,
and comprehensive PDF reports.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib as mpl

mpl.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.backtest.metrics import PerformanceMetrics

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


class BacktestVisualizer:
    """Generates visualizations and reports for backtest results."""

    @staticmethod
    def plot_equity_curve(
        equity_curve: pd.DataFrame,
        output_path: Path | None = None,
    ) -> bytes | None:
        """Plot equity curve over time.

        Args:
            equity_curve: DataFrame with 'timestamp' and 'equity' columns
            output_path: Optional path to save the plot

        Returns:
            PNG image bytes if output_path is None, otherwise None
        """
        _fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            equity_curve["timestamp"],
            equity_curve["equity"],
            linewidth=2,
            color="steelblue",
            label="Equity",
        )

        ax.set_title("Equity Curve", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Equity ($)", fontsize=12)
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        # Rotate date labels
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            return None

        # Return as bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return buf.read()

    @staticmethod
    def plot_drawdown(
        equity_curve: pd.DataFrame,
        output_path: Path | None = None,
    ) -> bytes | None:
        """Plot drawdown over time.

        Args:
            equity_curve: DataFrame with 'timestamp' and 'drawdown' columns
            output_path: Optional path to save the plot

        Returns:
            PNG image bytes if output_path is None, otherwise None
        """
        _fig, ax = plt.subplots(figsize=(12, 4))

        ax.fill_between(
            equity_curve["timestamp"],
            equity_curve["drawdown"] * 100,
            0,
            alpha=0.3,
            color="red",
            label="Drawdown",
        )

        ax.set_title("Drawdown Over Time", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Drawdown (%)", fontsize=12)
        ax.legend(loc="lower left")
        ax.grid(True, alpha=0.3)

        # Rotate date labels
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            return None

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return buf.read()

    @staticmethod
    def plot_returns_distribution(
        trades: list[dict[str, Any]],
        output_path: Path | None = None,
    ) -> bytes | None:
        """Plot distribution of trade returns.

        Args:
            trades: List of trade dictionaries
            output_path: Optional path to save the plot

        Returns:
            PNG image bytes if output_path is None, otherwise None
        """
        pnls = [float(t["pnl"]) for t in trades]

        _fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(pnls, bins=50, alpha=0.7, color="steelblue", edgecolor="black")

        ax.set_title("Trade Returns Distribution", fontsize=14, fontweight="bold")
        ax.set_xlabel("PnL ($)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.axvline(0, color="red", linestyle="--", linewidth=2, label="Break-even")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            return None

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return buf.read()

    @staticmethod
    def generate_markdown_report(
        metrics: PerformanceMetrics,
        strategy_name: str,
        symbols: list[str],
        output_path: Path,
    ) -> None:
        """Generate a Markdown backtest report.

        Args:
            metrics: Performance metrics
            strategy_name: Name of the strategy
            symbols: List of symbols traded
            output_path: Path to save the report
        """
        report = f"""# Backtest Report: {strategy_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Strategy Configuration

- **Strategy:** {strategy_name}
- **Symbols:** {", ".join(symbols)}
- **Period:** {metrics.start_date.strftime("%Y-%m-%d")} to {metrics.end_date.strftime("%Y-%m-%d")}
- **Duration:** {metrics.duration_days} days

## Performance Summary

| Metric | Value |
|--------|-------|
| Total Return | {metrics.total_return_pct:.2f}% |
| Annualized Return | {metrics.annualized_return_pct:.2f}% |
| CAGR | {metrics.cagr_pct:.2f}% |
| Sharpe Ratio | {metrics.sharpe_ratio:.2f} |
| Sortino Ratio | {metrics.sortino_ratio:.2f} |
| Calmar Ratio | {metrics.calmar_ratio:.2f} |
| Max Drawdown | {metrics.max_drawdown_pct:.2f}% |
| Volatility (Ann.) | {metrics.volatility_annualized_pct:.2f}% |

## Trade Statistics

| Metric | Value |
|--------|-------|
| Total Trades | {metrics.total_trades} |
| Winning Trades | {metrics.winning_trades} ({metrics.win_rate_pct:.1f}%) |
| Losing Trades | {metrics.losing_trades} ({100-metrics.win_rate_pct:.1f}%) |
| Profit Factor | {metrics.profit_factor:.2f} |
| Average Win | ${metrics.avg_win:.2f} |
| Average Loss | ${metrics.avg_loss:.2f} |
| Average Trade | ${metrics.avg_trade:.2f} |
| Largest Win | ${metrics.largest_win:.2f} |
| Largest Loss | ${metrics.largest_loss:.2f} |
| Expectancy | ${metrics.expectancy:.2f} |
| Risk/Reward Ratio | {metrics.avg_risk_reward_ratio:.2f} |

## Risk Metrics

| Metric | Value |
|--------|-------|
| Final Equity | ${metrics.final_equity:,.2f} |
| Peak Equity | ${metrics.peak_equity:,.2f} |
| Max Consecutive Wins | {metrics.max_consecutive_wins} |
| Max Consecutive Losses | {metrics.max_consecutive_losses} |
| Max Drawdown Duration | {metrics.max_drawdown_duration_days} days |

---

*Report generated by ZenMarket AI Backtesting Engine*
"""

        output_path.write_text(report)

    @staticmethod
    def generate_pdf_report(
        metrics: PerformanceMetrics,
        strategy_name: str,
        symbols: list[str],
        equity_curve: pd.DataFrame,
        trades: list[dict[str, Any]],
        output_path: Path,
    ) -> None:
        """Generate a comprehensive PDF backtest report.

        Args:
            metrics: Performance metrics
            strategy_name: Name of the strategy
            symbols: List of symbols traded
            equity_curve: DataFrame with equity curve data
            trades: List of trade dictionaries
            output_path: Path to save the PDF report
        """
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=24,
            textColor=colors.HexColor("#2C3E50"),
        )
        story.append(Paragraph(f"Backtest Report: {strategy_name}", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # Metadata
        story.append(
            Paragraph(
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        story.append(Paragraph(f"<b>Symbols:</b> {', '.join(symbols)}", styles["Normal"]))
        story.append(
            Paragraph(
                f"<b>Period:</b> {metrics.start_date.strftime('%Y-%m-%d')} to {metrics.end_date.strftime('%Y-%m-%d')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Performance Summary Table
        story.append(Paragraph("<b>Performance Summary</b>", styles["Heading2"]))
        perf_data = [
            ["Metric", "Value"],
            ["Total Return", f"{metrics.total_return_pct:.2f}%"],
            ["Annualized Return", f"{metrics.annualized_return_pct:.2f}%"],
            ["Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}"],
            ["Sortino Ratio", f"{metrics.sortino_ratio:.2f}"],
            ["Max Drawdown", f"{metrics.max_drawdown_pct:.2f}%"],
            ["Volatility (Ann.)", f"{metrics.volatility_annualized_pct:.2f}%"],
        ]
        perf_table = Table(perf_data, colWidths=[3 * inch, 2 * inch])
        perf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(perf_table)
        story.append(Spacer(1, 0.3 * inch))

        # Trade Statistics
        story.append(Paragraph("<b>Trade Statistics</b>", styles["Heading2"]))
        trade_data = [
            ["Metric", "Value"],
            ["Total Trades", str(metrics.total_trades)],
            ["Win Rate", f"{metrics.win_rate_pct:.1f}%"],
            ["Profit Factor", f"{metrics.profit_factor:.2f}"],
            ["Average Trade", f"${metrics.avg_trade:.2f}"],
            ["Expectancy", f"${metrics.expectancy:.2f}"],
        ]
        trade_table = Table(trade_data, colWidths=[3 * inch, 2 * inch])
        trade_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(trade_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(
            Paragraph(
                "<i>Report generated by ZenMarket AI Backtesting Engine</i>",
                styles["Normal"],
            )
        )

        # Build PDF
        doc.build(story)

    @staticmethod
    def print_summary(metrics: PerformanceMetrics, strategy_name: str) -> None:
        """Print a summary of the backtest results to console.

        Args:
            metrics: Performance metrics
            strategy_name: Name of the strategy
        """

        # Performance Summary

        # Trade Statistics
        [
            ["Total Trades", metrics.total_trades],
            ["Winning Trades", f"{metrics.winning_trades} ({metrics.win_rate_pct:.1f}%)"],
            ["Losing Trades", f"{metrics.losing_trades} ({100-metrics.win_rate_pct:.1f}%)"],
            ["Profit Factor", f"{metrics.profit_factor:.2f}"],
            ["Average Win", f"${metrics.avg_win:.2f}"],
            ["Average Loss", f"${metrics.avg_loss:.2f}"],
            ["Average Trade", f"${metrics.avg_trade:.2f}"],
            ["Largest Win", f"${metrics.largest_win:.2f}"],
            ["Largest Loss", f"${metrics.largest_loss:.2f}"],
            ["Expectancy", f"${metrics.expectancy:.2f}"],
            ["Risk/Reward Ratio", f"{metrics.avg_risk_reward_ratio:.2f}"],
        ]

        # Risk Metrics
