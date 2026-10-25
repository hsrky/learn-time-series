---
id: s0-02-numpy-vectorization
title: numpy arrays and vectorization
minutes: 25
level: beginner
goals: [Create and read numpy arrays, Replace Python loops with vectorized code, Use broadcasting on rows and columns, Handle missing values with np.nan]
prereqs: [s0-01-python-for-data]
tags: [numpy, vectorization, broadcasting, nan]
skills: [pandas-fluency]
---
## Warm-up

```check
{"q": "steps = [3, 6, 9]. What does [s / 3 for s in steps] return?", "type": "single",
 "options": ["[1.0, 2.0, 3.0]", "[3, 6, 9]", "2.0"], "answer": 0,
 "why": ["Correct. It divides each value by 3.", "That is the original list.", "A comprehension builds a list, not one number."]}
```

```check
{"q": "Python starts counting positions at which number?", "type": "single",
 "options": ["0", "1", "-1"], "answer": 0,
 "why": ["Correct. The first value has position 0.", "Humans count from 1, but Python does not.", "-1 is the last value."]}
```

## Why it matters

A forecasting job can have millions of numbers. A Python loop handles them one at a time and is slow.

[[numpy]] stores numbers in one block of memory and works on all of them at once. This is called [[vectorization]]. It is often 10 to 100 times faster than a loop.

Every pandas and machine learning library is built on numpy. So this is the base for all that follows.

## Arrays

A numpy [[array]] is like a list, but all values have the same type. You make one from a list.

An array has a **shape**. A shape of `(7,)` means 7 values in one row. A shape of `(2, 3)` means 2 rows and 3 columns.

```python
import numpy as np

a = np.array([4200, 5100, 3900, 6000, 7200, 8100, 2500])
print(a.shape)       # (7,)  -> one dimension, 7 values
print(a.dtype)       # int64 -> every value is an integer
print(a[1:4])        # slices work like lists

m = np.array([[1, 2, 3],
              [4, 5, 6]])
print(m.shape)       # (2, 3) -> 2 rows, 3 columns
print(m[1, 2])       # row 1, column 2
# Output:
# (7,)
# int64
# [5100 3900 6000]
# (2, 3)
# 6
```

```check
{"q": "What is the shape of np.array([[1, 2, 3], [4, 5, 6]])?", "type": "single",
 "options": ["(3, 2)", "(2, 3)", "(6,)"], "answer": 1,
 "why": ["That would be 3 rows and 2 columns.", "Correct. There are 2 rows with 3 values each.", "That is a flat array with 6 values."]}
```

## Vectorization: no loop needed

With an array, an operation applies to **every** value. Compare the two ways.

Loop: `[x * 2 for x in values]`. Vectorized: `a * 2`.

You can also compare. `a > 5000` gives an array of True and False. This is a [[boolean mask]]. Put the mask inside brackets to keep only the True positions.

```python
import numpy as np

a = np.array([4200, 5100, 3900, 6000, 7200, 8100, 2500])

print(a * 2)                 # every value doubled
print(a - a.mean())          # distance from the mean
mask = a > 5000              # True where steps are above 5000
print(mask)
print(a[mask])               # keep only those values
print(a[mask].sum(), mask.sum())  # total of big days, and how many (True counts as 1)
# Output:
# [ 8400 10200  7800 12000 14400 16200  5000]
# [-1085.71428571  -185.71428571 -1385.71428571   714.28571429
#   1914.28571429  2814.28571429 -2785.71428571]
# [False  True False  True  True  True False]
# [5100 6000 7200 8100]
# 26400 4
```

```chart
{"title": "Mask: days above 5000 steps", "x": "day", "height": 210, "kind": "bar",
 "series": [{"name": "steps", "y": [4200, 5100, 3900, 6000, 7200, 8100, 2500]},
            {"name": "threshold 5000", "y": [5000, 5000, 5000, 5000, 5000, 5000, 5000], "kind": "line", "dash": true}],
 "caption": "Four bars are above the dashed line. The mask has True at exactly those four positions."}
```

```check
{"q": "a = np.array([1, 5, 9]). What is (a > 4).sum()?", "type": "numeric", "answer": 2, "tol": 0,
 "why": "a > 4 is [False, True, True]. True counts as 1, so the sum is 2."}
```

## Broadcasting

[[broadcasting]] lets numpy combine arrays of different shapes. A small array is "stretched" to match a big one.

Example: a table with 3 days (rows) and 2 sensors (columns). You want to subtract each sensor's mean from its column.

The column means have shape `(2,)`. The table has shape `(3, 2)`. numpy repeats the means for each row.

Rule: compare shapes **from the right**. Two sizes fit if they are equal or one of them is 1.

```python
import numpy as np

table = np.array([[10.0, 100.0],
                  [12.0, 140.0],
                  [14.0, 120.0]])      # shape (3, 2): 3 days, 2 sensors

col_mean = table.mean(axis=0)          # axis=0 -> down the rows -> one mean per column
print(col_mean)                        # shape (2,)
print(table - col_mean)                # (3,2) - (2,) works by broadcasting

row_mean = table.mean(axis=1, keepdims=True)   # keepdims keeps shape (3, 1)
print(table - row_mean)                # (3,2) - (3,1) also works
# Output:
# [ 12. 120.]
# [[ -2. -20.]
#  [  0.  20.]
#  [  2.   0.]]
# [[-45.  45.]
#  [-64.  64.]
#  [-53.  53.]]
```

```check
{"q": "A has shape (4, 3) and b has shape (3,). Does A + b work?", "type": "single",
 "options": ["Yes, b is repeated for each of the 4 rows", "No, the shapes are different", "Yes, but only if b has 4 values"],
 "answer": 0,
 "why": ["Correct. Compared from the right, 3 equals 3, and the missing leading size is stretched.", "Different shapes can work. The rule is about equal sizes or a size of 1.", "b has 3 values, which matches the 3 columns."]}
```

## Missing values: np.nan

[[nan]] means "not a number". We use it for a missing value. It is a float, so an array with nan has the float type.

nan is **contagious**: any sum with nan gives nan. Also `nan == nan` is False. Use `np.isnan` to find them.

Use the `nan` versions of the functions, such as `np.nanmean` and `np.nansum`. They skip the missing values.

```python
import numpy as np

x = np.array([2.0, np.nan, 4.0, 6.0])

print(x.mean())            # nan  (one nan poisons the result)
print(np.nanmean(x))       # 4.0  (ignores the nan)
print(np.isnan(x))         # [False  True False False]
print(x == np.nan)         # all False: never compare with ==
print(np.where(np.isnan(x), 0.0, x))   # replace nan with 0.0
# Output:
# nan
# 4.0
# [False  True False False]
# [False False False False]
# [2. 0. 4. 6.]
```

```check
{"q": "x = np.array([1.0, np.nan, 3.0]). What does np.nanmean(x) return?", "type": "numeric", "answer": 2.0, "tol": 0.0001,
 "why": "np.nanmean skips the nan. The mean of 1.0 and 3.0 is 2.0."}
```

## Worked example

Task: three sensors measure temperature on five days. One reading is missing. Standardize each sensor, so it has mean 0 and standard deviation 1. This is a [[z-score]].

Formula: z = (x − mean) / std

- x: one reading.
- mean: the average of that sensor.
- std: the [[standard deviation]] of that sensor. It tells how far values are from the mean on average.

```python
import numpy as np

# rows = 5 days, columns = 3 sensors; nan = missing reading
data = np.array([[20.0, 15.0, 30.0],
                 [22.0, 17.0, np.nan],
                 [21.0, 19.0, 33.0],
                 [25.0, 14.0, 36.0],
                 [24.0, 20.0, 31.0]])

# One mean and one std per column. nan-versions skip missing values.
mean = np.nanmean(data, axis=0)      # shape (3,)
std = np.nanstd(data, axis=0)        # shape (3,)

z = (data - mean) / std              # broadcasting: (5,3) with (3,)

print(np.round(mean, 2))
print(np.round(z, 2))
# The same z-score without any Python loop over rows or columns.
print(np.allclose(np.nanmean(z, axis=0), 0))   # True: every sensor now has mean 0
# Output:
# [22.4 17.  32.5]
# [[-1.29 -0.88 -1.09]
#  [-0.22  0.     nan]
#  [-0.75  0.88  0.22]
#  [ 1.4  -1.32  1.53]
#  [ 0.86  1.32 -0.65]]
# True
```

Notice: the missing value stays `nan` in the result. The other values are still correct.

## Common mistakes

- Using `==` to find nan. Use `np.isnan`.
- Writing a Python loop over a big array. Look for a vectorized form first.
- Forgetting `axis`. `axis=0` goes down the rows (one result per column). `axis=1` goes across the columns (one result per row).
- Confusing shapes `(3,)` and `(3, 1)`. They broadcast in different ways.
- Using `np.mean` on data with nan and getting nan back.

## Interview lens

**Typical question:** "Standardize each column of a 2D array without a loop. Missing values are nan."

**Strong answer:** Compute the mean and the standard deviation per column with `axis=0`. Use the `nan` versions so missing values do not break the result. Subtract and divide by broadcasting. Say that a column with zero spread would divide by zero, and show how you guard against it. Mention the cost: one pass over the data, O(n).

**Red flags:**
- Looping over rows in Python.
- Using `np.mean` with nan present.
- Not knowing what `axis` means.

## Real world

- numpy is the base of the Python scientific stack. pandas, scikit-learn and PyTorch all use arrays like these.
- The M5 forecasting competition (Walmart sales data) had tens of thousands of daily series. At this size, vectorized code is a necessity.

## Key points

- An array holds same-type numbers in a shape. Operations apply to all values at once (vectorization).
- A boolean mask such as `a > 5` selects values. Summing a mask counts the True values.
- Broadcasting compares shapes from the right. Sizes must be equal or 1.
- nan marks a missing value. Test it with `np.isnan` and use `nanmean`, `nansum` and friends.
