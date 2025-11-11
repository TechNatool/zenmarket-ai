"""
Report generator for ZenMarket AI.
Creates beautiful financial reports in multiple formats (Markdown, HTML, PDF).
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import seaborn as sns

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.date_utils import format_friendly_date

logger = get_logger(__name__)


class ReportGenerator:
    """Generates comprehensive financial reports."""

    def __init__(self):
        """Initialize report generator."""
        self.config = get_config()
        self.report_dir = self.config.report_output_dir

        # Set plot style
        if self.config.report_chart_style == "seaborn":
            sns.set_theme(style="darkgrid")
        else:
            plt.style.use('default')

    def generate_report(
        self,
        news_articles: List[Dict],
        market_snapshots: Dict,
        sentiment_data: Dict,
        ai_insights: str,
        recommendations: List[str],
        report_date: Optional[datetime] = None
    ) -> Dict[str, Path]:
        """
        Generate complete report in all configured formats.

        Args:
            news_articles: List of news article dicts
            market_snapshots: Dictionary of market snapshots
            sentiment_data: Sentiment analysis data
            ai_insights: AI-generated insights
            recommendations: List of recommendations
            report_date: Report date (default: now)

        Returns:
            Dictionary of format: file_path
        """
        from ..utils.date_utils import now

        if report_date is None:
            report_date = now(self.config.timezone)

        logger.info(f"Generating report for {report_date.strftime('%Y-%m-%d')}")

        # Generate filename
        date_str = report_date.strftime("%Y-%m-%d")
        base_filename = f"zenmarket_report_{date_str}"

        # Generate content
        markdown_content = self._generate_markdown(
            news_articles,
            market_snapshots,
            sentiment_data,
            ai_insights,
            recommendations,
            report_date
        )

        # Generate charts if enabled
        chart_files = {}
        if self.config.report_include_charts:
            chart_files = self._generate_charts(market_snapshots, base_filename)

        # Save in requested formats
        output_files = {}

        for fmt in self.config.report_formats:
            if fmt == "markdown":
                file_path = self._save_markdown(markdown_content, base_filename)
                output_files["markdown"] = file_path

            elif fmt == "html":
                file_path = self._save_html(markdown_content, base_filename, chart_files)
                output_files["html"] = file_path

            elif fmt == "pdf":
                file_path = self._save_pdf(markdown_content, base_filename, chart_files)
                output_files["pdf"] = file_path

        logger.info(f"Report generated successfully: {', '.join(output_files.keys())}")
        return output_files

    def _generate_markdown(
        self,
        news_articles: List[Dict],
        market_snapshots: Dict,
        sentiment_data: Dict,
        ai_insights: str,
        recommendations: List[str],
        report_date: datetime
    ) -> str:
        """Generate Markdown content."""

        date_formatted = format_friendly_date(report_date)

        # Header
        md = f"""# ZenMarket AI — Daily Financial Brief

📅 **Date:** {date_formatted}

---

## 📊 Executive Summary

{ai_insights}

**Overall Market Sentiment:** {sentiment_data.get('overall_sentiment', 'neutral').upper()}
({sentiment_data.get('overall_score', 0.0):.2f})

---

## 📰 Top News Headlines

"""

        # Top news (limit to 5-7)
        top_news = news_articles[:7]
        for i, article in enumerate(top_news, 1):
            impact_emoji = self._get_sentiment_emoji(article.get('sentiment', 'neutral'))
            md += f"""### {i}. {article.get('title', 'N/A')}

**Source:** {article.get('source', 'Unknown')} | **Sentiment:** {impact_emoji} {article.get('sentiment', 'neutral').title()}

{article.get('summary', article.get('description', 'No summary available.'))}

[Read more]({article.get('url', '#')})

---

"""

        # Market overview table
        md += """## 📈 Market Overview

| Index/Asset | Last Price | Change | Change % | Trend | Volatility |
|-------------|------------|--------|----------|-------|------------|
"""

        for ticker, snapshot in market_snapshots.items():
            trend_emoji = self._get_trend_emoji(snapshot.get('trend', 'neutral'))
            change_emoji = "📈" if snapshot.get('change_percent', 0) > 0 else "📉" if snapshot.get('change_percent', 0) < 0 else "➖"

            md += f"| {snapshot.get('name', ticker)} | {snapshot.get('last_price', 0):.2f} | "
            md += f"{snapshot.get('change', 0):+.2f} | "
            md += f"{change_emoji} {snapshot.get('change_percent', 0):+.2f}% | "
            md += f"{trend_emoji} {snapshot.get('trend', 'neutral').title()} | "
            md += f"{snapshot.get('volatility', 0):.1f}% |\n"

        md += "\n---\n\n"

        # Sentiment distribution
        md += """## 💬 Sentiment Analysis

"""
        distribution = sentiment_data.get('distribution', {})
        total = sum(distribution.values())

        if total > 0:
            for sentiment, count in distribution.items():
                percentage = (count / total) * 100
                emoji = self._get_sentiment_emoji(sentiment)
                bar = "█" * int(percentage / 5)
                md += f"{emoji} **{sentiment.title()}:** {count} articles ({percentage:.1f}%) {bar}\n\n"

        md += "---\n\n"

        # AI Insights
        md += f"""## 🤖 AI Market Insights

{ai_insights}

---

"""

        # Recommendations
        md += """## ⚠️ Key Points to Watch

"""
        for i, rec in enumerate(recommendations, 1):
            md += f"{i}. {rec}\n"

        md += "\n---\n\n"

        # Footer
        md += """## 📌 Disclaimer

*This report is generated automatically by ZenMarket AI for informational purposes only.
It does not constitute financial advice. Always conduct your own research and consult
with a qualified financial advisor before making investment decisions.*

---

✅ **Report generated automatically by ZenMarket AI**
🤖 **Powered by advanced AI and real-time market data**

"""

        return md

    def _save_markdown(self, content: str, base_filename: str) -> Path:
        """Save Markdown file."""
        file_path = self.report_dir / f"{base_filename}.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Markdown report saved: {file_path}")
        return file_path

    def _save_html(
        self,
        markdown_content: str,
        base_filename: str,
        chart_files: Dict
    ) -> Path:
        """Convert Markdown to HTML and save."""
        try:
            import markdown2

            # Convert markdown to HTML
            html_body = markdown2.markdown(
                markdown_content,
                extras=["tables", "fenced-code-blocks"]
            )

            # Wrap in HTML template
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZenMarket AI - Daily Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 30px;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        a {{
            color: #4CAF50;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>
"""

            file_path = self.report_dir / f"{base_filename}.html"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"HTML report saved: {file_path}")
            return file_path

        except ImportError:
            logger.error("markdown2 not installed. Skipping HTML generation.")
            return None
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            return None

    def _save_pdf(
        self,
        markdown_content: str,
        base_filename: str,
        chart_files: Dict
    ) -> Path:
        """Generate PDF from Markdown."""
        try:
            import markdown2
            from weasyprint import HTML

            # Convert markdown to HTML
            html_body = markdown2.markdown(
                markdown_content,
                extras=["tables", "fenced-code-blocks"]
            )

            # Create styled HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 20px;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
"""

            file_path = self.report_dir / f"{base_filename}.pdf"

            # Generate PDF
            HTML(string=html_content).write_pdf(file_path)

            logger.info(f"PDF report saved: {file_path}")
            return file_path

        except ImportError as e:
            logger.error(f"Required library not installed for PDF generation: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return None

    def _generate_charts(
        self,
        market_snapshots: Dict,
        base_filename: str
    ) -> Dict[str, Path]:
        """Generate market charts."""
        chart_files = {}

        try:
            # Chart 1: Market performance bar chart
            chart_path = self._create_performance_chart(market_snapshots, base_filename)
            if chart_path:
                chart_files['performance'] = chart_path

            # Chart 2: Volatility comparison
            chart_path = self._create_volatility_chart(market_snapshots, base_filename)
            if chart_path:
                chart_files['volatility'] = chart_path

        except Exception as e:
            logger.error(f"Error generating charts: {e}")

        return chart_files

    def _create_performance_chart(
        self,
        market_snapshots: Dict,
        base_filename: str
    ) -> Optional[Path]:
        """Create market performance bar chart."""
        try:
            names = []
            changes = []
            colors = []

            for ticker, snapshot in market_snapshots.items():
                names.append(snapshot.get('name', ticker))
                change_pct = snapshot.get('change_percent', 0)
                changes.append(change_pct)
                colors.append('#4CAF50' if change_pct >= 0 else '#F44336')

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(names, changes, color=colors)

            ax.set_xlabel('Change (%)', fontsize=12)
            ax.set_title('Market Performance', fontsize=14, fontweight='bold')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax.grid(axis='x', alpha=0.3)

            # Add value labels
            for i, (bar, change) in enumerate(zip(bars, changes)):
                ax.text(
                    change,
                    i,
                    f' {change:+.2f}%',
                    va='center',
                    ha='left' if change >= 0 else 'right',
                    fontsize=10
                )

            plt.tight_layout()

            chart_path = self.report_dir / f"{base_filename}_performance.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Performance chart saved: {chart_path}")
            return chart_path

        except Exception as e:
            logger.error(f"Error creating performance chart: {e}")
            plt.close()
            return None

    def _create_volatility_chart(
        self,
        market_snapshots: Dict,
        base_filename: str
    ) -> Optional[Path]:
        """Create volatility comparison chart."""
        try:
            names = []
            volatilities = []

            for ticker, snapshot in market_snapshots.items():
                vol = snapshot.get('volatility')
                if vol is not None:
                    names.append(snapshot.get('name', ticker))
                    volatilities.append(vol)

            if not names:
                return None

            fig, ax = plt.subplots(figsize=(10, 6))

            # Color code by volatility level
            colors = ['#4CAF50' if v < 15 else '#FFC107' if v < 30 else '#F44336' for v in volatilities]

            bars = ax.bar(names, volatilities, color=colors)

            ax.set_ylabel('Volatility (%)', fontsize=12)
            ax.set_title('Market Volatility Comparison', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

            # Rotate x labels if needed
            plt.xticks(rotation=45, ha='right')

            # Add value labels
            for bar, vol in zip(bars, volatilities):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f'{vol:.1f}%',
                    ha='center',
                    va='bottom',
                    fontsize=9
                )

            plt.tight_layout()

            chart_path = self.report_dir / f"{base_filename}_volatility.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Volatility chart saved: {chart_path}")
            return chart_path

        except Exception as e:
            logger.error(f"Error creating volatility chart: {e}")
            plt.close()
            return None

    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji for sentiment."""
        emojis = {
            "positive": "🔺",
            "negative": "🔻",
            "neutral": "➖"
        }
        return emojis.get(sentiment.lower(), "➖")

    def _get_trend_emoji(self, trend: str) -> str:
        """Get emoji for trend."""
        emojis = {
            "bullish": "🔼",
            "bearish": "🔽",
            "neutral": "➡️"
        }
        return emojis.get(trend.lower(), "➡️")
