from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class ScanRequest(BaseModel):
    symbols: Optional[List[str]] = []
    index: Optional[str] = None
    sector: Optional[str] = None
    analysis_type: Optional[str] = "trading"  # "trading" or "investing"


class EarningsData(BaseModel):
    date: Optional[str] = None
    quarter: Optional[str] = None
    eps_reported: Optional[float] = None
    eps_expected: Optional[float] = None
    revenue_reported: Optional[float] = None
    revenue_expected: Optional[float] = None
    guidance_outlook: Optional[str] = None
    topics: Optional[List[str]] = []
    source: Optional[str] = None


class QuarterlyMetric(BaseModel):
    quarter: str
    fiscal_year: int
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None


class SentimentData(BaseModel):
    overall_sentiment: str  # "bullish", "neutral", "bearish"
    score: float  # -1.0 to +1.0
    confidence: float  # 0.0 to 1.0
    keywords: Optional[Dict[str, int]] = {}
    tone: Optional[str] = None


class EarningsAnomalyData(BaseModel):
    signal_type: str  # "SEAD" or "PEAD"
    direction: str  # "bullish", "neutral", "bearish"
    strength: float  # 0.0 to 1.0
    reason: str
    confidence: float  # 0.0 to 1.0
    expected_drift: Optional[str] = None
    expected_drift_percent: Optional[float] = None


class TradingSignal(BaseModel):
    direction: str  # "bullish", "neutral", "bearish"
    confidence: float  # 0.0 to 1.0
    reasoning: Optional[str] = None
    indicators_agree: Optional[float] = None


class ScanResult(BaseModel):
    symbol: str
    trading_score: Optional[float]
    investing_score: Optional[float]
    trading_signal: Optional[TradingSignal] = None
    investing_signal: Optional[TradingSignal] = None
    metadata: Optional[Any] = None


class ScanResponse(BaseModel):
    generated_at: str
    results: List[ScanResult]


class StockAnalysisResponse(BaseModel):
    symbol: str
    price: Optional[float] = None
    change_percent: Optional[float] = None
    price_source: Optional[dict] = None
    
    # Technical Analysis
    technical_indicators: Optional[Dict[str, float]] = None
    
    # Fundamentals
    fundamentals: Optional[Dict[str, Any]] = None
    
    # Earnings & Quarterly
    latest_earnings: Optional[EarningsData] = None
    quarterly_metrics: Optional[List[QuarterlyMetric]] = None
    
    # Sentiment & Anomalies
    sentiment: Optional[SentimentData] = None
    earnings_anomaly: Optional[EarningsAnomalyData] = None
    
    # Signals
    trading_score: Optional[float] = None
    investing_score: Optional[float] = None
    trading_signal: Optional[TradingSignal] = None
    investing_signal: Optional[TradingSignal] = None
    
    # Metadata
    analysis_timestamp: Optional[str] = None
    data_confidence: Optional[float] = None
