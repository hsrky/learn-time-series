---
id: s14-01-framing-problems
title: Framing ambiguous business problems as forecasting problems
minutes: 30
level: staff
goals: [Start from the decision and not from the model, Fill in a decision canvas with who acts, cost of error, horizon and granularity, Decide when a forecast is the wrong tool, Turn a vague request into a metric and a pilot plan]
prereqs: []
tags: [staff, framing, decision, requirements]
skills: [staff, communication]
---

## Warm-up

```check
{"q": "Why do we compare a new model with a seasonal naive baseline?", "type": "single", "options": ["It is always the best", "To check the new model adds value over a simple rule", "To save time", "To remove seasonality"], "answer": 1, "why": ["It is not always best.", "Correct.", "Not the reason.", "Not the reason."]}
```
```check
{"q": "What does WAPE divide by?", "type": "single", "options": ["The number of rows", "The sum of the actual values", "The mean forecast", "The last value"], "answer": 1, "why": ["No.", "Correct: sum of absolute errors over sum of actuals.", "No.", "No."]}
```

## Why it matters

A VP says: "We need better forecasting." That sentence is not a problem. It does not say who uses the forecast, what they do with it, or what a mistake costs. A mid-level engineer starts with a model. A staff engineer starts with the **decision**. Many forecasting projects fail not because the model is weak but because the forecast does not change any decision. This lesson gives you a short canvas to frame any request.

## The decision canvas

Fill in these eight lines before you write any code. If you cannot fill a line, that is your first task.

| Line | Question | Example (grocery) |
|---|---|---|
| 1. Decision | What will someone do differently? | How many crates of milk to order |
| 2. Actor | Who acts, and with what tool? | Store manager, ordering app |
| 3. Cost of error | What does too high cost? Too low? | Waste 1 per unit; empty shelf 3 per unit |
| 4. Horizon | How far ahead must we see? | Order lead time 2 days + review period 1 day = 3 days |
| 5. Granularity | Which level: item, store, day, hour? | Item x store x day |
| 6. Refresh | How often does the decision repeat? | Every night |
| 7. Baseline today | What do they do without the model? | Last week's sales + manager's feeling |
| 8. Success | How will we know it worked? | Less waste and fewer stock-outs in an A/B test |

**Horizon** is not a free choice. It equals the **lead time** (time from the decision to the effect) plus the **review period** (time between decisions). Forecasting beyond that is wasted effort. Forecasting less is useless.

```check
{"q": "Orders are placed every day and arrive 2 days later. What is the minimum horizon to forecast?", "type": "numeric",
 "answer": 3, "tol": 0,
 "why": "Lead time 2 days + review period 1 day = 3 days. The order must cover the demand until the next order can arrive."}
```

## Cost of error decides the target

The mean is the best single number only when over- and under-forecast cost the same. Usually they do not. When under-stock costs 3 and over-stock costs 1, the best order is **not** the mean. It is the **75th percentile** of demand: 3 / (3 + 1) = 0.75. This idea is called the newsvendor rule. See the chart: the cost is lowest at an order near 114, above the mean of 100.

```chart
{"title": "Expected cost per day vs order quantity (demand about 100; under-stock costs 3, over-stock costs 1)", "x": "order quantity", "height": 240,
 "series": [
   {"name": "expected cost", "x": [70,75,80,85,90,95,100,105,110,115,120,125,130], "y": [92.4,79.1,66.7,55.5,45.9,38.0,32.0,27.9,25.8,25.5,26.7,29.1,32.4]}
 ],
 "marks": [{"x": 100, "label": "mean demand"}],
 "caption": "Ordering the mean (100) costs about 32 per day. Ordering near the 75th percentile (about 114) costs about 25."}
```

So the target of your project is not "predict sales". It is "support an order quantity at a service level". That changes the model (quantiles), the metric (pinball loss and cost), and the test (simulated cost).

```check
{"q": "Under-stock costs 4 and over-stock costs 1 per unit. Which quantile of demand should you plan for?", "type": "numeric",
 "answer": 0.8, "tol": 0.001,
 "why": "Critical ratio = under-cost / (under-cost + over-cost) = 4 / (4 + 1) = 0.8, the 80th percentile."}
```

## Is a forecast the right tool?

Sometimes it is not. Ask:

- **Can the decision change?** If the order is fixed by a contract, a better forecast has no value.
- **Is the future influenced by the decision?** If your price changes demand, you need a causal or optimisation model. A forecast alone is not enough.
- **Is a rule enough?** "Always keep 3 days of stock" can beat a complex forecast if demand is stable.
- **Is the data there?** Without history or signals, a forecast is a guess in a nice chart.

A staff engineer says "no" or "not yet" to some projects. This saves the team months.

```check
{"q": "A team asks for a demand forecast, but the supplier delivers a fixed amount every week and the order can never change. What is the best response?", "type": "single",
 "options": ["Build the best model possible", "Ask which decision the forecast would change; if none, do not build it", "Use a foundation model", "Ask for more data"],
 "answer": 1,
 "why": ["Value comes from changing decisions.", "Correct: no changeable decision means no value from a forecast.", "A model type does not fix a missing decision.", "More data does not create a decision."]}
```

## From vague request to plan

A good staff-level answer to "we need better forecasting" has this shape:

1. **Restate** the decision in one sentence and confirm it with the actor.
2. **Quantify** the prize: current cost of error × realistic improvement. (Lesson on FVA and ROI covers the math.)
3. **Define** one primary metric (linked to cost) and two guard-rail metrics.
4. **Pilot**: smallest slice (one region, one category) with a clear baseline and a stop rule.
5. **Decide the owner** and the review date.

Write this in one page. Then ask the stakeholder to sign it. Agreement on the page is worth more than any early model.

## Worked example

We simulate the choice from the chart. Demand is random with mean 100 and spread 20. We compare two ordering rules: the mean, and the 75th percentile.

```python
import numpy as np

rng = np.random.default_rng(0)
demand = rng.normal(100, 20, 200_000).clip(0)
c_under, c_over = 3.0, 1.0

def avg_cost(order):
    short = np.clip(demand - order, 0, None)     # units we could not sell
    extra = np.clip(order - demand, 0, None)     # units left over
    return (c_under * short + c_over * extra).mean()

q = c_under / (c_under + c_over)                   # critical ratio = 0.75
order_mean = demand.mean()
order_q = np.quantile(demand, q)

print(f"critical ratio: {q:.2f}")
print(f"order the mean ({order_mean:.0f}): cost {avg_cost(order_mean):.1f}")
print(f"order the 75th percentile ({order_q:.0f}): cost {avg_cost(order_q):.1f}")
print(f"saving: {1 - avg_cost(order_q) / avg_cost(order_mean):.0%}")
# Output:
# critical ratio: 0.75
# order the mean (100): cost 32.0
# order the 75th percentile (114): cost 25.4
# saving: 20%
```

The cost falls by about a fifth with no change in forecast accuracy. We only changed what we forecast and how we use it. This is the staff lens: the largest gain is often in the framing.

## Common mistakes

- Starting with the model or the tool.
- Using the mean when costs are asymmetric.
- Forecasting at the wrong level (daily data for a weekly decision).
- A horizon that does not match the lead time.
- No baseline of "what they do today".
- Measuring success with a forecast metric only, and not with the business result.
- Not asking who will act on the forecast.

## Interview lens

**Typical question:** "The CEO wants to forecast revenue. How do you start?"

**Strong answer:** "I ask what decision it informs: hiring, budget, or investor guidance. Each needs a different horizon and accuracy. I ask who owns the decision and what a 5% error costs in each direction. I look at how it is done today and what the error of that process is. Then I propose one pilot with a baseline, a primary metric, and a stop rule. I would also ask if the CEO wants a point number or a range. A range changes how we plan."

**Red flags:** naming a model first; no mention of the actor or cost; no baseline; no pilot.

## Real world

- The newsvendor problem is a classic from operations research. It is taught in many supply-chain courses and used in retail ordering, airline capacity and spare-parts planning.
- Public forecasting guides tell readers to understand how the forecast will be used before choosing methods. One example is the free book "Forecasting: Principles and Practice" by Hyndman and Athanasopoulos.

## Staff lens

Your scarce resource is not code. It is the team's attention. Say no to the projects with no changeable decision, and write down why. Keep a short list of "decisions we support", each with an owner, a cost of error, and a metric. This list becomes the roadmap.

## Key points

- Start with the decision: actor, action, cost of error, horizon, granularity, refresh.
- Horizon = lead time + review period.
- With unequal costs, forecast a quantile (critical ratio), not the mean.
- Check that the decision can change; say no when it cannot.
- End with a one-page plan: prize, metric, pilot, owner.
