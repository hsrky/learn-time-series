---
slug: big-sellers
title: Big Sellers
difficulty: Easy
type: function
tags: [pandas, dataframe, filter]
skills: [pandas-fluency]
packages: []
companies_style: [retail]
---
A DataFrame `df` has the column `units` (units sold per row). The index holds dates.

Write `big_sellers(df, min_share)`.

1. Add a column `share`. It is `units` divided by the **sum of all units** in `df`.
2. Keep only the rows where `share >= min_share`.
3. Return the DataFrame with the original columns plus `share`. Keep the original order of the rows.

Do not change the input DataFrame.

### Example 1
**Input:** `df` with `units = [10, 30, 60]`, `min_share = 0.3`
**Output:** rows with `units` 30 and 60, with `share` 0.3 and 0.6
**Explanation:** The total is 100. The shares are 0.1, 0.3 and 0.6. The first row is below 0.3.

### Constraints
- `1 <= len(df) <= 10^5`; `units >= 0`; the total is greater than 0.
- `0 <= min_share <= 1`

### Hints
1. Compute `total = df["units"].sum()` first.
2. Make a copy of `df`, then assign `out["share"] = out["units"] / total`.
3. Filter with a boolean mask: `out[out["share"] >= min_share]`.

### Solution explanation
1. `out = df.copy()` protects the input.
2. A column divided by a number is a new Series with the same index.
3. The mask keeps matching rows in the original order.

Time O(n), space O(n). Common bug: `df["share"] = ...` changes the input. Another bug is to use `>` instead of `>=`.
