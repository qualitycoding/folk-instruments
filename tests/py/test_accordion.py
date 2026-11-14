# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Accordion registers, tremolo, tone chamber and bend (SC-06; C-017 to C-020; D-030 to D-033).
Register indices: 0 Piccolo, 1 Clarinet, 2 Bassoon, 3 Oboe, 4 Violin, 5 Musette (imitation), 6 Musette (authentic),
7 Organ, 8 Harmonium, 9 Bandoneon, 10 Accordion, 11 Master."""
import pytest
from conftest import hz, level_at, m, note, pitch_cents

WITH_L = [2, 7, 8, 9, 10, 11]
WITHOUT_L = [0, 1, 3, 4, 5, 6]


def held(register, midi=69, vel=0.7, dur=2.0, **sets):
    return ("accordion", note(midi, vel, dur), {"register": register, "musette_cents": 0, **sets})


def test_T120_single_rank_registers_sound_in_their_octave(render):
    """T-120. For the key A4: Piccolo (4') sounds at 880 Hz, Clarinet (8') at 440 Hz, Bassoon (16') at 220 Hz."""
    for register, f in ((0, 880.0), (1, 440.0), (2, 220.0)):
        x, sr = render(*held(register))
        assert abs(m.cents(m.peak_near(m.seg(x, sr, 0.6, 1.6), sr, f, 60.0)[0], f)) <= 5.0
        assert level_at(x, sr, f / 2, 0.6, 1.6) <= level_at(x, sr, f, 0.6, 1.6) - 50.0   # nothing an octave below


@pytest.mark.parametrize("register", range(12))
def test_T120_low_rank_present_exactly_in_registers_that_include_it(render, register):
    """T-120. The 220 Hz component of the key A4 is within 25 dB of the 440 or 880 Hz component when the register
    includes the 16' rank, and at least 50 dB below it otherwise."""
    x, sr = render(*held(register))
    low = level_at(x, sr, 220.0, 0.6, 1.6)
    ref = max(level_at(x, sr, 440.0, 0.6, 1.6), level_at(x, sr, 880.0, 0.6, 1.6))
    if register in WITH_L:
        assert low >= ref - 25.0
    else:
        assert low <= ref - 50.0


def test_T120_master_is_louder_than_one_rank(render):
    """T-120. Four ranks carry at least 4 dB more level than one (four uncorrelated equal sources give +6 dB)."""
    one, sr = render(*held(1, musette_cents=15))
    four, _ = render(*held(11, musette_cents=15))
    assert m.rms_db(m.seg(four, sr, 0.6, 1.9)) >= m.rms_db(m.seg(one, sr, 0.6, 1.9)) + 4.0


@pytest.mark.parametrize("midi", [57, 69, 81])
def test_T121_tremolo_beat_rate_constant_cents(render, midi):
    """T-121. Violin register, 15 cents, constant-cents scaling: the level beats at f*(2^(15/1200)-1), within 8 %."""
    x, sr = render("accordion", note(midi, 0.7, 5.0, tail=0.2), {"register": 4, "musette_cents": 15, "musette_scaling": 0})
    f, depth = m.modulation_frequency(m.seg(x, sr, 0.8, 4.8), sr, 0.5, 30.0)
    expected = hz(midi) * (2 ** (15 / 1200) - 1)
    assert abs(f / expected - 1.0) <= 0.08 and depth >= 0.2


@pytest.mark.parametrize("midi", [57, 69, 81])
def test_T121_tremolo_beat_rate_constant_hz(render, midi):
    """T-121. With musette_scaling 1 every key beats at the rate the setting gives at A4 (3.829 Hz for 15 cents)."""
    x, sr = render("accordion", note(midi, 0.7, 5.0, tail=0.2), {"register": 4, "musette_cents": 15, "musette_scaling": 1})
    f, depth = m.modulation_frequency(m.seg(x, sr, 0.8, 4.8), sr, 0.5, 30.0)
    assert abs(f / 3.829 - 1.0) <= 0.08 and depth >= 0.2


def test_T121_dry_tuning_and_three_reed_musette(render):
    """T-121. With 0 cents two unison ranks do not beat; the authentic musette (M-, M, M+) beats at the offset rate or twice it."""
    dry, sr = render("accordion", note(69, 0.7, 5.0, tail=0.2), {"register": 4, "musette_cents": 0})
    wet, _ = render("accordion", note(69, 0.7, 5.0, tail=0.2), {"register": 4, "musette_cents": 15})
    _, d_dry = m.modulation_frequency(m.seg(dry, sr, 0.8, 4.8), sr, 0.5, 30.0)
    _, d_wet = m.modulation_frequency(m.seg(wet, sr, 0.8, 4.8), sr, 0.5, 30.0)
    assert d_dry <= d_wet / 5.0
    x, _ = render("accordion", note(69, 0.7, 5.0, tail=0.2), {"register": 6, "musette_cents": 15})
    f, depth = m.modulation_frequency(m.seg(x, sr, 0.8, 4.8), sr, 0.5, 30.0)
    assert min(abs(f / 3.829 - 1.0), abs(f / 7.657 - 1.0)) <= 0.08 and depth >= 0.1


@pytest.mark.parametrize("param", ["cassotto", "sordina"])
def test_T122_tone_chamber_and_mute_reduce_the_treble(render, param):
    """T-122. Switching the cassotto or the sordina on lowers the energy between 2 and 10 kHz, relative to the whole
    signal, by at least 3 dB and leaves the pitch within 3 cents (D-032: a design value; no measurement was found, C-019)."""
    a, sr = render(*held(1, **{param: 0}))
    b, _ = render(*held(1, **{param: 1}))
    rel = lambda x: m.band_energy_db(m.seg(x, sr, 0.6, 1.6), sr, 2000, 10000) - m.band_energy_db(m.seg(x, sr, 0.6, 1.6), sr, 20, 20000)
    assert rel(b) <= rel(a) - 3.0
    assert abs(pitch_cents(b, sr, 69) - pitch_cents(a, sr, 69)) <= 3.0


@pytest.mark.parametrize("bend_cents", [25, 10])
def test_T123_bend(render, bend_cents):
    """T-123. The pitch wheel fully down lowers the pitch by bend_cents (default 25, the figure of C-020), within 6 cents."""
    x, sr = render("accordion", ["0 bend -1.0"] + note(69, 0.7, 2.0), {"register": 1, "bend_cents": bend_cents})
    assert abs(pitch_cents(x, sr, 69) + bend_cents) <= 6.0


def test_T124_sixteen_keys_sound_together(render):
    """T-124. Sixteen held keys all sound (each fundamental within 30 dB of the strongest); a seventeenth does no harm."""
    keys = list(range(48, 80, 2))
    ev = [f"0 on {k} 0.7" for k in keys] + ["1.0 on 81 0.7"] + [f"2.2 off {k}" for k in keys + [81]] + ["2.5 end"]
    x, sr = render("accordion", ev, {"register": 1})
    lv = [level_at(x, sr, hz(k), 0.4, 0.95, search=25.0) for k in keys]
    assert max(lv) - min(lv) <= 30.0 and max(lv) > -60.0
    assert m.peak_db(x) <= 0.0


def test_T125_key_noise(render):
    """T-125. key_noise = 1 adds at least 6 dB to the first 15 ms of a soft note compared with key_noise = 0."""
    a, sr = render(*held(1, vel=0.3, key_noise=0))
    b, _ = render(*held(1, vel=0.3, key_noise=1))
    assert m.rms_db(m.seg(b, sr, 0.0, 0.015)) >= m.rms_db(m.seg(a, sr, 0.0, 0.015)) + 6.0
