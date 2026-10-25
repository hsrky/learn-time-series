---
id: s1-03-frequency-resampling
title: Frequency, resampling and aggregation
minutes: 30
level: beginner
goals: [Explain upsampling and downsampling, Choose the right aggregation for each kind of column, Fill new rows after upsampling without leaking the future, Use label and closed for bin edges]
prereqs: [s1-02-components]
tags: [resample, frequency, aggregation, ffill, ohlc]
skills: [pandas-fluency, leakage]
---
## Warm-up

```check
{"q": "Which model fits sales where the weekly swing grows as sales grow?", "type": "single",
 "options": ["Multiplicative", "Additive", "No model"], "answer": 0,
 "why": ["Correct. The swing is a percentage of the level.", "An additive swing would stay the same size.", "One of the two models fits."]}
```

```check
{"q": "What is the period of daily data with a weekly season?", "type": "numeric", "answer": 7, "tol": 0,
 "why": "One week has 7 daily steps."}
```

## Why it matters

Data rarely arrives at the frequency you need. A sensor sends every second, but the manager wants hourly averages. A bank reports monthly numbers, but your model works with days.

Changing the frequency is called **resampling**. One wrong choice, such as `mean` instead of `sum`, makes every later number wrong. And a careless fill can leak the future.

## Downsampling: fewer, longer steps

[[downsampling]] goes from a high frequency to a low one: hourly to daily, daily to monthly. Several rows become one.

You must say **how** to combine the rows. The right choice depends on what the number means:

| Kind of number | Example | Aggregation |
|---|---|---|
| Flow (amount in the period) | sales, rain, clicks | `sum` |
| Level (state at any moment) | temperature, price, CPU load | `mean` (or `max`, `min`) |
| Stock (balance at the end) | bank balance, stock in warehouse | `last` |
| Price bars | trading prices | `ohlc` (open, high, low, close) |

Use `.agg()` to give each column its own rule.

```python
import pandas as pd

idx = pd.date_range("2024-01-01", periods=6, freq="h")
df = pd.DataFrame({"sales": [5, 3, 4, 6, 2, 8],
                   "temp": [10.0, 11.0, 12.0, 12.5, 12.0, 11.0],
                   "stock": [100, 97, 94, 90, 88, 80]}, index=idx)

three_hourly = df.resample("3h").agg({"sales": "sum", "temp": "mean", "stock": "last"})
print(three_hourly)
# Output:
#                      sales       temp  stock
# 2024-01-01 00:00:00     12  11.000000     94
# 2024-01-01 03:00:00     16  11.833333     80
```

```check
{"q": "Hourly warehouse stock (units on the shelf). You need daily data. Which aggregation?", "type": "single",
 "options": ["last", "sum", "max"], "answer": 0,
 "why": ["Correct. Stock is a state; the end-of-day value is the daily stock.", "Summing a stock counts the same boxes 24 times.", "max is not the end-of-day value."]}
```

## Upsampling: more, shorter steps

[[upsampling]] goes from low to high frequency: monthly to daily. New rows appear, and they have **no data** (NaN). You must decide how to fill them.

- `ffill()` (forward fill): carry the last known value forward. It uses only the past. Good for values that stay until changed, such as a price list.
- `interpolate()`: draw a line between known points. It needs the **next** known value, which is in the future. It is fine for analysis, but not when you must predict.
- Do not use `bfill()` for features: it copies the future backward.

Never `sum` after upsampling a flow. A monthly total of 300 is not 300 for each day. Spread it (`/30`) if you need it.

```chart
{"title": "Upsampling: monthly values carried forward", "x": "day", "height": 200, "kind": "line",
 "series": [{"name": "ffill (step)", "y": [10,10,10,10,10,10,10,10,10,10, 14,14,14,14,14,14,14,14,14,14, 12,12,12,12,12,12,12,12,12,12]},
            {"name": "linear interpolation", "y": [10,10.4,10.8,11.2,11.6,12,12.4,12.8,13.2,13.6, 14,13.8,13.6,13.4,13.2,13,12.8,12.6,12.4,12.2, 12,12,12,12,12,12,12,12,12,12]}],
 "caption": "The step line only uses known past values. The straight lines between points need the next value, so they use the future."}
```

```check
{"q": "You must forecast tomorrow using a daily feature that came from monthly data. Which fill is safe?", "type": "single",
 "options": ["ffill", "bfill", "interpolate()"], "answer": 0,
 "why": ["Correct. ffill uses only values already known.", "bfill copies a future value backward. That is leakage.", "interpolate needs the next known point, which is in the future."]}
```

## Bins: label and closed

`resample` puts rows into **bins** (time buckets). Two settings matter:

- `closed`: which edge belongs to the bin. `left` means the bin is [start, end). The row at exactly `end` goes to the next bin.
- `label`: which edge names the bin: the start or the end.

Defaults: `left` for fixed steps such as `"h"`, `"D"`, `"5min"`. `right` for the end-of-period codes `"ME"`, `"W"`, `"QE"`, `"YE"`.

A row at 00:05 with `5min` bins goes to the bin labelled 00:05 (covering 00:05 to 00:10). If you want the opposite, set `closed="right", label="right"`. Be careful: a label at the end of a bin shows a time *after* some of the data in it.

```python
import pandas as pd

idx = pd.date_range("2024-01-01 00:00", periods=11, freq="min")
s = pd.Series(1, index=idx)       # one event per minute, 00:00 .. 00:10

print(s.resample("5min").sum())                                # default: closed left, label left
print(s.resample("5min", closed="right", label="right").sum()) # (00:00,00:05] is named 00:05
# Output:
# 2024-01-01 00:00:00    5
# 2024-01-01 00:05:00    5
# 2024-01-01 00:10:00    1
# Freq: 5min, dtype: int64
# 2024-01-01 00:00:00    1
# 2024-01-01 00:05:00    5
# 2024-01-01 00:10:00    5
# Freq: 5min, dtype: int64
```

```check
{"q": "With the default 5min bins, which bin holds a row timestamped exactly 00:05?", "type": "single",
 "options": ["The bin labelled 00:05 (00:05 to 00:10)", "The bin labelled 00:00", "It is dropped"], "answer": 0,
 "why": ["Correct. The default is closed on the left, so 00:05 starts a new bin.", "That would be closed on the right.", "No row is dropped."]}
```

## Worked example

Task: you have trade prices at irregular times. Build 5-minute bars (open, high, low, close). Then upsample a daily value to hours without using the future.

```python
import pandas as pd

times = pd.to_datetime(["2024-01-02 09:00:10", "2024-01-02 09:02:30", "2024-01-02 09:04:50",
                        "2024-01-02 09:06:00", "2024-01-02 09:07:45", "2024-01-02 09:16:20"])
price = pd.Series([100.0, 101.5, 99.0, 100.5, 102.0, 103.0], index=times)

# 1) Irregular ticks -> regular 5-minute bars
bars = price.resample("5min").ohlc()
print(bars)

# 2) The bin 09:10 has no trades. Its OHLC is NaN. Carry the last close forward.
bars["close"] = bars["close"].ffill()
print(bars["close"].tolist())

# 3) Upsample a daily series to 6-hour steps, carrying values forward only
daily = pd.Series([10.0, 20.0], index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
print(daily.resample("6h").ffill())
# Output:
#                       open   high    low  close
# 2024-01-02 09:00:00  100.0  101.5   99.0   99.0
# 2024-01-02 09:05:00  100.5  102.0  100.5  102.0
# 2024-01-02 09:10:00    NaN    NaN    NaN    NaN
# 2024-01-02 09:15:00  103.0  103.0  103.0  103.0
# [99.0, 102.0, 102.0, 103.0]
# 2024-01-02 00:00:00    10.0
# 2024-01-02 06:00:00    10.0
# 2024-01-02 12:00:00    10.0
# 2024-01-02 18:00:00    10.0
# 2024-01-03 00:00:00    20.0
# Freq: 6h, dtype: float64
```

Notice the empty bin at 09:10. `resample` keeps it, because it creates every bin between the first and the last row. You have to decide what an empty bin means.

## Common mistakes

- Using `mean` for a flow such as sales (you get an average hour, not the total).
- Using `sum` for a stock such as a balance.
- Using `interpolate` or `bfill` to prepare features for a forecast. This is leakage.
- Forgetting that the last bin may be incomplete (a half week looks like a drop).
- Reading a bin label that is the end of the period as if it were the start.

## Interview lens

**Typical question:** "You have tick data with irregular timestamps. How do you create a regular series for modeling?"

**Strong answer:** I choose the target frequency from the business need and the data density. Then I resample with an aggregation that fits the meaning of the number: sum for counts, last for balances, OHLC for prices. I look at empty bins and decide to keep them as zero (no events) or as missing (no data). I check that the last bin is complete. I make sure no fill step uses future values.

**Red flags:**
- Using `mean` for everything.
- Not checking empty or partial bins.
- Using backward fill in a forecasting pipeline.

## Real world

- Financial charts are drawn from OHLC bars, built by resampling trade ticks into minute, hour or day bars.
- The public M4 competition data comes in fixed frequencies (yearly, quarterly, monthly, weekly, daily, hourly), and you pick methods by frequency.
- Retail teams often forecast at a higher level (week) and then spread the result to days. Both steps are resampling.

## Key points

- Downsampling combines rows: sum for flows, mean for levels, last for stocks, OHLC for prices.
- Upsampling creates empty rows. `ffill` uses only the past. `interpolate` and `bfill` use the future.
- `closed` and `label` decide which bin a boundary row falls in and how the bin is named.
- Always check empty bins and the incomplete last bin.
