---
slug: token-bucket
title: Token Bucket Rate Limiter
difficulty: Medium
type: class
tags: [rate-limiting, class, timestamps]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
Implement `TokenBucket(capacity, rate)`.

- The bucket holds at most `capacity` tokens. It starts **full** at time 0 (`last = 0`).
- Tokens are added at `rate` tokens per second.
- `allow(t, cost=1)`: a request arrives at time `t` (seconds, never smaller than a previous `t`). First refill: `tokens = min(capacity, tokens + (t - last) * rate)` and set `last = t`. Then, if `tokens >= cost`, remove `cost` tokens and return `True`. Otherwise return `False` and remove nothing.

A rejected request still updates `last`.

### Example 1
**Input:** `capacity = 3`, `rate = 1`; requests at `0, 0, 0, 0, 1, 1`
**Output:** `[True, True, True, False, True, False]`
**Explanation:** The first three use the 3 tokens. The 4th finds none. At t = 1 one token has returned: allowed. The next request at t = 1 finds none.

### Constraints
- 0 <= number of calls <= 10^5
- capacity > 0, rate >= 0, cost > 0

### Hints
1. Keep two numbers: `tokens` and `last`.
2. Refill first, then check, then spend.
3. Do not forget `min(capacity, ...)`.

### Solution explanation
**Approach.** Lazy refill: we do not run a timer. On each request we compute how many tokens came back since the last request, clamp to the capacity, and decide.

**Why it works.** The number of tokens at any time depends only on the last state and the elapsed time, so two numbers are enough.

**Complexity.** O(1) time per request and O(1) memory per bucket (one bucket per user in practice).

**Common bugs.** Not clamping at the capacity; refilling by a fixed amount per call; forgetting to update `last` when a request is rejected; spending tokens on a rejected request.
