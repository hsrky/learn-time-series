import random

random.seed(11)
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BIG = [(random.choice(DAYS), random.randint(1, 100)) for _ in range(4000)]

CASES = [
    {"name": "basic", "call": "total_by_day([('Mon', 5), ('Tue', 3), ('Mon', 2)])", "expected": "{'Mon': 7, 'Tue': 3}", "visible": True},
    {"name": "single sale", "call": "total_by_day([('Sun', 9)])", "expected": "{'Sun': 9}", "visible": True},
    {"name": "empty", "call": "total_by_day([])", "expected": "{}"},
    {"name": "decimals", "call": "total_by_day([('a', 1.5), ('a', 2.25), ('b', 0.5)])", "expected": "{'a': 3.75, 'b': 0.5}"},
    {"name": "negative refund", "call": "total_by_day([('Mon', 10), ('Mon', -4)])", "expected": "{'Mon': 6}"},
    {"name": "random 4000", "call": "total_by_day(BIG)"},
]
