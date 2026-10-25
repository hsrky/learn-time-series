---
slug: holiday-dummies
title: Holiday Dummy Features
difficulty: Easy
type: function
tags: [holidays, dummy-variables, pandas, feature-engineering]
skills: [pandas-fluency, leakage]
packages: []
companies_style: [retail demand]
---
Build holiday features for a regression model, with pandas.

Write `holiday_features(dates, holidays, before=0, after=0)`.

- `dates`: a `pd.DatetimeIndex` (the days of your series; daily frequency, may be unsorted, no duplicates).
- `holidays`: a dict `{name: list of date strings}`. For example `{"xmas": ["2023-12-25", "2024-12-25"]}`.
- `before`, `after`: the number of days **before** and **after** each holiday that should also be marked (the effect often spreads).

Return a `DataFrame` with the same index as `dates` (same order). It has one integer column (`0` or `1`) for each holiday name, in the order of the dict. A day gets `1` in the column of a holiday if it lies within `[holiday - before days, holiday + after days]` for any date of that holiday. It also gets a final column `"any_holiday"`, which is `1` if any holiday column is `1` that day.

Compare **calendar days** (ignore the time of the day: normalise to midnight).

### Example 1
**Input:** `dates = 2023-12-23 .. 2023-12-27`, `holidays = {"xmas": ["2023-12-25"]}`, `before=1, after=0`
**Output:** a frame with `xmas = [0, 1, 1, 0, 0]` and `any_holiday = [0, 1, 1, 0, 0]`.
**Explanation:** The marked days are Dec 24 (the day before) and Dec 25.

### Example 2
**Input:** two holidays `{"a": ["2024-01-01"], "b": ["2024-01-02"]}` with `before=0, after=0` on 3 days.
**Output:** `a = [1, 0, 0]`, `b = [0, 1, 0]`, `any_holiday = [1, 1, 0]`.

### Constraints
- `0 <= len(dates) <= 10^4`, `0 <= before, after <= 14`
- Holiday dates may be outside the range of `dates`. Ignore them silently.
- Use integers (`int`) for all columns.

### Hints
1. Normalise the index: `idx = dates.normalize()`.
2. For one holiday, loop over its dates and use `idx.to_series()` comparisons, or `np.isin` with the expanded list of marked days.
3. Expand each holiday date into `pd.date_range(h - before days, h + after days)`.

### Solution explanation
For each holiday we expand every date into a small window of days and mark the days that fall inside. The union over holiday names gives `any_holiday`. Time O(n + H * (before + after)) where H is the number of dates. Common bugs: comparing timestamps with a time of day, forgetting the future dates in the training of a real model, and returning booleans instead of integers.
