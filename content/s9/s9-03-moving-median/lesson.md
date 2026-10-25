---
id: s9-03-moving-median
title: Moving median with two heaps
minutes: 30
level: intermediate
goals: [Build a running median with two heaps, Add lazy deletion for a moving window, Compare mean and median smoothing]
prereqs: [s9-02-sliding-window-extrema]
tags: [heap, median, streaming]
skills: [streaming-algorithms, from-scratch]
---
## Warm-up
```check
{"q": "What is the median of 3, 9, 5, 1?", "type": "single", "options": ["4", "5", "4.5"], "answer": 0, "why": ["Correct: sorted 1, 3, 5, 9; the two middle values 3 and 5 give 4.", "5 is one of the middle values only.", "4.5 is the mean of 1, 9."]}
```
```check
{"q": "A min-heap gives you quick access to...", "type": "single", "options": ["The smallest item, in O(1)", "The median", "The newest item"], "answer": 0, "why": ["Correct. Push and pop cost O(log n).", "A heap alone does not give the median.", "A heap does not track the time."]}
```

## Why it matters
Averages are fragile: one broken sensor value of 10,000 ruins a moving average. The **moving median** ignores such spikes, so it is a standard way to clean a signal. The question is how to compute it fast. Sorting each [[window]] costs O(k log k) per step. In an interview, you are asked to do better.

## Two heaps: a running median
Split the numbers seen so far into two halves:

- **Low half**: the smaller numbers, in a **max-heap** (the biggest of the low half is on top).
- **High half**: the larger numbers, in a **min-heap** (the smallest of the high half is on top).

Keep the sizes equal, or the low half bigger by one. Then:

- Odd count → the median is the top of the low half.
- Even count → the median is the mean of the two tops.

Example: add 5, 15, 1, 3.

| add | low (max-heap) | high (min-heap) | median |
|---|---|---|---|
| 5 | {5} | {} | 5 |
| 15 | {5} | {15} | 10 |
| 1 | {5, 1} | {15} | 5 |
| 3 | {3, 1} | {5, 15} | 4 |

Adding costs **O(log n)**. Reading the median costs **O(1)**. Python's `heapq` is a min-heap, so for a max-heap push the **negative** of the number.

```check
{"q": "Low half {{2, 4}}, high half {{7, 9}}. What is the median?", "type": "numeric", "answer": 5.5, "tol": 0.01, "why": "Even count: the two tops are 4 and 7. The mean is 5.5."}
```

## Moving median: the window must forget
For a window of size k, an old value must leave. A [[heap]] cannot remove a value from the middle quickly. The trick is **[[lazy deletion]]**:

1. Keep a counter (dictionary) of values that should be deleted: `late[value] += 1`.
2. Track the **valid sizes** of both halves (not the raw heap lengths).
3. Only when a "late" value reaches the **top** of a heap, pop it for real.
4. After each step, rebalance so that `size(low) = size(high)` or `size(low) = size(high) + 1`.

Each value is pushed once and popped once: **O(log k) amortised** per step, compared with O(k log k) for sorting each window.

```chart
{"title": "Moving mean against moving median with spikes", "x": "t", "height": 230, "series": [{"name": "signal with spikes", "gen": [["const", {"value": 20}], ["noise", {"sd": 1}], ["spike", {"at": 40, "size": 60}], ["spike", {"at": 70, "size": -40}]], "n": 100, "seed": 11}, {"name": "clean level", "gen": [["const", {"value": 20}]], "n": 100, "dash": true}], "marks": [{"x": 40, "label": "spike"}, {"x": 70, "label": "dip"}], "caption": "A moving median of size 5 ignores a single spike. A moving mean of size 5 is pulled up by 12 units."}
```

```check
{"q": "Why is lazy deletion used for the moving median?", "type": "single", "options": ["A heap cannot remove an item from the middle fast", "To save memory only", "Because medians are lazy"], "answer": 0, "why": ["Correct: we delete only when the item reaches the top.", "Memory is not the main reason.", "No."]}
```

## Alternatives
| Method | Per step | Note |
|---|---|---|
| Sort the window | O(k log k) | simple, slow |
| Two heaps with lazy deletion | O(log k) | the interview answer |
| Sorted list + `bisect` | O(k) (insert and delete shift items) | fast in practice for small k |
| pandas `rolling(k).median()` | about O(log k) | use this in real code |

## Worked example
A moving median with `bisect` (simple), checked against pandas.

```python
import bisect
import pandas as pd
from collections import deque

def moving_median(x, k):
    win = deque()          # values in time order
    srt = []               # the same values, sorted
    out = []
    for v in x:
        win.append(v)
        bisect.insort(srt, v)                       # insert, keep sorted
        if len(win) > k:
            old = win.popleft()
            del srt[bisect.bisect_left(srt, old)]   # remove the oldest value
        n = len(srt)
        out.append(srt[n // 2] if n % 2 else (srt[n // 2 - 1] + srt[n // 2]) / 2)
    return out

x = [5, 15, 1, 3, 100, 2, 4]
mine = moving_median(x, 3)
ref = pd.Series(x).rolling(3, min_periods=1).median().tolist()
print(mine)
print(ref)
print("same:", mine == ref)

# Output:
# [5, 10.0, 5, 3, 3, 3, 4]
# [5.0, 10.0, 5.0, 3.0, 3.0, 3.0, 4.0]
# same: True
```

## Common mistakes
- Using the raw heap length instead of the valid sizes when lazy deletion is used.
- Forgetting to **negate** values for the max-heap.
- Returning an integer division result for an even count (`(a + b) // 2` instead of `/ 2`).
- Not rebalancing after both an insert and a removal.
- Pruning only one heap after a removal.

## Interview lens
**Typical question:** "Find the median of a stream" and then "now only the last k values".

**Strong answer:** For the stream I keep two heaps: a max-heap for the lower half and a min-heap for the upper half, with sizes that differ by at most one. Insert is O(log n) and the median is O(1). For the window I add lazy deletion: I count outgoing values in a dictionary, keep logical sizes, and pop an outgoing value only when it reaches a heap top. Each step is O(log k) amortised and the space is O(k). A sorted list with bisect is a simple alternative with O(k) memmove per step.

**Red flags:** sorting the whole window each time; mixing up which heap is the max-heap; forgetting that Python has only a min-heap.

## Real world
- Median filters are a standard tool in signal and image processing to remove spikes ("salt and pepper" noise) while keeping edges.
- Monitoring systems often report medians (and other percentiles) of latency instead of means, because a few slow requests distort the mean.

## Key points
- Median of a stream: low half in a max-heap, high half in a min-heap, sizes balanced. Add O(log n), read O(1).
- Python `heapq` is a min-heap: negate for the max-heap.
- Moving median needs lazy deletion plus valid-size counters: O(log k) amortised.
- A moving median resists spikes where a moving mean does not.
