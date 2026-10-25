BUILD = {"name": "build", "fixed": 20000, "per_1k": 0.02, "latency_ms": 50}
API = {"name": "api", "fixed": 0, "per_1k": 1.00, "latency_ms": 400}
FM = {"name": "fm-gpu", "fixed": 6000, "per_1k": 0.30, "latency_ms": 200}
OPTS = [BUILD, API, FM]

CASES = [
    {"name": "api wins at 10M", "call": "choose_option([BUILD, API], 10_000_000, 1000)",
     "expected": "{'best': 'api', 'cost': 10000.0, 'ranking': ['api', 'build']}", "visible": True},
    {"name": "break-even", "call": "breakeven_volume(BUILD, API)", "expected": "20000*1000/0.98", "visible": True},
    {"name": "latency limit removes api", "call": "choose_option(OPTS, 10_000_000, 250)",
     "expected": "{'best': 'fm-gpu', 'cost': 9000.0, 'ranking': ['fm-gpu', 'build']}"},
    {"name": "build wins at high volume", "call": "choose_option(OPTS, 100_000_000, 1000)",
     "expected": "{'best': 'build', 'cost': 22000.0, 'ranking': ['build', 'fm-gpu', 'api']}"},
    {"name": "nothing feasible", "call": "choose_option(OPTS, 1000, 10)", "expected": "{'best': None, 'cost': None, 'ranking': []}"},
    {"name": "tie goes to the alphabetical name", "call": "choose_option([{'name': 'b', 'fixed': 10, 'per_1k': 0, 'latency_ms': 1}, {'name': 'a', 'fixed': 10, 'per_1k': 0, 'latency_ms': 1}], 5, 5)",
     "expected": "{'best': 'a', 'cost': 10.0, 'ranking': ['a', 'b']}"},
    {"name": "parallel lines", "call": "breakeven_volume(API, {'name': 'x', 'fixed': 5, 'per_1k': 1.0, 'latency_ms': 1})", "expected": "None"},
    {"name": "cross at negative volume", "call": "breakeven_volume(BUILD, {'name': 'x', 'fixed': 10000, 'per_1k': 0.01, 'latency_ms': 1})", "expected": "None"},
    {"name": "empty options", "call": "choose_option([], 100, 100)", "expected": "{'best': None, 'cost': None, 'ranking': []}"},
]
