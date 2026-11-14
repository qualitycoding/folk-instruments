# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Comparison with recordings of real instruments (SC-13; C-021, C-049; D-050, D-051). These thresholds are frozen
before any listening and the listening gates never relax them.

T-200 uses the TinySOL accordion notes (CC BY 4.0, redistributable). Its thresholds are the spread between neighbouring
real notes, measured in research/spikes/s07-tinysol-accordion (646 notes): a synthetic note need not match a real note
better than the real note one semitone away does. The test first re-measures part of that spread from the data set
and fails if the data or the metric has drifted from what was frozen.

T-201 applies the same procedure to any other reference set described by references/index.csv (private references
included), with thresholds computed from that set's own neighbour spread at run time.

Environment: FOLK_TINYSOL = directory holding TinySOL_metadata.csv and the extracted Keyboards/Accordion folder;
FOLK_REF_ROOT = directory holding the files named in references/index.csv. Missing variables fail the test (Rule 14)."""
import csv
import hashlib
import os
import pathlib

import numpy as np
import pytest
from conftest import hz, m, note

pytestmark = pytest.mark.reference

REPO = pathlib.Path(__file__).resolve().parents[2]
TINYSOL_METADATA_MD5 = "a86c9bb115f69e61f2f25872e397fc4a"
A4_TINYSOL = 441.6                       # the set's median pitch is +6 cents re 440 Hz (S07)
VELOCITY = {"pp": 0.3, "mf": 0.6, "ff": 0.95}
# Neighbour spread of the real notes (S07 output.json): 90th percentile of the mean absolute difference of harmonics 1..8 (dB).
MAD_Q90 = {"pp": 10.1, "mf": 7.8, "ff": 9.8}
CENTROID_RATIO_RANGE = (0.5, 1.7)        # 5th to 95th percentile of the neighbour centroid ratio is 0.50 to 1.69 over the dynamics
FF_MINUS_PP_LEVEL = (12.0, 25.0)         # 10th to 90th percentile of the real ff - pp level difference (dB)
RISE_RANGE = {"pp": (0.065, 0.91), "mf": (0.022, 0.38), "ff": (0.013, 0.17)}   # half the 10th to twice the 90th percentile of the real rise time (s)
PITCHES = list(range(45, 94, 3))         # A2 to A6 in minor thirds


def tinysol_root():
    p = os.environ.get("FOLK_TINYSOL")
    assert p, "FOLK_TINYSOL is not set"
    root = pathlib.Path(p)
    meta = root / "TinySOL_metadata.csv"
    assert meta.is_file(), f"{meta} is missing"
    assert hashlib.md5(meta.read_bytes()).hexdigest() == TINYSOL_METADATA_MD5, "TinySOL_metadata.csv is not the frozen version 6.0 file"
    return root


def accordion_rows(root):
    with open(root / "TinySOL_metadata.csv", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["Instrument (abbr.)"] == "Acc" and r["Needed digital retuning"] == "FALSE" and r["Dynamics"] in VELOCITY]


def measure(x, sr, midi, a4):
    """Harmonic profile (8 harmonics), centroid / f0, steady level and rise time of one note that lasts at least 1.5 s."""
    f0 = hz(midi, a4)
    dur = len(x) / sr
    a, b = 0.3 * dur, min(0.3 * dur + 1.0, 0.8 * dur)
    s = m.seg(x, sr, a, b)
    f, _ = m.peak_near(s, sr, f0, 80.0)
    t, e = m.envelope_db(x, sr, 0.002)
    first = t[np.nonzero(e > e.max() - 40.0)[0][0]]
    half = t[np.nonzero(e > m.rms_db(s) - 6.0)[0][0]]
    return m.harmonic_profile_db(s, sr, f, 8), m.spectral_centroid(s, sr) / f, m.rms_db(s), float(half - first)


@pytest.fixture(scope="module")
def reference():
    root = tinysol_root()
    out = {}
    for r in accordion_rows(root):
        midi = int(r["Pitch ID"])
        if midi in PITCHES or midi - 1 in PITCHES or midi + 1 in PITCHES:
            x, sr = m.load_mono(root / r["Path"])
            out.setdefault((midi, r["Dynamics"]), []).append(measure(x, sr, midi, A4_TINYSOL))
    assert len(out) >= 100, "too few TinySOL accordion notes were found"
    return out


def test_T200_frozen_thresholds_still_describe_the_data(reference):
    """T-200a. Re-measure the neighbour spread at mf on the subset of pitches used here: its 90th percentile must lie within
    2.5 dB of the frozen figure for the whole set (7.8 dB). A failure means the data set or the metric changed."""
    mads = []
    for p in PITCHES:
        if all((q, "mf") in reference for q in (p - 1, p, p + 1)):
            pred = np.mean([v[0] for q in (p - 1, p + 1) for v in reference[(q, "mf")]], axis=0)
            mads += [float(np.mean(np.abs(v[0] - pred))) for v in reference[(p, "mf")]]
    assert len(mads) >= 12
    assert abs(float(np.percentile(mads, 90)) - MAD_Q90["mf"]) <= 2.5


@pytest.fixture(scope="module")
def candidate(render):
    out = {}
    for p in PITCHES:
        for dyn, vel in VELOCITY.items():
            x, sr = render("accordion", note(p, vel, 3.0, tail=0.2), {"register": 1, "cassotto": 0, "a4_hz": A4_TINYSOL, "vibrato_depth": 0})
            out[(p, dyn)] = measure(m.seg(x, sr, 0.0, 3.0), sr, p, A4_TINYSOL)
    return out


@pytest.mark.parametrize("dyn", ["pp", "mf", "ff"])
def test_T200_harmonic_profile(reference, candidate, dyn):
    """T-200b. For at least 80 % of the compared pitches, the mean absolute difference of harmonics 1 to 8 between the
    synthetic Clarinet-register note and the real note of that pitch and dynamic is within the real neighbour spread."""
    ok = []
    for p in PITCHES:
        if (p, dyn) in reference:
            ref = np.mean([v[0] for v in reference[(p, dyn)]], axis=0)
            ok.append(float(np.mean(np.abs(candidate[(p, dyn)][0] - ref))) <= MAD_Q90[dyn])
    assert len(ok) >= 10 and np.mean(ok) >= 0.8, ok


@pytest.mark.parametrize("dyn", ["pp", "mf", "ff"])
def test_T200_centroid(reference, candidate, dyn):
    """T-200c. For at least 80 % of the compared pitches the centroid ratio (synthetic / real) is between 0.5 and 1.7."""
    ok = []
    for p in PITCHES:
        if (p, dyn) in reference:
            r = candidate[(p, dyn)][1] / np.mean([v[1] for v in reference[(p, dyn)]])
            ok.append(CENTROID_RATIO_RANGE[0] <= r <= CENTROID_RATIO_RANGE[1])
    assert len(ok) >= 10 and np.mean(ok) >= 0.8, ok


def test_T200_dynamic_range(candidate):
    """T-200d. The synthetic ff - pp level difference, averaged over the pitches, is between 12 and 25 dB."""
    d = np.mean([candidate[(p, "ff")][2] - candidate[(p, "pp")][2] for p in PITCHES])
    assert FF_MINUS_PP_LEVEL[0] <= d <= FF_MINUS_PP_LEVEL[1], d


@pytest.mark.parametrize("dyn", ["pp", "mf", "ff"])
def test_T200_rise_time(candidate, dyn):
    """T-200e. The median synthetic rise time at each dynamic lies in the frozen range, and pp rises more slowly than ff."""
    med = float(np.median([candidate[(p, dyn)][3] for p in PITCHES]))
    assert RISE_RANGE[dyn][0] <= med <= RISE_RANGE[dyn][1], med
    assert np.median([candidate[(p, "pp")][3] for p in PITCHES]) > np.median([candidate[(p, "ff")][3] for p in PITCHES])


# ---------------------------------------------------------------------------------------------------- T-201
INDEX = REPO / "references" / "index.csv"
INDEX_FIELDS = ["id", "instrument", "file", "sha256", "midi", "velocity", "sets", "source_url", "author", "licence", "licence_url", "accessed", "redistributable"]


def index_rows():
    assert INDEX.is_file(), "references/index.csv is missing (step S-REF writes it, with a header even when it has no rows)"
    with open(INDEX, newline="") as fh:
        rd = csv.DictReader(fh)
        assert rd.fieldnames == INDEX_FIELDS, rd.fieldnames
        return list(rd)


def test_T201_index_is_well_formed():
    """T-201a. Every row of references/index.csv has an instrument, a 64-digit sha256, a licence, an author, a source URL
    and a redistributable flag of exactly 'true' or 'false' (Rule 15: a reference with no named author is never used)."""
    for r in index_rows():
        assert r["instrument"] in ("harmonica", "accordion", "melodion", "mandolin", "bouzouki"), r
        assert len(r["sha256"]) == 64 and all(c in "0123456789abcdef" for c in r["sha256"]), r
        assert r["redistributable"] in ("true", "false"), r
        assert r["author"].strip() and r["licence"].strip() and r["source_url"].startswith("https://"), r
        assert r["licence"].strip().lower() not in ("unknown", "none stated"), r
        assert 0 <= int(r["midi"]) <= 127 and 0.0 < float(r["velocity"]) <= 1.0


@pytest.mark.parametrize("instrument", ["harmonica", "melodion", "mandolin", "bouzouki"])
def test_T201_candidate_against_reference_set(render, instrument, capsys):
    """T-201b. For an instrument with at least 8 indexed reference notes of which at least 4 have a neighbour within two
    semitones: at least 75 % of the notes have a harmonic-profile difference (harmonics 1 to 8, first second of the note
    for plucked instruments, steady part for reeds) within max(6 dB, the 90th percentile of the set's own neighbour
    spread). With fewer notes the instrument has no reference comparison: the test prints NOT-APPLICABLE and passes, and
    the listening gate for that instrument runs on demos alone (D-051)."""
    rows = [r for r in index_rows() if r["instrument"] == instrument]
    root = os.environ.get("FOLK_REF_ROOT")
    if len(rows) < 8:
        with capsys.disabled():
            print(f"\nT-201 {instrument}: NOT-APPLICABLE ({len(rows)} reference notes indexed)")
        return
    assert root, "FOLK_REF_ROOT is not set although references/index.csv lists notes for " + instrument
    plucked = instrument in ("mandolin", "bouzouki")

    def profile(x, sr, midi):
        s = m.seg(x, sr, 0.03, 1.03) if plucked else m.seg(x, sr, 0.3 * len(x) / sr, min(0.3 * len(x) / sr + 1.0, 0.8 * len(x) / sr))
        f, _ = m.peak_near(s, sr, hz(midi), 80.0)
        return m.harmonic_profile_db(s, sr, f, 8)

    ref = {}
    for r in rows:
        path = pathlib.Path(root) / r["file"]
        assert path.is_file(), f"{path} is missing"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r["sha256"], f"{path} does not match its recorded sha256"
        x, sr = m.load_mono(path)
        ref[r["id"]] = (int(r["midi"]), profile(x, sr, int(r["midi"])), r)
    spread = []
    for i, (mi, pi, _) in ref.items():
        near = [pj for j, (mj, pj, _) in ref.items() if j != i and 0 < abs(mj - mi) <= 2]
        if near:
            spread.append(float(np.mean(np.abs(pi - np.mean(near, axis=0)))))
    if len(spread) < 4:
        with capsys.disabled():
            print(f"\nT-201 {instrument}: NOT-APPLICABLE (only {len(spread)} notes have a neighbour)")
        return
    limit = max(6.0, float(np.percentile(spread, 90)))
    ok = []
    for i, (midi, prof, r) in ref.items():
        sets = dict(kv.split("=") for kv in r["sets"].split(";") if kv)
        x, sr = render(instrument, note(midi, float(r["velocity"]), 3.0, tail=0.2), sets)
        ok.append(float(np.mean(np.abs(profile(m.seg(x, sr, 0.0, 3.0), sr, midi) - prof))) <= limit)
    with capsys.disabled():
        print(f"\nT-201 {instrument}: {sum(ok)} of {len(ok)} notes within {limit:.1f} dB")
    assert np.mean(ok) >= 0.75
