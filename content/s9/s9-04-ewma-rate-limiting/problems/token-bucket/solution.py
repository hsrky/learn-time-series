class TokenBucket:
    def __init__(self, capacity, rate):
        self.capacity = capacity
        self.rate = rate
        self.tokens = float(capacity)       # starts full
        self.last = 0.0

    def allow(self, t, cost=1):
        self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)
        self.last = t
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
