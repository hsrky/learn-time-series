---
id: s3-07-sarima-model-selection
title: SARIMA, model selection and residual checks
minutes: 40
level: intermediate
goals: [Read the SARIMA(p,d,q)(P,D,Q)m notation, Compare models with AIC and BIC, Check residuals with the ACF and the Ljung-Box test, Follow a clear model-building workflow, Fit a SARIMAX model with statsmodels]
prereqs: [s3-06-ma-arma-arima, s2-04-unit-root-adf-kpss]
tags: [sarima, aic, bic, ljung-box, statsmodels]
skills: [backtest, from-scratch]
---

## Warm-up

```check
{"q": "In ARIMA(p,d,q), what does d control?", "type": "single",
 "options": ["How many times the series is differenced", "How many past values are used", "How many shocks are used"],
 "answer": 0,
 "why": ["Correct: d is the number of differences.", "That is p, the AR order.", "That is q, the MA order."]}
```

```check
{"q": "Monthly data with a yearly pattern. What seasonal difference lag removes the pattern?", "type": "numeric",
 "answer": 12, "tol": 0.001,
 "why": "Compare each month with the same month last year: lag m = 12."}
```

## Why it matters

Real series often have trend **and** season. ARIMA alone cannot handle a season well. **SARIMA** adds seasonal AR, difference and MA parts. But now there are many possible models. How do you choose one, and how do you know it is good? You need a clear process: compare models with a score (AIC or BIC), then check that the residuals are white noise. This workflow is a typical interview topic.

## SARIMA notation

SARIMA(p, d, q)(P, D, Q)m

- (p, d, q): the normal ARIMA part for the short-term pattern.
- (P, D, Q): the same three ideas, but on the **seasonal lags** m, 2m, 3m, ...
- m: the season length (12 for monthly data with a yearly pattern, 7 for daily data with a weekly pattern).

Meaning of the seasonal parts:

- D: number of **seasonal differences** y(t) − y(t−m). Usually 0 or 1.
- P: seasonal AR. The value depends on y(t−m), y(t−2m), ...
- Q: seasonal MA. The value depends on shocks ε(t−m), ε(t−2m), ...

Famous example: the **airline model**, SARIMA(0,1,1)(0,1,1)12 fitted to the log of monthly airline passengers. It has just two parameters and works well on many monthly series with trend and season.

```check
{"q": "What is the meaning of SARIMA(1,1,0)(0,1,1)7?", "type": "single",
 "options": ["Weekly season on daily data: one AR lag, one normal difference, one seasonal difference, one seasonal MA term", "Yearly season on monthly data", "Seven AR lags and one MA lag", "A model with no differencing"],
 "answer": 0,
 "why": ["Correct: m = 7, d = 1, D = 1, p = 1, Q = 1.", "m = 7 is a weekly cycle on daily data, not a yearly one on monthly data.", "The 7 is the season length m. It is not the AR order.", "d = 1 and D = 1, so there is differencing."]}
```

## Model selection: AIC and BIC

More parameters always fit the training data better. We need a score that **punishes complexity**.

AIC = 2k − 2·ln(L)

BIC = k·ln(n) − 2·ln(L)

- k: number of parameters in the model.
- n: number of observations.
- ln(L): the log-likelihood, a measure of how well the model fits (higher is better).
- **Lower AIC or BIC is better.**

Numbers: ln(L) = −100, k = 3, n = 50. AIC = 6 + 200 = 206. BIC = 3·ln(50) + 200 = 11.7 + 200 = 211.7.

BIC punishes complexity more than AIC when n > 7, so it prefers smaller models. For a Gaussian model you can use the shortcut AIC ≈ n·ln(SSE/n) + 2k, where SSE is the sum of squared residuals.

**Rules:**

- Compare AIC only between models fitted on the **same data** with the **same differencing**. A model with d = 1 has fewer data points than one with d = 0. So their AIC values cannot be compared.
- A difference of less than about 2 is not meaningful.
- AIC is only a guide. Check a backtest too.

```check
{"q": "Model A has AIC = 410 and model B has AIC = 402. Both use the same data and the same differencing. Which is preferred?", "type": "single",
 "options": ["Model B", "Model A", "They are equal", "Cannot say without the test set"],
 "answer": 0,
 "why": ["Correct: lower AIC is better, and 8 points is a clear gap.", "Model A has the higher (worse) AIC.", "A gap of 8 is more than the usual 2 points.", "AIC is computed on the training data and is already a guide for selection."]}
```

## Residual diagnostics

A good model leaves residuals that look like **white noise**. Check three things:

1. **Plot** the residuals. No pattern, no change in spread.
2. **ACF of the residuals**: all bars inside the ±1.96/√n band.
3. **Ljung-Box test**: a single p-value for "no autocorrelation up to lag h".

The Ljung-Box statistic:

Q = n·(n+2)·Σ r(k)² / (n − k), summed for k = 1..h

- r(k): the autocorrelation of the residuals at lag k.
- h: the number of lags tested (for example 10, or 2·m for seasonal data).
- Under H0 (white noise), Q follows a chi-square distribution with h − (number of fitted ARMA parameters) degrees of freedom.

**Null hypothesis: the residuals are white noise.** A **large** p-value (above 0.05) is good: no evidence of leftover pattern. A small p-value means the model missed something.

```chart
{"title": "AIC of four candidate models on a monthly series (lower is better)", "x": "model number", "height": 210,
 "series": [{"name": "AIC", "kind": "bar", "x": [1, 2, 3, 4], "y": [1190.1, 1000.4, 895.7, 893.8]}],
 "caption": "Model 1: no season term. Model 2: seasonal AR. Models 3 and 4: seasonal difference and seasonal MA. The seasonal difference makes the big gain."}
```

```check
{"q": "Ljung-Box on the residuals gives p = 0.003. What do you conclude?", "type": "single",
 "options": ["The residuals still have autocorrelation: the model missed a pattern", "The model is good", "The data is stationary", "The test is wrong"],
 "answer": 0,
 "why": ["Correct: H0 is 'white noise'. A small p-value rejects it.", "A good model would give a large p-value.", "The test is about residuals, not about the raw data.", "The result is a valid warning."]}
```

## A workflow you can explain

1. **Plot** the series. Find trend, season and variance changes.
2. **Stabilise**: log or Box-Cox if the spread grows.
3. **Pick d and D**: difference until stationary, and no more.
4. **Look** at ACF and PACF of the differenced series for starting orders.
5. **Fit** a few small candidates. Compare AIC (and BIC).
6. **Check** residuals: plot, ACF, Ljung-Box.
7. **Backtest** the best one or two against seasonal naive on rolling origins.
8. **Forecast** with intervals and refit regularly.

## Fitting SARIMAX in statsmodels

`SARIMAX(y, order=(p,d,q), seasonal_order=(P,D,Q,m)).fit()` gives a result with `.aic`, `.bic`, `.resid`, `.forecast(h)` and `.summary()`. The X stands for optional **exogenous** variables (extra input columns). Use `disp=False` to hide the optimiser messages.

## Worked example

We simulate monthly data with a trend and a yearly season. We fit four models on the first 18 years, compare them, check residuals, and test on the last 2 years. The code needs the `statsmodels` library, and the output is real.

```python
import warnings
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")

rng = np.random.default_rng(10)
n = 240
t = np.arange(n)
y = 50 + 0.1 * t + 8 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 2, n)
train, test = y[:216], y[216:]            # 18 years to fit, 2 years to test

candidates = [
    ((1, 1, 0), (0, 0, 0, 0)),            # no seasonal part
    ((1, 0, 0), (1, 1, 0, 12)),           # seasonal AR + seasonal difference
    ((1, 1, 1), (0, 1, 1, 12)),
    ((0, 1, 1), (0, 1, 1, 12)),           # the "airline" form
]
print("order, seasonal_order, AIC, BIC, test MAE, Ljung-Box p (lag 12)")
for order, sorder in candidates:
    fit = SARIMAX(train, order=order, seasonal_order=sorder).fit(disp=False)
    forecast = fit.forecast(24)
    resid = fit.resid[13:]                # skip the start-up residuals
    p_value = float(acorr_ljungbox(resid, lags=[12], return_df=True)["lb_pvalue"].iloc[0])
    mae = np.mean(np.abs(test - forecast))
    print(order, sorder, round(fit.aic, 1), round(fit.bic, 1), round(mae, 2), round(p_value, 3))

# baseline: seasonal naive (repeat the last year)
snaive = np.tile(train[-12:], 2)
print("seasonal naive test MAE:", round(np.mean(np.abs(test - snaive)), 2))
# Output:
# order, seasonal_order, AIC, BIC, test MAE, Ljung-Box p (lag 12)
# (1, 1, 0) (0, 0, 0, 0) 1190.1 1196.8 5.46 0.0
# (1, 0, 0) (1, 1, 0, 12) 1000.4 1010.3 2.69 0.0
# (1, 1, 1) (0, 1, 1, 12) 895.7 909.0 1.45 0.986
# (0, 1, 1) (0, 1, 1, 12) 893.8 903.8 1.43 0.986
# seasonal naive test MAE: 2.53
```

The seasonal difference gives a big drop in AIC and in test error. The last two models also pass the Ljung-Box test (large p-value). They beat the seasonal naive baseline.

## Common mistakes

- Comparing AIC across different differencing orders or different data.
- Choosing the model with the best AIC and skipping the residual check.
- Using the Ljung-Box test with too few lags.
- Forgetting that the degrees of freedom shrink with the number of fitted parameters.
- Forgetting the season length m or using the wrong one.
- Searching a huge grid of orders. It overfits the selection, so confirm with a backtest.
- Never comparing with seasonal naive.

## Interview lens

**Typical question:** "How do you select and validate a SARIMA model?"

**Strong answer:** First I make the series stable. I use a transform and differencing: d for the trend and D for the season. I decide with plots and unit-root tests. I look at ACF and PACF for starting orders and fit a few small candidates. I compare them by AIC or BIC on the same differenced data. Then I check that the residuals are white noise with a residual ACF and the Ljung-Box test. Finally I backtest on rolling origins against the seasonal naive baseline, because AIC measures in-sample fit and not forecast accuracy.

**Red flags:** Comparing AIC across different d. Trusting AIC alone. Never checking residuals. Not knowing what the null hypothesis of Ljung-Box is.

## Real world

- Box and Jenkins introduced the airline model in their 1970 book. They used monthly totals of international airline passengers from 1949 to 1960.
- The `auto.arima` function in the R forecast package, and `pmdarima` in Python, automate the search over orders using AIC (or AICc). They are common starting points in industry.

## Key points

- SARIMA(p,d,q)(P,D,Q)m adds seasonal AR, difference and MA terms at lag m.
- AIC = 2k − 2 ln L and BIC = k ln n − 2 ln L. Lower is better. Compare only on the same data and the same differencing.
- Good residuals are white noise: no ACF bars outside the band and a large Ljung-Box p-value.
- Workflow: plot, stabilise, difference, fit a few small models, compare, check residuals, backtest against seasonal naive.
