---
id: s8-08-similarity-matrix-profile
title: Similarity search, matrix profile and clustering
minutes: 30
level: intermediate
goals: [Search for a shape with z-normalised distance, Explain the matrix profile (motifs and discords), Cluster series sensibly]
prereqs: [s8-07-classification-dtw-rocket]
tags: [similarity, matrix-profile, clustering]
skills: [ts-classification, anomaly-detection]
---
## Warm-up
```check
{"q": "What does it mean to z-normalise a window?", "type": "single", "options": ["Subtract its mean and divide by its standard deviation", "Sort its values", "Multiply it by 100"], "answer": 0, "why": ["Correct: the result has mean 0 and standard deviation 1.", "Sorting destroys the time order.", "That does not normalise anything."]}
```
```check
{"q": "DTW is used to compare...", "type": "single", "options": ["The shape of two series, with small time shifts allowed", "Two dates", "Two tables of text"], "answer": 0, "why": ["Correct.", "Not dates.", "Not text tables."]}
```

## Why it matters
You have one hour of heartbeat data and you see a strange beat. **Have we seen something like this before?** Or the reverse: you have a year of sensor data with no labels, and you want to know **which pattern repeats** and **which part is unique**. These are questions of **similarity search**. The tool that answers all of them with one table is the **[[matrix profile]]**.

## Similarity search: find a pattern inside a long series
Task: you have a short **query** (m points) and a long series (n points). Find where the query fits best.

1. Cut the long series into all windows of length m ("subsequences"). There are n − m + 1 of them.
2. **[[z-normalise|Z-normalise]]** the query and each window. This removes level and scale, so only the **shape** counts.
3. Compute the distance (Euclidean) between the query and each window.
4. The smallest distance is the best match.

The z-normalised distance between windows `a` and `b` of length m:

`d(a, b) = sqrt( Σ ( za(i) − zb(i) )² )`   where `z(i) = (x(i) − mean) / std`

A brute-force search costs O(n · m). The algorithm **MASS** (Mueen) uses the fast Fourier transform and gets O(n log n).

```chart
{"title": "A query shape hidden in a long series", "x": "t", "height": 220, "series": [{"name": "long series", "gen": [["season", {"period": 40, "amp": 1}], ["noise", {"sd": 0.15}], ["spike", {"at": 90, "size": 2.5}]], "n": 160, "seed": 6}], "marks": [{"x": 90, "label": "best match for the query 'spike'"}], "caption": "The query is a narrow spike. After z-normalisation, the best window is the one that contains the spike, whatever its height."}
```

```check
{"q": "Why z-normalise before comparing windows?", "type": "single", "options": ["So that only the shape counts, not the level or the scale", "To make the series shorter", "To remove all noise"], "answer": 0, "why": ["Correct.", "The length does not change.", "Noise is still there."]}
```

## Matrix profile: nearest neighbour for every window
The **matrix profile** (Yeh et al., 2016) answers: for **every** window, how far is its nearest other window? It stores one number per window.

- **Low value** → this pattern repeats somewhere. This is a **[[motif]]**.
- **High value** → this window is unlike all others. This is a **[[discord]]**, a natural [[anomaly]] detector!

To avoid the trivial answer (a window is very similar to the window shifted by one step), ignore neighbours closer than an **exclusion zone**, often m/2 positions.

The Python library **stumpy** computes it fast: `stumpy.stump(T, m)` returns the profile (and the index of each nearest neighbour). It needs no training and has a single parameter, the window length m.

```check
{"q": "In a matrix profile, which windows are anomaly candidates?", "type": "single", "options": ["Those with the highest values (discords)", "Those with the lowest values (motifs)", "Those with value exactly 1"], "answer": 0, "why": ["Correct: no other window is similar to them.", "Low values are repeated patterns.", "There is no special value of 1."]}
```

## Clustering series
**[[clustering|Clustering]]** groups series without labels. Common recipe: z-normalise each series, then use **[[k-means]]** (Euclidean) to find k groups. If shapes are shifted in time, use a DTW-based distance and cluster centres that respect [[DTW]] (DTW barycenter averaging, available in `tslearn`). Choose k with the silhouette score or with domain sense. Typical uses: group stores by sales shape, group users by daily activity.

| Task | Method |
|---|---|
| Find a known shape in a long series | z-normalised distance profile (MASS) |
| Find repeated patterns and odd ones | matrix profile (stumpy) |
| Group many series | z-normalise, then k-means (or DTW k-means) |

```check
{"q": "You want to group 10,000 daily-activity curves where people peak at slightly different times. What is a good choice?", "type": "single", "options": ["z-normalise, then DTW-based k-means or k-means on smoothed curves", "Plain k-means on raw values with different scales", "Sort the curves by their first value"], "answer": 0, "why": ["Correct: shape matters, with small shifts allowed.", "Scale differences dominate the groups.", "That is not clustering."]}
```

## Worked example
A tiny matrix profile in numpy. We look for the **discord** in a sine wave with one broken period.

```python
import numpy as np

rng = np.random.default_rng(0)
t = np.arange(240)
x = np.sin(2 * np.pi * t / 30) + rng.normal(0, 0.05, 240)
x[150:165] = rng.normal(0, 0.5, 15)                # a broken half period

m = 30
def znorm(a):
    s = a.std()
    return (a - a.mean()) / s if s > 1e-9 else np.zeros_like(a)

Z = np.array([znorm(x[i:i + m]) for i in range(len(x) - m + 1)])   # all windows, z-normalised
n = len(Z)
profile = np.empty(n)
for i in range(n):
    d = np.sqrt(((Z - Z[i]) ** 2).sum(axis=1))      # distance to every window
    lo, hi = max(0, i - m // 2), min(n, i + m // 2 + 1)
    d[lo:hi] = np.inf                                # exclusion zone: ignore trivial neighbours
    profile[i] = d.min()

print("discord (highest profile) starts at:", int(profile.argmax()))
print("profile there:", round(float(profile.max()), 2), "typical:", round(float(np.median(profile)), 2))

# Output:
# discord (highest profile) starts at: 148
# profile there: 4.02 typical: 0.47
```

## Common mistakes
- Forgetting the exclusion zone: every window matches its own neighbours and the profile is near 0 everywhere.
- Choosing a window length m that does not match the pattern (try several values).
- Not z-normalising when only the shape matters, or z-normalising flat windows (division by zero).
- Using the matrix profile over the full series including the future in a live system.
- Choosing k in k-means without checking the result visually.

## Interview lens
**Typical question:** "How would you find repeated patterns and unusual patterns in a long sensor series, without labels?"

**Strong answer:** I would use the matrix profile. For a window length m, it gives the distance of every window to its nearest neighbour outside an exclusion zone. Low values show repeated patterns (motifs), high values show discords, which are anomaly candidates. Z-normalisation makes it shape-based. It has one parameter, m, and the `stumpy` library computes it quickly. For a query search I would use a z-normalised distance profile (MASS). For grouping many series I would z-normalise and cluster with k-means or DTW-based k-means.

**Red flags:** no normalisation; no exclusion zone; O(n²) memory for the full distance matrix on long series.

## Real world
- The matrix profile was introduced in 2016 by Yeh, Zhu and colleagues, including Eamonn Keogh, at the University of California, Riverside.
- `stumpy` is an open-source Python library for the matrix profile; `tslearn` offers DTW-based k-means for series.

## Key points
- Similarity search finds the best match of a short query in a long series; z-normalise to compare shape only.
- The matrix profile stores the nearest-neighbour distance for each window: low = motif, high = discord (anomaly).
- Use an exclusion zone to skip trivial neighbours.
- Cluster series after z-normalisation; use DTW when time shifts matter.
