# Sentiment Analysis Module

The Sentiment module analyzes financial news and text to determine market sentiment.

---

## Overview

Features:
- Lexicon-based sentiment scoring
- AI-powered sentiment analysis (OpenAI, Anthropic)
- Confidence scoring
- Fallback mechanisms
- Batch processing

---

## Sentiment Analyzer (`sentiment_analyzer.py`)

### Methods

#### 1. Lexicon-Based Analysis

Uses predefined word lists to score sentiment.

```python
from src.core.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze_lexicon(
    "Apple stock surges on strong earnings report"
)

print(f"Sentiment: {result.sentiment}")  # positive/negative/neutral
print(f"Score: {result.score}")  # -1.0 to +1.0
print(f"Confidence: {result.confidence}")  # 0-100%
```

**Features:**
- Fast (< 1ms)
- No API calls
- Good for bulk analysis
- Basic but reliable

#### 2. AI-Powered Analysis

Uses GPT-4 or Claude for nuanced analysis.

```python
result = analyzer.analyze_with_ai(
    text="Despite revenue miss, margins improved significantly",
    provider="openai"  # or "anthropic"
)
```

**Features:**
- Context-aware
- Handles sarcasm
- Detects subtle sentiment
- Slower but more accurate

---

## Sentiment Scores

```
Score Range:
+1.0 to +0.5  : Strong Positive
+0.5 to +0.1  : Positive
+0.1 to -0.1  : Neutral
-0.1 to -0.5  : Negative
-0.5 to -1.0  : Strong Negative
```

---

## Confidence Scores

Confidence indicates reliability:

```
90-100%: Very High - Clear sentiment signals
70-89%:  High - Confident assessment
50-69%:  Medium - Some ambiguity
30-49%:  Low - Mixed signals
< 30%:   Very Low - Unclear sentiment
```

---

## Batch Analysis

```python
articles = [
    {"title": "Apple earnings beat", "content": "..."},
    {"title": "Tesla misses targets", "content": "..."},
]

results = analyzer.analyze_batch(articles)

# Get sentiment distribution
positive = sum(1 for r in results if r.sentiment == "positive")
negative = sum(1 for r in results if r.sentiment == "negative")
```

---

## Fallback Strategy

```
1. Try AI analysis (OpenAI/Anthropic)
2. If fails → Lexicon analysis
3. If fails → Return neutral sentiment
```

---

## Configuration

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SENTIMENT_PROVIDER=openai  # or anthropic
SENTIMENT_FALLBACK=lexicon
```

---

## Examples

### Financial News

```python
analyzer = SentimentAnalyzer()

# Positive
result = analyzer.analyze_lexicon(
    "Stock rallies on earnings beat and positive guidance"
)
# Score: +0.75, Sentiment: positive

# Negative
result = analyzer.analyze_lexicon(
    "Company warns of declining revenue and layoffs"
)
# Score: -0.82, Sentiment: negative

# Neutral
result = analyzer.analyze_lexicon(
    "Company announces quarterly dividend"
)
# Score: +0.05, Sentiment: neutral
```

---

## Testing

- `tests/test_sentiment_analyzer.py` - 10 tests
- `tests/test_sentiment_analyzer_complete.py` - 25 tests

Coverage: 100% for sentiment_analyzer.py
