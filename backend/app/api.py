from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .core import data_fetcher, indicators, scoring
from .core import scrapers
from .schemas import ScanRequest, ScanResponse, StockAnalysisResponse
import datetime

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    symbols = req.symbols or []
    results = []
    for s in symbols:
        try:
            analysis = scoring.analyze_stock(s)
            results.append(analysis)
        except Exception as e:
            results.append({"symbol": s, "error": str(e)})
    return {"generated_at": datetime.datetime.utcnow().isoformat(), "results": results}


@router.get("/stock/{symbol}", response_model=StockAnalysisResponse)
def stock_detail(symbol: str):
    try:
        analysis = scoring.analyze_stock(symbol)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch")
def fetch_url(url: str):
    """Fetch raw HTML of a public URL (useful when APIs aren't available)."""
    try:
        res = scrapers.fetch_html(url)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
