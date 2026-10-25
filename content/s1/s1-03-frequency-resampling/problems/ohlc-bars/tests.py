import numpy as np
import pandas as pd

T = pd.to_datetime(["2024-01-02 09:00:10", "2024-01-02 09:02:30", "2024-01-02 09:04:50", "2024-01-02 09:16:20"])
P = pd.Series([100.0, 101.5, 99.0, 103.0], index=T)
rng = np.random.default_rng(21)
secs = np.sort(rng.choice(3600 * 6, 400, replace=False))
BIG = pd.Series(100 + rng.normal(0, 1, 400).cumsum(), index=pd.Timestamp("2024-03-01 10:00:00") + pd.to_timedelta(secs, unit="s"))
BIG.index = BIG.index.sort_values()

CASES = [
    {"name": "gap of two bins", "call": "ohlc_bars(P, '5min')",
     "expected": "pd.DataFrame({'open': [100.0, 99.0, 99.0, 103.0], 'high': [101.5, 99.0, 99.0, 103.0], 'low': [99.0, 99.0, 99.0, 103.0], 'close': [99.0, 99.0, 99.0, 103.0]}, index=pd.date_range('2024-01-02 09:00', periods=4, freq='5min'))", "visible": True},
    {"name": "one bin only", "call": "ohlc_bars(P.iloc[:3], '1h')",
     "expected": "pd.DataFrame({'open': [100.0], 'high': [101.5], 'low': [99.0], 'close': [99.0]}, index=pd.date_range('2024-01-02 09:00', periods=1, freq='h'))", "visible": True},
    {"name": "single trade", "call": "ohlc_bars(P.iloc[:1], '5min')",
     "expected": "pd.DataFrame({'open': [100.0], 'high': [100.0], 'low': [100.0], 'close': [100.0]}, index=pd.date_range('2024-01-02 09:00', periods=1, freq='5min'))"},
    {"name": "daily bars", "call": "ohlc_bars(pd.Series([10.0, 12.0, 11.0], index=pd.to_datetime(['2024-01-01 10:00', '2024-01-01 15:00', '2024-01-04 09:00'])), 'D')",
     "expected": "pd.DataFrame({'open': [10.0, 12.0, 12.0, 11.0], 'high': [12.0, 12.0, 12.0, 11.0], 'low': [10.0, 12.0, 12.0, 11.0], 'close': [12.0, 12.0, 12.0, 11.0]}, index=pd.date_range('2024-01-01', periods=4, freq='D'))"},
    {"name": "random 400 trades, 10min", "call": "ohlc_bars(BIG, '10min')"},
    {"name": "random 400 trades, 1min (many empty bins)", "call": "ohlc_bars(BIG, '1min')"},
]
