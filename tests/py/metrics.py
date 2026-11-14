# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Audio measurements used by the frozen tests. Every function is checked against a signal with a known answer in
test_metrics_selfcheck.py (lesson: a DSP test once measured the wrong quantity). numpy, scipy and soundfile only."""
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt


def load_mono(path):
    """Returns (samples as float64 mono, sample rate)."""
    x, sr = sf.read(str(path), dtype="float64", always_2d=True)
    return x.mean(axis=1), int(sr)


def seg(x, sr, t0, t1):
    a, b = int(round(t0 * sr)), int(round(t1 * sr))
    assert 0 <= a < b <= len(x), f"segment {t0}..{t1} s is outside the signal ({len(x) / sr:.3f} s)"
    return x[a:b]


def rms_db(x):
    return 10.0 * np.log10(np.mean(np.square(x)) + 1e-30)


def peak_db(x):
    return 20.0 * np.log10(np.max(np.abs(x)) + 1e-30)


def cents(f, ref):
    return 1200.0 * np.log2(f / ref)


def _spectrum(x, sr, pad=8):
    n = len(x)
    w = np.hanning(n)
    nfft = int(2 ** np.ceil(np.log2(n * pad)))
    mag = np.abs(np.fft.rfft(x * w, nfft)) / (w.sum() / 2.0)
    return mag, sr / nfft


def peak_near(x, sr, f_expected, search_cents=60.0):
    """Frequency (Hz) and level (dB re full scale sine) of the strongest spectral peak within search_cents of f_expected.
    Hann window, 8x zero padding, parabolic interpolation on the log magnitude. Needs at least 20 periods."""
    assert len(x) / sr * f_expected >= 20.0, "segment too short for a reliable frequency estimate"
    mag, df = _spectrum(x, sr)
    lo = int(np.floor(f_expected * 2 ** (-search_cents / 1200.0) / df))
    hi = int(np.ceil(f_expected * 2 ** (search_cents / 1200.0) / df))
    lo, hi = max(lo, 1), min(hi, len(mag) - 2)
    k = lo + int(np.argmax(mag[lo:hi + 1]))
    a, b, c = np.log(mag[k - 1:k + 2] + 1e-300)
    d = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    return (k + d) * df, 20.0 * np.log10(np.exp(b - 0.25 * (a - c) * d) + 1e-30)


def partials(x, sr, f0, count, B=0.0, search_cents=35.0):
    """Frequencies and levels of partials 1..count, searched near n*f0*sqrt(1+B*n^2). Partials above 0.45*sr are dropped."""
    out_f, out_l = [], []
    for n in range(1, count + 1):
        fe = n * f0 * np.sqrt(1.0 + B * n * n)
        if fe > 0.45 * sr:
            break
        f, l = peak_near(x, sr, fe, search_cents)
        out_f.append(f)
        out_l.append(l)
    return np.array(out_f), np.array(out_l)


def harmonic_count_above(x, sr, f0, floor_db_re_max=-60.0, max_count=40):
    _, lv = partials(x, sr, f0, max_count)
    return int(np.sum(lv >= lv.max() + floor_db_re_max))


def spectral_centroid(x, sr, fmin=20.0):
    mag, df = _spectrum(x, sr, pad=1)
    f = np.arange(len(mag)) * df
    m = f >= fmin
    p = mag[m] ** 2
    return float(np.sum(f[m] * p) / (np.sum(p) + 1e-300))


def band_energy_db(x, sr, f_lo, f_hi):
    mag, df = _spectrum(x, sr, pad=1)
    f = np.arange(len(mag)) * df
    m = (f >= f_lo) & (f < f_hi)
    return 10.0 * np.log10(np.sum(mag[m] ** 2) + 1e-30)


def envelope_db(x, sr, frame_s=0.005):
    """RMS level in consecutive frames. Returns (frame centre times, levels in dB)."""
    n = max(1, int(round(frame_s * sr)))
    m = len(x) // n
    fr = x[:m * n].reshape(m, n)
    return (np.arange(m) + 0.5) * n / sr, 10.0 * np.log10(np.mean(fr * fr, axis=1) + 1e-30)


def band_envelope_db(x, sr, f_centre, half_width_cents=80.0, frame_s=0.01):
    """Envelope of the band around one partial (zero-phase 4th-order Butterworth band-pass)."""
    lo, hi = f_centre * 2 ** (-half_width_cents / 1200.0), f_centre * 2 ** (half_width_cents / 1200.0)
    sos = butter(4, [lo, min(hi, 0.49 * sr)], btype="bandpass", fs=sr, output="sos")
    return envelope_db(sosfiltfilt(sos, x), sr, frame_s)


def bandpass(x, sr, f_centre, half_width_cents=80.0):
    """The signal restricted to the band around one partial (zero-phase 4th-order Butterworth band-pass)."""
    lo, hi = f_centre * 2 ** (-half_width_cents / 1200.0), f_centre * 2 ** (half_width_cents / 1200.0)
    return sosfiltfilt(butter(4, [lo, min(hi, 0.49 * sr)], btype="bandpass", fs=sr, output="sos"), x)


def decay_rate_db_per_s(t, level_db, t0, t1):
    """Least-squares slope of the level between t0 and t1 (negative for a decay)."""
    m = (t >= t0) & (t < t1)
    assert m.sum() >= 4, "too few envelope frames in the fit range"
    return float(np.polyfit(t[m], level_db[m], 1)[0])


def onset_time(x, sr, fraction=0.5, frame_s=0.002, steady=(0.5, 1.0)):
    """Time at which the frame RMS first reaches the given fraction of the steady RMS (measured in steady, seconds)."""
    t, e = envelope_db(x, sr, frame_s)
    ref = rms_db(seg(x, sr, *steady))
    thr = ref + 20.0 * np.log10(fraction)
    idx = np.nonzero(e >= thr)[0]
    assert len(idx) > 0, "the signal never reaches the onset threshold"
    return float(t[idx[0]])


def modulation_frequency(x, sr, f_lo=0.3, f_hi=30.0, frame_s=0.005):
    """Dominant frequency (Hz) of the amplitude envelope between f_lo and f_hi, and its depth (peak modulation index)."""
    # Low-pass the squared signal before decimating, so that ripple at twice the note frequency cannot alias into the band.
    sos = butter(4, 2.0 * f_hi, btype="lowpass", fs=sr, output="sos")
    power = np.maximum(sosfiltfilt(sos, x * x), 0.0)
    n = max(1, int(round(frame_s * sr)))
    m = len(x) // n
    env = np.sqrt(power[:m * n].reshape(m, n).mean(axis=1))
    fs_env = sr / n
    env = env / (np.mean(env) + 1e-30) - 1.0
    w = np.hanning(m)
    nfft = int(2 ** np.ceil(np.log2(m * 8)))
    spec = np.abs(np.fft.rfft(env * w, nfft)) / (w.sum() / 2.0)
    f = np.arange(len(spec)) * fs_env / nfft
    sel = (f >= f_lo) & (f <= f_hi)
    k = np.nonzero(sel)[0][0] + int(np.argmax(spec[sel]))
    a, b, c = spec[k - 1:k + 2]
    # Interpolate only at an interior local maximum; at the edge of the band report the edge bin itself.
    d = 0.5 * (a - c) / (a - 2 * b + c) if (b >= a and b >= c and (a - 2 * b + c) != 0) else 0.0
    d = float(np.clip(d, -0.5, 0.5))
    return float((k + d) * fs_env / nfft), float(b)


def count_onsets(x, sr, min_gap_s=0.03, rise_db=6.0, frame_s=0.004):
    """Number of attacks: frames whose level exceeds the level two frames (8 ms) earlier by rise_db, at least min_gap_s apart,
    ignoring frames more than 40 dB below the loudest frame."""
    t, e = envelope_db(x, sr, frame_s)
    top = e.max()
    e = np.concatenate(([-300.0, -300.0], e))   # silence before the start, so an attack in the first frame counts
    t = np.concatenate(([-2 * frame_s, -frame_s], t))
    hits, last = 0, -1e9
    for i in range(2, len(e)):
        if e[i] - e[i - 2] >= rise_db and e[i] > top - 40.0 and t[i] - last >= min_gap_s:
            hits += 1
            last = t[i]
    return hits


def harmonic_profile_db(x, sr, f0, count=10):
    """Levels of harmonics 1..count relative to the strongest of them (dB, <= 0)."""
    _, lv = partials(x, sr, f0, count)
    return lv - lv.max()
