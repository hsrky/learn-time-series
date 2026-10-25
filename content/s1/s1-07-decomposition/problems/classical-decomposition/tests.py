import numpy as np
import pandas as pd

def D(n, freq="D"):
    return pd.date_range("2024-01-01", periods=n, freq=freq)

nan = np.nan
S1 = pd.Series([1, 3, 1, 3, 1, 3.0], index=D(6))
# quarterly data: trend 12 + 0.5 per step (rises 2 per year) plus the season [-2.75, 0.75, 4.25, -2.25]
S2 = pd.Series([10, 14, 18, 12, 12, 16, 20, 14, 14, 18, 22, 16.0], index=D(12, "MS"))
S3 = pd.Series([2, 3, 4, 2, 3, 5, 2, 4, 6, 2.0], index=D(10))

rng = np.random.default_rng(41)
t = np.arange(120)
BIG_ADD = pd.Series(50 + 0.4 * t + 8 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 1.5, 120), index=D(120, "MS"))
BIG_MUL = pd.Series((50 + 0.4 * t) * (1 + 0.2 * np.sin(2 * np.pi * t / 7)) * rng.uniform(0.97, 1.03, 120), index=D(120))
ODD = pd.Series(20 + 0.2 * np.arange(53) + np.tile([3, -1, -2, 0, 1.0], 11)[:53] + rng.normal(0, 0.3, 53), index=D(53))

CASES = [
    {"name": "period 2", "call": "classical_decompose(S1, 2)",
     "expected": "pd.DataFrame({'trend': [nan, 2.0, 2.0, 2.0, 2.0, nan], 'seasonal': [-1.0, 1.0, -1.0, 1.0, -1.0, 1.0], 'resid': [nan, 0.0, 0.0, 0.0, 0.0, nan]}, index=S1.index)", "visible": True},
    {"name": "quarterly, period 4", "call": "classical_decompose(S2, 4)",
     "expected": "pd.DataFrame({'trend': [nan, nan, 13.75, 14.25, 14.75, 15.25, 15.75, 16.25, 16.75, 17.25, nan, nan], 'seasonal': [-2.75, 0.75, 4.25, -2.25] * 3, 'resid': [nan, nan] + [0.0] * 8 + [nan, nan]}, index=S2.index)", "visible": True},
    {"name": "odd period, multiplicative", "call": "classical_decompose(S3, 3, 'multiplicative')", "visible": True},
    {"name": "seasonal sums to zero", "call": "round(float(classical_decompose(BIG_ADD, 12)['seasonal'].iloc[:12].sum()), 8)", "expected": "0.0"},
    {"name": "multiplicative seasonal averages 1", "call": "round(float(classical_decompose(BIG_MUL, 7, 'multiplicative')['seasonal'].iloc[:7].mean()), 8)", "expected": "1.0"},
    {"name": "components add back up", "call": "d = classical_decompose(BIG_ADD, 12)\nbool(np.allclose((d.trend + d.seasonal + d.resid).dropna(), BIG_ADD[d.trend.notna()]))", "expected": "True"},
    {"name": "NaN edges for even period", "call": "int(classical_decompose(BIG_ADD, 12)['trend'].isna().sum())", "expected": "12"},
    {"name": "NaN edges for odd period", "call": "int(classical_decompose(ODD, 5)['trend'].isna().sum())", "expected": "4"},
    {"name": "random monthly additive", "call": "classical_decompose(BIG_ADD, 12)"},
    {"name": "random weekly multiplicative", "call": "classical_decompose(BIG_MUL, 7, 'multiplicative')"},
    {"name": "random odd period 5", "call": "classical_decompose(ODD, 5)"},
]
