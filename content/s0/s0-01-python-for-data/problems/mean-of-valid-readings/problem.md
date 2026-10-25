---
slug: mean-of-valid-readings
title: Mean of Valid Readings
difficulty: Easy
type: function
tags: [python, list-comprehension]
skills: [pandas-fluency]
packages: []
companies_style: [sensor data, IoT]
---
A sensor sends one reading per hour. When the sensor fails, the reading is `None` (missing). Write `mean_valid(readings)`. It returns the mean of the readings that are **not** `None`.

If there is no valid reading, return `float("nan")`.

### Example 1
**Input:** `readings = [18.5, None, 21.5]`
**Output:** `20.0`
**Explanation:** The valid readings are 18.5 and 21.5. Their sum is 40.0 and there are 2 of them.

### Example 2
**Input:** `readings = [None, None]`
**Output:** `nan`
**Explanation:** No valid reading exists.

### Constraints
- `0 <= len(readings) <= 10^5`
- Each item is a float, an int, or `None`.

### Hints
1. Build a new list that holds only the values that are not `None`.
2. Use a list comprehension: `[r for r in readings if r is not None]`.
3. Check if the new list is empty before you divide.

### Solution explanation
1. Filter the list with a comprehension. Use `is not None`, not `!= None`. Also, do not use `if r`, because the valid reading `0` would be dropped.
2. If the filtered list is empty, return `nan`.
3. Otherwise return `sum(valid) / len(valid)`.

Time O(n), space O(n). A common bug is to divide by `len(readings)`, which counts the missing values too.
