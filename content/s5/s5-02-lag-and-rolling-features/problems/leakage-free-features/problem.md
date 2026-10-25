---
slug: leakage-free-features
title: Leakage-Free Lag and Rolling Features
difficulty: Medium
type: function
tags: [pandas, features, groupby, leakage]
skills: [leakage, pandas-fluency]
packages: []
---
You get a long table `df` with columns `series_id`, `date` and `y`. It holds several daily series and the rows may be in any order. Dates are not duplicated within a series. Dates may have **gaps**: you must shift by **rows** inside each series (after sorting by date), not by calendar days.

Write `build_features(df)`. It returns a new table sorted by `series_id`, then `date`, with a fresh index `0 … n-1`, and these columns in this order:

`series_id, date, y, lag_1, lag_7, roll_mean_3, roll_std_3, exp_mean`

All features are computed **inside each series** and must not use the current row's `y`:
- `lag_1`: `y` one row earlier. `lag_7`: `y` seven rows earlier.
- `roll_mean_3`: mean of the three previous values (`lag_1`, `lag_2`, `lag_3`). `NaN` if fewer than 3 previous values exist.
- `roll_std_3`: sample standard deviation (`ddof=1`) of the same three values. `NaN` if fewer than 3.
- `exp_mean`: mean of **all** previous values. `NaN` in the first row.

### Example 1
**Input:** one series `a` with `y = 10, 12, 11, 13, 15`

**Output (selected columns):**

| y | lag_1 | roll_mean_3 | exp_mean |
|---|---|---|---|
| 10 | NaN | NaN | NaN |
| 12 | 10 | NaN | 10 |
| 11 | 12 | NaN | 11 |
| 13 | 11 | 11 | 11 |
| 15 | 13 | 12 | 11.5 |

**Explanation:** For the last row the three previous values are 12, 11, 13, so the mean is 12. The current value 15 is not used.

### Constraints
- 0 ≤ rows ≤ 10^5. `y` may contain `NaN` (it simply propagates; `min_periods` is 3 for the rolling window).

### Hints
1. Sort first: `df.sort_values(["series_id", "date"])`.
2. Use `g = df.groupby("series_id")["y"]` and `g.shift(k)`.
3. For rolling features, shift first and roll inside each group: `g.transform(lambda s: s.shift(1).rolling(3).mean())`.

### Solution explanation
Sort once, then compute every feature with `groupby(...).transform(...)` on the shifted series, so each series is handled alone and the result stays aligned with the original rows. The shift by one row before rolling and expanding removes the current target from every window. Time O(n log n) for the sort plus O(n) for features. Common bugs: calling `rolling` without the shift, shifting over the whole table (lags cross series), and forgetting to sort by date.
