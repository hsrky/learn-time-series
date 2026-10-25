---
id: s5-02-lag-and-rolling-features
title: Lag and rolling features without leakage
minutes: 30
level: intermediate
goals: [Build lag features with shift, Build rolling and expanding statistics that are shifted so they do not leak, Choose lags that are allowed for the forecast horizon]
prereqs: [s5-01-reduction-to-supervised]
tags: [features, lags, rolling, leakage, pandas]
skills: [leakage, pandas-fluency]
---
## Warm-up
```check
{"q": "A series has 30 points. Window 5, horizon 1. How many rows does the table have?", "type": "numeric",
 "answer": 25, "tol": 0.001,
 "why": "30 - 5 - 1 + 1 = 25."}
```

```check
{"q": "In a window table, every feature must be ... than every target in the same row.", "type": "single",
 "options": ["older", "newer", "larger"],
 "answer": 0,
 "why": ["Correct: features come from the past, the target from the future.", "Newer features would leak the future.", "Size has nothing to do with time order."]}
```

## Why it matters
Features are the most important part of a machine learning forecast. Simple lag and rolling features often beat complex models. But they are also the easiest place to leak the future. One missing `.shift(1)` can make a model look perfect in testing and fail in production. This lesson shows the safe way.

## Lag features
A **[[lag]]** feature is the value of the series some steps ago.

- `lag_1` = yesterday's value (for daily data).
- `lag_7` = the value 7 days ago, the same weekday last week.

In pandas: `s.shift(k)` moves the values down by `k` rows. The first `k` rows become `NaN`.

Example: `s = 10, 12, 11, 13`. Then `s.shift(1) = NaN, 10, 12, 11`. At the third row (value 11), `lag_1` is 12.

```widget
{"name": "lag-features", "params": {}}
```

```check
{"q": "s = 5, 8, 6, 9. What is s.shift(2) at the last row?", "type": "numeric",
 "answer": 8, "tol": 0.001,
 "why": "shift(2) moves each value down by 2 rows: NaN, NaN, 5, 8. The last row has 8."}
```

## Rolling statistics must be shifted
A **[[rolling statistic|rolling]]** statistic summarizes the last `w` values, for example the 7-day mean. In pandas, `s.rolling(7).mean()` at row `t` uses rows `t−6 … t`. It **includes today's value**. If today's value is your target, the feature contains the answer. This is a leak.

Safe version: `s.shift(1).rolling(7).mean()`. At row `t` it uses rows `t−7 … t−1`.

Example: `s = 10, 12, 11, 13, 15`.

- `s.rolling(3).mean()` at the last row = (11 + 13 + 15) / 3 = **13.0**. Contains 15 (leak).
- `s.shift(1).rolling(3).mean()` at the last row = (12 + 11 + 13) / 3 = **12.0**. Safe.

```check
{"q": "You predict y at time t. Which feature is safe?", "type": "single",
 "options": ["y.rolling(7).mean()", "y.shift(1).rolling(7).mean()", "y.rolling(7, center=True).mean()"],
 "answer": 1,
 "why": ["At time t it includes y(t), the target.", "Correct: the shift removes today's value before the rolling window.", "A centered window uses future values, which is a double leak."]}
```

## Expanding statistics and differences
An **[[expanding statistic|expanding]]** statistic uses all values from the start up to now. Example: the average of everything seen so far. Again, shift first: `s.shift(1).expanding().mean()`.

You can also build features from lags:

- Change: `lag_1 − lag_2` (is the series going up?).
- Ratio: `lag_1 / lag_8` (this week compared with last week).
- Rolling spread: `s.shift(1).rolling(7).std()` (how noisy is it lately?).
- Rolling min and max.

```check
{"q": "s = 10, 12, 11, 13, 15. What is s.shift(1).expanding().mean() at the last row?", "type": "numeric",
 "answer": 11.5, "tol": 0.001,
 "why": "After the shift, the last row sees 10, 12, 11, 13. Their mean is 46 / 4 = 11.5."}
```

## Which lags are allowed? The horizon rule
Your model predicts `h` steps ahead. A feature must be known at the **forecast origin**, `h` steps before the target.

- A **recursive** one-step model needs lags ≥ 1. For step 2 it uses its own prediction as lag 1.
- A **direct** model for horizon `h` can only use lags ≥ `h`. Otherwise it needs values that will not exist yet.

Example: predict the value of day t + 7 at day t. `lag_1` of the target day is the value of day t + 6. That is in the future at day t. So with a 7-day-ahead direct model, define lags relative to the **origin** (value at t, t − 1, ...). A common rule: lag ≥ horizon (in target-relative terms).

```check
{"q": "You make a 7-day-ahead forecast. Counting lags back from the TARGET day, which lag is NOT allowed?", "type": "single",
 "options": ["lag 7", "lag 14", "lag 3"],
 "answer": 2,
 "why": ["Lag 7 from the target is the origin day. It is known.", "Lag 14 is even older. It is known.", "Correct: lag 3 from the target day is 4 days after the origin. It is not known yet."]}
```

## Worked example
We build features for a short daily series and show that shifted features do not change when today's target changes.

```python
import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=12, freq="D")
s = pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19, 21, 20], index=idx, dtype=float)

def make_features(s):
    f = pd.DataFrame({"y": s})
    f["lag_1"] = s.shift(1)                         # yesterday
    f["lag_7"] = s.shift(7)                         # same weekday last week
    f["roll3_safe"] = s.shift(1).rolling(3).mean()  # shift first, then roll
    f["roll3_leaky"] = s.rolling(3).mean()          # includes today: leak!
    f["exp_mean"] = s.shift(1).expanding().mean()   # all past values
    return f

f = make_features(s)
print(f.tail(3).round(2))

# Leak check: change ONLY the last target and see which features move.
s2 = s.copy()
s2.iloc[-1] = 1000.0
g = make_features(s2)
for col in ["lag_1", "lag_7", "roll3_safe", "roll3_leaky", "exp_mean"]:
    same = bool(np.isclose(f[col].iloc[-1], g[col].iloc[-1]))
    print(col, "unchanged" if same else "CHANGED (leak)")
# Output:
#                y  lag_1  lag_7  roll3_safe  roll3_leaky  exp_mean
# 2024-01-10  19.0   17.0   11.0        17.0         18.0     14.00
# 2024-01-11  21.0   19.0   13.0        18.0         19.0     14.50
# 2024-01-12  20.0   21.0   15.0        19.0         20.0     15.09
# lag_1 unchanged
# lag_7 unchanged
# roll3_safe unchanged
# roll3_leaky CHANGED (leak)
# exp_mean unchanged
```

A safe feature does not depend on today's target. `roll3_leaky` moves when we change today's value, so the model could read the answer from it.

## Common mistakes
- `rolling(...)` without `shift(1)` before it.
- Centered windows (`center=True`) in a forecasting feature.
- `fillna` with the global mean or backfill (`bfill`), which uses future values.
- Computing features on the whole table of many series without `groupby`. Lags then mix neighbour series.
- Using lags that are shorter than the horizon in a direct model.
- Keeping the first rows with `NaN` features without a plan. Drop them or let the model handle them.

## Interview lens
**Typical question:** "Build features for a demand model. How do you avoid leakage?"

**Strong answer:** I use lags such as 1, 7 and 14 days, plus rolling mean and standard deviation. I always shift by one step before the rolling window, so a row never sees its own target. For multi-series data I use `groupby(series_id)` so lags do not cross series. I check the horizon: with a direct model for horizon `h`, only information available at the origin may be used. Finally I run a test. I change the target of the last row. The features of that row must not change.

**Red flags:**
- `df['y'].rolling(7).mean()` as a feature.
- `center=True`.
- `bfill` of missing values.
- Lags computed over a table with several series and no group.

## Real world
- Lag and rolling features are the core of the top M5 solutions (Walmart sales), usually with gradient boosting.
- The Nixtla library `mlforecast` builds lag and rolling features and keeps them correct for recursive forecasting.
- The pandas docs state that `rolling` windows are trailing by default and include the current row. This is why the shift is needed.

## Key points
- `s.shift(k)` gives lag `k`. Always check that lags are at least the horizon in a direct model.
- Rolling and expanding statistics must be built on `s.shift(1)` so that the current target is not inside.
- Features for many series must be computed per series (`groupby`).
- Never use centered windows, backfill or global statistics in features.
- Test for leaks: change today's target and check that today's features stay the same.
