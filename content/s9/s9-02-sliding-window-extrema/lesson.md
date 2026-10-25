---
id: s9-02-sliding-window-extrema
title: Sliding-window max and min (monotonic deque)
minutes: 30
level: beginner
goals: [Explain why brute force is O(n·k), Implement the monotonic deque, Track max and min together]
prereqs: []
tags: [sliding-window, deque, monotonic]
skills: [streaming-algorithms, from-scratch]
---
## Warm-up
```check
{"q": "A loop inside a loop, each running n times, has which time cost?", "type": "single", "options": ["O(n)", "O(n²)", "O(log n)"], "answer": 1, "why": ["That is one loop.", "Correct: n × n steps.", "No."]}
```
```check
{"q": "What is a deque?", "type": "single", "options": ["A list where you can add and remove at both ends in O(1)", "A sorted list", "A dictionary"], "answer": 0, "why": ["Correct. In Python: collections.deque.", "A deque is not sorted.", "A dictionary maps keys to values."]}
```

## Why it matters
A trading screen shows "the highest price of the last 5 minutes", updated every second. A monitoring system alerts when "the maximum latency in the last hour" is too high. The simple way is to scan the whole [[window]] at every step. With a window of k = 3600 values, that is 3600 steps for every new value. We want **O(1) per new value**.

## Brute force and its cost
Take the list `[1, 3, -1, -3, 5, 3, 6, 7]` and window size `k = 3`. The window maxima are `[3, 3, 5, 5, 6, 7]`.

Brute force: for every window, call `max(window)`. That costs **O(n · k)**. With n = 10^6 and k = 10^4 this is 10^10 steps: too slow.

```widget
{"name": "sliding-window", "params": {"window": 3}}
```

```check
{"q": "n = 100,000 values and k = 1,000. What is the brute-force cost?", "type": "single", "options": ["About 10^8 steps", "About 10^5 steps", "About 10^3 steps"], "answer": 0, "why": ["Correct: n · k = 10^8.", "That is n alone.", "That is k alone."]}
```

## The monotonic deque
Keep a [[deque]] of **indices**. The values at these indices are always in **decreasing** order (a "monotonic" deque). The **front** is the index of the current maximum.

For each new index `i`:

1. **Remove from the front** if the index is outside the window (`front <= i − k`).
2. **Remove from the back** while `x[back] <= x[i]`. These values are smaller than the new one and are *older*, so they can never be the maximum again.
3. **Add `i` to the back.**
4. If `i >= k − 1`, the window is full: the answer is `x[front]`.

Trace with `[1, 3, -1, -3, 5]`, k = 3 (deque shows values):

| i | x[i] | deque (values) | answer |
|---|---|---|---|
| 0 | 1 | 1 | – |
| 1 | 3 | 3 (1 removed) | – |
| 2 | −1 | 3, −1 | 3 |
| 3 | −3 | 3, −1, −3 | 3 |
| 4 | 5 | 5 (all smaller removed) | 5 |

Each index is added once and removed once, so the total is **[[O(n)]]**.

```check
{"q": "Why can we remove smaller, older values from the back of the deque?", "type": "single", "options": ["They are older and smaller, so they will never be the maximum of any later window", "They are wrong data", "To save time in sorting"], "answer": 0, "why": ["Correct: a newer larger value outlives them.", "They are valid data.", "There is no sorting."]}
```

## Maximum and minimum together
For the **minimum**, use a second deque with increasing values (or negate the values). Two deques answer range questions. What is the range (max − min) in each window? What is the longest period where the range stays below a limit? For the longest such window, move the left side forward only when `max − min > limit`.

```check
{"q": "To get both the max and the min of every window in O(n), you can...", "type": "single", "options": ["Use two monotonic deques", "Sort each window", "Use a heap and delete from the middle"], "answer": 0, "why": ["Correct.", "Sorting each window is O(n k log k).", "Deleting from the middle of a heap is slow without tricks."]}
```

## Worked example
Sliding window maximum with a deque, checked against brute force.

```python
from collections import deque

def window_max(x, k):
    dq = deque()                          # indices; their values are in decreasing order
    out = []
    for i, v in enumerate(x):
        if dq and dq[0] <= i - k:         # front index left the window
            dq.popleft()
        while dq and x[dq[-1]] <= v:      # smaller or equal older values are useless
            dq.pop()
        dq.append(i)
        if i >= k - 1:                    # window is full
            out.append(x[dq[0]])
    return out

x = [1, 3, -1, -3, 5, 3, 6, 7]
print(window_max(x, 3))
print([max(x[i:i + 3]) for i in range(len(x) - 2)])    # brute force for comparison

# Output:
# [3, 3, 5, 5, 6, 7]
# [3, 3, 5, 5, 6, 7]
```

## Common mistakes
- Storing **values** instead of **indices**: you cannot tell when the front leaves the window.
- Using `<` instead of `<=` for removal. Both work, but be consistent; `<=` keeps the deque smaller.
- Using a list with `pop(0)`: it is O(k). Use `collections.deque`.
- Reporting an answer before the first window is full.
- Forgetting that `k` can be larger than `n`.

## Interview lens
**Typical question:** "Return the maximum of every window of size k."

**Strong answer:** The brute-force solution is O(n·k). I use a [[monotonic deque]] of indices whose values decrease from front to back. For each new value I drop the front if it is outside the window. I drop smaller values from the back. Then I append the new index. The front is the maximum. Each index is pushed and popped at most once, so the time is O(n) and the space is O(k). For the minimum I use a second deque. A [[heap]] with [[lazy deletion]] also works in O(n log n).

**Red flags:** O(n·k) as the final answer; using `list.pop(0)`; storing values only.

## Real world
- Monotonic queues are a standard tool in competitive programming. Stream processors also use them for "max over the last N seconds".
- Sliding-window max and min are the base of rolling Donchian channels in trading charts. These show the highest high and lowest low over N periods.

## Key points
- Brute force costs O(n·k). A monotonic deque costs O(n).
- Keep **indices** in a deque with decreasing values; the front is the answer.
- Pop the front when it leaves the window; pop the back while smaller or equal.
- Use two deques for max and min together.
