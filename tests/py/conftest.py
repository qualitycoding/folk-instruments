# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Shared helpers for the audio tests. The tests drive the product only through the folk-render command line
(plan/DECISIONS.md, D-092); its path comes from the environment variable FOLK_RENDER. A missing variable is a failure,
never a skip (Rule 14)."""
import hashlib
import os
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import metrics as m  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"


def render_path():
    p = os.environ.get("FOLK_RENDER")
    assert p, "FOLK_RENDER is not set: it must hold the path of the folk-render executable"
    assert pathlib.Path(p).is_file(), f"FOLK_RENDER points to a missing file: {p}"
    return p


def run_tool(args, timeout=600):
    """Runs folk-render with the given arguments; returns the CompletedProcess (text mode)."""
    return subprocess.run([render_path(), *[str(a) for a in args]], capture_output=True, text=True, timeout=timeout)


class Renderer:
    def __init__(self, tmp):
        self.tmp = tmp

    def __call__(self, instrument, events, sets=None, sr=48000, block=256):
        """events: list of event-file lines without the final 'end'; the last line must be '<time> end'.
        Returns (mono samples, sample rate). Asserts that the tool succeeded and wrote a sane file."""
        sets = sets or {}
        text = "\n".join(events) + "\n"
        assert events[-1].split()[1] == "end", "the event list must finish with an end line"
        key = hashlib.sha256(repr((instrument, text, sorted(sets.items()), sr, block)).encode()).hexdigest()[:16]
        ev, wav = self.tmp / f"{key}.events", self.tmp / f"{key}.wav"
        if not wav.exists():
            ev.write_text(text, encoding="utf-8")
            args = ["--instrument", instrument, "--events", ev, "--out", wav, "--sr", sr, "--block", block]
            for k, v in sets.items():
                args += ["--set", f"{k}={v}"]
            r = run_tool(args)
            assert r.returncode == 0, f"folk-render failed with status {r.returncode}: {r.stderr.strip()}"
            assert wav.exists() and wav.stat().st_size > 1000, "folk-render reported success but wrote no usable file"
        x, got_sr = m.load_mono(wav)
        assert got_sr == sr
        end_t = float(events[-1].split()[0])
        assert abs(len(x) - round(end_t * sr)) <= 1, "the rendered length does not match the end time"
        return x, sr


@pytest.fixture(scope="session")
def render(tmp_path_factory):
    return Renderer(tmp_path_factory.mktemp("renders"))


def note(midi, vel=0.6, dur=2.0, tail=0.5, start=0.0):
    """Event lines for one held note followed by a tail."""
    return [f"{start} on {midi} {vel}", f"{start + dur} off {midi}", f"{start + dur + tail} end"]


def hz(midi, a4=440.0):
    return a4 * 2.0 ** ((midi - 69) / 12.0)


def pitch_cents(x, sr, midi, t0=0.6, t1=1.6, a4=440.0, search=80.0):
    """Deviation in cents of the fundamental from the equal-tempered pitch of the MIDI note."""
    f, _ = m.peak_near(m.seg(x, sr, t0, t1), sr, hz(midi, a4), search)
    return m.cents(f, hz(midi, a4))


def level_at(x, sr, f, t0, t1, search=40.0):
    """Level (dB) of the spectral peak near f in the segment."""
    return m.peak_near(m.seg(x, sr, t0, t1), sr, f, search)[1]
