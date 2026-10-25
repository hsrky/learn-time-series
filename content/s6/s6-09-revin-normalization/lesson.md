---
id: s6-09-revin-normalization
title: RevIN and distribution shift
minutes: 25
level: advanced
goals: [Explain distribution shift in a forecasting model, Implement RevIN normalize and denormalize, Know when to use instance normalization instead of global scaling]
prereqs: [s6-01-windowed-datasets, s6-08-are-transformers-effective]
tags: [revin, normalization, distribution-shift]
skills: [from-scratch, leakage]
---
## Warm-up

```check
{"q": "Where do you compute the mean for global standardization of the inputs?", "type": "single",
 "options": ["On the training data only", "On all data", "On the test data"], "answer": 0,
 "why": ["Correct.", "That leaks the future.", "That leaks the test set."]}
```

```check
{"q": "NLinear subtracts which value from the input window before the linear layer?", "type": "single",
 "options": ["The window mean", "The last value of the window", "The first value of the window"], "answer": 1,
 "why": ["That is close to RevIN, but NLinear uses the last value.", "Correct.", "Not what NLinear does."]}
```

## Why it matters

A model that learned "sales are around 100" in 2023 fails when sales are around 300 in 2025. The shape of the weekly pattern may be the same, but the level is new. This is [[distribution shift]]: the statistics of the data (mean, spread) change between training and use.
Time series change level often: growth, inflation, new products, sensor recalibration. **RevIN** is a small layer that makes a model robust to this. It is used inside PatchTST and in many other recent models.

## The idea in numbers

Take an input window `[100, 110, 120]`.

1. **Normalize** with the window's own mean and standard deviation: mean = 110, std = 8.165 (population). Normalized window: `[−1.22, 0, +1.22]`.
2. The model works on this normalized window, where level and scale are gone. Suppose it predicts the next value as `+2.0` (in normalized units).
3. **Denormalize**: `2.0 · 8.165 + 110 = 126.3`. The forecast is back on the original scale.

Now take a window `[1000, 1100, 1200]`. It has the same shape, so the normalized window is the same and the model predicts `+2.0` again. Denormalized, it is `2.0 · 81.65 + 1100 = 1263`. The model did not need to see level 1100 in training.

```chart
{"title": "Same pattern, new level after step 60", "x": "step", "height": 200,
 "series": [{"name": "series", "gen": [["season", {"period": 12, "amp": 5}], ["const", {"value": 100}], ["step", {"at": 60, "size": 200}]], "n": 100, "seed": 1}],
 "marks": [{"x": 60, "label": "level jumps"}],
 "caption": "The wave is the same before and after the jump. RevIN removes the level, so the model sees the same shape in both parts."}
```

The name: **Rev**ersible **In**stance **N**ormalization (Kim et al., ICLR 2022). "Instance" means each input window (each instance) is normalized by itself. "Reversible" means the same numbers are used to undo the step at the output.

```check
{"q": "Window [2, 4, 6]: mean 4, population std 1.633. What is the normalized value of 6?", "type": "numeric", "answer": 1.2247, "tol": 0.001,
 "why": "(6 − 4) / 1.633 = 1.2247."}
```

## The formulas

For each sample and each channel, over the time axis:

`mean = average of x`, `std = sqrt( variance(x) + eps )`

`x_norm = (x − mean) / std · gamma + beta`

After the model: `y = ( (y_norm − beta) / gamma ) · std + mean`

- `x`: input window, shape `[batch, time, channels]`.
- `mean`, `std`: computed per sample, per channel. Shape `[batch, 1, channels]`.
- `eps`: a tiny number (like 1e-5) so we never divide by zero when a window is flat.
- `gamma`, `beta`: learned scale and shift per channel (shape `[channels]`). They let the model undo part of the normalization if that helps.
- The model output `y_norm` has shape `[batch, horizon, channels]`.

Important: the **same** `mean` and `std` from the **input** window are used for the output. The model never sees the future, so there is no leakage.

```check
{"q": "Which statistics does RevIN use to denormalize the forecast?", "type": "single",
 "options": ["The mean and std of the input window", "The mean and std of the true future", "The mean and std of the whole training set"], "answer": 0,
 "why": ["Correct: they are known when you forecast.", "The future is unknown at forecast time; using it would be leakage.", "That would be global scaling, not instance normalization."]}
```

## RevIN vs global scaling vs NLinear

| Method | Statistics from | Handles level shift | Note |
|---|---|---|---|
| Global standardization | whole training set | No | Simple; the test level may be new |
| RevIN | each input window | Yes | Mean and spread of the window; reversible |
| NLinear | last value of the window | Yes (level only) | No scale change |
| DeepAR scaling | mean of the window | Yes (scale) | Divides by the average |

A limit of RevIN: if the window is short or noisy, the mean and std are noisy too. And it removes the level information, which can matter (for example, if "high sales" behave differently from "low sales"). Some models add the removed mean and std back as extra inputs.

```check
{"q": "A series jumps to a new level that never appeared in training. Which approach copes best?", "type": "single",
 "options": ["Global standardization with train statistics", "RevIN per window", "No scaling"], "answer": 1,
 "why": ["The new level is far outside the training range, so inputs look extreme.", "Correct: each window is brought to mean 0 and std 1.", "Raw values would be even more extreme for the network."]}
```

## Worked example

We fit a simple linear forecaster on a series at one level. Then the level jumps. We compare plain scaling with RevIN.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

rng = np.random.default_rng(0)
t = np.arange(600)
base = 5 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.3, 600)     # a pattern with period 12
y = 100 + base                                                       # level 100
y[400:] += 200                                                       # the level jumps to 300 after t = 400

L, H = 24, 6
frames = sliding_window_view(y, L + H)
X, Y = frames[:, :L], frames[:, L:]
Xtr, Ytr = X[:300], Y[:300]                                          # train: only level 100
Xte, Yte = X[400:], Y[400:]                                          # test: windows that start after the jump
print("test windows:", len(Xte), " test level ~", round(float(Xte.mean())))

def fit_linear(A, B):
    A1 = np.concatenate([A, np.ones((len(A), 1))], axis=1)
    return np.linalg.lstsq(A1, B, rcond=None)[0]

def predict(A, W):
    return np.concatenate([A, np.ones((len(A), 1))], axis=1) @ W

# A) plain model on raw values
W_raw = fit_linear(Xtr, Ytr)
mae_raw = np.abs(Yte - predict(Xte, W_raw)).mean()

# B) RevIN-style: normalize each window by its own mean/std, fit, then denormalize with the same numbers
def revin(X):
    m = X.mean(axis=1, keepdims=True)
    s = np.sqrt(X.var(axis=1, keepdims=True) + 1e-5)
    return (X - m) / s, m, s

Xn, m, s = revin(Xtr)
Yn = (Ytr - m) / s                                                   # targets use the INPUT window statistics
W_rev = fit_linear(Xn, Yn)
Xn_te, m_te, s_te = revin(Xte)
pred_rev = predict(Xn_te, W_rev) * s_te + m_te                       # denormalize
mae_rev = np.abs(Yte - pred_rev).mean()

print("MAE plain linear on raw values:", round(float(mae_raw), 2))
print("MAE with RevIN-style scaling  :", round(float(mae_rev), 2))
print("MAE naive (last value)        :", round(float(np.abs(Yte - Xte[:, -1:]).mean()), 2))

# Output:
# test windows: 171  test level ~ 300
# MAE plain linear on raw values: 229.64
# MAE with RevIN-style scaling  : 0.26
# MAE naive (last value)        : 4.58
```

The plain model learned "values are around 100". It cannot handle level 300. With RevIN, the same linear model works at the new level, because it only sees the shape.

```notebook
# PyTorch sketch of the RevIN layer (check the original authors' code for the full version)
import torch
import torch.nn as nn

class RevIN(nn.Module):
    def __init__(self, n_channels, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(n_channels))
        self.beta = nn.Parameter(torch.zeros(n_channels))

    def forward(self, x, mode):                      # x: [batch, time, channels]
        if mode == "norm":
            self.mean = x.mean(dim=1, keepdim=True)
            self.std = torch.sqrt(x.var(dim=1, keepdim=True, unbiased=False) + self.eps)
            return (x - self.mean) / self.std * self.gamma + self.beta
        return (x - self.beta) / self.gamma * self.std + self.mean    # mode == "denorm"
```

## Common mistakes

- Computing the mean and std over the batch axis instead of the time axis.
- Using statistics of the target (future) window. That is leakage.
- Using the sample variance (divide by n − 1) in one place and the population variance in another; stay consistent.
- Applying RevIN to features that should not be scaled (for example a 0/1 holiday flag or a category).
- Forgetting `eps`: a flat window then gives a division by zero.

## Interview lens

**Typical question:** "What is distribution shift in time series and how does RevIN address it?"

**Strong answer:** Distribution shift means the mean, spread or pattern of the data in use differs from training; in time series it is common because of trend and level changes. RevIN normalizes each input window with its own mean and standard deviation per channel, lets the model work on the normalized data, then denormalizes the output with the same statistics. Learnable scale and shift parameters let the model recover from over-normalizing. It is reversible and does not use the future. The cost is that level information is removed, so I would check if the level matters for the task.

**Red flags:** confusing RevIN with batch normalization; computing statistics over the batch; using the future window to denormalize.

## Real world

- RevIN was proposed by Kim et al. at ICLR 2022 and was used in PatchTST and many later long-term forecasting models.
- Pre-trained foundation models use the same family of ideas: Chronos divides each series by the mean of its absolute values before turning it into tokens (stage 7).

## Staff lens

- **Monitoring.** Instance normalization hides level shifts from the model, but not from your business. Still monitor the raw level and spread of inputs and alert when they leave the known range.
- **Platform default.** Put per-window scaling in the shared model code, so no team forgets it or leaks train statistics.

## Key points

- Distribution shift: the data in use has different level or spread than the training data.
- RevIN normalizes each window with its own mean and std, and denormalizes the output with the same numbers.
- `x_norm = (x − mean)/std · gamma + beta`; use `eps` for flat windows.
- Use only input-window statistics. Never use the future.
