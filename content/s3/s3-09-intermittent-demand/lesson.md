---
id: s3-09-intermittent-demand
title: Intermittent demand: Croston, SBA and TSB
minutes: 35
level: intermediate
goals: [Explain why plain smoothing and common metrics fail on series with many zeros, Compute the Croston forecast by hand, Explain the SBA bias correction and the TSB idea, Classify demand with ADI and CV squared, Implement Croston in numpy]
prereqs: [s3-02-simple-exponential-smoothing]
tags: [intermittent, croston, sba, tsb, spare-parts]
skills: [from-scratch, metrics]
---

## Warm-up

```check
{"q": "SES with alpha = 0.2, old level 10, new value 0. What is the new level?", "type": "numeric",
 "answer": 8, "tol": 0.001,
 "why": "10 + 0.2 * (0 - 10) = 8."}
```

```check
{"q": "A series is 0, 0, 5, 0, 0, 0, 3, 0. What is the mean demand per period?", "type": "numeric",
 "answer": 1, "tol": 0.001,
 "why": "Total demand is 5 + 3 = 8 over 8 periods. 8 / 8 = 1."}
```

## Why it matters

A warehouse sells a spare part. Most days nobody buys it. Some days, 3 or 8 pieces are sold. The series is full of **zeros**. This is **[[intermittent demand]]**. It is common for spare parts, slow-moving retail items and rare events. Simple smoothing works badly here. The forecast jumps up after each sale and decays to zero in between, and it is rarely right. [[Croston's method]] (1972) was made for this problem and is still a standard tool.

## What goes wrong with normal methods

- **SES** reacts to every sale and every zero. The forecast zig-zags. It is too high just after a sale and too low just before the next one.
- **MAE** is smallest for a forecast of **zero**. Zero is the median of a series with more than half zeros. A model can look "good" while it predicts nothing.
- **MAPE** divides by the actual value. With zeros, it is undefined.

Better: forecast the **average demand per period**. Judge it with scaled errors, or with a service-level view of inventory (quantiles). More about metrics comes in the evaluation stage.

## Croston: split the problem in two

Look at two things only when a sale happens:

1. **Size z:** how much is sold when there is a sale.
2. **Interval p:** how many periods pass between two sales.

Smooth each with SES, but **update only in periods with demand**:

- If y(t) > 0, with q = periods since the previous demand:
  z = α·y(t) + (1 − α)·z
  p = α·q + (1 − α)·p
- If y(t) = 0: change nothing.
- **Forecast** (for all future periods): z / p, the average demand per period.

## Croston: start values and an example

Start values: z is the size of the first demand. p is the number of periods until the first demand.

Numbers: series 0, 0, 5, 0, 0, 0, 3, 0, 4 with α = 0.5.
- First demand at t = 3: z = 5, p = 3.
- Next demand at t = 7 (size 3, q = 4):
  - z = 0.5·3 + 0.5·5 = 4.
  - p = 0.5·4 + 0.5·3 = 3.5.
- Next demand at t = 9 (size 4, q = 2):
  - z = 0.5·4 + 0.5·4 = 4.
  - p = 0.5·2 + 0.5·3.5 = 2.75.
- Forecast = 4 / 2.75 = 1.45 per period.

```chart
{"title": "Demand (bars), SES forecast zig-zags, Croston forecast is steady", "x": "period", "height": 240,
 "series": [
  {"name": "demand", "kind": "bar", "y": [0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 4, 0, 6, 0, 0, 0, 3, 3, 0, 0, 0, 6, 5, 0, 0, 0, 2, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
  {"name": "SES (alpha 0.2)", "y": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.6, 2.08, 1.66, 2.53, 2.02, 1.62, 1.3, 1.64, 1.91, 1.53, 1.22, 0.98, 1.98, 2.59, 2.07, 1.65, 1.32, 1.46, 1.17, 2.13, 1.71, 1.37, 1.09, 0.87, 0.7, 0.56, 0.45, 0.36, 0.29, 0.23, 0.18]},
  {"name": "Croston (alpha 0.2)", "dash": true, "y": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.88, 0.88, 1.0, 1.0, 1.0, 1.0, 0.97, 1.05, 1.05, 1.05, 1.05, 1.12, 1.3, 1.3, 1.3, 1.3, 1.15, 1.15, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35]}
 ],
 "caption": "Croston changes only when a sale happens, so it stays flat in the zeros. SES decays toward 0 in the long gap at the end."}
```

```check
{"q": "In Croston's method, what happens to z and p in a period with zero demand?", "type": "single",
 "options": ["Nothing changes", "z becomes 0", "p is reduced by alpha", "Both are set to the mean"],
 "answer": 0,
 "why": ["Correct: both are updated only when a demand occurs.", "z is the size of the last demands. A zero is not a size.", "p changes only when a new demand ends an interval.", "Nothing is reset."]}
```

## Bias and the fixes: SBA and TSB

**Croston is biased.** The ratio z/p is, on average, a little too high. The fix of **[[SBA]]** (Syntetos-Boylan Approximation) is simple:

SBA forecast = (1 − α/2) · z / p

With α = 0.1 the factor is 0.95. In the example above with α = 0.5: 0.75 · 1.45 = 1.09.

## TSB: when an item stops selling

Another problem: when an item **stops selling** (it becomes obsolete), Croston never changes, because it only updates at a demand. The forecast stays high for ever. **[[TSB]]** (Teunter-Syntetos-Babai, 2011) fixes this. It smooths the **probability of demand** in **every** period:

- Probability, in every period: π = β·d + (1 − β)·π. Here d = 1 if there was a sale, else d = 0.
- Size: z = α·y + (1 − α)·z (only when y > 0)
- **Forecast = π · z**

During a long run of zeros, π decays, and so does the forecast. TSB handles obsolescence.

```check
{"q": "An item has had no sales for 6 months, but Croston's forecast is unchanged from before. Which method fixes this?", "type": "single",
 "options": ["TSB, which updates the probability of demand in every period", "SBA, which multiplies by 1 - alpha/2", "Plain mean forecast", "Seasonal naive"],
 "answer": 0,
 "why": ["Correct: the probability falls with every zero, so the forecast falls.", "SBA corrects the bias but still updates only at demands.", "The mean is slow and would not fix the structure either.", "Seasonal naive repeats old values and has no sense of obsolescence."]}
```

## Which demand is intermittent? ADI and CV²

- **[[ADI]]** (average demand interval) = number of periods / number of periods with demand.
- **CV²** (squared coefficient of variation) of the **non-zero** demand sizes = (std / mean)².

A common classification (Syntetos, Boylan and Croston, 2005) uses the cut-offs ADI = 1.32 and CV² = 0.49:

| | CV² ≤ 0.49 | CV² > 0.49 |
|---|---|---|
| **ADI ≤ 1.32** | Smooth | Erratic |
| **ADI > 1.32** | Intermittent | Lumpy |

Croston-type methods are meant for the intermittent and lumpy cases.

## Worked example

We implement Croston, SBA and TSB. We apply them to a simulated series and to an item that stops selling.

```python
import numpy as np

def croston(y, alpha, variant="croston"):
    y = np.asarray(y, dtype=float)
    demand = np.nonzero(y > 0)[0]
    if len(demand) == 0:
        return 0.0
    first = demand[0]
    z, p, last = y[first], first + 1.0, first          # start values from the first demand
    for t in range(first + 1, len(y)):
        if y[t] > 0:                                   # update only when there is a demand
            q = t - last                               # periods since the last demand
            z = alpha * y[t] + (1 - alpha) * z
            p = alpha * q + (1 - alpha) * p
            last = t
    f = z / p
    return f * (1 - alpha / 2) if variant == "sba" else f

def tsb(y, alpha, beta):
    y = np.asarray(y, dtype=float)
    demand = np.nonzero(y > 0)[0]
    if len(demand) == 0:
        return 0.0
    first = demand[0]
    z, prob = y[first], 1.0 / (first + 1)
    for t in range(first + 1, len(y)):
        if y[t] > 0:
            z = alpha * y[t] + (1 - alpha) * z
            prob = beta + (1 - beta) * prob
        else:
            prob = (1 - beta) * prob                   # the probability decays in every zero
    return prob * z

print("lesson example:", round(croston([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5), 3))

rng = np.random.default_rng(6)
sale = rng.random(120) < 0.25                          # a sale happens in 25% of the periods
y = np.where(sale, 1 + rng.poisson(3, 120), 0)         # sizes 1 + Poisson(3), true mean 0.25 * 4 = 1
print("true average demand:", round(y.mean(), 2))
print("Croston:", round(croston(y, 0.1), 2), " SBA:", round(croston(y, 0.1, "sba"), 2),
      " TSB:", round(tsb(y, 0.1, 0.1), 2))

# An item that stops selling: 60 periods of the same pattern, then 40 zeros
stopped = np.concatenate([y[:60], np.zeros(40)])
print("after 40 zeros -> Croston:", round(croston(stopped, 0.1), 2), " TSB:", round(tsb(stopped, 0.1, 0.1), 2))
# Output:
# lesson example: 1.455
# true average demand: 1.06
# Croston: 1.06  SBA: 1.0  TSB: 1.25
# after 40 zeros -> Croston: 1.14  TSB: 0.02
```

## Common mistakes

- Using MAE or MAPE on intermittent data and trusting the result.
- Using SES on a series with many zeros.
- Forgetting that Croston never reacts to a long run of zeros (obsolescence). Check with TSB.
- Treating Croston's z/p as a forecast of the next sale. It is the **average per period**.
- Ignoring the lead time. For stock decisions you need a quantile of demand over the lead time, not only a mean.

## Interview lens

**Typical question:** "How would you forecast demand for a spare part that sells once every few weeks?"

**Strong answer:** The series is intermittent, so ordinary smoothing and MAPE do not work. I would use Croston, or better the SBA variant. It splits demand into size and interval, and it updates them only when a sale occurs. The forecast is size divided by interval, that is the average demand per period. If items can become obsolete, I would use TSB, which updates the probability of demand in every period. I would evaluate with a scaled error such as MASE or RMSSE. For inventory decisions I would forecast a quantile of lead-time demand to reach a target service level.

**Red flags:** Using MAPE with zeros. Saying Croston gives the next sale date. Not knowing the bias of Croston. Judging by MAE alone and picking a zero forecast.

## Real world

- J. D. Croston published the method in 1972, for demand of spare parts and slow-moving items. It is still widely used and appears in libraries such as statsforecast and in the R package tsintermittent.
- Syntetos and Boylan (2005) showed the bias and proposed the SBA fix. TSB was published by Teunter, Syntetos and Babai in 2011.
- The Walmart data of the M5 competition has many items with zero-sales days. Its scaled error metric was designed with such data in mind.

## Key points

- Intermittent demand has many zeros. SES zig-zags and MAE/MAPE mislead.
- Croston: smooth the demand size z and the interval p, only when demand occurs. Forecast = z/p.
- SBA: multiply by (1 − α/2) to remove the bias. TSB: smooth the probability of demand every period, so the forecast decays for obsolete items.
- ADI > 1.32 means intermittent. CV² > 0.49 means lumpy sizes.
