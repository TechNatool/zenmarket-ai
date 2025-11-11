"""
News fetcher module for ZenMarket AI.
Retrieves financial news from multiple sources: NewsAPI, RSS feeds, etc.
"""

import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import time

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.date_utils import now, get_lookback_time

logger = get_logger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles."""

    title: str
    description: str
    source: str
    url: str
    published_at: datetime
    author: Optional[str] = None
    category: Optional[str] = None
    sentiment: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['published_at'] = self.published_at.isoformat()
        return data


class NewsFetcher:
    """Fetches financial news from multiple sources."""

    # RSS feeds for financial news
    RSS_FEEDS = {
        "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
        "investing_general": "https://www.investing.com/rss/news.rss",
        "investing_forex": "https://www.investing.com/rss/news_301.rss",
        "investing_crypto": "https://www.investing.com/rss/news_301.rss",
        "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "marketwatch": "https://www.marketwatch.com/rss/topstories",
    }

    # NewsAPI categories for financial news
    NEWSAPI_CATEGORIES = ["business", "technology"]

    # Keywords for filtering relevant financial news
    FINANCIAL_KEYWORDS = [
        "stock", "market", "trading", "economy", "fed", "ecb", "inflation",
        "interest rate", "dollar", "euro", "bitcoin", "crypto", "nasdaq",
        "dow", "s&p", "dax", "ftse", "earnings", "revenue", "profit",
        "gdp", "unemployment", "central bank", "fiscal", "monetary"
    ]

    def __init__(self):
        """Initialize news fetcher with configuration."""
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ZenMarket-AI/1.0'
        })

    def fetch_from_newsapi(
        self,
        lookback_hours: Optional[int] = None,
        max_articles: Optional[int] = None
    ) -> List[NewsArticle]:
        """
        Fetch news from NewsAPI.org.

        Args:
            lookback_hours: Hours to look back. If None, uses config.
            max_articles: Maximum articles to fetch. If None, uses config.

        Returns:
            List of NewsArticle objects
        """
        if not self.config.newsapi_key:
            logger.warning("NewsAPI key not configured, skipping NewsAPI")
            return []

        lookback_hours = lookback_hours or self.config.news_lookback_hours
        max_articles = max_articles or self.config.news_max_articles

        from_date = get_lookback_time(lookback_hours)
        from_str = from_date.strftime("%Y-%m-%dT%H:%M:%S")

        articles = []

        # Query with financial keywords
        query = " OR ".join(self.FINANCIAL_KEYWORDS[:5])  # Limit to avoid too long query

        try:
            url = f"{self.config.newsapi_endpoint}/everything"
            params = {
                "q": query,
                "from": from_str,
                "sortBy": "publishedAt",
                "language": self.config.news_language,
                "pageSize": min(max_articles, 100),
                "apiKey": self.config.newsapi_key,
            }

            logger.info(f"Fetching news from NewsAPI (from {from_str})")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "ok":
                for item in data.get("articles", []):
                    try:
                        article = NewsArticle(
                            title=item.get("title", ""),
                            description=item.get("description", ""),
                            source=item.get("source", {}).get("name", "Unknown"),
                            url=item.get("url", ""),
                            published_at=datetime.fromisoformat(
                                item.get("publishedAt", "").replace("Z", "+00:00")
                            ),
                            author=item.get("author"),
                        )
                        articles.append(article)
                    except Exception as e:
                        logger.warning(f"Error parsing NewsAPI article: {e}")
                        continue

                logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from NewsAPI: {e}")

        return articles

    def fetch_from_rss(
        self,
        feeds: Optional[Dict[str, str]] = None,
        lookback_hours: Optional[int] = None
    ) -> List[NewsArticle]:
        """
        Fetch news from RSS feeds.

        Args:
            feeds: Dictionary of feed_name: feed_url. If None, uses default feeds.
            lookback_hours: Hours to look back. If None, uses config.

        Returns:
            List of NewsArticle objects
        """
        feeds = feeds or self.RSS_FEEDS
        lookback_hours = lookback_hours or self.config.news_lookback_hours

        cutoff_time = get_lookback_time(lookback_hours)
        articles = []

        for feed_name, feed_url in feeds.items():
            try:
                logger.info(f"Fetching RSS feed: {feed_name}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    try:
                        # Parse publication date
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            pub_date = datetime(*entry.updated_parsed[:6])
                        else:
                            pub_date = now()

                        # Filter by date
                        if pub_date < cutoff_time:
                            continue

                        article = NewsArticle(
                            title=entry.get("title", ""),
                            description=entry.get("summary", entry.get("description", "")),
                            source=feed_name,
                            url=entry.get("link", ""),
                            published_at=pub_date,
                            author=entry.get("author"),
                        )
                        articles.append(article)

                    except Exception as e:
                        logger.warning(f"Error parsing RSS entry from {feed_name}: {e}")
                        continue

                logger.info(f"Fetched {len([a for a in articles if a.source == feed_name])} articles from {feed_name}")

            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_name}: {e}")
                continue

        return articles

    def filter_relevant(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Filter articles to keep only financially relevant ones.

        Args:
            articles: List of articles to filter

        Returns:
            Filtered list of articles
        """
        relevant = []

        for article in articles:
            text = f"{article.title} {article.description}".lower()

            # Check if any financial keyword is present
            if any(keyword.lower() in text for keyword in self.FINANCIAL_KEYWORDS):
                relevant.append(article)

        logger.info(f"Filtered {len(relevant)}/{len(articles)} relevant articles")
        return relevant

    def deduplicate(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles based on title similarity.

        Args:
            articles: List of articles

        Returns:
            Deduplicated list
        """
        seen_titles = set()
        unique = []

        for article in articles:
            # Normalize title for comparison
            normalized = article.title.lower().strip()

            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(article)

        logger.info(f"Removed {len(articles) - len(unique)} duplicate articles")
        return unique

    def fetch_all(
        self,
        use_newsapi: bool = True,
        use_rss: bool = True,
        filter_relevant: bool = True,
        deduplicate: bool = True
    ) -> List[NewsArticle]:
        """
        Fetch news from all sources.

        Args:
            use_newsapi: Whether to fetch from NewsAPI
            use_rss: Whether to fetch from RSS feeds
            filter_relevant: Whether to filter by financial relevance
            deduplicate: Whether to remove duplicates

        Returns:
            Combined list of articles
        """
        logger.info("Starting news fetch from all sources")

        articles = []

        if use_newsapi:
            newsapi_articles = self.fetch_from_newsapi()
            articles.extend(newsapi_articles)

        if use_rss:
            rss_articles = self.fetch_from_rss()
            articles.extend(rss_articles)

        logger.info(f"Total articles fetched: {len(articles)}")

        if filter_relevant:
            articles = self.filter_relevant(articles)

        if deduplicate:
            articles = self.deduplicate(articles)

        # Sort by publication date (newest first)
        articles.sort(key=lambda x: x.published_at, reverse=True)

        logger.info(f"Final article count: {len(articles)}")
        return articles
