# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Mandolin and bouzouki: stiff strings in double courses on a modal body (SC-08 to SC-10; C-026 to C-031, C-034 to C-042;
D-060 to D-073). Unless a test says otherwise: course_mode 0 plays both strings of a course, 1 plays the first string only;
body_coupling scales the bridge admittance (0 = rigid bridge with a fixed radiation path, 1 = the body preset)."""
import json

import numpy as np
import pytest
from conftest import hz, level_at, m, note, pitch_cents, run_tool

OPEN = {("mandolin", "body", 0): [55, 62, 69, 76], ("mandolin", "body", 1): [55, 62, 69, 76], ("mandolin", "body", 2): [55, 62, 69, 76],
        ("bouzouki", "variant", 0): [50, 57, 62], ("bouzouki", "variant", 1): [48, 53, 57, 62], ("bouzouki", "variant", 2): [43, 50, 57, 62]}
SINGLE = {"course_mode": 1, "pair_detune_cents": 0, "body_coupling": 0, "pick_stiffness": 1}


def dump_model(instrument, sets):
    args = ["--instrument", instrument, "--dump-model"]
    for k, v in sets.items():
        args += ["--set", f"{k}={v}"]
    r = run_tool(args)
    assert r.returncode == 0, f"folk-render --dump-model failed with status {r.returncode}: {r.stderr.strip()}"
    return json.loads(r.stdout)


@pytest.mark.parametrize("ins,param,value,midi", [(k[0], k[1], k[2], n) for k, v in OPEN.items() for n in v])
def test_T140_open_strings(render, ins, param, value, midi):
    """T-140. Every open string of every variant sounds within 3 cents of its tuning (C-034, C-039, C-040)."""
    x, sr = render(ins, note(midi, 0.7, 1.5), {param: value, "pair_detune_cents": 0})
    assert abs(pitch_cents(x, sr, midi, t0=0.05, t1=0.55)) <= 3.0


def test_T141_inharmonicity_of_the_mandolin_a_string(render):
    """T-141. Partials 2 to 10 of the open A string (0.015 in plain steel at 352.4 mm) lie at n*sqrt((1+B*n^2)/(1+B)) times
    the first, within 3 cents, with B as the model reports it, and that B is within 2 % of pi^3*E*d^4/(64*T*L^2) = 1.910e-4."""
    model = dump_model("mandolin", {"body": 0})
    s = model["courses"][2]["strings"][0]
    assert s["midi"] == 69 and abs(s["B"] / 1.910e-4 - 1.0) <= 0.02
    x, sr = render("mandolin", note(69, 0.8, 1.5), {"body": 0, **SINGLE})
    f, _ = m.partials(m.seg(x, sr, 0.05, 0.85), sr, 440.0, 10, B=s["B"], search_cents=30.0)
    for n in range(2, 11):
        expected = n * np.sqrt((1 + s["B"] * n * n) / (1 + s["B"]))
        assert abs(m.cents(f[n - 1] / f[0], expected)) <= 3.0, n


@pytest.mark.parametrize("position,notch", [(0.25, 4), (0.2, 5)])
def test_T142_pluck_position_comb(render, position, notch):
    """T-142. Plucking at 1/k of the string suppresses partial k (and 2k) by at least 20 dB relative to its neighbours (C-030)."""
    x, sr = render("mandolin", note(62, 0.8, 1.2), {"body": 0, "pick_position": position, **SINGLE})
    _, lv = m.partials(m.seg(x, sr, 0.02, 0.52), sr, hz(62), 2 * notch + 1)
    for k in (notch, 2 * notch):
        assert lv[k - 1] <= 0.5 * (lv[k - 2] + lv[k]) - 20.0, (k, lv)


def test_T143_weakly_coupled_pair_beats_at_the_mistuning(render):
    """T-143. Open E string pair mistuned by 4 cents with a nearly rigid bridge: the fundamental's envelope beats at
    659.26*(2^(4/1200)-1) = 1.525 Hz, within 10 % (C-028; spike S04)."""
    x, sr = render("mandolin", note(76, 0.8, 4.5, tail=0.1), {"body": 2, "pair_detune_cents": 4, "body_coupling": 0.02})
    t, e = m.band_envelope_db(m.seg(x, sr, 0.1, 4.5), sr, hz(76), frame_s=0.01)
    lin = 10 ** (e / 20.0)
    trend = np.exp(np.polyval(np.polyfit(t, np.log(lin + 1e-12), 1), t))
    d = lin / trend - 1.0
    spec = np.abs(np.fft.rfft(d * np.hanning(len(d)), 8 * len(d)))
    fr = np.arange(len(spec)) * 100.0 / (8 * len(d))
    sel = (fr > 0.5) & (fr < 6.0)
    assert abs(fr[sel][np.argmax(spec[sel])] / 1.525 - 1.0) <= 0.10


def test_T144_double_decay_of_a_pair_and_single_decay_of_one_string(render):
    """T-144. Bowl-back mandolin, open E pair, default mistuning and body: the fundamental first decays at least twice as
    fast (0.03 to 0.25 s) as later (1.2 to 2.5 s). One string alone decays at one rate (ratio under 1.5) (C-028, C-029)."""
    def rates(mode):
        x, sr = render("mandolin", note(76, 0.8, 3.0, tail=0.1), {"body": 2, "course_mode": mode})
        t, e = m.band_envelope_db(x, sr, hz(76))
        return m.decay_rate_db_per_s(t, e, 0.03, 0.25), m.decay_rate_db_per_s(t, e, 1.2, 2.5)
    early, late = rates(0)
    assert early < 0 and late < 0 and early / late >= 2.0, (early, late)
    early1, late1 = rates(1)
    assert early1 < 0 and late1 < 0 and early1 / late1 < 1.5, (early1, late1)


def test_T145_high_partials_decay_faster(render):
    """T-145. With a rigid bridge the eighth partial of the open G string decays at least 1.2 times as fast (in dB/s) as
    the first: air damping per second grows with frequency and bending damping adds to it (C-027)."""
    x, sr = render("mandolin", note(55, 0.8, 3.0, tail=0.1), {"body": 0, **SINGLE})
    model = dump_model("mandolin", {"body": 0})
    B = model["courses"][0]["strings"][0]["B"]
    r = []
    for n in (1, 8):
        t, e = m.band_envelope_db(x, sr, n * hz(55) * np.sqrt(1 + B * n * n), half_width_cents=60.0)
        r.append(m.decay_rate_db_per_s(t, e, 0.1, 1.5))
    assert r[0] < 0 and r[1] <= 1.2 * r[0], r


BODY_EXPECT = {("mandolin", "body", 0): [313.0, 464.0], ("mandolin", "body", 1): [209.0, 398.0, 482.0]}


@pytest.mark.parametrize("ins,param,value", [("mandolin", "body", 0), ("mandolin", "body", 1), ("mandolin", "body", 2),
                                             ("bouzouki", "variant", 0), ("bouzouki", "variant", 1), ("bouzouki", "variant", 2)])
def test_T146_body_modes_ring_where_the_preset_puts_them(render, ins, param, value):
    """T-146. A tap on the bridge excites spectral peaks at the first three body modes the model reports, within 35 cents
    and within 30 dB of the strongest. Presets: f-hole mandolin has modes within 3 % of 313 and 464 Hz, oval-hole within 3 %
    of 209, 398 and 482 Hz (C-035); the bowl-back has one mode between 180 and 215 Hz and one between 450 and 700 Hz (C-036)."""
    model = dump_model(ins, {param: value})
    modes = sorted(model["body_modes"], key=lambda b: b["hz"])
    assert len(modes) >= 3 and all(b["q"] > 1 for b in modes)
    freqs = [b["hz"] for b in modes]
    for target in BODY_EXPECT.get((ins, param, value), []):
        assert min(abs(f / target - 1.0) for f in freqs) <= 0.03, (target, freqs)
    if (ins, value) == ("mandolin", 2):
        assert any(180.0 <= f <= 215.0 for f in freqs) and any(450.0 <= f <= 700.0 for f in freqs)
    # The tap comes at 0.1 s and the 0.2 s analysis window is centred 50 ms after it, where short-lived modes still ring.
    x, sr = render(ins, ["0.1 tap 1.0", "1.0 end"], {param: value})
    lv = [m.peak_near(m.seg(x, sr, 0.05, 0.25), sr, f, 35.0)[1] for f in freqs[:3]]
    assert max(lv) > -80.0 and max(lv) - min(lv) <= 30.0, lv


def test_T147_octave_course_adds_the_upper_octave(render):
    """T-147. Tetrachordo C course (C3 with C4), rigid bridge: with both strings the 261.6 Hz component is at least 3 dB
    stronger, relative to the 130.8 Hz component, than with the thick string alone (C-039, C-042). The bridge is made
    rigid because a compliant bridge makes the octave string's fundamental and the thick string's second partial a
    coupled pair whose in-phase part decays fast, which hides the level difference this test is about."""
    def ratio(mode):
        x, sr = render("bouzouki", note(48, 0.8, 1.5), {"variant": 1, "course_mode": mode, "pair_detune_cents": 0, "body_coupling": 0})
        return level_at(x, sr, hz(60), 0.05, 0.75) - level_at(x, sr, hz(48), 0.05, 0.75)
    assert ratio(0) >= ratio(1) + 3.0


@pytest.mark.parametrize("how", ["param", "cc"])
def test_T148_tremolo(render, how):
    """T-148. Tremolo at 12 strokes per second re-plucks a held note: 24 attacks in 2 s, give or take one. It is switched
    by the tremolo parameter or by the modulation wheel at or above 0.5."""
    ev = (["0 cc 1 1.0"] if how == "cc" else []) + note(76, 0.8, 2.0, tail=0.3)
    x, sr = render("mandolin", ev, {"tremolo": 1 if how == "param" else 0, "tremolo_rate_hz": 12})
    assert abs(m.count_onsets(m.seg(x, sr, 0.0, 2.0), sr) - 24) <= 1
    y, _ = render("mandolin", note(76, 0.8, 2.0, tail=0.3), {"tremolo": 0})
    assert m.count_onsets(m.seg(y, sr, 0.0, 2.0), sr) == 1


def test_T149_one_note_per_course(render):
    """T-149. A second note on the same course replaces the first (the first is 30 dB down 0.3 s later); notes on
    different courses ring together."""
    x, sr = render("mandolin", ["0 on 69 0.8", "0.5 on 71 0.8", "1.5 off 69", "1.5 off 71", "1.8 end"], {"pair_detune_cents": 0})
    assert level_at(x, sr, hz(69), 0.8, 1.3) <= level_at(x, sr, hz(71), 0.8, 1.3) - 30.0
    y, _ = render("mandolin", ["0 on 69 0.8", "0 on 76 0.8", "1.5 off 69", "1.5 off 76", "1.8 end"], {"pair_detune_cents": 0})
    assert abs(level_at(y, sr, hz(69), 0.2, 0.7) - level_at(y, sr, hz(76), 0.2, 0.7)) <= 25.0


@pytest.mark.parametrize("wheel,rng,shift", [(1.0, 2, 200.0), (-1.0, 2, -200.0), (0.5, 2, 100.0), (1.0, 0, 0.0), (1.0, 12, 1200.0)])
def test_T150_pitch_bend(render, wheel, rng, shift):
    """T-150. The pitch wheel moves a string's pitch by wheel * bend_range semitones, within 5 cents."""
    x, sr = render("mandolin", [f"0 bend {wheel}"] + note(69, 0.8, 1.2), {"bend_range": rng, "pair_detune_cents": 0})
    f, _ = m.peak_near(m.seg(x, sr, 0.05, 0.55), sr, 440.0 * 2 ** (shift / 1200.0), 40.0)
    assert abs(m.cents(f, 440.0) - shift) <= 5.0


def test_T151_note_off_damps_unless_sustained(render):
    """T-151. Releasing a note damps it: 0.5 s after note-off the level is at least 30 dB below the level just before,
    and at least 12 dB further down than when the sustain pedal (CC 64) holds the note (a coupled pair's own first
    decay can reach 15 to 20 dB in that time, so no absolute bound is set for the sustained case)."""
    def drop(pedal):
        ev = (["0 cc 64 1.0"] if pedal else []) + ["0 on 62 0.8", "0.3 off 62", "1.2 end"]
        x, sr = render("mandolin", ev, {})
        return m.rms_db(m.seg(x, sr, 0.2, 0.3)) - m.rms_db(m.seg(x, sr, 0.8, 0.9))
    released, held = drop(False), drop(True)
    assert released >= 30.0 and released >= held + 12.0, (released, held)


@pytest.mark.parametrize("ins", ["mandolin", "bouzouki"])
def test_T152_velocity(render, ins):
    """T-152. A hard stroke (velocity 1.0) is at least 6 dB louder than a soft one (0.3) and not darker."""
    soft, sr = render(ins, note(62, 0.3, 1.0))
    hard, _ = render(ins, note(62, 1.0, 1.0))
    assert m.rms_db(m.seg(hard, sr, 0.0, 0.5)) >= m.rms_db(m.seg(soft, sr, 0.0, 0.5)) + 6.0
    assert m.spectral_centroid(m.seg(hard, sr, 0.0, 0.5), sr) >= m.spectral_centroid(m.seg(soft, sr, 0.0, 0.5), sr)


def test_T153_damping_parameter(render):
    """T-153. damping = 1 makes a held note decay at least 1.5 times as fast (dB/s, 0.1 to 1.0 s) as damping = 0."""
    r = []
    for d in (0, 1):
        x, sr = render("mandolin", note(62, 0.8, 2.0), {"damping": d, **SINGLE})
        t, e = m.band_envelope_db(x, sr, hz(62))
        r.append(m.decay_rate_db_per_s(t, e, 0.1, 1.0))
    assert r[0] < 0 and r[1] <= 1.5 * r[0], r
