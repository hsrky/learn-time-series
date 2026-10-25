---
id: s8-07-classification-dtw-rocket
title: Time series classification: DTW and ROCKET
minutes: 30
level: intermediate
goals: [Explain DTW and its recurrence, Implement DTW with a window, Describe 1-NN DTW and ROCKET]
prereqs: [s8-01-point-anomalies]
tags: [classification, dtw, rocket]
skills: [ts-classification]
---
## Warm-up
```check
{"q": "Euclidean distance between [1, 2, 3] and [2, 3, 4] (sum of squares, then square root)?", "type": "single", "options": ["1.73", "3", "1"], "answer": 0, "why": ["Correct: three differences of 1, so sqrt(3) = 1.73.", "3 is the sum of the squares, not the root.", "1 is a single difference."]}
```
```check
{"q": "In classification, what is a label?", "type": "single", "options": ["The class we want to predict, such as 'walking' or 'running'", "The time index", "A feature"], "answer": 0, "why": ["Correct.", "The index is the time axis.", "A feature is an input."]}
```

## Why it matters
A phone records 3 seconds of motion. Is the person walking or running? Two walking recordings look the same, but one starts a little later. If you compare point by point, they look far apart. A good method should say: "same shape, small shift". That is **time series [[classification]]**, and its classic tool is **[[DTW]]**.

## Dynamic Time Warping (DTW)
Euclidean distance compares point i of A with point i of B. With **DTW**, point i of A may match a nearby point j of B. It stretches or squeezes time to find the best match.

Example: A = [0, 1, 2, 1, 0], B = [0, 0, 1, 2, 1, 0]. B is A with one extra 0 at the start.
- Euclidean cannot even compare them (different lengths).
- DTW matches the first 0 of A with both starting zeros of B. The distance is 0.

## The DTW table

The method fills a table `D`:

`D[i][j] = |a(i) − b(j)| + min( D[i−1][j], D[i][j−1], D[i−1][j−1] )`

- `D[i][j]` = the best total cost to match the first i points of A with the first j of B
- `|a(i) − b(j)|` = the cost of matching these two points
- The three options are: A advances, B advances, or both advance
- `D[0][0] = 0`, the border is infinity, and the answer is `D[n][m]`

```check
{"q": "A = [1, 3], B = [1, 1, 3]. The best DTW path matches 1-1, 1-1, 3-3 (absolute differences). What is the DTW distance?", "type": "numeric", "answer": 0, "tol": 0.01, "why": "Every matched pair has equal values: 0 + 0 + 0 = 0."}
```

## The window constraint (Sakoe-Chiba band)
Plain DTW costs **O(n · m)** time. It can also match a point at the start with one at the end, which is often wrong. A **window** `w` allows only pairs with `|i − j| <= w`.

- It is **faster**: only about `n · (2w + 1)` cells.
- It is often **more accurate**, because wild warps are blocked.
- If lengths differ by more than w, use `w = max(w, |n − m|)`, or no path exists.

```chart
{"title": "Two walks with a time shift", "x": "t", "height": 220, "series": [{"name": "walk A", "gen": [["season", {"period": 20, "amp": 1}]], "n": 80}, {"name": "walk B (shifted)", "gen": [["season", {"period": 20, "amp": 1, "phase": 3}]], "n": 80, "dash": true}], "caption": "Same shape, shifted in time. Euclidean distance is large, DTW distance is small."}
```

```check
{"q": "What is the main effect of a narrow DTW window?", "type": "single", "options": ["Faster, and it blocks very large time shifts", "Slower but more exact", "It makes the series longer"], "answer": 0, "why": ["Correct.", "It is faster.", "The series is unchanged."]}
```

## 1-NN DTW and ROCKET
**[[1-NN]] DTW** is a strong baseline. For a new series, find the **one nearest** training series by DTW and copy its [[label]]. It needs no training, but each prediction costs `n_train` DTW computations.

**[[ROCKET]]** (Dempster, Petitjean, Webb, 2020) takes another road. It makes thousands of **random convolution kernels**. A kernel is a short list of weights, such as 9 random numbers. You slide it along the series and compute a number at each step. For each kernel, keep two numbers: the **maximum** and the **proportion of positive values (PPV)**. These become features, and a simple linear model (ridge regression classifier) is trained on them. It is very fast. It is as accurate as much slower methods on many benchmark data sets. The newer **MiniRocket** (2021) uses a small fixed set of kernels and only PPV. It is much faster again.

| Method | Training | Prediction cost | Note |
|---|---|---|---|
| 1-NN DTW | none | high (many DTW) | strong, simple baseline |
| ROCKET / MiniRocket | fast linear model | low | very good accuracy for the speed |

```check
{"q": "What features does a ROCKET kernel produce?", "type": "single", "options": ["The maximum and the proportion of positive values (PPV)", "The mean and the median", "The date and the weekday"], "answer": 0, "why": ["Correct.", "Not these.", "These are calendar features."]}
```

## Worked example
We implement DTW and use 1-NN DTW to tell two shapes apart.

```python
import numpy as np

def dtw(a, b, w=None):
    n, m = len(a), len(b)
    w = max(n, m) if w is None else max(w, abs(n - m))       # window must allow some path
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(max(1, i - w), min(m, i + w) + 1):
            cost = abs(a[i - 1] - b[j - 1])
            D[i, j] = cost + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return D[n, m]

t = np.linspace(0, 2 * np.pi, 30)
train = [(np.sin(t), "wave"), (np.sin(t + 0.3), "wave"), (np.sign(np.sin(t)), "square"), (np.sign(np.sin(t + 0.3)), "square")]
query = np.sin(t + 0.6)                                        # a shifted wave

dists = [(dtw(query, s, w=5), label) for s, label in train]
print([round(float(d), 2) for d, _ in dists])
print("1-NN DTW says:", min(dists)[1])

# Output:
# [2.99, 2.08, 13.32, 10.98]
# 1-NN DTW says: wave
```

## Common mistakes
- Not z-normalising the series before DTW (level and scale then dominate the distance).
- Using full DTW on long series (O(n²)). Use a window, or a lower bound such as LB_Keogh.
- Forgetting that a window must be at least `|n − m|`.
- Comparing DTW distances of series with different lengths without scaling.
- Using DTW when the classes differ in speed itself (warping can hide that difference).

## Interview lens
**Typical question:** "How would you classify sensor recordings into activities?"

**Strong answer:** First, a baseline: [[z-normalise]] each recording and use 1-NN with DTW with a small window. It is simple and strong. If I have many series or need speed, I use ROCKET or MiniRocket. Random convolution kernels turn each series into features (max and PPV). A ridge classifier is trained on them. I would also try hand-made features (mean, spread, frequency) with gradient boosting. I validate by splitting by subject or by time, not randomly, to avoid leakage.

**Red flags:** random split of overlapping windows from the same person; no baseline; DTW with no window on long series.

## Real world
- The UCR Time Series Archive is the standard public set of classification tasks. 1-NN DTW was long a baseline on it.
- ROCKET was published by Dempster, Petitjean and Webb (2020); MiniRocket by the same group (2021). Both are in the `sktime` and `aeon` libraries.

## Key points
- DTW compares shapes while allowing small shifts and stretches in time.
- It is a dynamic program on an n × m table: O(n · m) time. A window w cuts it to about O(n · w).
- 1-NN DTW is a strong, training-free baseline. Always z-normalise first.
- ROCKET: random convolution kernels → features (max, PPV) → linear classifier. MiniRocket is faster.
