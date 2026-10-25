import numpy as np

A = np.arange(8.0)
M = np.vstack([np.arange(12.0), -np.arange(12.0)])
rng = np.random.default_rng(2)
BIG = rng.normal(size=(7, 512))

CASES = [
    {"name": "no padding", "call": "patchify(A, 4, 2, pad=False)", "visible": True},
    {"name": "with padding", "call": "patchify(A, 4, 2)", "visible": True},
    {"name": "two channels", "call": "patchify(M, 4, 4, pad=False)", "visible": True},
    {"name": "series shorter than a patch", "call": "patchify(np.arange(3.0), 8, 4, pad=False)"},
    {"name": "padding makes one patch", "call": "patchify(np.arange(5.0), 8, 4)"},
    {"name": "empty series", "call": "patchify(np.zeros((2, 0)), 4, 2)"},
    {"name": "stride 1", "call": "patchify(M, 3, 1)"},
    {"name": "PatchTST sizes 512 / 16 / 8", "call": "patchify(BIG, 16, 8)"},
    {"name": "token count is 64", "call": "patchify(BIG, 16, 8).shape", "expected": "(7, 64, 16)"},
]
