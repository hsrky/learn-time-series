---
slug: top-k-anomalous-days
title: Top-k Anomalous Days
difficulty: Medium
type: function
tags: [pandas, anomaly, robust, MAD, weekday]
skills: [pandas-fluency, communication]
packages: []
companies_style: [take-home project, operations monitoring]
---
In error analysis you look first at the days that behave strangely. You have a daily series `s` (a `pd.Series` with a daily `DatetimeIndex`). Many series have a weekday pattern, so a Saturday must be compared with other Saturdays.

Write `top_anomalous_days(s, k)`:

1. For each weekday (Monday to Sunday), compute the **median** of the values of that weekday. This is the expected value for each day of that weekday.
2. The residual of a day is `value − expected`.
3. Let `med` be the median of all residuals and `mad = median(|residual − med|)`. The score of a day is `|residual − med| / mad`. If `mad` is 0, use `|residual − med|` as the score.
4. Return the dates of the `k` highest scores as a list of strings `"YYYY-MM-DD"`, highest score first. Break ties by the earlier date. If the series has fewer than `k` days, return all days. For an empty series return `[]`.

### Example 1
**Input:** a series for three weeks (21 days), flat at 10 on weekdays and 20 on weekends, except one Wednesday that has value 50; `k = 1`
**Output:** `["2024-01-10"]`
**Explanation:** The Wednesday median is 10, so the residual of 50 is 40. Every other residual is 0, so `mad` is 0 and the score is the absolute residual. The top day is the spike.

### Constraints
- 0 ≤ len(s) ≤ 10^5, values are finite numbers
- `k` ≥ 1

### Hints
1. `s.groupby(s.index.dayofweek).transform("median")` gives the expected value for every day.
2. Compute the residual, then the median and MAD of the residuals with numpy or pandas.
3. Rank with `sort_values(ascending=False, kind="stable")` after sorting by date, so ties keep the earlier date first.

### Solution explanation
A median per weekday is robust to a few spikes, which a mean is not. The MAD (median absolute deviation) scales the residuals the same way, so a score of 5 means "five typical deviations". Sorting by date first and then using a stable sort by score makes ties pick the earlier day. Time O(n log n).

Common bugs: using the mean (spikes pull it), comparing against the global median (ignores weekdays), and a non-stable sort that breaks the tie rule.
