---
slug: rolling-zscore-anomalies
title: Rolling Z-Score Anomalies
difficulty: Easy
type: function
tags: [anomaly, rolling, numpy]
skills: [anomaly-detection, leakage-free]
packages: []
companies_style: [payments monitoring]
---
You get a list of numbers `values`, a window size `window` and a `threshold`.

For each position `i` with `i >= window`, look at the `window` values just **before** it: `values[i-window:i]`. The current value is **not** in the window. Compute the mean and the population standard deviation (divide by `window`) of that window. The point is an anomaly when `abs(values[i] - mean) / std > threshold`.

If `std` is 0 (the window is flat), the point is an anomaly when it is different from the mean. Treat `std < 1e-9` as 0.

Return the list of anomaly positions in increasing order. The first `window` points are never flagged.

### Example 1
**Input:** `values = [1, 1, 1, 1, 1, 9, 1, 1]`, `window = 5`, `threshold = 3`
**Output:** `[5]`
**Explanation:** The window before position 5 is all ones, so std = 0 and 9 is different from the mean. Position 6 sees a window with the 9, std is large, and 1 is not far enough.

### Example 2
**Input:** `values = [10, 11, 9, 10, 12, 10, 30, 11]`, `window = 4`, `threshold = 3`
**Output:** `[6]`
**Explanation:** Position 6 (value 30) is far above the mean of 9, 10, 12, 10 (mean 10.25, std about 1.09). Position 7 sees 30 in its window, so 11 is normal.

### Constraints
- 1 <= len(values) <= 10^5
- 1 <= window
- values are numbers; threshold > 0

### Hints
1. Loop `i` from `window` to the end and slice `values[i-window:i]`.
2. `np.mean` and `np.std` (default ddof=0) give the population statistics.
3. Check the flat-window case first: if std < 1e-9, flag when `values[i] != mean`.

### Solution explanation
**Approach.** For each position `i >= window`, slice the previous `window` values, compute the mean and std, and compare. The slice stops at `i-1`, so there is no leakage.

**Why it works.** The score of a point uses only older data, so the method also works online, one point at a time.

**Complexity.** This simple version costs O(n · window) time and O(window) extra space. You can reach O(n) time by keeping a running sum and a running sum of squares (add the new value, remove the oldest), but this needs care with float rounding.

**Common bugs.** Including `values[i]` in the window; dividing by zero when the window is flat; using the sample std (ddof=1) by mistake.
