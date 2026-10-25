---
slug: calendar-features
title: Calendar and Holiday Distance Features
difficulty: Medium
type: function
tags: [pandas, calendar, holidays, features]
skills: [pandas-fluency, leakage]
packages: []
---
Write `calendar_features(dates, holidays)`.

- `dates` is a `pd.DatetimeIndex` (any order, may be empty). Dates have no time of day (midnight).
- `holidays` is a list of date strings (any order, may contain duplicates, may be empty).

Return a `DataFrame` with `dates` as its index (same order as the input) and these integer-like columns:

- `dow`: day of week, Monday = 0.
- `is_weekend`: 1 for Saturday and Sunday, else 0.
- `month`: 1 to 12.
- `is_holiday`: 1 if the date is in `holidays`, else 0.
- `days_to_next`: days from the date to the first holiday **on or after** it (0 on a holiday). `NaN` if there is none.
- `days_since_last`: days from the last holiday **on or before** the date to the date (0 on a holiday). `NaN` if there is none.

`dow`, `is_weekend`, `month` and `is_holiday` are integers. `days_to_next` and `days_since_last` are floats.

### Example 1
**Input:** `dates = 2024-12-23 … 2024-12-27`, `holidays = ["2024-12-25"]`

**Output:**

| date | dow | is_weekend | month | is_holiday | days_to_next | days_since_last |
|---|---|---|---|---|---|---|
| 2024-12-23 | 0 | 0 | 12 | 0 | 2 | NaN |
| 2024-12-24 | 1 | 0 | 12 | 0 | 1 | NaN |
| 2024-12-25 | 2 | 0 | 12 | 1 | 0 | 0 |
| 2024-12-26 | 3 | 0 | 12 | 0 | NaN | 1 |
| 2024-12-27 | 4 | 0 | 12 | 0 | NaN | 2 |

### Constraints
- 0 ≤ len(`dates`) ≤ 10^5, 0 ≤ len(`holidays`) ≤ 10^4.

### Hints
1. Convert the holidays to a sorted, unique `DatetimeIndex`.
2. `holidays.searchsorted(dates, side="left")` gives the position of the first holiday on or after each date.
3. For the last holiday on or before, use `side="right"` and subtract 1. Mark positions outside the list as `NaN`.

### Solution explanation
`searchsorted` finds neighbours in O(log m) per date, so the whole function is vectorized: O((n + m) log m). Positions equal to `len(holidays)` mean "no next holiday"; position `−1` means "no previous holiday". Common bugs: using `side="right"` for the next holiday (it skips a holiday that is today), and the Sunday = 6 convention (`dayofweek` already gives Monday = 0).
