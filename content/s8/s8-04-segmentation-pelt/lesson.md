---
id: s8-04-segmentation-pelt
title: Offline change points: binary segmentation and PELT
minutes: 25
level: intermediate
goals: [Compute the cost of a segment, Implement binary segmentation, Explain penalties and the PELT idea]
prereqs: [s8-03-cusum]
tags: [change-point, segmentation, pelt]
skills: [anomaly-detection, from-scratch]
---
## Warm-up
```check
{"q": "CUSUM works while the data arrive one by one. What is this called?", "type": "single", "options": ["Online (streaming) detection", "Offline detection", "Batch training"], "answer": 0, "why": ["Correct: it decides with the data seen so far.", "Offline methods look at the whole series at once.", "Training is a different topic."]}
```
```check
{"q": "What is the sum of squared deviations of the numbers 1, 2, 3 around their mean?", "type": "single", "options": ["2", "6", "0"], "answer": 0, "why": ["Correct: mean = 2, so (−1)² + 0² + 1² = 2.", "6 is the sum of the values.", "0 is the sum of deviations, not of squares."]}
```

## Why it matters
You have a full year of daily sales. You want to know: **when did the level change, and how many times?** You are looking back, not watching live. This is **offline** change-point detection. You can use all the data, so you can find the best split points.

## Cost of a segment
A **[[segment]]** is a part of the series between two change points. We say a segment is "good" when its values are all close to one level. The **cost** measures how bad the fit is:

`cost(a, b) = Σ (x(i) − mean(a..b))²`   for i from a to b−1

- `Σ` = sum
- `mean(a..b)` = the average of the segment

Example: 1, 1, 1, 5, 5, 5. As one segment the mean is 3 and the cost is 6 × 4 = 24. If we cut after the third value, both parts are flat: cost = 0 + 0. The **gain** of the cut is 24 − 0 = 24.

```chart
{"title": "Two levels: where is the best cut?", "x": "t", "height": 220, "series": [{"name": "series", "gen": [["const", {"value": 10}], ["noise", {"sd": 0.8}], ["step", {"at": 50, "size": 4}]], "n": 90, "seed": 8}], "marks": [{"x": 50, "label": "best cut"}], "caption": "Try every cut. The cut at t = 50 gives the smallest total cost of the two parts."}
```

```check
{"q": "Segment values 2, 4, 6. What is the cost (sum of squared deviations from the mean)?", "type": "numeric", "answer": 8, "tol": 0.01, "why": "The mean is 4. The deviations are −2, 0, 2. The squares are 4, 0, 4. Sum = 8."}
```

## Binary segmentation
**[[binary segmentation|Binary segmentation]]** is a greedy method:

1. For the whole series, try every cut position. Take the cut with the largest gain.
2. If the gain is **larger than the [[penalty]]**, keep the cut. Repeat step 1 on the left part and on the right part.
3. If not, stop for this part.

The **penalty** stops the method from cutting forever. Without it, every point would become its own segment (cost 0). A bigger penalty gives fewer change points. A common choice for a mean shift is `penalty ≈ 2 · σ² · ln(n)`, a BIC-style rule. Here σ² is the noise variance.

Also use a **minimum segment size**, so you do not cut off 1 or 2 points.

```check
{"q": "What happens if the penalty is 0?", "type": "single", "options": ["The method cuts into many tiny segments", "The method finds no change point", "The method becomes faster"], "answer": 0, "why": ["Correct: any cut with a positive gain is accepted, so noise creates many cuts.", "Without a penalty, more cuts are accepted, not fewer.", "Speed is not the point; the result is bad."]}
```

## PELT and other ideas
Binary segmentation is fast, but it is greedy. An early wrong cut cannot be undone. The method **[[PELT]]** (Pruned Exact Linear Time, Killick et al. 2012) finds the **best** set of cuts for the objective

`total = Σ cost(segments) + penalty × (number of change points)`

It uses [[dynamic programming]] and prunes options that can never be best. Under some conditions it runs in about O(n) time. In Python the `ruptures` library offers `Binseg`, `Pelt` and other methods. You choose the cost model (mean shift, variance, ...) and the penalty.

| Method | Idea | Speed | Exact? |
|---|---|---|---|
| [[CUSUM]] | counter, online | O(n) | no, tuned |
| Binary segmentation | greedy splits | about O(n log n) | no |
| PELT | dynamic programming with pruning | about O(n) | yes, for its objective |

```check
{"q": "Which method gives the best set of change points for a fixed penalty?", "type": "single", "options": ["Binary segmentation", "PELT", "A rolling z-score"], "answer": 1, "why": ["It is greedy and can miss the best set.", "Correct: PELT solves the penalised problem exactly.", "It does not find change points."]}
```

## Worked example
Find the cut for a series with a clear mean shift, with an explicit cost function.

```python
import numpy as np

x = np.array([1, 1, 1, 1, 5, 5, 5, 5, 5, 5], dtype=float)

def cost(seg):
    return float(((seg - seg.mean()) ** 2).sum())    # sum of squared deviations

total = cost(x)
best = None
for k in range(2, len(x) - 1):                       # at least 2 points on each side
    c = cost(x[:k]) + cost(x[k:])
    if best is None or c < best[1]:
        best = (k, c)

gain = total - best[1]
print("cost of the whole series:", round(total, 2))
print("best cut at:", best[0], "cost after cut:", best[1])
print("gain:", round(gain, 2))
penalty = 5.0
print("accept the cut?", gain > penalty)

# Output:
# cost of the whole series: 38.4
# best cut at: 4 cost after cut: 0.0
# gain: 38.4
# accept the cut? True
```

## Common mistakes
- No penalty (or a penalty that is not scaled to the noise level).
- A minimum segment size of 1: it cuts out single outliers as "segments".
- Using a mean-shift cost when the variance changes (use a cost that fits the change type).
- Reporting the cut index without saying if it ends the old segment or starts the new one.
- Treating binary segmentation as exact.

## Interview lens
**Typical question:** "You have a year of data with several level shifts. How do you find them?"

**Strong answer:** This is offline, so I use a segmentation method. I would pick a cost for the change type, for example squared error for mean shifts. Binary segmentation is simple. It splits where the gain is largest and recurses. It stops when the gain is smaller than a penalty. PELT finds the exact optimum for a penalised cost in about linear time. I scale the penalty with the noise variance and the log of the length, and I check the result visually. I also set a minimum segment size.

**Red flags:** no penalty; confusing online and offline methods; not saying how the number of change points is chosen.

## Real world
- Killick, Fearnhead and Eckley published PELT in 2012 in the Journal of the American Statistical Association.
- The `ruptures` Python library (Truong, Oudre, Vayatis) collects many offline change-point methods and cost functions, including binary segmentation and PELT.

## Key points
- Offline change-point detection splits the series into segments with a simple model (for example one mean each).
- A cut is good when it lowers the total cost by more than the **penalty**.
- Binary segmentation: cut where the gain is best, recurse on both sides. It is greedy.
- PELT: exact for the penalised objective, with pruning for speed.
- Always use a penalty and a minimum segment size.
