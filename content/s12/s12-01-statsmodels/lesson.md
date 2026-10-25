---
id: s12-01-statsmodels
title: statsmodels: tests, ACF/PACF and STL
minutes: 30
level: intermediate
goals: [Run adfuller and read its p-value, Compute and read acf and pacf, Split a series with STL and use the pieces]
prereqs: [s11-08-anomaly-detection-at-large-companies]
tags: [statsmodels, adfuller, acf, pacf, STL, stationarity]
skills: [statsmodels, stationarity, acf-pacf, decomposition]
---

## Warm-up

```check
{"q": "A random walk is...", "type": "single",
 "options": ["Stationary", "Non-stationary, but its first difference is stationary", "Always seasonal"],
 "answer": 1,
 "why": ["Its variance grows with time, so it is not stationary.", "Correct: the differences are the white-noise steps.", "A random walk has no season."]}
```

```check
{"q": "What does the ACF at lag 7 measure?", "type": "single",
 "options": ["Correlation between values 7 steps apart", "The mean of every 7th value", "The trend slope"],
 "answer": 0,
 "why": ["Correct.", "That is a seasonal average, not the ACF.", "The slope is a different statistic."]}
```

## Why it matters

**[[statsmodels]]** is the classic Python library for statistics and time series. It is not the fastest or the newest. But it is everywhere: in tutorials, in interviews, and in the code of colleagues. Its tests and plots are the first tools you use on any new series. They include stationarity tests, ACF and decomposition. Use them before you choose a model. It also runs **in your browser** on this site. So you can practise with real code in the problems of this stage.

## Library map: what is inside

| Module | Main tools |
|---|---|
| `statsmodels.tsa.stattools` | `adfuller`, `kpss`, `acf`, `pacf`, `ccf`, `acovf`, `grangercausalitytests` |
| `statsmodels.tsa.seasonal` | `seasonal_decompose`, `STL`, `MSTL` |
| `statsmodels.tsa.holtwinters` | `SimpleExpSmoothing`, `Holt`, `ExponentialSmoothing` |
| `statsmodels.tsa.exponential_smoothing.ets` | `ETSModel` (state-space ETS with AIC) |
| `statsmodels.tsa.arima.model` | `ARIMA` |
| `statsmodels.tsa.statespace.sarimax` | `SARIMAX` (seasonal ARIMA, exogenous variables) |
| `statsmodels.graphics.tsaplots` | `plot_acf`, `plot_pacf` |

The next lesson covers the models. Here we start with the tools for looking at the data.

## Stationarity tests

Many models need a **[[stationary]]** series (stable mean and variance). Two tests are standard:

- **[[ADF test|ADF]]** (`adfuller`): null hypothesis = the series has a **[[unit root]]** (non-stationary). A small [[p-value]] (for example below 0.05) means: reject, so the series looks stationary.
- **KPSS** (`kpss`): null hypothesis = the series **is** stationary. A small p-value means non-stationary. It is the opposite direction, so use both to cross-check.

```python
from statsmodels.tsa.stattools import adfuller
stat, pvalue, usedlag, nobs, crit, icbest = adfuller(x, autolag="AIC")
```

Read it like this: p-value 0.01, "stationary"; p-value 0.60, "not stationary: try differencing".

```check
{"q": "adfuller returns a p-value of 0.72 for a series. What do you do?", "type": "single",
 "options": ["Conclude the series is stationary", "Do not reject the unit root; difference the series and test again", "Remove the p-value", "Use a smaller alpha"],
 "answer": 1,
 "why": ["A large p-value means we cannot reject non-stationarity.", "Correct: difference once and re-run the test.", "The p-value is the evidence.", "A smaller alpha makes rejection harder."]}
```

## ACF and PACF

- **[[ACF]]**: correlation of the series with itself at lag `k`.
- **[[PACF]]**: correlation at lag `k` after removing the effect of the lags in between.

Simple guides for choosing ARIMA orders on a stationary series: An AR(p) process has a PACF that **cuts off** after lag p. An MA(q) process has an ACF that **cuts off** after lag q. A seasonal series shows peaks at multiples of the season length.

```python
from statsmodels.tsa.stattools import acf, pacf
r = acf(x, nlags=30, fft=True)            # array of length 31: r[0] = 1
p = pacf(x, nlags=30)                     # array of length 31
r, ci = acf(x, nlags=30, alpha=0.05)      # also returns confidence intervals
```

Bars outside the confidence band (about ±1.96/√n) are "significant".

```widget
{"name": "acf", "params": {}}
```

```check
{"q": "The PACF of a stationary series has a big spike at lag 1 and nothing after. Which model is suggested?", "type": "single",
 "options": ["AR(1)", "MA(1)", "White noise", "Seasonal AR(7)"],
 "answer": 0,
 "why": ["Correct: the PACF cuts off after lag 1.", "An MA(1) shows the cut-off in the ACF.", "White noise has no spikes.", "A seasonal AR would show a spike at lag 7."]}
```

## STL decomposition

**[[STL]]** (Seasonal-Trend decomposition using Loess) splits a series into trend, seasonal and residual:

```python
from statsmodels.tsa.seasonal import STL
res = STL(y, period=7, robust=True).fit()
res.trend, res.seasonal, res.resid
```

Why STL and not `seasonal_decompose`? STL lets the seasonal shape change slowly and handles any period. It has a **robust** option, so outliers do not distort the trend. Uses: see the pattern, **deseasonalise** before modelling, and detect anomalies in the residual (as in S-H-ESD).

```chart
{"title": "A series, its trend and its seasonal part", "x": "day", "height": 230,
 "series": [
   {"name": "series", "gen": [["trend", {"start": 50, "slope": 0.3}], ["season", {"period": 7, "amp": 8}], ["noise", {"sd": 1.5}]], "n": 98, "seed": 8},
   {"name": "trend", "gen": [["trend", {"start": 50, "slope": 0.3}]], "n": 98, "dash": true}
 ],
 "caption": "STL separates the dashed trend from the weekly pattern. The rest is the residual."}
```

```check
{"q": "Why use robust=True in STL?", "type": "single",
 "options": ["It makes the code faster", "Outliers have less influence on the trend and seasonal parts", "It removes the trend", "It forces a multiplicative model"],
 "answer": 1,
 "why": ["Speed is not the aim.", "Correct.", "It does not remove the trend.", "STL is additive; for multiplicative effects use a log transform."]}
```

## Worked example

We build a daily series with trend and a weekly season. We test it, difference it, find the season in the ACF, and run STL.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, acf
from statsmodels.tsa.seasonal import STL

rng = np.random.default_rng(0)
idx = pd.date_range("2024-01-01", periods=210, freq="D")
t = np.arange(len(idx))
y = pd.Series(50 + 0.3 * t + 8 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 1.5, len(t)), index=idx)

print("ADF p-value, raw       :", round(adfuller(y, autolag="AIC")[1], 3))
print("ADF p-value, 1st diff  :", round(adfuller(y.diff().dropna(), autolag="AIC")[1], 3))

r = acf(y.diff().dropna(), nlags=14, fft=True)
print("strongest ACF lag in 2..14:", int(np.argmax(r[2:]) + 2))

res = STL(y, period=7, robust=True).fit()
print("trend slope per day:", round((res.trend.iloc[-1] - res.trend.iloc[0]) / (len(y) - 1), 3))
print("seasonal range     :", round(float(res.seasonal.max() - res.seasonal.min()), 1))
print("residual std       :", round(float(res.resid.std()), 2))
# Output:
# ADF p-value, raw       : 0.857
# ADF p-value, 1st diff  : 0.0
# strongest ACF lag in 2..14: 7
# trend slope per day: 0.296
# seasonal range     : 18.4
# residual std       : 1.24
```

The raw series has a trend, so ADF does not reject the unit root. After one difference the p-value is tiny. The ACF finds the weekly period 7. STL recovers a trend slope near the true 0.3. It finds a seasonal range of about 18. The clean wave has range 16, and a little noise leaks in. The residual standard deviation is near the noise level 1.5.

## Common mistakes

- Reading a large ADF p-value as "stationary". The null hypothesis is non-stationarity.
- Testing a series that still has a strong season: the test can mislead. Deseasonalise or use seasonal differencing first.
- Differencing more than needed (over-differencing creates negative autocorrelation).
- Using `seasonal_decompose` with a centered moving average for forecasting: it has no values at the edges.
- Forgetting `period` in STL, or giving a series without a regular index.
- Using ACF on a series with a trend: it decays very slowly and hides the season.

## Interview lens

**Typical question:** "How do you check if a series is stationary, and what do you do if it is not?"

**Strong answer:** I look at the plot first. Then I run the ADF test, whose null hypothesis is a unit root. I cross-check with KPSS, whose null is stationarity. If the series is not stationary I take a first difference. For a strong season I take a seasonal difference. Then I test again. I use ACF and PACF on the stationary series to see AR and MA structure and the season length. I use STL with robust fitting to split trend, season and residual, and I look at the residual for outliers. For forecasting I still validate with a rolling backtest, not only tests.

**Red flags:** "p-value above 0.05 means stationary". Differencing automatically many times. No plot.

## Real world

statsmodels is a long-standing open-source project. Its tsa module has existed for many years. Other libraries use it as a reference implementation. The ADF test goes back to Dickey and Fuller (1979), and STL to Cleveland and others (1990). Many forecasting tutorials, university courses and interview questions use exactly these tools.

## Key points

- `adfuller`: null = unit root. Small p-value means stationary. Pair with `kpss`.
- `acf` and `pacf` show structure: AR order from the PACF cut-off, MA order from the ACF cut-off, seasons from peaks.
- `STL(y, period=m, robust=True)` gives trend, seasonal and residual.
- Difference to remove a trend; do not over-difference.
- statsmodels runs in the browser here, so you can practise with the problems.
