import numpy as np

rng = np.random.default_rng(6)
R = list(np.round(rng.normal(0, 30, size=40), 2))

CASES = [
    {"name": "padding to widest", "call": "llm_encode([1.23, 45.6], decimals=2)", "visible": True},
    {"name": "negative number", "call": "llm_encode([-0.5, 0.25], decimals=2)", "visible": True},
    {"name": "decode", "call": "llm_decode('0 1 2 3 , 4 5 6 0', decimals=2)", "visible": True},
    {"name": "empty", "call": "llm_encode([])"},
    {"name": "zero decimals", "call": "llm_encode([7.0, 12.0, 3.0], decimals=0)"},
    {"name": "all zeros", "call": "llm_encode([0.0, 0.0])"},
    {"name": "decode negative", "call": "llm_decode('- 5 0 , 2 5')"},
    {"name": "empty decode", "call": "llm_decode('')"},
    {"name": "round trip on 40 random values", "call": "llm_decode(llm_encode(R, 2), 2)"},
    {"name": "encoded length", "call": "len(llm_encode(R, 2).split(' , '))", "expected": "40"},
]
