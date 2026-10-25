---
id: s4-03-point-metrics
title: Point forecast metrics
minutes: 30
level: intermediate
goals: [Compute MAE and RMSE and say when each is better, Explain why MAPE fails at zero and is asymmetric, Use WAPE and MASE and RMSSE for fair comparisons]
prereqs: [s4-02-backtesting]
tags: [metrics, mae, rmse, mape, mase]
skills: [metrics, from-scratch]
---
## Warm-up
```check
{"q": "A backtest has 12 folds and a horizon of 7 days. How many errors per horizon step do you get?", "type": "numeric",
 "answer": 12, "tol": 0.001,
 "why": "Each fold gives one error for each horizon step. So step 1 has 12 errors, step 2 has 12 errors, and so on."}
```

```check
{"q": "What is a seasonal naive forecast with period 7 on daily data?", "type": "single",
 "options": ["The value from 7 days ago", "The average of the last 7 days", "The value from the next week"],
 "answer": 0,
 "why": ["Correct: it repeats the value from the same weekday last week.", "That is a moving average, not seasonal naive.", "Next week is the future. You do not know it."]}
```

## Why it matters
Two teams forecast demand. Team A says: "Our error is 8%." Team B says: "Our error is 120 units." Who is better? You cannot tell. The metric decides who wins. A bad metric makes you pick a bad model. For example, the popular MAPE metric rewards forecasts that are too low. In this lesson you learn the main metrics, their traps, and how to choose.

## Error, MAE and RMSE
The **error** at one time is `e = y − ŷ`. Here `y` is the actual value and `ŷ` ("y-hat") is the forecast.

Example: actual = 10, 20, 30, 40. Forecast = 12, 18, 33, 36. The errors are −2, +2, −3, +4.

- [[mae|MAE]] (mean absolute error) = mean of `|e|` = (2 + 2 + 3 + 4) / 4 = **2.75**.
- [[rmse|RMSE]] (root mean squared error) = `sqrt(mean(e²))` = sqrt((4 + 4 + 9 + 16) / 4) = sqrt(8.25) = **2.87**.

MAE is easy to explain: "on average we are 2.75 units off". RMSE punishes big errors more, because it squares them. RMSE is always ≥ MAE. Both are in the **units of the data**, so you cannot compare them across different series.

```check
{"q": "Errors are 1, 1, 1, 9. Which is larger, MAE or RMSE, and why?", "type": "single",
 "options": ["MAE, because it adds the errors", "RMSE, because the large error 9 is squared", "They are equal"],
 "answer": 1,
 "why": ["MAE = 3. It does not square.", "Correct: RMSE = sqrt((1+1+1+81)/4) = 4.58, bigger than MAE = 3.", "They are equal only if all errors have the same size."]}
```

## Percentage errors: MAPE and sMAPE
To compare series of different size, divide by the actual value.

`MAPE = mean(|y − ŷ| / |y|) × 100%`

Same example: 2/10, 2/20, 3/30, 4/40 = 0.2, 0.1, 0.1, 0.1. The mean is 0.125, so MAPE = **12.5%**.

MAPE has two serious problems.

1. **It breaks at zero.** If `y = 0`, you divide by zero. If `y` is tiny, the percentage is huge.
2. **It is asymmetric.** Actual 100, forecast 50 gives 50%. Actual 50, forecast 100 gives 100%. An under-forecast is capped at 100%. An over-forecast has no limit. So a model that minimizes MAPE tends to forecast too low.

```chart
{"title": "Same error of 10 units, different actuals", "x": "actual value", "height": 220,
 "series": [
   {"name": "APE in % for an error of 10", "x": [10, 20, 30, 40, 50, 60, 80, 100, 150, 200], "y": [100, 50, 33.3, 25, 20, 16.7, 12.5, 10, 6.7, 5]}
 ],
 "caption": "When the actual value is small, the same error gives a huge percentage. At zero it is infinite."}
```

**sMAPE** (symmetric MAPE) divides by the mean of actual and forecast: `mean(2|e| / (|y| + |ŷ|)) × 100%`. It is limited to 0–200%. It is still not truly symmetric, and it still has trouble when both are 0. Many experts avoid it.

```check
{"q": "Actual = 0 and forecast = 5. What happens to the MAPE of this point?", "type": "single",
 "options": ["It is 0%", "It is 5%", "It is undefined (division by zero)"],
 "answer": 2,
 "why": ["A wrong forecast cannot have 0% error.", "MAPE divides by the actual, which is 0, not by 5.", "Correct: |e| / |y| = 5 / 0."]}
```

## WAPE: a safer percentage
**WAPE** (weighted absolute percentage error) divides the total error by the total actual:

`WAPE = sum(|y − ŷ|) / sum(|y|)`

Example: total error = 11, total actual = 100, so WAPE = **11%**. One zero in the data causes no problem. Large values get more weight, which fits business use: "we missed 11% of the units we sold". WAPE equals MAE divided by the mean actual. It only breaks when the whole sum is zero.

```check
{"q": "Actual: 0, 0, 100. Forecast: 10, 10, 80. What is the WAPE?", "type": "numeric",
 "answer": 0.4, "tol": 0.001,
 "why": "Total error = 10 + 10 + 20 = 40. Total actual = 100. WAPE = 40 / 100 = 0.4 (40%)."}
```

## MASE and RMSSE: scale-free by a baseline
**MASE** (mean absolute scaled error) compares your MAE with the MAE of a naive method on the **training** data.

`MASE = MAE_test / MAE_naive_train`

- `MAE_test` is your MAE on the test period.
- `MAE_naive_train` is the mean of `|y_t − y_{t−m}|` over the training series. Use `m = 1` for the naive forecast or `m` = season length (for example 7) for seasonal naive.

MASE < 1 means: better than the naive method on average. MASE = 1.3 means 30% worse. It works for series with zeros and for series of different scale. **RMSSE** is the same idea for squared errors: `RMSSE = sqrt(MSE_test / MSE_naive_train)`. The M5 competition used a weighted RMSSE.

Use the **training** data for the scale. If you use test data, you leak.

```check
{"q": "Your MASE is 0.8. What does it mean?", "type": "single",
 "options": ["Your error is 0.8%", "Your MAE is 20% lower than the naive method's in-sample MAE", "You are 0.8 units wrong"],
 "answer": 1,
 "why": ["MASE is a ratio, not a percent of the actual value.", "Correct: 0.8 means 20% smaller than the baseline error.", "MASE has no units. It is a ratio."]}
```

## Which metric to use?
| Situation | Good choice |
|---|---|
| One series, plain explanation | MAE |
| Big misses are very costly | RMSE |
| Many series, same unit, sales volume matters | WAPE |
| Many series of different scale, or zeros | MASE or RMSSE |
| Data far from zero and all positive | MAPE is acceptable, but still weak |
| Over- and under-forecasts cost differently | A quantile (pinball) loss — next lessons |

## Worked example
We compute all metrics by hand with numpy.

```python
import numpy as np

y = np.array([10.0, 20.0, 30.0, 40.0])        # actual (test)
f = np.array([12.0, 18.0, 33.0, 36.0])        # forecast
train = np.array([10.0, 12.0, 11.0, 13.0, 15.0, 14.0, 16.0, 18.0])

e = y - f
mae = np.abs(e).mean()
rmse = np.sqrt((e ** 2).mean())
mape = (np.abs(e) / np.abs(y)).mean() * 100
smape = (2 * np.abs(e) / (np.abs(y) + np.abs(f))).mean() * 100
wape = np.abs(e).sum() / np.abs(y).sum()

# MASE: scale = mean absolute one-step change in the TRAINING data (m = 1)
scale = np.abs(np.diff(train)).mean()
mase = mae / scale
# RMSSE: same idea with squared errors
rmsse = np.sqrt((e ** 2).mean() / (np.diff(train) ** 2).mean())

print("MAE  ", round(mae, 3))
print("RMSE ", round(rmse, 3))
print("MAPE ", round(mape, 2), "%")
print("sMAPE", round(smape, 2), "%")
print("WAPE ", round(wape, 3))
print("MASE ", round(mase, 3))
print("RMSSE", round(rmsse, 3))
# Output:
# MAE   2.75
# RMSE  2.872
# MAPE  12.5 %
# sMAPE 12.19 %
# WAPE  0.11
# MASE  1.604
# RMSSE 1.62
```

MASE above 1 here: this forecast is worse than the naive method on the training data. Note that this toy test series (10 to 40) has a bigger scale than the training series (10 to 18). In real work, check that the two periods are comparable.

## Common mistakes
- Using MAPE when the data has zeros (intermittent demand, small counts).
- Averaging MAPE over many series. Series with tiny values dominate the average.
- Computing the MASE scale on the test set instead of the training set.
- Comparing MAE across series of different units.
- Reporting only RMSE when you need to explain the result to a manager. MAE or WAPE is easier.
- Forgetting the season length `m` in MASE for strongly seasonal data.

## Interview lens
**Typical question:** "Why not use MAPE for demand forecasting?"

**Strong answer:** MAPE divides by the actual value. It is undefined at zero and very large near zero, which is common in retail data. It is also asymmetric: over-forecasts are punished more, so a model tuned for MAPE learns to forecast low. For one business number I prefer WAPE, which is total error divided by total sales. For comparing many series, I use MASE or RMSSE, which are scaled by a naive baseline on the training data. I also look at bias, the sign of the average error, because accuracy metrics hide it.

**Red flags:** "MAPE is the standard so I always use it"; not knowing what happens at y = 0; computing the MASE scale on test data; comparing RMSE of series with different units.

## Real world
- The M4 forecasting competition (2018) ranked methods by a combination of sMAPE and MASE (the overall weighted average, OWA).
- The M5 competition (Walmart sales) used the weighted RMSSE as the accuracy metric.
- Rob Hyndman and Anne Koehler proposed MASE in 2006 to fix the problems of percentage errors.

## Key points
- MAE is easy to read; RMSE punishes big errors more; both have the units of the data.
- MAPE fails at zero and is asymmetric. sMAPE is only a partial fix.
- WAPE = total error / total actual. It is a good business metric.
- MASE and RMSSE divide by a naive in-sample error, so they are scale-free. Below 1 means better than naive.
- Always report at least one metric that is scale-free and one in real units.
