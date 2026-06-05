import pytest
pytest.importorskip("pandas")
pytest.importorskip("numpy")
import pandas as pd
import numpy as np
from backend.app.core import indicators, scoring


def make_sample_df():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=200)
    price = np.cumsum(np.random.randn(200)) + 100
    high = price + np.random.rand(200)
    low = price - np.random.rand(200)
    openp = price + np.random.randn(200) * 0.5
    close = price
    vol = np.random.randint(1000, 5000, size=200)
    df = pd.DataFrame({"High": high, "Low": low, "Open": openp, "Close": close, "Volume": vol}, index=dates)
    return df


def test_indicators_compute():
    df = make_sample_df()
    ind = indicators.compute_indicators(df)
    assert "ema20" in ind
    assert "rsi14" in ind


def test_scoring_analyze_sample(monkeypatch):
    # patch fetcher to return our synthetic dataframe
    df = make_sample_df().reset_index()

    def fake_fetch_price_history(symbol, period="6mo"):
        return {"data": df, "meta": {"source": "test", "symbol": symbol}}

    monkeypatch.setattr(scoring, "fetch_price_history", fake_fetch_price_history)
    monkeypatch.setattr(scoring, "fetch_company_fundamentals", lambda s: {"data": None, "meta": {"note": "none"}})
    res = scoring.analyze_stock("TEST.NS")
    assert res["symbol"] == "TEST.NS"
    assert res["trading_signal"] is not None
