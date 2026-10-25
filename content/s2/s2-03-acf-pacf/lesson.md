---
id: s2-03-acf-pacf
title: Autocorrelation: ACF and PACF
minutes: 35
level: beginner
goals: [Compute the autocorrelation at a lag by hand, Implement ACF from scratch, Read ACF and PACF plots and the confidence band, Guess AR and MA orders from the plots]
prereqs: [s2-02-stationarity-transforms]
tags: [acf, pacf, autocorrelation, order-selection]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "Daily data with a weekly season. Which seasonal difference lag do you use?", "type": "single",
 "options": ["1", "7", "30"],
 "answer": 1,
 "why": ["Lag 1 removes a trend but not the weekly pattern.", "Correct: compare each day with the same weekday one week before.", "Lag 30 is about a month. It does not match a weekly pattern."]}
```

```check
{"q": "Which property is needed for a stationary series?", "type": "single",
 "options": ["The mean changes slowly", "The mean and variance are constant", "The values are always positive"],
 "answer": 1,
 "why": ["A changing mean means it is not stationary.", "Correct: constant mean and variance, and autocorrelation that depends only on the lag.", "Stationary series can have negative values."]}
```

## Why it matters

A doctor looks at an X-ray before choosing a treatment. A forecaster looks at the [[ACF]] and [[PACF]] plots before choosing a model. They show how a value today is linked to values in the past. They tell you if there is a season, if the series is a random walk, and which ARIMA orders to try. Interviewers love the question "how do you choose p and q?".

## Autocorrelation at one lag

**Autocorrelation** is the correlation of a series with a shifted copy of itself. The shift is the **lag** k. Lag 1 compares each value with the one before it.

Small example: x = 1, 3, 2, 4, 3.

- Mean = 2.6. Deviations from the mean: −1.6, 0.4, −0.6, 1.4, 0.4.
- Sum of squared deviations = 5.2.
- Lag-1 products: 0.4·(−1.6) + (−0.6)·0.4 + 1.4·(−0.6) + 0.4·1.4 = −1.16.
- r(1) = −1.16 / 5.2 = −0.22.

The sign is negative: a high value is often followed by a low value.

```check
{"q": "A series with strong positive lag-1 autocorrelation (r1 = 0.9). After a high value, what comes next?", "type": "single",
 "options": ["Probably another high value", "Probably a low value", "Nothing can be said"],
 "answer": 0,
 "why": ["Correct: positive autocorrelation means neighbours move in the same direction.", "This would be negative autocorrelation.", "A value of 0.9 gives a lot of information about the next value."]}
```

## The ACF formula

The **ACF** (autocorrelation function) is r(k) for k = 0, 1, 2, ...

r(k) = Σ (x(t) − m)·(x(t−k) − m)  /  Σ (x(t) − m)²

- x(t): the value at time t.
- m: the mean of the whole series.
- k: the lag.
- The top sum runs over t = k, ..., n−1. The bottom sum runs over all t.
- r(0) is always 1.

The plot shows r(k) as bars. The shaded **band** is ±1.96/√n. For white noise about 95% of the bars stay inside it. A bar outside the band is called **significant**.

```widget
{"name": "acf", "params": {"process": "ar1", "phi": 0.7}}
```

```check
{"q": "A series has n = 100 points. How wide is the 95% band of the ACF (the number after the ±)?", "type": "numeric",
 "answer": 0.196, "tol": 0.001,
 "why": "1.96 / sqrt(100) = 1.96 / 10 = 0.196."}
```

## Reading ACF shapes

| What you see in the ACF | What it means |
|---|---|
| All bars inside the band | White noise. Nothing to model. |
| Very slow decay, many bars above the band | Trend or random walk. Difference the series. |
| Spikes at lag m, 2m, 3m | Season of length m. Use a seasonal difference. |
| Bars decay smoothly (geometrically) | AR process (depends on past values). |
| Bars stop after lag q, then zero | MA(q) process (depends on past shocks). |

```chart
{"title": "Theoretical ACF of an AR(1) with phi = 0.7: smooth decay", "x": "lag", "height": 200,
 "series": [{"name": "ACF", "kind": "bar", "x": [0,1,2,3,4,5,6,7,8], "y": [1, 0.7, 0.49, 0.343, 0.24, 0.168, 0.118, 0.082, 0.058]}],
 "caption": "For AR(1) the ACF at lag k is phi to the power k."}
```

```chart
{"title": "Theoretical ACF of an MA(1) with theta = 0.6: cuts off after lag 1", "x": "lag", "height": 200,
 "series": [{"name": "ACF", "kind": "bar", "x": [0,1,2,3,4,5,6,7,8], "y": [1, 0.441, 0, 0, 0, 0, 0, 0, 0]}],
 "caption": "An MA(1) process has memory of only one shock, so the ACF is zero after lag 1."}
```

```check
{"q": "Monthly sales. The ACF has big spikes at lags 12, 24, 36. What does it mean?", "type": "single",
 "options": ["A yearly season", "White noise", "A moving average of order 12 only"],
 "answer": 0,
 "why": ["Correct: spikes at multiples of 12 show a yearly pattern in monthly data.", "White noise has no spikes outside the band.", "A pure MA(12) has no repeated spikes at 24 and 36."]}
```

## PACF: the direct link

Problem: in an AR(1) series, x(t) is linked to x(t−2) only **through** x(t−1). The ACF shows this indirect link, and it hides which lags matter.

The **partial autocorrelation** at lag k is the link between x(t) and x(t−k). We first remove the effect of the lags in between. It is the last coefficient in a regression of x(t) on x(t−1), ..., x(t−k).

Numbers: for AR(1) with φ = 0.7, the ACF is 0.7, 0.49, 0.34, ... but the PACF is 0.7, 0, 0, ... All the indirect links vanish.

## Guess the order: the cheat table

| Process | ACF | PACF |
|---|---|---|
| AR(p) | decays slowly | **cuts off after lag p** |
| MA(q) | **cuts off after lag q** | decays slowly |
| ARMA(p, q) | decays | decays |

How to use it:

1. Make the series stationary (previous lesson).
2. Plot ACF and PACF.
3. If the PACF stops after lag p, try AR(p). If the ACF stops after lag q, try MA(q).
4. If both decay, try small ARMA models and compare them with AIC (see the SARIMA lesson).

This is a **guide**, not a proof. Real plots are noisy, so test two or three nearby models.

```check
{"q": "The PACF has significant bars at lags 1 and 2 and nothing after. The ACF decays slowly. Which model?", "type": "single",
 "options": ["AR(2)", "MA(2)", "ARMA(1,1)"],
 "answer": 0,
 "why": ["Correct: PACF cuts off after lag 2 and ACF decays. That is the AR(2) signature.", "For MA(2) it is the ACF that cuts off after lag 2.", "ARMA(1,1) has both ACF and PACF decaying."]}
```

## Worked example

We write ACF from scratch and test it on an AR(1) series with φ = 0.7. Then we compute the PACF with the Durbin-Levinson method.

```python
import numpy as np

def acf(x, nlags):
    x = np.asarray(x, dtype=float)
    d = x - x.mean()
    denom = np.sum(d * d)
    return np.array([np.sum(d[k:] * d[:len(d) - k]) / denom for k in range(nlags + 1)])

def pacf(x, nlags):
    r = acf(x, nlags)
    out = [1.0, r[1]]
    phi = np.array([r[1]])                      # AR coefficients for the current order
    for k in range(2, nlags + 1):
        num = r[k] - np.dot(phi, r[1:k][::-1])
        den = 1.0 - np.dot(phi, r[1:k])
        phi_kk = num / den                      # new partial autocorrelation
        phi = np.append(phi - phi_kk * phi[::-1], phi_kk)
        out.append(phi_kk)
    return np.array(out)

# Simulate AR(1): x(t) = 0.7 * x(t-1) + noise
rng = np.random.default_rng(1)
n = 1000
x = np.zeros(n)
for t in range(1, n):
    x[t] = 0.7 * x[t - 1] + rng.normal()

print("small example r1:", round(acf([1, 3, 2, 4, 3], 1)[1], 3))
print("ACF  1-5:", np.round(acf(x, 5)[1:], 2))
print("PACF 1-5:", np.round(pacf(x, 5)[1:], 2))
print("95% band:", round(1.96 / np.sqrt(n), 3))
# Output:
# small example r1: -0.223
# ACF  1-5: [0.69 0.47 0.34 0.23 0.17]
# PACF 1-5: [ 0.69  0.01  0.03 -0.02  0.02]
# 95% band: 0.062
```

The ACF decays like 0.7, 0.49, 0.34 and so on. The PACF has one large bar at lag 1, then values inside the band. That is the AR(1) signature.

## Common mistakes

- Reading the ACF of a non-stationary series. A trend makes all bars big and hides the structure. Difference first.
- Treating one bar outside the band as important. With 40 lags, about 2 bars are outside the band by chance.
- Using the ACF of the raw series when a season is present. Remove the season first, or read the spikes at the season lag.
- Confusing the rules: AR is seen in the PACF cut-off, MA in the ACF cut-off.
- Calling the bar at lag 0 an effect. It is always 1.

## Interview lens

**Typical question:** "How do you choose p and q for an ARIMA model?"

**Strong answer:** First I make the series stationary with differencing or a transform. Then I plot ACF and PACF. If the PACF cuts off after lag p and the ACF decays, I try AR(p). If the ACF cuts off after lag q and the PACF decays, I try MA(q). Real plots are noisy, so I fit a few neighbouring models and pick by AIC and by residual checks. I also validate by a backtest, because a good in-sample fit does not guarantee a good forecast.

**Red flags:** Reading the ACF of a trending series. Mixing up which plot shows AR and which shows MA. Saying "I trust the plot completely" with no model comparison. Not knowing the ±1.96/√n band.

## Real world

- Box and Jenkins described this identify-estimate-check workflow in their 1970 book. Many courses still teach it as the classical way to build ARIMA models.
- Modern auto-ARIMA tools do not read plots. They search over orders and compare AIC, but the ACF and PACF are still the first diagnostic that engineers draw.

## Key points

- ACF r(k) is the correlation of a series with itself k steps earlier. The band is ±1.96/√n.
- Slow ACF decay means trend or random walk. Spikes at m, 2m, 3m mean a season of length m.
- PACF is the direct link at lag k after removing shorter lags.
- AR(p): PACF cuts off after p. MA(q): ACF cuts off after q.
- Plots guide the search. Confirm with AIC, residual checks and a backtest.
