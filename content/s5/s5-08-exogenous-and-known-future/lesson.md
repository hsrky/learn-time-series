---
id: s5-08-exogenous-and-known-future
title: Exogenous variables, known-future covariates and point-in-time joins
minutes: 30
level: intermediate
goals: [Sort covariates into known-future, past-only and static, Avoid training-serving skew with forecast covariates, Join features with pd.merge_asof so that each row sees only what was known]
prereqs: [s5-03-calendar-holidays-target-encoding, s5-05-multistep-strategies]
tags: [exogenous, covariates, merge_asof, point-in-time, leakage]
skills: [leakage, production, pandas-fluency]
---
## Warm-up
```check
{"q": "A recursive multi-step forecast uses price as a feature. What do you need for step 5?", "type": "single",
 "options": ["The price for the date of step 5, known or forecast", "Nothing", "The price of step 1 only"],
 "answer": 0,
 "why": ["Correct: each step needs the covariate for its own date.", "The model asks for the feature at every step.", "Step 5 is a different date, so it needs its own value."]}
```

```check
{"q": "Which feature is known years in advance?", "type": "single",
 "options": ["Day of week", "Competitor price", "Tomorrow's weather"],
 "answer": 0,
 "why": ["Correct: the calendar is fixed.", "Competitors decide later.", "Weather is only forecast."]}
```

## Why it matters
Price, promotions, weather, holidays and marketing spend explain a lot of the movement of a series. These are **[[exogenous variable|exogenous]]** variables: they come from outside the series. They can lift a model a lot. They are also the number one source of hidden leakage in production: in testing you have the real weather of tomorrow, but in production you only have a forecast. A model trained on perfect covariates then fails.

## Three types of covariates
Ask one question: **"At the forecast origin, do I know the value for the target date?"**

| Type | Known at forecast time? | Examples | How to use |
|---|---|---|---|
| **[[known-future covariate|Known-future]]** | Yes, for the whole horizon | calendar, holidays, planned promotions, price lists, scheduled events | Use the value of the target date directly |
| **[[past-only covariate|Past-only]]** (observed) | Only up to the origin | actual weather, competitor sales, web traffic, stock levels | Use lags (value at or before the origin) |
| **Static** | Always | store type, region, product group | Use as a constant feature |

Example: you forecast sales for next Monday on Friday. The planned Monday promotion is known-future. The actual Monday temperature is not known. Use last week's temperature (past-only) or a weather forecast.

```check
{"q": "You forecast demand 7 days ahead. Which covariate can you use for the target day without any extra forecast?", "type": "single",
 "options": ["Planned promotion calendar", "Actual temperature on the target day", "Competitor's sales on the target day"],
 "answer": 0,
 "why": ["Correct: planned, so known in advance.", "Not known yet; at best a forecast exists.", "Unknown until the day has passed."]}
```

## Forecast covariates and training-serving skew
Sometimes a covariate is unknown, but a forecast of it exists (weather forecast, a macro forecast). You can use the forecast. But think about **what you train with**.

- In production the model gets the **forecast** issued before the target date, with its errors.
- If you train with the **actual** values, the model learns to trust the covariate too much. This is **[[training-serving skew]]**.
- Better: train with the forecasts that were available at the time (stored with their issue time), or add noise.

If you cannot get past forecasts, use only past-only lags of the covariate.

```check
{"q": "You trained a model with the actual temperature. In production you only have the weather forecast. What is the risk?", "type": "single",
 "options": ["The model trusts the temperature too much and the real error is bigger than in testing", "None, forecast and actual are the same", "The model cannot run"],
 "answer": 0,
 "why": ["Correct: this is training-serving skew.", "Forecasts have errors, so they differ from the actual values.", "It runs, but the test score is too optimistic."]}
```

## Point-in-time joins with merge_asof
Features often come as a separate table with timestamps: price changes, stock levels, user plan updates. You want, for each row, the **latest value that was known at that row's time**. This is a **[[point-in-time join]]** ("as-of join").

A normal `merge` on dates matches only exact equal timestamps. `pd.merge_asof` matches each row with the **nearest earlier** row of the other table:

```
pd.merge_asof(left, right, left_on="time", right_on="effective_at",
              by="item", direction="backward", tolerance=pd.Timedelta("7D"))
```

- `direction="backward"`: the latest right row at or before the left time. This is the safe choice.
- `direction="forward"`: the next right row **after** the left time. That is future information, so it is a leak.
- `by`: match only inside the same group (same item).
- `tolerance`: if the latest value is older than this, give `NaN`.
- Both tables must be **sorted** by the time key.
- `allow_exact_matches`: whether a value with the same timestamp counts.

```chart
{"title": "Price valid over time (hours from Jan 1, 00:00)", "x": "hour", "height": 200, "series": [{"name": "price valid at that time", "x": [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72], "y": [10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8]}], "marks": [{"x": 56, "label": "order at Jan 3, 08:00"}], "caption": "At the order time the valid price is 9.0. The price 8.0 starts one hour later, so a forward join would leak it."}
```

Another detail: data that is revised later (such as economic numbers) needs the **[[vintage]]**: the value as it was known at that time, not the final value.

```check
{"q": "Which merge_asof direction avoids a leak when you add 'latest known price' to an order?", "type": "single",
 "options": ["backward", "forward", "nearest"],
 "answer": 0,
 "why": ["Correct: it takes the latest price at or before the order time.", "It takes a later price, which was not known.", "Nearest can pick a later row too, so it can leak."]}
```

## Worked example
Orders happen at several times. The price table shows when each new price started. We join the price that was valid at each order time, and compare with the wrong forward join.

```python
import pandas as pd

orders = pd.DataFrame({
    "time": pd.to_datetime(["2024-01-01 09:00", "2024-01-01 15:00",
                            "2024-01-02 10:00", "2024-01-03 08:00"]),
    "units": [5, 7, 6, 9],
})
price = pd.DataFrame({
    "effective_at": pd.to_datetime(["2023-12-31 00:00", "2024-01-01 12:00", "2024-01-03 09:00"]),
    "price": [10.0, 9.0, 8.0],
})

# Both tables must be sorted by their time key (they are).
safe = pd.merge_asof(orders, price, left_on="time", right_on="effective_at",
                     direction="backward")
leak = pd.merge_asof(orders, price, left_on="time", right_on="effective_at",
                     direction="forward")

print(safe.loc[:, ["time", "units", "price"]])
print("forward join price for the last order:", leak["price"].iloc[-1])
# Output:
#                  time  units  price
# 0 2024-01-01 09:00:00      5   10.0
# 1 2024-01-01 15:00:00      7    9.0
# 2 2024-01-02 10:00:00      6    9.0
# 3 2024-01-03 08:00:00      9    9.0
# forward join price for the last order: 8.0
```

The last order is at 2024-01-03 08:00. The price that was valid then is 9.0 (set on Jan 1 at 12:00). The forward join takes 8.0, which only starts one hour later. A model trained with the forward join sees a price it could not know.

## Common mistakes
- Using actual weather, actual competitor data or actual prices of the target date as features.
- Training on perfect covariates and serving with noisy forecasts.
- Merging on the date only, so that a value from later in the day is used.
- Forgetting to sort the tables before `merge_asof` (it raises an error).
- Using `direction="nearest"` or `"forward"`.
- Ignoring publication delay: a monthly number for January is published in February; its available time is February.
- Using the final revised value of a number that was first published with errors.

## Interview lens
**Typical question:** "You add weather to a demand model and the test error falls by half. What do you check?"

**Strong answer:** First I ask whether the weather value for the target date is known at forecast time. If I used the actual weather, the real gain will be smaller because production only has a forecast. I would retrain with the weather forecast as it was issued before the target date, or use lagged weather only. I make sure that the join is point-in-time: each row gets the latest value available at its prediction time, for example with `merge_asof` backward. And I check the improvement in a walk-forward backtest that copies production.

**Red flags:** "Weather helps, so I add it" without asking when it is known; random split; merging by date only; not knowing about training-serving skew.

## Real world
- [[feature store|Feature stores]] such as Feast and Tecton offer "point-in-time correct" joins. Leaking future feature values is a common failure in machine learning systems.
- Many forecasting libraries (for example Darts, GluonTS, Nixtla) separate "past covariates" from "future covariates" in their API for the same reason.
- Chronos-2 (Amazon, 2025) supports covariates, and its documentation distinguishes past-only and known-future variables.

## Key points
- Ask: "Is this value known for the target date at the forecast origin?" Known-future, past-only or static.
- Use past-only covariates through lags; forecast covariates only if you train on past forecasts.
- Training-serving skew: train on what you will really have in production.
- Use `pd.merge_asof(..., direction="backward")` for point-in-time joins, with `by` and `tolerance`.
- Remember publication delays and data revisions.
