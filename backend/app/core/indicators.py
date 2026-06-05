import pandas as pd
import numpy as np


def ema(series: pd.Series, span: int):
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period).mean()
    ma_down = down.rolling(window=period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger_bands(series: pd.Series, window: int = 20, n_std: int = 2):
    ma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper = ma + (std * n_std)
    lower = ma - (std * n_std)
    return upper, ma, lower


def adx(df: pd.DataFrame, period: int = 14):
    # Basic ADX implementation
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()
    return adx


def support_resistance(series: pd.Series, window: int = 20):
    # simple support/resistance as rolling min/max
    support = series.rolling(window=window).min()
    resistance = series.rolling(window=window).max()
    return support, resistance


def compute_indicators(df: pd.DataFrame):
    out = {}
    close = df["Close"]
    out["ema20"] = ema(close, 20).iloc[-1]
    out["ema50"] = ema(close, 50).iloc[-1]
    out["ema100"] = ema(close, 100).iloc[-1]
    out["ema200"] = ema(close, 200).iloc[-1]
    out["rsi14"] = rsi(close, 14).iloc[-1]
    macd_line, signal_line, hist = macd(close)
    out["macd"] = {"macd": macd_line.iloc[-1], "signal": signal_line.iloc[-1], "hist": hist.iloc[-1]}
    upper, ma, lower = bollinger_bands(close)
    out["bollinger"] = {"upper": upper.iloc[-1], "middle": ma.iloc[-1], "lower": lower.iloc[-1]}
    try:
        out["adx"] = adx(df).iloc[-1]
    except Exception:
        out["adx"] = None
    support, resistance = support_resistance(close)
    out["support"] = support.iloc[-1]
    out["resistance"] = resistance.iloc[-1]
    # simple stoploss/targets: use recent ATR proxy
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - df["Close"].shift()).abs(), (df["Low"] - df["Close"].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean().iloc[-1]
    out["stop_loss"] = close.iloc[-1] - 1.5 * atr
    out["target1"] = close.iloc[-1] + 1.5 * atr
    out["target2"] = close.iloc[-1] + 3 * atr
    out["position_size_suggestion"] = None
    return out
