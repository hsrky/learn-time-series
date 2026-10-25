---
id: s5-05-multistep-strategies
title: Multi-step strategies: recursive, direct, MIMO and hybrid
minutes: 30
level: intermediate
goals: [Explain recursive, direct, MIMO and hybrid forecasting, Implement recursive and direct forecasts with numpy [[least squares]], Choose a strategy using error growth and cost]
prereqs: [s5-01-reduction-to-supervised, s5-02-lag-and-rolling-features]
tags: [multi-step, recursive, direct, mimo]
skills: [from-scratch, backtest]
---
## Warm-up
```check
{"q": "A series has 40 points. Window 4, horizon 2 (targets are the next 2 values). How many rows?", "type": "numeric",
 "answer": 35, "tol": 0.001,
 "why": "40 - 4 - 2 + 1 = 35."}
```

```check
{"q": "Which feature is allowed in a direct model for horizon 7, counting back from the forecast origin?", "type": "single",
 "options": ["The value at the origin", "The value 3 days after the origin", "The mean of the next 7 days"],
 "answer": 0,
 "why": ["Correct: the origin is the last known time.", "That day has not happened at the origin.", "That is the target period itself."]}
```

## Why it matters
Most business questions need more than one step: the next 14 days, the next 12 months. A model that predicts one step ahead can be used for many steps in different ways. The way you choose, called the **multi-step strategy**, changes the error, the cost and the code. Interviewers like this topic, because it shows that you understand how errors travel.

## Recursive (iterated)
Train **one** model for one step ahead (the [[recursive strategy]]). To forecast `h` steps:

1. Predict step 1 from the last real values.
2. Add the prediction to the history as if it were real.
3. Predict step 2 from the updated history. Repeat.

Pros: one model, simple, any horizon. Cons: **errors accumulate**. A small mistake in step 1 becomes an input for step 2. All features (lags, rolling means) must be recomputed from predictions. Features that are unknown in the future, such as price, need their own forecast.

Example: last values 10, 12. The model says: next = 1.1 × last. Step 1: 13.2. Step 2: 1.1 × 13.2 = 14.52, and so on.

```check
{"q": "Why can recursive forecasts get worse at long horizons?", "type": "single",
 "options": ["The model forgets how to predict", "Each predicted value, with its error, is used as an input for the next step", "The data gets smaller"],
 "answer": 1,
 "why": ["The model is the same at every step.", "Correct: errors feed back and can grow.", "The data size does not change."]}
```

## Direct
Train **one model per horizon step** (the [[direct strategy]]). Model `k` predicts `y(t+k)` directly from the information at time `t`. For horizon 6, you train 6 models.

Pros: no feedback of errors; each model can use its own features and settings. Cons: `h` models to train and store; the forecasts of different steps may not fit together (a "jumpy" path); each model sees fewer training rows at long horizons.

Example: model 1 learns `y(t+1) = f1(y(t), y(t−1), ...)`. Model 3 learns `y(t+3) = f3(y(t), y(t−1), ...)`. Both use the same inputs but have different targets.

```check
{"q": "Horizon 12, direct strategy. How many models do you train?", "type": "numeric",
 "answer": 12, "tol": 0.001,
 "why": "One model per horizon step: 12."}
```

## MIMO and hybrid
**[[mimo|MIMO]]** (multi-input multi-output): **one** model predicts the whole vector `y(t+1), ..., y(t+h)` at once. The target table has `h` columns. Neural networks and multi-output regression do this naturally. Pros: one model, forecasts are consistent. Cons: the model must share its capacity among all steps. (Gradient boosting libraries need one model per output, or a wrapper.)

**[[hybrid strategy|Hybrid]]** strategies mix ideas. Examples: **DirRec** (a direct model for each step that also uses the predictions of earlier steps as inputs); or **block** strategies (one MIMO model per block of steps, such as days 1–7 and days 8–14).

| Strategy | Models | Error feedback | Typical use |
|---|---|---|---|
| Recursive | 1 | yes | ARIMA-like, simple ML, many steps |
| Direct | h | no | Gradient boosting, M5-style |
| MIMO | 1 | no | Neural networks |
| Hybrid | few | partly | Long horizons with a compromise |

```chart
{"title": "Typical error by horizon step (illustration, made-up numbers)", "x": "horizon step", "height": 220,
 "series": [
   {"name": "recursive", "y": [1.0, 1.4, 1.9, 2.5, 3.2, 4.0]},
   {"name": "direct", "y": [1.0, 1.5, 1.8, 2.0, 2.2, 2.4], "dash": true}
 ],
 "caption": "Recursive errors often grow faster because of feedback. Direct errors grow more slowly. The best strategy depends on the data."}
```

```check
{"q": "You have a neural network that outputs 14 values at once. Which strategy is it?", "type": "single",
 "options": ["Recursive", "Direct", "MIMO"],
 "answer": 2,
 "why": ["Recursive uses one 1-step model many times.", "Direct would need 14 separate models.", "Correct: one model, vector output."]}
```

## Worked example
We build an AR(6) model with numpy least squares and forecast 6 steps with both strategies. The series has a season of 12 and a slow trend.

```python
import numpy as np

rng = np.random.default_rng(0)
t = np.arange(200)
y = 10 + 3 * np.sin(2 * np.pi * t / 12) + 0.02 * t + rng.normal(0, 0.3, 200)
train, test = y[:180], y[180:186]
p, H = 6, 6

def windows(y, p, k):
    """Features: p lags, plus a 1 for the intercept. Target: value k steps after the window."""
    n = len(y) - p - k + 1
    X = np.array([y[i:i + p] for i in range(n)])
    Y = np.array([y[i + p + k - 1] for i in range(n)])
    return np.c_[X, np.ones(n)], Y

# Recursive: one 1-step model, feed predictions back
A, Y = windows(train, p, 1)
w, *_ = np.linalg.lstsq(A, Y, rcond=None)
hist = list(train[-p:])
rec = []
for _ in range(H):
    nxt = float(np.r_[hist[-p:], 1.0] @ w)
    rec.append(nxt)
    hist.append(nxt)                       # the prediction becomes an input

# Direct: one model per step k
last = np.r_[train[-p:], 1.0]
dire = []
for k in range(1, H + 1):
    A, Y = windows(train, p, k)
    wk, *_ = np.linalg.lstsq(A, Y, rcond=None)
    dire.append(float(last @ wk))

print("recursive abs error by step:", np.abs(test - rec).round(2))
print("direct abs error by step   :", np.abs(test - dire).round(2))
print("mean recursive:", round(np.abs(test - rec).mean(), 3))
print("mean direct   :", round(np.abs(test - dire).mean(), 3))
# Output:
# recursive abs error by step: [0.31 0.18 1.11 0.86 1.25 1.49]
# direct abs error by step   : [0.31 0.12 0.36 0.01 0.05 0.11]
# mean recursive: 0.868
# mean direct   : 0.161
```

In this one run, direct has the lower error (0.16 against 0.87), because the recursive path carries its small mistakes forward. One run is not proof. Always compare the strategies in a walk-forward backtest, step by step.

## Common mistakes
- In a recursive loop, using the **true** future values as lags (a leak). Feed back predictions only.
- Recomputing rolling features from the real series in the recursive loop.
- Using a future covariate (price, weather) that is not known for the whole horizon.
- Training direct models with different training windows, so they cannot be compared.
- Reporting one average error for all steps.
- Forgetting that the number of training rows shrinks for large `k` in direct models.

## Interview lens
**Typical question:** "You must forecast the next 28 days with gradient boosting. What strategy do you use and why?"

**Strong answer:** There are three main options. A recursive model is one 1-step model used 28 times; it is cheap but errors accumulate and I need to recompute lag features from predictions. A direct strategy trains one model per horizon step; it avoids error feedback and can use step-specific features, at the cost of more models. MIMO predicts all 28 values at once, which suits neural networks. For gradient boosting, I would start with direct for important steps, or with a global model that gets the horizon step as a feature. I compare the options in a walk-forward backtest with errors per step.

**Red flags:** not knowing that errors accumulate in recursive forecasting; using true future lags inside a recursive loop; one model for all steps without any horizon information.

## Real world
- Taieb, Bontempi and co-authors compared recursive, direct and MIMO strategies in a well-known study; no strategy wins everywhere.
- Many top solutions in the M5 competition trained separate gradient boosting models per horizon block or per day, using a direct approach.
- Nixtla's `mlforecast` supports both recursive and direct strategies for tree models.

## Key points
- Recursive: one 1-step model used repeatedly. Cheap but errors accumulate.
- Direct: one model per step. No feedback, but more models.
- MIMO: one model with `h` outputs. Natural for neural nets.
- Hybrid methods mix them (DirRec, blocks).
- Choose by backtest, and always report the error for each horizon step.
