---
id: s0-03-pandas-series-dataframe
title: pandas Series, DataFrame and index alignment
minutes: 25
level: beginner
goals: [Create a Series and a DataFrame, Select rows with loc iloc and filters, Explain index alignment and why it makes NaN, Find and fill missing values]
prereqs: [s0-02-numpy-vectorization]
tags: [pandas, series, dataframe, alignment]
skills: [pandas-fluency]
---
## Warm-up

```check
{"q": "a has shape (3, 4) and b has shape (4,). What happens with a - b?", "type": "single",
 "options": ["b is stretched over the 3 rows (broadcasting)", "An error, shapes must be equal", "b is cut to 3 values"], "answer": 0,
 "why": ["Correct. From the right, 4 equals 4, so b is repeated for each row.", "Equal shapes are not required.", "numpy never cuts data to fit."]}
```

```check
{"q": "Which function gives the mean and skips nan?", "type": "single",
 "options": ["np.nanmean", "np.mean", "np.isnan"], "answer": 0,
 "why": ["Correct.", "np.mean returns nan if any value is nan.", "np.isnan only tests for nan."]}
```

## Why it matters

Real data comes with labels: dates, store names, sensor names. A numpy array has only positions.

[[pandas]] adds **labels** to arrays. Then you can ask for "sales on 2024-03-05" instead of "the 64th number".

Labels have a second effect: pandas matches values **by label** when you combine data. This saves you from many bugs, and it creates a few surprises. You must know both.

## Series

A [[Series]] is a one-dimensional array with a label for each value. The labels are called the [[index]].

Think of a column in a spreadsheet, plus its row labels.

Use `.loc[label]` to select by label. Use `.iloc[position]` to select by position.

```python
import pandas as pd

sales = pd.Series([120, 135, 90, 160], index=["Mon", "Tue", "Wed", "Thu"], name="sales")
print(sales)
print(sales.loc["Tue"])        # by label
print(sales.iloc[0])           # by position
print(sales["Wed":"Thu"])      # label slice: the end label IS included
print(sales[sales > 100])      # filter with a boolean mask, like numpy
# Output:
# Mon    120
# Tue    135
# Wed     90
# Thu    160
# Name: sales, dtype: int64
# 135
# 120
# Wed     90
# Thu    160
# Name: sales, dtype: int64
# Mon    120
# Tue    135
# Thu    160
# Name: sales, dtype: int64
```

```check
{"q": "s = pd.Series([5, 6, 7], index=['a', 'b', 'c']). What is s.loc['a':'b']?", "type": "single",
 "options": ["Only the value for a", "The values for a and b", "The values for a, b and c"], "answer": 1,
 "why": ["Label slices include the end label.", "Correct. Unlike positions, a label slice includes the last label.", "c is after the end label."]}
```

## DataFrame

A [[DataFrame]] is a table. It has an index for the rows and **column names**. Each column is a Series.

Select one column with `df["col"]` (a Series) or several by giving a list of names (a DataFrame). Add a new column by assigning to a new name.

```python
import pandas as pd

df = pd.DataFrame(
    {"store": ["A", "A", "B", "B"],
     "units": [10, 12, 7, 9],
     "price": [2.5, 2.5, 4.0, 4.0]},
    index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]),
)
df["revenue"] = df["units"] * df["price"]     # new column, computed for all rows
print(df)
print(df.loc[df["store"] == "A", "revenue"])   # rows where store is A, column revenue
print(df.dtypes)
# Output:
#            store  units  price  revenue
# 2024-01-01     A     10    2.5     25.0
# 2024-01-02     A     12    2.5     30.0
# 2024-01-01     B      7    4.0     28.0
# 2024-01-02     B      9    4.0     36.0
# 2024-01-01    25.0
# 2024-01-02    30.0
# Name: revenue, dtype: float64
# store       object
# units        int64
# price      float64
# revenue    float64
# dtype: object
```

```check
{"q": "How do you add a column 'total' as the sum of columns a and b?", "type": "single",
 "options": ["df['total'] = df['a'] + df['b']", "df.total = a + b", "df.add('total')"], "answer": 0,
 "why": ["Correct. The right side is a Series; the assignment creates the column.", "a and b are not variables here. They are columns.", "There is no such call."]}
```

## Index alignment

When you add two Series, pandas matches them by **index label**, not by position. This is [[index alignment]].

If a label exists in only one Series, there is no partner. The result is `NaN` (missing).

Example below: store A has days 1 to 3, store B has days 2 to 4. Only days 2 and 3 exist in both.

```chart
{"title": "Two stores, partly different days", "x": "day", "height": 210, "kind": "dots",
 "series": [{"name": "store A (days 1-3)", "x": [1, 2, 3], "y": [10, 12, 14]},
            {"name": "store B (days 2-4)", "x": [2, 3, 4], "y": [1, 2, 3]}],
 "caption": "A + B has values on days 2 and 3 only. Days 1 and 4 become NaN. Use add(..., fill_value=0) to treat a missing day as 0."}
```

```python
import pandas as pd

a = pd.Series([10, 12, 14], index=[1, 2, 3])
b = pd.Series([1, 2, 3], index=[2, 3, 4])

print(a + b)                       # aligned by label; days 1 and 4 have no partner
print(a.add(b, fill_value=0))      # a missing partner counts as 0
# Output:
# 1     NaN
# 2    13.0
# 3    16.0
# 4     NaN
# dtype: float64
# 1    10.0
# 2    13.0
# 3    16.0
# 4     3.0
# dtype: float64
```

```check
{"q": "a has index [1, 2, 3] and b has index [3, 4]. How many values are NaN in a + b?", "type": "numeric", "answer": 3, "tol": 0,
 "why": "The result index is [1, 2, 3, 4]. Only label 3 is in both. Labels 1, 2 and 4 are NaN, so 3 values are NaN."}
```

## Missing values

pandas marks missing values as `NaN`. Find them with `isna()`. Count them with `isna().sum()`.

Two ways to handle them: `dropna()` removes the rows. `fillna(value)` replaces them.

Important for time series: **the choice matters**. Filling with a constant, a mean or a neighbor value gives different results. We study this in Stage 1.

```python
import numpy as np
import pandas as pd

s = pd.Series([1.0, np.nan, 3.0, np.nan, 5.0])
print(s.isna().sum())          # how many missing
print(s.mean())                # pandas skips NaN by default (unlike numpy)
print(s.dropna().tolist())     # remove them
print(s.fillna(0).tolist())    # replace with 0
# Output:
# 2
# 3.0
# [1.0, 3.0, 5.0]
# [1.0, 0.0, 3.0, 0.0, 5.0]
```

```check
{"q": "s = pd.Series([2.0, None, 4.0]). What is s.mean()?", "type": "numeric", "answer": 3.0, "tol": 0.0001,
 "why": "pandas skips NaN by default. The mean of 2.0 and 4.0 is 3.0."}
```

## Worked example

Task: two warehouses report daily shipments, but not on the same days. Find the total shipments for each day, treating a missing report as 0. Then list the days with more than 15 shipments.

```python
import pandas as pd

north = pd.Series([8, 9, 7, 12], index=pd.to_datetime(["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04"]))
south = pd.Series([5, 6, 10], index=pd.to_datetime(["2024-03-02", "2024-03-04", "2024-03-05"]))

# 1) Plain + would give NaN for days that appear in only one series.
print((north + south).isna().sum(), "days are NaN with plain +")

# 2) add() with fill_value treats a missing report as 0.
total = north.add(south, fill_value=0)
print(total)

# 3) Filter with a boolean mask, then read the labels of the result.
busy = total[total > 15]
print(busy.index.strftime("%Y-%m-%d").tolist())
# Output:
# 3 days are NaN with plain +
# 2024-03-01     8.0
# 2024-03-02    14.0
# 2024-03-03     7.0
# 2024-03-04    18.0
# 2024-03-05    10.0
# dtype: float64
# ['2024-03-04']
```

Notice: the result is sorted by date and has the union of both indexes.

## Common mistakes

- Expecting `a + b` to match by position. It matches by label.
- Treating NaN as a normal number. `NaN == NaN` is False. Use `isna()`.
- Using `df["a"]["b"] = 1` to assign (chained assignment). Use `df.loc["b", "a"] = 1`.
- Confusing `loc` (labels, end included) with `iloc` (positions, end excluded).
- Filling missing values with 0 when 0 is a real value with a different meaning.

## Interview lens

**Typical question:** "Two Series have different dates. Add them and explain what happens to dates that are in only one of them."

**Strong answer:** pandas aligns both Series on the index, so the result has the union of the dates. Dates present in only one Series give NaN. I choose on purpose: `add(other, fill_value=0)` if a missing report really means zero, or keep NaN if it means unknown. I check `isna().sum()` after. I also check that both indexes are sorted and have the same timezone.

**Red flags:**
- Not knowing that alignment exists.
- Calling `fillna(0)` on every problem.
- Using a loop over dates.

## Real world

- Alignment by label is a main reason finance teams use pandas. Pandas was started by Wes McKinney in 2008 at a hedge fund, AQR Capital, for working with financial time series.
- In forecasting pipelines, a silent misalignment of dates between a target and a feature is a classic source of wrong results.

## Key points

- A Series is values plus an index. A DataFrame is a table of Series that share an index.
- `loc` selects by label (end included). `iloc` selects by position (end excluded).
- Operations align on index labels. Labels without a partner give NaN.
- Count missing values with `isna().sum()`. Choose `dropna` or `fillna` on purpose.
