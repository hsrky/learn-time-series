---
id: s6-08-are-transformers-effective
title: Are Transformers effective? DLinear and NLinear
minutes: 30
level: advanced
goals: [Explain the claim of Zeng et al. (AAAI 2023), Implement DLinear (decomposition plus linear layers) and NLinear, Judge a deep model fairly against a simple linear baseline]
prereqs: [s6-07-transformers-for-ts]
tags: [dlinear, nlinear, baselines, ltsf]
skills: [baseline-first, from-scratch, communication]
---
## Warm-up

```check
{"q": "How many tokens does PatchTST create from 512 steps with patch length 16, stride 8 and end padding 8?", "type": "numeric", "answer": 64, "tol": 0,
 "why": "(512 + 8 − 16) // 8 + 1 = 64."}
```

```check
{"q": "Why do we always build a naive or seasonal naive baseline first?", "type": "single",
 "options": ["To know whether a complex model adds value.", "Because it is required by law.", "To make training faster."], "answer": 0,
 "why": ["Correct.", "There is no such law.", "It has no effect on training speed."]}
```

## Why it matters

In 2022, the paper **"Are Transformers Effective for Time Series Forecasting?"** asked a direct question and gave a surprising answer. The authors were Zeng, Chen, Zhang and Xu (AAAI 2023). A very simple **one-layer linear model** beat many new Transformer models. This was on popular long-term forecasting benchmarks, often by a large margin.
This lesson is about method as much as models. A strong, simple baseline can show that a field made less progress than it looked.

## The claim and the reasons

The authors tested Transformer models (Informer, Autoformer, FEDformer and others) on nine real data sets for long-term forecasting (LTSF). Their points:

1. **Attention ignores order by itself.** Self-attention treats the tokens as a set. Time series depend strongly on order. Positional encodings help, but the authors argue that point-wise tokens still lose temporal information.
2. **More history did not help the Transformers.** With a longer lookback window, errors often did not improve. Sometimes they got worse. The linear models improved.
3. **A very simple model was enough.** One linear layer from the past to the future horizon was a strong baseline.

Remember what this does **not** say: it does not say "Transformers never work". Later work (PatchTST, iTransformer, and foundation models in stage 7) fixed some design problems. The lasting lesson is about baselines.

```check
{"q": "What is the main lesson of the Zeng et al. paper for your own projects?", "type": "single",
 "options": ["Never use Transformers.", "Always compare complex models with simple linear baselines.", "Linear models are always best."], "answer": 1,
 "why": ["The paper does not say that.", "Correct.", "Linear models have limits (see Common mistakes)."]}
```

## DLinear: decomposition plus two linear layers

**DLinear** has two steps (you built it in the practice problem):

1. **Decompose** the input window with a moving average. The moving average is the *trend*. The rest, `window − trend`, is the *remainder* (it holds the season and noise). At the edges, the first and last values are repeated, so the length stays the same. The kernel size in the paper is 25.
2. Apply **one linear layer** to the trend and **another** to the remainder. Each maps `L` past steps to `H` future steps. Add the two outputs.

`forecast = trend · W_trend + remainder · W_rem`

- `trend`, `remainder`: vectors of length `L` (the lookback).
- `W_trend`, `W_rem`: weight matrices of shape `[L, H]`. That is only `2·L·H` numbers.

The weights can be shared by all variables or kept separate for each variable.

## NLinear: a one-step fix for level shifts

**NLinear** is even simpler. Subtract the **last value** of the window from the whole window. Apply one linear layer, then add the last value back. It handles a level shift in the data (a form of distribution shift) without any decomposition.

```chart
{"title": "Decomposition: trend and remainder of one window", "x": "step", "height": 220,
 "series": [
   {"name": "window", "gen": [["trend", {"slope": 0.3, "start": 20}], ["season", {"period": 12, "amp": 4}], ["noise", {"sd": 0.5}]], "n": 48, "seed": 4},
   {"name": "trend (moving average idea)", "gen": [["trend", {"slope": 0.3, "start": 20}]], "n": 48, "dash": true}
 ],
 "caption": "The linear layer for the trend extends the slope. The linear layer for the remainder repeats the wave."}
```

```check
{"q": "L = 96 past steps, H = 24 future steps. How many weights has DLinear (no bias, two linear layers)?", "type": "numeric", "answer": 4608, "tol": 0,
 "why": "2 · 96 · 24 = 4608."}
```

## Why a linear model can work

Many LTSF data sets are strongly seasonal and smooth (electricity, traffic, weather). A weighted sum of the last `L` values can copy "the same hour yesterday" or "the same hour last week". It can also extend the trend. This is almost what seasonal naive plus drift does, but with weights learned from data.
Where the linear model fails: sudden events, non-linear effects (price × promotion), cross-variable effects, and short noisy series. For those you need richer models or features.

```check
{"q": "Which situation is hard for a linear model on the past window?", "type": "single",
 "options": ["A clean daily season", "A multiplicative effect of price and promotion together", "A steady upward trend"], "answer": 1,
 "why": ["A linear map copies seasons well.", "Correct: an interaction needs a non-linear model.", "Trend is easy for linear models."]}
```

## Worked example

We fit a DLinear-style model with least squares. No neural network library is needed. The data is a synthetic hourly-like series with a period of 24. Then we compare it with naive and seasonal naive forecasts.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

rng = np.random.default_rng(0)
T = 900
t = np.arange(T)
y = 50 + 0.02 * t + 8 * np.sin(2 * np.pi * t / 24) + rng.normal(0, 1.0, T)

L, H, K = 72, 12, 25                                   # lookback, horizon, moving-average kernel

def decompose(X, k):                                   # X: [n, L] -> trend, remainder
    pad = (k - 1) // 2
    P = np.concatenate([np.repeat(X[:, :1], pad, 1), X, np.repeat(X[:, -1:], pad, 1)], axis=1)
    trend = sliding_window_view(P, k, axis=1).mean(-1)
    return trend, X - trend

frames = sliding_window_view(y, L + H)                 # [n, L+H]
X, Y = frames[:, :L], frames[:, L:]
split = 500                                            # train on the first windows, test on later ones
gap = L + H - 1                                        # no overlap between train and test windows
Xtr, Ytr, Xte, Yte = X[:split], Y[:split], X[split + gap:], Y[split + gap:]

# two linear layers == one least-squares fit on [trend, remainder] side by side
def features(X):
    tr, rem = decompose(X, K)
    return np.concatenate([tr, rem], axis=1)           # [n, 2L]

A = features(Xtr)
W = np.linalg.solve(A.T @ A + 1e-3 * np.eye(2 * L), A.T @ Ytr)    # ridge: tiny penalty for stability
pred = features(Xte) @ W

naive = np.repeat(Xte[:, -1:], H, axis=1)                          # repeat the last value
snaive = Xte[:, -24:][:, np.arange(H) % 24]                        # repeat the last season (period 24)

mae = lambda p: round(float(np.abs(Yte - p).mean()), 3)
print("test windows:", len(Xte), " weights:", W.size)
print("MAE naive          :", mae(naive))
print("MAE seasonal naive :", mae(snaive))
print("MAE DLinear-style  :", mae(pred))

# Output:
# test windows: 234  weights: 1728
# MAE naive          : 7.013
# MAE seasonal naive : 1.12
# MAE DLinear-style  : 0.771
```

The linear model learns the season and the trend from data. It beats the naive forecast by a wide margin and is also better than seasonal naive here. On a series with more noise or less season, the order of the results can change. That is why you run the comparison on your own data.

```notebook
# PyTorch version (sketch). Run with PyTorch installed.
import torch
import torch.nn as nn

class DLinear(nn.Module):
    def __init__(self, L, H, kernel=25):
        super().__init__()
        self.kernel = kernel
        self.lin_trend = nn.Linear(L, H)
        self.lin_rem = nn.Linear(L, H)

    def forward(self, x):                                  # x: [batch, L]
        pad = (self.kernel - 1) // 2
        xp = torch.cat([x[:, :1].repeat(1, pad), x, x[:, -1:].repeat(1, pad)], dim=1)
        trend = xp.unfold(1, self.kernel, 1).mean(-1)      # moving average, [batch, L]
        return self.lin_trend(trend) + self.lin_rem(x - trend)
```

## Common mistakes

- Reading the paper as "Transformers are useless". Newer designs (patching, inversion) and pre-trained models changed the picture.
- Skipping the linear baseline in your own project because "it is too simple".
- Using a lookback so short that the linear model cannot see the season.
- Expecting a linear model to learn effects of promotions or holidays that need interactions.
- Comparing models on one data set and one horizon only.

## Interview lens

**Typical question:** "What did 'Are Transformers Effective for Time Series Forecasting?' show, and how does it change how you work?"

**Strong answer:** The authors showed that a one-layer linear model, DLinear, beat many Transformer forecasters on long-term benchmarks. It splits the window into a moving-average trend and a remainder. It applies one linear layer to each. They argued that attention loses order and that Transformers did not use longer history well. For my work it means I always build naive, seasonal naive and a linear model first. I report the lift of the complex model over them. I run the comparison on my own data with a time-based backtest. It does not mean Transformers are useless: later models like PatchTST narrowed the gap, and linear models cannot learn interactions.

**Red flags:** quoting the paper as proof that deep learning fails; not knowing how DLinear works; no mention of baselines.

## Real world

- The code and benchmarks of the paper are public (the LTSF-Linear repository). Libraries like NeuralForecast and Darts include DLinear and NLinear.
- The paper changed how many follow-up papers report results: they now include DLinear as a standard baseline.

## Staff lens

- **Evaluation governance.** Put simple baselines into the evaluation platform as defaults, so every new model must beat them. Make this a rule of the review process, not a favor.
- **Reproducibility.** Benchmarks fail silently with small code differences (data splits, scaling, dropping the last batch). Keep one shared, versioned evaluation harness for all teams.
- **Build vs buy.** A linear model may get 95% of the lift at 1% of the cost. Then it is the right answer for most series. Keep the expensive model for the series where it earns its cost.

## Key points

- Zeng et al. (AAAI 2023): simple linear models (DLinear, NLinear) beat many Transformers on long-term benchmarks.
- DLinear = moving-average decomposition + one linear layer for trend and one for remainder.
- NLinear = subtract the last value, linear layer, add it back.
- The lasting lesson: build strong simple baselines first, on your own data.
