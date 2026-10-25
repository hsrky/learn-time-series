---
slug: lttb-downsample
title: Downsample with LTTB
difficulty: Hard
type: function
tags: [downsampling, lttb, geometry]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
Implement **LTTB** (Largest-Triangle-Three-Buckets). You get lists `x` and `y` (same length `n`, `x` increasing) and `threshold`, the number of points to keep. Return the sorted list of **indices** of the kept points.

- If `threshold >= n`, return all indices `[0, ..., n-1]`. If `threshold == 2`, return `[0, n-1]`.
- Otherwise: `every = (n - 2) / (threshold - 2)`. Keep index 0 first. Let `a = 0` (the last chosen index).
- For `i = 0 .. threshold-3` (the buckets):
  - The **next bucket** is `s = int((i + 1) * every) + 1` to `e = min(int((i + 2) * every) + 1, n)` (end excluded). `cx`, `cy` are the means of `x[s:e]` and `y[s:e]`.
  - The **current bucket** is `lo = int(i * every) + 1` to `hi = int((i + 1) * every) + 1` (end excluded).
  - For each `j` in the current bucket: `area = abs((x[a] - cx) * (y[j] - y[a]) - (x[a] - x[j]) * (cy - y[a])) / 2`. Choose the `j` with the largest area; on a tie choose the smaller `j`. Append it and set `a = j`.
- Append index `n - 1` at the end.

### Example 1
**Input:** `x = 0..9`, `y = [0, 1, 0, 1, 0, 9, 0, 1, 0, 1]`, `threshold = 5`
**Output:** `[0, 2, 5, 6, 9]`
**Explanation:** Five points are kept: the first, the last, and one per bucket. The spike at index 5 is kept.

### Constraints
- 2 <= threshold
- 1 <= n <= 10^5
- x strictly increasing

### Hints
1. Compute `every` once, then loop over the buckets with the integer formulas of the statement.
2. For the next bucket use `sum(...) / (e - s)` or `np.mean`.
3. The first candidate with the maximum area wins: update only when `area > best_area`.

### Solution explanation
**Approach.** Follow the definition: for each bucket compute the average point of the next bucket, then scan the current bucket and keep the point with the largest triangle area relative to the previously chosen point.

**Why it works.** The triangle area measures how far a candidate is from the line between its neighbours (the previous chosen point and the future average), so peaks and valleys score high.

**Complexity.** Each point is a candidate once, and each point is in one "next bucket" average, so the total is O(n) time. Extra memory is O(threshold) for the output.

**Common bugs.** Using the current bucket's average; forgetting that the last bucket's next bucket ends at `n`; off-by-one in `int()` bucket edges; not returning the last index.
