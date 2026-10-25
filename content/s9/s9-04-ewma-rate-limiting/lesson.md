---
id: s9-04-ewma-rate-limiting
title: Streaming EWMA and token-bucket rate limiting
minutes: 30
level: intermediate
goals: [Implement a streaming EWMA, Handle irregular timestamps, Implement a token bucket]
prereqs: [s9-01-online-statistics]
tags: [streaming, ewma, rate-limiting]
skills: [streaming-algorithms, from-scratch]
---
## Warm-up
```check
{"q": "In an exponentially weighted moving average, a larger alpha means...", "type": "single", "options": ["The average reacts faster to new values", "The average reacts slower", "The average ignores new values"], "answer": 0, "why": ["Correct.", "That is a small alpha.", "Alpha = 0 would do that."]}
```
```check
{"q": "In Welford's algorithm, how much memory is used per stream?", "type": "single", "options": ["O(1)", "O(n)", "O(n²)"], "answer": 0, "why": ["Correct: three numbers.", "That would store every value.", "No."]}
```

## Why it matters
Two questions appear again and again in [[streaming]] systems:

1. "Give me a **smooth** estimate of the current level, using only O(1) memory." The answer is the **[[EWMA]]**.
2. "Allow at most N requests per second per user." The answer is a **rate limiter**. The classic one is the **[[token bucket]]**.

Both are small classes. Interviewers like them because they test state, time and edge cases.

## Streaming EWMA
The EWMA keeps one number, the current estimate `s`. For each new value `x`:

`s(t) = α · x(t) + (1 − α) · s(t−1)`      with `s(0) = x(0)`

- `α` (alpha) in (0, 1] = how much weight the new value gets
- `s(t−1)` = the old estimate

Example with α = 0.5 and values 10, 20, 30. First s = 10. Then 0.5·20 + 0.5·10 = 15. Then 0.5·30 + 0.5·15 = 22.5.

This is the same as `pandas.Series.ewm(alpha=0.5, adjust=False).mean()`. Cost: **O(1) time, O(1) memory** per value. A simple guide: the "memory" of the average is about `1/α` values. With `α = 0.1`, it is about 10 values.

```chart
{"title": "A noisy level that jumps up", "x": "t", "height": 210, "series": [{"name": "stream", "gen": [["const", {"value": 10}], ["noise", {"sd": 2}], ["step", {"at": 50, "size": 8}]], "n": 100, "seed": 12}, {"name": "true level", "gen": [["const", {"value": 10}], ["step", {"at": 50, "size": 8}]], "n": 100, "dash": true}], "caption": "An EWMA with a small alpha is smooth but slow after the jump. A large alpha follows the jump fast but keeps more noise."}
```

```check
{"q": "α = 0.2, old estimate 50, new value 100. What is the new estimate?", "type": "numeric", "answer": 60, "tol": 0.01, "why": "0.2 × 100 + 0.8 × 50 = 20 + 40 = 60."}
```

## Irregular timestamps
If values arrive at uneven times, a fixed α is wrong: a value after a long pause should count more. Use the time [[gap]] `dt` and a time constant `τ` (tau):

`α = 1 − exp(−dt / τ)`

A long gap makes α close to 1 (the old estimate is almost forgotten). A short gap makes α small.

```check
{"q": "Values arrive at irregular times. Why is a constant α a weak choice?", "type": "single", "options": ["A value after a long pause carries more new information, so it should get a larger weight", "Constant α is not allowed", "It needs more memory"], "answer": 0, "why": ["Correct: use alpha = 1 − exp(−dt/τ).", "It is allowed, only less accurate.", "Memory is the same."]}
```

## Rate limiting with a token bucket
Picture a [[bucket]] that holds up to **capacity** tokens. Tokens are added at a steady **rate** (for example 2 per second), but never above the capacity. Each request needs a token (or `cost` tokens). If there are enough, take them and **allow** the request. If not, **reject**.

You do not need a timer. Store only `tokens` and `last_time`. On a request at time `t`:

1. `tokens = min(capacity, tokens + (t − last_time) · rate)`
2. `last_time = t`
3. If `tokens >= cost`: `tokens −= cost`, allow. Else reject.

Example: capacity 3, rate 1 per second, start full. Requests at t = 0, 0, 0, 0 → allow, allow, allow, reject (empty). A request at t = 1 → one token has been added → allow.

| Limiter | Memory | Allows bursts? | Weakness |
|---|---|---|---|
| Fixed [[window]] counter | O(1) | up to 2× at the window edge | burst at the boundary |
| Sliding window log | O(requests in window) | no | memory |
| Token bucket | O(1) | yes, up to capacity | needs two numbers |

```chart
{"title": "Token bucket: tokens over time (capacity 3, rate 1/s)", "x": "time (s)", "height": 210, "series": [{"name": "tokens", "y": [3, 2, 1, 0, 0, 1, 2, 3, 3, 2, 1, 0, 1, 2, 3], "kind": "line"}], "caption": "Each request removes a token. Between requests, the bucket refills by 1 token per second, up to 3."}
```

```check
{"q": "Capacity 5, rate 2 per second, bucket is empty at t = 10. A request arrives at t = 11. What happens?", "type": "single", "options": ["Allowed: 2 tokens were added", "Rejected: the bucket is empty", "Allowed: the bucket is full"], "answer": 0, "why": ["Correct: 1 s × 2 tokens/s = 2 tokens, enough for cost 1.", "It was refilled during the second.", "It holds only 2 tokens."]}
```

## Worked example
Streaming EWMA and a small token bucket.

```python
import math

class EWMA:
    def __init__(self, alpha):
        self.alpha, self.s = alpha, None
    def update(self, x):
        self.s = x if self.s is None else self.alpha * x + (1 - self.alpha) * self.s
        return self.s

e = EWMA(0.5)
print([e.update(x) for x in [10, 20, 30]])

class TokenBucket:
    def __init__(self, capacity, rate):
        self.cap, self.rate = capacity, rate
        self.tokens, self.last = float(capacity), 0.0       # start full
    def allow(self, t, cost=1):
        self.tokens = min(self.cap, self.tokens + (t - self.last) * self.rate)   # refill
        self.last = t
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

b = TokenBucket(3, 1)
print([b.allow(t) for t in [0, 0, 0, 0, 1, 1, 3.5]])

# Output:
# [10, 15.0, 22.5]
# [True, True, True, False, True, False, True]
```

## Common mistakes
- Starting the EWMA at 0 (it is biased low for a long time). Start with the first value.
- Mixing the roles of α: a **larger** α means **less** smoothing.
- Refilling tokens by a fixed amount per call instead of by elapsed time.
- Letting tokens grow above the capacity.
- Updating `last_time` only when a request is allowed (the refill then counts twice).

## Interview lens
**Typical question:** "Implement a rate limiter that allows 100 requests per minute per user."

**Strong answer:** I would use a token bucket per user: store the token count and the last [[timestamp]]. On each request I add `elapsed × rate` tokens up to the capacity, then take one token if available. It uses O(1) memory per user, O(1) time per request, and allows short bursts up to the capacity. I would mention alternatives. The fixed window counter has burst problems at the edge. The sliding window log is exact but uses memory. In a distributed system I would keep the state in a shared store and make the update atomic.

**Red flags:** using a timer thread per user; not clamping at the capacity; fixed window without mentioning the boundary burst.

## Real world
- Token-bucket and leaky-bucket limiters are used in network traffic shaping and in API gateways of cloud providers. Many public API docs describe limits as "requests per second with a burst".
- EWMA is used for smoothed latency estimates. One example is the round-trip time estimate in TCP (Jacobson, 1988), which uses an exponential average.

## Key points
- EWMA: `s = α·x + (1−α)·s`, O(1) time and memory. Start with the first value.
- Irregular times: use `α = 1 − exp(−dt/τ)`.
- Token bucket: store tokens and last time; refill by elapsed time, clamp at capacity, spend on request.
- Compare limiters by memory and burst behaviour.
