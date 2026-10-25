---
slug: llmtime-digit-encoding
title: Numbers as Text for an LLM (LLMTime Encoding)
difficulty: Medium
type: function
tags: [llm, tokenization, llmtime]
skills: [from-scratch]
packages: []
---
The **LLMTime** idea (Gruver et al., 2023) writes a time series as plain text, so a language model can continue it.
Many tokenizers cut long numbers into odd pieces (for example "1234" may become "12" + "34").
To avoid this, LLMTime writes **each digit separately, with spaces between digits**, and separates time steps with a comma.

Write two functions:

`llm_encode(values, decimals=2)`

1. Multiply each value by `10**decimals` and round to an integer (use `int(round(v * 10**decimals))`).
2. Let `width` be the number of digits of the largest absolute integer (at least 1). Write each number with **zero padding** to `width` digits. A negative number starts with a `-` token.
3. Join the digits of one value with a space, and join values with `" , "`.

`llm_decode(text, decimals=2)` is the inverse. It returns a list of floats. An empty text returns `[]`.

### Example 1
**Input:** `llm_encode([1.23, 45.6], decimals=2)`
**Output:** `'0 1 2 3 , 4 5 6 0'`
**Explanation:** Integers are 123 and 4560. The widest has 4 digits, so 123 becomes `0123`.

### Example 2
**Input:** `llm_encode([-0.5, 0.25], decimals=2)`
**Output:** `'- 5 0 , 2 5'`
**Explanation:** Integers are −50 and 25. Width is 2. The minus sign is a separate token.

### Constraints
- `0 <= len(values) <= 10^4`, `0 <= decimals <= 6`.
- Values are finite floats. After encoding and decoding, each value is correct up to `10**-decimals / 2`.

### Hints
1. `s = str(abs(n)).zfill(width)` pads with zeros; `" ".join(s)` puts spaces between digits.
2. A negative number: prefix `"- "` before the digits.
3. For decoding, split on `" , "`, remove spaces inside each part, check for a leading `-`, then divide by `10**decimals`.

### Solution explanation
Fixed width keeps every number the same length, so the position of a digit always has the same meaning (for the model, the third digit is always the same place value).
Cost: the text is long. A series of 1000 values with 4 digits each needs about 9000 tokens counting spaces and commas, which is why LLMs on long series are slow and costly.
Time `O(total digits)`.
