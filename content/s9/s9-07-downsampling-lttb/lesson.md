---
id: s9-07-downsampling-lttb
title: Downsampling for charts: LTTB
minutes: 25
level: intermediate
goals: [Explain why charts need downsampling, Compute a triangle area for LTTB, Implement LTTB]
prereqs: []
tags: [downsampling, lttb, visualisation]
skills: [streaming-algorithms, from-scratch]
---
## Warm-up
```check
{"q": "A screen chart is 1,000 pixels wide. You have 1,000,000 points. What is the problem?", "type": "single", "options": ["Many points fall on the same pixel column; sending all of them wastes time and memory", "The chart will be too small", "The data are wrong"], "answer": 0, "why": ["Correct: about 1,000 points per pixel column.", "The size of the chart is fine.", "The data may be fine."]}
```
```check
{"q": "The area of a triangle with base b and height h is...", "type": "single", "options": ["b · h / 2", "b · h", "b + h"], "answer": 0, "why": ["Correct.", "That is a rectangle.", "That is not an area."]}
```

## Why it matters
A monitoring page draws a metric with 5 million points. The browser freezes. You cannot show 5 million points on a 1,200-pixel screen anyway. You need to **downsample**: choose about 1,000 to 2,000 points that still **look like** the full chart. The spikes and turning points must stay. A bad method hides the very event the user wants to see.

## Simple methods and their problems
- **Every n-th point**: fast, but it can **skip a spike** completely.
- **Average per [[bucket]]**: smooth, but spikes are flattened.
- **Min and max per bucket**: keeps spikes, uses 2 points per bucket, and can look "busy".

The **[[LTTB]]** algorithm (Largest-Triangle-Three-Buckets, Sveinn Steinarsson, 2013) picks **one point per bucket** so that the line stays close to the original in **shape**.

```chart
{"title": "Every 10th point can miss a spike", "x": "t", "height": 220, "series": [{"name": "full data", "gen": [["season", {"period": 50, "amp": 2}], ["noise", {"sd": 0.2}], ["spike", {"at": 123, "size": 6}]], "n": 300, "seed": 13}], "marks": [{"x": 123, "label": "a spike that every-10th sampling would miss"}], "caption": "Index 123 is not a multiple of 10. Sampling every 10th point skips it. LTTB keeps it."}
```

```check
{"q": "Why can taking every n-th point be dangerous for anomaly charts?", "type": "single", "options": ["It may skip the one spike you want to show", "It is slow", "It changes the time zone"], "answer": 0, "why": ["Correct.", "It is the fastest method.", "Time zones are unrelated."]}
```

## How LTTB works
Input: n points (x, y) and a target number `threshold`.

1. **Always keep** the first and the last point.
2. Split the points between them into `threshold − 2` **buckets** of about equal size.
3. Go through the buckets from left to right. For each bucket choose the point that makes the **largest triangle** with two other points:
   - point A = the point chosen in the **previous** bucket,
   - point C = the **average point** of the **next** bucket (for the last bucket, use the last point),
   - point B = each candidate in the current bucket.
4. Keep the candidate with the largest triangle area.

The area of the triangle A, B, C (A = (ax, ay), B = (bx, by), C = (cx, cy)):

`area = |(ax − cx)·(by − ay) − (ax − bx)·(cy − ay)| / 2`

A big triangle means B sticks out from the straight line between A and C. So LTTB keeps **peaks, valleys and turning points**.

Cost: one pass, **[[O(n)]]** time, **O(threshold)** extra memory.

```check
{"q": "In LTTB, which point is the 'third' point of the triangle for a middle bucket?", "type": "single", "options": ["The average of the next bucket", "The average of the previous bucket", "The last point of the series"], "answer": 0, "why": ["Correct: this is a look-ahead.", "The previous point A is the chosen point, not an average.", "The last point is used only for the last bucket."]}
```

## Worked example
We downsample a sine wave with a spike from 300 to 30 points and test whether the spike survives.

```python
import numpy as np

def lttb(x, y, threshold):
    n = len(x)
    if threshold >= n or threshold < 3:
        return list(range(n)) if threshold >= n else [0, n - 1]
    every = (n - 2) / (threshold - 2)                 # bucket size
    chosen = [0]                                      # always keep the first point
    a = 0
    for i in range(threshold - 2):
        # average point of the NEXT bucket
        s = int((i + 1) * every) + 1
        e = min(int((i + 2) * every) + 1, n)
        cx, cy = np.mean(x[s:e]), np.mean(y[s:e])
        # candidates in the CURRENT bucket
        lo, hi = int(i * every) + 1, int((i + 1) * every) + 1
        best, best_area = lo, -1.0
        for j in range(lo, hi):
            area = abs((x[a] - cx) * (y[j] - y[a]) - (x[a] - x[j]) * (cy - y[a])) / 2
            if area > best_area:
                best, best_area = j, area
        chosen.append(best)
        a = best
    chosen.append(n - 1)                              # always keep the last point
    return chosen

rng = np.random.default_rng(13)
x = np.arange(300)
y = 2 * np.sin(2 * np.pi * x / 50) + rng.normal(0, 0.2, 300)
y[123] += 6                                           # one spike

idx = lttb(x, y, 30)
print("points kept:", len(idx), "first/last:", idx[0], idx[-1])
print("spike (123) kept by LTTB:", 123 in idx)
print("spike kept by every 10th point:", 123 in range(0, 300, 10))

# Output:
# points kept: 30 first/last: 0 299
# spike (123) kept by LTTB: True
# spike kept by every 10th point: False
```

## Common mistakes
- Forgetting to keep the first and last points.
- Using the average of the **current** bucket instead of the next one.
- Bucket boundaries that overlap or leave gaps (use one formula for start and end).
- Applying LTTB to unsorted x values.
- Using LTTB for calculations. It is for **display**, not for statistics: the sampled data cannot be used to compute the true mean or max.

## Interview lens
**Typical question:** "You need to show a time series with 10 million points in a web chart. What do you do?"

**Strong answer:** I downsample on the server to about two points per pixel column. Taking every n-th point can hide spikes, and averaging flattens them. I would use LTTB: split the series into buckets, keep the first and last point, and in each bucket choose the point with the largest triangle area using the previously chosen point and the average of the next bucket. It is O(n) and keeps the visual shape. If extremes matter, I use min/max per bucket. I keep the raw data for zooming and re-query at higher resolution on zoom.

**Red flags:** sending all points; random sampling; not saying that the downsampled data is for display only.

## Real world
- LTTB comes from the 2013 master's thesis of Sveinn Steinarsson (University of Iceland).
- Charting and monitoring tools offer LTTB-style [[downsampling]], for example in time-series databases and dashboard plugins.

## Key points
- Charts need about 1 to 2 points per pixel column; more is wasted.
- Every n-th point can miss spikes; averages flatten them.
- LTTB: keep first and last; one point per bucket with the largest triangle (previous chosen point, next bucket average).
- O(n) time, O(threshold) memory. Use it for display only.
