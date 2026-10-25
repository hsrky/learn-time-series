---
id: s1-05-lags-differences-returns
title: Lags, differences, returns and log returns
minutes: 30
level: beginner
goals: [Build lag features and explain why they are safe, Compute first and seasonal differences, Compute simple returns and log returns, Explain why log returns add up over time]
prereqs: [s1-04-missing-data-imputation]
tags: [lag, difference, returns, log-returns]
skills: [leakage, pandas-fluency, from-scratch]
---
## Warm-up

```check
{"q": "A series has a missing row for 3 March. You call s.shift(1). What can go wrong?", "type": "single",
 "options": ["4 March gets the value of 2 March, two days back", "Nothing; shift uses dates", "shift raises an error"], "answer": 0,
 "why": ["Correct. shift moves by rows, not by dates. Reindex to a full grid first.", "shift works on row positions, not dates.", "It runs without a warning, which is why it is dangerous."]}
```

```check
{"q": "Which fill is safe for the inputs of a forecast model?", "type": "single",
 "options": ["ffill with a limit", "interpolate over the whole series", "bfill"], "answer": 0,
 "why": ["Correct. It uses only the past.", "It uses the value after the gap.", "It copies future values backward."]}
```

## Why it matters

Raw values are often a poor starting point. A price of 105 tells you little. A change of +5% tells you much more.

Four tools turn a raw series into something a model can use:

- **lags:** yesterday's value as an input for today,
- **differences:** the change from one step to the next,
- **returns:** the relative change,
- **log returns:** the relative change in a form that adds up.

You will use them in every stage after this one.

## Lags

A [[lag]] is a past value. Lag k at time t is y(t − k). In pandas: `s.shift(k)`.

Lag features let an ordinary model see the past. A row for "today" holds today's target and the values of the last few days as columns.

Lag features are safe: they use only data from before the target. Always reindex to a full grid first, so a lag of 1 row is a lag of 1 step.

| day | y | lag_1 | lag_2 |
|---|---|---|---|
| 1 | 5 | NaN | NaN |
| 2 | 7 | 5 | NaN |
| 3 | 6 | 7 | 5 |
| 4 | 9 | 6 | 7 |

The first rows have NaN because the past does not exist. Drop them or keep them on purpose.

```widget
{"name": "lag-features", "params": {}}
```

```check
{"q": "A daily series with a weekly season: which lag is most useful besides lag 1?", "type": "single",
 "options": ["Lag 7", "Lag 3", "Lag 10"], "answer": 0,
 "why": ["Correct. The same weekday one week ago has the same seasonal effect.", "Three days back has no special link in a weekly pattern.", "Ten days back mixes different weekdays."]}
```

## Differences

The [[difference]] is the change between neighbors: d(t) = y(t) − y(t − 1). In pandas: `s.diff()`.

Differences remove a **trend**. A series that goes up by about 2 per step has differences near 2, a flat series.

The **seasonal difference** removes a season of period m: y(t) − y(t − m). Example: with a weekly season, `s.diff(7)` compares each day with the same weekday last week.

Differencing loses the first row (or the first m rows). Later, in Stage 2, you will learn why a flat series is easier to model.

```chart
{"title": "Differencing removes a trend", "x": "day", "height": 230,
 "series": [
  {"name": "series with trend", "gen": [["trend", {"slope": 2, "start": 10}], ["noise", {"sd": 2}]], "n": 60, "seed": 5},
  {"name": "first difference (about +2 each step)", "gen": [["const", {"value": 2}], ["noise", {"sd": 2.8}]], "n": 60, "seed": 6}
 ],
 "caption": "The top line climbs. The differences stay around 2: the trend is gone, only the changes are left."}
```

```check
{"q": "y = [4, 7, 5, 9]. What is the last value of the first difference?", "type": "numeric", "answer": 4, "tol": 0,
 "why": "9 − 5 = 4."}
```

## Returns

A [[return]] is the **relative** change.

r(t) = (p(t) − p(t − 1)) / p(t − 1) = p(t) / p(t − 1) − 1

- p(t): the price (or any positive level) at time t.
- r(t): the return. 0.10 means +10%.

Example: 100 → 110 → 99. The returns are +10% and −10%. Be careful: +10% then −10% does **not** return to 100, it ends at 99.

Returns compare things of different size. A move of 5 on a price of 50 (10%) is bigger than 5 on a price of 500 (1%).

To combine returns over several steps, you **multiply**: (1 + r₁)(1 + r₂) − 1. That is awkward.

## Log returns

The [[log return]] is the natural logarithm of the price ratio.

g(t) = ln(p(t) / p(t − 1)) = ln p(t) − ln p(t − 1)

- ln: the natural logarithm. In numpy: `np.log`.

Why use them?

1. They **add up**: the log return over 3 steps is g₁ + g₂ + g₃. No multiplication needed.
2. For small moves they are almost the same as simple returns: ln(1.01) ≈ 0.00995.
3. A rise of +10% and a fall that undoes it have equal size and opposite sign: ln(1.1) = 0.0953 and ln(1/1.1) = −0.0953.

You get the price back with `p(t) = p(0) · exp(g₁ + ... + g_t)`.

```python
import numpy as np
import pandas as pd

p = pd.Series([100.0, 110.0, 99.0, 108.9])

simple = p.pct_change()                    # p(t)/p(t-1) - 1
logret = np.log(p / p.shift(1))            # ln(p(t)/p(t-1))
print(pd.DataFrame({"price": p, "simple": simple, "log": logret}).round(4))

# log returns add up: the total log return equals ln(last / first)
print(round(logret.sum(), 6), round(np.log(p.iloc[-1] / p.iloc[0]), 6))

# rebuild the price from the first price and the log returns
rebuilt = p.iloc[0] * np.exp(logret.fillna(0).cumsum())
print(rebuilt.round(2).tolist())
# Output:
#    price  simple     log
# 0  100.0     NaN     NaN
# 1  110.0     0.1  0.0953
# 2   99.0    -0.1 -0.1054
# 3  108.9     0.1  0.0953
# 0.08526 0.08526
# [100.0, 110.0, 99.0, 108.9]
```

```check
{"q": "A price goes from 50 to 60. What is the simple return?", "type": "numeric", "answer": 0.2, "tol": 0.0001,
 "why": "60 / 50 − 1 = 0.20, which is +20%."}
```

```check
{"q": "Log returns of three days are 0.02, -0.01 and 0.03. What is the log return over the 3 days?", "type": "numeric", "answer": 0.04, "tol": 0.0001,
 "why": "Log returns add up: 0.02 − 0.01 + 0.03 = 0.04."}
```

## Worked example

Task: weekly seasonal series with growth. Show lags, a first difference, a seasonal difference, and log returns. Then check that no feature uses today's target.

```python
import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=14, freq="D")
week = np.array([10, 12, 11, 13, 20, 30, 25])
y = pd.Series(np.tile(week, 2) * np.repeat([1.0, 1.1], 7), index=idx)   # second week is 10% higher

df = pd.DataFrame({"y": y})
df["lag_1"] = y.shift(1)                    # yesterday
df["lag_7"] = y.shift(7)                    # same weekday last week
df["diff_1"] = y.diff(1)                    # change from yesterday
df["diff_7"] = y.diff(7)                    # change from the same weekday last week
df["logret_7"] = np.log(y / y.shift(7))     # weekly log growth
print(df.round(3).tail(7))

# Safe? Every column is built from rows BEFORE today, except y itself (the target).
# Check one cell by hand: lag_7 on day 14 equals y on day 7.
print(df["lag_7"].iloc[13] == df["y"].iloc[6])
# Output:
#                y  lag_1  lag_7  diff_1  diff_7  logret_7
# 2024-01-08  11.0   25.0   10.0   -14.0     1.0     0.095
# 2024-01-09  13.2   11.0   12.0     2.2     1.2     0.095
# 2024-01-10  12.1   13.2   11.0    -1.1     1.1     0.095
# 2024-01-11  14.3   12.1   13.0     2.2     1.3     0.095
# 2024-01-12  22.0   14.3   20.0     7.7     2.0     0.095
# 2024-01-13  33.0   22.0   30.0    11.0     3.0     0.095
# 2024-01-14  27.5   33.0   25.0    -5.5     2.5     0.095
# True
```

Notice: `diff_7` is not zero: it shows the growth from week one to week two. `logret_7` is the same number (about 0.095) on every weekday: the seasonal pattern is gone and only the growth is left.

## Common mistakes

- Using `shift(-1)` as a feature. That is tomorrow's value.
- Computing lags on a series with missing rows.
- Taking `log` of zero or negative values. Use only positive levels, or `np.log1p`.
- Averaging simple returns over time. Multiply them, or add log returns instead.
- Differencing twice by accident, then wondering why the signal is noisy.

## Interview lens

**Typical question:** "Why do people model log returns instead of prices?"

**Strong answer:** Prices have a trend and their size changes, so their statistics change over time. Returns are relative changes, so they are comparable across levels and are much more stable. Log returns also add up across time, which makes multi-step math simple, and a gain and a loss of the same size cancel exactly. For small moves log and simple returns are almost equal. I use them only for positive values, and I convert the forecast back with `exp` and the last known price.

**Red flags:**
- Saying "log returns are always better" with no reason.
- Not knowing that +10% and −10% do not cancel.
- Using returns on data that can be zero or negative.

## Real world

- Finance uses returns, not prices, as the standard object of study. Many classic volatility models work on log returns.
- Differencing is the "I" (integrated) in ARIMA, the classic forecasting model family you meet in Stage 3.
- Lag features are the core of the gradient boosting solutions seen in public forecasting competitions.

## Key points

- A lag is a past value (`shift(k)`). Lags are safe inputs; negative shifts are not.
- A difference is the change (`diff`). It removes a trend. A seasonal difference (`diff(m)`) removes a season.
- A simple return is the relative change. Returns multiply over time.
- A log return is `ln(p_t / p_{t-1})`. It adds over time and rebuilds the price with `exp(cumsum)`.
