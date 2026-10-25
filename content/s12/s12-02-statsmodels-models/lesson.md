---
id: s12-02-statsmodels-models
title: statsmodels models: Holt-Winters, ETS, ARIMA and SARIMAX
minutes: 30
level: intermediate
goals: [Fit Holt-Winters, ARIMA and SARIMAX with statsmodels, Get forecasts with prediction intervals, Compare models with AIC and a holdout, and check residuals]
prereqs: [s12-01-statsmodels]
tags: [statsmodels, ARIMA, SARIMAX, ETS, Holt-Winters, AIC, forecast]
skills: [statsmodels, arima, exponential-smoothing]
---

## Warm-up

```check
{"q": "ADF p-value 0.80 means...", "type": "single",
 "options": ["Looks stationary", "Cannot reject a unit root: difference and test again", "The series is seasonal"],
 "answer": 1,
 "why": ["A large p-value does not show stationarity.", "Correct.", "ADF does not test for seasonality."]}
```

```check
{"q": "An MA(2) process has an ACF that...", "type": "single",
 "options": ["Cuts off after lag 2", "Cuts off after lag 1", "Never cuts off"],
 "answer": 0,
 "why": ["Correct.", "That is MA(1).", "Pure AR processes have ACF that decays; MA cuts off."]}
```

## Why it matters

Once you know the data, you fit a model. statsmodels offers the classic ones in a consistent way. Create a model object, call `.fit()`, then call `.forecast(h)` or `.get_forecast(h)`. This pattern, and reading `AIC`, `summary()` and residual tests, is what interviewers expect from a Python forecaster. These models are also your **baselines**: any complex model must beat them.

## The pattern

```python
model = SomeModel(train, ...settings...)   # nothing is estimated yet
fit = model.fit()                           # parameters are estimated
fit.summary()                               # table of coefficients and tests
fit.aic                                     # lower is better (compare on the SAME data)
fit.forecast(h)                             # point forecasts
fit.get_forecast(h).summary_frame(alpha=0.2)   # mean and 80% interval (for ARIMA/SARIMAX)
fit.resid                                   # residuals for diagnostics
```

## Exponential smoothing: Holt-Winters and ETS

`ExponentialSmoothing` (in `holtwinters`) implements [[Holt-Winters]]:

- `trend=None | "add"`, optional `damped_trend=True`
- `seasonal=None | "add" | "mul"`, with `seasonal_periods=m`

`ETSModel` (in `exponential_smoothing.ets`) is the state-space version with `error`, `trend`, `seasonal` choices. It gives proper AIC values and prediction intervals, so you can compare many ETS variants.

Choose `"add"` when the seasonal swing is constant. Choose `"mul"` when the swing grows with the level (data must be positive).

```check
{"q": "Weekly sales swing by ±10% of the level, and the level doubles over the year. Which seasonal type?", "type": "single",
 "options": ["add", "mul", "None", "damped"],
 "answer": 1,
 "why": ["With additive seasonality, the swing stays at the same size in units.", "Correct: the swing grows with the level.", "There is a season.", "Damping is about the trend, not the season."]}
```

## ARIMA and SARIMAX

**[[ARIMA]](p, d, q)**: `p` autoregressive terms, `d` differences, `q` moving-average terms. `statsmodels.tsa.arima.model.ARIMA(train, order=(p, d, q))`.

**[[SARIMAX]]** adds a **seasonal order** `(P, D, Q, m)`. It also adds **[[exogenous variable|exogenous]]** variables `exog`, which are outside information such as price or holidays. Example: `SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7))` is the classic "airline model" for a weekly season. It has one difference, one seasonal difference, one MA term and one seasonal MA term.

Practical points:

- Give the model a series with a regular `DatetimeIndex` (with frequency), or you get warnings.
- Seasonal models with large `m` (for example 365) are slow and use much memory. Use Fourier terms in `exog` instead.
- Use `fit(disp=False)` to hide the optimiser output.
- For future `exog`, you need its future values (known in advance).

```check
{"q": "SARIMAX seasonal_order=(0, 1, 1, 12) means...", "type": "single",
 "options": ["One seasonal difference with period 12 and one seasonal MA term", "Twelve AR terms", "Twelve differences", "A trend of 12"],
 "answer": 0,
 "why": ["Correct: (P, D, Q, m) = (0, 1, 1, 12).", "P = 0 here, so there are no seasonal AR terms.", "D = 1, one seasonal difference of lag 12.", "m is the season length, not a trend."]}
```

## Choosing and checking

1. **Compare with [[AIC]]** on the *same* training data and the *same* differencing. AIC punishes extra parameters. You cannot compare AIC of models with a different number of differences.
2. **Check residuals.** If the model is good, the residuals look like white noise. `acorr_ljungbox(resid, lags=[10])` (the **[[Ljung-Box test]]**) returns a p-value. A small value (below 0.05) means there is still autocorrelation left.
3. **Holdout / rolling backtest.** AIC is about fit on past data. The forecast error on later data is the real test.
4. **Intervals.** Check that an 80% interval contains about 80% of the actuals.

```chart
{"title": "SARIMAX forecast with an 80% interval", "x": "day", "height": 240, "series": [{"name": "history", "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41], "y": [140.2, 147.3, 149.6, 144.5, 138.6, 133.0, 134.5, 143.6, 149.1, 153.6, 144.7, 142.0, 134.4, 136.9, 146.0, 153.0, 154.8, 152.7, 142.3, 135.2, 140.3, 144.2, 159.1, 157.8, 153.2, 149.4, 144.2, 142.4, 151.6, 160.8, 164.3, 155.7, 147.9, 145.1, 145.5, 154.7, 162.6, 161.5, 157.0, 145.2, 144.9, 150.5]}, {"name": "forecast", "x": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], "y": [156.1, 164.9, 166.4, 162.1, 153.5, 149.1, 151.7, 159.0, 167.7, 169.2, 164.9, 156.3, 152.0, 154.5], "dash": true}, {"name": "lower 80%", "x": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], "y": [153.4, 162.1, 163.7, 159.4, 150.8, 146.4, 149.0, 156.3, 165.0, 166.5, 162.2, 153.6, 149.2, 151.8], "dash": true}, {"name": "upper 80%", "x": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], "y": [158.8, 167.6, 169.1, 164.8, 156.2, 151.8, 154.4, 161.8, 170.4, 172.0, 167.6, 159.0, 154.7, 157.2], "dash": true}], "marks": [{"x": 42, "label": "forecast starts"}], "caption": "The interval gets wider when the horizon grows, because uncertainty adds up."}
```

```check
{"q": "Two models have AIC 600.5 and 904.2 on the same data. Which one do you prefer by AIC?", "type": "single",
 "options": ["600.5", "904.2", "They are equal", "AIC cannot be used"],
 "answer": 0,
 "why": ["Correct: lower AIC is better.", "A higher AIC means a worse fit/complexity trade-off.", "They differ a lot.", "AIC can be used when the models use the same data."]}
```

## Worked example

We fit three models on 140 days of data with trend and weekly season, and forecast the next 14 days.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

rng = np.random.default_rng(4)
idx = pd.date_range("2024-01-01", periods=154, freq="D")
t = np.arange(len(idx))
y = pd.Series(100 + 0.4 * t + 10 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 2, len(t)), index=idx)
train, test = y[:140], y[140:]

arima = ARIMA(train, order=(1, 1, 1)).fit()                              # no seasonal part
sarimax = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False)
hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=7).fit()

print(f"AIC ARIMA   {arima.aic:7.1f}")
print(f"AIC SARIMAX {sarimax.aic:7.1f}")

forecasts = {"SARIMAX": sarimax.forecast(14), "Holt-Winters": hw.forecast(14),
             "seasonal naive": pd.Series(np.resize(train.values[-7:], 14), index=test.index)}
for name, f in forecasts.items():
    print(f"MAE {name:<15} {np.mean(np.abs(test.values - np.asarray(f))):.2f}")

lb = acorr_ljungbox(sarimax.resid, lags=[10])
print("Ljung-Box p-value (lag 10):", round(float(lb["lb_pvalue"].iloc[0]), 3))
# Output:
# AIC ARIMA     904.2
# AIC SARIMAX   600.5
# MAE SARIMAX         1.41
# MAE Holt-Winters    1.42
# MAE seasonal naive  5.28
# Ljung-Box p-value (lag 10): 0.031
```

The seasonal models are much better than the non-seasonal ARIMA (AIC) and beat seasonal naive in MAE. SARIMAX and Holt-Winters are close. The Ljung-Box p-value is small, so a little autocorrelation is left in the residuals. A real project would try another order or add terms. Then it would compare again on a rolling backtest.

## Common mistakes

- Comparing AIC across models with different differencing or different data.
- Using an ARIMA without a seasonal part on seasonal data.
- Forgetting that SARIMAX needs future `exog` values for the forecast.
- Choosing the model only by AIC and skipping the backtest.
- Ignoring convergence warnings.
- Using a huge seasonal period such as 365 with SARIMAX.

## Interview lens

**Typical question:** "How would you build an ARIMA forecast for daily sales with a weekly season?"

**Strong answer:** I plot the data and check stationarity with ADF. I difference once for the trend and once seasonally with lag 7. I look at ACF and PACF to pick small orders, then I fit a few SARIMAX candidates and compare AIC. I check residuals with the Ljung-Box test and an ACF plot. The real choice comes from a rolling-origin backtest against seasonal naive and Holt-Winters, because those baselines are hard to beat. I use `get_forecast` for intervals and check their coverage. For many series I would use a faster library, or a global model.

**Red flags:** Choosing orders by guessing. No residual check. Comparing AIC across different differencing. Not testing a seasonal naive baseline.

## Real world

ARIMA goes back to Box and Jenkins (1970), and Holt-Winters to Holt (1957) and Winters (1960). Both families are still used in business forecasting and were strong in the M competitions. statsmodels' SARIMAX is flexible. Teams often use it for a quick, interpretable baseline. For thousands of series, faster libraries (see the Nixtla lesson) are common.

## Key points

- Pattern: model object, `.fit()`, `.forecast(h)`, `.aic`, `.resid`.
- `ExponentialSmoothing` or `ETSModel` for trend and season by smoothing; `ARIMA` and `SARIMAX` for autocorrelation, seasonal terms and exogenous variables.
- Compare AIC only on the same data and differencing; confirm with a holdout or rolling backtest.
- Check residuals (Ljung-Box) and interval coverage.
- Always include seasonal naive as a baseline.
