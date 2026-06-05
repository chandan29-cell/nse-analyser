"""Tests for earnings call parser, quarterly extractor, and sentiment analyzer"""

import pytest
from backend.app.core.earnings_parser import EarningsCallParser, EarningsCallSummary
from backend.app.core.quarterly_extractor import QuarterlyExtractor, QuarterlyMetrics
from backend.app.core.sentiment_analyzer import SentimentAnalyzer, SentimentScore


class TestEarningsParser:
    def setup_method(self):
        self.parser = EarningsCallParser()

    def test_extract_key_topics(self):
        transcript = "Our revenue grew significantly this quarter, up 15% year-over-year. We're raising our guidance. Gross margins improved to 45%, from 42% last quarter. We're investing in cost optimization."
        topics = self.parser.extract_key_topics(transcript)
        assert len(topics) > 0
        assert any("revenue" in t.lower() or "growth" in t.lower() for t in topics)

    def test_extract_eps_revenue(self):
        summary = "EPS of $2.50 (expected: $2.30). Revenue: $1.2B (expected: $1.15B)"
        result = self.parser.extract_eps_revenue(summary)
        assert result["eps"] == 2.50
        assert result["eps_expected"] == 2.30
        assert result["revenue"] == 1.2
        assert result["revenue_expected"] == 1.15

    def test_close(self):
        self.parser.close()


class TestQuarterlyExtractor:
    def setup_method(self):
        self.extractor = QuarterlyExtractor()

    def test_calculate_metrics(self):
        data = {"symbol": "INFY", "quarter": "Q4", "fiscal_year": 2024, "date": "2024-03-31",
                "revenue": 2000.0, "gross_profit": 1200.0, "operating_income": 600.0,
                "net_income": 500.0, "eps": 2.50, "total_assets": 15000.0,
                "total_liabilities": 8000.0, "shareholders_equity": 7000.0, "debt": 3000.0,
                "operating_cash_flow": 600.0, "capital_expenditure": 100.0}
        metrics = self.extractor.calculate_metrics(data)
        assert metrics.symbol == "INFY"
        assert metrics.gross_margin == 60.0
        assert metrics.operating_margin == 30.0
        assert metrics.net_margin == 25.0
        assert metrics.free_cash_flow == 500.0

    def test_get_cash_flow_quality(self):
        metric = QuarterlyMetrics(symbol="INFY", quarter="Q4", fiscal_year=2024,
                                 date="2024-03-31", net_income=500.0,
                                 operating_cash_flow=600.0, free_cash_flow=500.0,
                                 capital_expenditure=100.0, revenue=2000.0)
        quality = self.extractor.get_cash_flow_quality(metric)
        assert "quality_score" in quality
        assert 0 <= quality["quality_score"] <= 100


class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_bullish_sentiment(self):
        text = "Strong growth, excellent performance, record revenue, beating expectations."
        sentiment = self.analyzer.analyze_text_sentiment(text)
        assert sentiment.overall_sentiment == "bullish"
        assert sentiment.score > 0.2

    def test_analyze_bearish_sentiment(self):
        text = "Significant decline, weak performance, missed guidance, downgrade."
        sentiment = self.analyzer.analyze_text_sentiment(text)
        assert sentiment.overall_sentiment == "bearish"
        assert sentiment.score < -0.2

    def test_analyze_earnings_sentiment(self):
        earnings_call = "Record earnings, strong guidance, excellent margins."
        signal = self.analyzer.analyze_earnings_sentiment("INFY", earnings_call,
                                                         analyst_consensus="Consensus: Good growth expected")
        assert signal.symbol == "INFY"
        assert signal.signal_type in ["SEAD", "PEAD"]
        assert signal.direction in ["bullish", "neutral", "bearish"]
