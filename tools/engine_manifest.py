#!/usr/bin/env python3
"""Write engine/manifest.json: the SHA-256 and size of every engine file.

Usage:  python tools/engine_manifest.py [ENGINE_DIR]        (default: site/engine)

Format: {"version": "<16 hex>", "files": {"<name>": {"sha256": "...", "size": N}}}
"version" is the first 16 hex characters of the SHA-256 over the sorted (name, sha256) list, so it changes
whenever any engine file changes. engine/worker.js uses the manifest to cache the files in Cache Storage
("tsp-engine-<version>") and to check every file before it is used.

Called by tools/build.py (end of the build) and tools/split_engine.py (for the Artifact copy, where the
files that were split are listed under their ORIGINAL name with the original hash, plus the parts).
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def file_info(path):
    """{"sha256", "size"} of one file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"sha256": h.hexdigest(), "size": os.path.getsize(path)}


def write_manifest(engine_dir, originals=None):
    """Write engine_dir/manifest.json. `originals` = {name: file_info} for files that no longer exist
    in engine_dir because they were split into parts (they are listed so the rebuilt file is verified)."""
    files = {}
    for name in sorted(os.listdir(engine_dir)):
        path = os.path.join(engine_dir, name)
        if os.path.isfile(path) and name != "manifest.json":
            files[name] = file_info(path)
    for name, info in (originals or {}).items():
        files[name] = info
    files = {k: files[k] for k in sorted(files)}
    digest = hashlib.sha256(json.dumps([[n, i["sha256"]] for n, i in files.items()], separators=(",", ":")).encode()).hexdigest()
    manifest = {"version": digest[:16], "files": files}
    with open(os.path.join(engine_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
        f.write("\n")
    return manifest


if __name__ == "__main__":
    d = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "site", "engine")
    m = write_manifest(d)
    print("wrote %s/manifest.json: version %s, %d files" % (d, m["version"], len(m["files"])))
