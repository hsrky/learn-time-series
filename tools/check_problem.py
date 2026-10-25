"""Validate coding problems: the reference passes every case, the starter fails at least one.

Usage: python tools/check_problem.py <problem dir | lesson dir | stage dir | content dir> [...]
Exit code 1 if any problem is broken.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

REQUIRED = ["problem.md", "starter.py", "solution.py", "tests.py"]


def find_problems(path):
    if all(os.path.exists(os.path.join(path, f)) for f in REQUIRED):
        yield path
        return
    for root, dirs, files in os.walk(path):
        dirs.sort()
        if "problem.md" in files:
            yield root


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def check(pdir):
    errs = []
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(pdir, f))]
    if missing:
        return [f"missing files: {missing}"]
    tests, ref, starter = (read(os.path.join(pdir, f)) for f in ("tests.py", "solution.py", "starter.py"))
    job = {"code": ref, "reference": ref, "tests": tests, "mode": "submit"}
    try:
        r = harness.run_job(job)
    except Exception as e:  # noqa
        return [f"harness crashed: {e!r}"]
    if r["status"] != "Accepted" or r["passed"] != r["total"]:
        bad = next((x for x in r["results"] if not x["ok"]), None)
        errs.append(f"reference fails: {r['status']} {r.get('error') or ''} {json.dumps(bad)[:600] if bad else ''}")
    if r["total"] < 4:
        errs.append(f"only {r['total']} cases (need >= 4)")
    vis = harness.run_job({**job, "mode": "run"})
    if not (2 <= vis["total"] <= 3):
        errs.append(f"{vis['total']} visible cases (need 2-3)")
    s = harness.run_job({"code": starter, "reference": ref, "tests": tests, "mode": "submit"})
    if s["status"] == "Accepted":
        errs.append("starter passes all cases (it must fail)")
    return errs


def main(paths):
    bad = 0
    n = 0
    for path in paths:
        for pdir in find_problems(path):
            n += 1
            errs = check(pdir)
            if errs:
                bad += 1
                print(f"FAIL {pdir}")
                for e in errs:
                    print("   -", e)
            else:
                print(f"ok   {pdir}")
    print(f"\n{n - bad}/{n} problems ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["content"]))
