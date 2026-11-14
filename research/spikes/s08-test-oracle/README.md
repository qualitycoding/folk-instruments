# Spike S08: test oracle

`fake_render.py` is an idealised additive-synthesis stand-in for `folk-render`. It follows the command-line contract of
D-092 and the intended behaviour of each instrument, and exists only to check the frozen Python tests: that each
assertion can be satisfied by a consistent instrument, and that each measurement measures what its test claims.

Result on 2026-11-14 (`FOLK_RENDER` pointing at a wrapper that runs this file; `python3 -m pytest -m "not reference"` in `tests/`):
every test in `test_reeds.py`, `test_harmonica.py`, `test_accordion.py`, `test_melodion.py`, `test_strings.py` and
`test_common.py` passes, except `test_T163_two_runs_write_identical_files`, which fails intermittently for the oracle
only: libsndfile writes a PEAK chunk with a time stamp into float WAV files, so two runs in different seconds differ in
one header byte. The product's own WAV writer must not write a PEAK chunk or any time stamp (D-092).

The first run found three defects in the tests, corrected before the freeze (lesson
`L-20261114T135800Z-frozen-tests-checked-against-oracle`): the body-mode test analysed a window whose Hann taper removed
the tap; the octave-course test compared levels after the coupled pair's fast decay; the sustain test set an absolute
bound that a coupled pair's own first decay exceeds.

The oracle is not a reference implementation. It models no reed physics and its numbers are arbitrary.
