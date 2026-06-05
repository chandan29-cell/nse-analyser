import pytest
pytest.importorskip("requests")

from backend.app.core.scrapers import fetch_html


def test_fetch_example():
    res = fetch_html("https://example.com")
    assert isinstance(res, dict)
    # data may be None if network blocked — ensure meta present
    assert "meta" in res or "data" in res
    if res.get("data"):
        assert "Example Domain" in res["data"]
