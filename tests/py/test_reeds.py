# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Behaviour common to the three free-reed instruments (SC-03, SC-04; claims C-001 to C-004; decisions D-010 to D-013, D-024).
Reference figures quoted in the comments are from research/spikes/s07-tinysol-accordion/output.json (646 real accordion notes).
With breath_source = 0 (the default) the note velocity is the breath or bellows pressure for the whole note."""
import numpy as np
import pytest
from conftest import hz, level_at, m, note, pitch_cents

REEDS = ["harmonica", "accordion", "melodion"]
A = {"harmonica": 72, "accordion": 69, "melodion": 69}   # a mid-range note each instrument plays by default
PITCH_NOTES = {
    "harmonica": [60, 62, 64, 67, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 96],   # every natural note of a C diatonic
    "accordion": [40, 52, 57, 60, 64, 69, 72, 76, 81, 88, 93, 100],
    "melodion": [53, 56, 59, 62, 65, 68, 71, 74, 77, 80, 83, 86, 89],                            # F3 to F6 in minor thirds
}


@pytest.mark.parametrize("ins,midi", [(i, n) for i in REEDS for n in PITCH_NOTES[i]])
def test_T100_reed_pitch_within_5_cents(render, ins, midi):
    """T-100. At the reference breath (velocity 0.6) every reed sounds within 5 cents of equal temperament: the model's
    sounding pitch lies 13 to 25 cents below the reed's natural frequency (spikes S03, S03c), so the engine must compensate."""
    x, sr = render(ins, note(midi, 0.6, 2.0))
    assert abs(pitch_cents(x, sr, midi)) <= 5.0


@pytest.mark.parametrize("ins", REEDS)
def test_T101_threshold(render, ins):
    """T-101. Below the threshold pressure a reed is silent; at normal pressure it sounds (C-002)."""
    quiet, sr = render(ins, note(A[ins], 0.02, 1.5))
    loud, _ = render(ins, note(A[ins], 0.5, 1.5))
    assert m.rms_db(m.seg(quiet, sr, 0.5, 1.5)) < -70.0
    assert m.rms_db(m.seg(loud, sr, 0.5, 1.5)) > -40.0


@pytest.mark.parametrize("ins", REEDS)
def test_T102_level_rises_with_breath(render, ins):
    """T-102. Level never falls as breath rises, and spans 10 to 40 dB between velocity 0.25 and 1.0
    (real accordion, ff minus pp: 12.4 to 24.8 dB between the 10th and 90th percentile)."""
    lv = [m.rms_db(m.seg(render(ins, note(A[ins], v, 1.6))[0], 48000, 0.6, 1.6)) for v in (0.25, 0.4, 0.55, 0.7, 0.85, 1.0)]
    assert all(b >= a - 0.5 for a, b in zip(lv, lv[1:])), lv
    assert 10.0 <= lv[-1] - lv[0] <= 40.0, lv


@pytest.mark.parametrize("ins", REEDS)
def test_T103_pitch_falls_slightly_with_breath(render, ins):
    """T-103. From velocity 0.3 to 1.0 the pitch moves by between -30 and +5 cents (model: about -1 to -5 cents;
    real accordion ff minus pp: -8.6 to +2.2 cents between the 10th and 90th percentile)."""
    lo = pitch_cents(*render(ins, note(A[ins], 0.3, 2.0)), A[ins])
    hi = pitch_cents(*render(ins, note(A[ins], 1.0, 2.0)), A[ins])
    assert -30.0 <= hi - lo <= 5.0


@pytest.mark.parametrize("ins", REEDS)
def test_T104_spectrum_is_rich_and_not_darker_when_louder(render, ins):
    """T-104. At velocity 0.6 at least 8 harmonics lie within 60 dB of the strongest (real accordion: 10 of the first 10);
    the spectral centroid at velocity 1.0 is not below that at 0.3 (C-003)."""
    x, sr = render(ins, note(A[ins], 0.6, 2.0))
    assert m.harmonic_count_above(m.seg(x, sr, 0.6, 1.6), sr, hz(A[ins]), -60.0, 20) >= 8
    c_lo = m.spectral_centroid(m.seg(render(ins, note(A[ins], 0.3, 2.0))[0], sr, 0.6, 1.6), sr)
    c_hi = m.spectral_centroid(m.seg(render(ins, note(A[ins], 1.0, 2.0))[0], sr, 0.6, 1.6), sr)
    assert c_hi >= c_lo


@pytest.mark.parametrize("ins", REEDS)
def test_T105_attack_is_neither_instant_nor_sluggish(render, ins):
    """T-105. The level reaches half its steady value between 5 ms and 400 ms after note-on at velocity 0.6, and a soft
    note speaks later than a loud one (real accordion median rise: pp 213 ms, mf 94 ms, ff 40 ms)."""
    t_mid = m.onset_time(render(ins, note(A[ins], 0.6, 1.6))[0], 48000, 0.5, steady=(0.8, 1.4))
    t_soft = m.onset_time(render(ins, note(A[ins], 0.3, 1.6))[0], 48000, 0.5, steady=(0.8, 1.4))
    t_loud = m.onset_time(render(ins, note(A[ins], 1.0, 1.6))[0], 48000, 0.5, steady=(0.8, 1.4))
    assert 0.005 <= t_mid <= 0.4
    assert t_soft > t_loud


@pytest.mark.parametrize("ins", REEDS)
def test_T106_note_off_stops_the_reed(render, ins):
    """T-106. Half a second after note-off the level is at least 40 dB below the held level."""
    x, sr = render(ins, note(A[ins], 0.7, 1.5, tail=1.0))
    assert m.rms_db(m.seg(x, sr, 2.0, 2.5)) <= m.rms_db(m.seg(x, sr, 0.6, 1.4)) - 40.0


@pytest.mark.parametrize("ins", REEDS)
def test_T107_vibrato(render, ins):
    """T-107. With vibrato_depth 1 the level is modulated at vibrato_rate_hz (5.5 Hz); with depth 0 the modulation is at most a third as deep.
    The modulation wheel (CC 1) adds to vibrato_depth."""
    ev = note(A[ins], 0.7, 4.0, tail=0.2)
    f, depth = m.modulation_frequency(m.seg(render(ins, ev, {"vibrato_depth": 1, "vibrato_rate_hz": 5.5})[0], 48000, 0.8, 3.8), 48000, 2.0, 12.0)
    assert abs(f - 5.5) <= 0.3 and depth >= 0.02
    _, still = m.modulation_frequency(m.seg(render(ins, ev, {"vibrato_depth": 0})[0], 48000, 0.8, 3.8), 48000, 2.0, 12.0)
    assert still <= depth / 3.0
    f2, d2 = m.modulation_frequency(m.seg(render(ins, ["0 cc 1 1.0"] + ev, {"vibrato_depth": 0})[0], 48000, 0.8, 3.8), 48000, 2.0, 12.0)
    assert abs(f2 - 5.5) <= 0.3 and d2 >= 0.02


@pytest.mark.parametrize("ins,src,cc", [(i, s, c) for i in REEDS for s, c in ((1, 2), (2, 11))])
def test_T108_breath_from_controller(render, ins, src, cc):
    """T-108. With breath_source 1 (CC 2) or 2 (CC 11) the controller, not the velocity, sets the pressure."""
    n = A[ins]
    silent, sr = render(ins, [f"0 cc {cc} 0.0", f"0 on {n} 1.0", f"1.5 off {n}", "1.7 end"], {"breath_source": src})
    assert m.rms_db(m.seg(silent, sr, 0.5, 1.5)) < -70.0
    swell, _ = render(ins, [f"0 cc {cc} 0.0", f"0 on {n} 0.1"] + [f"{0.5 + 0.1 * k:.1f} cc {cc} {0.1 * k:.1f}" for k in range(1, 11)] + [f"2.5 off {n}", "2.7 end"], {"breath_source": src})
    assert m.rms_db(m.seg(swell, sr, 1.7, 2.4)) > m.rms_db(m.seg(swell, sr, 0.0, 0.5)) + 30.0
