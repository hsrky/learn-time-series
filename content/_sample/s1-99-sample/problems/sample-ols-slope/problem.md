---
slug: sample-ols-slope
title: Trend Slope with statsmodels
difficulty: Medium
type: function
tags: [statsmodels]
skills: [from-scratch]
packages: [statsmodels]
---
Fit a line `y = a + b*t` with statsmodels OLS and return `b`.

### Hints
1. Build `t = arange(n)`.
2. `sm.add_constant`.
3. `.params[1]`.

### Solution explanation
OLS on time index.
