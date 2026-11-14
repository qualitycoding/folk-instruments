# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Harmonica layout, bends and variants (SC-05; C-011 to C-014; D-020 to D-023)."""
import pytest
from conftest import hz, level_at, m, note, pitch_cents


@pytest.mark.parametrize("key,midi", [(7, 69), (7, 55), (9, 57), (2, 62), (6, 66), (11, 59)])
def test_T110_other_keys(render, key, midi):
    """T-110. Key G hole 4 draw is A4 and hole 1 blow G3; A starts at A3, D at D4, F-sharp at F-sharp 4, B at B3."""
    x, sr = render("harmonica", note(midi, 0.6, 2.0), {"key": key})
    assert abs(pitch_cents(x, sr, midi)) <= 5.0


@pytest.mark.parametrize("midi,bend", [(62, 1), (67, 2), (71, 3), (74, 1), (81, 1), (88, 1), (91, 1), (96, 2)])
def test_T111_full_bend_reaches_the_table_depth(render, midi, bend):
    """T-111. With the pitch wheel fully down, each bendable note of a C diatonic falls by its table depth, within 20 cents."""
    x, sr = render("harmonica", ["0 bend -1.0"] + note(midi, 0.6, 2.0))
    assert abs(pitch_cents(x, sr, midi - bend, search=45.0)) <= 20.0


def test_T111_half_bend_and_wheel_up(render):
    """T-111. Half the wheel gives a bend strictly between none and full; wheel up does nothing."""
    half = pitch_cents(*render("harmonica", ["0 bend -0.5"] + note(71, 0.6, 2.0)), 71, search=320.0)
    assert -260.0 <= half <= -40.0
    up = pitch_cents(*render("harmonica", ["0 bend 1.0"] + note(71, 0.6, 2.0)), 71)
    assert abs(up) <= 5.0


@pytest.mark.parametrize("midi", [60, 77, 83])
def test_T111_unbendable_notes_ignore_the_wheel(render, midi):
    """T-111. Hole 1 blow, hole 5 draw and hole 7 draw have no whole-semitone bend: the wheel moves them by under 30 cents."""
    x, sr = render("harmonica", ["0 bend -1.0"] + note(midi, 0.6, 2.0))
    assert -30.0 <= pitch_cents(x, sr, midi) <= 5.0


@pytest.mark.parametrize("midi", [61, 63, 65, 68, 70, 75, 78, 82, 85, 87, 90, 92, 94, 97])
def test_T111_notes_missing_from_the_layout_are_played_as_bends_or_overbends(render, midi):
    """T-111. A MIDI note that is not a natural note of the harmonica sounds at its own pitch, within 20 cents (D-021)."""
    x, sr = render("harmonica", note(midi, 0.6, 2.0))
    assert abs(pitch_cents(x, sr, midi, search=45.0)) <= 20.0


@pytest.mark.parametrize("midi", [59, 98, 30, 120])
def test_T111_notes_outside_the_instrument_are_silent(render, midi):
    x, sr = render("harmonica", note(midi, 0.8, 1.0))
    assert m.rms_db(x) < -90.0


@pytest.mark.parametrize("midi", [60, 61, 65, 66, 71, 72, 84, 95, 97])
def test_T112_chromatic_notes(render, midi):
    """T-112. The chromatic variant plays every semitone from C4 to C-sharp 7 within 5 cents."""
    x, sr = render("harmonica", note(midi, 0.6, 2.0), {"variant": 1})
    assert abs(pitch_cents(x, sr, midi)) <= 5.0


def test_T112_chromatic_bend_and_range(render):
    """T-112. A chromatic bends a single reed down by one semitone at most (C-014), and is silent outside C4 to C-sharp 7."""
    x, sr = render("harmonica", ["0 bend -1.0"] + note(72, 0.6, 2.0), {"variant": 1})
    assert abs(pitch_cents(x, sr, 71, search=45.0)) <= 25.0
    for midi in (59, 98):
        y, _ = render("harmonica", note(midi, 0.8, 1.0), {"variant": 1})
        assert m.rms_db(y) < -90.0


def test_T113_chord(render):
    """T-113. Three notes held together all sound: each fundamental is within 20 dB of the strongest of them."""
    x, sr = render("harmonica", ["0 on 72 0.6", "0 on 76 0.6", "0 on 79 0.6", "2.0 off 72", "2.0 off 76", "2.0 off 79", "2.3 end"])
    lv = [level_at(x, sr, hz(n), 0.6, 1.6) for n in (72, 76, 79)]
    assert max(lv) - min(lv) <= 20.0 and max(lv) > -50.0


def test_T114_hand_wah_darkens(render):
    """T-114. wah = 1 (hands closed) lowers the spectral centroid by at least 10 % and leaves the pitch alone."""
    a, sr = render("harmonica", note(72, 0.6, 2.0), {"wah": 0})
    b, _ = render("harmonica", note(72, 0.6, 2.0), {"wah": 1})
    assert m.spectral_centroid(m.seg(b, sr, 0.6, 1.6), sr) <= 0.9 * m.spectral_centroid(m.seg(a, sr, 0.6, 1.6), sr)
    assert abs(pitch_cents(b, sr, 72)) <= 5.0
