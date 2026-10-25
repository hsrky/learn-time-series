---
slug: direct-dataset
title: Build a Direct Forecasting Dataset
difficulty: Medium
type: function
tags: [pandas, lag-features, leakage, supervised]
skills: [leakage, pandas-fluency]
packages: []
companies_style: [retail demand]
---
You want to train a model that, standing at time t, predicts the value `h` steps later. Write `direct_dataset(s, n_lags, h)`.

Return a DataFrame. Each row is a **forecast origin** t (index = the timestamp of t). The columns, in this order:

- `lag_0, lag_1, ..., lag_{n_lags-1}`: `lag_j` is the value of `s` at time t − j. So `lag_0` is the value at the origin.
- `target`: the value of `s` at time t + h.

Drop every row that has a NaN in any column (the first rows have no past, the last `h` rows have no target). The series has a regular index and no NaN values.

### Example 1
**Input:** `s = [1, 2, 3, 4, 5]`, `n_lags = 2`, `h = 1`
**Output:**

| origin | lag_0 | lag_1 | target |
|---|---|---|---|
| day 2 | 2 | 1 | 3 |
| day 3 | 3 | 2 | 4 |
| day 4 | 4 | 3 | 5 |

**Explanation:** Day 1 has no lag_1. Day 5 has no target.

### Constraints
- `1 <= n_lags`, `1 <= h`, `len(s) >= 1`. The result can be empty.
- Features must use only values at or before the origin.
- Do not use a Python loop over rows.

### Hints
1. `s.shift(j)` is the value j steps in the past.
2. `s.shift(-h)` is the value h steps in the future. It is allowed only for the **target**.
3. Build a DataFrame from a dictionary of Series and call `dropna()`.

### Solution explanation
1. `cols = {f"lag_{j}": s.shift(j) for j in range(n_lags)}` builds the features.
2. `cols["target"] = s.shift(-h)` adds the answer to predict.
3. `pd.DataFrame(cols).dropna()` removes incomplete rows.

Time O(n · n_lags). This is the "direct" strategy of multi-step forecasting: one row per origin, one target per horizon. Bug to avoid: using `shift(-j)` for the features leaks the future.
