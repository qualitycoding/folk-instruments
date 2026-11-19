# Traceability

## 1. Success criteria

| ID | Criterion (measurable) | Tests | Steps |
|---|---|---|---|
| SC-01 | Five plugins build as VST3 and Standalone on Windows x64, macOS (universal: arm64 and x86_64) and Linux x64, and pass pluginval at strictness 10 with proof of coverage | T-300, T-302; the `plugins` CI job on four runners; the universal-binary check | S-310, S-320 |
| SC-02 | The core's public interface behaves as specified: parameter tables, names, state text | T-008, T-014 | S-110 |
| SC-03 | Every playable note sounds at its equal-tempered pitch: reeds within 5 cents at the reference breath, strings within 3 cents; `a4_hz` shifts it | T-001, T-100, T-110, T-112, T-140, T-162 | S-100, S-201, S-210 to S-260 |
| SC-04 | Reeds behave like reeds: a threshold, level rising with breath by 10 to 40 dB, pitch moving by -30 to +5 cents, a rich spectrum that is mostly brighter when louder, an attack between 5 and 400 ms that is slower when soft, release, vibrato, breath from controllers | T-101 to T-108 | S-200 to S-230 |
| SC-05 | Harmonica: Richter layout in 12 keys; bends to the table depth; missing notes played as bends or overbends; chromatic variant; chords; hand effect | T-002, T-003, T-110 to T-114 | S-100, S-210 |
| SC-06 | Accordion: 12 registers with the right ranks; tremolo beat rate within 8 % in both scalings; cassotto and sordina; bend; 16 keys; key noise | T-004, T-120 to T-125 | S-100, S-220 |
| SC-07 | Melodion: chord sag under a flow-limited breath and none under a pressure-controlled breath; moisture; ranges; bodies | T-131 to T-134 | S-230 |
| SC-08 | Strings: stiff-string partials within 3 cents; loss formulas; pluck-position comb; beats at the mistuning; two-stage decay of a pair and single decay of one string; faster decay of high partials | T-005, T-006, T-141 to T-145 | S-101, S-240, S-250 |
| SC-09 | Bodies: preset modes ring where the preset puts them; presets carry the literature values | T-146 | S-240 to S-260 |
| SC-10 | Courses and playing: tunings of all six string variants; note-to-course rule; octave courses; tremolo; one note per course; pitch bend; damping and sustain; velocity; damping control | T-007, T-140, T-147 to T-154 | S-100, S-250, S-260 |
| SC-11 | Robustness and safety: finite output within full scale under random use; block-size and sample-rate independence; no allocation on the audio thread; determinism; malformed state and event files refused; tails end; command-line contract | T-009 to T-012, T-015, T-160, T-161, T-163, T-302 | S-110, S-300, S-310 |
| SC-12 | Performance: each instrument at full polyphony at least 4 times faster than real time at 48 kHz, block 256, on the `ubuntu-24.04` x64 hosted runner (A-009) | T-013 | S-300, S-320 |
| SC-13 | Reference comparison: the accordion within the spread of real notes (harmonic profile, centroid, dynamic range, rise time); other instruments within their own reference spread where 8 or more notes exist; reference handling is fail-closed | T-200, T-201, T-210 | S-REF, S-330 |
| SC-14 | Listening: each instrument passes its gate (at most 8 of 12 blind pairs identified where pairs exist; no demo reported as wrong) | gates G-L1 to G-L5 (records under `listening/`) | S-LISTEN |
| SC-15 | Supply chain: no known vulnerability in the Python test dependencies; pins as recorded | T-310; `plan/ENVIRONMENT.md` | S-003, S-320 |
| SC-16 | Delivery: a pull request to `main` with every check green | `all-green` on the pull request | S-INTEGRATE |

## 2. Tests

Categories: U unit, I integration, O operational, S security, P performance, R reference, V plugin validation, K tool check (passes from the freeze).

| ID | File (frozen) | Category | Enforces | Cases |
|---|---|---|---|---|
| T-001 | `tests/cpp/test_tuning.cpp` | U | SC-03 | 1 |
| T-002 | same | U | SC-05; C-011 | 3 |
| T-003 | same | U | SC-05; C-012, C-013, C-014 | 3 |
| T-004 | same | U | SC-06; C-017 | 1 |
| T-007 | same | U | SC-10; C-034, C-039, C-040 | 3 |
| T-005 | `tests/cpp/test_strings.cpp` | U | SC-08; C-026, C-027 | 3 |
| T-006 | same | U | SC-08; C-028 | 3 |
| T-008 | `tests/cpp/test_engine.cpp` (with `param_table.h`) | U | SC-02 | 2 |
| T-009 | same | I, S | SC-11 | 2 |
| T-010 | same | I | SC-11 | 1 |
| T-011 | same | I | SC-11 | 1 |
| T-012 | same | I | SC-11 | 1 |
| T-014 | same | U, S | SC-02, SC-11 | 2 |
| T-015 | same | I, O | SC-11 | 1 |
| T-016 | `tests/cpp/test_locale.cpp` (program `folk-locale-tests`) | U, S | SC-02, SC-11 | 2 |
| T-013 | `tests/cpp/test_perf.cpp` | P | SC-12 | 1 |
| T-302 | `tests/juce/host_test.cpp` (one program per plugin) | I, S | SC-01, SC-11 | 7 per plugin |
| T-303 | same | I | SC-01 | 1 per plugin |
| T-304 | same (also run under ThreadSanitizer in job `host-tsan`) | I, S | SC-01, SC-11 | 1 per plugin |
| T-090 | `tests/py/test_metrics_selfcheck.py` (checks `tests/py/metrics.py`) | K | the measurements themselves | 12 |
| T-091 | `tests/py/test_pluginval_log_check.py` (checks `tests/ci/check_pluginval_log.py`) | K | T-300's check | 2 |
| T-092 | `tests/py/test_tsan_supp_check.py` (checks `tests/ci/check_tsan_supp.py`; with the canaries `tests/ci/tsan_canary.cpp`, `tests/ci/tsan_canary_named.cpp` and `tests/ci/tsan_canary_scope.cpp` in job `host-tsan`) | K | T-304's sanitiser run | 29 |
| T-100 to T-109 | `tests/py/test_reeds.py` | I | SC-03, SC-04; C-001 to C-004, C-053, C-059, C-062 | 44, 9, 9, 9, 3, 3, 3, 3, 6, 3 |
| T-110 to T-114 | `tests/py/test_harmonica.py` | I | SC-05 | 6, 30, 10, 1, 1 |
| T-120 to T-125 | `tests/py/test_accordion.py` | I | SC-06 | 14, 7, 2, 2, 1, 1 |
| T-131 to T-134 | `tests/py/test_melodion.py` | I | SC-07 | 2, 1, 3, 1 |
| T-140 to T-154 | `tests/py/test_strings.py` | I | SC-08, SC-09, SC-10 | 23, 1, 2, 1, 1, 1, 6, 1, 2, 1, 5, 1, 2, 1, 27 |
| T-160 | `tests/py/test_common.py` | I | SC-11 | 10 |
| T-161 | same (with `tests/fixtures/`) | O, S | SC-11 | 16 |
| T-162 | same | I | SC-03, SC-11 | 5 |
| T-163 | same | O | SC-11 | 5 |
| T-200 | `tests/py/test_reference.py` | R | SC-13; C-055 | 11: T-200a (1, a tool check on the data), T-200b harmonic profile (3), T-200c centroid (3), T-200d dynamic range (1), T-200e rise time (3) |
| T-201 | same | R | SC-13 | 5: T-201a index well-formed (1), T-201b comparison per instrument (4) |
| T-210 | `tests/py/test_evidence_guard.py` | S | SC-13; Rule 15 | 7 |
| T-211 | `tests/py/test_fetch_references.py` | S | SC-13; Rule 16 | 10 |
| T-300 | CI step "pluginval, strictness 10, each plugin" with `tests/ci/check_pluginval_log.py` | V | SC-01 | 5 plugins on 4 runners |
| T-310 | CI job `audit` (`pip_audit --strict`) | S | SC-15 | 1 |

Test IDs T-130 and T-017 to T-089 are unused.

Required categories (protocol 2B.3): unit (T-001 to T-008, T-014); integration (T-009 to T-012, T-100 to T-163, T-302); operational (T-015 tails and shutdown of sound, T-161 start-up, configuration errors and I/O failures of the render tool, T-163 repeatability; resource exhaustion: T-009's event flood and T-124's seventeenth key; resume after interruption does not apply to a plugin or a one-shot render, which hold no persistent state beyond the state text of T-014); security (T-009, T-014, T-161, T-210, T-302 malformed state, T-310 dependency scan); performance (T-013, best of three runs, on the named runner). Deployment tests: not applicable (`software.deploys = false`).

Every test with a numeric threshold fails the build when missed: all are assertions in programs whose exit status CI checks without any failure-swallowing; T-013 gates on `ubuntu-24.04` (D-086).

## 3. Decisions and claims to tests

| Decision | Claims | Tests |
|---|---|---|
| D-010 to D-016 (reed model, scaling, breath, safety) | C-001 to C-004, C-053, C-054, C-059 to C-061 | T-009 to T-013, T-100 to T-109; the checks of S-200 and S-201 |
| D-020 to D-024 | C-011 to C-014 | T-002, T-003, T-110 to T-114 |
| D-030 to D-033 | C-017 to C-020 | T-004, T-120 to T-125 |
| D-040, D-041 | C-023 to C-025, C-065 | T-131 to T-134 |
| D-050 to D-053 | C-021, C-049 to C-051, C-055 | T-200, T-201, T-210, T-211; gates G-L1 to G-L5 |
| D-060 to D-064 | C-026 to C-031, C-042, C-064 | T-005, T-006, T-140 to T-154 |
| D-070 to D-073 | C-034 to C-041, C-052 | T-007, T-140, T-146, T-147 |
| D-080 to D-086 | C-043 to C-048, C-057 | T-300, T-302, T-310, T-013; S-003 |
| D-090 to D-094 | C-056, C-057 | T-008, T-014, T-016, T-160 to T-163, T-302, T-303, T-304 |
| D-095 | none (audit amendments) | T-016, T-302 (locale case); the `host-tsan` object check |

## 4. CI platform matrix (protocol 3.9)

| Platform declared at intake (A-005) | CI entry | Notes |
|---|---|---|
| Linux x64 | `ubuntu-24.04` in jobs `core` and `plugins` | performance gate here |
| Windows x64 | `windows-2025` in both jobs | Visual Studio 2026 toolchain of the image |
| macOS arm64 | `macos-15` in both jobs | builds the universal binary, runs the arm64 slice |
| macOS x86_64 | `macos-15-intel` in both jobs | builds the universal binary, runs the x86_64 slice |
| ARM64 Linux, libc variant, oldest toolchain | waived | D-005 |

The matrix is produced by step `S-003` from `plan/ci/ci.yml` and recorded in `plan/ENVIRONMENT.md` section 5. The mutation job placement rule does not apply (D-004).

## 5. State at the freeze (red verification, 2026-11-15, planning sandbox, against the stubs; re-frozen after pre-mortem round 1 with T-016, T-211 and the new T-302 to T-304 cases, after round 2 with T-092, the TinySOL hash list and a stronger T-302 program case, after round 3 with an anchored T-092 checker, after round 4 with the named canary and the parenthesis-anchored form, after cold read 9 with the top-frame `race_top:` form, after round 5 with the scope canary, and after the assumption audit with locale cases that also switch the C++ global locale; 36 frozen files)

| Suite | Result |
|---|---|
| `build/folk-tests` | 27 test cases, 27 failed, every failure an exception `not implemented: ...` or an assertion that follows from it; no crash |
| `build/folk-locale-tests` | 2 test cases, 2 failed with `not implemented: ...` (under `de_DE.UTF-8`) |
| `build/folk-perf` | 1 test case, failed with `not implemented: Engine::create` |
| five `...HostTest` programs | 9 test cases each (T-302: 7, T-303, T-304), all failed with `not implemented: createPluginFilter` |
| `pytest -m "not reference"` | 345 collected: 43 passed (T-090: 12, T-091: 2, T-092: 29), 302 failed; the failures are `folk-render failed with status 64: folk-render: not implemented`, a returned status of 64 where another was expected, or (T-210, T-211) status 64 from the stubs of `tools/evidence_guard.py` and `tools/fetch_references.py` |
| `pytest -m reference` with TinySOL present | 16 collected: 1 passed (T-200a, a tool check on the data), 5 failed (T-201: no `references/index.csv` yet), 10 errors raised in the fixture that renders the candidate (`folk-render failed with status 64`) |

The Python tests of instrument behaviour were also run against an idealised stand-in renderer (spike S08): all pass except T-163, for a reason that concerns only the stand-in (`research/spikes/s08-test-oracle/README.md`).
