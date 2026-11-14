# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-090 known-answer checks of tests/py/metrics.py. These tests exercise the test tooling, not the product, so they pass
from the day they are frozen; they are excluded from red verification (plan/TRACEABILITY.md)."""
import numpy as np
import pytest
import metrics as m

SR = 48000


def tone(f, dur=2.0, amp=0.5, sr=SR, phase=0.0):
    t = np.arange(int(dur * sr)) / sr
    return amp * np.sin(2 * np.pi * f * t + phase)


def test_peak_near_frequency_and_level():
    for f in (98.0, 440.0, 1046.5, 3520.0):
        fe, le = m.peak_near(tone(f * 2 ** (7 / 1200)), SR, f)   # the true tone is 7 cents sharp of the expectation
        assert abs(m.cents(fe, f) - 7.0) < 0.2
        assert abs(le - 20 * np.log10(0.5)) < 0.1


def test_peak_near_refuses_short_segments():
    with pytest.raises(AssertionError):
        m.peak_near(tone(100.0, dur=0.1), SR, 100.0)


def test_partials_follow_stiff_string_law():
    f0, B = 220.0, 2e-4
    x = sum(tone(n * f0 * np.sqrt(1 + B * n * n), amp=0.3 / n) for n in range(1, 13))
    f, lv = m.partials(x, SR, f0, 12, B=B)
    for n in range(1, 13):
        assert abs(m.cents(f[n - 1], n * f0 * np.sqrt(1 + B * n * n))) < 0.5
        assert abs(lv[n - 1] - 20 * np.log10(0.3 / n)) < 0.2


def test_rms_peak_centroid_band():
    x = tone(1000.0, amp=0.5)
    assert abs(m.rms_db(x) - 20 * np.log10(0.5 / np.sqrt(2))) < 0.01
    assert abs(m.peak_db(x) - 20 * np.log10(0.5)) < 0.01
    assert abs(m.spectral_centroid(x, SR) - 1000.0) < 2.0
    y = tone(500.0, amp=0.5) + tone(4000.0, amp=0.5)
    assert abs(m.spectral_centroid(y, SR) - 2250.0) < 5.0
    assert abs(m.band_energy_db(y, SR, 3000, 5000) - m.band_energy_db(y, SR, 300, 700)) < 0.1


def test_decay_rate_and_two_stage_decay():
    t = np.arange(3 * SR) / SR
    x = np.sin(2 * np.pi * 660 * t) * (0.5 * 10 ** (-60 * t / 20) + 0.02 * 10 ** (-4 * t / 20))
    te, e = m.band_envelope_db(x, SR, 660.0)
    assert abs(m.decay_rate_db_per_s(te, e, 0.02, 0.2) - (-60.0)) < 6.0
    assert abs(m.decay_rate_db_per_s(te, e, 1.5, 2.5) - (-4.0)) < 0.5


def test_onset_time():
    x = tone(440.0, dur=1.5)
    ramp = np.clip(np.arange(len(x)) / (0.1 * SR), 0, 1)    # linear attack of 100 ms: half amplitude at 50 ms
    assert abs(m.onset_time(x * ramp, SR, fraction=0.5) - 0.05) < 0.004


def test_modulation_frequency_of_two_detuned_tones():
    f0, c = 440.0, 15.0
    x = tone(f0, dur=4.0, amp=0.3) + tone(f0 * 2 ** (c / 1200), dur=4.0, amp=0.3)
    fm, depth = m.modulation_frequency(x, SR)
    assert abs(fm - f0 * (2 ** (c / 1200) - 1)) < 0.05
    assert depth > 0.3


def test_count_onsets():
    x = np.zeros(2 * SR)
    for k in range(24):   # 12 strokes per second for 2 s
        a = int(k * SR / 12)
        n = int(0.07 * SR)
        x[a:a + n] += tone(880.0, dur=0.07) * np.exp(-np.arange(n) / (0.02 * SR))
    assert m.count_onsets(x, SR) == 24


def test_harmonic_count_and_profile():
    x = sum(tone(n * 300.0, amp=0.4 * 10 ** (-6 * (n - 1) / 20)) for n in range(1, 21))   # -6 dB per harmonic
    assert m.harmonic_count_above(x, SR, 300.0, -60.0) == 11                               # harmonics 1..11 are within 60 dB
    p = m.harmonic_profile_db(x, SR, 300.0, 5)
    assert np.allclose(p, [0, -6, -12, -18, -24], atol=0.2)


def test_modulation_frequency_ignores_ripple_of_a_steady_tone():
    for f in (261.63, 440.0, 523.25, 1046.5):
        _, depth = m.modulation_frequency(tone(f, dur=4.0), SR, 2.0, 12.0)
        assert depth < 0.002
    t = np.arange(4 * SR) / SR
    fm, depth = m.modulation_frequency(tone(523.25, dur=4.0) * (1 + 0.05 * np.sin(2 * np.pi * 5.5 * t)), SR, 2.0, 12.0)
    assert abs(fm - 5.5) < 0.05 and abs(depth - 0.05) < 0.01


def test_modulation_frequency_stays_inside_its_band():
    t = np.arange(4 * SR) / SR
    slow = tone(440.0, dur=4.0) * (1 + 0.3 * np.sin(2 * np.pi * 0.1 * t))     # modulation below the band
    f, _ = m.modulation_frequency(slow, SR, 0.5, 30.0)
    assert 0.5 <= f <= 30.0


def test_bandpass_isolates_the_fundamental_beat():
    """Two detuned tones with strong third harmonics: the broadband envelope also beats at three times the rate; the
    band around the fundamental beats at the rate itself."""
    f0, d = 440.0, 3.829
    x = sum(tone(n * f0, dur=5.0, amp=a) + tone(n * (f0 + d), dur=5.0, amp=a) for n, a in ((1, 0.2), (3, 0.25)))
    f, depth = m.modulation_frequency(m.bandpass(x, SR, f0), SR, 0.5, 30.0)
    assert abs(f - d) < 0.05 and depth > 0.3
