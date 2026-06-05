import yfinance as yf
import datetime
from . import finnhub_client
from . import scrapers


def fetch_price_history(symbol: str, period: str = "6mo"):
    """Fetches price history via yfinance. Returns dict with data and metadata.

    If data is unavailable, returns {'data': None, 'meta': {...}}
    """
    meta = {"source": "yfinance", "symbol": symbol, "fetched_at": datetime.datetime.utcnow().isoformat()}
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist is None or hist.empty:
            return {"data": None, "meta": {**meta, "note": "Data unavailable"}}
        # convert to simple dict
        df = hist.reset_index()
        return {"data": df, "meta": meta}
    except Exception as e:
        return {"data": None, "meta": {**meta, "error": str(e), "note": "Data unavailable"}}


def fetch_company_fundamentals(symbol: str):
    """Try verified providers (Finnhub) for fundamentals. If unavailable, return None.

    The function will not fabricate data. Each returned record includes a `meta` block
    with `source`, `url` when available, and `fetched_at` timestamp.
    """
    try:
        res = finnhub_client.fetch_company_fundamentals(symbol)
        if res and res.get("data") is not None:
            return res
    except Exception:
        pass

    # Fallback: try public sources (Yahoo via yfinance)
    try:
        yf_res = scrapers.fetch_yahoo_fundamentals(symbol)
        if yf_res and yf_res.get("data") is not None:
            return yf_res
    except Exception:
        pass

    # If all providers fail, return a clear unavailable payload
    return {"data": None, "meta": {"source": "verified-fundamentals", "note": "Verified data not available"}}
