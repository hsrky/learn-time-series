---
id: s10-08-design-anomaly-platform
title: Design case: a metric anomaly detection platform
minutes: 40
level: staff
goals: [Build a seasonal baseline with a robust z-score, Explain how to keep false alerts low at scale, Size an anomaly platform with simple numbers]
prereqs: [s10-07-design-demand-forecasting]
tags: [system-design, anomaly-detection, monitoring, drill]
skills: [ml-system-design, anomaly-detection]
---

## Warm-up

```check
{"q": "Why are sales not the same as demand?", "type": "single",
 "options": ["Sales include returns", "Sales stop when stock runs out, so demand is hidden", "Demand is always lower", "Sales are in a different unit"],
 "answer": 1,
 "why": ["Returns exist but are not the main point.", "Correct: this is censored demand.", "Demand can be higher than sales.", "Units are not the issue."]}
```

```check
{"q": "A forecast is in shadow mode. What does that mean?", "type": "single",
 "options": ["It runs at night", "It predicts but nobody uses the output yet", "It uses old data", "It is hidden from the model owner"],
 "answer": 1,
 "why": ["Time of day is not the meaning.", "Correct: you compare it with the live model safely.", "Data age is unrelated.", "Owners see it; the business does not act on it."]}
```

## Why it matters

A company has hundreds of thousands of metrics: orders per minute, payment errors, page load time per country. Nobody can watch them all. An **anomaly detection platform** watches them and sends an alert when something is wrong. The hard part is not detection. The hard part is **alert quality**: if the platform sends many false alerts, people mute it. Then it misses the real outage.

## Types of anomalies

- **Point anomaly**: one value is far from normal (a spike at 14:03).
- **Level shift**: the metric moves to a new level and stays (a deploy broke checkout).
- **Trend or variance change**: slow growth or more noise.
- **Contextual anomaly**: the value is normal in general but wrong for this time (500 orders at 4 a.m. on Sunday).
- **Missing data**: the metric stops arriving. This is often the most important alert.

Most business metrics have **seasonality** (daily and weekly cycles). A detector that ignores it will alert every morning.

```widget
{"name": "anomaly-zscore", "params": {}}
```

```check
{"q": "Orders on a Sunday at 4 a.m. are 500, normal for Monday at noon but 20 times the usual for that time. Which anomaly type?", "type": "single",
 "options": ["Point anomaly in a global sense only", "Contextual anomaly", "Missing data", "Level shift"],
 "answer": 1,
 "why": ["Against the global range 500 may look normal.", "Correct: the value is only strange for this time context.", "Data is present.", "A level shift needs a lasting change."]}
```

## A simple, strong baseline: seasonal robust z-score

Method:

1. For each point, find the **expected value** for its time slot, for example the median of the same hour of the week over the last 4 weeks.
2. Compute the **residual** = actual − expected.
3. Compute the typical size of residuals with the **MAD** (median absolute deviation) of recent residuals.
4. The **[[robust z-score]]**: `z = 0.6745 × residual / MAD`. Alert if `|z| > 4`, for example.

Why median and MAD? The mean and standard deviation are pulled by the outliers you want to find. The median and MAD are not. The number 0.6745 makes the score comparable to a normal z-score (MAD ≈ 0.6745 × standard deviation for normal data).

```chart
{"title": "Weekly cycle with one spike and one dip", "x": "hour", "height": 230,
 "series": [
   {"name": "metric", "gen": [["season", {"period": 24, "amp": 30}], ["const", {"value": 100}], ["noise", {"sd": 4}], ["spike", {"at": 130, "size": 70}], ["spike", {"at": 52, "size": -60}]], "n": 168, "seed": 12},
   {"name": "expected (daily pattern)", "gen": [["season", {"period": 24, "amp": 30}], ["const", {"value": 100}]], "n": 168, "dash": true}
 ],
 "caption": "The model uses the daily pattern as the expected value. The two big gaps from the dashed line are the anomalies."}
```

```check
{"q": "Residuals (actual − expected) are 2, −1, 3, 0, −2, 40. The MAD of the first five numbers is 2 (median absolute deviation). What is the robust z-score of 40? (use 0.6745)", "type": "numeric",
 "answer": 13.49, "tol": 0.05,
 "why": "z = 0.6745 × 40 / 2 = 13.49. A huge score, so it is an anomaly."}
```

## Making it work at scale

A platform has more parts than a detector.

| Part | What it does |
|---|---|
| Ingestion | Receives metric points (stream) and stores them in a time-series database |
| Detection | Runs a detector per metric, on a schedule or per point |
| Model management | Picks a method by metric type (seasonal, sparse, counter), retrains baselines |
| Alert logic | Suppresses, groups and routes alerts |
| Feedback | Users mark alerts as true or false; labels improve thresholds |
| UI and API | Charts, expected band, history, mute button |

Key techniques against **[[alert fatigue]]**:

- **Require persistence**: alert only if the anomaly lasts 3 of 5 points.
- **Dedupe and group**: one outage can break 200 metrics; send one alert for the group.
- **Severity and routing** by business impact (revenue metric vs debug metric).
- **Dynamic thresholds** per metric from its own history, with a target alert rate.
- **Cooldown**: no repeat for the same metric for 30 minutes.
- **Feedback**: a "not useful" click lowers sensitivity for that metric.

```check
{"q": "A bad deploy breaks 300 related metrics at once. What should the platform do?", "type": "single",
 "options": ["Send 300 alerts", "Group related alerts and send one with the list of affected metrics", "Ignore it", "Retrain all baselines"],
 "answer": 1,
 "why": ["That causes alert fatigue and hides the root cause.", "Correct: grouping speeds up the diagnosis.", "It is a real incident.", "Retraining would learn the broken level as normal."]}
```

## Worked example

We build a seasonal robust-z detector on a synthetic hourly metric with a daily cycle and three injected anomalies.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(10)
idx = pd.date_range("2024-01-01", periods=24 * 28, freq="h")
base = 100 + 30 * np.sin(2 * np.pi * idx.hour / 24)
y = pd.Series(base + rng.normal(0, 4, len(idx)), index=idx)
y.iloc[500] += 60      # spike
y.iloc[600] -= 50      # dip
y.iloc[650] += 45      # spike

# expected = median of the same hour of day in the whole history (simple, robust)
expected = y.groupby(y.index.hour).transform("median")
resid = y - expected
mad = (resid - resid.median()).abs().median()
z = 0.6745 * resid / mad

alerts = z[z.abs() > 4]
print("MAD:", round(mad, 2))
print("alerts at positions:", [int(idx.get_loc(t)) for t in alerts.index])
# Output:
# MAD: 2.51
# alerts at positions: [500, 600, 650]
```

All three injected anomalies are found and nothing else. Real data is harder: levels shift, so a rolling window and a trend term are needed.

## Common mistakes

- Using mean and standard deviation on data that contains outliers.
- Ignoring seasonality, so every Monday morning is an alert.
- One global threshold for all metrics.
- No handling of missing data points.
- No feedback path, so the platform never improves.
- Reporting "accuracy". Anomalies are rare, so measure precision, recall and alerts per day.

## Interview lens

**Typical question:** "Design a system that detects anomalies in 500 000 business metrics."

**Strong answer:** I ask who receives alerts and which anomalies matter, then define a target: a small number of alerts per on-call person per day with high precision. The core is a seasonal baseline per metric (STL or same-time-slot median) with a robust z-score on the residual, plus a different method for sparse metrics. At scale I stream metrics into a time-series store, run detectors in partitions by metric id, and apply persistence, grouping, severity and cooldown before alerting. I collect user feedback as labels to tune thresholds and later train a model. I monitor the platform itself: detection delay, alert rate, precision, and missing-data alerts.

**Red flags:** Saying "use deep learning" first. No view on false alerts. Ignoring seasonality or missing data. No labels or feedback plan.

## Real world

Several large companies have described anomaly systems publicly. Twitter released the open-source AnomalyDetection R package based on seasonal decomposition and the (Seasonal) Hybrid ESD test. LinkedIn open-sourced ThirdEye for monitoring and root-cause analysis. Netflix wrote about robust principal-component-based detection for its metrics. The next stage describes these in more detail.

## Key points

- Use a seasonal baseline and a robust z-score as the first detector.
- Alert quality (precision, alerts per day) matters more than detector sophistication.
- Persistence, grouping, severity and cooldown cut false alerts.
- Handle missing data and sparse metrics explicitly.
- Collect feedback and monitor the platform itself.
