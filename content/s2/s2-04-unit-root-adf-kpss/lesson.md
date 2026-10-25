---
id: s2-04-unit-root-adf-kpss
title: Unit-root tests: ADF and KPSS
minutes: 30
level: intermediate
goals: [Explain a unit root in simple words, State the null hypothesis of ADF and of KPSS and why they are opposite, Read the output of adfuller and kpss in statsmodels, Combine both tests into a decision about differencing]
prereqs: [s2-03-acf-pacf]
tags: [adf, kpss, unit-root, statsmodels]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "The ACF of a series decays very slowly and stays high for 30 lags. What is likely?", "type": "single",
 "options": ["Trend or random walk: not stationary", "White noise", "An MA(1) process"],
 "answer": 0,
 "why": ["Correct: slow decay is the typical sign of a trend or a random walk.", "White noise has all ACF bars inside the band.", "An MA(1) has an ACF that stops after lag 1."]}
```

```check
{"q": "What does the first difference of a random walk give?", "type": "single",
 "options": ["White noise", "A trend", "A season"],
 "answer": 0,
 "why": ["Correct: the changes of a random walk are the shocks.", "A trend would need a constant change.", "A season would need a repeating pattern."]}
```

## Why it matters

Plots can lie. A series can look stationary to your eye and still wander. You need a number to support your choice to difference or not. **Unit-root tests** give you that number. They are very common in interviews, but many people read them wrong. The main trap: the two famous tests, ADF and KPSS, have **opposite** null hypotheses.

## What is a unit root?

Take the simple model y(t) = φ·y(t−1) + ε(t). The number φ (phi) controls the memory.

- If |φ| < 1, a shock fades away. Example φ = 0.5: a shock of 1 becomes 0.5, 0.25, 0.125. The series returns to its mean. It is **stationary**.
- If φ = 1, a shock never fades. This is the random walk. We say the series has a **[[unit root]]**. It is not stationary.

A unit-root test asks: "Is φ equal to 1, or smaller than 1?"

```chart
{"title": "phi = 0.5 returns to its mean. phi = 1 wanders away.", "x": "time", "height": 220,
 "series": [
  {"name": "phi 0.5 (stationary)", "gen": [["ar1", {"phi": 0.5, "sd": 1}]], "n": 200, "seed": 8},
  {"name": "phi 1 (unit root)", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 200, "seed": 8}
 ],
 "caption": "Same shocks, different memory. Only phi = 1 gives a random walk."}
```

```check
{"q": "In y(t) = 0.9·y(t−1) + ε(t), a shock of 10 happens now. About how big is its effect 2 steps later?", "type": "numeric",
 "answer": 8.1, "tol": 0.05,
 "why": "The effect is multiplied by 0.9 each step. 10 * 0.9 * 0.9 = 8.1. It fades, so the series is stationary."}
```

## The ADF test

The **Augmented Dickey-Fuller (ADF)** test checks the unit root directly. It fits this regression:

Δy(t) = α + γ·y(t−1) + δ₁·Δy(t−1) + ... + ε(t)

- Δy(t) = y(t) − y(t−1), the change.
- γ (gamma) = φ − 1. If γ = 0 there is a unit root.
- The extra lagged changes (the "augmented" part) remove autocorrelation from the errors.

**Null hypothesis H0: the series HAS a unit root (not stationary).**

- Small p-value (< 0.05): reject H0. The data supports **stationary**.
- Large p-value: you cannot reject H0. The series may have a unit root.

The test statistic is a negative number. **More negative = stronger evidence for stationarity.** Compare it with the critical values. If it is below the 5% value (about −2.86 for a constant), reject H0.

## The KPSS test

The **KPSS** test asks the opposite question.

**Null hypothesis H0: the series IS stationary (around a constant, or around a trend).**

- Small p-value (< 0.05): reject H0. The data supports **not stationary**.
- Large p-value: no evidence against stationarity.

Here a **bigger** statistic is stronger evidence against stationarity.

| Test | H0 | Small p-value means |
|---|---|---|
| ADF | unit root (not stationary) | stationary |
| KPSS | stationary | not stationary |

```check
{"q": "ADF p-value = 0.01. What is the conclusion?", "type": "single",
 "options": ["Reject the unit root: evidence of stationarity", "The series is a random walk", "The test failed"],
 "answer": 0,
 "why": ["Correct: H0 is 'unit root'. A small p-value rejects it.", "That would need a large p-value, not a small one.", "A small p-value is a normal test result."]}
```

```check
{"q": "KPSS p-value = 0.01. What is the conclusion?", "type": "single",
 "options": ["Evidence that the series is NOT stationary", "Evidence that the series is stationary", "Nothing, the test is invalid"],
 "answer": 0,
 "why": ["Correct: H0 is 'stationary'. A small p-value rejects it.", "This is the ADF reading. KPSS is the opposite.", "The test is fine. The result says: not stationary."]}
```

## Use both tests together

Because the nulls are opposite, you can combine them:

| ADF | KPSS | Conclusion | Action |
|---|---|---|---|
| reject H0 (p small) | do not reject (p large) | **stationary** | Use as is |
| do not reject | reject | **unit root** | Difference the series |
| reject | reject | mixed signals (maybe a trend or a break) | Check the plot, try detrending |
| do not reject | do not reject | not enough data to decide | Look at the plot, collect more data |

## Reading statsmodels output

`adfuller(x)` returns a tuple:

1. test statistic
2. p-value
3. number of lags used
4. number of observations used
5. dictionary of critical values (1%, 5%, 10%)
6. best information criterion value

`kpss(x)` returns: statistic, p-value, number of lags, critical values. KPSS p-values are only in a table from 0.01 to 0.1. If the real p-value is outside, statsmodels prints a warning and gives 0.01 or 0.1.

Use `regression="c"` (constant, default) when the data moves around a level. Use `regression="ct"` when it moves around a straight trend.

## Worked example

We test a random walk, an AR(1) series with φ = 0.5, and the differenced random walk. The code needs the `statsmodels` library. The output below is real.

```python
import warnings
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss

warnings.filterwarnings("ignore")        # KPSS prints a warning when p is outside its table

rng = np.random.default_rng(0)
e = rng.normal(size=300)
walk = np.cumsum(e)                      # unit root
ar = np.zeros(300)
for t in range(1, 300):
    ar[t] = 0.5 * ar[t - 1] + e[t]       # stationary

def verdict(name, x):
    adf_stat, adf_p, *_ = adfuller(x, regression="c", autolag="AIC")
    kpss_stat, kpss_p, *_ = kpss(x, regression="c", nlags="auto")
    adf_ok = adf_p < 0.05                # ADF rejects "unit root"
    kpss_ok = kpss_p >= 0.05             # KPSS does NOT reject "stationary"
    if adf_ok and kpss_ok:
        text = "stationary"
    elif not adf_ok and not kpss_ok:
        text = "unit root -> difference"
    else:
        text = "mixed / unclear"
    print(f"{name:<12} ADF p={adf_p:.3f}  KPSS p={kpss_p:.3f}  -> {text}")

verdict("random walk", walk)
verdict("AR(1) 0.5", ar)
verdict("diff(walk)", np.diff(walk))
# Output:
# random walk  ADF p=0.841  KPSS p=0.010  -> unit root -> difference
# AR(1) 0.5    ADF p=0.000  KPSS p=0.100  -> stationary
# diff(walk)   ADF p=0.000  KPSS p=0.100  -> stationary
```

## Common mistakes

- Mixing up the null hypotheses. For ADF a small p means stationary. For KPSS a small p means NOT stationary.
- Saying "p = 0.20 proves a unit root". You only failed to reject. Power is low with short series.
- Running the test on a series with a strong season or a structural break. Both can fool the test.
- Using the p-value alone and ignoring the plot.
- Forgetting `regression="ct"` when the data has a deterministic trend.

## Interview lens

**Typical question:** "How do you test if a series is stationary? What do ADF and KPSS test?"

**Strong answer:** ADF has the null hypothesis that the series has a unit root. A small p-value means I reject it and call the series stationary. KPSS has the opposite null: the series is stationary, so a small p-value means non-stationary. I use both. If ADF rejects and KPSS does not, I treat the series as stationary. If the opposite happens, I difference once and test again. I also look at the plot and the ACF. The tests have low power on short series and fail with structural breaks.

**Red flags:** Reversing the null hypotheses. Saying "p-value above 0.05 proves the series is a random walk". Using only a test and never plotting. Differencing over and over until the test passes.

## Real world

- The Dickey-Fuller test comes from David Dickey and Wayne Fuller (1979). It is a standard tool in economics, for example for GDP and price series.
- Cointegration, a related idea used for pairs of price series, is built on unit-root tests. Clive Granger and Robert Engle shared the 2003 Nobel Memorial Prize in Economic Sciences for work on such time-series methods.

## Key points

- A unit root (φ = 1) means shocks never fade: the series is a random walk and is not stationary.
- ADF H0: unit root. Small p means stationary. KPSS H0: stationary. Small p means not stationary.
- Use both tests, plus a plot. ADF reject + KPSS not reject = stationary.
- In statsmodels, `adfuller(x)[1]` is the ADF p-value and `kpss(x)[1]` is the KPSS p-value.
- Tests have low power on short series and are fooled by breaks and seasons.
