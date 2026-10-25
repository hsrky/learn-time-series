---
id: s10-01-point-in-time-correctness
title: Point-in-time correctness and feature stores
minutes: 25
level: advanced
goals: [Explain why a feature must be known at prediction time, Build a point-in-time join with merge_asof, Describe what a feature store does]
prereqs: [s1-03-resampling]
tags: [leakage, feature-store, merge_asof, production]
skills: [leakage-free-features, ml-system-design]
---

## Warm-up

```check
{"q": "You forecast sales for 10 May. Which feature is safe to use?", "type": "single",
 "options": ["Sales of 10 May", "Average sales of 3 to 9 May", "Average sales of 8 to 12 May"],
 "answer": 1,
 "why": ["This is the value you want to predict. Using it is leakage.", "Correct: all of these days are in the past on 10 May.", "It includes days after 10 May. You do not know them yet."]}
```

```check
{"q": "What does 'data leakage' mean?", "type": "single",
 "options": ["The model uses information that will not exist at prediction time", "Some rows are missing from the data", "The model is too slow in production"],
 "answer": 0,
 "why": ["Correct. The score looks great in the notebook and fails in real use.", "That is missing data, a different problem.", "That is a speed problem, not leakage."]}
```

## Why it matters

A team builds a model that predicts food-delivery time. In the notebook the error is tiny. In production it is three times worse. The reason: the training table used the **final** value of "driver count in the area", a number that was fixed later in the day. At prediction time that number was still changing. The model had seen the future. This is [[data leakage|leakage]]. This lesson shows how to stop this with **[[point-in-time correctness]]**.

## What "point-in-time" means

**Point-in-time correctness** means this: for every training row, each feature has the value that was *known at that moment*, and not a later value.

Example. A store has a feature "orders in the last 7 days". It is recomputed every night at 02:00.

| Time | Feature value known |
|---|---|
| Mon 02:00 | 410 |
| Tue 02:00 | 455 |
| Wed 02:00 | 430 |

A label (a real order) arrives on Tue 15:00. The correct feature is **455**, the value from Tue 02:00. Not 430, because Wed 02:00 is in the future. The rule is: take the **latest** feature value with `feature_time <= label_time`.

```chart
{"title": "A feature that updates once per day", "x": "hour", "height": 220,
 "series": [
   {"name": "feature value (known)", "gen": [["const", {"value": 410}], ["step", {"at": 24, "size": 45}], ["step", {"at": 48, "size": -25}]], "n": 72, "kind": "line"}
 ],
 "marks": [{"x": 37, "label": "label time: use 455"}],
 "caption": "At hour 37 the right value is 455. The drop to 430 happens at hour 48, in the future."}
```

```check
{"q": "A label is at Tue 15:00. Features are known at Mon 02:00 (410), Tue 02:00 (455) and Wed 02:00 (430). Which value is point-in-time correct?", "type": "numeric",
 "answer": 455, "tol": 0.1,
 "why": "Pick the latest feature time that is not after the label time: Tue 02:00, so 455."}
```

## The tool: merge_asof

A normal join needs equal keys. Times almost never match exactly. **[[merge_asof|`pd.merge_asof`]]** matches each left row to the *nearest earlier* row on the right. This is exactly the point-in-time rule.

Rules for `merge_asof`:

- Both tables must be **sorted** by the time key. If not, pandas raises an error.
- `direction="backward"` (the default) takes the latest right row with time **at or before** the left time.
- `by="store"` does the match inside each store (each entity).
- `tolerance=pd.Timedelta("1D")` (a [[tolerance]]) rejects values that are too old. Then you get NaN, which is honest: the feature is stale.
- `allow_exact_matches=False` makes the rule "strictly before".

```check
{"q": "What does direction='forward' in merge_asof do for a training set?", "type": "single",
 "options": ["It is the correct choice for point-in-time joins", "It takes a value from the future, so it creates leakage", "It sorts the table for you"],
 "answer": 1,
 "why": ["No. Forward looks for the next row after the label time.", "Correct: forward takes the nearest later row. That is the future.", "merge_asof never sorts. You must sort first."]}
```

## Feature stores

A **[[feature store]]** is a system that keeps feature values *with their timestamps*. It has two sides:

- **[[offline store|Offline store]]**: the full history, used to build training sets with point-in-time joins.
- **[[online store|Online store]]**: only the latest value per entity, read in milliseconds when the model serves a request.

The big benefit is **training-serving consistency**: the same feature code and definition is used for training and for serving. Without it, teams write the feature twice (SQL for training, Java for serving) and the two versions slowly differ. This is called **[[training-serving skew]]**.

Open-source example: Feast. Cloud examples exist too. You do not need to know product details in an interview. You need to know the two stores and the point-in-time join.

```check
{"q": "Why do teams keep an online store AND an offline store?", "type": "single",
 "options": ["Offline stores are faster than online stores", "Offline has full history for training; online has the latest value for fast serving", "Online is only a backup of offline"],
 "answer": 1,
 "why": ["No. Offline stores are large and slower.", "Correct: two different access patterns need two storage designs.", "It is not a backup. Each side has its own job."]}
```

## Worked example

We join three delivery orders to a feature table that updates at different times for two stores.

```python
import pandas as pd

orders = pd.DataFrame({
    "store": ["A", "A", "B", "B"],
    "ts": pd.to_datetime(["2024-03-05 15:00", "2024-03-06 09:00",
                          "2024-03-05 15:00", "2024-03-09 12:00"]),
    "minutes": [31, 28, 40, 35],
})
feat = pd.DataFrame({
    "store": ["A", "A", "A", "B", "B"],
    "feature_ts": pd.to_datetime(["2024-03-04 02:00", "2024-03-05 02:00", "2024-03-06 02:00",
                                  "2024-03-04 02:00", "2024-03-06 02:00"]),
    "orders_7d": [410, 455, 430, 300, 320],
})

# Both sides must be sorted by their time column.
orders = orders.sort_values("ts")
feat = feat.sort_values("feature_ts")

out = pd.merge_asof(orders, feat, left_on="ts", right_on="feature_ts",
                    by="store", direction="backward",
                    tolerance=pd.Timedelta("2D"))
cols = ["store", "ts", "feature_ts", "orders_7d"]
print(out[cols].to_string(index=False))
# Output:
# store                  ts          feature_ts  orders_7d
#     A 2024-03-05 15:00:00 2024-03-05 02:00:00      455.0
#     B 2024-03-05 15:00:00 2024-03-04 02:00:00      300.0
#     A 2024-03-06 09:00:00 2024-03-06 02:00:00      430.0
#     B 2024-03-09 12:00:00                 NaT        NaN
```

Look at the last row: the latest feature for store B is 3 days old, more than the 2-day tolerance, so the result is NaN. A stale feature is better shown as missing than silently used.

## Common mistakes

- Joining on the **date** only (`df.merge(feat, on="date")`). A daily feature computed at the end of the day then leaks into events earlier that day.
- Forgetting to sort. Or sorting only by time and not by the `by` column in an old pandas version.
- Using `direction="nearest"`. It can pick a future row.
- Computing features with the *final* corrected data (late-arriving fixes) instead of the data as it looked then.
- Computing a target-based feature (like store mean of the label) on the full dataset before the split.

## Interview lens

**Typical question:** "Your model is great offline and bad online. What do you check first?"

**Strong answer:** I check for leakage and training-serving skew. I ask for each feature: is it available at prediction time, and with which delay? I rebuild the training set with a point-in-time join so each row sees only the feature values known at that time. I compare the feature distribution in the training set with the logged serving features. If a feature store exists, I make sure both paths use the same feature definition.

**Red flags:** Saying "just add more data". Joining on date only. Not knowing that late data and backfills change history. Random shuffling of rows before a time-based split.

## Real world

Feature stores became common in large ML teams after about 2017. Uber described its Michelangelo platform with a shared feature store, and Feast is a well-known open-source feature store. Their public documents all stress the same two points: reuse of features and point-in-time correct training data.

## Key points

- A training row may only use feature values known at its own timestamp.
- Use `pd.merge_asof(..., direction="backward", by=entity, tolerance=...)` and sort both tables first.
- A feature store has an offline store (history) and an online store (latest value).
- One feature definition for training and serving prevents training-serving skew.
- When data arrives late, store *when you knew it*, not only *what it describes*.
