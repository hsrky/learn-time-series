---
id: s11-05-uber-forecasting-orbit
title: Uber: forecasting platform and Orbit
minutes: 25
level: advanced
goals: [Describe the forecasting needs of a marketplace like Uber, Explain what a Bayesian time series model adds to exponential smoothing, Build a local-level Kalman filter with prediction intervals]
prereqs: [s11-04-timesfm-foundation-models]
tags: [uber, orbit, bayesian, exponential-smoothing, kalman, uncertainty]
skills: [case-studies, probabilistic-forecasting]
---

## Warm-up

```check
{"q": "Patches in TimesFM mainly help to...", "type": "single",
 "options": ["Reduce the number of tokens and the attention cost", "Remove seasonality", "Add covariates"],
 "answer": 0,
 "why": ["Correct.", "Patches do not remove seasonality.", "Covariates are a different feature."]}
```

```check
{"q": "In simple exponential smoothing, a larger alpha means...", "type": "single",
 "options": ["The forecast reacts faster to new data", "The forecast is smoother", "The trend is stronger"],
 "answer": 0,
 "why": ["Correct: more weight on the newest value.", "A smaller alpha gives a smoother line.", "SES has no trend."]}
```

## Why it matters

Uber is a **marketplace**: riders on one side, drivers on the other. It must predict how many trips will be requested, where, and when, and how many drivers will be online. Wrong forecasts mean long waits (too few drivers) or idle drivers (too many). Uber has many forecasting problems, from city demand next hour to company finance next year. Their public work shows a typical path: strong classical models, a platform, then neural and Bayesian methods where they help.

## What Uber has said publicly

- **Forecasting platform.** Uber engineering posts describe tools for many teams: a common way to run backtests, compare models and deploy forecasts, so each team does not rebuild the same pipeline.
- **Extreme events.** A 2017 Uber engineering post described using LSTM networks to forecast demand on extreme days such as holidays, where little history exists.
- **M4 winner.** Slawek Smyl, then at Uber, won M4 with ES-RNN, a hybrid of exponential smoothing and an RNN. This shows the value of keeping a statistical core.
- **Orbit.** In 2020 Uber released the open-source Python library **[[Orbit]]**. Authors include Edwin Ng, Zhishi Wang, Huigang Chen, Steve Yang and Slawek Smyl.

## Orbit: Bayesian exponential smoothing

Orbit provides **[[Bayesian structural time series]]** models. They look like exponential smoothing (a level, a trend, a season), but they are fitted in a **Bayesian** way.

Exponential smoothing gives one fitted value for each parameter, for example alpha = 0.3. The Bayesian way gives a **distribution** for each parameter ("alpha is probably between 0.2 and 0.4"). Forecasts then carry the uncertainty about the parameters too.

Main models in Orbit:

| Model | Idea |
|---|---|
| **DLT** (Damped Local Trend) | Level and a damped trend, with seasonality and regressors |
| **LGT** (Local Global Trend) | A local trend mixed with a global trend, robust to sudden changes |
| **KTR** (Kernel-based Time-varying Regression) | Regression coefficients that change smoothly over time |

Other features: priors (you can add knowledge: "this coefficient is positive"), regression with external variables, full **prediction intervals**, built-in backtesting, and a scikit-learn-like API. Fitting uses Stan (or Pyro in some versions).

```widget
{"name": "ses-alpha", "params": {"alpha": 0.3}}
```

```check
{"q": "What does a Bayesian model give for a parameter such as alpha?", "type": "single",
 "options": ["One fixed number only", "A distribution that shows how sure we are", "A random number", "No number"],
 "answer": 1,
 "why": ["That is the classical point estimate.", "Correct.", "It is not random; it comes from the data and the prior.", "It gives a full description."]}
```

## Why uncertainty matters here

If supply planners get only "100 trips", they cannot decide how many drivers to incentivise. With "80% chance between 85 and 118" they can plan for the risk. A model with proper intervals also lets you alert when reality leaves the interval: a ready-made anomaly detector.

```check
{"q": "An 80% prediction interval should contain the actual value about...", "type": "single",
 "options": ["80% of the time", "50% of the time", "95% of the time", "100% of the time"],
 "answer": 0,
 "why": ["Correct: this is calibration (coverage).", "That is a 50% interval.", "That is a 95% interval.", "Then the interval would be infinitely wide."]}
```

## The simplest Bayesian-style model: the local level

The **local level model** is the state-space form of simple exponential smoothing:

- Hidden level: `μ(t) = μ(t−1) + η(t)`, with noise variance `q`.
- Observation: `y(t) = μ(t) + ε(t)`, with noise variance `r`.

The **Kalman filter** updates our belief about the level at each step. With belief mean `m` and variance `P`:

1. Predict: `P_pred = P + q`.
2. Gain: `K = P_pred / (P_pred + r)`.
3. Update: `m = m + K · (y − m)` and `P = (1 − K) · P_pred`.

`K` plays the role of alpha in SES: it is high when the level moves a lot (`q` big) or the observation is precise (`r` small). A forecast `h` steps ahead has mean `m` and variance `P + h·q + r`, so the interval **widens with the horizon**.

```check
{"q": "In the Kalman update, if the observation noise r is very large, the gain K is...", "type": "single",
 "options": ["Close to 1", "Close to 0", "Exactly 0.5", "Negative"],
 "answer": 1,
 "why": ["That happens when r is small.", "Correct: noisy observations get little weight, so the level moves slowly.", "Only if P_pred equals r.", "K is between 0 and 1."]}
```

## Worked example

We filter a simulated series, forecast 5 steps ahead with 80% intervals, and check the coverage on 400 simulated series.

```python
import numpy as np

def kalman_level(y, q, r, m0=None, p0=1e6):
    """Filter a local level model. Return the final belief mean and variance."""
    m, P = (y[0] if m0 is None else m0), p0
    for obs in y:
        P_pred = P + q
        K = P_pred / (P_pred + r)
        m = m + K * (obs - m)
        P = (1 - K) * P_pred
    return m, P

rng = np.random.default_rng(0)
q, r, n, h, z80 = 1.0, 4.0, 60, 5, 1.2816
hits, abs_err = 0, []
for _ in range(400):
    level = 100 + np.cumsum(rng.normal(0, np.sqrt(q), n + h))   # hidden random-walk level
    y = level + rng.normal(0, np.sqrt(r), n + h)                # noisy observations
    m, P = kalman_level(y[:n], q, r)
    sd = np.sqrt(P + h * q + r)                                  # forecast sd at horizon h
    actual = y[n + h - 1]
    hits += abs(actual - m) <= z80 * sd                          # inside the 80% interval?
    abs_err.append(abs(actual - m))

print("coverage of the 80% interval at h=5:", round(hits / 400, 2))
print("mean absolute error at h=5:", round(float(np.mean(abs_err)), 2))
# Output:
# coverage of the 80% interval at h=5: 0.79
# mean absolute error at h=5: 2.63
```

Coverage close to 0.80 means the intervals are well calibrated. This is the checking habit you need for any probabilistic model, including Orbit.

## Common mistakes

- Reporting a Bayesian forecast without checking coverage.
- Using a flexible model (KTR) with too little data and weak priors.
- Treating prior settings as magic. They are assumptions: state them and test them.
- Forgetting that fitting with MCMC is slower than classical ETS, which matters at scale.
- Comparing only point accuracy and ignoring the interval quality.

## Interview lens

**Typical question:** "What does a Bayesian forecasting model give you that ETS does not?"

**Strong answer:** A Bayesian structural model has the same ingredients as exponential smoothing, level, trend and season, but it gives a distribution for the parameters and the forecast, so intervals include parameter uncertainty. It allows priors, such as knowing a regressor effect is positive, and it handles regressors with time-varying coefficients. The costs are slower fitting and more assumptions. I check calibration, meaning the share of actuals inside the 80% interval, and compare with classical ETS on a rolling backtest. Orbit from Uber is an example with DLT, LGT and KTR models.

**Red flags:** Saying Bayesian means more accurate. Not mentioning priors or calibration.

## Real world

Orbit is open source (the project is on GitHub, with a paper on arXiv titled "Orbit: Probabilistic Forecast with Exponential Smoothing"). Uber engineering has described its forecasting platform, its use of LSTM models for extreme events, and Slawek Smyl's M4-winning ES-RNN. These are public, so you can read the originals before an interview at a marketplace company.

## Key points

- A marketplace needs forecasts of demand and supply, with uncertainty.
- Orbit: Bayesian exponential-smoothing style models (DLT, LGT, KTR) with priors, regressors and intervals.
- The local level Kalman filter is the simplest example: gain K acts like alpha, interval widens with horizon.
- Check calibration: an 80% interval should contain about 80% of actuals.
- Bayesian models cost more compute and need explicit assumptions.
