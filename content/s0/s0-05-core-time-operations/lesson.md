---
id: s0-05-core-time-operations
title: shift, diff, rolling, resample and groupby
minutes: 30
level: beginner
goals: [Move values in time with shift and diff, Compute trailing rolling statistics, Change frequency with resample, Summarize by group with groupby]
prereqs: [s0-04-datetime-timezones]
tags: [pandas, shift, diff, rolling, resample, groupby]
skills: [pandas-fluency, leakage]
---
## Warm-up

```check
{"q": "Naive log times were written in UTC. You want New York time. Which calls, in order?", "type": "single",
 "options": ["tz_localize('UTC') then tz_convert('America/New_York')", "tz_convert('UTC') then tz_localize('America/New_York')", "tz_localize('America/New_York') only"], "answer": 0,
 "why": ["Correct. Label first, then change the clock.", "tz_convert needs aware data, so it fails on naive data.", "That claims the numbers are already New York time."]}
```

```check
{"q": "What does s['2024-03'] return for a Series with a DatetimeIndex?", "type": "single",
 "options": ["All rows in March 2024", "Only 1 March 2024", "An error"], "answer": 0,
 "why": ["Correct. Partial date text selects the whole month.", "You would need '2024-03-01' for one day.", "It works on a DatetimeIndex."]}
```

## Why it matters

Five operations do most of the work in time series code: **shift, diff, rolling, resample, groupby**.

Most forecasting features are built from them. Examples: "sales yesterday", "change since last week", "average of the last 7 days", "weekly total".

They also hide the most common bug in this field: using information from the future. In each chunk below, we ask: *which rows does this value use?*

## shift and diff

`s.shift(1)` moves every value **one step later** in time. The value at day t becomes the value of day t−1. The first row has no past, so it is NaN.

`s.diff()` is `s - s.shift(1)`. It is the change since the previous row.

`s.pct_change()` is the change divided by the previous value. It is the growth rate.

```python
import pandas as pd

s = pd.Series([100, 110, 99, 120], index=pd.date_range("2024-01-01", periods=4, freq="D"))
df = pd.DataFrame({"sales": s})
df["yesterday"] = s.shift(1)        # past value: safe to use as a feature
df["change"] = s.diff()             # today minus yesterday
df["growth"] = s.pct_change()       # (today - yesterday) / yesterday
df["tomorrow"] = s.shift(-1)        # FUTURE value: only for building a target, never a feature
print(df)
# Output:
#             sales  yesterday  change    growth  tomorrow
# 2024-01-01    100        NaN     NaN       NaN     110.0
# 2024-01-02    110      100.0    10.0  0.100000      99.0
# 2024-01-03     99      110.0   -11.0 -0.100000     120.0
# 2024-01-04    120       99.0    21.0  0.212121       NaN
```

```check
{"q": "s = [100, 110, 99]. What is s.diff() at the third row?", "type": "numeric", "answer": -11, "tol": 0,
 "why": "The third value is 99 and the previous value is 110. 99 − 110 = −11."}
```

## rolling windows

A [[rolling window]] looks at the last k rows and computes one number, such as the mean. The window moves forward one row at a time.

`s.rolling(7).mean()` is the 7-day [[moving average]]. The first 6 rows are NaN because 7 values are not yet available. Use `min_periods=1` if you want a value anyway.

This window is **trailing**: it uses today and the 6 days before. It uses no future data, so it is safe.

```widget
{"name": "moving-average", "params": {"window": 7}}
```

```chart
{"title": "Daily sales and the 7-day rolling mean", "x": "day", "height": 230,
 "series": [
  {"name": "daily", "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
   "y": [10, 13, 13, 16, 24, 35, 31, 17, 20, 20, 23, 31, 42, 38, 24, 27, 27, 30, 38, 49, 45, 31, 34, 34, 37, 45, 56, 52]},
  {"name": "7-day mean", "x": [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
   "y": [20.3, 21.3, 22.3, 23.3, 24.3, 25.3, 26.3, 27.3, 28.3, 29.3, 30.3, 31.3, 32.3, 33.3, 34.3, 35.3, 36.3, 37.3, 38.3, 39.3, 40.3, 41.3]}],
 "caption": "The rolling mean removes the weekly zig-zag and shows the slow rise. It starts on day 7."}
```

```check
{"q": "s.rolling(3).mean() on [3, 6, 9, 12]. What is the value at the last row?", "type": "numeric", "answer": 9, "tol": 0,
 "why": "The last window is [6, 9, 12]. The mean is (6 + 9 + 12) / 3 = 9."}
```

## resample

`s.resample("W").sum()` changes the frequency. It needs a DatetimeIndex. Here daily data becomes weekly data.

You must choose how to combine the values inside each new period. Use `sum` for totals, `mean` for levels, and `last` for stocks and balances.

Compare with rolling: rolling keeps **one row per original row**. Resample makes **one row per new period**, so the series gets shorter.

```python
import pandas as pd

pat = [10, 12, 11, 13, 20, 30, 25]                       # a weekly pattern
vals = [pat[i % 7] + i for i in range(28)]               # plus a slow rise
s = pd.Series(vals, index=pd.date_range("2024-01-01", periods=28, freq="D"))   # starts on a Monday

weekly = s.resample("W").sum()      # "W" = weeks ending on Sunday
print(weekly)
print(len(s), "->", len(weekly))
# Output:
# 2024-01-07    142
# 2024-01-14    191
# 2024-01-21    240
# 2024-01-28    289
# Freq: W-SUN, dtype: int64
# 28 -> 4
```

```check
{"q": "You have hourly electricity use in kWh. You need the total per day. Which call?", "type": "single",
 "options": ["s.resample('D').sum()", "s.resample('D').mean()", "s.rolling(24).sum()"], "answer": 0,
 "why": ["Correct. Energy used in a day is the sum of its hours.", "The mean is the average hour, not the daily total.", "Rolling keeps one row per hour; it does not make daily rows."]}
```

## groupby

`groupby` splits rows into groups, computes a number for each group, and joins the results.

It does not need time. You can group by store, by day of week, by hour of day. For a **seasonal profile** group by a calendar part of the index.

Resample groups by consecutive time periods. Groupby by calendar part groups rows that are far apart in time, such as all Mondays.

```python
import pandas as pd

pat = [10, 12, 11, 13, 20, 30, 25]
vals = [pat[i % 7] + i for i in range(28)]
s = pd.Series(vals, index=pd.date_range("2024-01-01", periods=28, freq="D"))

by_weekday = s.groupby(s.index.dayofweek).mean()    # 0 = Monday ... 6 = Sunday
print(by_weekday)

# A DataFrame example: total per store
df = pd.DataFrame({"store": ["A", "B", "A", "B"], "units": [5, 3, 7, 1]})
print(df.groupby("store")["units"].sum())
# Output:
# 0    20.5
# 1    23.5
# 2    23.5
# 3    26.5
# 4    34.5
# 5    45.5
# 6    41.5
# dtype: float64
# store
# A    12
# B     4
# Name: units, dtype: int64
```

```check
{"q": "You want the average sales for each hour of the day (0 to 23) over many days. Which call?", "type": "single",
 "options": ["s.groupby(s.index.hour).mean()", "s.resample('h').mean()", "s.rolling(24).mean()"], "answer": 0,
 "why": ["Correct. It groups all rows with the same hour, from every day.", "That keeps every hour of every day as its own period.", "That gives a moving average, not one value per hour of day."]}
```

## Worked example

Task: 28 days of sales. Build three things. (1) A safe feature: "average of the last 3 days before today". (2) The weekly totals. (3) The average per weekday.

```python
import pandas as pd

pat = [10, 12, 11, 13, 20, 30, 25]
vals = [pat[i % 7] + i for i in range(28)]
s = pd.Series(vals, index=pd.date_range("2024-01-01", periods=28, freq="D"), name="sales")

# 1) Feature for day t: mean of days t-3, t-2, t-1  (NOT including day t)
#    rolling(3).mean() includes today, so we shift by one step.
past3 = s.rolling(3).mean().shift(1)
print(past3.head(5))

# 2) Weekly totals (weeks end on Sunday)
print(s.resample("W").sum().tolist())

# 3) Average per weekday: the weekly shape (Monday first)
profile = s.groupby(s.index.dayofweek).mean()
print(profile.round(1).tolist())
# Output:
# 2024-01-01     NaN
# 2024-01-02     NaN
# 2024-01-03     NaN
# 2024-01-04    12.0
# 2024-01-05    14.0
# Freq: D, Name: sales, dtype: float64
# [142, 191, 240, 289]
# [20.5, 23.5, 23.5, 26.5, 34.5, 45.5, 41.5]
```

Why shift after rolling? `rolling(3).mean()` at day t uses days t−2, t−1 and t. Day t is the value we want to predict. If we keep it, the feature contains the answer. This is [[data leakage]]. `shift(1)` removes today.

## Common mistakes

- Using `rolling(k).mean()` as a feature for the same day without `shift(1)`. The target is inside the feature.
- Using `shift(-1)` as a feature. That is the future.
- Using `resample().mean()` when you need a total.
- Forgetting that `diff()` and `shift()` make a NaN in the first row.
- Looping over rows with `for` when one of these five calls does the work.

## Interview lens

**Typical question:** "Build a feature: the average sales of the previous 7 days, for each day. Be careful about leakage."

**Strong answer:** I use `s.shift(1).rolling(7).mean()`. The shift moves the series one day later. So the window for day t covers days t−7 to t−1 and does not contain day t. The first 7 rows are NaN, and I keep them as NaN or drop them on purpose. This is vectorized, so it runs in O(n). I also check on a small example by hand.

**Red flags:**
- `s.rolling(7).mean()` used for the same day as a feature.
- A Python loop over dates.
- Not saying what happens in the first rows.

## Real world

- Lag and rolling-mean features were the main inputs of the gradient boosting solutions in the M5 forecasting competition (Walmart sales). Those solutions were strong. You will build them yourself in Stage 5.
- Weekly, monthly or hourly aggregation with `resample` is the first step in almost every demand or traffic project.

## Key points

- `shift(k)` moves values later in time by k rows; `diff` is the change; `pct_change` is the growth rate.
- `rolling(k)` is a trailing window. It uses the past and today, never the future.
- `resample` makes one row per new period. Choose sum, mean or last on purpose.
- `groupby` summarizes by any key, such as weekday or hour of day.
- To avoid leakage, shift features so they only use data before the day you predict.
