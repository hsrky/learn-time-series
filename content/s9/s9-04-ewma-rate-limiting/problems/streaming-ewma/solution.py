import math


class StreamingEWMA:
    def __init__(self, alpha):
        self.alpha = alpha
        self.s = None
        self.last_t = None

    def update(self, x):
        self.s = x if self.s is None else self.alpha * x + (1 - self.alpha) * self.s
        return self.s

    def update_at(self, x, t, tau):
        if self.s is None:
            self.s = x
        else:
            a = 1 - math.exp(-(t - self.last_t) / tau)
            self.s = a * x + (1 - a) * self.s
        self.last_t = t
        return self.s
