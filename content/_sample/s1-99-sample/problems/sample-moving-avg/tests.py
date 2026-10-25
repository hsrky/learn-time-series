CASES = [
    {"name": "basic", "call": "m = MovingAverage(3)\n[m.next(x) for x in [1, 10, 3, 5]]", "visible": True},
    {"name": "k=1", "call": "m = MovingAverage(1)\n[m.next(x) for x in [4, 5, 6]]", "visible": True},
    {"name": "k large", "call": "m = MovingAverage(10)\n[m.next(x) for x in range(5)]"},
    {"name": "long", "call": "m = MovingAverage(4)\n[m.next(x * 1.5) for x in range(50)]"},
]
