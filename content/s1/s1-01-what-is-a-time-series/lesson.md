---
id: s1-01-what-is-a-time-series
title: What is a time series (and what is not)
minutes: 20
level: beginner
goals: [Define a time series in one sentence, Tell time series from cross-sectional and panel data, Tell regular from irregular timestamps, Check a series for gaps in pandas]
prereqs: [s0-05-core-time-operations]
tags: [basics, panel, regular, irregular]
skills: [pandas-fluency]
---
## Warm-up

```check
{"q": "s.shift(1) at day t gives the value of which day?", "type": "single",
 "options": ["Day t−1", "Day t+1", "Day t"], "answer": 0,
 "why": ["Correct. shift(1) moves values later, so each row sees the previous day.", "That is shift(-1), the future.", "No shift would keep the same day."]}
```

```check
{"q": "You need weekly totals from daily sales. Which call?", "type": "single",
 "options": ["s.resample('W').sum()", "s.rolling(7).mean()", "s.diff(7)"], "answer": 0,
 "why": ["Correct. resample makes one row per week; sum adds the days.", "Rolling keeps one row per day.", "diff(7) is the change versus 7 days ago."]}
```

## Why it matters

Your phone counts your steps every day. A shop counted its sales every hour. A power company measured electricity every 15 minutes.

All of these are **time series**. Many real data problems are time series, and many common methods break on them.

If you treat a time series like a normal table, you shuffle the rows. You test on the past. You train on the future. The model looks great in tests and fails in real life. First step: know what you have.

## The definition

A [[time series]] is a set of values of the same thing, measured at different times and **kept in time order**.

Two things make it special:

1. **Order matters.** Day 5 comes after day 4. If you shuffle the rows, you lose the information.
2. **Nearby values are related.** Today's temperature is close to yesterday's. This is called [[autocorrelation]] (you meet it in Stage 2).

Because of the second point, the usual rule "rows are independent" is false. That changes how we split data, how we test, and how we build models.

```chart
{"title": "A time series: order carries information", "x": "day", "height": 220,
 "series": [{"name": "value", "gen": [["randomWalk", {"sd": 1.0, "start": 20}]], "n": 60, "seed": 4}],
 "caption": "Each point is close to the point before it. If you shuffle the days, this shape is gone."}
```

```check
{"q": "Which fact makes a time series different from a normal table?", "type": "single",
 "options": ["The order of rows carries information", "It has more than 100 rows", "It has only numbers"], "answer": 0,
 "why": ["Correct. Shuffling the rows destroys the signal.", "Size does not matter.", "Time series can hold any type of value."]}
```

## Time series, cross-sectional and panel data

Three common shapes of data:

| Type | What it is | Example |
|---|---|---|
| [[cross-sectional]] | Many things, **one** moment | Heights of 1,000 people measured today |
| Time series | **One** thing, many moments | Daily sales of one store |
| [[panel data]] | Many things, many moments | Daily sales of 500 stores |

Panel data is also called "many series" or "hierarchical data". Most real forecasting jobs are panels: many products, many stores.

In a panel you must keep the **time order inside each series**. You also add an id column such as `store`.

```python
import pandas as pd

# Panel data in "long" format: one row per (store, date)
long = pd.DataFrame({
    "store": ["A", "A", "A", "B", "B", "B"],
    "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"] * 2),
    "sales": [10, 12, 11, 5, 6, 9],
})

# One time series = one store, indexed by date
a = long[long["store"] == "A"].set_index("date")["sales"]
print(a)

# "Wide" format: one column per store (needs the same dates for all)
wide = long.pivot(index="date", columns="store", values="sales")
print(wide)
# Output:
# date
# 2024-01-01    10
# 2024-01-02    12
# 2024-01-03    11
# Name: sales, dtype: int64
# store        A  B
# date
# 2024-01-01  10  5
# 2024-01-02  12  6
# 2024-01-03  11  9
```

```check
{"q": "A table has 10,000 customers and the money each spent in March 2024. What is it?", "type": "single",
 "options": ["Cross-sectional data", "A time series", "Panel data"], "answer": 0,
 "why": ["Correct. Many things, one period.", "There is no time order of one thing.", "A panel needs many moments for each customer."]}
```

## Regular and irregular timestamps

A series is **regular** when the time steps are equal: every hour, every day, every month. Its [[frequency]] is that step.

A series is **irregular** when the steps differ. Examples: a customer buys at random times. A sensor sends data only when the value changes. We call such data an **event log** or [[irregular time series]].

Also be careful: monthly data is regular in calendar terms but months have 28 to 31 days. So the gap in days is not constant.

Many methods need a regular series. The usual fix is to aggregate events into fixed buckets (e.g. orders per hour). You learn this in lesson 3.

```chart
{"title": "Regular (every 2 hours) vs irregular (event times)", "x": "hour", "height": 190, "kind": "dots",
 "series": [{"name": "regular", "x": [0, 2, 4, 6, 8, 10, 12], "y": [1, 1, 1, 1, 1, 1, 1]},
            {"name": "irregular events", "x": [0.5, 1.1, 4.7, 5.0, 5.3, 9.8, 11.9], "y": [2, 2, 2, 2, 2, 2, 2]}],
 "caption": "The upper dots are events at random moments (gaps differ). The lower dots have equal steps."}
```

```check
{"q": "A shop logs each sale with its exact time. Which description is right?", "type": "single",
 "options": ["Irregular event data; aggregate it to hourly or daily counts first", "A regular time series with no work needed", "Cross-sectional data"], "answer": 0,
 "why": ["Correct. Sales happen at random moments. Counting per hour makes a regular series.", "The gaps between sales are not equal.", "It has time order, so it is not cross-sectional."]}
```

## What can you do with a time series?

| Task | Question |
|---|---|
| Forecasting | What will the next values be? |
| Anomaly detection | Is this value strange? |
| Classification | What kind of series is this (e.g. which activity)? |
| Description | What is the trend and the season? |

This course focuses on **forecasting**, but we use the same tools for all four.

## Worked example

Task: you receive a daily series. Before any model, check that it is sorted, has no duplicate dates, and has no missing days.

```python
import pandas as pd

dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-06", "2024-01-07"])
s = pd.Series([5, 6, 7, 10, 11], index=dates)

# 1) Is the index sorted and unique?
print("sorted:", s.index.is_monotonic_increasing, "| unique:", s.index.is_unique)

# 2) What are the steps between rows?
steps = s.index.to_series().diff().dropna()
print(steps.value_counts())

# 3) Which dates are missing from a full daily calendar?
full = pd.date_range(s.index.min(), s.index.max(), freq="D")
missing = full.difference(s.index)
print(list(missing.strftime("%Y-%m-%d")))

# 4) pandas can also guess the frequency (None means: no regular step)
print(pd.infer_freq(s.index))
# Output:
# sorted: True | unique: True
# 1 days    3
# 3 days    1
# Name: count, dtype: int64
# ['2024-01-04', '2024-01-05']
# None
```

Notice: two days are missing (4 and 5 January). The series looks regular at first sight, but it is not. A model that assumes one row per day would be wrong here.

## Common mistakes

- Shuffling the rows of a time series (for example `train_test_split` with default settings).
- Treating panel data as one long series. Mixing stores in one sequence makes no sense.
- Assuming a series is regular because most steps are equal.
- Forgetting to sort by time before you compute `diff` or `shift`.
- Mixing time zones in one index.

## Interview lens

**Typical question:** "What is the difference between a time series and a normal tabular dataset? Why does it matter for modeling?"

**Strong answer:** In a time series, rows have an order and neighbors are related, so rows are not independent. That means a random train and test split leaks the future into training. I split by time instead: train on the past, test on later dates. I also check if the data is regular and complete before I model. For many series, I treat it as panel data and keep each series in order.

**Red flags:**
- Using a random split.
- Not asking about missing timestamps or duplicates.
- Calling panel data "one big time series".

## Real world

- Weather stations, stock prices, web traffic, hospital admissions and electricity load are common public examples of time series.
- The M4 competition (a well-known public forecasting competition) used 100,000 series of different frequencies. It is a classic example of a large panel.
- The Kaggle competition *Store Sales – Time Series Forecasting* is panel data: many stores and product families over time.

## Key points

- A time series is values of one thing at different times, in time order. Order matters.
- Cross-sectional means many things at one time. Panel means many things over time.
- Regular series have equal steps. Irregular series (event logs) have unequal steps. Aggregate them to make them regular.
- Always check the index first: sorted, unique, no missing steps.
