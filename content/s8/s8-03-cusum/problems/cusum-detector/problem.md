---
slug: cusum-detector
title: CUSUM Change Detector
difficulty: Medium
type: function
tags: [change-point, cusum, streaming]
skills: [anomaly-detection, from-scratch]
packages: []
companies_style: []
---
Implement a **two-sided CUSUM** detector.

You get `values`, the target mean `mu`, the slack `k` and the limit `h`. Keep two counters `s_up` and `s_dn`, both start at 0. For each value `x` at position `t`:

- `s_up = max(0, s_up + x - mu - k)`
- `s_dn = max(0, s_dn + mu - x - k)`
- If `s_up > h`, record `(t, "up")`. Else if `s_dn > h`, record `(t, "down")`. After a record, set **both** counters to 0.

Return the list of records in order.

### Example 1
**Input:** `values = [10, 11, 12, 12, 9, 8, 7]`, `mu = 10`, `k = 0.5`, `h = 3`
**Output:** `[(3, 'up'), (6, 'down')]`
**Explanation:** S+ grows to 3.5 at position 3: alarm up, counters reset. Then 9, 8, 7 give S- of 0.5, 2.0, 4.5: alarm down at position 6.

### Example 2
**Input:** `values = [5, 5, 5]`, `mu = 5`, `k = 0.5`, `h = 1`
**Output:** `[]`
**Explanation:** The values equal the target, so there is no alarm.

### Constraints
- 0 <= len(values) <= 10^5
- k >= 0, h > 0

### Hints
1. Update both counters for every point. Do not use `elif` for the updates, only for the alarm.
2. `max(0, ...)` keeps the counters from going negative.
3. Reset both counters after an alarm.

### Solution explanation
**Approach.** One pass over the data with two counters. After the update, test the limit and reset on alarm.

**Why it works.** Each counter is the largest recent sum of deviations minus the slack. A lasting shift grows it steadily; noise around the target pushes it back to 0.

**Complexity.** O(n) time and O(1) extra memory (O(a) for the list of a alarms). It works online: one point at a time.

**Common bugs.** Forgetting the reset; letting the counters become negative; comparing with `>=` instead of `>`.
