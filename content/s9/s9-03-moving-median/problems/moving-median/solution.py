import heapq
from collections import deque, defaultdict


class MovingMedian:
    def __init__(self, k):
        self.k = k
        self.lo = []                       # max-heap (negated): lower half
        self.hi = []                       # min-heap: upper half
        self.late = defaultdict(int)       # values waiting to be deleted
        self.nlo = 0                       # valid sizes
        self.nhi = 0
        self.win = deque()

    def _prune(self, heap, sign):
        while heap and self.late[sign * heap[0]] > 0:
            self.late[sign * heap[0]] -= 1
            heapq.heappop(heap)

    def _balance(self):
        if self.nlo > self.nhi + 1:
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
            self.nlo -= 1
            self.nhi += 1
            self._prune(self.lo, -1)
        elif self.nlo < self.nhi:
            heapq.heappush(self.lo, -heapq.heappop(self.hi))
            self.nhi -= 1
            self.nlo += 1
            self._prune(self.hi, 1)

    def next(self, x):
        self.win.append(x)
        if not self.lo or x <= -self.lo[0]:
            heapq.heappush(self.lo, -x)
            self.nlo += 1
        else:
            heapq.heappush(self.hi, x)
            self.nhi += 1
        if len(self.win) > self.k:
            out = self.win.popleft()
            self.late[out] += 1
            if out <= -self.lo[0]:
                self.nlo -= 1
                if out == -self.lo[0]:
                    self._prune(self.lo, -1)
            else:
                self.nhi -= 1
                if self.hi and out == self.hi[0]:
                    self._prune(self.hi, 1)
        self._balance()
        if self.nlo > self.nhi:
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2
