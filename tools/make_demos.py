#!/usr/bin/env python3
"""Writes the demo event files of every instrument into demos/ (plan/PLAN.md, S-340; HANDOFF.md, listening).
Deterministic: running it again rewrites identical files. Demos cover a melody, a fast passage, slow sustained notes,
dynamics, each expressive control, the lowest and highest notes, chords, and one melody per variant."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "demos"
MELODY = [(0, 1, 0), (1, 1, 2), (2, 1, 4), (3, 1, 7), (4, 2, 9), (6, 1, 7), (7, 1, 4), (8, 1.5, 5), (9.5, 0.5, 4), (10, 1, 2), (11, 1, 0), (12, 1, 2), (13, 1, 4), (14, 2, 0)]
SCALE = [0, 2, 4, 5, 7, 9, 11, 12]
# instrument: (root MIDI note for the melody, lowest note, highest note, chord roots, variant settings for the melody)
INS = {
    "harmonica": (72, 60, 96, [(60, 64, 67), (65, 69, 72), (67, 71, 74)], [{"variant": 0, "key": 0}, {"variant": 0, "key": 7}, {"variant": 1}]),
    "accordion": (69, 41, 100, [(57, 61, 64), (62, 66, 69), (64, 68, 71)], [{"register": r} for r in range(12)] + [{"register": 1, "cassotto": 1}, {"register": 4, "musette_cents": 4}, {"register": 4, "musette_cents": 25}]),
    "melodion": (65, 53, 89, [(60, 64, 67), (65, 69, 72), (67, 71, 74)], [{"range": 1, "body": 0}, {"range": 1, "body": 1}, {"range": 1, "body": 2}, {"range": 1, "breath_mode": 1}]),
    "mandolin": (69, 55, 96, [(55, 62, 71, 79), (60, 64, 72, 79), (55, 62, 74, 78)], [{"body": 0}, {"body": 1}, {"body": 2}]),
    "bouzouki": (62, 50, 86, [(50, 57, 62), (55, 59, 62), (53, 57, 64)], [{"variant": 0}, {"variant": 1}, {"variant": 2}]),
}
PLUCKED = ("mandolin", "bouzouki")


def write(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def seq(notes, bpm, vel=0.7, gap=0.92, t0=0.0, sets=None, pre=None):
    """notes: (start beat, length in beats, MIDI note) -> event lines sorted by time, ending 1.5 s after the last note."""
    spb = 60.0 / bpm
    ev = [(0.0, 0, f"set {k} {v}") for k, v in (sets or {}).items()] + [(t, 0, e) for t, e in (pre or [])]
    for (b, d, n) in notes:
        ev.append((t0 + b * spb, 2, f"on {n} {vel}"))
        ev.append((t0 + (b + d * gap) * spb, 1, f"off {n}"))
    ev.sort(key=lambda e: (round(e[0], 6), e[1]))
    end = max(t for t, _, _ in ev) + 1.5
    return [f"{t:.4f} {e}" for t, _, e in ev] + [f"{end:.4f} end"]


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.events"):
        old.unlink()
    for ins, (root, lo, hi, chords, variants) in INS.items():
        mel = [(b, d, root + s) for (b, d, s) in MELODY]
        write(f"{ins}-01-melody.events", seq(mel, 96))
        run = [root - 12 + 12 * o + s for o in (0, 1) for s in SCALE[:-1]] + [root + 12]
        fast = [(i * 0.25, 0.25, n) for i, n in enumerate(run + run[::-1][1:])]
        write(f"{ins}-02-fast.events", seq(fast, 132, vel=0.8))
        write(f"{ins}-03-slow.events", seq([(0, 6, root), (6, 6, root + 7), (12, 6, root - 5), (18, 8, root)], 90, vel=0.55, gap=0.97))
        dyn, t = [], 0.0
        for v in (0.2, 0.35, 0.5, 0.65, 0.8, 1.0):
            dyn += [f"{t:.4f} on {root} {v}", f"{t + 1.3:.4f} off {root}"]
            t += 1.8
        write(f"{ins}-04-dynamics.events", dyn + [f"{t + 1.0:.4f} end"])
        low = [(i, 1, lo + i) for i in range(5)]
        high = [(6 + i, 1, hi - 4 + i) for i in range(5)]
        write(f"{ins}-05-extremes.events", seq(low + high, 80))
        ch, t = [], 0.0
        for c in chords + [chords[0]]:
            for k, n in enumerate(c):
                ch.append((t + (0.015 * k if ins in PLUCKED else 0.0), 2, f"on {n} 0.7"))
                ch.append((t + 1.6, 1, f"off {n}"))
            t += 2.0
        ch.sort(key=lambda e: (round(e[0], 6), e[1]))
        write(f"{ins}-06-chords.events", [f"{a:.4f} {e}" for a, _, e in ch] + [f"{t + 1.5:.4f} end"])
        if ins == "melodion":  # chords under a flow-limited breath (D-041; gate G-L4)
            write("melodion-11-chords-limited-breath.events", ["0.0000 set range 1", "0.0000 set breath_mode 1"] + [f"{a:.4f} {e}" for a, _, e in ch] + [f"{t + 1.5:.4f} end"])
        if ins in PLUCKED:
            trem = seq([(0, 4, root), (4, 4, root + 4), (8, 4, root + 7), (12, 6, root + 12)], 90, vel=0.75, gap=0.98, pre=[(0.0, "cc 1 1.0")])
            write(f"{ins}-07-tremolo.events", trem)
            bend = ["0.0000 on %d 0.8" % root] + [f"{0.5 + 0.05 * i:.4f} bend {i / 10:.1f}" for i in range(11)] + [f"{1.5 + 0.05 * i:.4f} bend {1 - i / 10:.1f}" for i in range(11)] + [f"2.6000 off {root}", "4.0000 end"]
            write(f"{ins}-08-bend.events", bend)
            write(f"{ins}-09-pick-positions.events", [l for pos in (0.05, 0.12, 0.25, 0.4) for l in []] + seq([(4 * i + b, d, root + s) for i in range(1) for (b, d, s) in MELODY[:5]], 96, sets={"pick_position": 0.05}))
        else:
            vib = ["0.0000 on %d 0.7" % root] + [f"{1.0 + 0.1 * i:.4f} cc 1 {i / 10:.1f}" for i in range(11)] + [f"4.5000 off {root}", "5.5000 end"]
            write(f"{ins}-07-vibrato.events", vib)
            notes = {"harmonica": (71, 3), "accordion": (69, 1), "melodion": (69, 0)}[ins]
            if ins != "melodion":  # the melodion ignores the pitch wheel (D-093)
              bend = [f"0.0000 on {notes[0]} 0.7"] + [f"{0.8 + 0.06 * i:.4f} bend {-i / 10:.1f}" for i in range(11)] + [f"{2.2 + 0.06 * i:.4f} bend {-(1 - i / 10):.1f}" for i in range(11)] + [f"3.4000 off {notes[0]}", "4.4000 end"]
              write(f"{ins}-08-bend.events", bend)
            swell = ["0.0000 set breath_source 1", "0.0000 cc 2 0.0", f"0.0000 on {root} 1.0"] + [f"{0.2 + 0.1 * i:.4f} cc 2 {min(1.0, i / 20):.2f}" for i in range(21)] + [f"{2.4 + 0.1 * i:.4f} cc 2 {max(0.0, 1 - i / 20):.2f}" for i in range(21)] + [f"4.6000 off {root}", "5.2000 end"]
            write(f"{ins}-09-breath-swell.events", swell)
        if ins == "harmonica":
            chrom = [(i * 0.5, 0.5, n) for i, n in enumerate(range(60, 85))]
            write("harmonica-10-chromatic-on-diatonic.events", seq(chrom, 100))
        for k, sets in enumerate(variants, 1):
            write(f"{ins}-2{k:02d}-variant.events", seq(mel, 96, sets=sets))
    print(len(list(OUT.glob("*.events"))), "demo event files written to", OUT)


if __name__ == "__main__":
    main()
