"""TimeSeries Path judge.

The same file runs locally (CPython, for build-time validation) and in the browser (Pyodide worker).
Entry point: run_job(job) -> dict, and run_job_json(json_str) -> json_str for the worker.

job = {"code": learner source, "reference": reference source, "tests": tests.py source,
       "mode": "run" | "submit"}
"""
import io
import json
import math
import sqlite3
import sys
import time
import traceback
import contextlib

import numpy as np
import pandas as pd

MAX_REPR = 1500


def sql(query, **tables):
    """Run a SQL query on in-memory sqlite tables (DataFrames) and return a DataFrame."""
    con = sqlite3.connect(":memory:")
    try:
        for name, df in tables.items():
            df.to_sql(name, con, index=False)
        return pd.read_sql_query(query, con)
    finally:
        con.close()


HELPERS = {"np": np, "pd": pd, "math": math, "sql": sql}


def short(x):
    try:
        if isinstance(x, pd.DataFrame):
            s = x.to_string(max_rows=20, max_cols=12)
        elif isinstance(x, pd.Series):
            s = x.to_string(max_rows=20)
            if x.name is not None:
                s += "\nName: " + str(x.name)
        elif isinstance(x, np.ndarray):
            with np.printoptions(precision=6, threshold=60, suppress=True):
                s = "array(" + np.array2string(x, separator=", ") + ")"
        elif isinstance(x, float):
            s = repr(round(x, 8))
        else:
            s = repr(x)
    except Exception:  # noqa
        s = object.__repr__(x)
    return s if len(s) <= MAX_REPR else s[:MAX_REPR] + " …"


def _num(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and not isinstance(x, (bool, np.bool_))


def default_compare(got, exp, tol=1e-6, check_index=True):
    """Return (ok, message)."""
    if exp is None:
        return (got is None, "" if got is None else "expected None")
    if isinstance(exp, pd.DataFrame):
        if not isinstance(got, pd.DataFrame):
            return False, f"expected a DataFrame, got {type(got).__name__}"
        try:
            g, e = got, exp
            if not check_index:
                g, e = g.reset_index(drop=True), e.reset_index(drop=True)
            pd.testing.assert_frame_equal(g, e, check_dtype=False, check_exact=False, atol=tol, rtol=tol,
                                          check_names=False, check_freq=False, check_index_type=False,
                                          check_column_type=False)
            return True, ""
        except AssertionError as err:
            return False, str(err).strip().split("\n")[0][:300]
    if isinstance(exp, pd.Series):
        if not isinstance(got, pd.Series):
            return False, f"expected a pandas Series, got {type(got).__name__}"
        try:
            g, e = got, exp
            if not check_index:
                g, e = g.reset_index(drop=True), e.reset_index(drop=True)
            pd.testing.assert_series_equal(g, e, check_dtype=False, check_exact=False, atol=tol, rtol=tol,
                                           check_names=False, check_freq=False, check_index_type=False)
            return True, ""
        except AssertionError as err:
            return False, str(err).strip().split("\n")[0][:300]
    if isinstance(exp, np.ndarray):
        try:
            g = np.asarray(got, dtype=exp.dtype if exp.dtype != object else None)
        except Exception:  # noqa
            return False, f"could not convert {type(got).__name__} to an array"
        if g.shape != exp.shape:
            return False, f"shape {g.shape} != expected {exp.shape}"
        if exp.dtype.kind in "fc" or g.dtype.kind in "fc":
            ok = np.allclose(g.astype(float), exp.astype(float), atol=tol, rtol=tol, equal_nan=True)
        else:
            ok = bool(np.array_equal(g, exp))
        return ok, "" if ok else "values differ"
    if _num(exp):
        if not _num(got):
            return False, f"expected a number, got {type(got).__name__}"
        if math.isnan(float(exp)):
            return (math.isnan(float(got)), "expected NaN")
        ok = math.isclose(float(got), float(exp), rel_tol=tol, abs_tol=tol)
        return ok, "" if ok else "number differs"
    if isinstance(exp, (list, tuple)):
        if not isinstance(got, (list, tuple, np.ndarray, pd.Series)):
            return False, f"expected a list, got {type(got).__name__}"
        got = list(got)
        if len(got) != len(exp):
            return False, f"length {len(got)} != expected {len(exp)}"
        for i, (a, b) in enumerate(zip(got, exp)):
            ok, msg = default_compare(a, b, tol, check_index)
            if not ok:
                return False, f"item {i}: {msg}"
        return True, ""
    if isinstance(exp, dict):
        if not isinstance(got, dict):
            return False, f"expected a dict, got {type(got).__name__}"
        if set(got) != set(exp):
            return False, f"keys {sorted(map(str, got))} != expected {sorted(map(str, exp))}"
        for k in exp:
            ok, msg = default_compare(got[k], exp[k], tol, check_index)
            if not ok:
                return False, f"key {k!r}: {msg}"
        return True, ""
    ok = got == exp
    try:
        ok = bool(ok)
    except Exception:  # noqa
        ok = False
    return ok, "" if ok else "value differs"


def _eval_call(call, ns, filename):
    """Evaluate a case. `call` is an expression, or a script whose last line is an expression."""
    import ast
    tree = ast.parse(call, filename, "exec")
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
        exec(compile(tree, filename, "exec"), ns)
        return eval(compile(last, filename, "eval"), ns)
    exec(compile(tree, filename, "exec"), ns)
    return ns.get("result")


def _fmt_user_tb(exc):
    """Traceback limited to frames in the learner's file."""
    tb = traceback.extract_tb(exc.__traceback__)
    lines = [f'  File "{f.filename}", line {f.lineno}, in {f.name}\n    {f.line}' for f in tb
             if f.filename == "solution.py"]
    head = "Traceback (most recent call last):\n" + "\n".join(lines) + "\n" if lines else ""
    return head + f"{type(exc).__name__}: {exc}"


def _load(src, filename):
    ns = {"__name__": "solution" if filename == "solution.py" else "reference"}
    ns.update(HELPERS)
    exec(compile(src, filename, "exec"), ns)
    return {k: v for k, v in ns.items() if not k.startswith("__")}


def run_job(job, emit=None):
    mode = job.get("mode", "run")
    out = {"status": "Accepted", "passed": 0, "total": 0, "results": [], "error": None}
    try:
        user = _load(job["code"], "solution.py")
    except SyntaxError as e:
        out.update(status="Syntax Error", error=f"SyntaxError: {e.msg} (line {e.lineno})\n    {(e.text or '').rstrip()}")
        return out
    except Exception as e:  # noqa
        out.update(status="Runtime Error", error=_fmt_user_tb(e))
        return out
    ref = _load(job["reference"], "reference.py")

    def fresh_tests():
        ns = {"__name__": "tests"}
        ns.update(HELPERS)
        exec(compile(job["tests"], "tests.py", "exec"), ns)
        return ns

    t0 = fresh_tests()
    cases = t0.get("CASES", [])
    if mode == "run":
        cases = [c for c in cases if c.get("visible")]
    out["total"] = len(cases)
    check = t0.get("check")
    for i, case in enumerate(cases):
        res = {"i": i, "name": case.get("name", f"Case {i + 1}"), "call": case["call"],
               "visible": bool(case.get("visible")), "ok": False, "got": None, "expected": None,
               "msg": "", "stdout": "", "error": None, "ms": 0}
        buf = io.StringIO()
        start = time.perf_counter()
        try:
            ns = fresh_tests()
            ns.update(user)
            with contextlib.redirect_stdout(buf):
                got = _eval_call(case["call"], ns, "case")
            res["ms"] = round((time.perf_counter() - start) * 1000, 1)
            if "expected" in case:
                exp = eval(case["expected"], fresh_tests())
            else:
                rns = fresh_tests()
                rns.update(ref)
                with contextlib.redirect_stdout(io.StringIO()):
                    exp = _eval_call(case["call"], rns, "case")
            if check:
                ok, msg = check(got, exp, case)
            else:
                ok, msg = default_compare(got, exp, case.get("tol", 1e-6), case.get("check_index", True))
            res.update(ok=bool(ok), msg=msg or "", got=short(got), expected=short(exp))
        except Exception as e:  # noqa
            res["ms"] = round((time.perf_counter() - start) * 1000, 1)
            res["error"] = _fmt_user_tb(e)
        res["stdout"] = buf.getvalue()[-4000:]
        out["results"].append(res)
        if res["ok"]:
            out["passed"] += 1
        elif out["status"] == "Accepted":
            out["status"] = "Runtime Error" if res["error"] else "Wrong Answer"
        if emit:
            emit(json.dumps(res))
        if not res["ok"] and mode == "submit":
            break  # like LeetCode: stop at the first failing case on submit
    return out


def run_job_json(job_json, emit=None):
    return json.dumps(run_job(json.loads(job_json), emit))


if __name__ == "__main__":
    print(run_job_json(sys.stdin.read()))
