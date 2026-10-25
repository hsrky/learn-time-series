---
id: s3-10-hierarchical-reconciliation
title: Hierarchical forecasting and reconciliation
minutes: 35
level: intermediate
goals: [Describe a hierarchy and build its summing matrix S, Explain why separate forecasts are not coherent, Compute bottom-up and top-down forecasts, Explain the idea of optimal reconciliation (OLS and MinT), Implement S and bottom-up in numpy]
prereqs: [s3-01-baselines, s3-05-autoregression]
tags: [hierarchical, reconciliation, bottom-up, top-down, mint]
skills: [from-scratch, scale, communication]
---

## Warm-up

```check
{"q": "A company forecasts each store separately. What is the problem if the head office also forecasts the national total separately?", "type": "single",
 "options": ["The store forecasts may not add up to the national forecast", "Stores cannot be forecast", "The national total has no trend"],
 "answer": 0,
 "why": ["Correct: two independent forecasts of the same quantity differ in general.", "Stores can be forecast. The issue is consistency.", "The national total can have a trend like any series."]}
```

```check
{"q": "What does a matrix times a vector do in this lesson?", "type": "single",
 "options": ["It sums or copies the entries of the vector into new rows", "It sorts the vector", "It removes outliers"],
 "answer": 0,
 "why": ["Correct: each row of a 0/1 matrix selects and adds some entries.", "Sorting is not a matrix product.", "Outlier removal is a different task."]}
```

## Why it matters

Most business data has a **hierarchy**: product → category → department → company; or store → region → country. Managers look at all levels. If the store forecasts add up to 950 but the country forecast says 1000, people stop trusting the numbers. We want forecasts that are **coherent**: the parts always add up to the whole. **Reconciliation** makes them so. A good reconciliation can also make every level more accurate. Large retail forecasting tasks, such as the M5 competition data (Walmart sales in states, stores, departments and items), have this structure.

## Hierarchy and the summing matrix

Example: a Total with two regions, A and B. The **bottom-level** series are A and B. The **aggregates** are the series made by summing: Total = A + B.

Put all series in one vector y = (Total, A, B). The bottom series are b = (A, B). Then:

y = S · b

with the **summing matrix** S:

| | A | B |
|---|---|---|
| Total | 1 | 1 |
| A | 1 | 0 |
| B | 0 | 1 |

Each row of S says which bottom series are added to make that series. The bottom rows form an identity matrix.

Numbers: A = 30, B = 20. Then y = S·b = (50, 30, 20).

A forecast vector ŷ is **coherent** if it equals S·b for some b. Forecasts from separate models are almost never coherent. Example: Total = 52, A = 31, B = 19. But 31 + 19 = 50, not 52.

```check
{"q": "A hierarchy has Total = A + B + C. How many bottom series and how many rows does S have?", "type": "single",
 "options": ["3 bottom series, S has 4 rows", "4 bottom series, S has 3 rows", "3 bottom series, S has 3 rows"],
 "answer": 0,
 "why": ["Correct: rows are Total, A, B, C (4), columns are the 3 bottom series.", "The bottom series are A, B, C only. The total is an aggregate.", "S also needs the row for the Total."]}
```

## Bottom-up and top-down

**Bottom-up:** forecast every bottom series. Sum them to get all upper levels: ỹ = S·b̂.

- Good: uses the detail of the bottom series. The result is coherent.
- Bad: the bottom series are noisy (or intermittent), and the noise adds up.

**Top-down:** forecast the Total. Split it with **proportions** p_j for each bottom series:

b̃_j = p_j · Total forecast

Two common ways to get p_j from history:

- **Average of proportions:** the mean over time of y_j(t) / Total(t).
- **Proportion of averages:** the mean of y_j divided by the mean of the Total.

Numbers: history A = 30, 40 and B = 20, 20; Total = 50, 60. Proportion of averages for A = 35 / 55 = 0.636. If the Total forecast is 66, then A = 42 and B = 24.

- Good: the Total is smooth and easy to forecast.
- Bad: proportions are fixed, so local trends are lost. The lower levels are less accurate.

**Middle-out:** forecast a middle level, sum up to the top, split down to the bottom.

```check
{"q": "The Total forecast is 100. Proportions are A 0.7 and B 0.3 (top-down). What is the forecast for B?", "type": "numeric",
 "answer": 30, "tol": 0.001,
 "why": "0.3 * 100 = 30."}
```

## Optimal reconciliation: use every forecast

Bottom-up and top-down each use only one level. **Optimal reconciliation** forecasts **all** series (the "base forecasts" ŷ), and then adjusts them to be coherent, using information from all levels. It finds the coherent forecasts that are closest to the base forecasts:

b̃ = (Sᵀ W⁻¹ S)⁻¹ Sᵀ W⁻¹ ŷ  and  ỹ = S · b̃

- ŷ: the base forecasts of all series (not coherent).
- S: the summing matrix. Sᵀ is its transpose.
- W: the covariance matrix of the base forecast errors. It says which forecasts are reliable.
- b̃: the new bottom forecasts. ỹ: the coherent forecasts for all levels.

Choices of W:

- **OLS:** W = identity. All forecasts count the same.
- **WLS:** W is diagonal, with the error variance of each series. Noisy series get less weight.
- **MinT** (minimum trace; Wickramasuriya, Athanasopoulos and Hyndman, 2019): W is estimated from the full error covariance (often shrunk). It minimises the total variance of the reconciled errors.

Numbers (OLS): ŷ = (52, 31, 19). SᵀS = [[2, 1], [1, 2]]. Sᵀŷ = (83, 71). The solution is b̃ = ((2·83 − 71)/3, (−83 + 2·71)/3) = (31.67, 19.67). Total = 51.33. The error of 2 was shared among the three series.

```chart
{"title": "Base forecasts (not coherent) and OLS-reconciled forecasts: bars 1 = Total, 2 = A, 3 = B", "x": "series", "height": 220,
 "series": [
  {"name": "base forecast", "kind": "bar", "x": [1, 2, 3], "y": [52, 31, 19]},
  {"name": "reconciled (OLS)", "kind": "bar", "x": [1, 2, 3], "y": [51.33, 31.67, 19.67]}
 ],
 "caption": "The base A + B is 50 but the base Total is 52. After reconciliation 31.67 + 19.67 = 51.33, which equals the new Total."}
```

```check
{"q": "What is the main advantage of optimal reconciliation (MinT) over pure bottom-up?", "type": "single",
 "options": ["It uses the forecasts of all levels and often reduces the error", "It needs no forecast models", "It removes the need for a summing matrix", "It always makes the bottom level exact"],
 "answer": 0,
 "why": ["Correct: information from the smooth upper levels helps the noisy bottom level.", "Base forecasts for every series are still needed.", "S is the core of the method.", "It adjusts the bottom level, so it is not exact."]}
```

## Practical notes

- Choose a good **base method** for each series (ETS, ARIMA, baselines). Reconciliation is a post-processing step.
- Use a backtest to compare bottom-up, top-down and MinT on each level. Bottom-up often wins at the bottom, top-down at the top, and reconciliation is often good at all levels.
- Reconciled forecasts can be negative. Clip or use a method with non-negativity.
- Grouped hierarchies (for example product × region) have several ways to add up; they still use S.
- Libraries: `hierarchicalforecast` (Nixtla) in Python, and `fable` / `forecast` in R.

## Worked example

We build S for a 3-level hierarchy (Total → regions A and B → four shops). We compare bottom-up, top-down and OLS reconciliation.

```python
import numpy as np

# Hierarchy: Total = A + B, A = A1 + A2, B = B1 + B2
# Rows: Total, A, B, A1, A2, B1, B2    Columns: A1, A2, B1, B2
S = np.array([
    [1, 1, 1, 1],   # Total
    [1, 1, 0, 0],   # A
    [0, 0, 1, 1],   # B
    [1, 0, 0, 0],   # A1
    [0, 1, 0, 0],   # A2
    [0, 0, 1, 0],   # B1
    [0, 0, 0, 1],   # B2
])

# Base forecasts for the next period (not coherent: the parts do not add up)
y_hat = np.array([100.0, 58.0, 38.0, 30.0, 26.0, 22.0, 18.0])
print("A1 + A2 + B1 + B2 =", y_hat[3:].sum(), "but Total =", y_hat[0])

# 1) Bottom-up: keep the bottom forecasts, sum upwards
bottom_up = S @ y_hat[3:]
print("bottom-up:", bottom_up)

# 2) Top-down: keep the Total, split with historical proportions of the shops
history = np.array([[28, 25, 20, 17], [32, 27, 21, 20], [30, 26, 23, 19]], dtype=float)
p = history.mean(axis=0) / history.sum(axis=1).mean()      # proportion of averages
top_down = S @ (y_hat[0] * p)
print("proportions:", np.round(p, 3))
print("top-down:", np.round(top_down, 1))

# 3) OLS reconciliation: b = (S'S)^-1 S' y_hat
b = np.linalg.solve(S.T @ S, S.T @ y_hat)
ols = S @ b
print("OLS:", np.round(ols, 2))
print("coherent?", np.allclose(ols[0], ols[3:].sum()), np.allclose(ols[1], ols[3] + ols[4]))
# Output:
# A1 + A2 + B1 + B2 = 96.0 but Total = 100.0
# bottom-up: [96. 56. 40. 30. 26. 22. 18.]
# proportions: [0.312 0.271 0.222 0.194]
# top-down: [100.   58.3  41.7  31.2  27.1  22.2  19.4]
# OLS: [98.29 58.48 39.81 31.24 27.24 21.9  17.9 ]
# coherent? True True
```

## Common mistakes

- Forecasting each level separately and showing the numbers without reconciliation.
- Using top-down with fixed proportions when the shares change over time.
- Computing proportions with the test period (leakage).
- Reconciling with an unreliable covariance estimate. Use a simple W (OLS or WLS) when you have few data.
- Evaluating only the top level. Check accuracy at every level.

## Interview lens

**Typical question:** "You forecast sales for 10,000 products, 200 stores and the company total. The numbers do not add up. What do you do?"

**Strong answer:** The forecasts are incoherent, so I would reconcile them. The simple options are bottom-up, which sums the lowest-level forecasts, and top-down, which splits the total by historical proportions. A better option is optimal reconciliation. It takes base forecasts at every level and projects them onto the coherent space defined by the summing matrix S. The weights come from the forecast error covariance (MinT), or from a simple diagonal estimate (WLS). I would compare all options in a backtest on every level, since bottom-up is often best at the bottom and top-down at the top.

**Red flags:** Not knowing what coherent means. Using top-down without noting that it loses local changes. Mixing the roles of S and the base forecasts. Evaluating only one level.

## Real world

- The M5 competition (2020) used Walmart sales data with a 12-level hierarchy (item, department, store, state and total). Its accuracy metric, WRMSSE, weighted the levels.
- Wickramasuriya, Athanasopoulos and Hyndman published the MinT reconciliation method in 2019. Rob Hyndman's book "Forecasting: Principles and Practice" has a free chapter on hierarchical forecasting.

## Key points

- A hierarchy gives coherence: y = S·b, where S is the summing matrix and b the bottom series.
- Bottom-up: forecast the bottom, then sum. Top-down: forecast the total, then split by proportions.
- Optimal reconciliation (OLS, WLS, MinT) adjusts the base forecasts of all levels to be coherent: b̃ = (SᵀW⁻¹S)⁻¹SᵀW⁻¹ŷ.
- Always backtest all levels. Reconciliation often helps every level.
