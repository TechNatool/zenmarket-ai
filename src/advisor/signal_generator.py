"""
Signal generator for AI Trading Advisor.
Generates trading signals (BUY/SELL/HOLD) based on technical indicators.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .indicators import TechnicalIndicators
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SignalType(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradingSignal:
    """Trading signal with reasoning."""

    ticker: str
    signal: SignalType
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    indicators: TechnicalIndicators

    def get_emoji(self) -> str:
        """Get emoji for signal."""
        emojis = {
            SignalType.BUY: "📈",
            SignalType.SELL: "📉",
            SignalType.HOLD: "⚖️"
        }
        return emojis.get(self.signal, "➖")

    def get_trend_description(self) -> str:
        """Get trend description."""
        if self.indicators.ma_20 > self.indicators.ma_50:
            return "Haussière" if self.signal == SignalType.BUY else "Haussière (prudence)"
        elif self.indicators.ma_20 < self.indicators.ma_50:
            return "Baissière" if self.signal == SignalType.SELL else "Baissière (prudence)"
        else:
            return "Neutre"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'ticker': self.ticker,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'reasons': self.reasons,
            'indicators': self.indicators.to_dict(),
            'trend': self.get_trend_description()
        }


class SignalGenerator:
    """Generates trading signals from technical indicators."""

    def __init__(
        self,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        rsi_strong_overbought: float = 80.0,
        rsi_strong_oversold: float = 20.0
    ):
        """
        Initialize signal generator.

        Args:
            rsi_overbought: RSI level considered overbought
            rsi_oversold: RSI level considered oversold
            rsi_strong_overbought: RSI level strongly overbought
            rsi_strong_oversold: RSI level strongly oversold
        """
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.rsi_strong_overbought = rsi_strong_overbought
        self.rsi_strong_oversold = rsi_strong_oversold

    def generate_signal(self, indicators: TechnicalIndicators) -> TradingSignal:
        """
        Generate trading signal from technical indicators.

        Logic:
        - BUY: MA20 > MA50 AND RSI < 70 AND price near/below MA20
        - SELL: MA20 < MA50 AND RSI > 30 AND price near/above MA20
        - HOLD: Otherwise

        Args:
            indicators: TechnicalIndicators object

        Returns:
            TradingSignal object
        """
        reasons = []
        signal_points = 0  # Positive = BUY, Negative = SELL

        # === Moving Average Analysis ===
        ma_cross_bullish = indicators.ma_20 > indicators.ma_50
        ma_cross_bearish = indicators.ma_20 < indicators.ma_50

        if ma_cross_bullish:
            signal_points += 2
            reasons.append(f"Croisement haussier MM20 ({indicators.ma_20:.2f}) > MM50 ({indicators.ma_50:.2f})")
        elif ma_cross_bearish:
            signal_points -= 2
            reasons.append(f"Croisement baissier MM20 ({indicators.ma_20:.2f}) < MM50 ({indicators.ma_50:.2f})")
        else:
            reasons.append("MAs en convergence")

        # === RSI Analysis ===
        if indicators.rsi < self.rsi_strong_oversold:
            signal_points += 3
            reasons.append(f"RSI très survendu ({indicators.rsi:.1f} < {self.rsi_strong_oversold})")
        elif indicators.rsi < self.rsi_oversold:
            signal_points += 1
            reasons.append(f"RSI survendu ({indicators.rsi:.1f} < {self.rsi_oversold})")
        elif indicators.rsi > self.rsi_strong_overbought:
            signal_points -= 3
            reasons.append(f"RSI très suracheté ({indicators.rsi:.1f} > {self.rsi_strong_overbought})")
        elif indicators.rsi > self.rsi_overbought:
            signal_points -= 1
            reasons.append(f"RSI suracheté ({indicators.rsi:.1f} > {self.rsi_overbought})")
        else:
            reasons.append(f"RSI neutre ({indicators.rsi:.1f})")

        # === Bollinger Bands Analysis ===
        if indicators.current_price < indicators.bb_lower:
            signal_points += 1
            reasons.append(f"Prix sous bande inférieure BB ({indicators.bb_lower:.2f})")
        elif indicators.current_price > indicators.bb_upper:
            signal_points -= 1
            reasons.append(f"Prix au-dessus bande supérieure BB ({indicators.bb_upper:.2f})")

        # === Price vs MA20 ===
        price_below_ma20 = indicators.current_price < indicators.ma_20
        price_above_ma20 = indicators.current_price > indicators.ma_20

        if ma_cross_bullish and price_below_ma20:
            signal_points += 1
            reasons.append("Prix proche/sous MA20 (opportunité d'achat)")
        elif ma_cross_bearish and price_above_ma20:
            signal_points -= 1
            reasons.append("Prix proche/au-dessus MA20 (opportunité de vente)")

        # === Determine Signal ===
        if signal_points >= 3:
            signal = SignalType.BUY
            confidence = min(1.0, signal_points / 6.0)
        elif signal_points <= -3:
            signal = SignalType.SELL
            confidence = min(1.0, abs(signal_points) / 6.0)
        else:
            signal = SignalType.HOLD
            confidence = 0.5

        # === Additional Rules (Override if needed) ===
        # Strong overbought/oversold can override
        if indicators.rsi > self.rsi_strong_overbought and signal == SignalType.BUY:
            signal = SignalType.HOLD
            reasons.append("⚠️ Signal d'achat annulé : RSI trop élevé")
            confidence = 0.4

        if indicators.rsi < self.rsi_strong_oversold and signal == SignalType.SELL:
            signal = SignalType.HOLD
            reasons.append("⚠️ Signal de vente annulé : RSI trop bas")
            confidence = 0.4

        trading_signal = TradingSignal(
            ticker=indicators.ticker,
            signal=signal,
            confidence=confidence,
            reasons=reasons,
            indicators=indicators
        )

        logger.info(
            f"Generated signal for {indicators.ticker}: {signal.value} "
            f"(confidence: {confidence:.2f}, points: {signal_points})"
        )

        return trading_signal

    def generate_signals_batch(
        self,
        indicators_list: List[TechnicalIndicators]
    ) -> List[TradingSignal]:
        """
        Generate signals for multiple tickers.

        Args:
            indicators_list: List of TechnicalIndicators

        Returns:
            List of TradingSignal objects
        """
        signals = []

        for indicators in indicators_list:
            try:
                signal = self.generate_signal(indicators)
                signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating signal for {indicators.ticker}: {e}")
                # Create a HOLD signal as fallback
                signals.append(TradingSignal(
                    ticker=indicators.ticker,
                    signal=SignalType.HOLD,
                    confidence=0.0,
                    reasons=["Erreur de calcul"],
                    indicators=indicators
                ))

        return signals

    def get_market_bias(self, signals: List[TradingSignal]) -> Tuple[str, float]:
        """
        Calculate overall market bias from multiple signals.

        Args:
            signals: List of TradingSignal objects

        Returns:
            Tuple of (bias_description, bias_score)
            bias_score: -1.0 (bearish) to 1.0 (bullish)
        """
        if not signals:
            return "Neutre", 0.0

        total_score = 0.0

        for signal in signals:
            if signal.signal == SignalType.BUY:
                total_score += signal.confidence
            elif signal.signal == SignalType.SELL:
                total_score -= signal.confidence

        avg_score = total_score / len(signals)

        if avg_score > 0.3:
            bias = "Haussier"
        elif avg_score < -0.3:
            bias = "Baissier"
        else:
            bias = "Neutre"

        logger.info(f"Market bias: {bias} (score: {avg_score:.2f})")

        return bias, avg_score

    def get_signal_summary(self, signals: List[TradingSignal]) -> Dict:
        """
        Get summary statistics of signals.

        Args:
            signals: List of TradingSignal objects

        Returns:
            Dictionary with summary stats
        """
        total = len(signals)
        buy_count = sum(1 for s in signals if s.signal == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal == SignalType.SELL)
        hold_count = sum(1 for s in signals if s.signal == SignalType.HOLD)

        avg_confidence = sum(s.confidence for s in signals) / total if total > 0 else 0

        return {
            'total': total,
            'buy': buy_count,
            'sell': sell_count,
            'hold': hold_count,
            'buy_pct': (buy_count / total * 100) if total > 0 else 0,
            'sell_pct': (sell_count / total * 100) if total > 0 else 0,
            'hold_pct': (hold_count / total * 100) if total > 0 else 0,
            'avg_confidence': avg_confidence
        }
