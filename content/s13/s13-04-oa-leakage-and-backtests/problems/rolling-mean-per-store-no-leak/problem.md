---
slug: rolling-mean-per-store-no-leak
title: Leakage-Free Rolling Mean per Store
difficulty: Medium
type: function
tags: [pandas, rolling, groupby, leakage, features]
skills: [leakage, pandas-fluency]
packages: []
companies_style: [retail demand, feature engineering]
---
You build a feature for a model that predicts today's sales for each store. The feature is the mean sales of the **previous** `window` days of the **same store**.

Write `prev_rolling_mean(df, window)`. For each row it must return the mean of up to `window` earlier rows of the same store. **Today's row must not be used.** If a store has fewer than `window` earlier days, use the days that exist. If there are no earlier days (the first day of a store), return `NaN`.

`df` has columns `store`, `date`, `sales`. There is one row per store and day, the days of a store are consecutive, and the rows can be in any order. Return a `pd.Series` with the **same index as `df`** (same row order as the input).

### Example 1
**Input:** `window = 2`
```
store  date        sales
A      2024-01-01  10
A      2024-01-02  20
A      2024-01-03  60
B      2024-01-01  5
```
**Output:** `[NaN, 10.0, 15.0, NaN]`
**Explanation:** Store A on day 2 uses only day 1: 10. On day 3 it uses days 1 and 2: (10 + 20) / 2 = 15. The first day of each store has no past, so NaN. Store B is never mixed with A.

### Constraints
- 0 ≤ number of rows ≤ 10^5
- 1 ≤ `window` ≤ 365
- `sales` has no missing values

### Hints
1. Within one store, the feature for day t is the mean of days t-window to t-1. First move the series by one day with `shift(1)`.
2. Then apply `rolling(window, min_periods=1).mean()` to the shifted series.
3. Do it per store with `groupby("store")["sales"].transform(...)`. Sort by store and date first, then put the result back in the original order using the index.

### Solution explanation
Sort by store and date, then use `groupby(...).transform` with `s.shift(1).rolling(window, min_periods=1).mean()`. The `shift(1)` first removes today's value from the window, so the feature only uses the past. `min_periods=1` allows short histories, and the first row stays NaN because the shifted value is NaN. Assigning the result back by index restores the input order. Time O(n log n) for the sort.

Common bugs: rolling without shift (this includes today and leaks the answer), a rolling window over the whole table without groups (mixes stores), and returning the result in sorted order instead of the original order.
