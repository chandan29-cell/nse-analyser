"""Quarterly Financial Data Extractor - Extract and analyze quarterly metrics, trends, cash flow"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import logging
import requests
import json

logger = logging.getLogger(__name__)


@dataclass
class QuarterlyMetrics:
    """Key financial metrics for a single quarter"""
    symbol: str
    quarter: str
    fiscal_year: int
    date: str
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    revenue_growth_qoq: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    cash: Optional[float] = None
    debt: Optional[float] = None
    working_capital: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None
    source: Optional[str] = None


@dataclass
class QuarterlyTrend:
    """Trend analysis across multiple quarters"""
    symbol: str
    metric_name: str
    quarters: List[str]
    values: List[Optional[float]]
    trend: str
    cagr: Optional[float] = None


class QuarterlyExtractor:
    """Extract and analyze quarterly financial data"""

    def __init__(self, finnhub_api_key: Optional[str] = None):
        self.finnhub_api_key = finnhub_api_key
        self.session = requests.Session()
        self.quarterly_cache = {}

    def fetch_latest_quarters(self, symbol: str, num_quarters: int = 8) -> List[QuarterlyMetrics]:
        """Fetch latest quarters' financial data."""
        try:
            quarters = []
            if self.finnhub_api_key:
                quarters = self._fetch_finnhub(symbol, num_quarters)
                if quarters:
                    return quarters
            quarters = self._fetch_yahoo_quarterly(symbol, num_quarters)
            if quarters:
                return quarters
            logger.info(f"No quarterly data available for {symbol}")
            return []
        except Exception as e:
            logger.error(f"Error fetching quarterly data: {e}")
            return []

    def _fetch_finnhub(self, symbol: str, num_quarters: int) -> List[QuarterlyMetrics]:
        """Fetch from Finnhub API (requires API key)"""
        try:
            logger.info(f"Finnhub quarterly data: Requires API key")
            return []
        except Exception as e:
            logger.warning(f"Finnhub fetch failed: {e}")
            return []

    def _fetch_yahoo_quarterly(self, symbol: str, num_quarters: int) -> List[QuarterlyMetrics]:
        """Fetch from Yahoo Finance (free, requires parsing)"""
        try:
            logger.info(f"Yahoo quarterly data: Parsing not yet implemented")
            return []
        except Exception as e:
            logger.warning(f"Yahoo quarterly fetch failed: {e}")
            return []

    def calculate_metrics(self, quarterly_data: Dict[str, float]) -> QuarterlyMetrics:
        """Calculate derived metrics from raw financial data."""
        metrics = QuarterlyMetrics(
            symbol=quarterly_data.get("symbol", ""),
            quarter=quarterly_data.get("quarter", ""),
            fiscal_year=quarterly_data.get("fiscal_year", 0),
            date=quarterly_data.get("date", ""),
        )
        for key in ["revenue", "gross_profit", "operating_income", "net_income", 
                    "eps", "total_assets", "total_liabilities", "shareholders_equity",
                    "cash", "debt", "working_capital", "operating_cash_flow",
                    "capital_expenditure"]:
            setattr(metrics, key, quarterly_data.get(key))
        if metrics.revenue and metrics.revenue > 0:
            if metrics.gross_profit:
                metrics.gross_margin = (metrics.gross_profit / metrics.revenue) * 100
            if metrics.operating_income:
                metrics.operating_margin = (metrics.operating_income / metrics.revenue) * 100
            if metrics.net_income:
                metrics.net_margin = (metrics.net_income / metrics.revenue) * 100
        if metrics.shareholders_equity and metrics.shareholders_equity > 0 and metrics.net_income:
            metrics.roe = (metrics.net_income / metrics.shareholders_equity) * 100
        if metrics.total_assets and metrics.total_assets > 0 and metrics.net_income:
            metrics.roa = (metrics.net_income / metrics.total_assets) * 100
        if metrics.shareholders_equity and metrics.shareholders_equity > 0 and metrics.debt:
            metrics.debt_to_equity = metrics.debt / metrics.shareholders_equity
        if metrics.operating_cash_flow and metrics.capital_expenditure:
            metrics.free_cash_flow = metrics.operating_cash_flow - metrics.capital_expenditure
        return metrics

    def analyze_trend(self, symbol: str, metric: str, quarters: List[QuarterlyMetrics]) -> Optional[QuarterlyTrend]:
        """Analyze trend for a specific metric across quarters."""
        if not quarters or len(quarters) < 2:
            return None
        try:
            values = [getattr(q, metric, None) for q in quarters]
            values = [v for v in values if v is not None]
            if len(values) < 2:
                return None
            if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                trend = "up"
            elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
                trend = "down"
            elif abs(max(values) - min(values)) / min(values) > 0.2 if min(values) > 0 else False:
                trend = "volatile"
            else:
                trend = "flat"
            cagr = None
            if len(values) >= 4 and values[0] > 0 and values[-1] > 0:
                years = (len(values) - 1) / 4
                cagr = ((values[-1] / values[0]) ** (1 / years) - 1) * 100 if years > 0 else None
            quarter_labels = [f"{q.quarter} {q.fiscal_year}" for q in quarters]
            return QuarterlyTrend(
                symbol=symbol,
                metric_name=metric,
                quarters=quarter_labels,
                values=values,
                trend=trend,
                cagr=cagr,
            )
        except Exception as e:
            logger.warning(f"Error analyzing trend: {e}")
            return None

    def get_cash_flow_quality(self, metric: QuarterlyMetrics) -> Dict[str, Any]:
        """Assess quality of earnings through cash flow analysis."""
        factors = []
        score = 50
        if metric.operating_cash_flow and metric.net_income:
            ratio = metric.operating_cash_flow / metric.net_income
            if ratio > 1.2:
                factors.append("Strong cash conversion (OCF > Net Income)")
                score += 20
            elif ratio > 1.0:
                factors.append("Healthy cash conversion")
                score += 10
            elif ratio < 0.7:
                factors.append("Weak cash conversion (cash < earnings)")
                score -= 15
        if metric.free_cash_flow and metric.free_cash_flow > 0:
            factors.append("Positive free cash flow")
            score += 15
        elif metric.free_cash_flow and metric.free_cash_flow < 0:
            factors.append("Negative free cash flow")
            score -= 15
        if metric.capital_expenditure and metric.revenue:
            capex_ratio = metric.capital_expenditure / metric.revenue
            if capex_ratio < 0.05:
                factors.append("Low capital intensity")
                score += 10
            elif capex_ratio > 0.15:
                factors.append("High capital intensity")
                score -= 5
        score = max(0, min(100, score))
        if score >= 80:
            assessment = "excellent"
        elif score >= 60:
            assessment = "good"
        elif score >= 40:
            assessment = "average"
        else:
            assessment = "poor"
        return {
            "quality_score": score,
            "assessment": assessment,
            "factors": factors,
        }

    def close(self):
        """Cleanup resources"""
        self.session.close()
