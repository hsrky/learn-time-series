---
id: s1-04-missing-data-imputation
title: Missing data, irregular timestamps and imputation
minutes: 30
level: beginner
goals: [Tell a missing row from a missing value, Fill gaps with ffill or interpolation, Explain why interpolation can leak the future, Put an irregular series on a regular grid]
prereqs: [s1-03-frequency-resampling]
tags: [missing, imputation, interpolation, leakage, irregular]
skills: [leakage, pandas-fluency]
---
## Warm-up

```check
{"q": "Hourly warehouse stock (units on the shelf) becomes daily data. Which aggregation?", "type": "single",
 "options": ["last", "sum", "mean of sums"], "answer": 0,
 "why": ["Correct. Stock is a state, so use the end-of-day value.", "Summing counts the same boxes many times.", "That is not a standard rule."]}
```

```check
{"q": "Which fill uses only past values after you upsample?", "type": "single",
 "options": ["ffill", "bfill", "interpolate"], "answer": 0,
 "why": ["Correct.", "bfill takes the next value, from the future.", "interpolate needs the next known point."]}
```

## Why it matters

Real data has holes. A sensor loses power. A shop closes on a holiday. A database job fails for one night.

Models cannot read NaN, and many pandas functions break or give wrong answers on gaps. So you must fill the holes, or flag them.

But the way you fill matters. A fill that looks at tomorrow's value makes your model look smart in tests. In real life, tomorrow is not known yet. This is a very common mistake.

## Two kinds of "missing"

1. **Missing value:** the row exists, but the value is `NaN`. Example: `2024-01-03, NaN`.
2. **Missing row (missing timestamp):** the row does not exist. Example: no row for 3 January at all.

A missing row is harder to see. Functions such as `shift(1)` then take the previous *row*, which may be two days ago. You must put the series on a full grid first.

Also watch for **hidden missing values**: codes like `-999`, `0` or `"N/A"` that stand for "unknown". Replace them with NaN first.

Ask also **why** it is missing. No sales on a Sunday can mean 0 (shop closed, true zero). A broken sensor means unknown. These need different fills.

```python
import numpy as np
import pandas as pd

dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-05", "2024-01-06"])
s = pd.Series([10.0, -999.0, 14.0, 15.0], index=dates)

s = s.replace(-999.0, np.nan)                            # hidden missing value -> NaN
print(s.shift(1).tolist())                               # shift on 4 rows: 5 Jan gets the value of 2 Jan (wrong!)

full = s.reindex(pd.date_range("2024-01-01", "2024-01-06", freq="D"))   # add missing rows
print(full.tolist())
print(full.shift(1).tolist())                            # now shift means "yesterday"
# Output:
# [nan, 10.0, nan, 14.0]
# [10.0, nan, nan, nan, 14.0, 15.0]
# [nan, 10.0, nan, nan, nan, 14.0]
```

```check
{"q": "A temperature log uses -999 when the sensor fails. What do you do first?", "type": "single",
 "options": ["Replace -999 by NaN", "Take the mean including -999", "Leave it; models handle it"], "answer": 0,
 "why": ["Correct. A code that means unknown must become a real missing value.", "-999 would pull the mean far down.", "A model sees -999 as a real temperature."]}
```

## Simple ways to fill

Four common fills:

| Method | Rule | Uses the future? |
|---|---|---|
| Constant | Fill with 0 or a typical value | No (if constant is fixed) |
| `ffill` | Copy the last known value | No |
| Mean | Fill with the mean | Yes, if the mean is over all data |
| `interpolate` | Draw a straight line between neighbors | **Yes** |

[[linear interpolation]] fills a gap with a straight line. The line goes from the value before the gap (y₀ at time t₀) to the value after it (y₁ at time t₁):

y(t) = y₀ + (y₁ − y₀) · (t − t₀) / (t₁ − t₀)

- y₀, y₁: the known values before and after the gap.
- t₀, t₁: their times. t is the time to fill.

Example: y₀ = 10 at day 0, y₁ = 16 at day 3. At day 1: 10 + 6 · (1/3) = 12. At day 2: 14.

```chart
{"title": "Filling a gap of two days", "x": "day", "height": 210,
 "series": [{"name": "ffill (past only)", "x": [0,1,2,3,4], "y": [10,10,10,16,17]},
            {"name": "interpolate (needs day 3)", "x": [0,1,2,3,4], "y": [10,12,14,16,17], "dash": true}],
 "caption": "Days 1 and 2 are missing. ffill copies 10. Interpolation draws the line to the value of day 3, so it needs data from the future."}
```

```check
{"q": "y = 10 on day 0 and y = 16 on day 3. What does linear interpolation give for day 2?", "type": "numeric", "answer": 14, "tol": 0.0001,
 "why": "10 + (16 − 10) · (2/3) = 10 + 4 = 14."}
```

## The leakage trap

[[data leakage]] means your model uses information that it would not have at prediction time.

Suppose a sensor misses day 5. You interpolate it using day 4 **and day 6**. Later you build a feature for day 5 from this filled value. The feature contains day 6, which is in the future of day 5.

Rules for forecasting:

1. If the filled value is used as an **input at time t**, fill it using only data up to time t. Use `ffill`, optionally with `limit`.
2. If you compute a mean or other statistic to fill, compute it on the **training period only**.
3. If you only describe the past (a report, a plot), interpolation is fine.
4. Keep a flag column `was_missing` (0 or 1). The model can learn that those values are less reliable.

Same problem: `bfill`, a centered rolling mean, and `fillna(s.mean())` over the whole series.

```check
{"q": "You fill gaps with s.interpolate() and then build lag features for a model that predicts the next day. What is the risk?", "type": "single",
 "options": ["Filled values contain information from later days (leakage)", "None; interpolate is always safe", "The series becomes shorter"], "answer": 0,
 "why": ["Correct. A value inside a gap is built from the value after the gap.", "It is safe for describing history, not for building inputs of a forecast.", "interpolate keeps the same length."]}
```

## Irregular timestamps

If events arrive at random times, you have an [[irregular time series]]. There are three usual ways to use it:

- **Aggregate to a grid:** count or average per hour or day (`resample`). This is the most common way.
- **Interpolate by time:** `interpolate(method="time")` weights by the real distance between points, not by row count.
- **Use "as of" joins:** `pd.merge_asof` attaches to each event the latest known value *before* it. It is the safe way to join slow data to fast data.

After you build the grid, decide: is an empty bucket **zero** (no events happened) or **missing** (we could not observe)? For counts of sales, empty means 0. For temperature, empty means missing.

## Worked example

Task: a daily sales series has one missing row and one NaN. Put it on a full grid, fill it in a leak-free way, and keep a flag.

```python
import numpy as np
import pandas as pd

dates = pd.to_datetime(["2024-03-01", "2024-03-02", "2024-03-04", "2024-03-05", "2024-03-06"])
s = pd.Series([20.0, 22.0, np.nan, 26.0, 27.0], index=dates)   # 3 March row is missing; 4 March is NaN

# 1) Full daily grid: missing rows become NaN rows
grid = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))

# 2) Flag which values were not observed
was_missing = grid.isna().astype(int)

# 3) Past-only fill (safe for forecasting), at most 1 step
causal = grid.ffill(limit=1)

# 4) Linear interpolation (uses future: only for description)
smooth = grid.interpolate()

print(pd.DataFrame({"raw": grid, "flag": was_missing, "ffill1": causal, "interp": smooth}))
# Output:
#              raw  flag  ffill1     interp
# 2024-03-01  20.0     0    20.0  20.000000
# 2024-03-02  22.0     0    22.0  22.000000
# 2024-03-03   NaN     1    22.0  23.333333
# 2024-03-04   NaN     1     NaN  24.666667
# 2024-03-05  26.0     0    26.0  26.000000
# 2024-03-06  27.0     0    27.0  27.000000
```

Notice: `ffill(limit=1)` fills 3 March but leaves 4 March as NaN, because it is the second missing day in a row. Interpolation fills both with values that depend on 5 March.

## Common mistakes

- Using `interpolate`, `bfill` or a full-series mean to build features for a forecast model.
- Filling holes before you reindex to a full grid. Missing rows stay invisible.
- Treating `-999` or `0` as real values.
- Filling every gap with 0 when the true meaning is "unknown".
- Hiding how many values you filled. Always report the share of filled points.

## Interview lens

**Typical question:** "Your hourly sensor data has gaps. How do you handle them before you train a forecast model?"

**Strong answer:** I first ask why values are missing, and I count them: missing rows and NaN values. I reindex to a full hourly grid, so that lags mean the same time distance for every row. For inputs, I use forward fill with a limit, so only the past is used. Long gaps stay NaN, or I use a model that accepts NaN. I add a missing-flag feature. I never fill with future information, and I compute any fill statistic on the training period only.

**Red flags:**
- `df.interpolate()` on the whole dataset before splitting.
- Dropping rows with `dropna()` and leaving holes in the time grid.
- Not telling how much data was filled.

## Real world

- Many forecasting libraries expect a full regular calendar for each series. Teams add the missing dates first.
- Gradient boosting libraries such as LightGBM and XGBoost accept NaN directly in features. So sometimes the best fill is no fill, plus a flag.

## Key points

- Two kinds of missing: a NaN value, and a missing row. Reindex to a full grid to see both.
- Replace codes like -999 with NaN. Decide if empty means zero or unknown.
- `ffill` uses the past only. `interpolate`, `bfill` and a global mean use the future.
- For forecasting inputs: fill causally, compute statistics on training data only, and add a missing flag.
