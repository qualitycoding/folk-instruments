# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Behaviour every instrument shares: sample-rate independence, levels, tuning reference, determinism and the command
line of folk-render (SC-11; D-090 to D-093; threat model: event files are untrusted input)."""
import pathlib
import subprocess

import numpy as np
import pytest
import soundfile as sf
from conftest import FIXTURES, hz, m, note, pitch_cents, render_path, run_tool

ALL = ["harmonica", "accordion", "melodion", "mandolin", "bouzouki"]
NOTE = {"harmonica": 72, "accordion": 69, "melodion": 69, "mandolin": 69, "bouzouki": 62}
WINDOW = {"harmonica": (0.6, 1.4), "accordion": (0.6, 1.4), "melodion": (0.6, 1.4), "mandolin": (0.05, 0.6), "bouzouki": (0.05, 0.6)}
SETS = {"mandolin": {"pair_detune_cents": 0}, "bouzouki": {"pair_detune_cents": 0}}


@pytest.mark.parametrize("ins", ALL)
def test_T160_sample_rate_independence(render, ins):
    """T-160. At 44.1, 48 and 96 kHz the same note has the same pitch (within 4 cents of each other), level (within
    1.5 dB) and spectral centroid below 15 kHz (within 10 %)."""
    res = []
    for sr in (44100, 48000, 96000):
        x, _ = render(ins, note(NOTE[ins], 0.7, 1.5), SETS.get(ins, {}), sr=sr)
        s = m.seg(x, sr, *WINDOW[ins])
        mag = np.abs(np.fft.rfft(s * np.hanning(len(s))))
        f = np.fft.rfftfreq(len(s), 1 / sr)
        sel = (f >= 20) & (f <= 15000)
        res.append((pitch_cents(x, sr, NOTE[ins], *WINDOW[ins]), m.rms_db(s), float(np.sum(f[sel] * mag[sel] ** 2) / np.sum(mag[sel] ** 2))))
    p, l, c = zip(*res)
    assert max(p) - min(p) <= 4.0, p
    assert max(l) - min(l) <= 1.5, l
    assert max(c) / min(c) <= 1.10, c


@pytest.mark.parametrize("ins", ALL)
def test_T160_block_size_does_not_change_the_file(render, ins):
    """T-160. Rendering in blocks of 32 and of 1024 samples gives the same samples within 1e-5."""
    a, sr = render(ins, note(NOTE[ins], 0.7, 1.0), block=32)
    b, _ = render(ins, note(NOTE[ins], 0.7, 1.0), block=1024)
    assert np.max(np.abs(a - b)) <= 1e-5


@pytest.mark.parametrize("ins", ALL)
def test_T162_level_and_tuning_reference(render, ins):
    """T-162. A default note at velocity 0.8 peaks between -30 and -1 dBFS; a4_hz = 442 raises the pitch by 7.85 cents."""
    x, sr = render(ins, note(NOTE[ins], 0.8, 1.5), SETS.get(ins, {}))
    assert -30.0 <= m.peak_db(x) <= -1.0
    y, _ = render(ins, note(NOTE[ins], 0.8, 1.5), {**SETS.get(ins, {}), "a4_hz": 442})
    delta = pitch_cents(y, sr, NOTE[ins], *WINDOW[ins]) - pitch_cents(x, sr, NOTE[ins], *WINDOW[ins])
    assert abs(delta - 7.85) <= 1.5
    half = float(np.max(np.abs(render(ins, note(NOTE[ins], 0.8, 1.5), {**SETS.get(ins, {}), "level": 0.35})[0])))
    assert half < float(np.max(np.abs(x)))


@pytest.mark.parametrize("ins", ALL)
def test_T163_two_runs_write_identical_files(tmp_path, ins):
    """T-163. The renderer is deterministic: two runs of the same job produce byte-identical files."""
    ev = tmp_path / "a.events"
    ev.write_text("\n".join(note(NOTE[ins], 0.7, 0.5)) + "\n")
    outs = []
    for k in (1, 2):
        out = tmp_path / f"{k}.wav"
        r = run_tool(["--instrument", ins, "--events", ev, "--out", out])
        assert r.returncode == 0, r.stderr
        outs.append(out.read_bytes())
    assert outs[0] == outs[1] and len(outs[0]) > 1000


def test_T161_output_format(tmp_path):
    """T-161. The output is a stereo 32-bit float WAV at the requested rate."""
    ev = tmp_path / "a.events"
    ev.write_text("0 on 69 0.7\n0.4 off 69\n0.5 end\n")
    out = tmp_path / "a.wav"
    r = run_tool(["--instrument", "accordion", "--events", ev, "--out", out, "--sr", 44100])
    assert r.returncode == 0, r.stderr
    info = sf.info(str(out))
    assert (info.samplerate, info.channels, info.subtype, info.frames) == (44100, 2, "FLOAT", 22050)


@pytest.mark.parametrize("ins", ALL)
def test_T161_list_params(ins):
    """T-161. --list-params prints one line per parameter: id, min, max, default, steps, separated by tabs."""
    r = run_tool(["--instrument", ins, "--list-params"])
    assert r.returncode == 0, r.stderr
    rows = [line.split("\t") for line in r.stdout.strip().splitlines()]
    assert len(rows) >= 11 and all(len(row) == 5 for row in rows)
    ids = [row[0] for row in rows]
    assert ids[0] == "level" and ids[1] == "a4_hz" and len(set(ids)) == len(ids)
    for row in rows:
        lo, hi, de = float(row[1]), float(row[2]), float(row[3])
        assert lo <= de <= hi and int(row[4]) >= 0


@pytest.mark.parametrize("fixture,needle", [("bad_kind.events", "line 2"), ("bad_time_order.events", "line 3"), ("missing_end.events", "end"),
                                           ("bad_number.events", "line 1"), ("negative_time.events", "line 1"), ("garbage.bin", "line"),
                                           ("huge_line.events", "line 1")])
def test_T161_malformed_event_files_are_refused(tmp_path, fixture, needle):
    """T-161. A malformed event file ends the run with status 3, a message naming the problem, and no output file."""
    out = tmp_path / "x.wav"
    r = run_tool(["--instrument", "mandolin", "--events", FIXTURES / fixture, "--out", out])
    assert r.returncode == 3, (r.returncode, r.stderr)
    assert needle in r.stderr.lower()
    assert not out.exists()


def test_T161_usage_errors(tmp_path):
    """T-161. Unknown instruments, parameters and options, and out-of-range sample rates, end with status 2; an output
    path that cannot be written ends with status 4; a missing event file ends with status 4."""
    ev = tmp_path / "a.events"
    ev.write_text("0 on 69 0.7\n0.4 off 69\n0.5 end\n")
    out = tmp_path / "a.wav"
    assert run_tool(["--instrument", "kazoo", "--events", ev, "--out", out]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", out, "--set", "no_such=1"]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", out, "--set", "level=abc"]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", out, "--frobnicate"]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", out, "--sr", 8000]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", out, "--block", 0]).returncode == 2
    assert run_tool(["--instrument", "mandolin", "--events", ev, "--out", tmp_path / "no_such_dir" / "a.wav"]).returncode == 4
    assert run_tool(["--instrument", "mandolin", "--events", tmp_path / "missing.events", "--out", out]).returncode == 4
    assert not out.exists()


def test_T161_version_and_help():
    r = run_tool(["--version"])
    assert r.returncode == 0 and r.stdout.strip().startswith("folk-render 0.")
    h = run_tool(["--help"])
    assert h.returncode == 0 and "--instrument" in h.stdout and "--events" in h.stdout


def test_T161_event_file_features(render):
    """T-161. Comments, blank lines and 'set' events are accepted; a 'set' event changes the sound from its time on."""
    x, sr = render("accordion", ["# a comment", "", "0 set register 1", "0 on 69 0.7", "1.5 set register 0", "3.0 off 69", "3.2 end"], {"musette_cents": 0})
    early = m.peak_near(m.seg(x, sr, 0.5, 1.4), sr, 440.0, 50.0)[1]
    late_440 = m.peak_near(m.seg(x, sr, 2.0, 2.9), sr, 440.0, 50.0)[1]
    late_880 = m.peak_near(m.seg(x, sr, 2.0, 2.9), sr, 880.0, 50.0)[1]
    assert early > -50.0 and late_880 > -50.0 and late_440 <= late_880 - 40.0
