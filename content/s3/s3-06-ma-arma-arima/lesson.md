---
id: s3-06-ma-arma-arima
title: MA, ARMA and ARIMA
minutes: 40
level: intermediate
goals: [Explain the moving average (MA) model and why its ACF stops, Explain invertibility in simple words, Combine AR and MA into ARMA, Explain what the d in ARIMA(p,d,q) does, Turn forecasts of differences back into forecasts of levels]
prereqs: [s3-05-autoregression]
tags: [ma, arma, arima, invertibility]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "AR(1): c = 2, phi = 0.5, last value 10. What is the next forecast?", "type": "numeric",
 "answer": 7, "tol": 0.001,
 "why": "2 + 0.5 * 10 = 7."}
```

```check
{"q": "The ACF of a stationary series stops after lag 2 and the PACF decays. Which model?", "type": "single",
 "options": ["MA(2)", "AR(2)", "White noise"],
 "answer": 0,
 "why": ["Correct: an ACF cut-off after lag q points to MA(q).", "AR(2) would show the cut-off in the PACF.", "White noise has no significant bars."]}
```

## Why it matters

AR models use past **values**. There is a second way to build memory: use past **errors**. The result is the [[moving average model|moving average (MA) model]]. Put both together and add [[differencing]], and you get **[[ARIMA]]**, the most famous classical forecasting model. In interviews, you must explain what p, d and q mean in one minute.

## MA(q): memory of shocks

A **moving average model** of order q says the series is the mean plus the current [[shock]] plus the last q shocks:

y(t) = μ + ε(t) + θ₁·ε(t−1) + ... + θ_q·ε(t−q)

- μ (mu): the mean of the series.
- ε(t): the [[white noise]] shock at time t.
- θ₁ ... θ_q (theta): the weights of the past shocks.

Do not mix it up with the "moving average" smoothing from earlier lessons. Here it is a model of shocks, not an average of data.

Numbers: μ = 10, θ₁ = 0.6. Shocks: ε(t) = 2 and ε(t−1) = −1. Then y(t) = 10 + 2 + 0.6·(−1) = 11.4.

An MA(q) series has memory of only q steps. So its [[ACF]] is zero after [[lag]] q. For the forecast, you know the last q shocks (they are the model [[residual]]s). They change the forecast for up to q steps. Beyond q steps the forecast is just μ.

```check
{"q": "MA(1): mu = 50, theta = 0.5, the last shock was +4. What is the one-step forecast (the next shock has mean zero)?", "type": "numeric",
 "answer": 52, "tol": 0.001,
 "why": "50 + 0.5 * 4 = 52."}
```

## Invertibility

The shocks ε(t) are not observed. We estimate them from the data. This works only if the MA model is **[[invertible]]**. That means it can be rewritten as an AR model of infinite order, where old data matters less and less.

For MA(1): invertible if |θ| < 1. For MA(q): all roots of the polynomial 1 + θ₁z + ... + θ_q·z^q must lie **outside** the unit circle (absolute value > 1).

Numbers: θ = 0.5 gives 1 + 0.5z = 0 and z = −2, which is outside (|−2| > 1). It is invertible. θ = 2 gives z = −0.5, which is inside. It is not invertible.

Why care? The pair θ = 0.5 and θ = 2 gives **the same ACF**. We pick the invertible one so the model has a unique answer, and its shock estimates make sense. Software enforces this.

Similarly, an AR model must be **[[stationary]]**: the roots of 1 − φ₁z − ... − φ_p·z^p must also be outside the unit circle.

```check
{"q": "Is an MA(1) with theta = 1.5 invertible?", "type": "single",
 "options": ["No, because |theta| is not below 1", "Yes, because theta is positive", "Yes, because it is above 1"],
 "answer": 0,
 "why": ["Correct: the root is z = -1/1.5 = -0.67, which is inside the unit circle.", "Positive values can be non-invertible. The size of theta matters.", "A value above 1 breaks invertibility."]}
```

## ARMA(p, q)

[[ARMA]] joins both parts: past values and past shocks.

y(t) = c + φ₁·y(t−1) + ... + φ_p·y(t−p) + ε(t) + θ₁·ε(t−1) + ... + θ_q·ε(t−q)

It can describe a long memory with few parameters. For example ARMA(1,1) can replace an AR with many lags. Prefer **small orders**.

Fitting is harder than for AR: the shocks are unknown, so we cannot simply use least squares on a table. Software uses **maximum likelihood** with a numerical search.

## ARIMA(p, d, q)

ARMA needs a stationary series. **ARIMA** adds an "I" for integrated: difference d times first.

- p: number of AR lags.
- d: number of differences. d = 0 means no differencing, d = 1 removes a trend or a [[random walk]], d = 2 is rare.
- q: number of MA lags.

Steps: difference the series d times and fit ARMA(p, q) to the differences. Forecast the differences. Then **integrate** them (cumulative sum) to get back to the original scale.

Special cases you should know:

| Model | Meaning |
|---|---|
| ARIMA(0,0,0) | White noise around a mean |
| ARIMA(0,1,0) | Random walk (naive forecast) |
| ARIMA(0,1,0) with a constant | Random walk with drift |
| ARIMA(1,0,0) | AR(1) |
| ARIMA(0,1,1) | Simple exponential smoothing (with θ = α − 1) |
| ARIMA(0,2,2) | Holt's linear trend method (a related form) |

Numbers for integration: the last value is 100. The model forecasts differences 2, 1.6, 1.28. The [[level]] forecasts are 100 + 2 = 102, 102 + 1.6 = 103.6, 103.6 + 1.28 = 104.88.

```chart
{"title": "Forecast of differences (2, 1.6, 1.28, ...) integrated into a level path", "x": "steps from the last value", "height": 210,
 "series": [{"name": "level forecast", "x": [0,1,2,3,4,5], "y": [100, 102, 103.6, 104.88, 105.9, 106.72]}],
 "caption": "The differences shrink (an AR part with phi = 0.8), so the level path rises more and more slowly."}
```

```check
{"q": "Last value 50. The model forecasts the first differences 3, 2, 1. What are the level forecasts?", "type": "single",
 "options": ["53, 55, 56", "3, 2, 1", "53, 52, 51"],
 "answer": 0,
 "why": ["Correct: running total of the differences added to 50: 53, 55, 56.", "These are the differences, not the levels.", "This subtracts the differences from the previous level by mistake."]}
```

## Worked example

We write the integration step with numpy. Then we fit an ARIMA(1,1,0) with statsmodels on a simulated series. The code needs the `statsmodels` library, and the output is real.

```python
import warnings
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

def integrate(last_value, diff_forecast):
    # level forecast = last value + running total of forecast differences
    return last_value + np.cumsum(diff_forecast)

print("integrate:", integrate(100, [2, 1.6, 1.28]))

# Simulate: the differences follow AR(1) with phi = 0.6, the level is their running total
rng = np.random.default_rng(4)
e = rng.normal(size=300)
d = np.zeros(300)
for t in range(1, 300):
    d[t] = 0.6 * d[t - 1] + e[t]
y = 100 + np.cumsum(d)

model = ARIMA(y, order=(1, 1, 0)).fit()          # p=1, d=1, q=0
print("AR coefficient:", round(model.params[0], 3), "(true 0.6)")
print("AIC:", round(model.aic, 1))
print("last value:", round(y[-1], 2))
print("forecast 5 steps:", np.round(model.forecast(5), 2))
# Output:
# integrate: [102.   103.6  104.88]
# AR coefficient: 0.585 (true 0.6)
# AIC: 860.7
# last value: 177.19
# forecast 5 steps: [177.55 177.77 177.89 177.96 178.01]
```

The forecasts rise slowly and flatten: the AR part makes the forecast differences fade away, so the level path flattens.

## Common mistakes

- Choosing d too large. Over-differencing adds noise. Check with the ACF and unit-root tests.
- Choosing large p and q. A complex model fits noise. Start small, such as (1,1,1).
- Forgetting that forecasts are for the **differenced** series if you model it by hand. Integrate them.
- Ignoring invertibility and stationarity warnings from the software.
- Putting the constant into a d = 2 model without thinking about it. It means a quadratic trend.

## Interview lens

**Typical question:** "Explain ARIMA(p, d, q). How do you choose the orders?"

**Strong answer:** p is the number of past values used (AR part). d is the number of differences that make the series stationary. q is the number of past shocks used (MA part). I choose d with plots and unit-root tests, usually 0 or 1. Then I look at the [[PACF]] for p and the ACF for q, and I compare a few small models by AIC. The residuals must look like white noise. To forecast, the model predicts the differenced series and then integrates it back. ARIMA(0,1,0) is the random walk, and ARIMA(0,1,1) is simple [[exponential smoothing]].

**Red flags:** Confusing the MA model with a moving average smoother. Not knowing that d is about differencing. Using high orders without checking residuals. Not knowing the random walk is ARIMA(0,1,0).

## Real world

- George Box and Gwilym Jenkins published "Time Series Analysis: Forecasting and Control" in 1970. It made ARIMA the standard tool in business and economics for decades.
- Auto-ARIMA tools (for example `auto.arima` in R by Rob Hyndman, and `pmdarima` in Python) search the orders for you using AIC.

## Key points

- MA(q): the series depends on the last q shocks. Its ACF cuts off after lag q.
- Invertible MA and stationary AR: roots of the polynomial are outside the unit circle.
- ARMA(p,q) joins both. ARIMA(p,d,q) differences d times first, then fits ARMA.
- To forecast, predict the differences and integrate them with a cumulative sum.
- ARIMA(0,1,0) is the random walk. ARIMA(0,1,1) is simple exponential smoothing.
