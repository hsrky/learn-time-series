---
id: s10-03-drift-monitoring
title: Monitoring data drift and concept drift
minutes: 25
level: advanced
goals: [Tell data drift from concept drift, Compute the Population Stability Index (PSI), Decide what to monitor when labels arrive late]
prereqs: [s10-02-pipelines-and-retraining]
tags: [drift, PSI, monitoring, production]
skills: [ml-system-design, monitoring]
---

## Warm-up

```check
{"q": "A job runs twice and the table has duplicate rows. Which word describes the missing property?", "type": "single",
 "options": ["Stationary", "Idempotent", "Seasonal"],
 "answer": 1,
 "why": ["Stationary describes a series, not a job.", "Correct: an idempotent job gives the same result when run again.", "Seasonal describes a repeating pattern in data."]}
```

```check
{"q": "Which retraining trigger can work WITHOUT labels?", "type": "single",
 "options": ["Live error above a limit", "Input drift above a limit", "Both need labels"],
 "answer": 1,
 "why": ["Error needs the true values, which arrive later.", "Correct: you compare input data only.", "Drift on inputs does not need labels."]}
```

## Why it matters

A model that was right in March is not always right in October. The world changes: prices, customers, sensors, and rules change. Nobody tells the model. If you do not **monitor**, the first sign of trouble is an angry business user. Good monitoring finds the change early, ideally before the error grows.

## Two kinds of drift

**[[data drift]]** (also called covariate shift): the *inputs* look different. The model is the same, but it now sees values it rarely saw in training.

**[[concept drift]]**: the *relationship* between inputs and target changes. The inputs may look the same, but the right answer is different.

| | Data drift | Concept drift |
|---|---|---|
| What changes | Distribution of inputs X | The rule from X to y |
| Example | A new store type with 3 times more orders | After a price rise, the same traffic gives fewer sales |
| Needs labels to detect? | No | Yes (you must see the error) |
| Typical fix | Retrain with new data, check features | Retrain, maybe change features or model |

```chart
{"title": "Data drift: the input level moves", "x": "day", "height": 220,
 "series": [
   {"name": "feature (average basket size)", "gen": [["const", {"value": 20}], ["step", {"at": 60, "size": 6}], ["noise", {"sd": 1.2}]], "n": 100, "seed": 9}
 ],
 "marks": [{"x": 60, "label": "new customer group"}],
 "caption": "The average moves from about 20 to about 26. A model trained on the first part now sees unusual inputs."}
```

```check
{"q": "After a big price increase, the same website traffic leads to fewer sales. Which drift is this?", "type": "single",
 "options": ["Data drift only", "Concept drift", "No drift", "A bug in pandas"],
 "answer": 1,
 "why": ["Traffic (the input) did not change.", "Correct: the link between traffic and sales changed.", "The rule did change.", "Nothing is wrong in the tools; the world changed."]}
```

Drift also has shapes: **sudden** (a step), **gradual** (slow slide), **recurring** (a season returns). A seasonal change is not a problem if the model knows the season. Do not raise an alert for something the model already expects.

## Measuring data drift with PSI

The **[[Population Stability Index]]** (PSI) compares two distributions of one feature. The *expected* one comes from training data. The *actual* one comes from recent data. It is common in credit scoring and in ML monitoring.

Steps with an example (4 bins):

1. Cut the training values into bins with equal shares (quartiles): 25% in each bin.
2. Count the share of recent data in the same bins. Suppose 10%, 20%, 30%, 40%.
3. For each bin compute `(a − e) × ln(a / e)`.

## The PSI formula and how to read it

Formula: **PSI = Σ (a_i − e_i) · ln(a_i / e_i)**

- `e_i` = share of training data in bin i (expected)
- `a_i` = share of recent data in bin i (actual)
- `ln` = natural logarithm

Bin by bin: (0.10−0.25)·ln(0.4) = 0.1374; (0.20−0.25)·ln(0.8) = 0.0112; (0.30−0.25)·ln(1.2) = 0.0091; (0.40−0.25)·ln(1.6) = 0.0705. The sum is **0.228**.

Common guideline: **below 0.1** stable, **0.1 to 0.25** some shift (look), **above 0.25** big shift (act). These are conventions, not laws. Each term is never negative, so PSI is never negative.

```check
{"q": "Training shares are 50% / 50% and recent shares are 50% / 50%. What is PSI?", "type": "numeric",
 "answer": 0, "tol": 0.001,
 "why": "Every (a − e) is 0, so every term is 0 and PSI = 0."}
```

```check
{"q": "Why must we protect against a bin share of exactly 0?", "type": "single",
 "options": ["ln(0) is undefined (minus infinity)", "Zero is a bad number", "pandas cannot divide", "It makes the PSI negative"],
 "answer": 0,
 "why": ["Correct: a / e or e / a can be 0, and the log breaks. Clip shares to a small value like 0.0001.", "Zero itself is fine. The log is the problem.", "Division is fine; the log of 0 is the problem.", "Each term stays non-negative."]}
```

## What to monitor

Build a layered view, from fast to slow:

1. **Data quality** (no labels): missing values, row counts, late files, out-of-range values.
2. **Input drift** (no labels): PSI or other tests per feature; also the *forecast itself* (does it look normal?).
3. **Forecast error** (labels needed): MAE or WAPE against actuals, by segment. Labels are delayed, so this is the slowest signal.
4. **Business metric**: stock-outs, waste, cost.

Beware of **too many alerts**: with 200 features some will drift by chance. Pick the top features by importance, set thresholds from history, and require the drift to last for several days.

## Worked example

We compute PSI for a feature that shifts upward by one standard deviation.

```python
import numpy as np

def psi(expected, actual, bins=10, eps=1e-4):
    expected, actual = np.asarray(expected, float), np.asarray(actual, float)
    # inner bin edges = quantiles of the TRAINING data
    inner = np.quantile(expected, np.linspace(0, 1, bins + 1)[1:-1])
    e = np.bincount(np.searchsorted(inner, expected, side="right"), minlength=bins) / len(expected)
    a = np.bincount(np.searchsorted(inner, actual, side="right"), minlength=bins) / len(actual)
    e, a = np.clip(e, eps, None), np.clip(a, eps, None)   # avoid log(0)
    return float(np.sum((a - e) * np.log(a / e)))

rng = np.random.default_rng(1)
train = rng.normal(0, 1, 5000)
same = rng.normal(0, 1, 2000)       # no drift
shifted = rng.normal(1, 1, 2000)    # mean moved by 1 sd

print("no drift :", round(psi(train, same), 3))
print("shifted  :", round(psi(train, shifted), 3))
# Output:
# no drift : 0.007
# shifted  : 0.928
```

No drift gives a PSI near 0. A shift of one standard deviation gives a value far above 0.25: the alarm would fire.

## Common mistakes

- Using PSI with bins made from the *recent* data instead of the training data. Bins must stay fixed.
- Alerting on every drift. Drift without error increase may not matter; error increase without drift points to concept drift.
- Checking only the mean. The spread or the share of missing values can change while the mean stays the same.
- Forgetting seasonality: December always looks different from July.
- Using too few recent points. PSI on 30 rows is noise.

## Interview lens

**Typical question:** "How do you know your forecasting model is going bad in production?"

**Strong answer:** I monitor in layers. First data quality and input drift, such as PSI per key feature, because these need no labels. Then forecast error (WAPE or MAE) by segment as labels arrive, compared with a seasonal naive baseline. I set thresholds from history and require the signal to last a few days, to avoid noise. When error rises and inputs did not drift, I suspect concept drift and look at what changed in the business. The action is a retrain or a rollback, decided by a backtest.

**Red flags:** Only looking at accuracy on the test set from training time. No baseline to compare with. Treating every PSI above 0.1 as an emergency.

## Real world

PSI comes from credit risk. Banks have used it for many years to check if a scoring population has changed. Open-source tools such as Evidently and others report PSI and statistical tests like Kolmogorov-Smirnov for each feature. The thresholds 0.1 and 0.25 are common conventions in that field.

## Key points

- Data drift: inputs change. Concept drift: the rule from inputs to target changes.
- Data drift can be seen without labels. Concept drift needs error data.
- PSI = Σ (a − e)·ln(a / e) over bins fixed from the training data. Common guideline: 0.1 and 0.25.
- Protect against empty bins, use enough data, and ignore expected seasonal change.
- Monitor in layers: data quality, input drift, forecast error, business metric.
