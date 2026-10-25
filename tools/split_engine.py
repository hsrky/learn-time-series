#!/usr/bin/env python3
"""Make a copy of site/ for hosts with a per-file size limit (Claude Artifact publish).

Usage:  python tools/split_engine.py OUT_DIR [--limit-mb 14] [--part-mb 10]

* Copies site/ to OUT_DIR.
* In OUT_DIR/engine, every file larger than --limit-mb (default 14 MB) is cut into parts of at most
  --part-mb (default 10 MB): "<name>.part0", "<name>.part1", ...  The whole file is removed from the copy.
* Archives (.whl, .zip) are not a served type on Claude Artifacts, so every archive is written as
  base64 text parts "<name>.b64-0.txt", "<name>.b64-1.txt", ... (each part decodes on its own).
* Writes OUT_DIR/engine/split.json  ({"<name>": ["<name>.part0", ...]} for binary parts,
  {"<name>": {"b64": ["<name>.b64-0.txt", ...]}} for base64 parts). engine/worker.js reads it and
  rebuilds the files in the browser (see setupSplit there).

site/ itself is never changed: normal static hosts keep using the unsplit files.
"""
import argparse
import base64
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def prepare_artifact_page(out):
    """The Artifact publisher adds its own <!doctype>/<head>/<body> skeleton: keep only what goes inside."""
    import re
    p = os.path.join(out, "index.html")
    with open(p, encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r"(?is)<!doctype html>\s*<html[^>]*>\s*<head>", "", s)
    s = re.sub(r'(?i)<meta charset="utf-8">\s*', "", s)
    s = re.sub(r'(?i)<meta name="viewport"[^>]*>\s*', "", s)
    s = re.sub(r"(?i)</head>\s*<body>", "", s)
    s = re.sub(r"(?i)</body>\s*</html>\s*$", "", s)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    mock = os.path.join(out, "js", "ai-mock.js")
    if os.path.exists(mock):
        os.remove(mock)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--limit-mb", type=float, default=14.0, help="split engine files larger than this")
    ap.add_argument("--part-mb", type=float, default=10.0, help="maximum size of one part")
    ap.add_argument("--artifact", action="store_true",
                    help="also prepare index.html for the Claude Artifact publish (body-only page) and drop the AI test shim")
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
        if name.endswith((".whl", ".zip")):
            raw = part - part % 3                      # multiple of 3: each base64 part decodes alone
            parts = []
            with open(path, "rb") as f:
                i = 0
                while True:
                    chunk = f.read(raw)
                    if not chunk:
                        break
                    pn = "%s.b64-%d.txt" % (name, i)
                    with open(os.path.join(eng, pn), "wb") as g:
                        g.write(base64.b64encode(chunk))
                    parts.append(pn)
                    i += 1
            os.remove(path)
            manifest[name] = {"b64": parts}
            print("base64 %s (%.1f MB) -> %d part(s)" % (name, size / 1048576, len(parts)))
            continue
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

    if a.artifact:
        prepare_artifact_page(out)

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
