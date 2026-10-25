---
slug: pit-join-asof
title: Point-in-Time Join
difficulty: Medium
type: function
tags: [pandas, merge_asof, leakage, feature-store]
skills: [leakage-free-features, pandas-fluency]
packages: []
companies_style: [food delivery, retail demand]
---
You have a table of **labels** (events you want to predict) and a table of **feature snapshots**. Each snapshot has the time when the value became known. Build a training table where every label gets the **latest feature values known at or before its time**, for the same entity.

Write `point_in_time_join(labels, features, tolerance=None)`.

- `labels` has columns `entity`, `ts`, `label`.
- `features` has columns `entity`, `feature_ts` and one or more feature columns.
- Return the label columns plus all feature columns, **without** `feature_ts`.
- Keep the **same row order** as `labels`, with a fresh index `0..n-1`.
- A feature with `feature_ts == ts` may be used.
- If `tolerance` is a `pd.Timedelta`, a feature older than `ts - tolerance` is too old: the result is NaN. `None` means no limit.
- If no feature exists, the feature columns are NaN.

The input tables can be in any order. Do not change them.

### Example 1
**Input:**
```
labels:   entity ts                label
          A      2024-01-02 12:00  1
features: entity feature_ts        x
          A      2024-01-02 02:00  10
          A      2024-01-03 02:00  20
```
**Output:** one row with `x = 10`.
**Explanation:** The value 20 is from the next day. It is in the future for the label.

### Constraints
- Up to 100 000 rows.
- `ts` and `feature_ts` are datetime64 columns. Entities are strings.
- Feature columns are numeric.

### Hints
1. Look at `pd.merge_asof`. It matches the nearest earlier row.
2. It needs both tables sorted by the time key. Add a helper column with the original row number so you can restore the order.
3. Use `by="entity"`, `direction="backward"`, and pass `tolerance`. Sort by row number at the end and drop the helper columns.

### Solution explanation
1. Copy the labels and add `_row = range(n)`.
2. Sort labels by `ts` and features by `feature_ts` (both required by `merge_asof`).
3. Call `merge_asof` with `left_on="ts"`, `right_on="feature_ts"`, `by="entity"`, backward direction and the tolerance.
4. Sort by `_row` to get the original order, drop `_row` and `feature_ts`, and reset the index.

Complexity: O(n log n) for sorting, O(n + m) for the merge. Common bugs: forgetting to sort, using `direction="nearest"`, changing the caller's data, and losing the original row order.
