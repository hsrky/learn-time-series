from collections import deque


class MovingAverage:
    def __init__(self, k: int):
        self.k, self.q, self.s = k, deque(), 0.0

    def next(self, x: float) -> float:
        self.q.append(x)
        self.s += x
        if len(self.q) > self.k:
            self.s -= self.q.popleft()
        return self.s / len(self.q)
