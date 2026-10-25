---
slug: znorm-subsequence-search
title: Best Match of a Query (z-normalised)
difficulty: Medium
type: function
tags: [similarity-search, numpy, windows]
skills: [ts-classification, from-scratch]
packages: []
companies_style: []
---
You get a long series `series` and a short `query` of length `m`. Find the window of `series` (length `m`) that is most similar to the query **in shape**.

1. Z-normalise the query and every window: subtract the mean and divide by the population standard deviation (`np.std`). If the standard deviation is smaller than `1e-9`, use a vector of zeros instead.
2. The distance is the Euclidean distance between the two z-normalised vectors.
3. Return a tuple `(start, distance)` for the window with the smallest distance. If two windows tie (difference below `1e-9`), return the smaller start.

`distance` is a float. You may assume `m <= len(series)`.

### Example 1
**Input:** `series = [0, 1, 0, 5, 10, 5, 0, 1, 0]`, `query = [1, 2, 1]`
**Output:** `(0, 0.0)`
**Explanation:** The window [0, 1, 0] at position 0 has exactly the same shape as [1, 2, 1] (a small hill), so the distance is 0.

### Example 2
**Input:** `series = [3, 1, 2, 4, 6, 8, 2]`, `query = [10, 20, 30]`
**Output:** `(2, 0.0)`
**Explanation:** The query is a straight line going up. The windows [2, 4, 6] and [4, 6, 8] have the same shape; the first one wins the tie.

### Constraints
- 1 <= m <= len(series) <= 5000

### Hints
1. `np.lib.stride_tricks.sliding_window_view(x, m)` gives all windows as rows.
2. Compute row means and stds with `axis=1`; handle std < 1e-9 with `np.where`.
3. `np.argmin` returns the first minimum, but ties with rounding noise need a small tolerance.

### Solution explanation
**Approach.** Build all windows as a 2-D view, z-normalise each row, and compute the distance to the z-normalised query. Take the smallest.

**Why it works.** Z-normalisation removes level and scale, so only shape differences remain.

**Complexity.** Brute force: O(n · m) time and O(n · m) memory if you materialise the windows (O(n) extra memory if you loop). The MASS algorithm computes all distances with the FFT in O(n log n).

**Common bugs.** Not handling a flat window (division by zero); using the sample std for some parts and the population std for others; comparing the raw query with z-normalised windows; breaking ties towards the last window.
