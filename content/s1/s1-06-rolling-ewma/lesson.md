---
id: s1-06-rolling-ewma
title: Rolling windows and EWMA
minutes: 30
level: beginner
goals: [Compute rolling mean and rolling std, Explain trailing versus centered windows and why centered leaks, Write the EWMA formula and choose alpha, Build a leak-free rolling feature]
prereqs: [s1-05-lags-differences-returns]
tags: [rolling, ewma, smoothing, leakage]
skills: [leakage, from-scratch, pandas-fluency]
---
## Warm-up

```check
{"q": "A price goes from 200 to 180. What is the simple return?", "type": "numeric", "answer": -0.1, "tol": 0.0001,
 "why": "180 / 200 − 1 = −0.10, so −10%."}
```

```check
{"q": "Which call removes a weekly season from a daily series?", "type": "single",
 "options": ["s.diff(7)", "s.diff(1)", "s.shift(1)"], "answer": 0,
 "why": ["Correct. It subtracts the value of the same weekday last week.", "diff(1) removes a trend, not a weekly pattern.", "shift(1) only moves values."]}
```

## Why it matters

Daily numbers jump up and down. A manager does not want to see every jump. She wants the "recent level": how are we doing lately?

A smoothed line answers this. It is also the base of many features ("average of the last 7 days") and many forecasts.

But smoothing hides a trap. If your smoother looks at days **after** the one you smooth, you leak the future. This lesson shows you how to avoid it.

## Rolling windows

A [[rolling window]] of size k takes the last k values and computes one number. Then the window moves one step.

Example: values 2, 4, 6, 8, 10 and k = 3.

| t | window | mean |
|---|---|---|
| 3 | 2, 4, 6 | 4 |
| 4 | 4, 6, 8 | 6 |
| 5 | 6, 8, 10 | 8 |

The first k − 1 rows have no result (NaN), unless you set `min_periods`.

Other statistics work too: `std` (how much the values vary), `min`, `max`, `median`, `quantile(0.9)`. A window of the last k values that ends at **today** is called **trailing**.

```python
import pandas as pd

s = pd.Series([2, 4, 6, 8, 10])
print(s.rolling(3).mean().tolist())
print(s.rolling(3, min_periods=1).mean().tolist())    # shorter windows at the start
print(s.rolling(3).std().round(2).tolist())           # spread inside each window
# Output:
# [nan, nan, 4.0, 6.0, 8.0]
# [2.0, 3.0, 4.0, 6.0, 8.0]
# [nan, nan, 2.0, 2.0, 2.0]
```

```check
{"q": "s = [1, 3, 5, 7]. What is s.rolling(2).mean() at the last row?", "type": "numeric", "answer": 6, "tol": 0,
 "why": "The last window is [5, 7]. The mean is 6."}
```

## Trailing or centered?

A trailing window uses today and the past. A **centered** window uses the values around today: some before, some after.

`s.rolling(5, center=True).mean()` at day t uses days t−2 to t+2. It looks 2 days **into the future**.

- For **describing** the past (a plot, a trend estimate, decomposition): centered is good. It has no delay.
- For **features or forecasts**: centered is leakage. In real life you do not know days t+1 and t+2 yet.

Trailing windows have a price: a **delay**. After a sudden jump, the trailing mean needs time to catch up.

```chart
{"title": "A step up on day 11: trailing, centered and EWMA", "x": "day", "height": 250,
 "series": [
  {"name": "raw", "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], "y": [10,10,10,10,10,10,10,10,10,10,20,20,20,20,20,20,20,20,20,20], "kind": "dots"},
  {"name": "trailing mean (5)", "x": [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], "y": [10,10,10,10,10,10,12,14,16,18,20,20,20,20,20,20]},
  {"name": "centered mean (5)", "x": [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18], "y": [10,10,10,10,10,10,12,14,16,18,20,20,20,20,20,20], "dash": true},
  {"name": "EWMA alpha 0.4", "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], "y": [10,10,10,10,10,10,10,10,10,10,14,16.4,17.8,18.7,19.2,19.5,19.7,19.8,19.9,19.9]}
 ],
 "caption": "The dashed centered line starts to rise on day 9, two days BEFORE the jump. It has seen the future. The trailing line and the EWMA react only after the jump."}
```

```check
{"q": "You build a rolling-mean feature to predict tomorrow's sales. Which setting is safe?", "type": "single",
 "options": ["Trailing window, shifted by one so it ends yesterday", "center=True", "A trailing window that includes today's value when today is the target"], "answer": 0,
 "why": ["Correct. It only uses values before the target.", "A centered window includes future days.", "If today is the target, the window contains the answer."]}
```

## EWMA: recent values count more

A rolling mean gives all k values the same weight and drops older ones suddenly. The [[EWMA]] (exponentially weighted moving average) gives **recent values more weight**, and older values less and less. It needs no window size.

S(t) = α · y(t) + (1 − α) · S(t − 1)

- y(t): the value at time t.
- S(t): the smoothed value at time t. Start with S(0) = y(0).
- α (alpha): a number between 0 and 1. The **smoothing factor**.

Big α (0.8): follows the data closely, little smoothing. Small α (0.1): very smooth, slow reaction.

Example with α = 0.4 and values 10, 10, 20: S(0) = 10. S(1) = 10. S(2) = 0.4·20 + 0.6·10 = 14.

## EWMA in pandas

In pandas: `s.ewm(alpha=0.4, adjust=False).mean()`. With `adjust=False` pandas uses exactly the formula above. A common alternative is `span`: α = 2 / (span + 1). So span = 9 gives α = 0.2.

```widget
{"name": "ses-alpha", "params": {"alpha": 0.4}}
```

```check
{"q": "EWMA with alpha = 0.5. S(t−1) = 20 and y(t) = 30. What is S(t)?", "type": "numeric", "answer": 25, "tol": 0.0001,
 "why": "S(t) = 0.5 · 30 + 0.5 · 20 = 25."}
```

```check
{"q": "You want an EWMA that reacts slowly and is very smooth. Which alpha?", "type": "single",
 "options": ["0.05", "0.9", "1.0"], "answer": 0,
 "why": ["Correct. Small alpha gives a small weight to the newest value.", "0.9 follows the newest value almost exactly.", "alpha = 1 copies the data; there is no smoothing."]}
```

## Why EWMA works: the weights

Unroll the formula. The weight of the value k steps ago is α · (1 − α)^k.

With α = 0.4 the weights are 0.4, 0.24, 0.144, 0.086, ... They shrink by the factor 0.6 each step and add up to 1. Old data fades out but is never fully cut.

An EWMA is trailing by construction: S(t) uses only y(t) and the past. It is safe for features, and it is the base of **simple exponential smoothing**, which you meet in Stage 3.

## Worked example

Task: daily sales with a sudden jump. Build a leak-free feature "recent level" for each day and check it against a centered average.

```python
import numpy as np
import pandas as pd

y = pd.Series([10.0] * 6 + [20.0] * 6, index=pd.date_range("2024-01-01", periods=12, freq="D"))

trailing = y.rolling(3).mean()                       # includes today
feature = y.shift(1).rolling(3).mean()               # ends yesterday: safe as input for today
centered = y.rolling(3, center=True).mean()          # sees tomorrow: only for description
ewma = y.shift(1).ewm(alpha=0.5, adjust=False).mean()   # EWMA of the past only

out = pd.DataFrame({"y": y, "trailing": trailing, "feature": feature, "centered": centered, "ewma_prev": ewma})
print(out.round(2).iloc[3:9])
# On day 7 the jump happens. The safe feature still says "10"; the centered one already moved on day 6.
# Output:
#                y  trailing  feature  centered  ewma_prev
# 2024-01-04  10.0     10.00    10.00     10.00       10.0
# 2024-01-05  10.0     10.00    10.00     10.00       10.0
# 2024-01-06  10.0     10.00    10.00     13.33       10.0
# 2024-01-07  20.0     13.33    10.00     16.67       10.0
# 2024-01-08  20.0     16.67    13.33     20.00       15.0
# 2024-01-09  20.0     20.00    16.67     20.00       17.5
```

Look at 6 January (the 6th row) and 7 January. The centered value rises on 6 January, one day before the jump. That is leakage. The `feature` column stays at 10 on 7 January. It is blind to the new level. This is the honest situation of a forecaster.

## Common mistakes

- Using `center=True` to make features for a forecast model.
- Using a rolling mean that includes today's value when today is the target.
- Taking a window larger than the data, which gives only NaN.
- Using `adjust=True` (the pandas default) and then comparing with the plain formula. The first values differ.
- Choosing alpha or the window size by looking at the test period.

## Interview lens

**Typical question:** "Create a 7-day rolling mean feature for a demand model. What can go wrong?"

**Strong answer:** The window must not contain the day we predict. So I shift the series by one day and then take the rolling mean: `s.shift(1).rolling(7).mean()`. I never use `center=True` for features, because it looks into the future. The first seven rows are NaN. I keep them as NaN or use `min_periods` on purpose. If recent days matter more, I use an EWMA, with `adjust=False`. I choose the window size by validation on past data, not on the test set.

**Red flags:**
- `rolling(7).mean()` on the target series, used as a feature of the same day.
- `center=True` in a feature pipeline.
- No idea how the first rows behave.

## Real world

- The moving average is one of the oldest tools for smoothing economic data. Statistical agencies still publish smoothed series.
- EWMA is also used in monitoring: control charts based on exponentially weighted averages detect small shifts in a process.
- Exponential smoothing methods (Stage 3) are strong baselines in public forecasting competitions such as M4.

## Key points

- A trailing rolling window uses today and the past. A centered window also uses the future, so it leaks.
- For features: `s.shift(1).rolling(k).<stat>()` keeps today out of the window.
- EWMA: S(t) = α·y(t) + (1 − α)·S(t−1). Big alpha reacts fast, small alpha is smooth. In pandas use `ewm(alpha=..., adjust=False)`.
- Smoothing always has a delay or a leak. Choose on purpose.
