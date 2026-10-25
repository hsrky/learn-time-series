class RunningStats:
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)       # uses the NEW mean
        var = self.m2 / (self.n - 1) if self.n > 1 else 0.0
        return (self.mean, var)
