"""Earnings Call Parser - Fetches earnings call transcripts, extracts topics, EPS/revenue comparison"""

import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


@dataclass
class EarningsCallSummary:
    """Earnings call metadata and summary"""
    symbol: str
    date: str  # YYYY-MM-DD
    quarter: str  # Q1-Q4
    fiscal_year: int
    company_name: Optional[str] = None
    call_duration_minutes: Optional[int] = None
    eps_reported: Optional[float] = None
    eps_expected: Optional[float] = None
    revenue_reported: Optional[float] = None
    revenue_expected: Optional[float] = None
    guidance_outlook: Optional[str] = None
    topics: List[str] = None
    full_transcript: Optional[str] = None
    source_url: Optional[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []


class EarningsCallParser:
    """Fetch and parse earnings call transcripts"""

    BASE_URLS = {
        "seekingalpha": "https://seekingalpha.com",
        "motleyfool": "https://www.motleyfool.com",
        "yahoo": "https://finance.yahoo.com",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def fetch_earnings_call(self, symbol: str, quarter: str = "latest") -> Optional[EarningsCallSummary]:
        """Fetch recent earnings call for a symbol."""
        try:
            for source in ["seekingalpha", "yahoo"]:
                call_data = self._fetch_from_source(symbol, quarter, source)
                if call_data:
                    return call_data
            logger.info(f"No earnings call found for {symbol} ({quarter})")
            return None
        except Exception as e:
            logger.error(f"Error fetching earnings call: {e}")
            return None

    def _fetch_from_source(self, symbol: str, quarter: str, source: str) -> Optional[EarningsCallSummary]:
        """Try to fetch from specific source"""
        try:
            if source == "seekingalpha":
                return self._fetch_seekingalpha(symbol, quarter)
            elif source == "yahoo":
                return self._fetch_yahoo(symbol, quarter)
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch from {source}: {e}")
            return None

    def _fetch_seekingalpha(self, symbol: str, quarter: str) -> Optional[EarningsCallSummary]:
        """Fetch from Seeking Alpha (free tier)"""
        logger.info(f"SeekingAlpha: Earnings call data unavailable (API key required)")
        return None

    def _fetch_yahoo(self, symbol: str, quarter: str) -> Optional[EarningsCallSummary]:
        """Fetch from Yahoo Finance"""
        logger.info(f"Yahoo Finance: Earnings call transcript unavailable")
        return None

    def extract_key_topics(self, transcript: str) -> List[str]:
        """Extract key topics from earnings call transcript."""
        topics = []
        topic_keywords = {
            "Revenue/Growth": [
                r"revenue (growth|decline|up|down)",
                r"top-?line (growth|decline)",
                r"segment growth",
            ],
            "Margins/Profitability": [
                r"(gross|operating|net) margin",
                r"ebitda",
                r"profitability",
            ],
            "Cost Management": [
                r"cost (reduction|optimization|control)",
                r"efficiency (gains|improvement)",
                r"headcount",
            ],
            "Cash Flow": [
                r"free cash flow",
                r"cash generation",
                r"working capital",
            ],
            "Guidance": [
                r"(raising|lowering|maintaining|withdraw) guidance",
                r"forward-looking statement",
                r"outlook",
            ],
        }
        for topic, keywords in topic_keywords.items():
            for pattern in keywords:
                if re.search(pattern, transcript, re.IGNORECASE):
                    topics.append(topic)
                    break
        return list(set(topics))

    def extract_eps_revenue(self, summary_text: str) -> Dict[str, Optional[float]]:
        """Extract EPS and revenue from earnings summary."""
        result = {"eps": None, "revenue": None, "eps_expected": None, "revenue_expected": None}
        eps_match = re.search(r"(?:EPS|earnings per share)[:\s]+\$?([\d.]+)", summary_text, re.IGNORECASE)
        if eps_match:
            result["eps"] = float(eps_match.group(1))
        exp_eps_match = re.search(r"(?:expected|estimate|consensus).*?EPS[:\s]+\$?([\d.]+)", summary_text, re.IGNORECASE)
        if exp_eps_match:
            result["eps_expected"] = float(exp_eps_match.group(1))
        rev_match = re.search(r"revenue[:\s]+\$?([\d.]+)\s*[Bb](?:illion)?", summary_text, re.IGNORECASE)
        if rev_match:
            result["revenue"] = float(rev_match.group(1))
        exp_rev_match = re.search(r"(?:expected|estimate|consensus).*?revenue[:\s]+\$?([\d.]+)\s*[Bb]", summary_text, re.IGNORECASE)
        if exp_rev_match:
            result["revenue_expected"] = float(exp_rev_match.group(1))
        return result

    def generate_transcript_summary(self, transcript: str, max_sentences: int = 5) -> str:
        """Generate concise summary of earnings call."""
        if not transcript:
            return "Transcript unavailable"
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        return " ".join(sentences[:max_sentences])

    def close(self):
        """Cleanup resources"""
        self.session.close()
