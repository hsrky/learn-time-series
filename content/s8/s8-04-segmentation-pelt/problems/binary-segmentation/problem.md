---
slug: binary-segmentation
title: Binary Segmentation for Mean Shifts
difficulty: Hard
type: function
tags: [change-point, recursion, numpy]
skills: [anomaly-detection, from-scratch]
packages: []
companies_style: []
---
Implement **binary segmentation** for shifts in the mean.

The cost of a segment is the sum of squared deviations from its mean. For a segment `values[a:b]`, try each cut position `c` with `a + min_size <= c <= b - min_size`. A cut makes the parts `values[a:c]` and `values[c:b]`. The **gain** is `cost(a, b) - cost(a, c) - cost(c, b)`.

- Choose the cut with the largest gain. If two cuts have the same gain, choose the smaller `c`.
- If the best gain is **greater than** `penalty`, keep the cut and repeat on `[a, c)` and `[c, b)`.
- Otherwise do not cut this segment.

Return the sorted list of cut positions (each is the index of the first point of a new segment). If no cut is possible, return an empty list.

### Example 1
**Input:** `values = [1, 1, 1, 1, 5, 5, 5, 5]`, `min_size = 2`, `penalty = 5`
**Output:** `[4]`
**Explanation:** The best cut is at 4 (gain 32). Both halves are flat, so no more cuts.

### Example 2
**Input:** `values = [1, 1, 1, 1, 5, 5, 5, 5, 9, 9, 9, 9]`, `min_size = 2`, `penalty = 5`
**Output:** `[4, 8]`
**Explanation:** The first cut is at 4 or 8, whichever has the larger gain. The other level is found by the recursion on the right part.

### Constraints
- 0 <= len(values) <= 5000
- 1 <= min_size
- penalty >= 0

### Hints
1. Prefix sums of x and x squared give the cost of any segment in O(1): cost = sum(x^2) - sum(x)^2 / length.
2. Write a recursive helper `split(a, b)` that appends cut positions to a list.
3. Ties: scan c from small to large and keep the first best gain (use `>` when updating).

### Solution explanation
**Approach.** Build prefix sums of `x` and `x²`. Then the cost of any segment is available in O(1). A recursive function scans all valid cuts, picks the best gain, and recurses if the gain is above the penalty.

**Why it works.** A good cut separates two levels, which lowers the total squared error a lot. Noise gives only a small gain, which stays under the penalty.

**Complexity.** One scan of a segment of length m costs O(m). On balanced splits the total is O(n log n). In the worst case (always cutting off a tiny piece) it is O(n²). Space is O(n) for the prefix sums and the recursion.

**Common bugs.** Off-by-one in the slice bounds; computing the cost by slicing and `np.var` in a loop (too slow for large inputs); forgetting `min_size`; sorting the result.
