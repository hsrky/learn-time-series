---
id: s10-04-forecast-error-alerts
title: Forecast-error alerts and the tracking signal
minutes: 25
level: advanced
goals: [Track forecast error and bias in production, Compute the tracking signal and use it as an alarm, Design alerts that are useful and not noisy]
prereqs: [s10-03-drift-monitoring]
tags: [monitoring, tracking-signal, bias, MAD, alerts]
skills: [monitoring, forecast-metrics]
---

## Warm-up

```check
{"q": "Which drift can you only see after the true values arrive?", "type": "single",
 "options": ["Data drift", "Concept drift", "Missing-data drift"],
 "answer": 1,
 "why": ["Data drift is seen from the inputs alone.", "Correct: you need the error to see that the rule changed.", "Missing data is an input check."]}
```

```check
{"q": "PSI is 0.31 for a key feature. By the common rule of thumb this is...", "type": "single",
 "options": ["Stable", "A small shift", "A large shift"],
 "answer": 2,
 "why": ["Stable is below 0.1.", "A small shift is 0.1 to 0.25.", "Correct: above 0.25 is a large shift."]}
```

## Why it matters

A forecast can fail in two ways. It can be **noisy**: sometimes too high, sometimes too low. Or it can be **biased**: it is too low every day. A small bias is hard to see in a daily chart, but it adds up. Ten units too low per day is 300 units at the end of the month: an empty shelf. The **tracking signal** is a classic tool from supply-chain planning that finds this kind of slow failure.

## Error and bias

Let `e(t) = actual(t) − forecast(t)`. Positive means we forecast too low.

- **Bias** = the average of `e(t)`. It tells the direction. Near zero is good.
- **MAD** ([[mean absolute deviation]], the same number as MAE) = the average of `|e(t)|`. It tells the size. Careful: in anomaly detection, MAD often means the *median* absolute deviation (see [[lesson:s8-01-point-anomalies]]).
- **[[WAPE]]** = `Σ|e| / Σ actual`. A percent that is safe when some actuals are near zero, because it divides by the total.

Example: actuals `[100, 110, 90]`, forecasts `[95, 100, 80]`. Errors `[5, 10, 10]`. Bias = 8.33 (too low). MAD = 8.33. WAPE = 25 / 300 = 8.3%.

```check
{"q": "Actuals [50, 60], forecasts [60, 50]. What is the bias (mean of actual − forecast)?", "type": "numeric",
 "answer": 0, "tol": 0.001,
 "why": "Errors are −10 and +10. The mean is 0. The errors cancel, but MAD is 10. This is why you need both numbers."}
```

## The tracking signal

The **[[tracking signal]]** (TS) divides the *running sum of errors* by the *running MAD*.

**TS(t) = RSFE(t) / MAD(t)**

- `RSFE(t)` = running sum of forecast errors, `Σ e(i)` for i = 1…t. Signs are kept, so bias adds up.
- `MAD(t)` = average of `|e(i)|` for i = 1…t.
- TS is a count of "how many typical errors the total error is worth".

If the forecast is unbiased, positive and negative errors cancel and TS stays near 0. If the forecast is too low every day, RSFE grows steadily and TS climbs. A common alarm rule is **|TS| > 4** (some teams use 3 to 6). Also require a minimum number of periods (for example 6), because TS is wild in the first few points.

```chart
{"title": "Tracking signal: a bias starts at day 30", "x": "day", "height": 230, "series": [{"name": "tracking signal", "y": [1.0, -0.94, -1.99, -3.58, -1.29, -0.23, -0.58, 0.21, 0.55, -0.08, 1.06, 0.74, 0.35, -0.67, -0.09, -0.23, 0.54, -0.33, -0.15, -1.46, -0.22, 0.05, 0.56, 1.21, -0.36, 0.83, 3.66, 1.3, -0.98, -2.83, 0.66, 2.98, 5.94, 8.3, 10.12, 11.9, 13.33, 15.27, 16.12, 17.33, 18.84, 20.94, 21.93, 22.81, 23.88, 25.5, 26.66, 28.3, 28.93, 30.47, 31.94, 32.72, 33.93, 35.39, 36.55, 37.9, 39.52, 40.67, 41.71, 42.65]}, {"name": "alarm limit +4", "y": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4], "dash": true}], "marks": [{"x": 30, "label": "bias starts"}], "caption": "Before day 30 the signal wanders near 0. After the bias starts it climbs fast and crosses +4 two days later."}
```

```check
{"q": "A forecast is 5 units too low every day for 20 days, with no other error. What is TS at day 20?", "type": "numeric",
 "answer": 20, "tol": 0.001,
 "why": "RSFE = 20 × 5 = 100. MAD = 5. TS = 100 / 5 = 20, far above the limit 4."}
```

## Designing alerts

Good alerts are few, clear and tied to action.

- **Compare with a baseline.** Alert on "MAE is 1.5 times the seasonal naive MAE", not only "MAE > 10". Then holidays that hurt every model do not trigger a false alarm.
- **Use windows.** A rolling 7-day or 28-day window avoids reacting to one bad day.
- **Use both size and direction.** WAPE for size, TS or bias for direction.
- **Segment.** An overall WAPE of 12% can hide one region at 40%.
- **Respect label delay.** If actuals come 3 days late, the alert is 3 days late. Say it on the dashboard.
- **Say what to do.** Each alert links to a runbook: check data, check the last deployment, retrain, or roll back.

```check
{"q": "Why compare live MAE with a seasonal naive baseline instead of a fixed number?", "type": "single",
 "options": ["Naive is always the best model", "Hard days (holidays, storms) raise the error of every model, and the ratio removes that effect", "A fixed number is not allowed", "Naive is cheaper to compute"],
 "answer": 1,
 "why": ["No. It is only a reference.", "Correct: the ratio tells you if YOUR model got worse, not if the world got harder.", "A fixed number is allowed but gives more false alarms.", "Cost is not the reason."]}
```

## Worked example

We make a forecast that is unbiased for 30 days and then runs 8 units too low. We compute the tracking signal and the first alarm day.

```python
import numpy as np

rng = np.random.default_rng(2)
n = 60
truth = 100 + 10 * np.sin(np.arange(n) * 2 * np.pi / 7)   # weekly pattern
actual = truth + rng.normal(0, 4, n)
forecast = truth.copy()
forecast[30:] -= 8                                         # bias starts on day 30

err = actual - forecast                                    # positive = forecast too low
rsfe = np.cumsum(err)                                      # running sum of errors
mad = np.cumsum(np.abs(err)) / np.arange(1, n + 1)         # running mean absolute error
ts = rsfe / mad

limit, min_periods = 4.0, 6
alarm = np.where((np.abs(ts) > limit) & (np.arange(1, n + 1) >= min_periods))[0]
print("TS at day 29:", round(ts[29], 2))
print("TS at day 59:", round(ts[59], 2))
print("first alarm at index:", int(alarm[0]) if len(alarm) else None)
# Output:
# TS at day 29: -2.83
# TS at day 59: 42.65
# first alarm at index: 32
```

Before the bias, TS stays small. After day 30, TS grows until it passes the limit. The alarm fires 2 days after the problem begins. Note: with other random seeds, noise alone can push TS past 4 early in the series. A limit is a trade-off, so tune it on your own history.

## Common mistakes

- Looking only at MAE. A biased forecast and an unbiased forecast can have the same MAE.
- Using the tracking signal without a minimum number of periods. The first points give huge values.
- Never resetting. After a retrain, start the running sums again, or use a rolling window.
- Alerting on percent error (MAPE) for items with near-zero sales.
- Ignoring the label delay and the forecast horizon: the error of a 14-day forecast is not the same as of a 1-day forecast.

## Interview lens

**Typical question:** "How would you set up alerts for a demand forecast used by planners?"

**Strong answer:** I track WAPE and bias per segment against a seasonal naive baseline, on a rolling window, using the forecasts I saved at the time. For slow bias I use the tracking signal, the running sum of errors divided by the running MAD, with an alarm near 4 and a minimum number of periods. Each alert has an owner and a runbook. I tune thresholds on history so that alerts are rare, and I show the label delay so people know how fresh the signal is.

**Red flags:** One global metric only. No baseline. Alerts without an owner. Using MAPE on intermittent demand.

## Real world

The tracking signal is a standard idea in textbooks on forecasting and inventory control, used by supply-chain planners for many decades. The same idea of "cumulative sum" is the basis of CUSUM control charts in quality control. Modern monitoring tools apply the same logic to model errors.

## Key points

- Track size (MAD, WAPE) and direction (bias) of the error. Both are needed.
- Tracking signal = running sum of errors / running MAD. Alarm when |TS| is above about 4 after a minimum number of periods.
- Compare with a seasonal naive baseline and use rolling windows to avoid false alarms.
- Segment the metrics, and show the label delay.
- Every alert needs an owner and a runbook.
