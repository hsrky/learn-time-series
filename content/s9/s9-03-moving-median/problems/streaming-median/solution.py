import heapq


class StreamMedian:
    def __init__(self):
        self.low = []        # max-heap (stored negated): smaller half
        self.high = []       # min-heap: larger half

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))      # biggest of low goes to high
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))   # keep low >= high in size

    def median(self):
        if not self.low:
            return 0.0
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2
