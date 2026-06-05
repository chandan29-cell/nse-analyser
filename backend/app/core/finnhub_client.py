"""Simple Finnhub integration for fundamentals and earnings.

Requires `FINNHUB_API_KEY` in environment to enable live requests.
If the key is missing or the API returns no data, functions return
`{"data": None, "meta": {...}}` and never fabricate values.
"""
import os
import requests
import datetime
from typing import Tuple, List, Dict, Any

BASE = "https://finnhub.io/api/v1"


def _get_api_key() -> str:
    return os.getenv("FINNHUB_API_KEY", "").strip()


def _now_iso():
    return datetime.datetime.utcnow().isoformat()


def _normalize_symbols(symbol: str) -> List[str]:
    s = symbol.strip()
    variants = [s]
    if not s.endswith(".NS"):
        variants.append(s + ".NS")
    if not s.startswith("NSE:"):
        variants.append("NSE:" + s.replace(".NS", ""))
    # de-duplicate preserving order
    seen = set()
    out = []
    for v in variants:
        if v not in seen:
            out.append(v)
            seen.add(v)
    return out


def _attempt_call(endpoint: str, symbol_variants: List[str], params: Dict[str, Any] = None) -> Tuple[Any, Dict[str, Any]]:
    """Try calling a Finnhub endpoint with a list of symbol variants.

    Returns (json_or_None, meta_dict)
    """
    key = _get_api_key()
    fetched_at = _now_iso()
    if not key:
        return None, {"source": "finnhub", "fetched_at": fetched_at, "note": "API key not configured"}

    last_err = None
    for sym in symbol_variants:
        try:
            p = dict(params or {})
            p.update({"symbol": sym, "token": key})
            url = f"{BASE}/{endpoint}"
            resp = requests.get(url, params=p, timeout=10)
            if resp.status_code == 200:
                j = resp.json()
                if j:
                    return j, {"source": "finnhub", "url": resp.url, "fetched_at": fetched_at}
                # empty payload -> keep trying other variants
            else:
                last_err = f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            last_err = str(e)

    return None, {"source": "finnhub", "fetched_at": fetched_at, "error": last_err, "note": "Data unavailable"}


def fetch_company_fundamentals(symbol: str) -> Dict[str, Any]:
    """Fetch combined fundamentals (metrics/profile/earnings).

    Returns: {"data": {...} | None, "meta": {...}}
    """
    variants = _normalize_symbols(symbol)
    metrics, metrics_meta = _attempt_call("stock/metric", variants, params={"metric": "all"})
    profile, profile_meta = _attempt_call("stock/profile2", variants, params={})
    earnings, earnings_meta = _attempt_call("stock/earnings", variants, params={})

    if metrics is None and profile is None and earnings is None:
        meta = {"source": "finnhub", "components": {"metrics": metrics_meta, "profile": profile_meta, "earnings": earnings_meta}, "fetched_at": _now_iso(), "note": "Data unavailable"}
        return {"data": None, "meta": meta}

    data = {"metrics": metrics, "profile": profile, "earnings": earnings}
    meta = {"source": "finnhub", "components": {}, "fetched_at": _now_iso()}
    if metrics_meta:
        meta["components"]["metrics"] = metrics_meta
    if profile_meta:
        meta["components"]["profile"] = profile_meta
    if earnings_meta:
        meta["components"]["earnings"] = earnings_meta

    return {"data": data, "meta": meta}


def fetch_earnings_history(symbol: str) -> Dict[str, Any]:
    variants = _normalize_symbols(symbol)
    earnings, emeta = _attempt_call("stock/earnings", variants, params={})
    if earnings is None:
        return {"data": None, "meta": emeta}
    return {"data": earnings, "meta": emeta}
