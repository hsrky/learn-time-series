---
id: s11-08-anomaly-detection-at-large-companies
title: Anomaly detection at Twitter, LinkedIn and Netflix
minutes: 30
level: advanced
goals: [Explain the S-H-ESD method from Twitter, Describe what ThirdEye and Netflix RAD do, Run a generalized ESD test on seasonal residuals]
prereqs: [s11-07-kaggle-competitions]
tags: [anomaly-detection, S-H-ESD, ESD, robust-PCA, ThirdEye, case-study]
skills: [case-studies, anomaly-detection]
---

## Warm-up

```check
{"q": "A robust z-score uses...", "type": "single",
 "options": ["The median and the MAD", "The mean and the standard deviation", "The maximum and the minimum"],
 "answer": 0,
 "why": ["Correct: outliers hardly change them.", "Outliers distort the mean and standard deviation.", "Extremes are the most sensitive statistics."]}
```

```check
{"q": "Which metric breaks when an actual value is 0?", "type": "single",
 "options": ["RMSPE", "RMSLE", "MAE"],
 "answer": 0,
 "why": ["Correct: it divides by the actual.", "RMSLE uses log(1 + y), which is fine at 0.", "MAE has no division."]}
```

## Why it matters

Big internet companies watch thousands of metrics: tweets per second, page loads, video starts. They need automatic detection of strange behaviour, with few false alarms. Three companies published useful ideas and code. **Twitter** used statistical tests on seasonal residuals. **LinkedIn** built a platform for detection and root-cause analysis. **Netflix** used robust PCA. This lesson covers only what these companies made public.

## Twitter: S-H-ESD

Twitter released an open-source R package called **AnomalyDetection** (2015). The method is **[[S-H-ESD]]**, Seasonal Hybrid ESD. The paper is "Automatic Anomaly Detection in the Cloud Via Statistical Learning" (Hochenbaum, Vallis and Kejariwal, 2017). The steps:

1. **Remove the seasonal part.** Use STL decomposition to get the seasonal component.
2. **Remove the level.** Subtract the series **median** (not the trend, which is easily pulled by anomalies).
3. You now have a **residual**: `residual = y − seasonal − median(y)`.
4. Run the **generalized ESD test** (Rosner, 1983) on the residual. It detects up to `k` outliers without knowing how many there are.
5. "Hybrid" means that the test uses **median and MAD** instead of mean and standard deviation, which makes it robust.

```check
{"q": "Why does S-H-ESD subtract the median and not the trend line?", "type": "single",
 "options": ["The median is faster", "A trend fitted to data with anomalies is pulled by them; the median is robust", "Trend lines do not exist", "The test needs the median for the p-value"],
 "answer": 1,
 "why": ["Speed is not the reason.", "Correct.", "Trend lines exist, but they are not robust.", "The reason is robustness."]}
```

## Global and local anomalies

The package can find **global** anomalies, which are large compared with the whole series. It can also find **local** anomalies, which are small in absolute value but large for their season. You can limit anomalies to only the positive or negative direction.

## The generalized ESD test

The generalized **Extreme Studentized Deviate** test finds up to `r` outliers in data that are roughly normal. For `i = 1 … r`:

1. Compute `R_i = max |x − mean| / s` on the remaining values (`s` = sample standard deviation).
2. Remove the most extreme value.
3. Compare `R_i` with a critical value `λ_i` from the t distribution.

The number of outliers is the **largest** `i` with `R_i > λ_i`. Removing the extreme one at a time stops a big outlier from hiding (masking) a smaller one. You will implement it in the practice problem.

```chart
{"title": "Seasonal metric with injected anomalies", "x": "hour", "height": 230,
 "series": [
   {"name": "metric", "gen": [["const", {"value": 100}], ["season", {"period": 24, "amp": 25}], ["noise", {"sd": 3}], ["spike", {"at": 70, "size": 55}], ["spike", {"at": 130, "size": -45}]], "n": 168, "seed": 21}
 ],
 "caption": "After removing the daily season, the residual has two extreme values. ESD finds them."}
```

```check
{"q": "ESD removes the most extreme value one at a time. Why?", "type": "single",
 "options": ["To make the code shorter", "A very large outlier inflates the standard deviation and can hide smaller outliers (masking)", "To save memory", "To sort the data"],
 "answer": 1,
 "why": ["Not about code length.", "Correct.", "Not about memory.", "Sorting is not the aim."]}
```

## LinkedIn: ThirdEye (and Luminol)

LinkedIn developed **[[ThirdEye]]**, an open-source platform for monitoring business and system metrics. Its main points, as described publicly:

- Detection with several methods per metric and configurable rules.
- **Root-cause analysis**: after an alert, explore which dimension (country, device, version) explains the change, and look at related events.
- Alert workflow: grouping, notifications and feedback from users to tune detection.

LinkedIn also released **Luminol**, a lightweight Python library for anomaly detection and correlation of time series. The key idea is that detection is only half of the job: users need to know **why** a metric moved.

## Netflix: RAD and robust PCA

Netflix described **RAD** (Robust Anomaly Detection), built on **Robust PCA** (Candes et al.). It was shared in the open-source Surus project. The idea:

- Arrange the data as a **matrix**. For example, each column is one day of a metric and each row is a time of day.
- Split the matrix into two parts, `M = L + S`. The **low-rank** part is the regular, repeating pattern. The **sparse** part holds rare large deviations.
- The entries of `S` that are not zero are the anomalies.

It is useful when the metric has a regular shape that repeats. It does not assume that the data are normal.

```check
{"q": "In Robust PCA, which part holds the anomalies?", "type": "single",
 "options": ["The low-rank part L", "The sparse part S", "The mean", "The eigenvectors"],
 "answer": 1,
 "why": ["L holds the regular pattern.", "Correct: a few large entries.", "The mean is a summary, not a part.", "Eigenvectors describe L."]}
```

## Worked example

We build a small S-H-ESD style detector on 14 days of hourly data. We remove the daily season (median by hour), subtract the median, and run generalized ESD.

```python
import numpy as np
import pandas as pd
from scipy import stats

def generalized_esd(x, max_outliers, alpha=0.05):
    x = np.asarray(x, dtype=float)
    n = len(x)
    remaining, removed, R, lam = list(range(n)), [], [], []
    for i in range(1, max_outliers + 1):
        vals = x[remaining]
        s = vals.std(ddof=1)
        j = int(np.argmax(np.abs(vals - vals.mean())))
        R.append(abs(vals[j] - vals.mean()) / s)
        removed.append(remaining.pop(j))
        p = alpha / (2 * (n - i + 1))
        t = stats.t.ppf(1 - p, n - i - 1)
        lam.append((n - i) * t / np.sqrt((n - i - 1 + t ** 2) * (n - i + 1)))
    k = max([i + 1 for i in range(len(R)) if R[i] > lam[i]], default=0)
    return sorted(removed[:k])

rng = np.random.default_rng(2)
idx = pd.date_range("2024-03-01", periods=24 * 14, freq="h")
y = pd.Series(200 + 40 * np.sin(2 * np.pi * idx.hour / 24) + rng.normal(0, 5, len(idx)), index=idx)
y.iloc[100] += 70     # injected spike
y.iloc[250] -= 60     # injected dip

seasonal = y.groupby(y.index.hour).transform("median") - y.median()   # robust seasonal part, centred
resid = y - seasonal - y.median()                           # S-H-ESD style residual
found = generalized_esd(resid.values, max_outliers=10)
print("anomaly positions:", found)
print("their residuals:", [round(float(resid.iloc[i]), 1) for i in found])
# Output:
# anomaly positions: [100, 250]
# their residuals: [61.3, -61.3]
```

Both injected points are found, and no normal point is flagged. A plain z-score on the raw series would not work. The daily season would make normal evening values look extreme.

### A tiny robust-PCA idea

We show the `M = L + S` split on a 24 x 7 matrix of hours by days. It has a rank-1 pattern and two anomalies. This is a simple alternating version, not the full algorithm.

```python
import numpy as np

rng = np.random.default_rng(0)
pattern = 100 + 40 * np.sin(2 * np.pi * np.arange(24) / 24)          # daily shape
scale = np.array([1.0, 1.0, 1.1, 1.0, 0.9, 1.2, 1.3])                # day-level factor
M = np.outer(pattern, scale) + rng.normal(0, 1.5, (24, 7))
M[5, 2] += 60                                                         # anomaly 1
M[18, 4] -= 50                                                        # anomaly 2

S = np.zeros_like(M)
for _ in range(20):                                                   # alternate: fit L, then S
    U, sv, Vt = np.linalg.svd(M - S, full_matrices=False)
    L = sv[0] * np.outer(U[:, 0], Vt[0])                              # rank-1 part
    R = M - L
    S = np.sign(R) * np.maximum(np.abs(R) - 10, 0)                    # keep only large deviations

print("anomalies found at (hour, day):", [tuple(int(v) for v in p) for p in np.argwhere(np.abs(S) > 0)])
# Output:
# anomalies found at (hour, day): [(5, 2), (18, 4)]
```

The regular shape goes into `L`; only the two rare big deviations stay in `S`.

## Common mistakes

- Running a normal-distribution test on a series that still has a season.
- Setting the maximum number of outliers too small, so a masked outlier is missed.
- Using a threshold only on size; some anomalies are local (small, but wrong for the season).
- Stopping at detection. People need explanations: which dimension, which deployment.
- Ignoring that the test assumes roughly normal residuals; heavy tails give false alarms.

## Interview lens

**Typical question:** "How does Twitter's S-H-ESD work, and what are its limits?"

**Strong answer:** It decomposes the series with STL and removes the seasonal component and the median. Then it runs the generalized ESD test on the residual. It uses median and MAD for robustness. It finds global and local anomalies and can be one-sided. Limits: it assumes roughly normal residuals and a stable seasonal pattern. It is built for batch windows. It does not explain causes. LinkedIn's ThirdEye adds root-cause analysis, and Netflix's RAD uses robust PCA to separate a regular pattern from sparse anomalies. In a platform, I would combine such a detector with persistence, grouping and feedback.

**Red flags:** Confusing ESD with a simple 3-sigma rule. Not knowing why seasonality must be removed. Claiming internal details of these companies' systems that are not public.

## Real world

All three have public sources. Twitter's AnomalyDetection package and the arXiv/KDD paper describe S-H-ESD. LinkedIn's ThirdEye and Luminol are open-source projects. Netflix wrote a technology blog post about RAD and released code in its Surus project. Read the originals for exact settings, and treat anything not in those sources as unknown.

## Key points

- S-H-ESD: STL seasonal part removed, minus median, generalized ESD with median/MAD on the residual.
- Generalized ESD removes the most extreme value step by step. The count is the largest i with R_i above its critical value.
- ThirdEye: detection plus root-cause analysis. Luminol: a lightweight Python library.
- Netflix RAD: robust PCA, matrix = low-rank pattern + sparse anomalies.
- Detection needs explanation, grouping and feedback to be useful.
