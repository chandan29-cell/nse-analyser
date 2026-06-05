import datetime
import yfinance as yf
from typing import Any, Dict
import requests


def _now_iso():
    return datetime.datetime.utcnow().isoformat()


def fetch_yahoo_fundamentals(symbol: str) -> Dict[str, Any]:
    """Fallback fundamentals fetcher using yfinance (public Yahoo data).

    Returns {'data': {...} | None, 'meta': {...}}
    """
    meta = {"source": "yahoo_finance", "symbol": symbol, "fetched_at": _now_iso(), "url": f"https://finance.yahoo.com/quote/{symbol}"}
    try:
        ticker = yf.Ticker(symbol)
        # yfinance provides `get_info()` in newer versions, fall back to `info` attribute
        info = None
        if hasattr(ticker, "get_info"):
            try:
                info = ticker.get_info()
            except Exception:
                info = getattr(ticker, "info", None)
        else:
            info = getattr(ticker, "info", None)

        if not info:
            return {"data": None, "meta": {**meta, "note": "Data unavailable"}}

        fields = [
            "marketCap",
            "trailingPE",
            "forwardPE",
            "trailingEps",
            "epsForward",
            "beta",
            "dividendYield",
            "fiftyTwoWeekHigh",
            "fiftyTwoWeekLow",
            "sector",
            "fullTimeEmployees",
            "longBusinessSummary",
        ]
        extracted = {k: info.get(k) for k in fields}
        return {"data": extracted, "meta": meta}
    except Exception as e:
        return {"data": None, "meta": {**meta, "error": str(e), "note": "Data unavailable"}}


def fetch_html(url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Fetches raw HTML for a given URL and returns page text plus metadata.

    This is a simple helper for scraping public pages when APIs are not available.
    It does not attempt heavy parsing — callers should parse the returned HTML
    with BeautifulSoup if needed.
    """
    meta = {"source": "html_fetch", "url": url, "fetched_at": datetime.datetime.utcnow().isoformat()}
    try:
        h = {"User-Agent": "Mozilla/5.0 (compatible; NSE-Analyser/1.0)"}
        if headers:
            h.update(headers)
        resp = requests.get(url, headers=h, timeout=15)
        if resp.status_code != 200:
            return {"data": None, "meta": {**meta, "status_code": resp.status_code, "note": "Data unavailable"}}
        return {"data": resp.text, "meta": meta}
    except Exception as e:
        return {"data": None, "meta": {**meta, "error": str(e), "note": "Data unavailable"}}
