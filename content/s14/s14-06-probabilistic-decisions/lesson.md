---
id: s14-06-probabilistic-decisions
title: Probabilistic forecasts into decisions
minutes: 40
level: staff
goals: [Turn quantile forecasts into inventory, staffing and capacity decisions, Pick the service level from costs and explain it to the business, Explain why quantiles of parts do not add up to the quantile of the total, Choose staffing from quantiles with an SLA]
prereqs: [s14-01-framing-problems]
tags: [staff, newsvendor, staffing, quantiles, capacity, decisions]
skills: [staff, uncertainty]
---

## Warm-up

```check
{"q": "A 90th percentile forecast of 55 contacts means:", "type": "single",
 "options": ["Contacts will be exactly 55", "About 9 times in 10, contacts will be 55 or fewer", "The model is 90% accurate", "55 is the average"],
 "answer": 1,
 "why": ["It is not a point forecast.", "Correct: the quantile is a level that demand stays under 90% of the time.", "Accuracy is a different idea.", "The average is the mean, not the 90th percentile."]}
```

## Why it matters

A point forecast says "we will sell 100". A decision needs more: "How many do I order?" "How many agents do I schedule?" "How much server capacity do I reserve?" The answer depends on **how much it hurts to be wrong in each direction**. A probabilistic forecast gives you the whole range, so you can pick the point that fits your costs and your promise to customers (the SLA, or service level agreement).

## Inventory: the newsvendor rule

You order once, then demand arrives. If you order too little, you lose sales (cost `c_under` per unit). If you order too much, you waste stock (cost `c_over` per unit). The best order is the quantile

`q* = c_under / (c_under + c_over)`

of the demand distribution. This is the **critical ratio**. It is the service level that minimises expected cost.

- Milk: waste cost 1, lost-sale cost 3. `q* = 0.75`.
- Rare spare part: lost sale stops a machine (cost 50), holding cost is 1. `q* = 50/51 = 0.98`.

If a business gives you a service-level target (for example "98% of customers find the item"), use it directly as `q*`, and ask what cost it implies. Sometimes the implied cost is surprisingly high.

```chart
{"title": "Same forecast, different decisions (demand about 100, spread 20)", "x": "critical ratio, in %", "height": 230,
 "series": [
   {"name": "units to order at that quantile", "x": [50,60,70,75,80,90,95,98], "y": [100,105,110,113,117,126,133,141]}
 ],
 "caption": "The higher the cost of a lost sale compared to waste, the higher the quantile and the larger the order."}
```

```check
{"q": "Lost sale costs 9 and a wasted unit costs 1. What quantile should you order at?", "type": "numeric",
 "answer": 0.9, "tol": 0.001,
 "why": "9 / (9 + 1) = 0.9. Order at the 90th percentile."}
```

## Staffing: quantiles and an SLA

A contact centre promises "we answer 90% of calls in 20 seconds". Too few agents break the promise. Too many waste salaries. The process:

1. Forecast contacts per half hour as quantiles.
2. Choose the **service level** `p` (for example 0.95) from the SLA and the cost of extra agents.
3. Demand at level `p` ÷ contacts one agent handles per half hour = agents needed. **Round up.**
4. Add rules: minimum staff, maximum staff, shift patterns.

Note that real call-centre models also use queueing theory (the Erlang formulas) to link staff to waiting time. The quantile method is a good first step and a clear way to explain the idea. You practise it in [[problem:staffing-from-quantiles]].

```check
{"q": "Demand at the 95th percentile is 63 contacts. One agent handles 10 per half hour. How many agents?", "type": "numeric",
 "answer": 7, "tol": 0,
 "why": "63 / 10 = 6.3. Round up to 7 agents. Half agents do not exist, and rounding down breaks the SLA."}
```

## Capacity: reserve for the peak, but not for ever

For servers and warehouses, capacity is slow or costly to change. Plan capacity at a high quantile of the **peak** (for example, the 95th percentile of the daily peak), and add a plan to scale when a signal appears. Remember that capacity needs a **horizon** equal to the lead time to add it. Cloud servers: minutes. A new warehouse: years.

## Many items: quantiles do not add up

This is a point many people miss. Suppose you forecast 5 items and plan each at the 90th percentile. Then you add the five numbers to plan total capacity. The sum is **too high**, because it is unlikely that all items peak at the same time. The 90th percentile of the **total** is lower than the sum of the 90th percentiles.

The reverse also holds. The sum of medians is not the median of the total when distributions are skewed. So:

- Forecast the quantile at the **level where the decision is made**.
- If you need the total, simulate or use a joint (sample-based) forecast, or reconcile quantiles, instead of adding quantiles.

```check
{"q": "You add the 90th percentile forecasts of 10 independent items to plan a shared warehouse. What will probably happen?", "type": "single",
 "options": ["The plan is exactly the 90th percentile of the total", "The plan is too high (over-capacity), because items rarely peak together", "The plan is too low", "Nothing; quantiles always add"],
 "answer": 1,
 "why": ["Quantiles do not add up in general.", "Correct: the sum of quantiles is larger than the quantile of the sum for independent items.", "The sum is higher, not lower, in this case.", "Means add; quantiles do not."]}
```

## Worked example

Five independent items, each with demand around 20 units per day (Poisson). We compare the sum of the 90th percentiles with the 90th percentile of the total.

```python
import numpy as np

rng = np.random.default_rng(3)
n_sims = 200_000
demand = rng.poisson(20, size=(5, n_sims))      # 5 items, many simulated days

q = 0.9
per_item = np.quantile(demand, q, axis=1)       # 90th percentile of each item
total = demand.sum(axis=0)                      # total demand on each simulated day

print("per-item p90:", per_item.astype(int).tolist())
print("sum of item p90:", int(per_item.sum()))
print("p90 of the total:", int(np.quantile(total, q)))
print("mean total:", round(total.mean(), 1))
# Output:
# per-item p90: [26, 26, 26, 26, 26]
# sum of item p90: 130
# p90 of the total: 113
# mean total: 100.0
```

Planning the shared warehouse at 130 would hold about 17 units (15%) more than the 90th percentile of the total, which is 113. The mean total is about 100. This is the cost of adding quantiles. At the SKU level (where each order is placed), the item quantile is right. At the warehouse level, use the total.

## Common mistakes

- Using the mean for ordering when costs are asymmetric.
- Rounding staff to the nearest integer.
- Adding quantiles across items or time.
- A service level chosen without knowing the cost it implies.
- A quantile forecast that is not calibrated, so the promise is not kept. Check coverage in the backtest.
- Ignoring that sales are censored by stock-outs.

## Interview lens

**Typical question:** "How do you use a probabilistic forecast to decide how much to order?"

**Strong answer:** "I take the newsvendor rule. The best order is the quantile of demand equal to the cost of a lost sale divided by the sum of the lost-sale and waste costs. So I need quantile forecasts by item and lead time, and I check their calibration in a backtest: a 0.8 quantile should be above the actual 80% of the time. I measure the result with simulated cost. For total capacity I do not add item quantiles. I use joint samples or a higher level forecast. I also remember that sales are censored when stock runs out."

**Red flags:** ordering the mean; adding quantiles; no calibration check; no cost link.

## Real world

- The newsvendor model is a standard result of operations research, taught in supply-chain courses. Retail and perishable goods planning use it widely.
- The Amazon DeepAR paper and the M5 uncertainty competition (Walmart data) both focus on quantile forecasts because planning decisions need ranges, not single numbers.
- Contact-centre staffing is a classical field of queueing theory. The Erlang formulas connect call volume, agents and waiting time.

## Staff lens

Do not ask the business "what service level do you want?" first. Show them the trade-off curve: each extra point of service level costs this much stock or this many agents. Let them pick a point and write it into the SLA. Revisit the choice when costs change. This turns forecasting from a technical output into a negotiated decision.

## Key points

- Newsvendor: order at the quantile `c_under / (c_under + c_over)`.
- Staffing: demand at the service level ÷ capacity per agent, rounded up.
- Capacity: plan a high quantile of the peak, matched to the lead time to add capacity.
- Quantiles do not add across items; use joint samples or forecast at the decision level.
- Show the trade-off curve and let the business choose the service level.
