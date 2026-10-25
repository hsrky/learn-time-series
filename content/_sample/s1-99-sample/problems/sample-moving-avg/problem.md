---
slug: sample-moving-avg
title: Streaming Moving Average
difficulty: Hard
type: class
tags: [streaming]
skills: [from-scratch]
---
Implement `MovingAverage(k)` with `next(x)` returning the average of the last `k` values.

### Hints
1. Keep a deque.
2. Keep a running sum.
3. Pop left when too long.

### Solution explanation
Running sum, O(1) per call.
