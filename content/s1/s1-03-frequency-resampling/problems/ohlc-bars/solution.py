import pandas as pd


def ohlc_bars(prices, freq):
    """Return open/high/low/close bars; empty bins repeat the previous close."""
    bars = prices.resample(freq).ohlc()                  # NaN rows for empty bins
    bars["close"] = bars["close"].ffill()                # last known price, past only
    for col in ["open", "high", "low"]:
        bars[col] = bars[col].fillna(bars["close"])      # empty bin: flat bar at the last close
    return bars[["open", "high", "low", "close"]]
