---
slug: demand-classification
title: Classify Demand with ADI and CV2
difficulty: Easy
type: function
tags: [intermittent-demand, adi, cv2, classification]
skills: [metrics, pandas-fluency]
packages: []
companies_style: [spare parts, retail assortment]
---
Before you pick a forecasting method for thousands of items, classify each demand series.

Write `classify_demand(y)` for a list of non-negative demands.

- `ADI` = `len(y) / (number of periods with y > 0)`
- `CV2` = `(std / mean) ** 2` of the **positive** values only. Use the population standard deviation (`np.std`, `ddof=0`).

Return a dict `{"adi": ADI, "cv2": CV2, "class": name}` with ADI and CV2 rounded to 4 decimals. The class depends on the cut-offs ADI = 1.32 and CV2 = 0.49:

- `"smooth"`: `ADI <= 1.32` and `CV2 <= 0.49`
- `"erratic"`: `ADI <= 1.32` and `CV2 > 0.49`
- `"intermittent"`: `ADI > 1.32` and `CV2 <= 0.49`
- `"lumpy"`: `ADI > 1.32` and `CV2 > 0.49`

If there is no positive value, return `{"adi": None, "cv2": None, "class": "no demand"}`.

Also write `classify_table(df)` for a `DataFrame` with one column per item (rows are periods). Return a `DataFrame` with the item names as index and columns `adi`, `cv2`, `class`.

### Example 1
**Input:** `classify_demand([0, 0, 5, 0, 0, 0, 3, 0, 4])`
**Output:** `{"adi": 3.0, "cv2": 0.0417, "class": "intermittent"}`
**Explanation:** 3 demands in 9 periods give ADI = 3. The positive values 5, 3, 4 have mean 4 and std 0.8165, so CV2 = (0.8165 / 4)^2 = 0.0417.

### Example 2
**Input:** `classify_demand([10, 12, 9, 11])`
**Output:** class `"smooth"`: every period has demand and the sizes vary little.

### Constraints
- `1 <= len(y) <= 10^5`
- Use numpy or pandas, no Python loop over periods.

### Hints
1. `pos = y[y > 0]` gives the positive values.
2. `adi = len(y) / len(pos)`.
3. For the table version use `df.apply(...)` over the columns, or a loop over the column names.

### Solution explanation
ADI measures how often demand occurs and CV2 measures how much the sizes vary. The grid of cut-offs (Syntetos, Boylan and Croston) says which forecasting family fits: smooth and erratic series suit normal methods, intermittent and lumpy series suit Croston-type methods. Time O(n) per item. Common bugs: using all periods (with zeros) for the CV2, using the sample std instead of the population std, and comparing with `<` instead of `<=` at the cut-offs.
