#!/usr/bin/env python3
"""Tuning calibration of the reeds (plan/DECISIONS.md D-016, step S-201).

  calibrate_reeds.py [--probe <path>] [--out presets/reeds.json]

Runs reed_probe at breath 0.6 (p0 = 1250 * 0.6^1.5 = 581 Pa) for every MIDI note from 28 to 112 and the host rates 44100, 48000,
88200, 96000, and writes the offset 'sounding minus natural' in cents per instrument and rate, the reference source RMS S_ref
(444 Hz, from the run at 48000) and the three curves of D-012 (all 1 until step S-330)."""
import argparse, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RATES = [44100, 48000, 88200, 96000]
MIDI = list(range(28, 113))
INSTRUMENTS = ["harmonica", "accordion", "melodion"]
PRESSURE = 1250.0 * 0.6 ** 1.5


def run(probe, hz, rate):
    r = subprocess.run([probe, "--freq", repr(hz), "--pressure", repr(PRESSURE), "--rate", str(rate)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"calibrate_reeds: reed_probe failed: {r.stderr.strip()}")
    return json.loads(r.stdout.splitlines()[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default=os.path.expanduser("~/folk-build/reed_probe"))
    ap.add_argument("--out", default=str(ROOT / "presets" / "reeds.json"))
    a = ap.parse_args()
    jobs = [(m, r) for r in RATES for m in MIDI]
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        res = list(ex.map(lambda j: run(a.probe, 440.0 * 2 ** ((j[0] - 69) / 12), j[1]), jobs))
    table = {str(r): [] for r in RATES}
    for (m, r), j in zip(jobs, res):
        if j["state"] != "sounds":
            sys.exit(f"calibrate_reeds: MIDI {m} at {r} Hz did not sound at breath 0.6 ({j['state']})")
        table[str(r)].append(round(j["cents"], 3))
    ref = run(a.probe, 444.0, 48000)
    out = {"breath": 0.6, "pressure_pa": PRESSURE, "midi_first": 28, "source_rms_ref": ref["source_rms"],
           "curves": {n: {"q": [[28, 1.0], [112, 1.0]], "x0": [[28, 1.0], [112, 1.0]], "hmin": [[28, 1.0], [112, 1.0]]} for n in INSTRUMENTS},
           "offsets": {n: table for n in INSTRUMENTS}}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    lo = min(min(v) for v in table.values()); hi = max(max(v) for v in table.values())
    print(f"offsets {lo:.2f} .. {hi:.2f} cents; source_rms_ref {ref['source_rms']:.6g}")


if __name__ == "__main__":
    main()
