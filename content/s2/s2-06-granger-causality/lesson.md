---
id: s2-06-granger-causality
title: Granger causality and its limits
minutes: 25
level: intermediate
goals: [Explain the idea of Granger causality in one sentence, Describe the two regressions and the F-test behind it, Run and read a Granger test, List why it is not true cause]
prereqs: [s2-05-spurious-regression-cross-correlation]
tags: [granger, causality, f-test]
skills: [communication, from-scratch]
---

## Warm-up

```check
{"q": "The cross-correlation of x and y peaks at k = 3, where k pairs x(t) with y(t+3). What does it mean?", "type": "single",
 "options": ["x leads y by 3 steps", "y leads x by 3 steps", "x causes y for sure"],
 "answer": 0,
 "why": ["Correct: today's x matches y three steps later.", "That needs a peak at k = -3.", "A lead-lag pattern shows order in time. It does not prove cause."]}
```

```check
{"q": "Before you correlate two trending series, what is the first fix?", "type": "single",
 "options": ["Take first differences", "Add a constant", "Use more lags"],
 "answer": 0,
 "why": ["Correct: differences remove the shared trend and avoid spurious results.", "A constant does not remove a trend.", "More lags do not remove the trend."]}
```

## Why it matters

A manager asks: "Does our marketing spend drive sales?" You cannot run an experiment right now, but you have years of data. Granger causality gives a careful, limited answer. It asks: "Does past marketing help to predict sales, once we use past sales too?" It is useful, but only if you know what it does **not** say. Interviewers like candidates who know the limits.

## The idea

Clive Granger (1969) proposed a simple test of **predictive** value.

> X **Granger-causes** Y if the past of X helps to predict Y. The past of Y alone is not enough.

Note the word "predict". It is about forecast quality and about time order. A cause must come before its effect, and Granger tests use this.

Plain example: Do last week's search counts help to predict this week's flu cases, if we already use last week's flu cases? If yes, search counts "Granger-cause" flu cases.

## The two regressions

Pick a number of lags p. Fit two models for Y:

1. **Restricted model** (only Y's own past):
   y(t) = c + a₁·y(t−1) + ... + a_p·y(t−p) + e(t)
2. **Unrestricted model** (add X's past):
   y(t) = c + a₁·y(t−1) + ... + a_p·y(t−p) + b₁·x(t−1) + ... + b_p·x(t−p) + e(t)

Compare the sum of squared errors (RSS) of the two. The bigger model always fits a bit better. The question is: is the improvement bigger than chance?

```check
{"q": "Which model includes the lags of X?", "type": "single",
 "options": ["The unrestricted model", "The restricted model", "Both"],
 "answer": 0,
 "why": ["Correct: the unrestricted model has Y's lags and X's lags.", "The restricted model forces the X coefficients to be zero.", "Only the unrestricted one uses X."]}
```

## The F-test

F = [ (RSS_r − RSS_u) / p ]  /  [ RSS_u / (N − (2p + 1)) ]

- RSS_r: error sum of squares of the restricted model.
- RSS_u: error sum of squares of the unrestricted model.
- p: the number of X lags added (the number of extra parameters).
- N: the number of rows used in the regressions (n − p).
- 2p + 1: the number of parameters in the unrestricted model (constant, p lags of Y, p lags of X).

Numbers: RSS_r = 120, RSS_u = 100, p = 2, N − (2p+1) = 50. Then F = (20 / 2) / (100 / 50) = 10 / 2 = 5.

**H0: all X coefficients are zero (X does not Granger-cause Y).** A large F (small p-value) rejects H0.

```check
{"q": "RSS_r = 60, RSS_u = 50, p = 1, and N-(2p+1) = 40. What is F?", "type": "numeric",
 "answer": 8, "tol": 0.01,
 "why": "F = ((60 - 50) / 1) / (50 / 40) = 10 / 1.25 = 8."}
```

```chart
{"title": "Error sum of squares: bar 1 = restricted model, bar 2 = unrestricted model", "x": "model", "height": 180,
 "series": [{"name": "RSS", "kind": "bar", "x": [1, 2], "y": [120, 100]}],
 "caption": "The bigger model always has a lower error. The F-test asks if the drop from 120 to 100 is larger than chance."}
```

## Running it in statsmodels

`grangercausalitytests(data, maxlag)` needs a 2-column array. **The test asks if the second column Granger-causes the first column.** Run it twice, once for each direction. Use stationary data (differences).

For each lag from 1 to `maxlag`, the output has an F-test (`ssr_ftest`). It gives the F value, the p-value and the degrees of freedom.

## Limits: what it does not say

1. **Not true cause.** A hidden third variable Z can drive both X and Y, with X reacting faster. X will "Granger-cause" Y without any real effect. Example: warm weather drives ice cream sales first and sunburn later.
2. **Needs stationary data.** Trends create spurious results.
3. **Depends on the lags p.** Too few lags miss the link. Too many lags waste data.
4. **Linear, in the mean only.** Non-linear links can be missed.
5. **Instant effects are invisible.** If X affects Y inside the same time step, the past of X adds nothing.
6. **Frequency matters.** If a link happens within an hour and your data is daily, the test is blurred.
7. **Feedback.** X may predict Y and Y may predict X at the same time.

Use it as **evidence for prediction and ordering**. Then back the story with domain knowledge or a causal design, such as an A/B test.

```check
{"q": "Test shows that last week's temperature Granger-causes this week's ice cream sales. Which statement is safe?", "type": "single",
 "options": ["Temperature helps to forecast sales", "Temperature proves a cause in a lab sense", "Ice cream sales cause temperature"],
 "answer": 0,
 "why": ["Correct: Granger causality is about predictive value.", "It is not proof of cause. A hidden variable could be involved.", "Nothing in the test supports this direction. Also, you would test it separately."]}
```

## Worked example

We write the F statistic with numpy only. X truly helps to predict Y here, but Y does not help to predict X.

```python
import numpy as np

def granger_f(y, x, p):
    # F statistic for "x Granger-causes y" with p lags
    y, x = np.asarray(y, float), np.asarray(x, float)
    n = len(y)
    target = y[p:]                                              # y(t) for t = p..n-1
    own = [y[p - k:n - k] for k in range(1, p + 1)]             # y(t-1) ... y(t-p)
    other = [x[p - k:n - k] for k in range(1, p + 1)]           # x(t-1) ... x(t-p)
    ones = np.ones(n - p)
    Xr = np.column_stack([ones] + own)                          # restricted design matrix
    Xu = np.column_stack([ones] + own + other)                  # unrestricted design matrix
    def rss(X):
        beta, *_ = np.linalg.lstsq(X, target, rcond=None)
        resid = target - X @ beta
        return float(resid @ resid)
    rss_r, rss_u = rss(Xr), rss(Xu)
    df2 = (n - p) - (2 * p + 1)
    return ((rss_r - rss_u) / p) / (rss_u / df2)

rng = np.random.default_rng(3)
n = 400
x = rng.normal(size=n)
y = np.zeros(n)
for t in range(1, n):
    y[t] = 0.3 * y[t - 1] + 0.8 * x[t - 1] + rng.normal(0, 0.5)   # x pushes y with a delay of 1

print("x -> y, F:", round(granger_f(y, x, 2), 1))
print("y -> x, F:", round(granger_f(x, y, 2), 1))
print("5% critical F for df (2, 394) is about 3.0")
# Output:
# x -> y, F: 472.7
# y -> x, F: 0.1
# 5% critical F for df (2, 394) is about 3.0
```

## Common mistakes

- Reading the result as proof of cause.
- Testing levels of trending series, not differences.
- Mixing the direction. In statsmodels, the second column is the possible cause.
- Testing one lag only and stopping. Check several values of p, or choose p by AIC.
- Ignoring a common driver that you have not measured.

## Interview lens

**Typical question:** "What is Granger causality? Can you use it to show that marketing drives sales?"

**Strong answer:** X Granger-causes Y if the past of X improves the forecast of Y beyond Y's own past. We fit a regression of Y on its lags, add the lags of X, and use an F-test on the extra coefficients. It shows predictive value and time order, not true cause. A hidden third variable, a trend, or an instant effect can all mislead the test. So I would use stationary data and try several lags. Then I would support the claim with an experiment, such as an A/B test.

**Red flags:** Saying it proves cause. Not knowing the null hypothesis. Using it on trending levels. Ignoring confounders.

## Real world

- Clive Granger introduced the concept in a 1969 paper in the journal Econometrica. He shared the 2003 Nobel Memorial Prize in Economic Sciences for methods of analysing economic time series.
- It is widely used in economics and in neuroscience. For example, researchers ask which brain signal leads another.

## Key points

- X Granger-causes Y if the past of X improves the forecast of Y, given the past of Y.
- Test: fit restricted and unrestricted regressions and compare with an F-test. H0: X does not help.
- Use stationary data. Choose lags carefully. Test both directions.
- It shows predictive value, not true cause. Hidden variables and instant effects can mislead.
