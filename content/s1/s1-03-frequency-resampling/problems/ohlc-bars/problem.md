---
slug: ohlc-bars
title: Price Bars With No Gaps
difficulty: Medium
type: function
tags: [pandas, resample, ohlc, finance]
skills: [pandas-fluency]
packages: []
companies_style: [trading data, market data]
---
A Series `prices` holds trade prices at irregular times (a `DatetimeIndex`, sorted). Build regular bars.

Write `ohlc_bars(prices, freq)`. Return a DataFrame with the columns `open`, `high`, `low`, `close`. There is one row per bin of size `freq`, from the first bin to the last bin (bins use the default `resample` rules: left edge, left label).

- For a bin with trades: `open` is the first price, `high` the largest, `low` the smallest, `close` the last price.
- For a bin **without** trades: all four values equal the `close` of the **previous** bin (the price did not change).

### Example 1
**Input:** trades at 09:00:10 → 100, 09:02:30 → 101.5, 09:04:50 → 99, 09:16:20 → 103; `freq = "5min"`
**Output:**

| time | open | high | low | close |
|---|---|---|---|---|
| 09:00 | 100 | 101.5 | 99 | 99 |
| 09:05 | 99 | 99 | 99 | 99 |
| 09:10 | 99 | 99 | 99 | 99 |
| 09:15 | 103 | 103 | 103 | 103 |

**Explanation:** The bins 09:05 and 09:10 have no trade, so they repeat the last close, 99.

### Constraints
- `1 <= len(prices) <= 10^5`; prices are positive floats.
- `freq` is a fixed step such as `"5min"`, `"h"` or `"D"`.
- The first bin always has at least one trade.

### Hints
1. `prices.resample(freq).ohlc()` gives the bars, with NaN rows for empty bins.
2. Fill `close` first with `ffill()`: the empty bins take the previous close.
3. For the other columns, empty bins must take the (filled) close value of the same row.

### Solution explanation
1. `bars = prices.resample(freq).ohlc()` creates every bin between the first and the last trade.
2. `bars["close"] = bars["close"].ffill()` carries the last known close forward. It uses only the past.
3. For `open`, `high`, `low`, replace NaN with the filled `close` of the same row: `bars[c].fillna(bars["close"])`.

Time O(n + m) for m bins. Bug to avoid: `bars.ffill()` on all columns would copy an old high or low into an empty bin.
