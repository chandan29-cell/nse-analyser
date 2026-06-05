from .data_fetcher import fetch_price_history, fetch_company_fundamentals
from .indicators import compute_indicators
import pandas as pd
import numpy as np


def generate_trading_signal(indicators: dict, latest_close: float):
    # Basic rule-based mapping
    try:
        ema20 = indicators.get("ema20")
        ema50 = indicators.get("ema50")
        rsi = indicators.get("rsi14")
        macd_hist = indicators.get("macd", {}).get("hist")
        if None in (ema20, ema50, rsi, macd_hist):
            return "Watchlist"
        if ema20 > ema50 and rsi < 70 and macd_hist > 0:
            return "Buy"
        if ema20 < ema50 and rsi > 70:
            return "Avoid"
        return "Hold"
    except Exception:
        return "Watchlist"


def generate_investing_signal(fundamentals: dict):
    # fundamentals['data'] may be None
    if not fundamentals or fundamentals.get("data") is None:
        return "Hold"
    data = fundamentals.get("data")
    # minimal checks
    pe = data.get("pe")
    roe = data.get("roe")
    if pe and roe and roe > 15 and pe < 25:
        return "Long-term Buy"
    return "Hold"


def combine_scores(indicators: dict, fundamentals: dict):
    # Technical trend 30, Momentum 20, Volume 15, Risk-reward 15, PEAD/SEAD 10, Sentiment 10
    t = 0.0
    # Simple proxies
    ema20 = indicators.get("ema20")
    ema50 = indicators.get("ema50")
    if ema20 and ema50:
        t += 30 if ema20 > ema50 else 0
    rsi = indicators.get("rsi14")
    if rsi:
        t += max(0, (50 - abs(50 - rsi)) / 50) * 20
    # volume confirmation and risk-reward approximate
    t += 15 * 0.5
    t += 15 * 0.5
    # PEAD/SEAD and sentiment unavailable -> 0
    score = t
    return min(100, score)


def analyze_stock(symbol: str):
    # Fetch price history
    ph = fetch_price_history(symbol)
    fundamentals = fetch_company_fundamentals(symbol)
    if ph["data"] is None:
        return {
            "symbol": symbol,
            "price_source": ph["meta"],
            "indicators": {},
            "technical": {},
            "fundamental": fundamentals,
            "trading_score": None,
            "investing_score": None,
            "trading_signal": "Data unavailable",
            "investing_signal": "Data unavailable",
        }
    df = ph["data"]
    ind = compute_indicators(df)
    latest_close = df["Close"].iloc[-1]
    trading_signal = generate_trading_signal(ind, latest_close)
    investing_signal = generate_investing_signal(fundamentals)
    trading_score = combine_scores(ind, fundamentals)
    investing_score = None
    return {
        "symbol": symbol,
        "price_source": ph["meta"],
        "indicators": ind,
        "technical": {"latest_close": float(latest_close)},
        "fundamental": fundamentals,
        "trading_score": float(trading_score),
        "investing_score": investing_score,
        "trading_signal": trading_signal,
        "investing_signal": investing_signal,
    }
