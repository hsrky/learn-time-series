---
slug: merge-irregular-sensors
title: Merge Two Irregular Sensors
difficulty: Hard
type: function
tags: [pandas, merge_asof, irregular, join]
skills: [pandas-fluency, leakage]
packages: []
companies_style: [IoT, equipment monitoring, OA]
---
Two sensors on the same machines send readings at **irregular** times. Sensor A sends `temp`. Sensor B sends `humidity`. The two sensors do not send at the same moments.

For every reading of sensor A, find the **latest** reading of sensor B from the **same device** with a time **less than or equal to** the A time. Use it only if it is not older than `tol_seconds`. If there is no such reading, the humidity is `NaN`.

Write `attach_latest(a, b, tol_seconds)`.

- `a` has columns `device`, `time` (datetime), `temp`.
- `b` has columns `device`, `time` (datetime), `humidity`.
- Both can be in any order. In `a`, each (`device`, `time`) pair is unique.
- Return a DataFrame with columns `device`, `time`, `temp`, `humidity`, one row per row of `a`, sorted by `device` then `time`, with a fresh index.

A B reading from the future (after the A time) must **never** be used. This would be look-ahead leakage.

### Example 1
**Input:** `tol_seconds = 60`
```
a: device  time      temp        b: device  time      humidity
   m1      10:00:30  20.0           m1      10:00:00  40.0
   m1      10:03:00  21.0           m1      10:00:50  45.0
   m2      10:00:30  19.0           m2      10:05:00  50.0
```
**Output:**
```
device  time      temp  humidity
m1      10:00:30  20.0  40.0
m1      10:03:00  21.0  NaN
m2      10:00:30  19.0  NaN
```
**Explanation:** At 10:00:30 the latest B reading of m1 is 10:00:00 (30 s old), so humidity is 40. At 10:03:00 the latest is 10:00:50, which is 130 s old and too old. For m2 the only B reading is in the future.

### Constraints
- 0 ≤ rows in a, b ≤ 10^5
- 0 ≤ `tol_seconds` ≤ 10^6
- A B reading with exactly the same time as the A reading is allowed (age 0)
- A B reading that is exactly `tol_seconds` old is allowed

### Hints
1. This is an "as of" join. Plain `merge` needs equal times and will not work.
2. Look at `pd.merge_asof`. Both tables must be sorted by the time column.
3. Use `by="device"`, `direction="backward"` and `tolerance=pd.Timedelta(seconds=tol_seconds)`. Sort the result at the end.

### Solution explanation
`merge_asof` walks through the left table and, for each row, takes the nearest right row that is not later (`direction="backward"`). `by="device"` stops it from mixing machines. `tolerance` removes matches that are too old, and these rows get NaN. Both inputs must be sorted by `time` first. The cost is O(n log n) for sorting, then one linear pass.

Common bugs: forgetting to sort (pandas raises an error), using `direction="nearest"` (which can use the future and leaks), and forgetting `by`, which mixes devices.
