---
id: s13-03-oa-pandas-wrangling
title: OA patterns - pandas wrangling and window loops
minutes: 35
level: intermediate
goals: [Fill missing timestamps per group with reindex, Join two irregular series with an as-of join without looking at the future, Write a one-pass window loop in plain Python, Run a calm 25-minute routine on each OA problem]
prereqs: [s13-01-how-interviews-work]
tags: [pandas, reindex, merge_asof, OA, window]
skills: [pandas-fluency, from-scratch]
---

## Warm-up

```check
{"q": "A table has daily sales but some days have no row. Which pandas call can add the missing days?", "type": "single",
 "options": ["df.sort_values()", "series.reindex(full_date_range)", "df.describe()", "series.shift(1)"],
 "answer": 1,
 "why": ["Sorting does not add rows.", "Correct: reindex makes the index equal to the full range and adds the missing rows.", "describe only summarises.", "shift moves values; it does not add dates."]}
```

```check
{"q": "You test a forecast model on a time series. Which split is correct?", "type": "single", "options": ["Random rows for test", "The last part of the time for test", "Every second row for test", "The first part of the time for test"], "answer": 1, "why": ["A random split lets the model see the future.", "Correct: test data must come after the training data.", "Neighbour rows leak information.", "Testing on the past and training on the future leaks the future."]}
```

## Why it matters

In an [[OA]] the data is rarely clean. Dates are missing. Sensors send at odd times. Each store has its own start date. The test is not about a hard algorithm. It is about **small, correct pandas steps** under a clock. These patterns come back again and again. If you know them, you finish early and have time to test edge cases.

## A calm routine for every problem

You have about 25 minutes per problem. Use the same five steps each time.

1. **Read twice.** Underline the output shape, the sort order, and the edge cases (empty, one row, ties).
2. **Write the example by hand** on paper. Check your idea on it.
3. **Write the simplest correct code.** Loops over groups are fine. Loops over rows are not.
4. **Run the visible tests.** Then add your own: empty input, one row, unsorted input.
5. **Clean up.** Check the index, the column order, and the sort order.

```check
{"q": "Which step do many candidates skip and then fail hidden tests?", "type": "single",
 "options": ["Reading the constraints", "Testing empty, one-row and unsorted inputs", "Naming variables", "Writing comments"],
 "answer": 1,
 "why": ["Reading matters, but the usual loss is in hidden edge cases.", "Correct: hidden tests almost always include empty, single-row, and unsorted data.", "Names do not change the result.", "Comments do not change the result."]}
```

## Pattern 1: fill missing timestamps per group

A [[reindex]] replaces an index by a new one. Rows that did not exist get a fill value. For many stores, do it **inside each group**, because each store has its own first and last date.

```chart
{"title": "Store with two missing days: after reindex the gaps are 0", "x": "day", "height": 200,
 "series": [
   {"name": "sales after fill", "kind": "bar", "x": [1,2,3,4,5,6,7], "y": [5, 0, 0, 7, 6, 0, 4]}
 ],
 "caption": "Days 2, 3 and 6 had no rows. After reindex they show 0. Nothing is added before day 1 or after day 7."}
```

Steps: `groupby("store")`, set `date` as index, `reindex(pd.date_range(first, last, freq="D"), fill_value=0)`, and collect the pieces.

```check
{"q": "Why must the date range be built per store, not once for the whole table?", "type": "single",
 "options": ["pandas forbids a global range", "A store may open later or close earlier; a global range adds fake days before it opened", "It is faster", "Because dates are strings"],
 "answer": 1,
 "why": ["pandas allows it, but the result is wrong for this task.", "Correct: a global range would create zeros before the store existed.", "Speed is not the reason.", "Date type does not matter here."]}
```

## Pattern 2: as-of join for irregular series

Two sensors send at different moments. An **[[as-of join]]** matches each row of the left table to the **latest earlier** row of the right table. In pandas it is `pd.merge_asof`.

Rules to remember:

- Sort both tables by the time column.
- Use `direction="backward"`. This takes only the past. `"nearest"` can take a future row. That is [[look-ahead]] leakage.
- Use `by="device"` so machines are not mixed.
- Use `tolerance` to ignore old values. Old values are often wrong.

Try it in the problem [[problem:merge-irregular-sensors]].

```check
{"q": "In merge_asof you want to use only readings from the past. Which setting is right?", "type": "single",
 "options": ["direction='forward'", "direction='nearest'", "direction='backward'", "No setting is needed; it is random"],
 "answer": 2,
 "why": ["Forward takes the next reading, from the future.", "Nearest can pick a future reading.", "Correct: backward takes the latest reading at or before the time.", "The direction is always explicit."]}
```

## Pattern 3: one-pass window loops

Some OA problems ask for a plain loop with O(n) time. Example: the longest stretch where the day-to-day change is small. Keep two numbers: the current run and the best run. Never compare with the start of the run. Compare with the **previous day**. Practise in [[problem:longest-calm-stretch]].

```check
{"q": "A list has 1,000,000 values. Which approach to find the longest calm stretch is fine?", "type": "single",
 "options": ["Check every pair of start and end days (O(n^2))", "One pass with a running counter (O(n))", "Sort the values first", "Convert to strings"],
 "answer": 1,
 "why": ["O(n^2) with a million values is too slow.", "Correct: a single pass is enough.", "Sorting destroys the time order.", "Strings do not help."]}
```

## Worked example

Fill the missing days for two stores, then attach the latest humidity to each temperature with an as-of join.

```python
import pandas as pd

# --- Part 1: fill missing days per store (each store has its own range)
df = pd.DataFrame({
    "store": ["A", "A", "B"],
    "date": pd.to_datetime(["2024-01-01", "2024-01-04", "2024-01-02"]),
    "sales": [5, 7, 3],
})
parts = []
for store, g in df.groupby("store"):
    s = g.set_index("date")["sales"]
    full = pd.date_range(s.index.min(), s.index.max(), freq="D")
    s = s.reindex(full, fill_value=0)          # new days get 0
    parts.append(pd.DataFrame({"store": store, "date": full, "sales": s.to_numpy()}))
filled = pd.concat(parts, ignore_index=True)
print(filled.to_string(index=False))

# --- Part 2: as-of join, past only, at most 60 seconds old
t = lambda s: pd.Timestamp("2024-06-01 " + s)
a = pd.DataFrame({"time": [t("10:00:30"), t("10:03:00")], "temp": [20.0, 21.0]})
b = pd.DataFrame({"time": [t("10:00:00"), t("10:00:50")], "humidity": [40.0, 45.0]})
m = pd.merge_asof(a, b, on="time", direction="backward", tolerance=pd.Timedelta(seconds=60))
print(m.to_string(index=False))
# Output:
# store       date  sales
#     A 2024-01-01      5
#     A 2024-01-02      0
#     A 2024-01-03      0
#     A 2024-01-04      7
#     B 2024-01-02      3
#                time  temp  humidity
# 2024-06-01 10:00:30  20.0      40.0
# 2024-06-01 10:03:00  21.0       NaN
```

At 10:00:30 the latest humidity is from 10:00:00. At 10:03:00 the latest is 130 seconds old, which is more than 60, so the result is `NaN`.

## Common mistakes

- One global date range for all groups.
- Forgetting to sort before `merge_asof` (pandas raises an error).
- `direction="nearest"` in a forecasting task: it looks at the future.
- Returning a wrong index or column order. Check what the statement asks.
- A Python loop over rows for 100,000 rows. Use group operations instead.
- Not testing the empty input.

## Interview lens

**Typical question:** "You have sensor readings with irregular timestamps from two sources. Build a table to train a model that predicts temperature."

**Strong answer:** "I would do an as-of join so each temperature row gets the latest earlier humidity, grouped by device. I set a tolerance, because a very old reading is stale, and I keep a flag or NaN for missing ones. I never use a nearest or future match, since that leaks information the model will not have at prediction time. I would check the share of rows with no match and the age of the matched values."

**Red flags:** using `merge` on exact timestamps; interpolating across devices; ignoring time zones; no tolerance.

## Real world

- IoT and observability systems store readings at irregular times. Engineers often align them with as-of joins before modelling. The `merge_asof` function in pandas was added for this purpose, mainly for financial tick data.
- Retail forecasting data sets often have no row when a store sold nothing. Teams must decide if a missing row means zero sales or missing data. In the Kaggle Store Sales data, for example, the daily table has gaps in the calendar, such as the end of each year.

## Key points

- Build the date range per group; reindex with `fill_value` to add missing days.
- Use `merge_asof` with `by`, `direction="backward"` and `tolerance` for irregular series.
- Window loops compare each day with the previous day, in one pass.
- Follow a 5-step routine and always test empty, single-row and unsorted input.
