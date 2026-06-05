from pydantic import BaseModel
from typing import List, Optional, Any


class ScanRequest(BaseModel):
    symbols: Optional[List[str]] = []
    index: Optional[str] = None
    sector: Optional[str] = None


class ScanResult(BaseModel):
    symbol: str
    trading_score: Optional[float]
    investing_score: Optional[float]
    trading_signal: Optional[str]
    investing_signal: Optional[str]
    metadata: Optional[Any]


class ScanResponse(BaseModel):
    generated_at: str
    results: List[Any]


class StockAnalysisResponse(BaseModel):
    symbol: str
    price_source: dict
    indicators: dict
    technical: dict
    fundamental: dict
    trading_score: Optional[float]
    investing_score: Optional[float]
    trading_signal: Optional[str]
    investing_signal: Optional[str]
