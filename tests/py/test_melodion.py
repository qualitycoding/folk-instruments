# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Melodion: one breath feeding every open reed (SC-07; C-023 to C-025; D-040, D-041)."""
import pytest
from conftest import hz, level_at, m, note, pitch_cents


def chord(notes, vel=0.7, dur=2.0):
    return [f"0 on {n} {vel}" for n in notes] + [f"{dur} off {n}" for n in notes] + [f"{dur + 0.3} end"]


def test_T131_flow_limited_breath_sags_as_keys_are_added(render):
    """T-131. With breath_mode 1 (a fixed breath flow shared by all open reeds) the A4 reed gets quieter by at least
    1.5 dB when three more keys are held and by a further 1.5 dB with seven more (mass conservation in the plenum, D-041)."""
    lv = []
    for others in ([], [60, 64, 67], [60, 62, 64, 65, 67, 71, 72]):
        x, sr = render("melodion", chord([69] + others), {"breath_mode": 1})
        lv.append(level_at(x, sr, 440.0, 0.8, 1.8, search=25.0))
    assert lv[0] - lv[1] >= 1.5 and lv[1] - lv[2] >= 1.5, lv


def test_T131_pressure_controlled_breath_does_not_sag(render):
    """T-131. With breath_mode 0 (the breath holds the plenum pressure) the A4 reed changes by under 1.5 dB."""
    one, sr = render("melodion", chord([69]), {"breath_mode": 0})
    many, _ = render("melodion", chord([69, 60, 62, 64, 65, 67, 71, 72]), {"breath_mode": 0})
    assert abs(level_at(one, sr, 440.0, 0.8, 1.8, search=25.0) - level_at(many, sr, 440.0, 0.8, 1.8, search=25.0)) <= 1.5


def test_T132_moisture_chokes_the_reed(render):
    """T-132. moisture = 1 lowers the level by at least 6 dB or delays the attack by at least 50 ms (design value, C-025)."""
    dry, sr = render("melodion", note(69, 0.6, 2.0), {"moisture": 0})
    wet, _ = render("melodion", note(69, 0.6, 2.0), {"moisture": 1})
    quieter = m.rms_db(m.seg(wet, sr, 0.8, 1.8)) <= m.rms_db(m.seg(dry, sr, 0.8, 1.8)) - 6.0
    later = m.rms_db(m.seg(wet, sr, 0.8, 1.8)) > -70.0 and m.onset_time(wet, sr, 0.5, steady=(1.2, 1.9)) >= m.onset_time(dry, sr, 0.5, steady=(1.2, 1.9)) + 0.05
    assert quieter or later


@pytest.mark.parametrize("rng,lowest,highest", [(0, 53, 84), (1, 53, 89), (2, 41, 64)])
def test_T133_keyboard_ranges(render, rng, lowest, highest):
    """T-133. range 0 is a 32-key F3 to C6 instrument, range 1 a 37-key F3 to F6 instrument (C-024), range 2 a 24-key
    bass instrument F2 to E4 (a design value: no maker's figure was found). Keys outside the range are silent."""
    for midi in (lowest, highest):
        x, sr = render("melodion", note(midi, 0.6, 2.0), {"range": rng})
        assert abs(pitch_cents(x, sr, midi)) <= 5.0
    for midi in (lowest - 1, highest + 1):
        x, sr = render("melodion", note(midi, 0.8, 1.0), {"range": rng})
        assert m.rms_db(x) < -90.0


def test_T134_wooden_body_is_darker_than_plastic(render):
    """T-134. body 1 (wood) has a spectral centroid at least 5 % below body 0 (plastic); body 2 (metal) differs from
    both by at least 3 % (design values, D-040)."""
    c = []
    for body in (0, 1, 2):
        x, sr = render("melodion", note(69, 0.6, 2.0), {"body": body})
        c.append(m.spectral_centroid(m.seg(x, sr, 0.6, 1.6), sr))
    assert c[1] <= 0.95 * c[0]
    assert abs(c[2] / c[0] - 1.0) >= 0.03 and abs(c[2] / c[1] - 1.0) >= 0.03
