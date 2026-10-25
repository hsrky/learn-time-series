---
id: s8-05-isolation-forest-reconstruction
title: Isolation Forest and reconstruction error
minutes: 25
level: intermediate
goals: [Explain how an Isolation Forest scores a point, Build window features, Explain reconstruction error (autoencoder, PCA)]
prereqs: [s8-01-point-anomalies]
tags: [anomaly, isolation-forest, autoencoder]
skills: [anomaly-detection, feature-engineering]
---
## Warm-up
```check
{"q": "Why do we cut a series into windows before we use a model like Isolation Forest?", "type": "single", "options": ["The model needs a table: one row of features per window", "Windows make the series longer", "The model only reads dates"], "answer": 0, "why": ["Correct: a window gives a small table row, for example mean, spread and range.", "Windows do not make the series longer.", "Models read numbers, not dates."]}
```
```check
{"q": "A window feature is computed from the window [5, 7, 9]. What is its range (max − min)?", "type": "single", "options": ["2", "4", "9"], "answer": 1, "why": ["2 is the step size.", "Correct: 9 − 5 = 4.", "9 is the maximum."]}
```

## Why it matters
A pump has a sensor that sends 100 values per second. Failures show in many ways: a spike, a flat line, a new vibration shape. A z-score only knows one shape. **Machine learning methods** look at the shape of a whole window and flag windows that look different from most. You do not need labels of past failures (this is **unsupervised** learning).

## Isolation Forest: anomalies are easy to isolate
Idea: imagine you pick a random feature and a random split value, again and again. A point far away from the others ends **alone** after only a few splits. A point inside the crowd needs many splits.

Example with 8 points: seven near 10 and one at 90. A random split between 10 and 90 isolates the 90 in one step. To isolate one of the seven, you need about 4 or more cuts.

The score:

`score(x) = 2 ^ ( − E[h(x)] / c(n) )`

- `h(x)` = the number of splits needed to isolate x in one random tree
- `E[h(x)]` = the average of `h(x)` over many trees (a "forest")
- `c(n)` = the typical path length for n points (a normaliser)
- A score near **1** means anomaly. A score near **0.5** or below means normal.

```chart
{"title": "Few splits for the outlier, many for the crowd", "x": "split step", "height": 200, "series": [{"name": "outlier", "y": [8, 1, 0, 0, 0, 0], "kind": "bar"}, {"name": "normal point", "y": [8, 6, 5, 3, 2, 1], "kind": "bar"}], "caption": "Number of points that are still together with the point after each random split (illustration)."}
```

```check
{"q": "In an Isolation Forest, which point gets a score close to 1?", "type": "single", "options": ["The one that needs few splits to be isolated", "The one in the densest area", "The one with the biggest index"], "answer": 0, "why": ["Correct: a short path means it is easy to isolate, so it is likely an anomaly.", "Dense areas need many splits.", "The index is not used."]}
```

## Window features and the leakage rule
For time series, we turn each window into features such as: mean, standard deviation, min, max, range, slope, the lag-1 autocorrelation. Then we fit the forest and score the windows.

- Use **past** data to fit the forest when you want a live detector. Then score new windows.
- Do not use the global statistics of the full series to normalise if you will later use the model live.
- The `contamination` setting (expected share of anomalies) only sets the cut-off. You can also rank windows by score and take the top k.

## Reconstruction error: the autoencoder idea
Another family: learn to **compress and rebuild** normal windows. An **autoencoder** is a small neural network with a narrow middle layer. It is trained on normal data only. For a normal window it rebuilds a close copy. For an unusual window the copy is poor: the **reconstruction error** is large.

`error(window) = mean( (window − rebuilt window)² )`

A simple version without a neural network is **PCA**: keep the main 2 or 3 directions of the windows, rebuild the window from them, and measure the error. Use the same idea: high error means "my model of normal does not explain this window".

```check
{"q": "An autoencoder is trained on normal windows only. A window with a new shape arrives. What do you expect?", "type": "single", "options": ["A large reconstruction error", "A reconstruction error of exactly 0", "The network fails to run"], "answer": 0, "why": ["Correct: it never learned that shape, so the rebuilt copy is poor.", "Only an exact copy gives 0.", "The network runs and gives a bad copy."]}
```

## Worked example
We put a different pattern into a sine wave and score windows of length 20 with Isolation Forest and with a PCA reconstruction error.

```python
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

rng = np.random.default_rng(0)
t = np.arange(400)
x = np.sin(2 * np.pi * t / 25) + rng.normal(0, 0.1, 400)
x[300:310] = 0.0                                   # a flat piece: the wave stops for 10 steps

w = 20
W = np.array([x[i:i + w] for i in range(len(x) - w + 1)])       # one row per window

# 1) Isolation Forest on simple window features
F = np.c_[W.mean(axis=1), W.std(axis=1), W.max(axis=1) - W.min(axis=1)]
iso = IsolationForest(n_estimators=100, random_state=0).fit(F)
top = np.argsort(iso.score_samples(F))[:3]         # lowest score_samples = most abnormal
# windows that overlap the flat piece start at positions 281 to 309
print("Isolation Forest, top windows:", sorted(top.tolist()))

# 2) PCA reconstruction error on the raw windows
pca = PCA(n_components=2).fit(W)
rebuilt = pca.inverse_transform(pca.transform(W))
err = ((W - rebuilt) ** 2).mean(axis=1)
print("PCA error, top windows:", sorted(np.argsort(-err)[:3].tolist()))

# Output:
# Isolation Forest, top windows: [287, 288, 289]
# PCA error, top windows: [290, 302, 303]
```

## Common mistakes
- Reading `score_samples` the wrong way: in scikit-learn **lower** scores mean **more abnormal**.
- Fitting on a period that already contains many anomalies.
- Training an autoencoder on all data without checking that the training part is mostly normal.
- Using windows that overlap and then counting each anomaly many times. Merge neighbouring alarms into one event.
- Skipping scaling when the features have very different units (for PCA and neural networks).

## Interview lens
**Typical question:** "You have sensor data with no labels. How would you find unusual behaviour?"

**Strong answer:** I cut the stream into windows and compute features: level, spread, range, trend, maybe frequency features. I fit an Isolation Forest on a period that I believe is mostly normal and score new windows. As a second view I train a small autoencoder or use PCA and look at the reconstruction error. I choose the threshold with a small set of known events, or from the alert budget. I merge neighbouring alarms into events, and I monitor the share of alarms over time.

**Red flags:** claiming the model needs labels; picking `contamination` by guess and reporting it as truth; not handling overlapping windows.

## Real world
- Isolation Forest was published by Liu, Ting and Zhou in 2008. It is available in scikit-learn as `IsolationForest`.
- Autoencoder-based anomaly detection on sensor windows is a common research topic (for example LSTM and convolutional autoencoders); results depend strongly on the data.

## Key points
- Isolation Forest: anomalies are isolated with few random splits. Score near 1 = anomaly.
- For time series, turn windows into features first. Fit on past, mostly-normal data.
- In scikit-learn, `score_samples` is higher for normal points. Flip the sign to rank anomalies.
- Reconstruction error (autoencoder or PCA): a window that the model cannot rebuild is unusual.
- Merge neighbouring window alarms into one event.
