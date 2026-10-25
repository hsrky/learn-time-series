---
slug: moving-median
title: Moving Median
difficulty: Hard
type: class
tags: [heap, median, sliding-window, class]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
Design a class `MovingMedian(k)`.

- `next(x)`: add the number `x` and return the median of the **last `k` numbers** (or of all numbers so far if fewer than `k` were added). For an even count return the mean of the two middle numbers, as a float.

Aim for O(log k) amortised time per call. A solution that sorts the whole window each time is too slow for the large tests.

### Example 1
**Input:** `m = MovingMedian(3)`; next for `1, 3, -1, -3, 5, 3`
**Output:** `[1.0, 2.0, 1.0, -1.0, -1.0, 3.0]`
**Explanation:** Windows: [1], [1,3], [1,3,-1], [3,-1,-3], [-1,-3,5], [-3,5,3].

### Constraints
- 1 <= k <= 10^5
- 0 <= number of calls <= 10^5
- x is an integer or float

### Hints
1. Keep a `deque` of the window values so you know which value leaves.
2. Use two heaps like in the stream median, plus a dictionary `late` that counts values waiting for deletion.
3. Track the valid sizes of both heaps yourself. Prune a heap top while it is in `late`.

### Solution explanation
**Approach.** Two heaps (`lo` max-heap, `hi` min-heap) with valid-size counters. When the window is full, the oldest value is marked in `late` and the counter of its heap decreases. Then rebalance and prune: pop heap tops that are marked as late. The median is read from the tops.

**Why it works.** Lazy deletion lets us remove from the middle of a heap without searching: the stale item stays in the heap until it reaches the top, and the size counters ignore it.

**Complexity.** O(log k) amortised per call, because each value is pushed once and popped once. Space O(k) (stale items are removed over time).

**Common bugs.** Using `len(heap)` instead of the valid size; not pruning after the rebalance move; deleting a value from the wrong heap (use `out <= max of low` to decide which half it was in).
