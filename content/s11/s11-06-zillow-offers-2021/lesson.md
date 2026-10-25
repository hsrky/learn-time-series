---
id: s11-06-zillow-offers-2021
title: Zillow Offers 2021: forecast risk at scale
minutes: 25
level: staff
goals: [State the public facts about the Zillow Offers shutdown, Explain adverse selection and why forecast error matters more when a company trades on its forecast, Describe how uncertainty and feedback loops should shape the design]
prereqs: [s11-05-uber-forecasting-orbit]
tags: [zillow, iBuying, uncertainty, adverse-selection, feedback-loop, case-study]
skills: [case-studies, probabilistic-forecasting, ml-system-design]
---

## Warm-up

```check
{"q": "A model gives an 80% prediction interval. About how often should the actual value fall inside it?", "type": "single",
 "options": ["80%", "50%", "100%"],
 "answer": 0,
 "why": ["Correct: this is calibration.", "That is a 50% interval.", "Then the interval would be infinitely wide."]}
```

```check
{"q": "What does the Kalman gain K do in the local level model?", "type": "single",
 "options": ["Acts like alpha: how much the new observation moves the level", "Sets the season length", "Counts outliers"],
 "answer": 0,
 "why": ["Correct.", "Seasons are not in a local level model.", "It does not count outliers."]}
```

## Why it matters

Most forecasting mistakes cost a bad dashboard. Some cost a company. In 2021 Zillow, a large US real-estate website, shut down its home-buying business **Zillow Offers**. The story is widely used in data science teaching. People did not only *read* the forecast. The company *traded* on it, with its own money, at large scale. This lesson uses **public facts only** and then shows general lessons about forecast risk. We do not know Zillow's internal models, so we do not claim to explain exactly what went wrong inside.

## Public facts

- **Zillow Offers** was an "iBuying" service: Zillow made cash offers for homes, then renovated and resold them. Home-value estimates (the "Zestimate" and related models) were part of pricing.
- In **November 2021**, with its third-quarter results, Zillow announced it would **wind down Zillow Offers**.
- The company reported an inventory write-down of about **$304 million** for that quarter and said more losses were likely. It also said it would reduce its workforce by about a quarter.
- Zillow's leaders said publicly that the **unpredictability of forecasting home prices** was a reason. In 2021 the housing market was moving fast, after the pandemic started.

Everything beyond these points is analysis by outside observers or general theory. Treat it as lessons about forecasting, not as a report on Zillow's internals.

## Lesson 1: a forecast that you trade on is a different problem

If a dashboard forecast is off by 5%, someone is annoyed. Suppose you buy 1 000 houses at prices based on a forecast with a 5% typical error. Your profit margin per house is 2% to 3%. Then **error is larger than margin**. Small average errors become big losses at scale. Margin must be compared with **forecast uncertainty**, not with the average accuracy.

```check
{"q": "A company buys homes with an expected resale margin of 3%. Its price model has a typical error of 6%. What is the main risk?", "type": "single",
 "options": ["No risk, the average error is zero", "Error is larger than the margin, so many trades lose money, even if the model is unbiased on average", "The model is too accurate", "Houses are cheap"],
 "answer": 1,
 "why": ["Zero average error does not remove the spread of outcomes.", "Correct: the spread of outcomes can wipe out a thin margin.", "6% is not very accurate relative to 3% margin.", "Price level is not the issue."]}
```

## Lesson 2: adverse selection (the winner's curse)

Sellers know things about their home that a model does not know: a leaking roof, a noisy street. A seller accepts an offer when it is **higher** than their own view of the home's value. So the homes you actually buy are biased towards homes where **your model overestimated**. This is **[[adverse selection]]**, close to the "winner's curse" in auctions.

So accuracy on all homes is not the same as accuracy on the homes you win. You must measure error on the **accepted** sample, and price in the selection effect.

```chart
{"title": "Illustration: a market that turns while you hold inventory", "x": "day", "height": 230,
 "series": [
   {"name": "price index", "gen": [["const", {"value": 100}], ["trend", {"start": 0, "slope": 0.15}], ["step", {"at": 70, "size": -12}], ["noise", {"sd": 0.8}]], "n": 120, "seed": 15}
 ],
 "marks": [{"x": 70, "label": "market turns"}],
 "caption": "Made-up data. A company that holds homes for months is exposed to a change in the trend. A model trained on the rising period does not know about the turn."}
```

```check
{"q": "Why are the homes a company actually buys likely to be overvalued by its model?", "type": "single",
 "options": ["Sellers are generous", "Sellers accept mainly when the offer is above their own private value, which is more likely when the model's estimate is too high", "Models always overvalue", "Because of taxes"],
 "answer": 1,
 "why": ["Sellers act in their interest.", "Correct: this is adverse selection.", "Models can err in both directions; the selection makes errors one-sided.", "Taxes are not the mechanism."]}
```

## Lesson 3: regime change and holding time

Models learn from the past. In a rising market, the past says "prices go up". A company that holds homes for 3 to 6 months expects gains. When the trend turns, the same model is wrong in one direction for all homes at the same time. This is **regime change**, or **concept drift**. These errors are **correlated**: they do not average out across 1 000 homes. Diversification does not help against a common shock.

Design answers: shorter holding time and limits on exposure per market. Add stress tests, such as "what if prices fall 5% in 3 months?". Add a human override with clear triggers.

## Lesson 4: feedback loops

When a company buys a large share of homes in a city, its own offers can influence the market. Its capacity limits, such as renovation crews and staff, affect resale speed. If sales slow, holding time grows, and risk grows. If the company raises offers to buy more, it may buy worse homes. Such **feedback loops** mean the data in the future is not the same as the data in the past.

## Lesson 5: what a better design looks like

- Use **probabilistic forecasts** (quantiles), not a single price. Offer based on a conservative quantile.
- Measure **calibration** on accepted deals.
- Monitor **bias** with the tracking signal, by city and price range, and have kill-switch rules.
- Run **stress tests** and set limits on total exposure.
- Keep **people in the loop** for extreme moves, and make sure alerts lead to action.
- Align incentives: growth targets can push people to ignore warning signs.

```check
{"q": "Which design change reduces risk from correlated forecast errors?", "type": "single",
 "options": ["Buy more homes in the same city", "Set exposure limits and run stress tests for a common price shock", "Remove the monitoring", "Use only point forecasts"],
 "answer": 1,
 "why": ["More exposure to the same shock increases risk.", "Correct.", "Monitoring helps to see the turn.", "Point forecasts hide uncertainty."]}
```

## Worked example

A toy simulation (not Zillow's data or model): a buyer offers 97% of its model's estimate. Sellers accept if the offer is at least their own private value. We compare the average margin on all homes with the margin on the homes actually bought.

```python
import numpy as np

rng = np.random.default_rng(3)
n = 200_000
true_value = 300_000 * np.exp(rng.normal(0, 0.25, n))          # true market value of each home
estimate = true_value * np.exp(rng.normal(0, 0.06, n))         # model estimate, about 6% error
seller_value = true_value * np.exp(rng.normal(0, 0.04, n))     # seller's private view
offer = 0.97 * estimate                                        # the buyer's offer

drift = rng.normal(-0.02, 0.04, n)                             # price change while holding
resale = true_value * (1 + drift)
costs = 0.04 * true_value                                      # renovation, holding, selling
margin = (resale - costs - offer) / offer

accepted = offer >= seller_value                               # sellers accept good offers only
print("share accepted        :", round(float(accepted.mean()), 3))
print("avg margin, all homes :", round(float(margin.mean()), 4))
print("avg margin, accepted  :", round(float(margin[accepted].mean()), 4))
print("avg estimate error, accepted:", round(float(np.mean(estimate[accepted] / true_value[accepted] - 1)), 4))
# Output:
# share accepted        : 0.338
# avg margin, all homes : -0.0293
# avg margin, accepted  : -0.0816
# avg estimate error, accepted: 0.0568
```

Check the last line. Among accepted homes the estimate is too high on average, even though the model is unbiased on all homes. The margin on accepted deals is lower than the margin on all homes. This is adverse selection in numbers.

## Common mistakes

- Judging a model by average error on all homes and not on the traded sample.
- Comparing error with the model's own history, but not with the business margin.
- Assuming errors across assets are independent.
- Treating a hot market as the normal state.
- Blaming only the model: process, incentives and monitoring also matter.

## Interview lens

**Typical question:** "What can we learn from the Zillow Offers shutdown for a forecasting system?"

**Strong answer:** The public facts: Zillow wound down Zillow Offers in 2021 after large inventory write-downs. It named the difficulty of forecasting home prices. General lessons: when you trade on a forecast, compare its uncertainty with your margin, not its average accuracy. Sellers choose, so you suffer adverse selection and must measure error on the accepted sample. Errors are correlated in a regime change. So you need exposure limits, stress tests, probabilistic forecasts, and bias monitoring with kill switches. And I would be careful not to claim knowledge of Zillow's internals.

**Red flags:** Stating invented details about Zillow's models. Blaming "a bad algorithm" without discussing uncertainty, selection and process.

## Real world

The facts above come from Zillow's own public announcement and quarterly results in November 2021, and from widespread press coverage. Many data science courses use it as a case on model risk. For the exact figures and statements, read Zillow's investor materials.

## Key points

- Zillow wound down Zillow Offers in November 2021 after large write-downs; leaders cited the difficulty of forecasting home prices.
- When you trade on a forecast, uncertainty must be smaller than margin or you need a wider safety margin.
- Adverse selection: the deals you win are biased towards your model's overestimates.
- Regime changes create correlated errors that diversification cannot remove.
- Use probabilistic forecasts, calibration on accepted deals, bias monitoring, exposure limits and human override.
