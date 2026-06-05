"""SEAD/PEAD Sentiment Analyzer - Detect earnings anomalies and market inefficiencies"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class SentimentScore:
    """Sentiment analysis result"""
    text: str
    overall_sentiment: str
    score: float
    confidence: float
    keywords: Dict[str, int]
    tone: str


@dataclass
class EarningsAnomalySignal:
    """Signal generated from sentiment drift analysis"""
    symbol: str
    signal_type: str
    direction: str
    strength: float
    reason: str
    confidence: float
    expected_drift: str
    expected_drift_percent: Optional[float] = None


class SentimentAnalyzer:
    """Analyze sentiment from text and generate trading signals"""

    BULLISH_KEYWORDS = {
        "strong": 2, "growth": 2, "outperform": 2, "upside": 2, "accelerate": 2,
        "expansion": 2, "beat": 2, "raise": 2, "upgrade": 2, "record": 1,
        "excellent": 1, "positive": 1, "improved": 1, "solid": 1, "better": 1,
        "exceed": 1, "opportunity": 1,
    }
    BEARISH_KEYWORDS = {
        "decline": 2, "miss": 2, "downside": 2, "downgrade": 2, "risk": 2,
        "weakness": 2, "slow": 2, "pressure": 2, "challenge": 2,
        "headwind": 2, "negative": 1, "concern": 1, "deteriorate": 1,
        "difficult": 1, "threat": 1,
    }
    NEGATION_WORDS = {"not", "no", "neither", "don't", "doesn't", "can't", "won't"}

    def __init__(self):
        self.sentiment_history = defaultdict(list)

    def analyze_text_sentiment(self, text: str, source: str = "general") -> SentimentScore:
        """Analyze sentiment of given text."""
        if not text or len(text.strip()) == 0:
            return SentimentScore(text=text, overall_sentiment="neutral", score=0.0,
                                confidence=0.0, keywords={}, tone="neutral")
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        bullish_count = bearish_count = 0
        bullish_words = bearish_words = {}
        for i, word in enumerate(words):
            is_negated = i > 0 and words[i-1] in self.NEGATION_WORDS
            if word in self.BULLISH_KEYWORDS:
                weight = self.BULLISH_KEYWORDS[word]
                if is_negated:
                    bearish_count += weight
                else:
                    bullish_count += weight
            elif word in self.BEARISH_KEYWORDS:
                weight = self.BEARISH_KEYWORDS[word]
                if is_negated:
                    bullish_count += weight
                else:
                    bearish_count += weight
        total_sentiment = bullish_count + bearish_count
        sentiment_score = (bullish_count - bearish_count) / total_sentiment if total_sentiment > 0 else 0.0
        confidence = min(1.0, total_sentiment / len(words)) if total_sentiment > 0 else 0.0
        overall_sentiment = "bullish" if sentiment_score > 0.2 else ("bearish" if sentiment_score < -0.2 else "neutral")
        return SentimentScore(text=text[:200], overall_sentiment=overall_sentiment,
                            score=sentiment_score, confidence=confidence,
                            keywords={}, tone="neutral")

    def analyze_earnings_sentiment(self, symbol: str, earnings_call_transcript: str,
                                  analyst_consensus: Optional[str] = None,
                                  recent_news: Optional[List[str]] = None) -> EarningsAnomalySignal:
        """Analyze sentiment around earnings announcement. Generates SEAD/PEAD signal."""
        call_sentiment = self.analyze_text_sentiment(earnings_call_transcript, source="earnings_call")
        analyst_sentiment = self.analyze_text_sentiment(analyst_consensus) if analyst_consensus else None
        news_sentiments = [self.analyze_text_sentiment(article, source="news") for article in (recent_news or [])]
        avg_news_sentiment = sum(s.score for s in news_sentiments) / len(news_sentiments) if news_sentiments else 0.0
        drift_detected = drift_type = False
        if analyst_sentiment and call_sentiment:
            drift = call_sentiment.score - analyst_sentiment.score
            if drift > 0.3:
                drift_detected, drift_type = True, "positive"
            elif drift < -0.3:
                drift_detected, drift_type = True, "negative"
        if drift_detected:
            signal_type = "SEAD"
            if drift_type == "positive":
                direction, strength = "bullish", min(1.0, abs(drift) * 2)
                reason = f"Earnings reality beats analyst expectations (drift: {drift:.2f})"
                expected_drift_percent = 3.0
            else:
                direction, strength = "bearish", min(1.0, abs(drift) * 2)
                reason = f"Earnings reality misses analyst expectations (drift: {drift:.2f})"
                expected_drift_percent = -3.0
        else:
            signal_type = "PEAD"
            call_direction = call_sentiment.overall_sentiment
            if call_direction == "bullish" and avg_news_sentiment > 0.1:
                direction, strength = "bullish", 0.5
                reason = "Earnings call bullish, news sentiment positive"
                expected_drift_percent = 2.0
            elif call_direction == "bearish" and avg_news_sentiment < -0.1:
                direction, strength = "bearish", 0.5
                reason = "Earnings call bearish, news sentiment negative"
                expected_drift_percent = -2.0
            else:
                direction, strength = "neutral", 0.3
                reason = "Mixed sentiment, expecting range-bound trading"
                expected_drift_percent = None
        confidence = min((call_sentiment.confidence + (analyst_sentiment.confidence if analyst_sentiment else 0)) / 2, 1.0)
        self.sentiment_history[symbol].append(call_sentiment)
        return EarningsAnomalySignal(
            symbol=symbol, signal_type=signal_type, direction=direction, strength=strength,
            reason=reason, confidence=confidence, expected_drift=drift_type if drift_detected else None,
            expected_drift_percent=expected_drift_percent,
        )

    def get_sentiment_trend(self, symbol: str, lookback: int = 10) -> Dict[str, Any]:
        """Get sentiment trend for a symbol over recent periods."""
        if symbol not in self.sentiment_history:
            return {"symbol": symbol, "avg_sentiment": 0.0, "trend": "unknown"}
        recent = self.sentiment_history[symbol][-lookback:]
        if not recent:
            return {"symbol": symbol, "avg_sentiment": 0.0, "trend": "unknown"}
        avg_sentiment = sum(s.score for s in recent) / len(recent)
        mid = len(recent) // 2
        first_half_avg = sum(s.score for s in recent[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(s.score for s in recent[mid:]) / (len(recent) - mid) if len(recent) - mid > 0 else 0
        if second_half_avg > first_half_avg + 0.1:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.1:
            trend = "deteriorating"
        else:
            trend = "stable"
        bullish = sum(1 for s in recent if s.overall_sentiment == "bullish")
        bearish = sum(1 for s in recent if s.overall_sentiment == "bearish")
        neutral = len(recent) - bullish - bearish
        return {
            "symbol": symbol, "avg_sentiment": avg_sentiment, "trend": trend,
            "bullish_count": bullish, "bearish_count": bearish, "neutral_count": neutral, "periods": len(recent),
        }
