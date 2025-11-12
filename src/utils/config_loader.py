"""
Configuration loader for ZenMarket AI.
Handles environment variables and application settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Central configuration manager for ZenMarket AI."""

    def __init__(self, env_file: str | None = None) -> None:
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file. If None, looks in project root.
        """
        if env_file is None:
            # Look for .env in project root
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / ".env"

        if os.path.exists(env_file):
            load_dotenv(env_file)

        self._load_config()

    def _load_config(self) -> None:
        """Load all configuration from environment variables."""

        # === API Keys ===
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.newsapi_endpoint = os.getenv("NEWSAPI_ENDPOINT", "https://newsapi.org/v2")

        self.alphavantage_key = os.getenv("ALPHAVANTAGE_KEY", "")
        self.finnhub_key = os.getenv("FINNHUB_KEY", "")

        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        self.ai_provider = os.getenv("AI_PROVIDER", "openai").lower()

        # === Telegram ===
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        # === Email ===
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_recipient = os.getenv("EMAIL_RECIPIENT", "")

        # === Application Settings ===
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.report_output_dir = Path(os.getenv("REPORT_OUTPUT_DIR", "./reports"))
        self.data_cache_dir = Path(os.getenv("DATA_CACHE_DIR", "./data"))
        self.timezone = os.getenv("TIMEZONE", "Europe/Paris")

        # === Market Configuration ===
        indices_str = os.getenv("MARKET_INDICES", "^GDAXI,^IXIC,^GSPC,EURUSD=X,BTC-USD")
        self.market_indices = [idx.strip() for idx in indices_str.split(",")]

        # === News Configuration ===
        self.news_lookback_hours = int(os.getenv("NEWS_LOOKBACK_HOURS", "24"))
        self.news_max_articles = int(os.getenv("NEWS_MAX_ARTICLES", "50"))
        self.news_language = os.getenv("NEWS_LANGUAGE", "en")

        # === Report Configuration ===
        formats_str = os.getenv("REPORT_FORMATS", "markdown,html,pdf")
        self.report_formats = [fmt.strip() for fmt in formats_str.split(",")]
        self.report_include_charts = os.getenv("REPORT_INCLUDE_CHARTS", "true").lower() == "true"
        self.report_chart_style = os.getenv("REPORT_CHART_STYLE", "seaborn")

        # Create directories if they don't exist
        self.report_output_dir.mkdir(parents=True, exist_ok=True)
        self.data_cache_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """
        Validate that required configuration is present.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required API keys
        if self.ai_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER=openai")

        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")

        if not self.newsapi_key:
            errors.append("NEWSAPI_KEY is required for news fetching")

        return errors

    def get_api_key(self, service: str) -> str:
        """
        Get API key for a specific service.

        Args:
            service: Service name (newsapi, alphavantage, etc.)

        Returns:
            API key string
        """
        service_map = {
            "newsapi": self.newsapi_key,
            "alphavantage": self.alphavantage_key,
            "finnhub": self.finnhub_key,
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
        }
        return service_map.get(service, "")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "ai_provider": self.ai_provider,
            "log_level": self.log_level,
            "timezone": self.timezone,
            "market_indices": self.market_indices,
            "news_lookback_hours": self.news_lookback_hours,
            "report_formats": self.report_formats,
            "report_include_charts": self.report_include_charts,
        }


# Global configuration instance
_config: Config | None = None


def get_config(reload: bool = False) -> Config:
    """
    Get global configuration instance.

    Args:
        reload: Force reload configuration

    Returns:
        Config instance
    """
    global _config
    if _config is None or reload:
        _config = Config()
    return _config
