---
slug: m4-owa
title: M4 Overall Weighted Average (OWA)
difficulty: Medium
type: function
tags: [metrics, M4, sMAPE, MASE, benchmarking]
skills: [forecast-metrics, numpy-fluency]
packages: []
companies_style: [forecasting competition, benchmarking]
---
The M4 competition ranked methods with the **Overall Weighted Average** (OWA). It compares a method with a simple benchmark called **Naive2** (a naive forecast after removing seasonality). A score of 1.0 means "as good as Naive2". Lower is better.

For one series with history `train` (length n), true future values `test` (length h) and a forecast `fc`:

- **sMAPE** = mean over the horizon of `200 · |y − f| / (|y| + |f|)` (a percent).
- **MASE** = `mean(|y − f|)` divided by the **in-sample seasonal naive error**: `mean(|train[t] − train[t−m]|)` for `t = m … n−1`. Here `m` is the season length (`m = 1` for a non-seasonal series).

For a set of series, average sMAPE and MASE over all series, separately for your method and for Naive2:

**OWA = 0.5 · ( sMAPE / sMAPE_naive2 + MASE / MASE_naive2 )**

Write `owa(train, test, fc, fc_naive2, m)`. The four first arguments are **lists of 1-D arrays**, one per series. Return the OWA as a float.

### Example 1
**Input:** one series: `train=[10,12,14,16]`, `test=[18,20]`, `fc=[17,22]`, `fc_naive2=[16,16]`, `m=1`
**Output:** about `0.4742`
**Explanation:** The in-sample scale is 2. Your MASE is 1.5 / 2 = 0.75 and the Naive2 MASE is 3 / 2 = 1.5. Your sMAPE is 7.62 and the Naive2 sMAPE is 16.99. OWA = 0.5 · (7.62 / 16.99 + 0.75 / 1.5) = 0.474.

### Constraints
- 1 ≤ number of series ≤ 10 000. Values are positive. Every history has at least `m + 1` points.
- Series can have different lengths.

### Hints
1. Write a small helper that returns `(smape, mase)` for one series.
2. The scale is `np.mean(np.abs(train[m:] - train[:-m]))`.
3. Average the per-series numbers first, then divide method by Naive2, then average the two ratios.

### Solution explanation
Compute sMAPE and MASE per series for the method and for Naive2, average over series, and combine the two ratios with equal weight. MASE makes errors comparable across series with different scales, and sMAPE gives a percent view. Averaging ratios of averages (not averaging per-series ratios) follows the M4 definition. Complexity: O(total length). Common bugs: using `train[m:] - train[:-m]` with `m = 0`, using `/ 2` instead of `200 /` in sMAPE, and averaging ratios per series.
