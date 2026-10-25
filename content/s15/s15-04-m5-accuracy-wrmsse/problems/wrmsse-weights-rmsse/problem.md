---
slug: wrmsse-weights-rmsse
title: WRMSSE Weights and RMSSE on a Tiny Hierarchy
difficulty: Hard
type: function
tags: [kaggle, m5, WRMSSE, hierarchy, metrics]
skills: [metrics, from-scratch, pandas-fluency]
packages: []
companies_style: [Kaggle M5 Forecasting]
---
The M5 metric, **WRMSSE**, scores forecasts on many aggregation levels of a hierarchy (total, store, department, item...). Each series gets a **weight** (its share of dollar sales on its level) and its error is scaled by the series' own history (**RMSSE**). Write both building blocks.

**1. `hierarchy_weights(bottom, levels)`**

`bottom` is a DataFrame of bottom-level series with some key columns and a column `revenue` (recent dollar sales). `levels` is a list; each item is a list of key columns that define one level. An empty list `[]` means the total. For each level, group the revenue by those columns. The weight of a group is its revenue divided by the total revenue (so weights sum to 1 in every level; if total revenue is 0 use `0.0`).

Return a DataFrame with columns `level` (the position in `levels`), `key` (the key values joined by `"/"`, or `"Total"` for the empty list) and `weight`, sorted by `level`, then `key`, with index `0, 1, 2, ...`.

**2. `rmsse(train, actual, forecast)`**

`scale = mean( (y[t] − y[t−1])² )` over the training history, starting from the **first non-zero** value. `rmsse = sqrt( mean((actual − forecast)²) / scale )`. If there are fewer than 2 values from the first non-zero value on, or the scale is 0, return `nan`.

### Example 1
```
bottom: store dept revenue
        S1    A    30
        S1    B    10
        S2    A    60
levels = [[], ["store"], ["store", "dept"]]
```
Level 0: `Total` weight 1.0. Level 1: `S1` 0.4, `S2` 0.6. Level 2: `S1/A` 0.3, `S1/B` 0.1, `S2/A` 0.6.

### Example 2
`rmsse([0, 0, 2, 4, 6], [8, 10], [7, 12])`: history from the first non-zero: `2, 4, 6`; squared differences `4, 4`; scale 4. Errors `1, 2` give mean squared error 2.5. `rmsse = sqrt(2.5 / 4) = 0.790569...`

### Constraints
- 1 ≤ rows in `bottom` ≤ 10^4, revenue ≥ 0
- `actual` and `forecast` have the same length ≥ 1

### Hints
1. For each level, `bottom.groupby(cols)["revenue"].sum()`; for the total use `bottom["revenue"].sum()`.
2. Build the key with `astype(str)` and `"/".join`.
3. For `rmsse`, find the first non-zero index with `np.nonzero`, then use `np.diff`.

### Solution explanation
Weights make big-money series count more, on each level. RMSSE divides by the in-sample one-step error, so series with very different sizes are comparable, and a score below 1 means better than a naive forecast. Starting the scale at the first non-zero value ignores the time before a product was sold. Time O(levels × n). Common bugs: using the whole history including leading zeros, forgetting the square before the mean, and weights that do not sum to 1.
