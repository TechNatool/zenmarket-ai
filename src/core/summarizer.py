"""
AI-powered summarizer for ZenMarket AI.
Generates summaries and insights using LLMs.
"""

from src.utils.config_loader import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AISummarizer:
    """AI-powered text summarizer and insight generator."""

    def __init__(self) -> None:
        """Initialize summarizer."""
        self.config = get_config()

    def summarize_article(self, title: str, content: str, max_words: int = 50) -> str:
        """
        Summarize a news article.

        Args:
            title: Article title
            content: Article content
            max_words: Maximum words in summary

        Returns:
            Summary string
        """
        try:
            if self.config.ai_provider == "openai":
                return self._summarize_with_openai(title, content, max_words)
            if self.config.ai_provider == "anthropic":
                return self._summarize_with_anthropic(title, content, max_words)
            # Fallback: truncate content
            words = content.split()[:max_words]
            return " ".join(words) + "..."

        except Exception as e:
            logger.exception(f"Error summarizing article: {e}")
            # Return truncated content as fallback
            words = content.split()[:max_words]
            return " ".join(words) + "..."

    def _summarize_with_openai(self, title: str, content: str, max_words: int) -> str:
        """Summarize with OpenAI."""
        import openai

        openai.api_key = self.config.openai_api_key

        prompt = f"""Summarize this financial news article in {max_words} words or less. Focus on the key market impact and implications for traders.

Title: {title}
Content: {content}

Summary:"""

        response = openai.chat.completions.create(
            model=self.config.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max_words * 2,
        )

        summary = response.choices[0].message.content.strip()
        logger.debug(f"Generated OpenAI summary: {summary[:100]}...")
        return summary

    def _summarize_with_anthropic(self, title: str, content: str, max_words: int) -> str:
        """Summarize with Anthropic Claude."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        prompt = f"""Summarize this financial news article in {max_words} words or less. Focus on the key market impact and implications for traders.

Title: {title}
Content: {content}

Summary:"""

        message = client.messages.create(
            model=self.config.anthropic_model,
            max_tokens=max_words * 2,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )

        summary = message.content[0].text.strip()
        logger.debug(f"Generated Claude summary: {summary[:100]}...")
        return summary

    def generate_market_insights(
        self, news_summaries: list[str], market_data: dict, sentiment_overall: str
    ) -> str:
        """
        Generate AI insights about current market conditions.

        Args:
            news_summaries: List of news summaries
            market_data: Dictionary of market snapshots
            sentiment_overall: Overall sentiment ("positive", "negative", "neutral")

        Returns:
            Insights text
        """
        try:
            # Prepare context
            news_context = "\n".join([f"- {summary}" for summary in news_summaries[:10]])

            market_context = "\n".join(
                [
                    f"- {data['name']}: {data['last_price']:.2f} ({data['change_percent']:+.2f}%)"
                    for ticker, data in list(market_data.items())[:5]
                ]
            )

            if self.config.ai_provider == "openai":
                return self._generate_insights_openai(
                    news_context, market_context, sentiment_overall
                )
            if self.config.ai_provider == "anthropic":
                return self._generate_insights_anthropic(
                    news_context, market_context, sentiment_overall
                )
            return self._generate_fallback_insights(sentiment_overall)

        except Exception as e:
            logger.exception(f"Error generating insights: {e}")
            return self._generate_fallback_insights(sentiment_overall)

    def _generate_insights_openai(
        self, news_context: str, market_context: str, sentiment: str
    ) -> str:
        """Generate insights with OpenAI."""
        import openai

        openai.api_key = self.config.openai_api_key

        prompt = f"""You are a professional financial analyst. Based on the following information, provide a brief market insight (2-3 sentences) for traders.

News highlights:
{news_context}

Market performance:
{market_context}

Overall sentiment: {sentiment}

Provide concise, actionable insights:"""

        response = openai.chat.completions.create(
            model=self.config.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200,
        )

        insights = response.choices[0].message.content.strip()
        logger.info("Generated market insights with OpenAI")
        return insights

    def _generate_insights_anthropic(
        self, news_context: str, market_context: str, sentiment: str
    ) -> str:
        """Generate insights with Anthropic Claude."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        prompt = f"""You are a professional financial analyst. Based on the following information, provide a brief market insight (2-3 sentences) for traders.

News highlights:
{news_context}

Market performance:
{market_context}

Overall sentiment: {sentiment}

Provide concise, actionable insights:"""

        message = client.messages.create(
            model=self.config.anthropic_model,
            max_tokens=200,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )

        insights = message.content[0].text.strip()
        logger.info("Generated market insights with Claude")
        return insights

    def _generate_fallback_insights(self, sentiment: str) -> str:
        """Generate basic insights without AI."""
        insights = {
            "positive": "Market sentiment appears optimistic based on recent news. Consider monitoring key support levels for potential entry points.",
            "negative": "Market sentiment shows concern. Exercise caution and consider defensive positions or wait for stabilization signals.",
            "neutral": "Markets show mixed signals. Maintain balanced positions and watch for clearer directional trends.",
        }

        return insights.get(sentiment, insights["neutral"])

    def categorize_news(self, articles: list[dict]) -> dict[str, list[dict]]:
        """
        Categorize news articles into themes.

        Args:
            articles: List of article dictionaries

        Returns:
            Dictionary of category: articles
        """
        categories = {
            "inflation": [],
            "interest_rates": [],
            "indices": [],
            "forex": [],
            "crypto": [],
            "earnings": [],
            "geopolitics": [],
            "other": [],
        }

        keywords = {
            "inflation": ["inflation", "cpi", "pce", "price"],
            "interest_rates": ["interest rate", "fed", "ecb", "central bank", "monetary policy"],
            "indices": ["nasdaq", "s&p", "dow", "dax", "ftse", "index"],
            "forex": ["forex", "dollar", "euro", "currency", "fx"],
            "crypto": ["bitcoin", "crypto", "ethereum", "blockchain"],
            "earnings": ["earnings", "revenue", "profit", "quarter", "q1", "q2", "q3", "q4"],
            "geopolitics": ["war", "conflict", "sanction", "trade", "tariff", "politics"],
        }

        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            categorized = False

            for category, category_keywords in keywords.items():
                if any(kw in text for kw in category_keywords):
                    categories[category].append(article)
                    categorized = True
                    break

            if not categorized:
                categories["other"].append(article)

        # Log distribution
        for category, items in categories.items():
            if items:
                logger.info(f"Category '{category}': {len(items)} articles")

        return categories

    def generate_recommendations(
        self, market_data: dict, sentiment: str, news_categories: dict
    ) -> list[str]:
        """
        Generate trading recommendations or watchpoints.

        Args:
            market_data: Market snapshots
            sentiment: Overall sentiment
            news_categories: Categorized news

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Based on sentiment
        if sentiment == "positive":
            recommendations.append(
                "Markets showing positive momentum. Consider long positions on major indices."
            )
        elif sentiment == "negative":
            recommendations.append(
                "Defensive positioning recommended. Consider hedging strategies or cash positions."
            )

        # Based on volatility
        high_vol_markets = [
            ticker
            for ticker, data in market_data.items()
            if data.get("volatility") and data["volatility"] > 25
        ]

        if high_vol_markets:
            recommendations.append(
                f"High volatility detected in {', '.join(high_vol_markets[:3])}. "
                "Use tight stop-losses and reduce position sizes."
            )

        # Based on news categories
        if news_categories.get("interest_rates"):
            recommendations.append(
                "Central bank policy in focus. Monitor rate-sensitive sectors (financials, real estate)."
            )

        if news_categories.get("earnings"):
            recommendations.append(
                "Earnings season active. Watch for guidance revisions and sector rotation opportunities."
            )

        if news_categories.get("geopolitics"):
            recommendations.append(
                "Geopolitical risks elevated. Consider safe-haven assets (gold, treasuries)."
            )

        # Default if no specific recommendations
        if not recommendations:
            recommendations.append(
                "No major catalysts detected. Maintain current positions and monitor for developments."
            )

        return recommendations[:5]  # Limit to 5 recommendations
