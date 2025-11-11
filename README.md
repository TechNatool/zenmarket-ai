# ZenMarket AI 📊

> **AI-powered financial intelligence and automated market analysis system**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ZenMarket AI is a professional-grade automated system that generates comprehensive daily financial intelligence reports. It combines real-time market data, news analysis, sentiment tracking, and AI-powered insights to deliver actionable market intelligence every morning.

---

## Features

- **Automated News Aggregation**: Fetches financial news from multiple sources (NewsAPI, RSS feeds)
- **Real-Time Market Data**: Tracks major indices (DAX, NASDAQ, S&P 500), forex (EUR/USD), and crypto (BTC-USD)
- **AI-Powered Analysis**: Uses OpenAI GPT-4 or Anthropic Claude for summaries and insights
- **Sentiment Analysis**: Analyzes market sentiment with lexicon-based and AI methods
- **Beautiful Reports**: Generates reports in Markdown, HTML, and PDF formats with charts
- **Automated Delivery**: Optional Telegram bot integration for automatic report delivery
- **Professional Quality**: Production-ready code with logging, error handling, and type hints

---

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- API keys for:
  - [NewsAPI](https://newsapi.org/) (required for news fetching)
  - [OpenAI](https://platform.openai.com/) or [Anthropic](https://www.anthropic.com/) (required for AI features)
  - [Telegram Bot](https://core.telegram.org/bots) (optional, for notifications)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

Required configuration in `.env`:
```env
NEWSAPI_KEY=your_newsapi_key_here
OPENAI_API_KEY=your_openai_key_here  # or ANTHROPIC_API_KEY
AI_PROVIDER=openai  # or anthropic
```

### 4. Run Your First Report

```bash
# Generate a report
python -m src.main

# Or use the automation script
./scripts/daily_report.sh
```

Your reports will be saved in the `reports/` directory.

---

## Usage

### Command Line Interface

```bash
# Basic usage - generate all formats
python -m src.main

# Generate only Markdown
python -m src.main --format markdown

# Generate PDF and HTML
python -m src.main --format pdf html

# Disable AI (faster, uses fallback methods)
python -m src.main --no-ai

# Enable debug logging
python -m src.main --log-level DEBUG
```

### Automation Script

```bash
# Run the complete workflow
./scripts/daily_report.sh

# With Telegram notification (non-interactive)
SEND_TELEGRAM=true ./scripts/daily_report.sh
```

### Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```
4. Send reports:
   ```bash
   python scripts/telegram_sender.py reports/zenmarket_report_2025-11-11.pdf
   ```

### Daily Automation with Cron

Add to your crontab (`crontab -e`):

```bash
# Run every weekday at 7:00 AM
0 7 * * 1-5 cd /path/to/zenmarket-ai && SEND_TELEGRAM=true ./scripts/daily_report.sh
```

---

## Report Contents

Each ZenMarket AI report includes:

1. **Executive Summary** - AI-generated overview of market conditions
2. **Top News Headlines** - 5-7 most relevant financial news stories with AI summaries
3. **Market Overview** - Performance table for all tracked indices and assets
4. **Sentiment Analysis** - Distribution and overall market sentiment score
5. **AI Market Insights** - Professional analysis combining news and market data
6. **Key Points to Watch** - Actionable recommendations and risk factors
7. **Charts** (optional) - Performance and volatility visualizations

---

## Project Structure

```
zenmarket-ai/
├── src/
│   ├── core/
│   │   ├── news_fetcher.py         # News aggregation from multiple sources
│   │   ├── market_data.py          # Real-time market data fetching
│   │   ├── sentiment_analyzer.py   # Sentiment analysis engine
│   │   ├── summarizer.py           # AI-powered summarization
│   │   └── report_generator.py     # Multi-format report generation
│   ├── utils/
│   │   ├── config_loader.py        # Configuration management
│   │   ├── logger.py               # Logging setup
│   │   └── date_utils.py           # Date/time utilities
│   └── main.py                     # Main entry point
├── scripts/
│   ├── daily_report.sh             # Automation script
│   └── telegram_sender.py          # Telegram bot integration
├── reports/                        # Generated reports (PDF, HTML, MD)
├── data/                          # Cache and logs
├── docs/                          # Additional documentation
├── tests/                         # Unit tests
├── requirements.txt               # Python dependencies
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## Configuration Options

All settings can be configured via `.env` file or environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEWSAPI_KEY` | NewsAPI.org API key | (required) |
| `OPENAI_API_KEY` | OpenAI API key | (required if AI_PROVIDER=openai) |
| `ANTHROPIC_API_KEY` | Anthropic API key | (required if AI_PROVIDER=anthropic) |
| `AI_PROVIDER` | AI service to use | `openai` |
| `MARKET_INDICES` | Comma-separated tickers | `^GDAXI,^IXIC,^GSPC,EURUSD=X,BTC-USD` |
| `NEWS_LOOKBACK_HOURS` | Hours of news to fetch | `24` |
| `REPORT_FORMATS` | Output formats | `markdown,html,pdf` |
| `REPORT_INCLUDE_CHARTS` | Generate charts | `true` |
| `TIMEZONE` | Report timezone | `Europe/Paris` |

See `.env.example` for complete configuration options.

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_news_fetcher.py
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type checking with MyPy
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests and linters
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to the branch: `git push origin feature/your-feature`
7. Open a Pull Request

---

## API Rate Limits

Be aware of API rate limits:

- **NewsAPI**: 100 requests/day (free tier)
- **OpenAI**: Pay-per-use (check your plan)
- **Yahoo Finance** (yfinance): No official limits, use responsibly
- **AlphaVantage**: 25 requests/day (free tier)

---

## Troubleshooting

### Common Issues

**"No module named 'src'"**
- Make sure you're running from the project root
- Use: `python -m src.main` (not `python src/main.py`)

**"Configuration validation failed"**
- Check that your `.env` file exists and has required API keys
- Verify API keys are valid and active

**"Failed to fetch news"**
- Verify NewsAPI key is valid
- Check internet connection
- Try with `--no-ai` flag to isolate the issue

**PDF generation fails**
- WeasyPrint requires system dependencies (Cairo, Pango)
- On Ubuntu/Debian: `sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0`
- On macOS: `brew install cairo pango`
- Or generate only HTML/Markdown: `--format markdown html`

---

## Roadmap

- [ ] Add support for more news sources (Bloomberg, Reuters)
- [ ] Implement technical indicators (MACD, Bollinger Bands)
- [ ] Add backtesting capabilities
- [ ] Web dashboard for historical reports
- [ ] Email notification support
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] Cloud deployment guides (AWS, Azure, GCP)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

**Important:** This software is for informational and educational purposes only. It does not constitute financial advice, investment recommendations, or trading signals. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

The developers and contributors of ZenMarket AI are not responsible for any financial losses or damages resulting from the use of this software.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TechNatool/zenmarket-ai/discussions)
- **Email**: contact@technatool.com

---

## Acknowledgments

- Financial data provided by [Yahoo Finance](https://finance.yahoo.com/)
- News data from [NewsAPI](https://newsapi.org/)
- AI capabilities powered by [OpenAI](https://openai.com/) and [Anthropic](https://www.anthropic.com/)

---

**Made with by TechNatool**

*Automate your market intelligence. Trade smarter.*
