---
slug: point-in-time-join
title: Point-in-Time Feature Join
difficulty: Medium
type: function
tags: [pandas, merge_asof, point-in-time, leakage]
skills: [leakage, pandas-fluency, production]
packages: []
---
You have a table of prediction events and a table of feature values that arrive over time.

- `events`: columns `id`, `time` (and maybe more). One row per prediction, **in any order**.
- `features`: columns `id`, `available_at`, `value`. A row means: from `available_at` on, the feature of this `id` has this `value`, until a newer row replaces it. Rows may be in any order.

Write `pit_join(events, features, tolerance_hours=None)`. For each event, find the **latest** feature row of the **same `id`** with `available_at <= time` (a feature that becomes available exactly at the event time counts). Add two columns to the events:

- `feature_time`: the `available_at` of the matched row, or `NaT` if none.
- `feature_value`: the matched `value`, or `NaN` if none.

If `tolerance_hours` is not `None`, a match older than this many hours (`time - available_at > tolerance_hours`) is ignored: both columns are missing.

Return the events in their **original order and with their original index**, with the original columns first and the two new columns last.

### Example 1
**Input:** events for id `a` at `2024-01-01 09:00` and `2024-01-03 08:00`; features for id `a`: `2023-12-31 00:00 → 10`, `2024-01-01 12:00 → 9`, `2024-01-03 09:00 → 8`.

**Output:** `feature_value = [10, 9]`

**Explanation:** At Jan 1 09:00 the latest known value is 10 (set on Dec 31). At Jan 3 08:00 it is 9. The value 8 starts one hour later and must not be used.

### Constraints
- 0 ≤ events, features ≤ 10^5. Times are `datetime64`. Ids can be strings or integers.

### Hints
1. `pd.merge_asof` needs both tables sorted by their time key. Remember the original order of `events` (save the index in a column).
2. Use `by="id"`, `direction="backward"`, and `tolerance=pd.Timedelta(hours=...)` when given.
3. Rename the right columns to `feature_time` and `feature_value` before merging, and restore the original order and index at the end.

### Solution explanation
`merge_asof(direction="backward")` is exactly the as-of rule. We sort, merge, then sort back. `allow_exact_matches=True` (the default) keeps features that arrive exactly at the event time. Time O((n + m) log(n + m)). Common bugs: `direction="nearest"` or `"forward"` (leak), joining on the date only, and losing the original order.
