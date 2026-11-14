#!/usr/bin/env python3
"""Refresh .checkpoints/state.json (sequence, artifact hashes, time). Usage: checkpoint.py <phase> <subphase> [key=value ...]"""
import hashlib, json, pathlib, subprocess, sys, datetime
root = pathlib.Path(__file__).resolve().parent.parent
p = root / ".checkpoints" / "state.json"
s = json.loads(p.read_text())
s["sequence"] += 1
s["phase"], s["subphase"] = sys.argv[1], sys.argv[2]
files = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout.split("\n")
s["artifacts"] = {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in sorted(files)
                  if f and not f.startswith(".checkpoints/") and (root / f).is_file()}
s["updated_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
p.write_text(json.dumps(s, indent=1) + "\n")
print("checkpoint", s["sequence"], s["phase"], s["subphase"], len(s["artifacts"]), "artifacts")
