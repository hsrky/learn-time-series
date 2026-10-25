---
id: s10-06-forecasts-into-decisions
title: From forecasts to business decisions: FVA and the newsvendor
minutes: 25
level: advanced
goals: [Measure forecast value added against a naive baseline, Explain why costs of under- and over-forecasting differ, Compute the newsvendor optimal order from a quantile]
prereqs: [s10-05-forecasting-at-scale]
tags: [newsvendor, FVA, quantile, asymmetric-cost, decisions]
skills: [ml-system-design, probabilistic-forecasting]
---

## Warm-up

```check
{"q": "A pinball (quantile) loss at tau = 0.9 punishes...", "type": "single",
 "options": ["Under-forecasts more than over-forecasts", "Over-forecasts more than under-forecasts", "Both equally"],
 "answer": 0,
 "why": ["Correct: with tau = 0.9, being below the actual costs 0.9 per unit, being above costs 0.1.", "That is the case for tau below 0.5.", "Equal weights belong to tau = 0.5, the median."]}
```

```check
{"q": "Why do we want a fallback forecast in a nightly job?", "type": "single",
 "options": ["To save memory", "So a failed run does not leave planners without any forecast", "To make the model more accurate", "To avoid using features"],
 "answer": 1,
 "why": ["Memory is not the point.", "Correct.", "A fallback is usually simpler and less accurate.", "Features are unrelated."]}
```

## Why it matters

A forecast is not the goal. A **decision** is the goal: how many loaves to bake, how many drivers to schedule, how many servers to buy. The best number for the decision is often **not** the mean forecast. A bakery that throws away unsold bread loses a little. A bakery that has no bread for a customer loses the sale and maybe the customer. Two kinds of error have two different prices.

## Forecast value added (FVA)

**[[Forecast value added]]** (FVA) asks: does each step of the process make the forecast better than the step before? Compare with a naive reference.

**FVA = (error of naive − error of your forecast) / error of naive**

Example: naive WAPE = 20%. Statistical model = 16%. After analysts adjust it, 17%.

| Step | WAPE | FVA vs naive |
|---|---|---|
| Naive (last week) | 20% | 0 |
| Statistical model | 16% | (20 − 16) / 20 = **+20%** |
| Analyst override | 17% | (20 − 17) / 20 = +15% |

The analyst step *lost* 5 points of FVA (from +20% to +15%). That does not mean analysts are useless: they may help with promotions and hurt on normal weeks. The method tells you **where** to look. A step with negative FVA should be changed or removed, and it costs time too.

```check
{"q": "Naive WAPE is 25%. Your model has WAPE 20%. What is the FVA?", "type": "numeric",
 "answer": 0.2, "tol": 0.001,
 "why": "(25 − 20) / 25 = 0.20, that is 20% better than naive."}
```

## Asymmetric costs and the newsvendor

The **[[newsvendor problem]]** is the classic model of one-time ordering under uncertain demand. You choose a quantity `q` before you know the demand `D`.

- **Underage cost** `cu`: the loss for each unit you are *short* (lost profit): `cu = price − cost`.
- **Overage cost** `co`: the loss for each unit *left over*: `co = cost − salvage value`.

## A bakery example

Example: a bakery sells a cake for 5 and makes it for 2. An unsold cake is worth 0 at the end of the day.
`cu = 5 − 2 = 3`, `co = 2 − 0 = 2`.

The expected cost is lowest when you order the quantile of demand at the **critical ratio**:

**q\* = the quantile of D at level  cu / (cu + co)**

Here: 3 / (3 + 2) = **0.6**. Order the 60th percentile of demand, not the mean (the 50th percentile for a symmetric distribution). When shortage costs more than waste, order more than the median. When waste costs more, order less.

```check
{"q": "A product sells for 10 and costs 7. Unsold units have no value. What is the critical ratio cu / (cu + co)?", "type": "numeric",
 "answer": 0.3, "tol": 0.001,
 "why": "cu = 10 − 7 = 3. co = 7 − 0 = 7. Ratio = 3 / 10 = 0.3. Waste is expensive, so order a LOW quantile (30th percentile)."}
```

## Why the quantile is the answer

Why does it work? At the optimum, one extra unit has a 1 − F(q) chance to be sold, which saves cu. It has an F(q) chance to be left, which costs co. Setting `cu·(1 − F) = co·F` gives `F = cu / (cu + co)`.

```widget
{"name": "quantile-loss", "params": {"tau": 0.6}}
```

The widget shows the same idea. The **pinball loss** at level tau is the newsvendor cost with `tau = cu / (cu + co)`. Training a model with quantile loss gives you the order quantity directly.

## From the forecast to the order

A real replenishment decision uses more than one number:

- **Probabilistic forecast**: you need quantiles or samples of demand, not only the mean. (See the stage on probabilistic forecasting.)
- **Horizon** = lead time + review period. Forecast the demand for the *whole* time you cannot change the order.
- **Service level**: a business target such as "95% of days without stock-out". It is the critical ratio chosen by policy.
- **Constraints**: minimum order size, shelf space, budget, shelf life.

Suppose you only have a point forecast and a normal error with standard deviation `s`. Then `q = mean + z × s`. Here `z` is the normal quantile: z = 0.25 for 0.6 and z = 1.64 for 0.95.

```check
{"q": "Shortage costs 9 per unit and waste costs 1 per unit. Which order is right?", "type": "single",
 "options": ["The mean forecast", "The median forecast", "A high quantile (90th percentile)", "A low quantile (10th percentile)"],
 "answer": 2,
 "why": ["The mean treats both errors as equal.", "The median also treats both errors as equal.", "Correct: ratio = 9 / (9 + 1) = 0.9. Better to have extra stock than to miss sales.", "That is the right answer for the opposite costs."]}
```

## Worked example

We simulate a bakery with demand `Normal(100, 20)`. We compare three order rules over 100 000 days: the mean, the median of samples, and the newsvendor quantile.

```python
import numpy as np

rng = np.random.default_rng(42)
demand = np.maximum(rng.normal(100, 20, 100_000), 0).round()   # cakes per day
cu, co = 3.0, 2.0                                              # underage, overage cost
ratio = cu / (cu + co)

def avg_cost(q):
    short = np.maximum(demand - q, 0)       # missed sales
    left = np.maximum(q - demand, 0)        # unsold cakes
    return float(np.mean(cu * short + co * left))

q_mean = demand.mean()
q_star = np.quantile(demand, ratio)         # newsvendor order
print("critical ratio:", ratio)
print("order = mean   :", round(q_mean, 1), "-> cost per day", round(avg_cost(q_mean), 2))
print("order = quantile:", q_star, "-> cost per day", round(avg_cost(q_star), 2))
# Output:
# critical ratio: 0.6
# order = mean   : 99.9 -> cost per day 39.97
# order = quantile: 105.0 -> cost per day 38.75
```

Ordering the 60th percentile gives a lower daily cost than ordering the mean. The saving per day looks small, but it repeats for every product and every day.

## Common mistakes

- Ordering the mean forecast when costs are not symmetric.
- Using the wrong costs: `cu` is lost *margin*, not lost revenue; `co` is cost minus salvage.
- Forecasting one day when the lead time is five days.
- Using a normal distribution for intermittent demand with many zeros.
- Judging the model only on MAE when the business pays for asymmetric errors. Evaluate with the pinball loss or the business cost.

## Interview lens

**Typical question:** "The business says stock-outs are worse than waste. How does that change your model?"

**Strong answer:** I convert the cost statement into numbers: underage cost (lost margin) and overage cost (cost minus salvage). The best order quantity is the demand quantile at cu / (cu + co). So I need a probabilistic forecast, or a direct quantile model trained with pinball loss. I evaluate with the business cost and with pinball loss at that level, not only MAE. I also check forecast value added against a naive baseline so every process step earns its place.

**Red flags:** Saying "increase the forecast by 10%" with no calculation. Using MAPE as the only metric. Not knowing the newsvendor formula.

## Real world

The newsvendor model is a textbook result in operations research, studied since at least the 1950s. Retail and supply-chain teams use it for perishable goods. The M5 competition added a second track, the "uncertainty" track. It scored quantile forecasts with a pinball-type loss. Planners need quantiles and not only means. The FVA idea was popularised by forecasting practitioners such as Michael Gilliland.

## Key points

- FVA = (naive error − model error) / naive error. Check each process step against it.
- Underage cost cu = lost margin per unit; overage cost co = cost − salvage per unit.
- Newsvendor: order the demand quantile at cu / (cu + co).
- Pinball loss at tau is the same trade-off. Train or tune quantile models with it.
- Forecast the whole lead time plus review period, and respect real-world constraints.
