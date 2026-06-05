import os
import pytest
pytest.importorskip("requests")
from backend.app.core import finnhub_client


def test_finnhub_no_api_key(monkeypatch):
    # Ensure no API key is present
    monkeypatch.delenv("FINNHUB_API_KEY", raising=False)
    res = finnhub_client.fetch_company_fundamentals("RELIANCE")
    assert res is not None
    assert res.get("data") is None
    assert isinstance(res.get("meta"), dict)
    assert "note" in res.get("meta") or res.get("meta").get("components") is not None
