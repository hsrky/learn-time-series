---
id: s5-03-calendar-holidays-target-encoding
title: Calendar, holiday and event features, and the target encoding trap
minutes: 30
level: intermediate
goals: [Add calendar and holiday features that are known in advance, Build days-to-event features, Use target encoding without leaking the target]
prereqs: [s5-02-lag-and-rolling-features]
tags: [features, calendar, holidays, target-encoding]
skills: [leakage, pandas-fluency]
---
## Warm-up
```check
{"q": "Which feature is safe for predicting y(t)?", "type": "single",
 "options": ["y.rolling(7).mean()", "y.shift(1).rolling(7).mean()", "y.shift(-1)"],
 "answer": 1,
 "why": ["It contains y(t).", "Correct: only past values.", "It is the next value, so a leak."]}
```

```check
{"q": "You want a feature for a daily table with many stores. How do you make lag_1?", "type": "single",
 "options": ["df['y'].shift(1)", "df.groupby('store')['y'].shift(1)", "df['y'].rolling(1).mean()"],
 "answer": 1,
 "why": ["The first row of each store would get the last value of another store.", "Correct: the lag is built inside each store.", "Rolling with window 1 is the current value, not the previous one."]}
```

## Why it matters
Sales are not random. They are higher on Saturday, lower in January, and jump before Christmas. The **calendar** explains a large part of many series. These facts are known years in advance, so they are safe and very strong features. Many winning solutions in retail forecasting are mostly calendar, price and lag features with a tree model. But one feature type is dangerous: **target encoding**. It is a common source of hidden leakage.

## Calendar features
A [[calendar feature]] is read from the date alone.

| Feature | Example for 2024-12-25 (Wednesday) |
|---|---|
| day of week (Mon = 0) | 2 |
| is weekend | 0 |
| month | 12 |
| day of month | 25 |
| week of year | 52 |
| is month end | 0 |

In pandas: `idx.dayofweek`, `idx.month`, `idx.day`, `idx.isocalendar().week`, `idx.is_month_end`.

Tree models (random forest, gradient boosting) can use these numbers directly. Linear models need a better form for cycles. Day 6 (Sunday) is next to day 0 (Monday), but 6 and 0 are far apart as numbers. Use **sin/cos**: `sin(2π·dow/7)` and `cos(2π·dow/7)`, or [[one-hot encoding|one-hot]] columns.

```check
{"q": "Why can a linear model not use 'month' as a plain number well?", "type": "single",
 "options": ["December (12) and January (1) are neighbours in time but far apart as numbers", "Month is not known in advance", "Month has too many values"],
 "answer": 0,
 "why": ["Correct: the cycle wraps around. Use sin/cos or one-hot columns.", "The month is known in advance.", "Twelve values are fine."]}
```

## Holidays and events
Holidays change demand a lot. Add:

- `is_holiday`: 1 on a holiday.
- `days_to_next_holiday`: 3 means the holiday is in 3 days (shoppers prepare before).
- `days_since_last_holiday`: effect after the day.
- Other events: promotions, sports finals, school breaks. Use a table of event dates.

Holidays must come from a **calendar list for each country**. Some holidays move each year (Easter, Lunar New Year), so never compute them from the day of the year. Event dates must be known **in advance**. A promotion that you plan is known. A surprise event is not.

Example: holidays on 2024-12-25 and 2025-01-01. For 2024-12-23, `days_to_next_holiday = 2`.

```check
{"q": "Holidays: Dec 25 and Jan 1. What is days_to_next_holiday on Dec 28 (holiday counts if it is today)?", "type": "numeric",
 "answer": 4, "tol": 0.001,
 "why": "From Dec 28 to Jan 1 is 4 days (29, 30, 31, Jan 1)."}
```

## Target encoding and why it leaks
A category such as `store_id` can be turned into a number. **[[target encoding|Target encoding]]** replaces the category with the mean of the target in that category. It is compact and often strong.

The danger: if you compute the mean over all rows, each row's own target is inside its feature.

Example: store A has sales 10, 20, 30 in time order.

| Row | Target | Leaky encoding (mean of all) | Safe encoding (mean of earlier rows) |
|---|---|---|---|
| 1 | 10 | 20 | NaN |
| 2 | 20 | 20 | 10 |
| 3 | 30 | 20 | 15 |

## Safe encoding and smoothing

The leaky column uses the future: row 1 knows about the sales of rows 2 and 3. The safe column is an **expanding mean** that only uses earlier rows. For rare categories, add smoothing toward the global mean. This avoids noisy values. Use `(sum + m × prior) / (count + m)`. Here `m` is a smoothing weight and `prior` is the overall mean so far.

```chart
{"title": "Leaky vs safe target encoding for one store", "x": "row", "height": 200,
 "series": [
   {"name": "target", "y": [10, 20, 30, 25, 35, 40]},
   {"name": "leaky (mean of all)", "y": [26.7, 26.7, 26.7, 26.7, 26.7, 26.7], "dash": true},
   {"name": "safe (mean of earlier rows)", "y": [26.7, 10, 15, 20, 21.2, 24]}
 ],
 "caption": "The safe encoding starts without information (here filled with the global mean 26.7) and learns as time passes."}
```

```check
{"q": "Store B sales in time order: 50, 60, 70. What is the safe (expanding, earlier rows only) encoding of row 3?", "type": "numeric",
 "answer": 55, "tol": 0.001,
 "why": "Earlier rows are 50 and 60. Their mean is 55."}
```

## Worked example
We build calendar and holiday-distance features, and compare leaky and safe target encoding.

```python
import numpy as np
import pandas as pd

idx = pd.date_range("2024-12-22", periods=7, freq="D")
holidays = pd.DatetimeIndex(["2024-12-25", "2025-01-01"])

cal = pd.DataFrame(index=idx)
cal["dow"] = idx.dayofweek                       # Monday = 0
cal["is_weekend"] = (idx.dayofweek >= 5).astype(int)
cal["is_holiday"] = idx.isin(holidays).astype(int)

# days until the next holiday (today counts): first holiday >= date
pos = holidays.searchsorted(idx)                 # position of next holiday
nxt = holidays[np.minimum(pos, len(holidays) - 1)]
cal["days_to_next"] = np.where(pos < len(holidays), (nxt - idx).days, np.nan)
print(cal)

# Target encoding of the store id
sales = pd.DataFrame({"store": list("ABABAB"), "y": [10, 50, 20, 60, 30, 70]})
g = sales.groupby("store")["y"]
sales["te_leaky"] = g.transform("mean")                                   # uses all rows
sales["te_safe"] = g.transform(lambda s: s.shift(1).expanding().mean())   # earlier rows only
print(sales)
# Output:
#             dow  is_weekend  is_holiday  days_to_next
# 2024-12-22    6           1           0           3.0
# 2024-12-23    0           0           0           2.0
# 2024-12-24    1           0           0           1.0
# 2024-12-25    2           0           1           0.0
# 2024-12-26    3           0           0           6.0
# 2024-12-27    4           0           0           5.0
# 2024-12-28    5           1           0           4.0
#   store   y  te_leaky  te_safe
# 0     A  10      20.0      NaN
# 1     B  50      60.0      NaN
# 2     A  20      20.0     10.0
# 3     B  60      60.0     50.0
# 4     A  30      20.0     15.0
# 5     B  70      60.0     55.0
```

`days_to_next` is 3 on 2024-12-22 and 0 on the holiday itself. After the holiday, it counts down to Jan 1 (6 days on Dec 26). The leaky encoding gives the same number to every row of a store, for example 20.0 for store A. The safe encoding starts with `NaN` and then follows the history.

## Common mistakes
- Using a holiday list for the wrong country or only for the training years. Include future years.
- Computing target means on the whole table before the split.
- Using event features that are not known in advance (for example 'actual' weather as a calendar-like feature).
- Using day of year to guess moving holidays like Easter.
- One-hot encoding thousands of categories. Use an id feature that the tree model supports, or safe target encoding.
- Forgetting time zones: a UTC timestamp can fall on a different calendar day than local time.

## Interview lens
**Typical question:** "How do you encode `store_id` with 1,000 values for a gradient boosting forecast?"

**Strong answer:** Options are one-hot (too wide), an integer or native categorical feature (many libraries support it), or target encoding. For target encoding I must avoid leakage. I compute it as an expanding mean of earlier rows only. I smooth it toward the global mean, so rare stores are not noisy. I fit it on training data and apply the same values to the test period. I also add calendar and holiday features, because they are known in advance and strong.

**Red flags:**
- Target mean computed on all data.
- Random K-fold target encoding on time series.
- Holiday features built from the test period's actual sales.
- Not knowing why a single feature gives a perfect score.

## Real world
- In the Rossmann Store Sales Kaggle competition, promotions, state holidays, school holidays and store type were key inputs. Strong teams used calendar features with gradient boosting or neural networks with embeddings.
- Facebook's Prophet library takes a table of holidays with optional windows before and after each holiday.
- Scikit-learn added `TargetEncoder` that uses cross-fitting; for time series you must still make sure the folds respect time order.

## Key points
- Calendar and holiday features are known in advance: they are safe and strong.
- Use sin/cos or one-hot for cycles in linear models; trees can use plain integers.
- Add distance features such as days to the next holiday.
- Target encoding must use earlier rows only (expanding mean), ideally with smoothing.
- Event features must be known at forecast time.
