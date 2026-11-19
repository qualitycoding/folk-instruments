#!/usr/bin/env python3
"""Reed check across the range (plan/PLAN.md S-201, rule DR-03). Runs reed_probe at the 12 check pitches and both host rates.

  reed_check.py [--instrument <name>] [--calibrated] [--probe <path>] --out <file.csv>

Without --calibrated: 50, 100, 400, 1500, 1800 Pa with the targets of DR-03 (silent at 50 Pa; offsets within 1.5 cents of -20.1,
-23.1, -23.3 at 100, 400, 1500 Pa; sounding and finite at 1800 Pa). With --calibrated: 28, 156, 400, 1500, 1800 Pa, checking only
silent / sounding / finite. Exits non-zero on any failing row."""
import argparse, csv, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

PITCHES = [28, 36, 45, 52, 60, 69, 76, 84, 93, 100, 108, 112]
RATES = [44100, 48000]
TARGET = {100: -20.1, 400: -23.1, 1500: -23.3}


def probe_row(args):
    probe, ins, midi, rate, p = args
    hz = 440.0 * 2 ** ((midi - 69) / 12)
    cmd = [probe, "--freq", repr(hz), "--pressure", str(p), "--rate", str(rate)]
    if ins:
        cmd += ["--instrument", ins]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return dict(midi=midi, rate=rate, pressure=p, state="error", cents="", amp_over_x0="", source_rms="")
    j = json.loads(r.stdout.splitlines()[0])
    return dict(midi=midi, rate=rate, pressure=p, state=j["state"], cents=j["cents"], amp_over_x0=j["amp_over_x0"], source_rms=j["source_rms"])


def verdict(row, calibrated):
    p, st = row["pressure"], row["state"]
    if st in ("error", "diverged"):
        return False
    if p in (50, 28):
        return st == "silent"
    if calibrated or p == 1800:
        return st == "sounds"
    return st == "sounds" and abs(row["cents"] - TARGET[p]) <= 1.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instrument")
    ap.add_argument("--calibrated", action="store_true")
    ap.add_argument("--probe", default=os.path.expanduser("~/folk-build/reed_probe"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pressures = [28, 156, 400, 1500, 1800] if a.calibrated else [50, 100, 400, 1500, 1800]
    jobs = [(a.probe, a.instrument, m, r, p) for m in PITCHES for r in RATES for p in pressures]
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        rows = list(ex.map(probe_row, jobs))
    bad = 0
    for row in rows:
        row["ok"] = verdict(row, a.calibrated)
        bad += not row["ok"]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["midi", "rate", "pressure", "state", "cents", "amp_over_x0", "source_rms", "ok"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows, {bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
