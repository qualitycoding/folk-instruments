#!/usr/bin/env python3
"""Per-instrument output gain G_out (plan/DECISIONS.md D-013, procedure GAIN of plan/PLAN.md).

  calibrate_gains.py --instrument <name> --render <folk-render> [--check]

Renders the default note of D-013 (velocity 0.8, 2 s) at level=0.007 (where tanh is linear to better than 0.01 %), multiplies the
peak by 100 and compares it with -12 dBFS. Without --check it writes G_out * target / measured to presets/gains.json (1 if absent);
with --check it only exits 0 when the measured peak is within 0.1 dB of the target."""
import argparse, json, math, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
GAINS = ROOT / "presets" / "gains.json"
NOTE = {"harmonica": 72, "accordion": 69, "melodion": 69, "mandolin": 69, "bouzouki": 62}
TARGET_DB = -12.0


def measure(instrument, render):
    n = NOTE[instrument]
    with tempfile.TemporaryDirectory() as d:
        ev, wav = Path(d) / "a.events", Path(d) / "a.wav"
        ev.write_text(f"0 on {n} 0.8\n2.0 off {n}\n2.5 end\n")
        r = subprocess.run([render, "--instrument", instrument, "--events", str(ev), "--out", str(wav), "--set", "level=0.007"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"calibrate_gains: folk-render failed with status {r.returncode}: {r.stderr.strip()}")
        x, _ = sf.read(str(wav), dtype="float64")
    return float(np.max(np.abs(x))) * 100.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instrument", required=True, choices=sorted(NOTE))
    ap.add_argument("--render", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    gains = json.loads(GAINS.read_text()) if GAINS.exists() else {}
    current = float(gains.get(a.instrument, 1.0))
    peak = measure(a.instrument, a.render)
    if not math.isfinite(peak) or peak <= 0:
        sys.exit(f"calibrate_gains: {a.instrument} produced no sound (peak {peak})")
    target = 10 ** (TARGET_DB / 20)
    db = 20 * math.log10(peak)
    print(f"{a.instrument}: peak {db:.3f} dBFS (G_out {current:.6g})")
    if a.check:
        sys.exit(0 if abs(db - TARGET_DB) <= 0.1 else 1)
    gains[a.instrument] = current * target / peak
    GAINS.parent.mkdir(exist_ok=True)
    GAINS.write_text(json.dumps(gains, indent=1) + "\n")
    print(f"{a.instrument}: G_out -> {gains[a.instrument]:.9g}")


if __name__ == "__main__":
    main()
