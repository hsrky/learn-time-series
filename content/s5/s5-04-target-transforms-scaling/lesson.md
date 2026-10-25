---
id: s5-04-target-transforms-scaling
title: Target transforms and per-series scaling
minutes: 25
level: intermediate
goals: [Use log1p and standardization on the target, Fit the scaler on training data only for each series, Invert the forecast back to the original units]
prereqs: [s5-03-calendar-holidays-target-encoding]
tags: [scaling, log, standardization, inverse-transform]
skills: [leakage, from-scratch]
---
## Warm-up
```check
{"q": "You standardize a feature. Which data must give the mean and the standard deviation?", "type": "single",
 "options": ["All rows", "Training rows only", "Test rows only"],
 "answer": 1,
 "why": ["All rows include the test period, which leaks.", "Correct: fit on training data, then apply to the test data.", "Test rows must stay hidden."]}
```

```check
{"q": "Safe encoding of a category for row t uses ...", "type": "single",
 "options": ["the mean of all rows", "the mean of earlier rows only", "the mean of later rows"],
 "answer": 1,
 "why": ["That includes the row's own target and the future.", "Correct: only earlier rows.", "Later rows are the future."]}
```

## Why it matters
Machine learning models like numbers in a similar range. Real series are not like that. One shop sells 5 items per day. Another sells 5,000. Sales often grow by percent, not by a fixed amount, so the noise grows with the level. A model trained on raw values spends all its effort on the big series. **Transforming the target** and **scaling each series** makes the problem easier. But we must always be able to go back to the original units ([[inverse transform]]), and the scaler must never see the test period.

## Log transform: log1p
The logarithm turns growth by percent into growth by a fixed amount, and makes large values closer together.

Use `log1p(y) = ln(1 + y)` (the [[log1p]] transform). The "1 +" lets zeros work, because `log(0)` is undefined but `log1p(0) = 0`. The inverse is `expm1(z) = e^z − 1`.

Example: sales 0, 9, 99, 999 → `log1p` = 0, 2.30, 4.61, 6.91. The gaps become almost equal.

Use it when values are zero or positive, and the spread grows with the level. Do **not** use it for values that can be negative (such as profit).

```chart
{"title": "Growth by percent: raw series and its log1p", "x": "t", "height": 220, "series": [{"name": "raw sales", "y": [5.0, 5.42, 5.87, 6.36, 6.89, 7.46, 8.08, 8.75, 9.48, 10.27, 11.13, 12.05, 13.06, 14.15, 15.32, 16.6, 17.98, 19.48, 21.1, 22.86, 24.77, 26.83, 29.06, 31.48, 34.1, 36.95, 40.02, 43.36, 46.97, 50.88, 55.12, 59.71, 64.68, 70.07, 75.9, 82.22, 89.07, 96.49, 104.53, 113.23]}, {"name": "log1p(sales), times 10", "y": [17.92, 18.59, 19.27, 19.96, 20.66, 21.35, 22.06, 22.77, 23.49, 24.22, 24.96, 25.69, 26.43, 27.18, 27.92, 28.68, 29.43, 30.19, 30.96, 31.72, 32.49, 33.26, 34.03, 34.81, 35.58, 36.36, 37.14, 37.92, 38.71, 39.49, 40.27, 41.06, 41.85, 42.64, 43.43, 44.21, 45.01, 45.8, 46.59, 47.38], "dash": true}], "caption": "The raw series bends upward. The log1p curve (scaled by 10 to share the axis) is almost a straight line."}
```

```check
{"q": "What is expm1(log1p(7))?", "type": "numeric",
 "answer": 7, "tol": 0.001,
 "why": "expm1 is the inverse of log1p, so we get back 7."}
```

## Standardize per series
**[[standardization|Standardization]]** gives a series mean 0 and standard deviation 1: `z = (y − μ) / σ`.

- `y` is a value of one series.
- `μ` (mu) is the mean of that series' **training** values.
- `σ` (sigma) is their standard deviation.

Do this **for each series** separately. Then a model trained on many series sees values in the same range. After the forecast, undo it: `y = z × σ + μ`.

Example: training values 10, 12, 14. μ = 12, σ = 1.63. The value 20 becomes (20 − 12) / 1.63 = 4.9. A forecast z = 0 means "the mean of the training data", which is 12.

Other scalers: mean scaling (`y / mean(|y|)`, used by Chronos and many deep models), min-max, robust scaling (median and interquartile range, good against spikes). The rule is the same: statistics from the training part only.

```check
{"q": "Train: μ = 100, σ = 20. The model predicts z = 1.5. What is the forecast in original units?", "type": "numeric",
 "answer": 130, "tol": 0.001,
 "why": "y = z × σ + μ = 1.5 × 20 + 100 = 130."}
```

## Order of steps and back-transform
When you combine transforms, undo them in the **reverse order**.

1. Forward: `log1p` first, then standardize with training statistics.
2. Train the model on the transformed target.
3. Inverse: de-standardize (`z σ + μ`), then `expm1`.

Details that matter:

- The back-transform of a log-model forecast gives roughly the **median**, not the mean. The mean of a skewed distribution is larger. For the mean you can add a correction, or use a loss that fits.
- After `expm1`, a count cannot be negative. Clip at 0: `np.maximum(pred, 0)`.
- Compute metrics in original units (or scale-free metrics), not only in log space.
- Save μ and σ of every series with the model. In production you need them again.

```check
{"q": "You trained with z = (log1p(y) − μ) / σ. What is the correct inverse for a prediction z?", "type": "single",
 "options": ["expm1(z × σ + μ)", "expm1(z) × σ + μ", "(expm1(z) − μ) / σ"],
 "answer": 0,
 "why": ["Correct: undo standardization first, then undo the log.", "This applies the inverse steps in the wrong order.", "This is a forward-like formula, not an inverse."]}
```

## Worked example
A series grows by about 2.7 times per step (like `e^t`). We fit a straight line on the raw values and on the log1p values, forecast the next 2 steps, and compare.

```python
import numpy as np

y = np.round(np.exp(np.arange(8))).astype(float)   # 1, 3, 7, 20, 55, 148, 403, 1097
train, test = y[:6], y[6:]
t_train, t_test = np.arange(6), np.arange(6, 8)

# (a) line on raw values
a = np.polyfit(t_train, train, 1)
pred_raw = np.polyval(a, t_test)

# (b) log1p, standardize with TRAIN statistics, fit a line, then invert
z = np.log1p(train)
mu, sd = z.mean(), z.std()
zs = (z - mu) / sd
b = np.polyfit(t_train, zs, 1)
pred_z = np.polyval(b, t_test)
pred_log = np.maximum(np.expm1(pred_z * sd + mu), 0)   # reverse order, clip at 0

print("test        :", test)
print("raw line    :", pred_raw.round(0))
print("log1p line  :", pred_log.round(0))
print("MAE raw line:", round(np.abs(test - pred_raw).mean(), 1))
print("MAE log line:", round(np.abs(test - pred_log).mean(), 1))
# Output:
# test        : [ 403. 1097.]
# raw line    : [129. 155.]
# log1p line  : [313. 748.]
# MAE raw line: 607.7
# MAE log line: 219.6
```

The straight line in raw space cannot follow the growth, so it under-predicts a lot. In log space the growth is closer to a line, so the same simple model works much better (MAE 220 against 608), although it still under-predicts. Note that `mu` and `sd` came from the training part only.

## Common mistakes
- Computing mean and standard deviation on all data, including the test period.
- Using one global scaler for series with very different levels.
- Forgetting to invert the transform before computing the business metric.
- Applying `np.log` to data with zeros.
- Inverting in the wrong order.
- Not clipping impossible values (negative counts) after the inverse.
- Dividing by a standard deviation of zero for a constant series.

## Interview lens
**Typical question:** "You train one model on 10,000 series with very different scales. What do you do?"

**Strong answer:** I scale each series separately. I use log1p if the series are non-negative and the noise grows with the level. Then I standardize each series with the mean and standard deviation of its training window. I fit those on training data only, and I store them so I can invert the forecast. I handle constant series by setting the standard deviation to 1. I clip negative forecasts for counts, and I compute metrics in original units or with scale-free metrics like MASE.

**Red flags:** one global scaler; scaling before the split; forgetting the inverse transform; using `log` on zeros; explaining the log transform as "it makes the data normal" without mentioning growth and variance.

## Real world
- Chronos (Amazon, 2024) scales each input series by the mean of its absolute values before converting it to tokens.
- DeepAR (Amazon) also divides each series by a scale factor based on its average. This lets one network learn from series of very different size.
- RevIN (reversible instance normalization), used with deep models, applies the same idea inside the network: normalize each input window and undo it at the output.

## Key points
- `log1p` turns percent growth into a fixed step and handles zeros; the inverse is `expm1`.
- Standardize each series with its own training mean and standard deviation.
- Never fit scalers on test data. Store them with the model.
- Invert in reverse order, clip impossible values, and evaluate in original units.
- A log-model forecast is closer to the median than to the mean.
