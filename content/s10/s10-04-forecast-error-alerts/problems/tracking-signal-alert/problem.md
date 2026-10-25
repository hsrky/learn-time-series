---
slug: tracking-signal-alert
title: Tracking Signal Alarm
difficulty: Medium
type: function
tags: [monitoring, bias, numpy, tracking-signal]
skills: [monitoring, forecast-metrics]
packages: []
companies_style: [supply chain, retail demand]
---
Planners want an alarm when a forecast becomes biased. Implement two functions.

**1. `tracking_signal(actual, forecast)`** returns an array `ts` of the same length. For each position `t` (counting from 1):

- `e(i) = actual(i) - forecast(i)`
- `RSFE(t) = e(1) + … + e(t)`
- `MAD(t) = mean(|e(1)|, …, |e(t)|)`
- `ts(t) = RSFE(t) / MAD(t)`, and `ts(t) = 0` when `MAD(t) = 0`.

**2. `first_alarm(actual, forecast, limit=4.0, min_periods=6)`** returns the **0-based index** of the first position where `|ts| > limit` and the position count `t >= min_periods`. Return `-1` if there is none.

### Example 1
**Input:** `actual = [10, 10, 10, 10]`, `forecast = [8, 8, 8, 8]`
**Output of `tracking_signal`:** `[1, 2, 3, 4]`
**Explanation:** Every error is 2. RSFE is 2, 4, 6, 8 and MAD is always 2.

### Example 2
**Input:** `first_alarm` on the same data with `limit=3, min_periods=2`
**Output:** `3`
**Explanation:** TS is 1, 2, 3, 4. Only the value 4 is above 3, at index 3.

### Constraints
- 1 ≤ length ≤ 100 000. Both inputs have the same length.
- Values are finite floats.

### Hints
1. `np.cumsum(err)` gives the running sum.
2. The running MAD is `np.cumsum(np.abs(err)) / np.arange(1, n + 1)`.
3. Use `np.divide(..., out=np.zeros(n), where=mad > 0)` to avoid dividing by zero. For the alarm use `np.flatnonzero` on a boolean mask.

### Solution explanation
Everything is vectorised with cumulative sums, so the time is O(n) and no loop is needed. Division by zero happens when all errors so far are 0, and the problem defines TS as 0 there. The `min_periods` mask removes the noisy start. Common bugs: using the absolute error in the numerator (then bias is lost), using a fixed total MAD instead of a running one, and returning a 1-based index.
