#!/usr/bin/env python3
"""Make a copy of site/ for hosts with a per-file size limit (Claude Artifact publish).

Usage:  python tools/split_engine.py OUT_DIR [--limit-mb 14] [--part-mb 10]

* Copies site/ to OUT_DIR.
* In OUT_DIR/engine, every file larger than --limit-mb (default 14 MB) is cut into parts of at most
  --part-mb (default 10 MB): "<name>.part0", "<name>.part1", ...  The whole file is removed from the copy.
* Writes OUT_DIR/engine/split.json  ({"<name>": ["<name>.part0", ...]}). engine/worker.js reads it and
  joins the parts again in the browser (see setupSplit there).

site/ itself is never changed: normal static hosts keep using the unsplit files.
"""
import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--limit-mb", type=float, default=14.0, help="split engine files larger than this")
    ap.add_argument("--part-mb", type=float, default=10.0, help="maximum size of one part")
    a = ap.parse_args()
    out = os.path.abspath(a.out_dir)
    if out == SITE or out.startswith(SITE + os.sep) or SITE.startswith(out + os.sep):
        sys.exit("OUT_DIR must be outside site/ (and must not contain it).")
    limit = int(a.limit_mb * 1024 * 1024)
    part = int(a.part_mb * 1024 * 1024)

    os.makedirs(out, exist_ok=True)
    # Refresh only the engine folder of an earlier run, so stale parts never linger.
    shutil.rmtree(os.path.join(out, "engine"), ignore_errors=True)
    shutil.copytree(SITE, out, dirs_exist_ok=True)

    eng = os.path.join(out, "engine")
    manifest = {}
    for name in sorted(os.listdir(eng)):
        path = os.path.join(eng, name)
        if not os.path.isfile(path) or name == "split.json":
            continue
        size = os.path.getsize(path)
        if size <= limit:
            continue
        parts = []
        with open(path, "rb") as f:
            i = 0
            while True:
                chunk = f.read(part)
                if not chunk:
                    break
                pn = "%s.part%d" % (name, i)
                with open(os.path.join(eng, pn), "wb") as g:
                    g.write(chunk)
                parts.append(pn)
                i += 1
        os.remove(path)
        manifest[name] = parts
        print("split %s (%.1f MB) -> %d parts" % (name, size / 1048576, len(parts)))
    with open(os.path.join(eng, "split.json"), "w") as f:
        json.dump(manifest, f, indent=1)

    # Report anything still too big for the 15 MB per-file limit.
    too_big = 0
    total = 0
    for dp, _, files in os.walk(out):
        for fn in files:
            sz = os.path.getsize(os.path.join(dp, fn))
            total += sz
            if sz > 15 * 1024 * 1024:
                too_big += 1
                print("WARNING: %s is %.1f MB (over 15 MB)" % (os.path.relpath(os.path.join(dp, fn), out), sz / 1048576))
    print("wrote %s (%.1f MB total, %d split file%s)" % (out, total / 1048576, len(manifest), "" if len(manifest) == 1 else "s"))
    sys.exit(1 if too_big else 0)


if __name__ == "__main__":
    main()
