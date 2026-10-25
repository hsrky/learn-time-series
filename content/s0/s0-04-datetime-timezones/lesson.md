---
id: s0-04-datetime-timezones
title: Dates, DatetimeIndex and time zones
minutes: 30
level: beginner
goals: [Parse text into Timestamps, Build and slice a DatetimeIndex, Use Timedelta for date math, Choose tz_localize or tz_convert correctly, Explain what happens on a DST day]
prereqs: [s0-03-pandas-series-dataframe]
tags: [pandas, datetime, timezone, dst]
skills: [pandas-fluency]
---
## Warm-up

```check
{"q": "a has index [1, 2] and b has index [2, 3]. What is the index of a + b?", "type": "single",
 "options": ["[1, 2, 3]", "[2]", "[1, 2]"], "answer": 0,
 "why": ["Correct. The result has the union of both indexes. Labels 1 and 3 are NaN.", "That would be the intersection. pandas keeps the union.", "That is only the index of a."]}
```

```check
{"q": "s.loc['a':'c'] on a Series with labels a, b, c, d returns which labels?", "type": "single",
 "options": ["a, b", "a, b, c", "b, c"], "answer": 1,
 "why": ["That would exclude the end. Label slices include it.", "Correct.", "The slice starts at a."]}
```

## Why it matters

Time is the heart of a time series. And time is messy. Text dates come in many formats. Clocks change twice a year in many countries.

A day can have 23 or 25 hours. A timestamp with no time zone can mean two different moments.

One wrong time zone step can shift all your data by hours. Then a forecast uses the wrong "hour of day" and fails with no error message. This lesson prevents that.

## Timestamps and parsing

A [[Timestamp]] is one moment in time, such as `2024-03-05 14:30`. pandas also has a [[Timedelta]], which is a length of time, such as 2 days.

Turn text into Timestamps with `pd.to_datetime`. Give `format=` when the text is not ISO, so day and month are not mixed up. `03/04/2024` can mean 3 April or 4 March.

Subtracting two Timestamps gives a Timedelta.

```python
import pandas as pd

t = pd.to_datetime("2024-03-05 14:30")
print(t, t.year, t.month, t.day_name())

t2 = pd.to_datetime("04/03/2024", format="%d/%m/%Y")   # day first: 4 March
print(t2)

gap = pd.Timestamp("2024-03-10") - pd.Timestamp("2024-03-05")
print(gap, gap.days)
print(t + pd.Timedelta(hours=36))      # date math with Timedelta
# Output:
# 2024-03-05 14:30:00 2024 3 Tuesday
# 2024-03-04 00:00:00
# 5 days 00:00:00 5
# 2024-03-07 02:30:00
```

```check
{"q": "pd.to_datetime('03/04/2024', format='%d/%m/%Y') is which date?", "type": "single",
 "options": ["3 April 2024", "4 March 2024", "March 2024 (any day)"], "answer": 0,
 "why": ["Correct. %d is the day, so 03 is the day and 04 is the month.", "That is the month-first reading. The format says day first.", "A format gives one exact date."]}
```

## DatetimeIndex

A [[DatetimeIndex]] is an index made of Timestamps. It is the standard way to hold a time series in pandas.

`pd.date_range(start, periods=..., freq=...)` builds one. The `freq` code gives the step: `"D"` day, `"h"` hour, `"min"` minute, `"W"` week, `"MS"` month start.

With a DatetimeIndex you can slice with date text: `s["2024-03"]` is the whole month. The index also gives helpers such as `.dayofweek` (Monday is 0) and `.hour`.

```python
import numpy as np
import pandas as pd

idx = pd.date_range("2024-02-26", periods=10, freq="D")
s = pd.Series(np.arange(10), index=idx)

print(s["2024-03-01":"2024-03-03"])        # slice by date text, end included
print(s["2024-02"].tolist())               # all of February in this series
print(idx.dayofweek.tolist())              # 0 = Monday ... 6 = Sunday
print(idx.freqstr)                         # the step is remembered: D = day
# Output:
# 2024-03-01    4
# 2024-03-02    5
# 2024-03-03    6
# Freq: D, dtype: int64
# [0, 1, 2, 3]
# [0, 1, 2, 3, 4, 5, 6, 0, 1, 2]
# D
```

```check
{"q": "What does pd.date_range('2024-01-01', periods=3, freq='h') build?", "type": "single",
 "options": ["Three timestamps, one hour apart", "Three timestamps, one day apart", "Three timestamps on the same hour of three days"], "answer": 0,
 "why": ["Correct. 'h' is the hourly step.", "That would be freq='D'.", "That is also freq='D'."]}
```

## Time zones: localize or convert

A **naive** timestamp has no time zone. `2024-03-05 14:30` could be anywhere. An **aware** timestamp knows its zone.

Two operations, two meanings:

- `tz_localize("zone")`: "These naive times **were measured in** this zone." You attach a label. The clock numbers do not change.
- `tz_convert("zone")`: "Show the same moment on **another zone's** clock." The clock numbers change. It works only on aware data.

Best practice: store everything in [[UTC]]. Convert to local time only to show or to build features like "hour of day".

```python
import pandas as pd

naive = pd.Timestamp("2024-07-01 12:00")        # no zone
utc = naive.tz_localize("UTC")                   # label: this was UTC
print(utc)
print(utc.tz_convert("Asia/Tokyo"))             # same moment, Tokyo clock (UTC+9)
print(utc.tz_convert("America/New_York"))       # same moment, New York clock (UTC-4 in July)
print(utc == utc.tz_convert("Asia/Tokyo"))      # True: it is the same instant
# Output:
# 2024-07-01 12:00:00+00:00
# 2024-07-01 21:00:00+09:00
# 2024-07-01 08:00:00-04:00
# True
```

```chart
{"title": "Same moment, different clocks (12:00 UTC)", "x": "city", "height": 200, "kind": "bar",
 "series": [{"name": "clock hour", "y": [12, 21, 8]}],
 "caption": "Bars: UTC (12), Tokyo (21), New York in July (8). The instant is the same. Only the clock number changes."}
```

```check
{"q": "Your naive log times were written by a server in Berlin. What is the first call?", "type": "single",
 "options": ["tz_localize('Europe/Berlin')", "tz_convert('Europe/Berlin')", "tz_convert('UTC')"], "answer": 0,
 "why": ["Correct. First say which zone the numbers belong to. Then convert if needed.", "tz_convert fails on naive data. You must localize first.", "This also fails on naive data."]}
```

## Daylight saving time (DST)

In many countries the clock jumps forward one hour in spring and back one hour in autumn. This is [[DST]].

- **Spring forward:** one hour does not exist (for New York on 2024-03-10: 02:00 to 02:59 is skipped). That local day has **23 hours**.
- **Fall back:** one hour happens twice (2024-11-03, 01:00 to 01:59). That day has **25 hours**. A naive 01:30 is **ambiguous**.

When you localize, pandas raises an error for these hours. You must say what to do with `nonexistent=` and `ambiguous=`. UTC has no DST, so it never has this problem.

```python
import pandas as pd

# Hourly UTC data over the spring-forward weekend in New York
utc = pd.date_range("2024-03-09 05:00", "2024-03-12 03:00", freq="h", tz="UTC")
local = utc.tz_convert("America/New_York")

# How many hours does each LOCAL day have?
per_day = pd.Series(1, index=local).groupby(local.date).sum()
print(per_day)
# Output:
# 2024-03-09    24
# 2024-03-10    23
# 2024-03-11    24
# dtype: int64
```

```chart
{"title": "Hours in each local day (New York)", "x": "day", "height": 200, "kind": "bar",
 "series": [{"name": "spring: Mar 9, 10, 11", "y": [24, 23, 24]},
            {"name": "autumn: Nov 2, 3, 4", "y": [24, 25, 24]}],
 "caption": "A day is not always 24 hours. Daily sums on local days can look low or high only because of DST."}
```

```check
{"q": "On the day clocks go back one hour, how many hours does that local day have?", "type": "numeric", "answer": 25, "tol": 0,
 "why": "The hour from 01:00 to 01:59 happens twice, so the day has 24 + 1 = 25 hours."}
```

## Worked example

Task: a server logs events with naive timestamps in UTC. You need the event count per **local hour of day** in New York, and the time between the first and last event.

```python
import pandas as pd

# Naive timestamps, written by a server that uses UTC
raw = pd.to_datetime(["2024-07-01 03:10", "2024-07-01 13:45", "2024-07-01 14:05", "2024-07-02 02:30"])
events = pd.Series(1, index=raw)

# 1) Say which zone the numbers belong to
events = events.tz_localize("UTC")

# 2) Convert to the clock we care about
local = events.tz_convert("America/New_York")
print(local.index[0])                     # 03:10 UTC -> 23:10 the day before (UTC-4)

# 3) Count per local hour of day
print(local.groupby(local.index.hour).sum())

# 4) Time between first and last event (a Timedelta)
span = local.index[-1] - local.index[0]
print(span, round(span.total_seconds() / 3600, 2))
# Output:
# 2024-06-30 23:10:00-04:00
# 9     1
# 10    1
# 22    1
# 23    1
# dtype: int64
# 0 days 23:20:00 23.33
```

Notice: the hours of day changed after the conversion, but the span between events did not. The instants are the same.

## Common mistakes

- Using `tz_convert` on naive data. Localize first.
- Using `tz_localize` when you mean to change the clock. That relabels the numbers and shifts the real moment.
- Parsing `03/04/2024` without `format=`. Day and month can be mixed.
- Averaging "per day" on local days around DST and thinking 23 or 25 hours are normal days.
- Storing local time without a zone.

## Interview lens

**Typical question:** "Timestamps in your data are naive. How do you handle time zones and DST?"

**Strong answer:** First I find out which zone the data was recorded in. I call `tz_localize` with that zone. For ambiguous or missing hours I set `ambiguous` and `nonexistent` on purpose. Then I store and join data in UTC. I convert to local time only to build features such as hour of day or to show the user. I check for 23-hour and 25-hour days when I aggregate by local day.

**Red flags:**
- Mixing up `tz_localize` and `tz_convert`.
- Ignoring DST in hourly or daily features.
- Saying "I just drop the time zone".

## Real world

- Time zone rules come from the public IANA time zone database. Python and pandas use it, so names like `America/New_York` work.
- Retail and energy forecasters care about DST because their daily load or sales has a different shape on the day clocks change.

## Key points

- `to_datetime` parses text. Always give `format=` for non-ISO text.
- A DatetimeIndex lets you slice with date text and use helpers like `.hour` and `.dayofweek`.
- `tz_localize` attaches a zone to naive times. `tz_convert` changes the clock of aware times.
- Store in UTC. Convert to local time for features. A local day can have 23 or 25 hours.
