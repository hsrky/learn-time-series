---
slug: chronos-tokenizer
title: Chronos-Style Tokenizer
difficulty: Medium
type: function
tags: [chronos, tokenization, foundation-models]
skills: [from-scratch]
packages: []
---
A language model reads **tokens** (integers), not decimals. The Chronos idea turns a time series into tokens in two steps:

1. **Mean scaling:** divide the series by `scale = mean(|x|)` over the context (ignore NaN). If the scale is 0 or there are no valid values, use `scale = 1`.
2. **Quantization:** cut the range `[low, high]` into `n_bins` equal bins. A scaled value `v` gets bin `b = floor((v − low) / (high − low) · n_bins)`, clipped to `0 … n_bins−1`.
   The token id is `b + 2`. Ids 0 and 1 are special: **0 = PAD** (used for missing values, NaN) and **1 = EOS** (not used in this task).

Write:

- `tokenize(x, n_bins=16, low=-4.0, high=4.0)` returns `(tokens, scale)`. `tokens` is an integer numpy array.
- `detokenize(tokens, scale, n_bins=16, low=-4.0, high=4.0)` returns floats: the **center** of each bin, times `scale`. PAD (0) becomes NaN.

(The real Chronos uses 4096 tokens and a wider range; we use small numbers so you can check by hand.)

### Example 1
**Input:** `tokenize(np.array([2.0, 4.0, 6.0]))`
**Output:** `(array([11, 12, 13]), 4.0)`
**Explanation:** The scale is mean(2, 4, 6) = 4. Scaled values are 0.5, 1.0, 1.5. The bin width is 8 / 16 = 0.5.
The bins are `(0.5 + 4) / 0.5 = 9`, 10 and 11. Add 2 for the special tokens: 11, 12, 13.

### Example 2
**Input:** `detokenize(np.array([11, 12, 13]), 4.0)`
**Output:** `array([3.0, 5.0, 7.0])`
**Explanation:** Bin 9 has center `−4 + (9 + 0.5)·0.5 = 0.75`. Times the scale 4 gives 3.0.
The original values were 2, 4, 6, so each error is at most half a bin times the scale = 1.0.

### Constraints
- `0 <= len(x) <= 10^5`; `n_bins >= 2`; `low < high`.
- NaN values give token 0.
- Values outside `[low, high]` go to the first or last bin.

### Hints
1. `scale = np.nanmean(np.abs(x))` gives a warning for all-NaN input: check `np.isnan(x).all()` first.
2. Compute the bin with `np.floor`, then `np.clip`, then add 2. Set NaN positions to 0 at the end.
3. Bin center = `low + (b + 0.5) * width`, with `b = token − 2`.

### Solution explanation
Scaling makes a series of sales in thousands and a series of temperatures in tens look the same to the model.
Quantizing makes the problem "pick the next word", so a normal language-model loss works.
Cost: you lose precision. The error is at most half a bin (times the scale), and values beyond the range are clipped.
Time `O(n)`.
