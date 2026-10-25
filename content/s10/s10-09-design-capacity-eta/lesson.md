---
id: s10-09-design-capacity-eta
title: Design case: capacity planning and ETA prediction
minutes: 40
level: staff
goals: [Plan capacity from a peak forecast with headroom, Explain how an ETA model is trained and checked, Choose quantile targets that match the business risk]
prereqs: [s10-08-design-anomaly-platform]
tags: [system-design, capacity-planning, ETA, quantiles, drill]
skills: [ml-system-design, probabilistic-forecasting]
---

## Warm-up

```check
{"q": "Which is the best first detector for a metric with a daily cycle?", "type": "single",
 "options": ["Static threshold", "Seasonal baseline with robust z-score", "Mean and standard deviation of all history"],
 "answer": 1,
 "why": ["A fixed threshold fires every day at the peak.", "Correct: it knows what is normal for each time slot.", "Outliers distort the mean and the standard deviation."]}
```

```check
{"q": "Shortage costs 4 and waste costs 1. The order should be the demand quantile at...", "type": "numeric",
 "answer": 0.8, "tol": 0.001,
 "why": "4 / (4 + 1) = 0.8."}
```

## Why it matters

Two very different questions look alike.

- **Capacity planning:** how many servers, drivers or warehouse slots will we need in 3 months?
- **ETA prediction:** when will this order arrive?

 Both are forecasts used for a decision, both have **asymmetric costs**, and both need more than a point value. A capacity plan at the average load fails on every busy day. An ETA that is too early makes customers angry; one that is too late loses orders.

## Capacity planning

Capacity planning forecasts *demand for resources* and turns it into a purchase or hiring plan.

Steps:

1. **Choose the unit and the peak.** Plan for the *peak*, not the daily mean. An example peak is the busiest 5 minutes of the day.
2. **Forecast the peak** with trend, weekly and yearly seasonality, and known events (a launch, a sale).
3. **Add headroom** for forecast error and for failures. Use the **upper quantile** of the forecast error (for example 95%), not the mean.
4. **Convert to resources.** `resources = peak ÷ (capacity per unit × target utilisation)`. A server run at 100% has no room for bursts, so use a target such as 60-70%.
5. **Account for lead time.** Hardware or hiring may take months. You must forecast *that* far ahead, where the uncertainty is larger.
6. **Review often.** Compare plan and actual each month.

## A capacity example

Example: peak is forecast at 12 000 requests per second (rps). One server handles 500 rps. Target utilisation 70%. Servers = 12 000 / (500 × 0.7) = **34.3**, so buy **35**. If the upper 95% quantile of the peak is 14 000, servers = 40.

```chart
{"title": "Daily peak load with trend, a weekly cycle, and a plan line", "x": "day", "height": 240,
 "series": [
   {"name": "daily peak (history + forecast)", "gen": [["trend", {"start": 100, "slope": 0.6}], ["season", {"period": 7, "amp": 12}], ["noise", {"sd": 4}]], "n": 120, "seed": 6},
   {"name": "capacity plan (p95 + headroom)", "gen": [["trend", {"start": 135, "slope": 0.6}]], "n": 120, "dash": true}
 ],
 "marks": [{"x": 90, "label": "forecast starts"}],
 "caption": "The plan line stays above the peaks. The gap is the headroom paid for forecast error."}
```

```check
{"q": "Forecast peak = 9 000 rps, one server = 300 rps, target utilisation 60%. How many servers (round up)?", "type": "numeric",
 "answer": 50, "tol": 0.01,
 "why": "9 000 / (300 × 0.6) = 9 000 / 180 = 50 servers."}
```

## ETA prediction

An **[[ETA]]** (estimated time of arrival) model predicts how long a trip or delivery will take. It is usually a **regression** problem on one event, not a classic time series, but time matters a lot.

**Features:** distance and route estimate, restaurant preparation time (recent and typical), traffic level now and weather. Add hour and weekday, courier supply near the restaurant and order size. Add recent actual times in the same area, a *rolling* feature built point-in-time.

## ETA targets, losses and checks

**Targets and losses.** Delivery time is skewed: most orders take 25 to 35 minutes, a few take 70. The mean is pulled up. Options: predict the **median** (MAE loss), or predict **quantiles** and show a range ("30-40 min"). Asymmetric costs decide: a promise that is too short breaks trust, a promise that is too long loses orders. Many systems promise a higher quantile (for example 80%) and track on-time rate.

**Checks:**

- **MAE** and **P90 absolute error** by segment (city, hour).
- **Bias** (is it systematically early or late?).
- **Calibration / coverage:** if the 80% quantile is correct, about 80% of deliveries finish before it.
- **Feedback loop:** a shorter promise changes who orders and how couriers behave.

```check
{"q": "You predict the 80th percentile of delivery time. Over 1 000 orders, 910 arrive before the prediction. What does that tell you?", "type": "single",
 "options": ["The model is well calibrated", "The prediction is too high (too cautious): coverage should be near 80%", "The model is too low", "Nothing"],
 "answer": 1,
 "why": ["Calibrated would be about 800.", "Correct: 91% is much higher than 80%, so the quantile is too large.", "A too-low quantile would give coverage below 80%.", "Coverage is exactly the check for quantile models."]}
```

## Worked example

Take a capacity plan for 90 days. Fit a trend and a weekly pattern on 180 days of daily peaks. Forecast, then add headroom from the 95th percentile of the fitting errors.

```python
import numpy as np

rng = np.random.default_rng(2)
n_hist, h = 180, 90
t = np.arange(n_hist + h)
weekly = 8 * np.sin(2 * np.pi * t / 7)
peak = 1000 + 3.0 * t + weekly + rng.normal(0, 15, n_hist + h)     # rps, truth
hist = peak[:n_hist]

# 1) trend by least squares, 2) weekly profile = mean residual per weekday
coef = np.polyfit(t[:n_hist], hist, 1)
resid = hist - np.polyval(coef, t[:n_hist])
profile = np.array([resid[(t[:n_hist] % 7) == k].mean() for k in range(7)])
fit_err = resid - profile[t[:n_hist] % 7]

# forecast and headroom
fc = np.polyval(coef, t[n_hist:]) + profile[t[n_hist:] % 7]
head = np.quantile(fit_err, 0.95)
plan = fc + head
actual_future = peak[n_hist:]

print("headroom (95th pct of fit error):", round(float(head), 1))
print("share of future days within plan:", round(float((actual_future <= plan).mean()), 2))
servers = int(np.ceil(plan.max() / (500 * 0.7)))
print("servers for the max plan value:", servers)
# Output:
# headroom (95th pct of fit error): 22.5
# share of future days within plan: 0.9
# servers for the max plan value: 6
```

About 90% of the future days stay under the plan. The target was 95%, but the trend also has to be estimated, and 90 days is a small sample. Real traffic has bigger shocks than Gaussian noise, so the plan should also include events and a safety factor.

## Common mistakes

- Planning for the average instead of the peak.
- Forgetting lead time: you decide today for a date months away.
- Headroom as a fixed percent for everything, without looking at the forecast error.
- Training an ETA model on random splits, or with features not known at order time.
- Reporting only mean error for ETAs. The tail (late deliveries) hurts users the most.
- Not checking calibration of quantile forecasts.

## Interview lens

**Typical question:** "How would you forecast the compute capacity we need next quarter?" or "How would you predict delivery time?"

**Strong answer:** For capacity I forecast the peak, not the mean, with trend, weekly and yearly seasonality and known launches. I add headroom from an upper quantile of the forecast error and convert to servers with a target utilisation. I include the purchase lead time, and I re-plan every month by comparing plan and actual. For ETA I build a regression on point-in-time features. Examples are distance, restaurant prep time, traffic, supply and recent local delivery times. I predict quantiles. I check MAE, P90 error, bias and coverage by segment. I choose the promised quantile from the cost of being late versus too cautious.

**Red flags:** Planning at the mean. A single point ETA with no uncertainty. No calibration check. No view on lead time.

## Real world

Companies such as Uber and DoorDash have published engineering posts on ETA models. The posts cover gradient boosting and deep models for delivery and trip times. Public cloud providers describe capacity planning in terms of peak load, headroom and utilisation targets. The details of each company's system differ, but the quantile and headroom ideas are standard.

## Key points

- Plan capacity for the forecast peak plus headroom from an upper error quantile.
- Resources = peak ÷ (capacity per unit × target utilisation).
- Lead time sets how far ahead you must forecast.
- ETA is regression with point-in-time features; predict quantiles when costs are asymmetric.
- Check coverage (calibration), tail error and bias by segment.
