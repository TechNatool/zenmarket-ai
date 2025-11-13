# AI Summarizer Module

The Summarizer module provides AI-powered text summarization and market insights.

---

## Overview

Features:
- Article summarization (OpenAI/Anthropic)
- Market insight generation
- News categorization
- Trading recommendations
- Fallback to rule-based summaries

---

## AI Summarizer (`summarizer.py`)

### Core Functions

#### 1. Article Summarization

```python
from src.core.summarizer import AISummarizer

summarizer = AISummarizer(provider="openai")

summary = summarizer.summarize_article(
    title="Apple Q4 Earnings Beat Expectations",
    content="Long article text...",
    max_length=150
)

print(summary)
# "Apple reported Q4 earnings that exceeded analyst expectations,
#  with revenue up 8% YoY. Strong iPhone sales drove results..."
```

#### 2. Market Insights

```python
insights = summarizer.generate_market_insights(
    articles=[article1, article2, article3],
    sentiment_scores=[0.75, -0.30, 0.50]
)

print(insights)
# "Overall market sentiment is positive. Key themes: strong tech
#  earnings, Fed policy uncertainty, sector rotation into growth..."
```

---

## Providers

### OpenAI (GPT-4)

```python
summarizer = AISummarizer(provider="openai")
```

**Strengths:**
- Excellent summarization
- Natural language
- Fast responses

**Configuration:**
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### Anthropic (Claude)

```python
summarizer = AISummarizer(provider="anthropic")
```

**Strengths:**
- Detailed analysis
- Context awareness
- Safety features

**Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229
```

---

## News Categorization

Automatically categorizes financial news:

```python
category = summarizer.categorize_news(
    title="Fed Raises Interest Rates 0.25%"
)
# Returns: "monetary_policy"
```

**Categories:**
- `earnings`: Company earnings reports
- `monetary_policy`: Central bank decisions
- `economic_data`: GDP, employment, inflation
- `mergers`: M&A activity
- `geopolitical`: International events
- `sector`: Industry-specific news
- `other`: Uncategorized

---

## Recommendations

Generates actionable recommendations:

```python
recommendations = summarizer.generate_recommendations(
    insights="Positive tech earnings, rising rates",
    sentiment=0.65,
    category="earnings"
)

# Returns list of recommendations:
# [
#   "Consider increasing exposure to tech sector",
#   "Monitor interest rate sensitivity",
#   "Set stop-losses given volatility"
# ]
```

---

## Fallback Mechanism

When AI is unavailable:

```python
# Fallback to rule-based summary
if sentiment > 0.5:
    summary = f"Positive news: {title}. Market impact likely bullish."
elif sentiment < -0.5:
    summary = f"Negative news: {title}. Market impact likely bearish."
else:
    summary = f"Neutral news: {title}. Limited market impact expected."
```

---

## Configuration

```bash
# .env
AI_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MAX_SUMMARY_LENGTH=200
ENABLE_AI_FALLBACK=true
```

---

## Usage Examples

### Daily Brief Generation

```python
from src.core.summarizer import AISummarizer
from src.core.news_fetcher import NewsFetcher
from src.core.sentiment_analyzer import SentimentAnalyzer

# Fetch news
fetcher = NewsFetcher()
articles = fetcher.fetch_latest(symbols=["AAPL", "MSFT"])

# Analyze sentiment
analyzer = SentimentAnalyzer()
sentiments = [analyzer.analyze_lexicon(a.content) for a in articles]

# Generate insights
summarizer = AISummarizer()
insights = summarizer.generate_market_insights(articles, sentiments)

# Generate recommendations
recommendations = summarizer.generate_recommendations(
    insights, 
    avg_sentiment=0.45
)
```

---

## Testing

- `tests/test_summarizer_complete.py` - 25 tests

Coverage: 100% for summarizer.py
