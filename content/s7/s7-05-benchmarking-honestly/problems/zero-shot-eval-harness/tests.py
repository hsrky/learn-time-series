import numpy as np

TR1 = [np.array([1.0, 2, 3, 2, 3, 4])]
TE1 = [np.array([3.0, 3, 5])]
rng = np.random.default_rng(13)
TRB, TEB, F_A, F_B = [], [], [], []
for k in range(40):
    t = np.arange(120 + k)
    s = 10 + 0.05 * t + 3 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.5, size=len(t))
    TRB.append(s[:-12]); TEB.append(s[-12:])
    F_A.append(TRB[-1][-12:] + 0.05 * 12)            # snaive plus drift
    F_B.append(np.full(12, TRB[-1].mean()))           # mean forecast

CASES = [
    {"name": "model equals seasonal naive", "call": "evaluate_models(TR1, TE1, {'same': [np.array([2.0, 3, 4])]}, 3)", "visible": True},
    {"name": "better model", "call": "evaluate_models(TR1, TE1, {'good': [np.array([3.0, 3, 4])]}, 3)", "visible": True},
    {"name": "two series: 2x better and 2x worse", "call": "evaluate_models([np.array([0.0,1,1,2,2,3])] * 2, [np.array([2.5, 3.5])] * 2, {'m': [np.array([2.25, 3.25]), np.array([3.5, 2.5])]}, 2)", "visible": True},
    {"name": "series too short is skipped", "call": "evaluate_models([np.array([1.0, 2]), np.array([1.0,2,3,2,3,4])], [np.array([1.0]), np.array([3.0,3,5])], {'m': [np.array([5.0]), np.array([3.0,3,4])]}, 3)"},
    {"name": "flat history is skipped", "call": "evaluate_models([np.ones(8)], [np.ones(2)], {'m': [np.ones(2)]}, 2)"},
    {"name": "horizon longer than season", "call": "evaluate_models([np.array([1.0,2,1,2,1,3])], [np.array([1.0,2,1,2,1])], {'m': [np.array([1.0,2,1,2,2])]}, 2)"},
    {"name": "perfect forecast is clipped", "call": "evaluate_models(TR1, TE1, {'perfect': TE1}, 3)"},
    {"name": "40 random seasonal series", "call": "evaluate_models(TRB, TEB, {'drift_snaive': F_A, 'mean': F_B}, 12)"},
]
