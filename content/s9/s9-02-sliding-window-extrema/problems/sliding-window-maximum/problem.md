---
slug: sliding-window-maximum
title: Sliding Window Maximum
difficulty: Medium
type: function
tags: [sliding-window, deque, monotonic]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: [latency monitoring]
---
You get a list of numbers `nums` (for example latency every second) and a window size `k`. Return a list with the **maximum of every window** of `k` consecutive numbers, from left to right. The result has `len(nums) - k + 1` values.

If `k > len(nums)` or the list is empty, return an empty list. The input is large, so use an **O(n)** method.

### Example 1
**Input:** `nums = [1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3`
**Output:** `[3, 3, 5, 5, 6, 7]`
**Explanation:** Windows: [1,3,-1] → 3, [3,-1,-3] → 3, [-1,-3,5] → 5, [-3,5,3] → 5, [5,3,6] → 6, [3,6,7] → 7.

### Example 2
**Input:** `nums = [9, 8, 7]`, `k = 1`
**Output:** `[9, 8, 7]`
**Explanation:** With k = 1 every number is its own maximum.

### Constraints
- 0 <= len(nums) <= 10^6
- 1 <= k
- Values are integers or floats

### Hints
1. Brute force `max(nums[i:i+k])` works but is O(n·k).
2. Keep a `collections.deque` of indices. Their values should decrease from front to back.
3. Pop the front if it is `<= i - k`. Pop the back while its value is `<=` the new value.

### Solution explanation
**Approach.** A deque of indices with decreasing values. For each index `i`: drop the front if it left the window, drop smaller values from the back, append `i`. Once `i >= k-1`, the front holds the maximum.

**Why it works.** An older value that is smaller than a newer one can never be a window maximum again, because the newer one stays in every window the older one is in (and more). So we can forget it.

**Complexity.** O(n) time, because each index is pushed once and popped at most once. O(k) extra space for the deque.

**Common bugs.** Using `list.pop(0)` (O(k)); storing values instead of indices; outputting before the window is full.
