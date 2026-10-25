---
slug: per-series-scaler
title: Per-Series Scaler with Inverse Transform
difficulty: Medium
type: class
tags: [scaling, log1p, class, leakage]
skills: [leakage, from-scratch, pandas-fluency]
packages: []
---
Implement the class `PerSeriesScaler(log=True)`. It scales many series with their own statistics.

**`fit(df, cutoff)`**: `df` has columns `series_id`, `date` and `y`. Use only rows with `date < cutoff` (a string or timestamp). For each series:
- `v = log1p(y)` if `log=True`, else `v = y`.
- store `mu = mean(v)` and `sd = std(v)` with `ddof=0`.
- if the standard deviation is 0, store `sd = 1.0`.
- if the series has **no** training rows, store `mu = 0.0` and `sd = 1.0`.

**`transform(df)`**: return a `Series` (same index as `df`) with `(v − mu) / sd` for every row, using the statistics of the row's series. Series that were not seen in `fit` use `mu = 0`, `sd = 1`.

**`inverse_transform(series_ids, z)`**: `series_ids` and `z` are equal-length lists. Return a numpy array with `v = z * sd + mu`, then `y = expm1(v)` if `log=True` (and clip at 0 with `np.maximum(y, 0)`), else `y = v`. Unknown ids use `mu = 0`, `sd = 1`.

### Example 1
**Input:** series `a` with `y = [0, 9, 99]` at dates `2024-01-01 … 03`, `fit(df, "2024-01-03")`

**Output:** training rows are `0` and `9`. `log1p` gives `0` and `2.3026`. `mu = 1.1513`, `sd = 1.1513`. `transform` of the three rows gives `[-1, 1, 3.0]`.

**Explanation:** `log1p(99) = 4.6052`, so `(4.6052 − 1.1513) / 1.1513 = 3.0`. The cutoff row (the third) is **not** used for fitting.

### Constraints
- Up to 10^5 rows and 10^4 series. `y ≥ 0` when `log=True`.

### Hints
1. Filter the training rows first, then use `groupby("series_id")` with `agg(["mean", "std"])`. Remember `ddof=0`.
2. Store `mu` and `sd` as dictionaries keyed by `series_id`. Use `.map(dict)` and `fillna` for unknown ids.
3. In `inverse_transform` apply the steps in reverse: de-standardize, then `expm1`, then clip.

### Solution explanation
`fit` computes the statistics on `date < cutoff` only, so the test period cannot shape the scaler. `transform` and `inverse_transform` are exact inverses (up to clipping). Time O(n). Common bugs: `ddof=1` (pandas default), fitting on all rows, forgetting the `sd = 0` case, and inverting in the wrong order.
