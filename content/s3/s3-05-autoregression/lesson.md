---
id: s3-05-autoregression
title: Autoregression AR(p) by least squares
minutes: 35
level: intermediate
goals: [Write the AR(p) model and explain each symbol, Fit AR(p) with numpy least squares, Forecast several steps ahead by recursion, Explain how the forecast returns to the mean, Choose p with the PACF and AIC]
prereqs: [s2-03-acf-pacf, s3-01-baselines]
tags: [ar, least-squares, recursive-forecast]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "The PACF has significant bars at lags 1 and 2 only. The ACF decays slowly. Which model do you try?", "type": "single",
 "options": ["AR(2)", "MA(2)", "AR(1)"],
 "answer": 0,
 "why": ["Correct: a PACF cut-off after lag 2 points to AR(2).", "MA(q) shows a cut-off in the ACF.", "AR(1) would cut off after lag 1."]}
```

```check
{"q": "Which condition must hold for an AR(1) model y(t) = c + φ·y(t-1) + e(t) to be stationary?", "type": "single",
 "options": ["|φ| < 1", "φ = 1", "c = 0"],
 "answer": 0,
 "why": ["Correct: shocks must fade. φ = 1 is a random walk.", "φ = 1 gives a random walk, which is not stationary.", "The constant c only sets the mean. It does not control stationarity."]}
```

## Why it matters

Many series remember their past: today is close to yesterday, and last week matters too. An **[[autoregressive model|autoregressive (AR) model]]** uses this memory. It predicts the next value as a weighted sum of the last p values. It is the "linear regression of time series". It is also the core of [[ARIMA]], and it is the model that interviewers ask you to build from scratch with numpy.

## The AR(p) model

y(t) = c + φ₁·y(t−1) + φ₂·y(t−2) + ... + φ_p·y(t−p) + ε(t)

- y(t): the value now.
- c: a constant (it sets the mean [[level]]).
- φ₁ ... φ_p (phi): the weights of the last p values. These are the parameters.
- p: the **order**, how many past values are used.
- ε(t): [[white noise]], the part we cannot predict.

Numbers: AR(1) with c = 2 and φ = 0.5. If y(t−1) = 10, the prediction is 2 + 0.5·10 = 7.

The process has a **mean** μ = c / (1 − φ₁ − ... − φ_p) when it is [[stationary]]. Here μ = 2 / 0.5 = 4.

```check
{"q": "AR(2): c = 1, φ1 = 0.5, φ2 = 0.2. y(t-1) = 10 and y(t-2) = 5. What is the prediction?", "type": "numeric",
 "answer": 7, "tol": 0.001,
 "why": "1 + 0.5 * 10 + 0.2 * 5 = 1 + 5 + 1 = 7."}
```

## Fit by least squares

This is a normal linear regression. The target is y(t). The inputs are the lagged values.

For a series y(1), ..., y(n) and order p, build a table with one row for each t = p+1, ..., n:

| target | const | y(t−1) | y(t−2) | ... |
|---|---|---|---|---|
| y(t) | 1 | y(t−1) | y(t−2) | ... |

Solve for the best weights β = (c, φ₁, ..., φ_p) that minimise the sum of squared errors. In numpy: `np.linalg.lstsq(X, target)`.

You lose p rows at the start, because they have no full set of [[lag|lags]].

Numbers: series 1, 2, 3, 4, 5 and p = 1. Rows: target 2 with lag 1, target 3 with lag 2, and so on. The perfect fit is y(t) = 1 + 1·y(t−1), so c = 1 and φ = 1.

```chart
{"title": "AR(1) with phi = 0.8: the series returns to its mean (10) after a shock", "x": "time", "height": 200,
 "series": [{"name": "AR(1) around 10", "gen": [["ar1", {"phi": 0.8, "sd": 1}], ["const", {"value": 10}]], "n": 150, "seed": 9}],
 "caption": "A larger phi means a longer memory. The series stays above or below the mean for longer."}
```

```check
{"q": "You fit AR(3) to a series of 100 points. How many rows does the regression table have?", "type": "numeric",
 "answer": 97, "tol": 0.001,
 "why": "You lose p = 3 rows at the start. 100 - 3 = 97."}
```

## Forecast by recursion

For h = 1 you use real past values. For h = 2 you need y(t+1), which you do not know. So you use the **forecast** of it as an input. This is a **recursive** (iterated) forecast:

1. Forecast one step ahead from the last p real values.
2. Add that forecast to the history.
3. Repeat from the new last p values.

Numbers: AR(1) with μ = 10, φ = 0.8 and last value 15. The forecasts are 14, 13.2, 12.56, ... Each step closes 20% of the gap to the mean.

In general, forecasts of a stationary AR model **return to the mean** μ as h grows. The speed depends on φ. The intervals widen up to the series [[variance]], not forever like a [[random walk]].

```chart
{"title": "Recursive forecast from 15 with mu = 10 and phi = 0.8", "x": "steps ahead h", "height": 200,
 "series": [
  {"name": "AR(1) forecast", "x": [0,1,2,3,4,5,6,7,8,9,10,11,12], "y": [15, 14, 13.2, 12.56, 12.05, 11.64, 11.31, 11.05, 10.84, 10.67, 10.54, 10.43, 10.34]},
  {"name": "mean", "dash": true, "x": [0,12], "y": [10, 10]}
 ],
 "caption": "The forecast decays toward the mean. Far in the future, an AR forecast is almost the mean."}
```

```check
{"q": "For a stationary AR model, what does the forecast do when the horizon becomes very large?", "type": "single",
 "options": ["It approaches the mean of the series", "It grows without limit", "It stays at the last value"],
 "answer": 0,
 "why": ["Correct: the effect of the last values fades, so the forecast tends to μ.", "That is the behaviour of a random walk with drift, not of a stationary AR model.", "That is the naive forecast. AR forecasts move toward the mean."]}
```

## Choosing p

1. Look at the **[[PACF]]**: the last [[significant]] lag suggests p.
2. Fit several p (1, 2, 3, ...) and compare **[[AIC]]**. Lower is better.
3. Check the **[[residual|residuals]]**: they should look like white noise.
4. Validate with a **backtest**, because a high p [[overfitting|overfits]].

Always fit on the training part of the data. Make the series stationary first (difference if needed).

## Worked example

We simulate an AR(2) series, recover its coefficients by [[least squares]], and forecast 5 steps.

```python
import numpy as np

def fit_ar(y, p):
    y = np.asarray(y, dtype=float)
    target = y[p:]                                              # y(t) for t = p..n-1
    cols = [np.ones(len(target))] + [y[p - k:len(y) - k] for k in range(1, p + 1)]
    X = np.column_stack(cols)                                   # [1, y(t-1), ..., y(t-p)]
    beta, *_ = np.linalg.lstsq(X, target, rcond=None)
    return beta                                                 # [c, phi1, ..., phip]

def forecast_ar(y, beta, h):
    p = len(beta) - 1
    hist = list(y)
    out = []
    for _ in range(h):
        lags = hist[-1:-p - 1:-1]                               # y(t-1), y(t-2), ..., y(t-p)
        nxt = beta[0] + np.dot(beta[1:], lags)
        out.append(nxt)
        hist.append(nxt)                                        # feed the forecast back in
    return np.array(out)

rng = np.random.default_rng(11)
n = 2000
y = np.zeros(n)
for t in range(2, n):
    y[t] = 2 + 0.5 * y[t - 1] + 0.3 * y[t - 2] + rng.normal()   # true c=2, phi=(0.5, 0.3)

beta = fit_ar(y, 2)
print("estimated [c, phi1, phi2]:", np.round(beta, 2))
print("true mean 2/(1-0.8) = 10, estimated mean:", round(beta[0] / (1 - beta[1:].sum()), 2))
print("5-step forecast:", np.round(forecast_ar(y, beta, 5), 2))
# Output:
# estimated [c, phi1, phi2]: [2.08 0.51 0.28]
# true mean 2/(1-0.8) = 10, estimated mean: 10.02
# 5-step forecast: [10.71 10.69 10.56 10.49 10.41]
```

## Common mistakes

- Fitting AR on a series with a trend. Difference it first.
- Feeding the true future values into a multi-step forecast. That is leakage. Use your own forecasts.
- Putting the lags in the wrong order when you multiply them with the coefficients.
- Using a large p on a short series. The model overfits.
- Forgetting the constant column (the intercept) in the design matrix.

## Interview lens

**Typical question:** "Implement AR(p) with numpy. How do you forecast 7 steps ahead?"

**Strong answer:** I build a design matrix with a column of ones and the p lagged columns. Then I solve the least squares problem with `np.linalg.lstsq` to get the constant and the φ coefficients. For a multi-step forecast I use the recursive method: I forecast one step, append it to the history, and repeat. The alternative is the direct method, one model per horizon. For a stationary model the forecast tends to the mean. I choose p with the PACF and AIC and check that the residuals look like white noise.

**Red flags:** Using future true values in the multi-step forecast. Fitting on a non-stationary series. Not knowing the intercept is needed. Choosing p by minimising training error only.

## Real world

- AR models are the base of the Box-Jenkins method (1970). Economists use them for series such as inflation.
- Modern "lag-feature" machine learning models use the same idea. They predict the next value from the last values, with a more flexible function.

## Key points

- AR(p): y(t) = c + φ₁·y(t−1) + ... + φ_p·y(t−p) + ε(t).
- Fit by ordinary least squares on a table of lags. You lose p rows.
- Multi-step forecast: recursive, feeding forecasts back in. It tends to the mean μ = c/(1 − Σφ).
- Choose p with PACF, AIC, residual checks and a backtest. Use stationary data.
