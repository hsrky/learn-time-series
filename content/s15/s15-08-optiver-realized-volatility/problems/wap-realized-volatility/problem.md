---
slug: wap-realized-volatility
title: WAP and Realized Volatility from an Order Book
difficulty: Medium
type: function
tags: [kaggle, optiver, volatility, finance, groupby]
skills: [pandas-fluency, from-scratch]
packages: []
companies_style: [Kaggle Optiver Realized Volatility Prediction]
---
In *Optiver Realized Volatility Prediction* each 10-minute window (`time_id`) of a stock has order-book snapshots. The best bid is the highest price a buyer offers; the best ask is the lowest price a seller offers. The **weighted average price (WAP)** combines both sides, weighted by the size on the **opposite** side:

`WAP = (bid_price1 × ask_size1 + ask_price1 × bid_size1) / (bid_size1 + ask_size1)`

The **log return** between two snapshots is `log(WAP_t) − log(WAP_{t−1})`. The **realized volatility** of a window is the square root of the sum of the squared log returns:

`RV = sqrt( Σ r_t² )`

Write two functions.

**1. `wap(bid_price1, ask_price1, bid_size1, ask_size1)`** — works on arrays (or numbers) and returns the WAP as a numpy array.

**2. `realized_volatility(book)`** — `book` is a DataFrame with columns `time_id`, `seconds_in_bucket`, `bid_price1`, `ask_price1`, `bid_size1`, `ask_size1`. For each `time_id`, sort its rows by `seconds_in_bucket`, compute the WAP, then the log returns **inside that `time_id` only** (the first row has no return), and the RV. A `time_id` with one row has `rv = 0.0`. Return a DataFrame with columns `time_id, rv`, sorted by `time_id`, index `0, 1, 2, ...`.

### Example 1
`wap(100, 101, 10, 30)` returns `100.25`: `(100 × 30 + 101 × 10) / 40`. The WAP is closer to the bid, because the ask side has more size (more sellers).

### Example 2
One window with WAPs `100, 101, 100`: returns `log(1.01)` and `log(100/101)`; `rv = sqrt(2) × log(1.01) = 0.014072...`

### Constraints
- 0 ≤ rows ≤ 10^5; sizes are positive; prices are positive
- Rows can be in any order

### Hints
1. Compute `wap` with vector arithmetic, then `np.log`.
2. Sort by `time_id` and `seconds_in_bucket`, then `groupby("time_id")["log_wap"].diff()`. The diff must not cross window borders.
3. Square, sum per `time_id` (NaN is skipped by `sum`), and take the square root.

### Solution explanation
`groupby(...).diff()` computes the return only inside each window, so the first snapshot of every window has `NaN` and does not use the previous window. Summing squares of returns estimates variance over the window; its square root is the volatility. Time O(n log n) for the sort. Common bugs: taking `diff` over the whole table (mixes windows), forgetting to sort by time, using the mid price instead of WAP, and dropping windows with one row (they should get 0).
