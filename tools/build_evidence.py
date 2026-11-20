#!/usr/bin/env python3
"""Builds the evidence bundle of one listening gate (plan/PLAN.md S-210 gate actions, S-340; HANDOFF.md "Delivering audio").

  build_evidence.py --gate <id> --instrument <name> --seed <n> --out <dir> --render <folk-render>
                    [--ref-root <dir>] [--private-out <dir>] [--index references/index.csv]

First version: renders the instrument's demos (demos/<instrument>-*.events) to <out>/demos/*.wav, writes MANIFEST.json, SHA256SUMS and
ATTRIBUTION.md, and runs tools/evidence_guard.py. Blind pairs, metrics and the key balance check come with S-340; until then a gate that
needs pairs (G-L1 to G-L5) builds demos only and says so."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--render", required=True)
    ap.add_argument("--ref-root")
    ap.add_argument("--private-out")
    ap.add_argument("--index", default=str(ROOT / "references" / "index.csv"))
    a = ap.parse_args()
    out = Path(a.out)
    (out / "demos").mkdir(parents=True, exist_ok=True)
    events = sorted((ROOT / "demos").glob(f"{a.instrument}-*.events"))
    if not events:
        print(f"build_evidence: no demos for {a.instrument}", file=sys.stderr)
        return 2
    files = []
    for ev in events:
        wav = out / "demos" / (ev.stem + ".wav")
        r = subprocess.run([a.render, "--instrument", a.instrument, "--events", str(ev), "--out", str(wav)], capture_output=True, text=True)
        if r.returncode != 0 or not wav.is_file() or wav.stat().st_size < 1000:
            print(f"build_evidence: rendering {ev.name} failed ({r.returncode}): {r.stderr.strip()}", file=sys.stderr)
            return 1
        files.append(f"demos/{wav.name}")
    if not a.gate.startswith("G-P"):
        print("build_evidence: blind pairs are not built yet (S-340); demos only")
    (out / "ATTRIBUTION.md").write_text(
        f"# Attribution\n\nGate {a.gate}, instrument {a.instrument}, seed {a.seed}.\n\nEvery file in `demos/` is rendered by folk-render from "
        "the event files in `demos/` of the repository (AGPL-3.0). No reference recording is used or derived from.\n", encoding="utf-8")
    files.append("ATTRIBUTION.md")
    manifest = {"gate": a.gate, "instrument": a.instrument, "seed": a.seed, "files": [{"path": f, "derived_from": []} for f in files + ["SHA256SUMS"]]}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    sums = "".join(f"{hashlib.sha256((out / f).read_bytes()).hexdigest()}  {f}\n" for f in files + ["MANIFEST.json"])
    (out / "SHA256SUMS").write_text(sums, encoding="utf-8")
    g = subprocess.run([sys.executable, str(ROOT / "tools" / "evidence_guard.py"), "--index", a.index, "--evidence", str(out)])
    if g.returncode != 0:
        return 1
    print(f"evidence for {a.gate}: {len(events)} demos in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
