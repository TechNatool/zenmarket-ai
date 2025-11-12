"""
AI Trading Advisor Report Generator.
Creates comprehensive trading reports with technical analysis and AI insights.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

from src.utils.config_loader import get_config
from src.utils.date_utils import format_friendly_date, now
from src.utils.logger import get_logger

from .indicators import IndicatorCalculator
from .plotter import TechnicalChartPlotter
from .signal_generator import SignalGenerator, SignalType, TradingSignal

logger = get_logger(__name__)


class AdvisorReportGenerator:
    """Generates AI Trading Advisor reports."""

    def __init__(self) -> None:
        """Initialize report generator."""
        self.config = get_config()
        self.calculator = IndicatorCalculator()
        self.signal_generator = SignalGenerator()
        self.plotter = TechnicalChartPlotter()

    def fetch_market_data(
        self, ticker: str, period: str = "3mo", interval: str = "1d"
    ) -> pd.DataFrame | None:
        """
        Fetch market data using yfinance.

        Args:
            ticker: Ticker symbol
            period: Data period
            interval: Data interval

        Returns:
            DataFrame or None
        """
        try:
            logger.info(f"Fetching data for {ticker}...")
            data = yf.download(ticker, period=period, interval=interval, progress=False)

            if data.empty:
                logger.warning(f"No data returned for {ticker}")
                return None

            logger.info(f"Fetched {len(data)} data points for {ticker}")
            return data

        except Exception as e:
            logger.exception(f"Error fetching data for {ticker}: {e}")
            return None

    def analyze_ticker(self, ticker: str) -> TradingSignal | None:
        """
        Perform complete analysis for a ticker.

        Args:
            ticker: Ticker symbol

        Returns:
            TradingSignal or None
        """
        try:
            # Fetch data
            df = self.fetch_market_data(ticker)
            if df is None:
                return None

            # Calculate indicators
            indicators = self.calculator.calculate_all_indicators(ticker, df)
            if indicators is None:
                return None

            # Generate signal
            signal = self.signal_generator.generate_signal(indicators)

            # Create chart
            self.plotter.plot_full_technical_chart(ticker, df, signal)

            return signal

        except Exception as e:
            logger.exception(f"Error analyzing {ticker}: {e}")
            return None

    def generate_ai_commentary(
        self, signals: list[TradingSignal], market_bias: str, bias_score: float
    ) -> str:
        """
        Generate AI commentary on trading signals.

        Args:
            signals: List of TradingSignal objects
            market_bias: Overall market bias
            bias_score: Bias score (-1 to 1)

        Returns:
            AI-generated commentary string
        """
        try:
            if self.config.ai_provider == "openai" and self.config.openai_api_key:
                return self._generate_commentary_openai(signals, market_bias, bias_score)
            if self.config.ai_provider == "anthropic" and self.config.anthropic_api_key:
                return self._generate_commentary_anthropic(signals, market_bias, bias_score)
            return self._generate_fallback_commentary(signals, market_bias, bias_score)

        except Exception as e:
            logger.exception(f"Error generating AI commentary: {e}")
            return self._generate_fallback_commentary(signals, market_bias, bias_score)

    def _generate_commentary_openai(
        self, signals: list[TradingSignal], market_bias: str, bias_score: float
    ) -> str:
        """Generate commentary using OpenAI."""
        import openai

        openai.api_key = self.config.openai_api_key

        # Prepare signal summary
        signal_summary = "\n".join(
            [
                f"- {s.ticker}: {s.signal.value} (RSI: {s.indicators.rsi:.1f}, "
                f"MA20: {s.indicators.ma_20:.2f}, MA50: {s.indicators.ma_50:.2f})"
                for s in signals
            ]
        )

        prompt = f"""Tu es un analyste financier professionnel. Rédige une analyse concise (2-3 phrases) basée sur ces signaux techniques:

Biais de marché global: {market_bias} (score: {bias_score:.2f})

Signaux:
{signal_summary}

Fournis une interprétation professionnelle et actionnable sans répéter les chiffres. Focus sur la tendance générale et les opportunités."""

        response = openai.chat.completions.create(
            model=self.config.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200,
        )

        commentary = response.choices[0].message.content.strip()
        logger.info("Generated AI commentary with OpenAI")
        return commentary

    def _generate_commentary_anthropic(
        self, signals: list[TradingSignal], market_bias: str, bias_score: float
    ) -> str:
        """Generate commentary using Anthropic Claude."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        signal_summary = "\n".join(
            [
                f"- {s.ticker}: {s.signal.value} (RSI: {s.indicators.rsi:.1f}, "
                f"MA20: {s.indicators.ma_20:.2f}, MA50: {s.indicators.ma_50:.2f})"
                for s in signals
            ]
        )

        prompt = f"""Tu es un analyste financier professionnel. Rédige une analyse concise (2-3 phrases) basée sur ces signaux techniques:

Biais de marché global: {market_bias} (score: {bias_score:.2f})

Signaux:
{signal_summary}

Fournis une interprétation professionnelle et actionnable sans répéter les chiffres. Focus sur la tendance générale et les opportunités."""

        message = client.messages.create(
            model=self.config.anthropic_model,
            max_tokens=200,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )

        commentary = message.content[0].text.strip()
        logger.info("Generated AI commentary with Claude")
        return commentary

    def _generate_fallback_commentary(
        self, signals: list[TradingSignal], market_bias: str, bias_score: float
    ) -> str:
        """Generate basic commentary without AI."""
        buy_count = sum(1 for s in signals if s.signal == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal == SignalType.SELL)

        if market_bias == "Haussier":
            base = "Les indicateurs techniques montrent une tendance haussière dominante."
        elif market_bias == "Baissier":
            base = "Les signaux techniques indiquent une pression baissière sur les marchés."
        else:
            base = "Les marchés affichent une consolidation avec des signaux mixtes."

        if buy_count > sell_count:
            detail = f" {buy_count} opportunités d'achat identifiées contre {sell_count} signaux de vente."
        elif sell_count > buy_count:
            detail = f" Prudence recommandée avec {sell_count} signaux de vente actifs."
        else:
            detail = " Approche équilibrée conseillée dans ce contexte incertain."

        return base + detail

    def generate_markdown_report(
        self, signals: list[TradingSignal], report_date: datetime | None = None
    ) -> str:
        """
        Generate Markdown report.

        Args:
            signals: List of TradingSignal objects
            report_date: Report date

        Returns:
            Markdown content
        """
        if report_date is None:
            report_date = now(self.config.timezone)

        date_formatted = format_friendly_date(report_date)

        # Market bias
        market_bias, bias_score = self.signal_generator.get_market_bias(signals)

        # AI commentary
        ai_commentary = self.generate_ai_commentary(signals, market_bias, bias_score)

        # Signal summary
        summary = self.signal_generator.get_signal_summary(signals)

        # Generate report
        md = f"""# ZenMarket AI — AI Trading Brief

📅 **Date:** {date_formatted}

---

## 📊 Vue d'ensemble

**Biais de marché:** {market_bias} ({bias_score:+.2f})

**Distribution des signaux:**
- 📈 Achat: {summary['buy']} ({summary['buy_pct']:.1f}%)
- 📉 Vente: {summary['sell']} ({summary['sell_pct']:.1f}%)
- ⚖️ Neutre: {summary['hold']} ({summary['hold_pct']:.1f}%)

**Confiance moyenne:** {summary['avg_confidence']:.2f}

---

## 📈 Signaux de Trading

| Actif | Tendance | RSI | MA20 | MA50 | Signal | Confiance | Commentaire |
|-------|----------|-----|------|------|--------|-----------|-------------|
"""

        for signal in signals:
            ind = signal.indicators
            emoji = signal.get_emoji()
            trend = signal.get_trend_description()

            # Short comment (first reason)
            comment = signal.reasons[0] if signal.reasons else "N/A"
            if len(comment) > 50:
                comment = comment[:47] + "..."

            md += f"| {ind.ticker} | {trend} | {ind.rsi:.1f} | {ind.ma_20:.2f} | {ind.ma_50:.2f} | "
            md += f"{emoji} {signal.signal.value} | {signal.confidence:.2f} | {comment} |\n"

        md += "\n---\n\n"

        # Detailed analysis per ticker
        md += "## 🔍 Analyse Détaillée\n\n"

        for signal in signals:
            ind = signal.indicators
            emoji = signal.get_emoji()

            md += f"### {emoji} {ind.ticker} — {signal.signal.value}\n\n"
            md += f"**Prix actuel:** {ind.current_price:.2f} | "
            md += f"**RSI:** {ind.rsi:.1f} | "
            md += f"**Confiance:** {signal.confidence:.0%}\n\n"

            md += "**Indicateurs techniques:**\n"
            md += f"- MA20: {ind.ma_20:.2f}\n"
            md += f"- MA50: {ind.ma_50:.2f}\n"
            md += f"- Bandes de Bollinger: [{ind.bb_lower:.2f} - {ind.bb_upper:.2f}]\n"
            md += f"- Position: {ind.current_price:.2f} vs BB Middle {ind.bb_middle:.2f}\n\n"

            md += "**Raisons du signal:**\n"
            for reason in signal.reasons:
                md += f"- {reason}\n"

            md += "\n---\n\n"

        # AI Commentary
        md += f"""## 💬 Analyse IA

> {ai_commentary}

---

## ⚠️ Recommandations

"""

        # Generate recommendations based on signals
        if market_bias == "Haussier":
            md += "1. **Opportunités haussières:** Considérer des positions longues sur les actifs avec signal d'achat\n"
            md += "2. **Gestion du risque:** Placer des stop-loss sous les supports récents\n"
        elif market_bias == "Baissier":
            md += "1. **Protection du capital:** Privilégier les positions défensives ou cash\n"
            md += "2. **Opportunités courtes:** Surveiller les rebonds techniques pour positions vendeuses\n"
        else:
            md += "1. **Approche prudente:** Attendre des signaux directionnels plus clairs\n"
            md += "2. **Trading range:** Exploiter les oscillations entre supports et résistances\n"

        md += "3. **Surveillance des RSI:** Attention aux zones de surachat/survente extrêmes\n"
        md += "4. **Confirmation volume:** Valider les mouvements avec le volume\n"
        md += "5. **Actualités:** Rester attentif aux annonces économiques et corporate\n"

        md += "\n---\n\n"

        # Disclaimer
        md += """## 📌 Disclaimer

*Ce rapport est généré automatiquement par ZenMarket AI à des fins informatives uniquement.
Les signaux techniques ne constituent pas des conseils en investissement. Effectuez toujours
vos propres analyses et consultez un conseiller financier qualifié.*

**Méthodologie:**
- Indicateurs: MA20/50, RSI(14), Bandes de Bollinger(20)
- Signaux basés sur croisements de moyennes mobiles et niveaux RSI
- Analyse complémentaire via IA pour contexte global

---

✅ **Rapport généré automatiquement par ZenMarket AI Trading Advisor**
🤖 **Powered by advanced technical analysis and AI**

"""

        return md

    def save_report(self, content: str, filename: str | None = None) -> Path:
        """
        Save report to file.

        Args:
            content: Report content
            filename: Output filename

        Returns:
            Path to saved file
        """
        if filename is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"trading_brief_{date_str}.md"

        filepath = self.config.report_output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Report saved: {filepath}")
        return filepath

    def generate_full_report(
        self, tickers: list[str] | None = None, generate_charts: bool = True
    ) -> dict:
        """
        Generate complete trading advisor report.

        Args:
            tickers: List of tickers to analyze
            generate_charts: Whether to generate charts

        Returns:
            Dictionary with report info
        """
        logger.info("=" * 70)
        logger.info("ZenMarket AI - Trading Advisor Report Generation")
        logger.info("=" * 70)

        if tickers is None:
            tickers = self.config.market_indices

        logger.info(f"Analyzing {len(tickers)} tickers: {', '.join(tickers)}")

        # Analyze all tickers
        signals = []
        for ticker in tickers:
            signal = self.analyze_ticker(ticker)
            if signal:
                signals.append(signal)

        if not signals:
            logger.error("No signals generated")
            return {"success": False, "error": "No signals generated"}

        logger.info(f"Generated {len(signals)} signals")

        # Generate overview charts
        if generate_charts:
            self.plotter.plot_signals_overview(signals)
            self.plotter.plot_rsi_heatmap(signals)

        # Generate report
        report_content = self.generate_markdown_report(signals)
        report_path = self.save_report(report_content)

        # Summary
        summary = self.signal_generator.get_signal_summary(signals)
        market_bias, bias_score = self.signal_generator.get_market_bias(signals)

        logger.info("=" * 70)
        logger.info("Report generation complete!")
        logger.info(f"Market bias: {market_bias} ({bias_score:+.2f})")
        logger.info(
            f"Signals: {summary['buy']} BUY, {summary['sell']} SELL, {summary['hold']} HOLD"
        )
        logger.info(f"Report: {report_path}")
        logger.info("=" * 70)

        return {
            "success": True,
            "report_path": report_path,
            "signals": signals,
            "market_bias": market_bias,
            "bias_score": bias_score,
            "summary": summary,
        }


# Import pandas at the top
