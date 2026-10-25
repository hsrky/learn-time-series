---
slug: streaming-median
title: Median of a Data Stream
difficulty: Medium
type: class
tags: [heap, median, class]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
Design a class `StreamMedian`.

- `add(x)`: add the number `x` to the stream.
- `median()`: return the median of **all** numbers added so far as a float. For an even count, return the mean of the two middle numbers. If nothing was added, return `0.0`.

Use two heaps. `add` should take O(log n) and `median` O(1).

### Example 1
**Input:** Add 5, 15, 1, 3 and read the median after each add
**Output:** `[5.0, 10.0, 5.0, 4.0]`
**Explanation:** Sorted lists: [5], [5,15], [1,5,15], [1,3,5,15].

### Constraints
- 0 <= number of operations <= 10^5
- -10^9 <= x <= 10^9

### Hints
1. Use one heap for the small half and one for the large half.
2. For the small half use negative numbers (max-heap).
3. After an add, move the top of one heap to the other if the sizes differ by more than allowed.

### Solution explanation
**Approach.** `low` is a max-heap (negated values) with the smaller half, `high` is a min-heap with the larger half. Push the new value into `low`, then move the top of `low` to `high`, then if `high` is bigger than `low`, move its top back. This keeps every value of `low` <= every value of `high` and the sizes balanced.

**Why it works.** The median is determined by the middle one or two values, which are exactly the heap tops.

**Complexity.** `add`: O(log n). `median`: O(1). Memory: O(n).

**Common bugs.** Forgetting to negate; allowing the sizes to differ by two; integer division for even counts.
