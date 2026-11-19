#!/usr/bin/env python3
"""Fail-closed check before reference-derived material is published (HANDOFF.md, Rule 15; plan/DECISIONS.md, D-052; test T-210).

  evidence_guard.py --index <index.csv> --evidence <directory>

The directory must hold MANIFEST.json: {"files": [{"path": ..., "derived_from": [reference ids]}]}. Exits 0 only if every other file in
the directory is listed, every entry has a derived_from list, and every reference named has redistributable == 'true' in the index
(a missing, empty or unknown flag counts as false). Exit status 1 on any violation, 2 on a usage error."""
import argparse, csv, json, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--evidence", required=True)
    a = ap.parse_args()
    ev = Path(a.evidence)
    problems = []
    try:
        with open(a.index, newline="", encoding="utf-8") as f:
            flags = {row["id"]: row.get("redistributable", "") for row in csv.DictReader(f)}
    except (OSError, KeyError, csv.Error) as e:
        print(f"evidence_guard: cannot read the index: {e}", file=sys.stderr)
        return 1
    manifest = ev / "MANIFEST.json"
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8"))["files"]
        listed = {}
        for e in entries:
            listed[e["path"]] = e["derived_from"]
            if not isinstance(e["derived_from"], list):
                raise TypeError("derived_from must be a list")
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"evidence_guard: MANIFEST.json missing or malformed: {e!r}", file=sys.stderr)
        return 1
    present = {p.relative_to(ev).as_posix() for p in ev.rglob("*") if p.is_file() and p.name != "MANIFEST.json" or (p.is_symlink())}
    present.discard("MANIFEST.json")
    for path in sorted(present - set(listed)):
        problems.append(f"file not listed in MANIFEST.json: {path}")
    for path, refs in listed.items():
        for ref in refs:
            if ref not in flags:
                problems.append(f"{path}: unknown reference {ref}")
            elif flags[ref] != "true":
                problems.append(f"{path}: reference {ref} is not redistributable (flag '{flags[ref]}')")
    for p in problems:
        print(f"evidence_guard: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
