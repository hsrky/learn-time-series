---
id: s11-01-m-competitions
title: The M competitions: M3, M4, M5 and M6
minutes: 30
level: intermediate
goals: [Describe what each M competition tested and who won, Compute the OWA score used in M4, Explain the main lessons about simple methods, combinations and global ML models]
prereqs: [s10-09-design-capacity-eta]
tags: [M4, M5, competitions, OWA, combinations, LightGBM]
skills: [forecast-metrics, case-studies]
---

## Warm-up

```check
{"q": "A global model is...", "type": "single",
 "options": ["One model per series", "One model trained on many series together", "A model that forecasts the whole world"],
 "answer": 1,
 "why": ["That is a local model.", "Correct.", "The word global refers to the training data, not to geography."]}
```

```check
{"q": "MASE divides the forecast error by...", "type": "single",
 "options": ["The mean of the actual values", "The error of a naive forecast on the training data", "The number of series"],
 "answer": 1,
 "why": ["That is closer to WAPE.", "Correct: this scale makes errors comparable across series.", "Series count is not a scale for one series."]}
```

## Why it matters

Before 1979 many people believed that complex forecasting methods must be better than simple ones. Spyros Makridakis and colleagues tested this with open **[[forecasting competition|forecasting competitions]]**: many methods, the same data, hidden test values. The "M competitions" (M for Makridakis) changed the field. Interviewers like to ask what they showed, because the answers are practical rules. Start with strong baselines. Combine models. Use global models for many related series.

## The competitions in short

| Competition | Data | Winner / main finding |
|---|---|---|
| **M3** (2000) | 3 003 series (yearly, quarterly, monthly, other) | Simple methods did as well as complex ones. The Theta method (Assimakopoulos and Nikolopoulos) did very well. Combinations helped. |
| **M4** (2018) | 100 000 series in six frequencies | **Slawek Smyl** (Uber) won with a hybrid of exponential smoothing and an RNN (ES-RNN). The second place used a feature-based combination of statistical models (FFORMA). 12 of the 17 most accurate methods were combinations. Pure ML methods were weak. |
| **M5** (2020) | Walmart sales: 42 840 hierarchical series, 28-day horizon, run on Kaggle | Global **LightGBM**-based models dominated. A second track scored quantile forecasts. |
| **M6** (2022) | Financial: 100 assets, forecasts of ranks and investment decisions | Very hard to beat the market consistently. The idea: test forecasts and decisions together. |

**Note:** exact placings are in the published papers (Makridakis, Spiliotis, Assimakopoulos in the International Journal of Forecasting). We list only the main facts.

## How M4 scored forecasts: OWA

M4 used two metrics and a benchmark. The benchmark is **[[Naive2]]**: a naive forecast of the *seasonally adjusted* series.

- **[[sMAPE]]** = mean of `200 · |y − f| / (|y| + |f|)`, a percent.
- **[[MASE]]** = mean `|y − f|` divided by the in-sample error of a seasonal naive forecast.

**[[OWA]] = 0.5 · ( sMAPE / sMAPE_naive2 + MASE / MASE_naive2 )**

- `sMAPE`, `MASE`: your averages over all series.
- `sMAPE_naive2`, `MASE_naive2`: the same for Naive2.
- OWA = 1 means "as good as Naive2". OWA below 1 is better. The M4 winner had an OWA of about 0.82. So it was about 18% better than the benchmark on this combined score.

```check
{"q": "A method has sMAPE 10 and MASE 1.2. Naive2 has sMAPE 12 and MASE 1.5. What is OWA?", "type": "numeric",
 "answer": 0.8167, "tol": 0.001,
 "why": "0.5 × (10/12 + 1.2/1.5) = 0.5 × (0.8333 + 0.8) = 0.8167."}
```

## Lesson 1: combinations are strong

Different methods make different errors. When you **average** them, some errors cancel. This is why combinations did so well in M4.

```chart
{"title": "Absolute error of two methods and of their average", "x": "month", "height": 230, "series": [{"name": "method A", "y": [3.0, 4.8, 1.4, 2.3, 0.3, 2.9, 3.4, 11.0, 0.0, 0.7, 5.9, 5.1, 3.6, 2.6, 2.8, 7.2, 5.1, 0.3, 8.4, 4.7, 8.1, 1.6, 4.6, 4.6, 3.9, 1.9, 12.1, 0.2, 2.7, 3.7, 6.2, 0.1, 2.9, 1.9, 9.4, 1.8, 2.8, 8.3, 0.5, 2.3, 3.7, 3.4, 4.4, 3.5, 11.2, 6.3, 8.2, 3.7]}, {"name": "method B", "y": [6.8, 9.0, 1.6, 10.2, 2.6, 0.5, 4.1, 1.1, 3.4, 1.0, 5.6, 7.1, 1.8, 5.8, 2.2, 10.1, 6.5, 4.2, 2.4, 3.9, 10.9, 7.8, 0.9, 15.0, 5.8, 3.6, 4.5, 1.1, 5.0, 5.2, 4.5, 6.1, 5.6, 4.8, 0.9, 3.7, 4.2, 9.7, 3.1, 5.7, 4.0, 0.9, 3.1, 1.0, 5.0, 3.3, 3.0, 0.5]}, {"name": "average of A and B", "y": [1.9, 6.9, 1.5, 6.3, 1.1, 1.2, 0.4, 6.1, 1.7, 0.1, 5.8, 1.0, 0.9, 4.2, 0.3, 1.5, 5.8, 2.0, 3.0, 0.4, 9.5, 3.1, 1.9, 5.2, 0.9, 0.9, 3.8, 0.5, 1.1, 0.8, 5.3, 3.1, 4.2, 3.3, 4.2, 2.8, 0.7, 0.7, 1.8, 1.7, 3.8, 2.2, 3.7, 2.2, 3.1, 1.5, 2.6, 2.1]}], "caption": "Illustration with made-up data: the two methods make errors in different directions, so the average has a smaller error (mean 2.7 compared with 4.2 and 4.6)."}
```

Combine models that are **different** (for example ETS, ARIMA and Theta). Two copies of the same model give no gain. Combination also protects you when one model fails on a series.

```check
{"q": "Why does an average of two forecasts often beat both?", "type": "single",
 "options": ["Averages are always more accurate", "Their errors partly cancel when the methods are different", "It uses more data", "It removes seasonality"],
 "answer": 1,
 "why": ["Not always. Two identical models give no gain.", "Correct: different errors cancel, and one bad forecast is diluted.", "Both models use the same data.", "Seasonality handling is unrelated."]}
```

## Lesson 2: simple baselines, and when ML wins

In M3 and early M4 analyses, simple methods (ETS, Theta) were hard to beat on **small, single series**. In M5, on **many related series with prices, promotions and calendar events**, global gradient-boosting models won. The difference is the data:

- Few short series with little other information: statistical methods and combinations.
- Thousands of related series with rich features: global ML (LightGBM, neural nets).
- Hybrid ideas (like ES-RNN) can win. They keep the statistical structure (level, seasonality) and let the neural part learn the rest.

M5 also used a scale-free metric (WRMSSE, weighted by dollar sales over a hierarchy) and a quantile track. Both teach the same lesson: **the metric must match the use**.

```check
{"q": "Which statement about M5 is correct?", "type": "single",
 "options": ["Pure ARIMA per series won", "Global LightGBM-style models were dominant", "No team beat the benchmarks", "It used only one series"],
 "answer": 1,
 "why": ["Per-series ARIMA was not the leading approach.", "Correct.", "Many teams beat the benchmarks.", "It had tens of thousands of hierarchical series."]}
```

## Worked example

We compute sMAPE, MASE and an OWA-like score for three simple methods on 200 simulated monthly series. The benchmark here is seasonal naive (M4 used Naive2).

```python
import numpy as np

rng = np.random.default_rng(0)
m, h, n = 12, 12, 72

def smape_mase(x, y, f):
    smape = np.mean(200 * np.abs(y - f) / (np.abs(y) + np.abs(f)))
    scale = np.mean(np.abs(x[m:] - x[:-m]))                 # in-sample seasonal naive error
    return smape, np.mean(np.abs(y - f)) / scale

res = {k: [] for k in ["seasonal naive", "drift", "average of both"]}
for _ in range(200):
    t = np.arange(n + h)
    s = 100 + 0.8 * t + 15 * np.sin(2 * np.pi * t / m)
    y = s * (1 + rng.normal(0, 0.04, n + h))
    x, test = y[:n], y[n:]
    snaive = x[-m:]                                          # repeat the last season
    drift = np.full(h, x[-1]) + (x[-1] - x[0]) / (n - 1) * np.arange(1, h + 1)
    for name, f in [("seasonal naive", snaive), ("drift", drift), ("average of both", (snaive + drift) / 2)]:
        res[name].append(smape_mase(x, test, f))

avg = {k: np.mean(v, axis=0) for k, v in res.items()}
base = avg["seasonal naive"]
for k, (sm, ma) in avg.items():
    owa = 0.5 * (sm / base[0] + ma / base[1])
    print(f"{k:<16} sMAPE {sm:5.2f}  MASE {ma:4.2f}  OWA {owa:4.2f}")
# Output:
# seasonal naive   sMAPE  6.92  MASE 1.06  OWA 1.00
# drift            sMAPE  8.32  MASE 1.30  OWA 1.21
# average of both  sMAPE  6.73  MASE 1.05  OWA 0.98
```

Drift ignores the season, so it is worse than seasonal naive (OWA 1.21). The average of the two is slightly better (OWA 0.98), because drift adds the trend that seasonal naive misses. The gain is small here. It depends on the data, but it costs almost nothing.

## Common mistakes

- Saying "deep learning won M4". The winner was a hybrid, and most pure ML methods were weak.
- Saying "simple always wins". M5 showed strong global ML on rich retail data.
- Comparing methods with a metric that is not scale-free across series.
- Using one sMAPE number with zeros in the data (sMAPE has problems near zero).
- Forgetting that competitions use fixed horizons and clean data. Production is messier.

## Interview lens

**Typical question:** "What did the M4 and M5 competitions teach us?"

**Strong answer:** M4 had 100 000 series. The winner was a hybrid of exponential smoothing and an RNN. Combinations of statistical methods were strong. Pure ML was weak. M5 used hierarchical Walmart data with prices and events, and global LightGBM-style models won. So the guide is simple. For few series, use strong statistical baselines and combine them. For many related series with covariates, use global ML. Always compare with a naive benchmark, using a scale-free metric such as MASE or OWA.

**Red flags:** Mixing up M4 and M5 winners. Claiming neural networks always win. Not knowing a benchmark metric.

## Real world

The M competitions are public. The papers appear in the International Journal of Forecasting, and the M5 data were hosted on Kaggle. Slawek Smyl worked at Uber when he won M4, and Uber later wrote about related forecasting work. The M-competition findings also influenced open-source libraries. Many tools now include a Theta model, ETS, and combination or ensemble methods by default.

## Key points

- M3: simple methods are hard to beat. M4: hybrid ES-RNN won, combinations were strong, pure ML was weak. M5: global LightGBM on Walmart data. M6: finance, hard to beat the market.
- OWA = 0.5 · (sMAPE/sMAPE_naive2 + MASE/MASE_naive2). Lower is better; 1 means as good as Naive2.
- Combine different models. Errors partly cancel.
- Data decides the method: few series use statistics; many related series with features use global ML.
- Choose a scale-free metric that matches the use.
