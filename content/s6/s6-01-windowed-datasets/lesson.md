---
id: s6-01-windowed-datasets
title: Tensors and windowed datasets
minutes: 25
level: intermediate
goals: [Read and write tensor shapes as [batch, time, features], Cut a series into input and target windows with numpy, Split windows into train and validation by time without leakage]
prereqs: []
tags: [deep-learning, tensors, windowing, numpy]
skills: [from-scratch, leakage]
---
## Warm-up

```check
{"q": "You have 1000 daily values. You keep the LAST 200 days for validation. Why not pick 200 random days?", "type": "single",
 "options": ["Random days are harder to plot.", "Random days put future information in training, so the score looks too good.", "Random days make the model train slower."],
 "answer": 1,
 "why": ["Plotting is not the reason.", "Correct: with random days, the model sees days after the validation days. This is data leakage.", "Speed is not the reason; the problem is a wrong score."]}
```

```check
{"q": "A lag feature of 1 for day t is the value of which day?", "type": "single",
 "options": ["Day t + 1", "Day t − 1", "Day t"],
 "answer": 1,
 "why": ["That is the future. A lag always looks back.", "Correct: lag 1 is yesterday's value.", "That is the value itself, lag 0."]}
```

## Why it matters

A neural network is a big function from numbers to numbers. It cannot read "a column of dates".
You must give it many **examples**, all with the same shape. For example: "here are the last 96 hours, predict the next 24".
Every deep learning model in this stage starts from the same step. That step is to cut one long series into windows. The models are RNN, TCN, N-BEATS and Transformers.
If you get the shapes or the split wrong, the model still trains, but the score is wrong. This is the most common silent bug in deep learning projects.

## Tensors and the shape [batch, time, features]

A [[tensor]] is just a numpy array with a name that deep learning libraries use. Its **shape** tells you what each axis means.

For time series the standard shape is `[batch, time, features]`:

- **batch**: how many examples you process together (for example 32).
- **time**: how many steps each example has (for example 96).
- **features**: how many values you have at each step (for example 3: sales, price, day of week).

One example with 96 steps and 3 features has shape `[96, 3]`. A [[batch]] of 32 examples has shape `[32, 96, 3]`.
A model gets this tensor and returns a forecast with shape `[batch, horizon]` (or `[batch, horizon, targets]`).
The libraries PyTorch and TensorFlow use this layout by default for RNNs when you ask for "batch first".

```check
{"q": "A tensor has shape [64, 168, 5]. What does the 168 mean?", "type": "single",
 "options": ["64 examples in the batch", "168 time steps in each example", "5 features at each step"],
 "answer": 1,
 "why": ["The batch size is the first number, 64.", "Correct: the middle axis is time. Here, 168 steps, for example one week of hourly data.", "The number of features is the last number, 5."]}
```

## Sliding windows

A [[sliding window]] is a fixed-size frame that moves along the series one step at a time.
Each position gives one example. The first part of the frame is the **input** (the [[lookback window]]). The rest is the **target** (the [[forecast horizon]]).

Small example. The series is `0 1 2 3 4 5`. Input length 3, horizon 2. The frame has length 3 + 2 = 5.

| Window | Input (X) | Target (y) |
|---|---|---|
| 1 | 0 1 2 | 3 4 |
| 2 | 1 2 3 | 4 5 |

Number of windows = `T − input_len − horizon + 1`, where `T` is the series length. Here 6 − 3 − 2 + 1 = 2.
A **stride** larger than 1 moves the frame by more than one step. Then there are fewer, less overlapping windows.

```widget
{"name": "sliding-window", "params": {}}
```

```check
{"q": "Series length 100, input length 24, horizon 12, stride 1. How many windows?", "type": "numeric",
 "answer": 65, "tol": 0,
 "why": "100 − 24 − 12 + 1 = 65."}
```

## Making windows fast with numpy

A Python loop that copies each window is slow for long series. numpy has a trick. `sliding_window_view` gives all windows as a **view**.
A view does not copy data. It only changes how numpy reads the same memory (it changes the "strides").

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

s = np.arange(6.0)
w = sliding_window_view(s, 5)      # every frame of length 5
print(w.shape)                              # 2 frames, each of length 5
print(np.shares_memory(w, s))               # True means: no copy was made

# Output:
# (2, 5)
# True
```

Because a view shares memory, writing into it would change the original series. For training, call `.copy()` on the result, or make sure you only read it.
For a 2D series `[time, features]`, use `axis=0`. The window axis is then placed last, so you must `transpose(0, 2, 1)` to get `[n, time, features]`.

```check
{"q": "Why can sliding_window_view be called 'free'?", "type": "single",
 "options": ["It uses a GPU.", "It returns a view on the same memory and copies nothing.", "It skips windows."],
 "answer": 1,
 "why": ["It runs on the CPU with numpy.", "Correct: only the strides change. The copy happens later, if you call .copy().", "It returns all windows."]}
```

## Split by time, then scale with train statistics only

Windows that overlap share values. If window 100 is in training and window 101 is in validation, they share almost all their data. That is [[leakage]].
The rules:

1. Split the **series** at a time point first. Or split the windows by time. Leave a **gap** of at least `input_len + horizon − 1` windows between train and validation.
2. Compute the mean and standard deviation on the **training part only**. Use them to scale both parts.
3. Never shuffle windows across the split. Shuffling **inside** the training set is fine and helps the optimizer.

```chart
{"title": "Split by time with a gap", "x": "step", "height": 220,
 "series": [
   {"name": "series", "gen": [["trend", {"slope": 0.2, "start": 10}], ["season", {"period": 24, "amp": 4}], ["noise", {"sd": 0.6}]], "n": 240, "seed": 5}
 ],
 "marks": [{"x": 160, "label": "train ends"}, {"x": 190, "label": "validation starts (after gap)"}],
 "caption": "Train on the left part. The gap keeps the last training window from overlapping the first validation window."}
```

```check
{"q": "You standardize the whole series with its global mean and std, then split. What is wrong?", "type": "single",
 "options": ["Nothing, scaling is harmless.", "The mean and std use future values, so information leaks into training.", "Standardizing is not allowed for neural networks."],
 "answer": 1,
 "why": ["Scaling with the full series uses validation data to set the scale.", "Correct: the scale must come from the training part only.", "Scaling is normal and helps training."]}
```

## Worked example

We build windows for a 2-feature series, split by time with a gap, and scale with train statistics.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

# 50 days: column 0 = sales (the target), column 1 = day of week (0..6)
t = np.arange(50)
sales = 100 + 2 * t + 10 * (t % 7 == 5)          # trend + a bump on day 5 of each week
series = np.column_stack([sales, t % 7]).astype(float)   # shape [50, 2]

input_len, horizon = 7, 3
total = input_len + horizon

# 1) all frames of length 10 along the time axis, then reorder to [n, time, features]
frames = sliding_window_view(series, total, axis=0).transpose(0, 2, 1)
X = frames[:, :input_len, :].copy()    # the past, both features
y = frames[:, input_len:, 0].copy()    # the future sales only
print("X", X.shape, "y", y.shape)

# 2) split by time. The last training window must end before the first validation target starts.
n = len(X)
n_train = 20
gap = total - 1                         # windows that would overlap with the training windows
X_tr, y_tr = X[:n_train], y[:n_train]
X_va, y_va = X[n_train + gap:], y[n_train + gap:]
print("train", X_tr.shape, "validation", X_va.shape)

# 3) scale with TRAIN statistics only (per feature)
mean = X_tr.mean(axis=(0, 1))
std = X_tr.std(axis=(0, 1))
X_tr_s = (X_tr - mean) / std
X_va_s = (X_va - mean) / std
print("mean", mean.round(2), "std", std.round(2))
print("train scaled mean", X_tr_s.mean(axis=(0, 1)).round(2))

# Output:
# X (41, 7, 2) y (41, 3)
# train (20, 7, 2) validation (12, 7, 2)
# mean [126.43   3.  ] std [12.66  2.  ]
# train scaled mean [0. 0.]
```

Read it: `X` has shape `[41, 7, 2]` (41 windows, 7 steps, 2 features). Only after the split do we compute `mean` and `std`.

## Common mistakes

- Putting the window axis in the wrong place: `[batch, features, time]` instead of `[batch, time, features]`. Check every layer's expected order.
- Scaling before the split (leakage).
- Random train/validation split of windows. Overlapping windows leak.
- Forgetting that targets may use only one feature, while inputs use all.
- Using the future values of a feature as an input without saying it is a known-future input. An example is next day's price.

## Interview lens

**Typical question:** "You have 3 years of hourly demand. How do you build the training set for an LSTM?"

**Strong answer:** I choose a lookback window and a horizon from the business need. For example, 168 hours back and 24 hours ahead. I cut sliding windows with shape `[batch, time, features]`, with the target as the next 24 values. I split by time. I train on the older part, validate on the next part and test on the latest part. I leave a gap so windows do not overlap. I compute the scaling statistics on the training part only. I also build a seasonal naive baseline on the same split to know if the network adds value.

**Red flags:** random shuffle split before windowing; scaling with all data; no baseline; not knowing the shape of the input tensor.

## Real world

- The GluonTS library (from Amazon) and the PyTorch Forecasting library both slide a window over each series. This builds the training examples. They sample windows from many series, which is why they can train one global model.
- In the M5 and Kaggle forecasting competitions, a careful time-based validation scheme was often worth more than a new model. Random splits gave scores that did not match the leaderboard.

## Key points

- A tensor has an agreed shape: `[batch, time, features]`.
- A sliding window gives an input (lookback) and a target (horizon). Count: `T − input_len − horizon + 1`.
- `sliding_window_view` makes windows without copying. Copy before you change them.
- Split by time, leave a gap, and compute scaling statistics on the training part only.
