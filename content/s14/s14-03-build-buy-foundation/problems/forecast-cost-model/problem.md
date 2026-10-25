---
slug: forecast-cost-model
title: Build vs Buy Cost Model
difficulty: Medium
type: function
tags: [staff, cost-model, build-vs-buy, foundation-model]
skills: [staff, scale]
packages: []
companies_style: [platform planning, vendor choice]
---
Your team can serve forecasts in several ways: build your own LightGBM service, call a vendor API, or host an open foundation model on GPUs. Each option has a **monthly fixed cost** (people, servers) and a **variable cost per 1,000 forecasts**. Each also has a typical **latency** in milliseconds.

The monthly cost of an option for a volume of `volume` forecasts per month is:

`cost = fixed + per_1k * volume / 1000`

Write two functions.

**1. `choose_option(options, volume, max_latency_ms)`**

`options` is a list of dicts with keys `name`, `fixed`, `per_1k`, `latency_ms`. Ignore options whose `latency_ms` is **greater than** `max_latency_ms`. Among the others, find the cheapest. Return a dict:

- `"best"`: the name of the cheapest feasible option (if two have the same cost, the name that is first in alphabetical order)
- `"cost"`: its monthly cost
- `"ranking"`: the list of feasible names sorted by cost, then by name

If no option is feasible, return `{"best": None, "cost": None, "ranking": []}`.

**2. `breakeven_volume(a, b)`**

`a` and `b` are two option dicts. Return the monthly volume at which both cost the same. Return `None` if the lines never cross at a positive volume (parallel lines, or the crossing is at a negative volume or at 0).

### Example 1
**Input:**
```
options = [
  {"name": "build", "fixed": 20000, "per_1k": 0.02, "latency_ms": 50},
  {"name": "api",   "fixed": 0,     "per_1k": 1.00, "latency_ms": 400},
]
choose_option(options, 10_000_000, 1000)
```
**Output:** `{"best": "api", "cost": 10000.0, "ranking": ["api", "build"]}`
**Explanation:** At 10 million forecasts, build costs 20,000 + 0.02 × 10,000 = 20,200. The API costs 1.00 × 10,000 = 10,000. The API is cheaper at this volume.

### Example 2
**Input:** `breakeven_volume(build, api)` with the same options
**Output:** `20408163.26530612`
**Explanation:** 20,000 + 0.02·v/1000 = 1.00·v/1000, so v = 20,000 × 1000 / 0.98.

### Constraints
- 0 ≤ number of options ≤ 50
- All numbers are ≥ 0
- Return costs as floats

### Hints
1. Filter first: `[o for o in options if o["latency_ms"] <= max_latency_ms]`.
2. Compute the cost for each, then sort by `(cost, name)`.
3. For the break-even, solve `fixed_a + pa·v/1000 = fixed_b + pb·v/1000` for `v`.

### Solution explanation
A linear cost model: fixed plus variable. Filtering by latency first removes options that violate a hard limit, however cheap. Sorting by `(cost, name)` makes ties deterministic. The break-even volume is where the two lines cross, `v = (fixed_b − fixed_a) · 1000 / (pa − pb)`. It is only useful when positive. Time O(n log n).

Common bugs: forgetting the `/ 1000`, comparing latency with `<` instead of `<=`, and returning a negative break-even volume.
