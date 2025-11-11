"""
Sentiment analyzer for ZenMarket AI.
Analyzes sentiment of news articles using multiple methods.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

from ..utils.logger import get_logger
from ..utils.config_loader import get_config

logger = get_logger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result."""

    text: str
    sentiment: str  # "positive", "negative", "neutral"
    score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    method: str  # "lexicon", "ai", "combined"


class SentimentAnalyzer:
    """Analyzes sentiment of financial news."""

    # Financial sentiment lexicon (simplified)
    POSITIVE_WORDS = {
        "gain", "gains", "up", "rise", "rises", "rising", "surge", "surges", "surging",
        "rally", "rallies", "rallying", "growth", "profit", "profits", "profitable",
        "boom", "booming", "bullish", "beat", "beats", "outperform", "strong", "stronger",
        "increase", "increases", "increasing", "improve", "improves", "improving",
        "recovery", "recovers", "optimistic", "optimism", "positive", "success",
        "advance", "advances", "advancing", "soar", "soars", "soaring", "breakthrough"
    }

    NEGATIVE_WORDS = {
        "loss", "losses", "down", "fall", "falls", "falling", "drop", "drops", "dropping",
        "decline", "declines", "declining", "crash", "crashes", "crashing", "plunge",
        "plunges", "plunging", "bearish", "miss", "misses", "underperform", "weak",
        "weaker", "decrease", "decreases", "decreasing", "worsen", "worsens", "worsening",
        "recession", "pessimistic", "pessimism", "negative", "failure", "risk", "risks",
        "threat", "threatens", "concern", "concerns", "worry", "worries", "turmoil"
    }

    # Sentiment modifiers
    INTENSIFIERS = {"very", "extremely", "highly", "significantly", "substantially"}
    NEGATIONS = {"not", "no", "never", "neither", "hardly", "barely"}

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.config = get_config()

    def analyze_lexicon(self, text: str) -> SentimentResult:
        """
        Analyze sentiment using lexicon-based approach.

        Args:
            text: Text to analyze

        Returns:
            SentimentResult
        """
        # Tokenize and lowercase
        words = re.findall(r'\b\w+\b', text.lower())

        positive_count = 0
        negative_count = 0
        total_sentiment_words = 0

        # Handle negations
        i = 0
        while i < len(words):
            word = words[i]

            # Check for negation
            is_negated = False
            if i > 0 and words[i-1] in self.NEGATIONS:
                is_negated = True

            # Check for intensifier
            intensifier_boost = 1.0
            if i > 0 and words[i-1] in self.INTENSIFIERS:
                intensifier_boost = 1.5

            # Count sentiment
            if word in self.POSITIVE_WORDS:
                total_sentiment_words += 1
                if is_negated:
                    negative_count += intensifier_boost
                else:
                    positive_count += intensifier_boost

            elif word in self.NEGATIVE_WORDS:
                total_sentiment_words += 1
                if is_negated:
                    positive_count += intensifier_boost
                else:
                    negative_count += intensifier_boost

            i += 1

        # Calculate score
        if total_sentiment_words == 0:
            score = 0.0
            sentiment = "neutral"
            confidence = 0.5
        else:
            score = (positive_count - negative_count) / max(total_sentiment_words, 1)
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]

            # Determine sentiment
            if score > 0.2:
                sentiment = "positive"
            elif score < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            # Confidence based on number of sentiment words
            confidence = min(1.0, total_sentiment_words / 10.0)

        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            sentiment=sentiment,
            score=score,
            confidence=confidence,
            method="lexicon"
        )

    def analyze_with_ai(self, text: str) -> Optional[SentimentResult]:
        """
        Analyze sentiment using AI (OpenAI or Anthropic).

        Args:
            text: Text to analyze

        Returns:
            SentimentResult or None if AI not available
        """
        try:
            if self.config.ai_provider == "openai" and self.config.openai_api_key:
                return self._analyze_with_openai(text)
            elif self.config.ai_provider == "anthropic" and self.config.anthropic_api_key:
                return self._analyze_with_anthropic(text)
            else:
                logger.warning("No AI provider configured for sentiment analysis")
                return None

        except Exception as e:
            logger.error(f"Error in AI sentiment analysis: {e}")
            return None

    def _analyze_with_openai(self, text: str) -> SentimentResult:
        """Analyze with OpenAI API."""
        import openai

        openai.api_key = self.config.openai_api_key

        prompt = f"""Analyze the financial sentiment of this text and respond with ONLY a JSON object:

Text: "{text}"

Response format:
{{"sentiment": "positive/negative/neutral", "score": <float -1.0 to 1.0>, "confidence": <float 0.0 to 1.0>}}"""

        response = openai.chat.completions.create(
            model=self.config.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=100
        )

        import json
        result = json.loads(response.choices[0].message.content.strip())

        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            sentiment=result["sentiment"],
            score=float(result["score"]),
            confidence=float(result["confidence"]),
            method="openai"
        )

    def _analyze_with_anthropic(self, text: str) -> SentimentResult:
        """Analyze with Anthropic Claude API."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        prompt = f"""Analyze the financial sentiment of this text and respond with ONLY a JSON object:

Text: "{text}"

Response format:
{{"sentiment": "positive/negative/neutral", "score": <float -1.0 to 1.0>, "confidence": <float 0.0 to 1.0>}}"""

        message = client.messages.create(
            model=self.config.anthropic_model,
            max_tokens=100,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result = json.loads(message.content[0].text.strip())

        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            sentiment=result["sentiment"],
            score=float(result["score"]),
            confidence=float(result["confidence"]),
            method="anthropic"
        )

    def analyze(self, text: str, use_ai: bool = False) -> SentimentResult:
        """
        Analyze sentiment with fallback strategy.

        Args:
            text: Text to analyze
            use_ai: Whether to use AI (if available)

        Returns:
            SentimentResult
        """
        if use_ai:
            ai_result = self.analyze_with_ai(text)
            if ai_result:
                return ai_result

        # Fallback to lexicon
        return self.analyze_lexicon(text)

    def analyze_batch(
        self,
        texts: List[str],
        use_ai: bool = False
    ) -> List[SentimentResult]:
        """
        Analyze multiple texts.

        Args:
            texts: List of texts
            use_ai: Whether to use AI

        Returns:
            List of SentimentResult
        """
        results = []

        for i, text in enumerate(texts):
            try:
                result = self.analyze(text, use_ai=use_ai)
                results.append(result)

                if (i + 1) % 10 == 0:
                    logger.info(f"Analyzed sentiment for {i + 1}/{len(texts)} texts")

            except Exception as e:
                logger.error(f"Error analyzing text {i}: {e}")
                # Create neutral result as fallback
                results.append(SentimentResult(
                    text=text[:100],
                    sentiment="neutral",
                    score=0.0,
                    confidence=0.0,
                    method="error"
                ))

        return results

    def get_overall_sentiment(
        self,
        results: List[SentimentResult]
    ) -> Tuple[str, float]:
        """
        Calculate overall sentiment from multiple results.

        Args:
            results: List of SentimentResult

        Returns:
            Tuple of (sentiment_label, average_score)
        """
        if not results:
            return "neutral", 0.0

        # Weighted average by confidence
        total_weighted_score = sum(r.score * r.confidence for r in results)
        total_confidence = sum(r.confidence for r in results)

        if total_confidence == 0:
            avg_score = 0.0
        else:
            avg_score = total_weighted_score / total_confidence

        # Determine label
        if avg_score > 0.2:
            sentiment = "positive"
        elif avg_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        logger.info(f"Overall sentiment: {sentiment} (score: {avg_score:.3f})")
        return sentiment, avg_score

    def get_sentiment_distribution(
        self,
        results: List[SentimentResult]
    ) -> Dict[str, int]:
        """
        Get distribution of sentiments.

        Args:
            results: List of SentimentResult

        Returns:
            Dictionary with counts
        """
        distribution = {"positive": 0, "negative": 0, "neutral": 0}

        for result in results:
            distribution[result.sentiment] = distribution.get(result.sentiment, 0) + 1

        return distribution
