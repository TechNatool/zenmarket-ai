# Usage Guide

Comprehensive guide for using ZenMarket AI.

## Basic Usage

### Generating a Report

```bash
# Navigate to project directory
cd zenmarket-ai

# Activate virtual environment
source venv/bin/activate

# Generate report with default settings
python -m src.main
```

This will:
1. Fetch news from the last 24 hours
2. Get current market data
3. Analyze sentiment
4. Generate AI insights
5. Create reports in all configured formats (Markdown, HTML, PDF)

Reports are saved in the `reports/` directory with timestamp.

## Command-Line Options

### Format Selection

Generate specific formats only:

```bash
# Markdown only (fastest)
python -m src.main --format markdown

# PDF and HTML
python -m src.main --format pdf html

# All formats (default)
python -m src.main --format markdown html pdf
```

### AI Settings

```bash
# Disable AI (faster, lower cost)
python -m src.main --no-ai

# Use AI (default, requires API keys)
python -m src.main
```

### Logging Level

```bash
# Normal output
python -m src.main --log-level INFO

# Detailed debug information
python -m src.main --log-level DEBUG

# Minimal output (warnings and errors only)
python -m src.main --log-level WARNING
```

### Combined Options

```bash
# Fast report without AI, Markdown only, debug mode
python -m src.main --no-ai --format markdown --log-level DEBUG
```

## Configuration

### Environment Variables

All settings are in `.env` file. Key options:

```env
# === Core Settings ===
AI_PROVIDER=openai              # or: anthropic
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR

# === Market Configuration ===
MARKET_INDICES=^GDAXI,^IXIC,^GSPC,EURUSD=X,BTC-USD
TIMEZONE=Europe/Paris

# === News Settings ===
NEWS_LOOKBACK_HOURS=24          # Hours of news to fetch
NEWS_MAX_ARTICLES=50            # Maximum articles to process
NEWS_LANGUAGE=en                # Language code

# === Report Settings ===
REPORT_FORMATS=markdown,html,pdf
REPORT_INCLUDE_CHARTS=true
REPORT_CHART_STYLE=seaborn      # or: default
```

### Adding Custom Tickers

Edit `MARKET_INDICES` in `.env`:

```env
# European indices
MARKET_INDICES=^GDAXI,^FTSE,^FCHI

# US markets
MARKET_INDICES=^IXIC,^GSPC,^DJI

# Forex
MARKET_INDICES=EURUSD=X,GBPUSD=X,USDJPY=X

# Crypto
MARKET_INDICES=BTC-USD,ETH-USD,BNB-USD

# Mixed (recommended)
MARKET_INDICES=^GDAXI,^IXIC,^GSPC,EURUSD=X,BTC-USD,^DJI,GC=F
```

Find ticker symbols at [Yahoo Finance](https://finance.yahoo.com/).

## Automation

### Daily Reports with Cron

Edit crontab:
```bash
crontab -e
```

Add entry:
```bash
# Monday-Friday at 7:00 AM
0 7 * * 1-5 cd /path/to/zenmarket-ai && ./scripts/daily_report.sh

# Daily at 8:30 AM with Telegram notification
30 8 * * * cd /path/to/zenmarket-ai && SEND_TELEGRAM=true ./scripts/daily_report.sh
```

### Using the Automation Script

```bash
# Interactive mode (will ask about Telegram)
./scripts/daily_report.sh

# Non-interactive with Telegram
SEND_TELEGRAM=true ./scripts/daily_report.sh

# Non-interactive without Telegram
./scripts/daily_report.sh
```

## Telegram Integration

### Setup

1. Get bot token from [@BotFather](https://t.me/BotFather)
2. Get chat ID from [@userinfobot](https://t.me/userinfobot)
3. Configure `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

### Sending Reports

```bash
# Send latest PDF
python scripts/telegram_sender.py

# Send specific report
python scripts/telegram_sender.py reports/zenmarket_report_2025-11-11.pdf
```

## Output Files

### Report Naming

Reports are named with timestamp:
```
zenmarket_report_2025-11-11.md
zenmarket_report_2025-11-11.html
zenmarket_report_2025-11-11.pdf
```

### Report Structure

Each report contains:

1. **Header**: Date and time
2. **Executive Summary**: AI-generated overview
3. **Top News**: 5-7 headlines with summaries
4. **Market Overview**: Performance table
5. **Sentiment Analysis**: Distribution chart
6. **AI Insights**: Professional analysis
7. **Key Points**: Recommendations
8. **Disclaimer**: Legal notice

### Charts (Optional)

If `REPORT_INCLUDE_CHARTS=true`:
- `*_performance.png`: Bar chart of market changes
- `*_volatility.png`: Volatility comparison

Charts are embedded in HTML/PDF, saved separately for Markdown.

## Advanced Usage

### Custom News Sources

Add RSS feeds by editing `src/core/news_fetcher.py`:

```python
RSS_FEEDS = {
    "your_source": "https://example.com/feed.rss",
    # ... existing feeds
}
```

### Custom Sentiment Words

Edit `src/core/sentiment_analyzer.py`:

```python
POSITIVE_WORDS = {
    "gain", "profit", "surge",
    "your_word",  # Add custom words
    # ... existing words
}
```

### Programmatic Usage

Use ZenMarket AI as a Python library:

```python
from src.core.news_fetcher import NewsFetcher
from src.core.market_data import MarketDataFetcher

# Fetch news
news_fetcher = NewsFetcher()
articles = news_fetcher.fetch_all()

# Fetch market data
market_fetcher = MarketDataFetcher()
snapshots = market_fetcher.fetch_all_markets()

# Process as needed
for ticker, snapshot in snapshots.items():
    print(f"{snapshot.name}: {snapshot.change_percent:+.2f}%")
```

## Best Practices

### Cost Optimization

1. **Use `--no-ai` for testing** - Saves API costs
2. **Limit news articles** - Set `NEWS_MAX_ARTICLES=30`
3. **Cache market data** - Fetch once per day
4. **Choose AI provider wisely** - Compare OpenAI vs Anthropic costs

### Reliability

1. **Schedule during market hours** - Better data availability
2. **Avoid weekends** - Markets closed, less news
3. **Set up logging** - Monitor for errors
4. **Backup reports** - Archive important reports

### Performance

1. **Disable charts if not needed** - Faster generation
2. **Use Markdown only** - Fastest format
3. **Limit lookback time** - Fewer articles to process
4. **Run during off-peak hours** - Better API response times

## Troubleshooting

### "No articles fetched"

- Check NewsAPI key validity
- Verify internet connection
- Try increasing `NEWS_LOOKBACK_HOURS`
- Check NewsAPI rate limits (100/day free tier)

### "AI summary failed"

- Verify OpenAI/Anthropic API key
- Check API account has credits
- Try alternative provider
- Use `--no-ai` as fallback

### "Market data unavailable"

- Check ticker symbols are valid
- Markets may be closed (weekends/holidays)
- Yahoo Finance may be temporarily down
- Try again later

### "PDF generation failed"

- Install system dependencies (see INSTALLATION.md)
- Use `--format markdown html` as alternative
- Check WeasyPrint logs for specific errors

## Tips and Tricks

### Quick Morning Check

```bash
# Markdown only for quick reading
python -m src.main --format markdown --no-ai
cat reports/zenmarket_report_$(date +%Y-%m-%d).md
```

### Generate Historical Report

```bash
# Increase lookback for weekly summary
# (Edit .env: NEWS_LOOKBACK_HOURS=168)
python -m src.main
```

### Multiple Market Profiles

Create different `.env` files:

```bash
# US markets
cp .env .env.us
# Edit .env.us with US-focused tickers

# European markets
cp .env .env.eu
# Edit .env.eu with EU-focused tickers

# Use specific profile
cp .env.us .env && python -m src.main
```

## Support

For issues and questions:
- [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues)
- [Documentation](https://github.com/TechNatool/zenmarket-ai/tree/main/docs)
- Email: contact@technatool.com
