---
slug: total-by-day
title: Total Sales per Day
difficulty: Easy
type: function
tags: [python, dict, loop]
skills: [pandas-fluency]
packages: []
companies_style: [retail]
---
A shop saves each sale as a pair `(day, amount)`. The same day can appear many times.

Write `total_by_day(sales)`. It returns a dict. Each key is a day. Each value is the sum of the amounts of that day.

### Example 1
**Input:** `sales = [("Mon", 5), ("Tue", 3), ("Mon", 2)]`
**Output:** `{"Mon": 7, "Tue": 3}`
**Explanation:** Monday has two sales, 5 and 2. Their total is 7.

### Constraints
- `0 <= len(sales) <= 10^5`
- `day` is a string. `amount` is a number.
- The order of keys in the dict does not matter.

### Hints
1. Start with an empty dict.
2. Loop over the pairs. For each pair, add the amount to the value of the day.
3. Use `totals.get(day, 0)` to read the old total. It gives 0 if the day is new.

### Solution explanation
1. Make an empty dict `totals`.
2. For each `(day, amount)`, set `totals[day] = totals.get(day, 0) + amount`.
3. Return `totals`.

Time O(n). Space O(k), where k is the number of different days. In pandas this is one line: `df.groupby("day")["amount"].sum()`. You will learn it in a later lesson.
