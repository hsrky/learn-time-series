---
slug: forecast-error-by-segment
title: Error Analysis by Segment
difficulty: Medium
type: function
tags: [pandas, error-analysis, WAPE, bias, groupby]
skills: [metrics, communication, pandas-fluency]
packages: []
companies_style: [take-home project, retail demand]
---
In a take-home project, reviewers ask: "Where does your model fail?" A single average hides the answer. You group the errors by segment (for example product category) and rank the segments.

Write `error_by_segment(df)`. `df` has columns `segment`, `actual`, `forecast`. For each segment compute:

- `n`: the number of rows
- `wape`: sum(|actual − forecast|) / sum(actual) (NaN if sum(actual) is 0)
- `bias`: sum(forecast − actual) / sum(actual) (NaN if sum(actual) is 0). Positive means over-forecast.
- `share_of_error`: the segment's sum of |actual − forecast| divided by the total absolute error of all rows (0 if the total is 0)

Return a DataFrame with columns `segment, n, wape, bias, share_of_error`, sorted by `share_of_error` descending (ties: by `segment` ascending), with a fresh index.

### Example 1
**Input:**
```
segment  actual  forecast
food     100     110
food     100     90
toys     10      30
toys     10      10
```
**Output:**
```
segment  n  wape  bias  share_of_error
food     2  0.10  0.00  0.5
toys     2  1.00  1.00  0.5
```
**Explanation:** Food errors: 10 and 10, total 20 of 200 actual: WAPE 0.10. Over- and under-forecasts cancel, so bias is 0. Toys error 20 of 20 actual: WAPE 1.0, bias +1.0. Total error is 40, so each segment has share 0.5. Notice that toys looks terrible on WAPE but is only half of the error.

### Constraints
- 0 ≤ rows ≤ 10^5
- `actual` ≥ 0, `forecast` is any number

### Hints
1. Create two helper columns: `abs_err` and `signed_err = forecast - actual`.
2. `groupby("segment")` then sum `abs_err`, `signed_err`, `actual` and count rows.
3. Divide the sums (use `where` for the zero case) and sort with `sort_values(["share_of_error", "segment"], ascending=[False, True])`.

### Solution explanation
All three ratios are ratios of sums, which is how WAPE is defined. The `share_of_error` column tells the reviewer where to spend time: a segment with a high WAPE but a tiny share is not the first thing to fix. Time O(n log n). Common bugs: averaging row-level percentages, and sorting by WAPE instead of share of error.
