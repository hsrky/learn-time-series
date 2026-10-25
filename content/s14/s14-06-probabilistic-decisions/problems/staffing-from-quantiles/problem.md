---
slug: staffing-from-quantiles
title: Staffing Level from Quantile Forecasts
difficulty: Medium
type: function
tags: [staff, quantiles, staffing, service-level, interpolation]
skills: [staff, uncertainty]
packages: []
companies_style: [customer support staffing, capacity planning]
---
A support centre forecasts the number of contacts for each half hour as **quantiles**: for several levels (for example 0.5, 0.9, 0.99) the forecast gives the number of contacts that will not be exceeded with that probability.

One agent can handle `capacity` contacts per half hour. The service goal is a **service level** `p` (for example 0.95): we want enough staff to cover demand with probability `p`.

Write `staff_levels(intervals, capacity, service_level, min_staff=1, max_staff=None)`.

- `intervals` is a list. Each item is a dict `{level: contacts}` with at least one quantile level between 0 and 1 (keys can be in any order).
- For each interval find the demand at `service_level` by **linear interpolation** between the two nearest quantile levels. If `service_level` is below the lowest level, use the lowest level's value. If it is above the highest level, use the highest level's value.
- Staff = `ceil(demand / capacity)`, but at least `min_staff`. If `max_staff` is not `None`, staff is at most `max_staff`.
- Return the list of staff numbers (integers), one per interval.

### Example 1
**Input:**
```
intervals = [{0.5: 40, 0.9: 55, 0.99: 70}, {0.5: 10, 0.9: 12, 0.99: 16}]
capacity = 10, service_level = 0.9
```
**Output:** `[6, 2]`
**Explanation:** Interval 1: demand at 0.9 is 55, so ceil(55 / 10) = 6. Interval 2: demand 12, so ceil(12 / 10) = 2.

### Example 2
Same input with `service_level = 0.95`.
**Output:** `[7, 2]`
**Explanation:** Interval 1: between 0.9 (55) and 0.99 (70). The weight is (0.95 − 0.9) / 0.09 = 0.5556, so demand = 55 + 15 × 0.5556 = 63.33 and ceil(6.33) = 7. Interval 2: 12 + 4 × 0.5556 = 14.22, so ceil(1.42) = 2.

### Constraints
- 0 ≤ number of intervals ≤ 10^4
- `capacity` > 0, 0 < `service_level` < 1
- Quantile values are ≥ 0 and do not decrease with the level

### Hints
1. Sort the items of each dict by level. Use the first and last values for the edge cases.
2. Between two levels `l0 < l1`, the demand is `v0 + (v1 − v0) · (p − l0) / (l1 − l0)`.
3. Avoid float problems with `math.ceil(round(demand / capacity, 9))`. Then apply `min_staff` and `max_staff`.

### Solution explanation
A quantile forecast is a few points of the demand distribution. Linear interpolation fills the gap between them. Covering the `p`-quantile of demand means the centre is short-staffed on at most `1 − p` of intervals (if the forecast is calibrated). Rounding up is essential: half an agent does not exist. Time O(n · k log k) for `k` quantile levels.

Common bugs: using the median (service level ignored), rounding to the nearest integer instead of up, and extrapolating beyond the highest level.
