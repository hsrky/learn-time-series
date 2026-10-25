---
id: s1-07-decomposition
title: Decomposition: classical and STL
minutes: 35
level: intermediate
goals: [Split a series into trend and season and remainder, Compute the classical decomposition step by step, Choose additive or multiplicative decomposition, Explain what STL adds and when decomposition leaks]
prereqs: [s1-06-rolling-ewma]
tags: [decomposition, seasonality, trend, stl, from-scratch]
skills: [from-scratch, leakage, baseline-first]
---
## Warm-up

```check
{"q": "Which window is safe for a feature that predicts tomorrow?", "type": "single",
 "options": ["Trailing window that ends today", "Centered window", "Window that includes tomorrow"], "answer": 0,
 "why": ["Correct. It uses only what is known today.", "A centered window includes future days.", "Tomorrow is the thing you want to predict."]}
```

```check
{"q": "EWMA with alpha = 0.5: S(t−1) = 10 and y(t) = 20. What is S(t)?", "type": "numeric", "answer": 15, "tol": 0.0001,
 "why": "0.5 · 20 + 0.5 · 10 = 15."}
```

## Why it matters

You look at three years of monthly sales. The line goes up, with a wave every year. Your boss asks: "How fast are we really growing, without the Christmas effect?"

**Decomposition** answers this. It splits the series into a trend, a seasonal part and a remainder.

People use it to explain a series, to remove a season before modeling, and to find odd values (a large remainder). It is also a classic OA task: "implement it without a library".

## The idea

[[decomposition]] splits a series into parts that you already know:

- Additive: **y = trend + season + remainder**
- Multiplicative: **y = trend × season × remainder**

The remainder (or residual) is what the trend and the season do not explain. A good decomposition leaves a remainder that looks like noise.

The classical method has four steps:

1. **Trend:** smooth the series with a centered moving average of one full period.
2. **Detrend:** remove the trend (subtract, or divide).
3. **Seasonal:** average the detrended values at each position of the period. Center them.
4. **Remainder:** what is left.

```widget
{"name": "components", "params": {}}
```

```check
{"q": "Why does the trend step use a moving average of exactly one full period?", "type": "single",
 "options": ["The average of one full season contains every seasonal position once, so the season cancels out", "It is the fastest window to compute", "It removes all noise"], "answer": 0,
 "why": ["Correct. Highs and lows of the season add to zero inside one full period, so only the trend stays.", "Speed is not the reason.", "Noise is reduced but not removed."]}
```

## Step 1: trend with a centered moving average

For an **odd** period m (for example 7), the window of m values centered on t is natural: t−3 ... t+3.

For an **even** period (for example 4 quarters or 12 months) no value sits in the exact center. So we use a "2 × m" average: take the mean of m values, shifted by one step, and average the two results. The result is a window of m + 1 values where the two **end values count half**:

T(t) = (0.5·y(t−m/2) + y(t−m/2+1) + ... + y(t+m/2−1) + 0.5·y(t+m/2)) / m

- m: the period (4 for quarters).
- The first and last m/2 values have no trend: they stay NaN.

Example: m = 4 and the values are 10, 14, 18, 12, 12. The trend at the third value is (0.5·10 + 14 + 18 + 12 + 0.5·12) / 4 = 55 / 4 = 13.75.

```chart
{"title": "Trend by centered moving average (period 4)", "x": "quarter", "height": 230,
 "series": [
  {"name": "data", "x": [1,2,3,4,5,6,7,8,9,10,11,12], "y": [10,14,18,12,12,16,20,14,14,18,22,16]},
  {"name": "trend (starts at quarter 3)", "x": [3,4,5,6,7,8,9,10], "y": [13.75,14.25,14.75,15.25,15.75,16.25,16.75,17.25], "dash": true}
 ],
 "caption": "The trend line is smooth and rises by 0.5 each quarter. It is missing at the two ends, where the window does not fit."}
```

```check
{"q": "Quarterly data (m = 4). How many trend values are NaN at the two ends together?", "type": "numeric", "answer": 4, "tol": 0,
 "why": "m / 2 = 2 values are lost at the start and 2 at the end, so 4 in total."}
```

## Steps 2 to 4: season and remainder

**Detrend:** y − trend (additive). For the quarterly example: 18 − 13.75 = 4.25 at quarter 3.

**Seasonal index:** collect the detrended values for each position of the period, and take the mean. Quarter 1 positions are 1, 5, 9; quarter 2 are 2, 6, 10; and so on. Skip the NaN.

Then **center** the indexes: subtract their mean, so that they add to 0. If you skip this, a constant level leaks from the trend into the season.

**Remainder:** y − trend − season.

For the example the seasonal indexes are −2.75, +0.75, +4.25, −2.25. They sum to 0. The remainder is exactly 0 here, because the data was built without noise.

```check
{"q": "The raw seasonal averages are 4, 6, 8, 2 (they add to 20). What are the centered additive indexes?", "type": "single",
 "options": ["-1, 1, 3, -3", "4, 6, 8, 2", "0.8, 1.2, 1.6, 0.4"], "answer": 0,
 "why": ["Correct. The mean is 5. Subtract 5 from each value: −1, 1, 3, −3. They sum to 0.", "These are not centered.", "These are the values divided by the sum (multiplicative style, wrong scale)."]}
```

## Multiplicative decomposition

When the seasonal swing grows with the level, use the multiplicative form.

Detrend by **dividing**: y / trend. The result is a ratio such as 1.20 (20% above the trend). Average the ratios per position, then **center by dividing by their mean**, so that the indexes average 1.

Remainder: y / (trend × season). It should be close to 1.

Quick alternative: take `np.log` of the series and use the additive method. Add `np.exp` at the end.

## STL: a more flexible method

Classical decomposition has limits:

- The seasonal pattern is **the same in every year**.
- The trend is lost at both ends.
- Outliers pull the averages.

[[STL]] (Seasonal and Trend decomposition using Loess) is a modern method that fixes these. It uses [[loess]]: many small local fits, instead of one average.

- The seasonal part is **allowed to change slowly** over time.
- The trend reaches the ends of the series.
- A robust option reduces the effect of outliers.
- It handles any period, but it is additive (use a log for multiplicative data).

In Python: `statsmodels.tsa.seasonal.STL(series, period=12).fit()`. You meet it again in Stage 12. For this course, remember the idea: *classical = fixed seasonal pattern, simple averages. STL = flexible pattern, local fits.*

```check
{"q": "A retailer's weekly pattern slowly gets stronger over the years. Which method suits better?", "type": "single",
 "options": ["STL, because the seasonal part may change over time", "Classical, because it is more flexible", "Neither can handle it"], "answer": 0,
 "why": ["Correct. STL lets the seasonal shape change slowly.", "Classical decomposition uses one fixed pattern for all periods.", "STL was made for this case."]}
```

## Worked example

Task: decompose 12 months of a quarterly-like series by hand with numpy. Then check that the three parts add up to the data.

```python
import numpy as np
import pandas as pd

y = np.array([10, 14, 18, 12, 12, 16, 20, 14, 14, 18, 22, 16], dtype=float)   # 3 years of quarters
m = 4

# Step 1: trend = 2 x 4 centered moving average (half weight at both ends)
w = np.array([0.5, 1, 1, 1, 0.5]) / m
trend = np.full(len(y), np.nan)
trend[2:-2] = np.convolve(y, w, mode="valid")          # the first and last 2 stay NaN

# Step 2: detrend
detrended = y - trend

# Step 3: seasonal indexes = mean per quarter, then centered
avg = np.array([np.nanmean(detrended[q::m]) for q in range(m)])
avg = avg - avg.mean()
seasonal = np.tile(avg, len(y) // m)

# Step 4: remainder
resid = y - trend - seasonal

out = pd.DataFrame({"y": y, "trend": trend, "seasonal": seasonal, "resid": resid})
print(out)
print("indexes:", avg, "sum:", avg.sum())
print(np.allclose((trend + seasonal + resid)[2:-2], y[2:-2]))
# Output:
#        y  trend  seasonal  resid
# 0   10.0    NaN     -2.75    NaN
# 1   14.0    NaN      0.75    NaN
# 2   18.0  13.75      4.25    0.0
# 3   12.0  14.25     -2.25    0.0
# 4   12.0  14.75     -2.75    0.0
# 5   16.0  15.25      0.75    0.0
# 6   20.0  15.75      4.25    0.0
# 7   14.0  16.25     -2.25    0.0
# 8   14.0  16.75     -2.75    0.0
# 9   18.0  17.25      0.75    0.0
# 10  22.0    NaN      4.25    NaN
# 11  16.0    NaN     -2.25    NaN
# indexes: [-2.75  0.75  4.25 -2.25] sum: 0.0
# True
```

You will turn this into a general function in the practice problem. The check at the end always passes, because the remainder is defined as what is left over.

## Common mistakes

- Forgetting the half weights for an even period. The trend then shifts by half a step.
- Forgetting to center the seasonal indexes.
- Choosing the wrong period (for example 12 for weekly data).
- Using the additive form when the swings grow with the level.
- Using the trend, season and remainder as **features** to predict the future. They use values after time t (the centered average), so they leak.
- Expecting a trend at the ends of the series from the classical method.

## Interview lens

**Typical question:** "How does classical seasonal decomposition work? Implement the trend step."

**Strong answer:** I estimate the trend with a centered moving average of one full period. For an even period I use the 2×m average with half weights at both ends. I detrend by subtracting, or dividing for multiplicative data. I average the detrended values for each position in the period and center them. What remains is the residual. I mention that the trend is missing at both ends, the season is fixed, and that STL fixes both. I also say that the centered average uses future values, so I do not feed the components to a forecast model.

**Red flags:**
- Not knowing why the window equals one period.
- Using a trailing mean for the trend and calling it classical.
- Not centering the seasonal part.

## Real world

- The classical method has been used by statistical agencies for decades. Modern agencies use more advanced relatives, such as X-13ARIMA-SEATS (US Census Bureau).
- STL was published by Cleveland and colleagues in 1990. It is a standard tool in Python (statsmodels), R, and in many forecasting and anomaly detection libraries.
- Anomaly detection often decomposes a metric first, then looks for large remainders.

## Key points

- Decomposition splits a series into trend, season and remainder. Additive: sum. Multiplicative: product.
- Classical steps: centered moving average, detrend, average per period position and center, remainder.
- Even periods need the 2×m average with half weights at both ends. The ends of the trend are NaN.
- STL uses loess. The season can change, the ends are covered, outliers can be down-weighted.
- Decomposition describes the past. Do not use its parts as forecast features without care.
